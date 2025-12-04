import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import defaultdict

from invoice_qc.schema import Invoice


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def validate(self, invoice: Invoice) -> Optional[str]:
        """
        Validate an invoice.
        Returns None if valid, otherwise returns error message.
        """
        raise NotImplementedError


class CompletenessRule(ValidationRule):
    """Validates that required fields are present."""

    def __init__(self, field_name: str):
        super().__init__(
            f"completeness: {field_name}",
            f"Invoice must have non-empty {field_name}"
        )
        self.field_name = field_name

    def validate(self, invoice: Invoice) -> Optional[str]:
        value = getattr(invoice, self.field_name, None)
        if not value or (isinstance(value, str) and not value.strip()):
            return f"missing_field: {self.field_name}"
        return None


class DateFormatRule(ValidationRule):
    """Validates date format and range."""

    def __init__(self, field_name: str):
        super().__init__(
            f"date_format: {field_name}",
            f"{field_name} must be in valid date format (YYYY-MM-DD)"
        )
        self.field_name = field_name

    def validate(self, invoice: Invoice) -> Optional[str]:
        value = getattr(invoice, self.field_name, None)
        if not value:
            return None

        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            # Check if date is within reasonable range (past 50 years, future 10 years)
            now = datetime.now()
            if dt.year < now.year - 50 or dt.year > now.year + 10:
                return f"date_out_of_range: {self.field_name}"
        except ValueError:
            return f"invalid_date_format: {self.field_name}"

        return None


class CurrencyRule(ValidationRule):
    """Validates currency is in known set."""

    ALLOWED_CURRENCIES = {"EUR", "USD", "GBP", "INR", "CHF", "JPY", "AUD", "CAD"}

    def __init__(self):
        super().__init__(
            "currency_valid",
            f"Currency must be one of {self.ALLOWED_CURRENCIES}"
        )

    def validate(self, invoice: Invoice) -> Optional[str]:
        if not invoice.currency:
            return None

        if invoice.currency.upper() not in self.ALLOWED_CURRENCIES:
            return f"invalid_currency: {invoice.currency}"

        return None


class AmountSignRule(ValidationRule):
    """Validates that amounts are non-negative."""

    def __init__(self, field_name: str):
        super().__init__(
            f"amount_sign: {field_name}",
            f"{field_name} must not be negative"
        )
        self.field_name = field_name

    def validate(self, invoice: Invoice) -> Optional[str]:
        value = getattr(invoice, self.field_name, None)
        if value is not None and value < 0:
            return f"negative_amount: {self.field_name}"
        return None


class TotalConsistencyRule(ValidationRule):
    """Validates that gross = net + tax."""

    def __init__(self):
        super().__init__(
            "totals_consistency",
            "gross_total should equal net_total + tax_amount (within 0.01 tolerance)"
        )

    def validate(self, invoice: Invoice) -> Optional[str]:
        if (invoice.net_total is not None and
            invoice.tax_amount is not None and
            invoice.gross_total is not None):

            expected_gross = round(invoice.net_total + invoice.tax_amount, 2)
            actual_gross = round(invoice.gross_total, 2)

            if abs(expected_gross - actual_gross) > 0.01:
                return (f"business_rule_failed: totals_mismatch "
                       f"(expected {expected_gross}, got {actual_gross})")

        return None


class DueDateRule(ValidationRule):
    """Validates that due_date is on or after invoice_date."""

    def __init__(self):
        super().__init__(
            "due_date_valid",
            "due_date must be on or after invoice_date"
        )

    def validate(self, invoice: Invoice) -> Optional[str]:
        if invoice.invoice_date and invoice.due_date:
            try:
                inv_date = datetime.strptime(invoice.invoice_date, "%Y-%m-%d")
                due_date = datetime.strptime(invoice.due_date, "%Y-%m-%d")

                if due_date < inv_date:
                    return "business_rule_failed: due_date_before_invoice_date"
            except ValueError:
                pass

        return None


class LineItemsConsistencyRule(ValidationRule):
    """Validates that line items sum to net total."""

    def __init__(self):
        super().__init__(
            "line_items_consistency",
            "Sum of line_items should equal net_total (if both present)"
        )

    def validate(self, invoice: Invoice) -> Optional[str]:
        if invoice.line_items and invoice.net_total is not None:
            items_sum = sum(
                item.line_total for item in invoice.line_items
                if item.line_total is not None
            )

            if items_sum > 0 and abs(items_sum - invoice.net_total) > 0.01:
                return (f"business_rule_failed: line_items_sum_mismatch "
                       f"(items sum {items_sum}, net total {invoice.net_total})")

        return None


class TaxIDFormatRule(ValidationRule):
    """Validates tax ID format."""

    def __init__(self, field_name: str):
        super().__init__(
            f"tax_id_format: {field_name}",
            f"{field_name} should match VAT ID format (e.g., DE123456789)"
        )
        self.field_name = field_name

    def validate(self, invoice: Invoice) -> Optional[str]:
        value = getattr(invoice, self.field_name, None)
        if not value:
            return None

        # Simple VAT ID format check: 2 letters + 9-12 digits
        if not re.match(r"^[A-Z]{2}\d{9,12}$", value):
            return f"invalid_tax_id_format: {self.field_name}"

        return None


class PartyNamesRule(ValidationRule):
    """Validates that seller and buyer names are different."""

    def __init__(self):
        super().__init__(
            "parties_different",
            "Seller and buyer must be different entities"
        )

    def validate(self, invoice: Invoice) -> Optional[str]:
        if (invoice.seller_name and invoice.buyer_name and
            invoice.seller_name.lower().strip() == invoice.buyer_name.lower().strip()):
            return "business_rule_failed: seller_and_buyer_same"

        return None


class InvoiceValidator:
    """Main validator that applies all rules."""

    def __init__(self):
        self.rules = [
            # Completeness rules
            CompletenessRule("invoice_number"),
            CompletenessRule("invoice_date"),
            CompletenessRule("seller_name"),
            CompletenessRule("buyer_name"),

            # Date format rules
            DateFormatRule("invoice_date"),
            DateFormatRule("due_date"),

            # Currency rule
            CurrencyRule(),

            # Amount sign rules
            AmountSignRule("net_total"),
            AmountSignRule("tax_amount"),
            AmountSignRule("gross_total"),

            # Business rules
            TotalConsistencyRule(),
            DueDateRule(),
            LineItemsConsistencyRule(),
            PartyNamesRule(),
        ]

    def validate_invoice(self, invoice: Invoice) -> Dict[str, Any]:
        """Validate a single invoice."""
        errors = []

        for rule in self.rules:
            error = rule.validate(invoice)
            if error:
                errors.append(error)

        invoice_id = invoice.invoice_number or "UNKNOWN"

        return {
            "invoice_id": invoice_id,
            "is_valid": len(errors) == 0,
            "errors": errors,
        }

    def validate_invoices(self, invoices: List[Invoice]) -> Dict[str, Any]:
        """Validate a list of invoices and return summary."""
        results = []
        error_counts = defaultdict(int)

        for invoice in invoices:
            result = self.validate_invoice(invoice)
            results.append(result)

            for error in result["errors"]:
                error_counts[error] += 1

        valid_count = sum(1 for r in results if r["is_valid"])
        invalid_count = len(results) - valid_count

        summary = {
            "total_invoices": len(invoices),
            "valid_invoices": valid_count,
            "invalid_invoices": invalid_count,
            "error_counts": dict(error_counts),
            "results": results,
        }

        return summary


def validate_invoices(invoices: List[Invoice]) -> Dict[str, Any]:
    """Convenience function to validate invoices."""
    validator = InvoiceValidator()
    return validator.validate_invoices(invoices)
