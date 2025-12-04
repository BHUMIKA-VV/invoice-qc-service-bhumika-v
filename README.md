# Invoice QC Service

A comprehensive invoice extraction and quality control system with PDF parsing, data validation, CLI tools, and a web-based QC console.

## Project Overview

This project provides an end-to-end solution for processing B2B invoices:

1. **PDF Extraction** - Extracts structured data from invoice PDFs
2. **Data Validation** - Applies business rules and quality checks
3. **CLI Tool** - Command-line interface for batch processing
4. **HTTP API** - FastAPI backend for integration
5. **Web Console** - React UI for interactive validation

### Completed Components

- ✅ Invoice schema design with 13+ fields
- ✅ PDF extraction module with intelligent text parsing
- ✅ Validation core with 11 comprehensive rules
- ✅ Python CLI with extract/validate/full-run commands
- ✅ FastAPI HTTP API
- ✅ React frontend QC console with real-time results
- ✅ Comprehensive documentation

## Schema & Validation Design

### Invoice Schema

The invoice schema captures all critical B2B invoice information:

**Identifiers:**
- `invoice_number` - Primary invoice identifier (required)
- `external_reference` - Additional reference number

**Dates:**
- `invoice_date` - Date invoice was issued (required)
- `due_date` - Payment due date

**Parties:**
- `seller_name` - Selling company name (required)
- `seller_address` - Seller address
- `seller_tax_id` - Seller VAT/tax ID
- `buyer_name` - Buying company name (required)
- `buyer_address` - Buyer address
- `buyer_tax_id` - Buyer VAT/tax ID

**Monetary:**
- `currency` - ISO currency code (EUR, USD, etc.)
- `net_total` - Pre-tax amount
- `tax_amount` - Tax/VAT amount
- `gross_total` - Total amount due
- `tax_rate` - Tax percentage

**Line Items:**
- Array of `LineItem` objects with:
  - `description` - Item description
  - `quantity` - Item quantity
  - `unit_price` - Price per unit
  - `line_total` - Quantity × unit price

### Validation Rules

All rules are designed to catch real-world invoice quality issues:

**Completeness Rules** (3 rules)
- `completeness: invoice_number` - Invoice must have a number (identifies the invoice)
- `completeness: invoice_date` - Invoice must have a date (establishes invoice period)
- `completeness: seller_name` - Seller name required (identifies vendor)
- `completeness: buyer_name` - Buyer name required (identifies customer)

**Format Rules** (3 rules)
- `date_format: invoice_date` - Date must be valid YYYY-MM-DD format with reasonable range
- `date_format: due_date` - Due date must be valid format if present
- `currency_valid` - Currency must be in known set (EUR, USD, GBP, INR, CHF, JPY, AUD, CAD)

**Amount Rules** (3 rules)
- `amount_sign: net_total` - Net amount cannot be negative
- `amount_sign: tax_amount` - Tax amount cannot be negative
- `amount_sign: gross_total` - Gross amount cannot be negative

**Business Logic Rules** (3 rules)
- `totals_consistency` - Validates: `gross_total ≈ net_total + tax_amount` (within 0.01 tolerance). Catches calculation errors early.
- `due_date_valid` - Due date must be on or after invoice date (prevents illogical dates)
- `line_items_consistency` - Sum of line items must match net total (if both present). Validates invoice arithmetic.
- `parties_different` - Seller and buyer must be different entities (catches invalid invoices)

**Rationale:** These rules cover the three main categories of invoice problems:
1. Missing critical information (completeness)
2. Invalid or malformed data (format)
3. Business logic violations (consistency)

## Architecture

### Project Structure

```
invoice-qc-service/
├── invoice_qc/                 # Python backend
│   ├── __init__.py
│   ├── __main__.py            # CLI entry point
│   ├── schema.py              # Invoice data classes
│   ├── extractor.py           # PDF extraction logic
│   ├── validator.py           # Validation rules & engine
│   └── cli.py                 # CLI commands
├── src/                        # React frontend
│   ├── components/
│   │   ├── FileUpload.tsx      # PDF drag-and-drop upload
│   │   ├── ValidationSummary.tsx  # Results overview
│   │   ├── InvoiceResults.tsx     # Invoice-level results
│   │   └── JSONInput.tsx          # JSON paste input
│   ├── types.ts               # TypeScript interfaces
│   ├── App.tsx                # Main React component
│   └── main.tsx
├── api.py                     # FastAPI application
├── requirements.txt           # Python dependencies
├── vite.config.ts
├── tsconfig.json
└── README.md
```

### Data Flow

```
PDFs/JSON
  ↓
Extraction Module (PDF text parsing)
  ↓
Invoice Objects (structured data)
  ↓
Validation Engine (applies 11 rules)
  ↓
Validation Results (per-invoice + summary)
  ↓
API Response / CLI Output / UI Display
```

### Extraction Pipeline

**1. PDF Parsing** (`extractor.py`)
- Uses `pdfplumber` to extract text from PDF pages
- Handles multiple pages and various PDF layouts

**2. Field Extraction**
- Invoice Number: Searches for "invoice no", "invoice number", "inv" patterns
- Dates: Regex patterns match various date formats (DD.MM.YYYY, DD/MM/YYYY, etc.)
- Party Info: Keyword-based search ("from", "to", "bill to", "bill from")
- Amounts: Currency-aware decimal parsing (handles both comma and dot separators)
- Line Items: Pattern matching for tabular data

**3. Data Normalization**
- Dates converted to YYYY-MM-DD format
- Decimal amounts parsed correctly (handles European format: 1.234,56)
- Empty/null values marked for validation

### Validation Core

**Architecture** (`validator.py`)
- Base `ValidationRule` class: Each rule is a separate class (Single Responsibility)
- `InvoiceValidator`: Orchestrates all rules and generates reports
- Rules are composable and easy to extend

**Example Rule Implementation:**
```python
class TotalConsistencyRule(ValidationRule):
    def validate(self, invoice: Invoice):
        if all needed amounts present:
            expected_gross = net_total + tax_amount
            if abs(expected_gross - actual_gross) > 0.01:
                return "business_rule_failed: totals_mismatch"
        return None
```

### CLI Interface

**Commands:**
- `extract` - PDF extraction only
- `validate` - JSON validation only
- `full-run` - Extract and validate end-to-end

**Example Usage:**
```bash
python -m invoice_qc.cli extract --pdf-dir ./pdfs --output extracted.json
python -m invoice_qc.cli validate --input extracted.json --report report.json
python -m invoice_qc.cli full-run --pdf-dir ./pdfs --report final_report.json
```

### API Endpoints

**FastAPI Application** (`api.py`)

1. `GET /health` - Health check
   ```json
   { "status": "ok", "version": "0.1.0" }
   ```

2. `POST /validate-json` - Validate extracted invoices
   - Request: List of invoice objects
   - Response: Validation summary + per-invoice results

3. `POST /extract-and-validate-pdfs` - Upload PDFs and get results
   - Request: Multipart file upload (multiple PDFs)
   - Response: Extracted data + validation results

4. `GET /` - API info endpoint

### Frontend Features

**React QC Console** (`src/App.tsx`)
- Drag-and-drop PDF upload or JSON paste
- Real-time API integration
- Validation summary with key metrics
- Expandable invoice results with error details
- Filter to show only invalid invoices
- Clean, professional UI with Tailwind CSS

## Setup & Installation

### Requirements
- Python 3.8+
- Node.js 16+ (for frontend)
- pdfplumber (Python library for PDF processing)

### Backend Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run API server:**
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure API URL** (optional):
   ```bash
   # .env or .env.local
   VITE_API_URL=http://localhost:8000
   ```

3. **Run dev server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## Usage

### CLI Examples

**Extract invoices from PDFs:**
```bash
python -m invoice_qc.cli extract \
  --pdf-dir /path/to/pdfs \
  --output extracted_invoices.json
```

**Validate extracted invoices:**
```bash
python -m invoice_qc.cli validate \
  --input extracted_invoices.json \
  --report validation_report.json
```

**Full end-to-end processing:**
```bash
python -m invoice_qc.cli full-run \
  --pdf-dir /path/to/pdfs \
  --report final_report.json
```

**Output example:**
```
============================================================
VALIDATION SUMMARY
============================================================
Total Invoices:   10
Valid Invoices:   7
Invalid Invoices: 3

Top Error Types:
  - missing_field: seller_name: 2
  - business_rule_failed: totals_mismatch: 1
============================================================
```

### API Examples

**Validate JSON invoices (curl):**
```bash
curl -X POST http://localhost:8000/validate-json \
  -H "Content-Type: application/json" \
  -d '[
    {
      "invoice_number": "INV-001",
      "invoice_date": "2024-01-10",
      "seller_name": "ACME GmbH",
      "buyer_name": "Example AG",
      "currency": "EUR",
      "net_total": 100.0,
      "tax_amount": 19.0,
      "gross_total": 119.0
    }
  ]'
```

**Upload PDFs (curl):**
```bash
curl -X POST http://localhost:8000/extract-and-validate-pdfs \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"
```

### Frontend Usage

1. Open http://localhost:5173 (or your dev server URL)
2. Choose "Upload PDFs" or "Paste JSON"
3. Upload files or paste JSON data
4. View results with validation summary and per-invoice errors
5. Filter to show only invalid invoices if needed
6. Export results via API or browser download

## AI Usage Notes

### Tools Used
- **ChatGPT (GPT-4)** - Regex pattern guidance, PDF text extraction strategies, FastAPI scaffolding
- **Claude** - Code organization, validation rule design, type system setup
- **Stack Overflow/MDN** - Specific API implementations

### Parts Assisted
1. **Regex Patterns** - AI helped design patterns for extracting invoice numbers, dates, and amounts in various formats. The European decimal format handling (comma vs dot) was refined through AI suggestions.

2. **PDF Extraction Strategy** - Initial approach discussed extracting via `pdf2image` + OCR, but AI recommended `pdfplumber` for simpler text extraction when dealing with text-based PDFs (more efficient for B2B invoices).

3. **Validation Rule Architecture** - AI suggested the class-based validation rule pattern which made rules composable and easy to extend.

### Example: Where AI Was Incomplete

**Issue:** Initial AI suggestion was to use `regex.VERBOSE` for complex amount patterns, but this didn't handle the ambiguity of comma/dot decimal separators correctly in European invoices.

**What I Did:** Implemented explicit logic that:
- Detects if both comma and dot exist
- Uses position-based heuristics (last occurrence is decimal separator if 2-3 digits after it)
- Falls back to simpler rules for single-separator cases

This required deeper understanding of real invoice formats than AI alone provided.

### AI Chats Summary
- Approximately 12-15 chat interactions for research and validation
- About 60% code scaffolding, 40% algorithmic/design questions
- No significant errors, mostly optimization suggestions

## Assumptions & Limitations

### Intentional Simplifications

1. **Text-Based PDFs Only** - Assumes invoices are text-based PDFs. Scanned/image PDFs require OCR (pdfplumber alone won't work).

2. **Simple Pattern Matching** - Extraction uses regex/keyword matching rather than machine learning. Works well for structured B2B invoices, but may struggle with highly irregular formats.

3. **Single Language** - Pattern matching optimized for English keywords ("invoice", "total", "tax"). Non-English invoices may have lower extraction accuracy.

4. **No Historical Duplicate Detection** - Validates invoices against rules but doesn't check against a database of previously processed invoices for duplicates.

5. **No Warehouse Integration** - Tax IDs aren't verified against external VAT/tax registries.

### Known Edge Cases

1. **Multi-currency invoices** - Only one currency per invoice is supported
2. **Complex tax scenarios** - Multiple tax rates on different line items not explicitly supported
3. **Invoices without line items** - Will extract totals but no item-level validation
4. **Very large PDFs** - No pagination/streaming for massive documents

### Recommended Future Enhancements

- Integration with real VAT ID validation services (e.g., VIES API)
- Machine learning-based field extraction for irregular layouts
- OCR support for scanned invoices
- Historical duplicate checking against database
- Support for multiple currencies and complex tax rules
- Webhook support for real-time validation in document processing pipelines
- Multi-language support

## How This Integrates Into Larger Systems

### Typical Integration Scenarios

**1. Document Processing Pipeline**
```
Incoming PDF Documents
  → Scanner/Document Management System
  → Invoice QC Service (extract + validate)
  → Valid: → Accounting System
  → Invalid: → Manual Review Queue
```

**2. Microservice Architecture**
```
Frontend/Web Application
  → Invoice QC Service (FastAPI)
  → Message Queue (RabbitMQ/Redis)
  → Database (store validation results)
  → Reporting Service
```

**3. Webhook/Event-Driven**
```
Document Upload Event
  → Trigger Lambda/Cloud Function
  → Call Invoice QC API
  → Store results in database
  → Notify stakeholders if validation fails
```

### API Integration Example

```javascript
// From another service
async function processInvoice(pdfFile) {
  const formData = new FormData();
  formData.append('files', pdfFile);

  const response = await fetch(
    'https://invoice-qc.company.com/extract-and-validate-pdfs',
    { method: 'POST', body: formData }
  );

  const result = await response.json();

  if (result.validation.invalid_invoices > 0) {
    // Handle validation failures
    logForReview(result.validation.results);
  } else {
    // Process valid invoices
    sendToAccounting(result.invoices);
  }
}
```

### Containerization (Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY invoice_qc/ ./invoice_qc/
COPY api.py .

EXPOSE 8000

# Run API server
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Usage:**
```bash
docker build -t invoice-qc .
docker run -p 8000:8000 invoice-qc
```

### Queue Integration Example (RabbitMQ/Celery)

```python
from celery import Celery

app = Celery('invoice_processor')

@app.task
def process_invoice_batch(pdf_paths):
    """Background task for batch processing"""
    invoices = extract_invoices(pdf_paths)
    results = validate_invoices(invoices)
    # Store results in database
    save_results(results)
    return results
```

## Technology Stack

### Backend
- **Python 3.8+** - Core language
- **FastAPI** - HTTP API framework
- **Uvicorn** - ASGI server
- **pdfplumber** - PDF text extraction
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Vite** - Build tool

## Testing

### Manual Testing Checklist

- [ ] Extract PDF with valid invoice data
- [ ] Validate JSON with all required fields
- [ ] Validate JSON with missing fields (expect errors)
- [ ] Test with invalid date formats
- [ ] Test with negative amounts
- [ ] Test with mismatched totals
- [ ] Upload multiple PDFs simultaneously
- [ ] Test API CORS headers
- [ ] Test CLI extract command
- [ ] Test CLI validate command
- [ ] Test CLI full-run command

## License

MIT License - Feel free to use this project for commercial or personal purposes.

## Contact

For questions or feedback about this implementation, reach out with specific issues or enhancement requests.
