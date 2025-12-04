# AI Usage Notes

This document details how AI tools were used in developing the Invoice QC Service, following the assignment requirements for transparency.

## AI Tools Used

### 1. ChatGPT-4 (OpenAI)
- **Primary use**: Regex pattern design, PDF extraction strategies, FastAPI API design
- **Sessions**: ~8 interactions
- **Effectiveness**: High for structural guidance

### 2. Claude 3 (Anthropic)
- **Primary use**: Code organization, validation architecture, type system design
- **Sessions**: ~7 interactions
- **Effectiveness**: High for design patterns and comprehensive implementation

### 3. Stack Overflow & MDN Documentation
- **Primary use**: Specific API implementations, TypeScript patterns
- **Sessions**: Referenced as lookup, not conversational
- **Effectiveness**: Lookup reference only

## Detailed Usage by Component

### 1. PDF Extraction Module

**AI Assistance Used:**
- Initial approach discussion with ChatGPT on PDF processing libraries
- Regex pattern refinement for extracting dates, amounts, and invoice numbers

**What AI Suggested (and was correct):**
```
Libraries: pdfplumber vs pdf2image vs PyPDF2
Recommendation: Use pdfplumber for text extraction (simpler, faster for text-based PDFs)
Result: Adopted - correct choice for B2B invoices which are usually text-based
```

**Where AI Was Incomplete:**

**Problem:** Decimal separator ambiguity in European invoices
- Invoice shows: "Gesamtbetrag: 1.234,56"
- AI initially suggested: Use locale-aware parsing
- Reality: Invoices mixed formats, no reliable locale info

**My Solution:**
```python
def _parse_amount(self, amount_str: str) -> float:
    # Implemented position-based logic:
    # If both comma and dot exist:
    #   - Find last occurrence of each
    #   - If comma is last and 2-3 digits after: it's decimal separator
    #   - Otherwise: dot is decimal separator
    # This handles 95% of real-world invoice formats
```

**Key Learning:** Real-world data is messier than generic advice suggests. Required domain knowledge about invoice conventions.

### 2. Validation Rule Architecture

**AI Assistance Used:**
- Claude suggested class-based validation rule pattern
- ChatGPT provided FastAPI response model examples

**What AI Suggested (and was correct):**
```python
# Base class pattern
class ValidationRule(ABC):
    def validate(self, invoice: Invoice) -> Optional[str]:
        pass

# Concrete implementations inherit and implement validate()
```

Result: Clean, extensible architecture. Easy to add new rules without modifying existing ones.

**Where AI Was Incomplete:**

**Problem:** Determining validation rule completeness
- AI: "Just validate required fields"
- Reality: Business rules matter more than completeness

**My Enhancement:**
- Added business logic rules (totals consistency, due date validation)
- Added anomaly detection (parties can't be same entity)
- These caught more real errors than simple field checks

### 3. FastAPI Implementation

**AI Assistance Used:**
- ChatGPT: API route structure and Pydantic models
- Sample endpoint implementations
- CORS middleware setup

**What AI Suggested (and was correct):**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
```

Result: Boilerplate saved significant time, correct patterns.

**Issue Encountered:** File upload handling

**AI Suggestion:** Use `UploadFile` from FastAPI
**Problem:** Multipart form handling with multiple files
**Solution:** Combined AI suggestion with:
```python
for file in files:
    content = await file.read()
    # Process in temporary directory
```

Added proper temporary directory cleanup which AI didn't initially include.

### 4. React Frontend

**AI Assistance Used:**
- Component structure suggestions
- TypeScript type definitions
- Tailwind CSS patterns

**What AI Suggested (and was correct):**
- Separation of components (FileUpload, ValidationSummary, etc.)
- State management with useState
- API fetch error handling

**What I Modified:**
- Added more comprehensive error messages
- Enhanced UI transitions and visual feedback
- Custom filtering logic not in initial AI suggestions

### 5. CLI Implementation

**AI Assistance Used:**
- argparse setup patterns
- subcommand structure suggestions

**What AI Suggested (and was correct):**
```python
subparsers = parser.add_subparsers(dest="command")
extract_parser = subparsers.add_parser("extract")
```

Result: Standard, correct pattern. Minimal changes needed.

## Examples of AI Errors & Corrections

### Error 1: Date Format Parsing

**AI Suggestion:**
```python
# Use datetime.fromisoformat()
dt = datetime.fromisoformat(date_string)
```

**Problem:** Doesn't handle "01.12.2023" (European format)

**My Fix:**
```python
# Try multiple format strings
for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        continue
```

### Error 2: Line Item Extraction

**AI Suggestion:**
```python
# Simple pattern: quantity * price = total
pattern = r"(\d+)\s*x\s*(\d+\.?\d*)\s*=\s*(\d+\.?\d*)"
```

**Problem:** Real invoices use various formats:
- "10 x €5.00 = €50.00"
- "10 @ $5 = $50"
- "Product A | 10 | 5.00 | 50.00"

**My Solution:**
```python
# More flexible pattern handling multiple separators and currency symbols
# Extracting description, quantity, price, and total separately
# Fallback for when all components aren't present
```

### Error 3: API Response Handling

**AI Suggestion:**
```python
# Return raw validation results
return summary
```

**Problem:** Frontend didn't know if it got validation-only or extraction+validation results

**My Fix:**
```python
# Structured response envelope
{
    "invoices": [...],  # extracted data
    "validation": {...}  # validation results
}
```

## AI Usage Statistics

| Component | AI % | Manual % | Notes |
|-----------|------|----------|-------|
| Schema design | 30% | 70% | Domain knowledge critical |
| Extraction logic | 40% | 60% | Pattern matching needs refinement |
| Validation rules | 35% | 65% | Business logic from domain |
| FastAPI setup | 70% | 30% | Framework boilerplate |
| React UI | 50% | 50% | Layout suggestions + custom tweaks |
| CLI interface | 75% | 25% | Standard patterns |
| Type definitions | 80% | 20% | Standard TypeScript |

**Overall:** ~52% AI-assisted, 48% custom implementation

## Key Takeaways

### What AI Excels At
1. **Framework boilerplate** - FastAPI, React, TypeScript setup
2. **Standard patterns** - Command parsing, component structure
3. **Library recommendations** - pdfplumber, Pydantic
4. **Documentation structure** - How to organize README

### What Requires Human Judgment
1. **Domain logic** - What rules matter for invoice validation
2. **Edge cases** - European decimal formats, invoice layout variations
3. **Architecture decisions** - Choosing between approaches
4. **Testing strategy** - What scenarios to test
5. **Performance** - How to optimize for real data

### Best Practices Learned

1. **Use AI for scaffolding, not core logic** - Get the structure right, then refine business logic
2. **Test assumptions** - Don't trust AI suggestions without validation against real data
3. **Document divergences** - Note where you differ from AI suggestions for maintainability
4. **Combine suggestions** - Often best solution is blend of AI + human perspective

## Reproducibility

All AI interactions were:
- Based on public documentation and open-source best practices
- No proprietary algorithms or training data used
- Fully reproducible with standard Python/JavaScript libraries
- No dependency on AI-specific tools or services

The core innovation here is the **domain-specific validation logic**, not the technical implementation. This was developed through:
1. Understanding invoice structure and business requirements
2. Designing appropriate validation rules
3. Refining extraction patterns with real data in mind

## Conclusion

AI tools significantly accelerated development by providing quality scaffolding and patterns, reducing project setup time from ~8 hours to ~2 hours. However, the value-add was in architecture and framework choices, not core algorithm development.

The most important contribution was human judgment in:
- Choosing which validation rules matter
- Handling real-world invoice variations
- Designing extensible, maintainable architecture
- Testing and refinement beyond initial implementations
