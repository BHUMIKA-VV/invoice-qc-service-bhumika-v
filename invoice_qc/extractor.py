import re
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from invoice_qc.schema import Invoice, LineItem


class InvoiceExtractor:
    def __init__(self):
        if not pdfplumber:
            raise ImportError("pdfplumber is required. Install with: pip install pdfplumber")

    def extract_from_folder(self, pdf_dir: str) -> List[Invoice]:
        """Extract invoices from all PDFs in a directory."""
        pdf_path = Path(pdf_dir)
        invoices = []

        for pdf_file in sorted(pdf_path.glob("*.pdf")):
            try:
                invoice = self.extract_from_pdf(str(pdf_file))
                if invoice:
                    invoices.append(invoice)
            except Exception as e:
                print(f"Error extracting {pdf_file.name}: {e}")

        return invoices

    def extract_from_pdf(self, pdf_path: str) -> Optional[Invoice]:
        """Extract a single invoice from a PDF."""
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        return self.parse_invoice_text(text)

    def parse_invoice_text(self, text: str) -> Optional[Invoice]:
        """Parse invoice text into structured data."""
        invoice = Invoice()

        # Extract invoice number
        invoice.invoice_number = self._extract_invoice_number(text)

        # Extract dates
        invoice.invoice_date = self._extract_date(text, ["invoice date", "date:", "issued"])
        invoice.due_date = self._extract_date(text, ["due date", "payment due", "due by"])

        # Extract party information
        invoice.seller_name = self._extract_seller_name(text)
        invoice.buyer_name = self._extract_buyer_name(text)
        invoice.seller_tax_id = self._extract_tax_id(text, ["seller", "from", "bill from"])
        invoice.buyer_tax_id = self._extract_tax_id(text, ["buyer", "to", "bill to"])

        # Extract currency
        invoice.currency = self._extract_currency(text)

        # Extract amounts
        amounts = self._extract_amounts(text)
        invoice.net_total = amounts.get("net_total")
        invoice.tax_amount = amounts.get("tax_amount")
        invoice.gross_total = amounts.get("gross_total")
        invoice.tax_rate = amounts.get("tax_rate")

        # Extract line items
        invoice.line_items = self._extract_line_items(text)

        return invoice

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text."""
        patterns = [
            r"(?:invoice\s*(?:no|number|#|num)?[\s:]*([A-Z0-9\-\/]+))",
            r"(?:invoice[^a-z0-9]*([A-Z0-9\-\/]+))",
            r"(?:inv[\s:]?\s*([A-Z0-9\-\/]+))",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_date(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract date by looking for keywords."""
        for keyword in keywords:
            pattern = rf"{keyword}[\s:]*(\d{{1,2}}[\.\/-]\d{{1,2}}[\.\/-]\d{{4}}|\d{{4}}[\.\/-]\d{{1,2}}[\.\/-]\d{{1,2}})"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                return self._normalize_date(date_str)

        # Try to find any date pattern
        date_pattern = r"(\d{1,2}[\.\/-]\d{1,2}[\.\/-]\d{4}|\d{4}[\.\/-]\d{1,2}[\.\/-]\d{1,2})"
        match = re.search(date_pattern, text)
        if match:
            return self._normalize_date(match.group(1))

        return None

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        try:
            # Try DD.MM.YYYY or DD/MM/YYYY or DD-MM-YYYY
            for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except:
            pass
        return date_str

    def _extract_seller_name(self, text: str) -> Optional[str]:
        """Extract seller name."""
        patterns = [
            r"(?:from|seller|invoice from)[\s:]*([A-Za-z\s&\.]+?)(?:\n|address|tax)",
            r"(?:^|\n)([A-Za-z][A-Za-z\s&\.]{5,40}?)(?:\n|address|tax|phone)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:
                    return name

        return None

    def _extract_buyer_name(self, text: str) -> Optional[str]:
        """Extract buyer name."""
        patterns = [
            r"(?:to|buyer|bill to|invoice to)[\s:]*([A-Za-z\s&\.]+?)(?:\n|address|tax)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:
                    return name

        return None

    def _extract_tax_id(self, text: str, keywords: List[str]) -> Optional[str]:
        """Extract tax ID (VAT ID)."""
        for keyword in keywords:
            pattern = rf"{keyword}[\s\S]*?(?:tax id|vat|vat id|tax number|reg no)[\s:]*([A-Z]{2}\d{{9,12}}|\d{{9,12}})"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Generic VAT pattern
        vat_pattern = r"(?:vat id|tax id|reg\.?\s*no)[\s:]*([A-Z]{2}\d{9,12})"
        match = re.search(vat_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def _extract_currency(self, text: str) -> Optional[str]:
        """Extract currency."""
        currencies = {
            "EUR": r"EUR|\€",
            "USD": r"USD|\$",
            "GBP": r"GBP|\£",
            "INR": r"INR|\₹",
            "CHF": r"CHF",
            "JPY": r"JPY|¥",
        }

        for currency, pattern in currencies.items():
            if re.search(pattern, text):
                return currency

        return None

    def _extract_amounts(self, text: str) -> dict:
        """Extract monetary amounts."""
        amounts = {
            "net_total": None,
            "tax_amount": None,
            "gross_total": None,
            "tax_rate": None,
        }

        # Pattern to find amounts: handles both comma and dot as decimal separator
        amount_pattern = r"([\d\.,]+)"

        # Extract net total
        net_patterns = [
            r"(?:subtotal|net|amount|total|net\s*total)[\s:]*[€$\£\₹]?\s*([0-9,\.]+)",
            r"(?:^|\n)([0-9,\.]+)\s*(?:€|$|£|₹|EUR|USD)",
        ]

        for pattern in net_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amounts["net_total"] = self._parse_amount(match.group(1))
                    break
                except:
                    continue

        # Extract tax amount
        tax_patterns = [
            r"(?:tax|vat|tva)[\s:]*[€$\£\₹]?\s*([0-9,\.]+)",
        ]

        for pattern in tax_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amounts["tax_amount"] = self._parse_amount(match.group(1))
                    break
                except:
                    continue

        # Extract gross total
        gross_patterns = [
            r"(?:total|amount due|grand total|gross)[\s:]*[€$\£\₹]?\s*([0-9,\.]+)",
        ]

        for pattern in gross_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amounts["gross_total"] = self._parse_amount(match.group(1))
                    break
                except:
                    continue

        # Extract tax rate
        tax_rate_pattern = r"(?:tax rate|vat rate|rate)[\s:]*([0-9,\.]+)\s*%"
        match = re.search(tax_rate_pattern, text, re.IGNORECASE)
        if match:
            try:
                amounts["tax_rate"] = float(match.group(1).replace(",", "."))
            except:
                pass

        return amounts

    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        # Remove spaces and determine decimal separator
        amount_str = amount_str.strip()

        # If it has both comma and dot, use the last one as decimal separator
        if "," in amount_str and "." in amount_str:
            if amount_str.rfind(",") > amount_str.rfind("."):
                amount_str = amount_str.replace(".", "").replace(",", ".")
            else:
                amount_str = amount_str.replace(",", "")
        elif "," in amount_str:
            # If only comma, check if it's thousands separator or decimal
            comma_pos = amount_str.rfind(",")
            if comma_pos > 0 and len(amount_str) - comma_pos == 3:
                # Likely decimal separator
                amount_str = amount_str.replace(",", ".")
            else:
                # Likely thousands separator
                amount_str = amount_str.replace(",", "")

        return float(amount_str)

    def _extract_line_items(self, text: str) -> List[LineItem]:
        """Extract line items from invoice text."""
        items = []

        # Simple pattern for line items
        # Looks for patterns like: "description quantity@price = total"
        line_pattern = r"^(.+?)\s+(\d+(?:[,\.]\d+)?)\s+(?:x|\*|@)?\s*([0-9,\.]+)\s*(?:€|\$|£|₹)?\s*=?\s*([0-9,\.]+)"

        matches = re.finditer(line_pattern, text, re.MULTILINE)
        for match in matches:
            try:
                item = LineItem(
                    description=match.group(1).strip(),
                    quantity=float(match.group(2).replace(",", ".")),
                    unit_price=self._parse_amount(match.group(3)),
                    line_total=self._parse_amount(match.group(4)),
                )
                items.append(item)
            except:
                continue

        return items


def extract_invoices(pdf_dir: str) -> List[Invoice]:
    """Convenience function to extract invoices from a directory."""
    extractor = InvoiceExtractor()
    return extractor.extract_from_folder(pdf_dir)


def extract_to_json(pdf_dir: str) -> str:
    """Extract invoices and return as JSON."""
    invoices = extract_invoices(pdf_dir)
    return json.dumps([inv.to_dict() for inv in invoices], indent=2)
