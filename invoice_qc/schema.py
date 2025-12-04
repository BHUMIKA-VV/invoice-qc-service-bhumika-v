from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class LineItem:
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None


@dataclass
class Invoice:
    # Identifiers
    invoice_number: Optional[str] = None
    external_reference: Optional[str] = None

    # Dates
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

    # Parties
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    seller_tax_id: Optional[str] = None

    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_tax_id: Optional[str] = None

    # Money
    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    tax_rate: Optional[float] = None

    # Line items
    line_items: List[LineItem] = field(default_factory=list)

    def to_dict(self):
        return {
            "invoice_number": self.invoice_number,
            "external_reference": self.external_reference,
            "invoice_date": self.invoice_date,
            "due_date": self.due_date,
            "seller_name": self.seller_name,
            "seller_address": self.seller_address,
            "seller_tax_id": self.seller_tax_id,
            "buyer_name": self.buyer_name,
            "buyer_address": self.buyer_address,
            "buyer_tax_id": self.buyer_tax_id,
            "currency": self.currency,
            "net_total": self.net_total,
            "tax_amount": self.tax_amount,
            "gross_total": self.gross_total,
            "tax_rate": self.tax_rate,
            "line_items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in self.line_items
            ],
        }
