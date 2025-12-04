from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import tempfile
from pathlib import Path

from invoice_qc.extractor import InvoiceExtractor
from invoice_qc.validator import InvoiceValidator
from invoice_qc.schema import Invoice, LineItem


app = FastAPI(
    title="Invoice QC Service",
    description="Invoice extraction and quality control API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class LineItemModel(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    line_total: Optional[float] = None


class InvoiceModel(BaseModel):
    invoice_number: Optional[str] = None
    external_reference: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    seller_tax_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    tax_rate: Optional[float] = None
    line_items: List[LineItemModel] = []


class ValidationResultModel(BaseModel):
    invoice_id: str
    is_valid: bool
    errors: List[str]


class ValidationSummaryModel(BaseModel):
    total_invoices: int
    valid_invoices: int
    invalid_invoices: int
    error_counts: Dict[str, int]
    results: List[ValidationResultModel]


class HealthModel(BaseModel):
    status: str
    version: str

class InvoiceExtractionResponse(BaseModel):
    invoices: List[InvoiceModel]
    validation: ValidationSummaryModel


@app.get("/health", response_model=HealthModel)
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0"
    }


@app.post("/validate-json", response_model=ValidationSummaryModel)
async def validate_json(invoices: List[InvoiceModel]):
    """
    Validate a list of invoice JSON objects.

    Request body: list of invoice objects
    Response: validation summary with per-invoice results
    """
    if not invoices:
        raise HTTPException(status_code=400, detail="Empty invoice list")

    # Convert Pydantic models to Invoice objects
    invoice_objs = []
    for inv_model in invoices:
        line_items = [
            LineItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                line_total=item.line_total,
            )
            for item in inv_model.line_items
        ]

        invoice = Invoice(
            invoice_number=inv_model.invoice_number,
            external_reference=inv_model.external_reference,
            invoice_date=inv_model.invoice_date,
            due_date=inv_model.due_date,
            seller_name=inv_model.seller_name,
            seller_address=inv_model.seller_address,
            seller_tax_id=inv_model.seller_tax_id,
            buyer_name=inv_model.buyer_name,
            buyer_address=inv_model.buyer_address,
            buyer_tax_id=inv_model.buyer_tax_id,
            currency=inv_model.currency,
            net_total=inv_model.net_total,
            tax_amount=inv_model.tax_amount,
            gross_total=inv_model.gross_total,
            tax_rate=inv_model.tax_rate,
            line_items=line_items,
        )
        invoice_objs.append(invoice)

    # Validate
    validator = InvoiceValidator()
    summary = validator.validate_invoices(invoice_objs)

    return summary


@app.post("/extract-and-validate-pdfs", response_model=InvoiceExtractionResponse)
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    """
    Extract and validate invoices from uploaded PDFs.

    Accepts multiple PDF files via multipart upload.
    Returns validation summary with extracted and validated data.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files provided")

    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded files
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")

            file_path = Path(tmpdir) / file.filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

        # Extract invoices
        extractor = InvoiceExtractor()
        invoices = extractor.extract_from_folder(tmpdir)

        if not invoices:
            raise HTTPException(status_code=400, detail="No invoices extracted from PDFs")

        # Validate
        validator = InvoiceValidator()
        summary = validator.validate_invoices(invoices)

        # Add extracted data to results
        extracted_data = {
            "invoices": [inv.to_dict() for inv in invoices],
            "validation": summary
        }

        return extracted_data


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "Invoice QC Service",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "validate_json": "/validate-json",
            "extract_and_validate": "/extract-and-validate-pdfs"
        }
    }
