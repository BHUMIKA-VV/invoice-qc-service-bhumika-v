# Quick Start Guide

This document provides step-by-step instructions to get the Invoice QC Service running locally.

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Git

## Installation & Running

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd invoice-qc-service
```

### Step 2: Backend Setup (Python API)

#### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Start API Server

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

The API documentation will be available at: http://localhost:8000/docs

### Step 3: Frontend Setup (React)

In a **new terminal**, navigate to the project directory:

#### Install Node Dependencies

```bash
npm install
```

#### Configure API URL (Optional)

If your API is running on a different URL, create/update `.env.local`:

```
VITE_API_URL=http://localhost:8000
```

#### Start Development Server

```bash
npm run dev
```

You should see output like:
```
VITE v5.4.8  ready in 123 ms

➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

## Using the Application

### 1. Upload Invoices (via UI)

1. Open the web console at http://localhost:5173
2. Click "Upload PDFs"
3. Drag and drop PDF files or click to browse
4. Wait for extraction and validation
5. View results with validation summary and error details

### 2. Validate JSON (via UI)

1. Click "Paste JSON"
2. Paste an array of invoice objects:
```json
[
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
]
```
3. Click "Validate JSON"
4. View results

### 3. CLI Usage (Command Line)

In the terminal with activated Python environment:

#### Extract Invoices from PDFs

```bash
python -m invoice_qc.cli extract \
  --pdf-dir /path/to/pdfs \
  --output extracted_invoices.json
```

#### Validate Extracted Invoices

```bash
python -m invoice_qc.cli validate \
  --input extracted_invoices.json \
  --report validation_report.json
```

#### Full End-to-End Processing

```bash
python -m invoice_qc.cli full-run \
  --pdf-dir /path/to/pdfs \
  --report final_report.json
```

### 4. API Usage (Programmatically)

#### Validate JSON via API

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

#### Upload and Extract PDFs via API

```bash
curl -X POST http://localhost:8000/extract-and-validate-pdfs \
  -F "files=@invoice1.pdf" \
  -F "files=@invoice2.pdf"
```

#### Health Check

```bash
curl http://localhost:8000/health
```

## Building for Production

### Frontend Build

```bash
npm run build
```

Output will be in the `dist/` directory.

### Docker (Optional)

Build and run the API in Docker:

```bash
# Build image
docker build -t invoice-qc-api .

# Run container
docker run -p 8000:8000 invoice-qc-api
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'invoice_qc'"

Make sure you're running the CLI from the project root and have activated the virtual environment:
```bash
source venv/bin/activate
python -m invoice_qc.cli --help
```

### "Connection refused" or "Failed to connect to API"

1. Verify the API server is running: Check terminal where you started `uvicorn`
2. Check port conflicts: API uses port 8000, frontend uses port 5173
3. Update API URL in frontend if needed: Create/update `.env.local` with correct `VITE_API_URL`

### PDF Extraction Returns Empty Fields

1. Ensure PDF is text-based (not scanned/image)
2. Check that PDF contains text that matches expected patterns
3. Review extracted JSON to see what was captured

### Build Errors

```bash
# Clear and rebuild frontend
rm -rf node_modules dist
npm install
npm run build

# Clear and reinstall Python
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Project Files

- `invoice_qc/` - Python backend modules
- `src/` - React frontend components
- `api.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `package.json` - Node dependencies
- `README.md` - Full documentation
- `SETUP.md` - This file

## Next Steps

- Review `README.md` for detailed architecture and validation rules
- Check sample invoice results in validation reports
- Explore API documentation at http://localhost:8000/docs
- Consider integrating with your document processing pipeline

## Support

For issues or questions, refer to:
1. README.md - Architecture and design decisions
2. API docs at http://localhost:8000/docs
3. Code comments in `invoice_qc/` modules
