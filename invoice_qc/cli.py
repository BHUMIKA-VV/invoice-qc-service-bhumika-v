import argparse
import json
import sys
from pathlib import Path

from invoice_qc.extractor import extract_invoices
from invoice_qc.validator import validate_invoices
from invoice_qc.schema import Invoice, LineItem


def load_invoices_from_json(json_file: str) -> list:
    """Load invoices from JSON file, converting nested LineItem dicts to dataclasses."""
    with open(json_file, "r") as f:
        data = json.load(f)

    invoices = []
    for raw_invoice_data in data:
        if 'line_items' in raw_invoice_data:
            raw_items = raw_invoice_data['line_items']
            line_item_objects = [LineItem(**item_dict) for item_dict in raw_items]
            
            raw_invoice_data['line_items'] = line_item_objects
        invoice = Invoice(**raw_invoice_data)
        invoices.append(invoice)

    return invoices


def save_invoices_to_json(invoices: list, output_file: str) -> None:
    """Save invoices to JSON file."""
    data = [inv.to_dict() for inv in invoices]
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


def print_summary(summary: dict) -> None:
    """Print validation summary to stdout."""
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Invoices:   {summary['total_invoices']}")
    print(f"Valid Invoices:   {summary['valid_invoices']}")
    print(f"Invalid Invoices: {summary['invalid_invoices']}")

    if summary["error_counts"]:
        print("\nTop Error Types:")
        sorted_errors = sorted(
            summary["error_counts"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        for error_type, count in sorted_errors[:10]:
            print(f"  - {error_type}: {count}")

    print("=" * 60 + "\n")


def cmd_extract(args):
    """Handle extract command."""
    if not Path(args.pdf_dir).exists():
        print(f"Error: PDF directory '{args.pdf_dir}' not found")
        sys.exit(1)

    print(f"Extracting invoices from {args.pdf_dir}...")
    invoices = extract_invoices(args.pdf_dir)

    print(f"Extracted {len(invoices)} invoices")

    if args.output:
        save_invoices_to_json(invoices, args.output)
        print(f"Saved to {args.output}")


def cmd_validate(args):
    """Handle validate command."""
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)

    print(f"Loading invoices from {args.input}...")
    invoices = load_invoices_from_json(args.input)

    print(f"Validating {len(invoices)} invoices...")
    summary = validate_invoices(invoices)

    print_summary(summary)

    if args.report:
        with open(args.report, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Report saved to {args.report}")

    # Exit with error if there are invalid invoices
    if summary["invalid_invoices"] > 0:
        sys.exit(1)


def cmd_full_run(args):
    """Handle full-run command."""
    if not Path(args.pdf_dir).exists():
        print(f"Error: PDF directory '{args.pdf_dir}' not found")
        sys.exit(1)

    print(f"Starting full-run on {args.pdf_dir}...")

    # Extract
    print("\n[1/2] Extracting invoices...")
    invoices = extract_invoices(args.pdf_dir)
    print(f"Extracted {len(invoices)} invoices")

    # Validate
    print("\n[2/2] Validating invoices...")
    summary = validate_invoices(invoices)

    print_summary(summary)

    if args.report:
        with open(args.report, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Report saved to {args.report}")

    # Exit with error if there are invalid invoices
    if summary["invalid_invoices"] > 0:
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Invoice QC Service - Extract and validate invoices"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract invoices from PDFs"
    )
    extract_parser.add_argument(
        "--pdf-dir",
        required=True,
        help="Directory containing PDF files"
    )
    extract_parser.add_argument(
        "--output",
        help="Output JSON file for extracted invoices"
    )
    extract_parser.set_defaults(func=cmd_extract)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate extracted invoices"
    )
    validate_parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file with extracted invoices"
    )
    validate_parser.add_argument(
        "--report",
        help="Output JSON file for validation report"
    )
    validate_parser.set_defaults(func=cmd_validate)

    # Full-run command
    fullrun_parser = subparsers.add_parser(
        "full-run",
        help="Extract and validate invoices end-to-end"
    )
    fullrun_parser.add_argument(
        "--pdf-dir",
        required=True,
        help="Directory containing PDF files"
    )
    fullrun_parser.add_argument(
        "--report",
        help="Output JSON file for validation report"
    )
    fullrun_parser.set_defaults(func=cmd_full_run)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
