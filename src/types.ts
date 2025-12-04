export interface LineItem {
  description: string | null;
  quantity: number | null;
  unit_price: number | null;
  line_total: number | null;
}

export interface Invoice {
  invoice_number: string | null;
  external_reference: string | null;
  invoice_date: string | null;
  due_date: string | null;
  seller_name: string | null;
  seller_address: string | null;
  seller_tax_id: string | null;
  buyer_name: string | null;
  buyer_address: string | null;
  buyer_tax_id: string | null;
  currency: string | null;
  net_total: number | null;
  tax_amount: number | null;
  gross_total: number | null;
  tax_rate: number | null;
  line_items: LineItem[];
}

export interface ValidationResult {
  invoice_id: string;
  is_valid: boolean;
  errors: string[];
}

export interface ValidationSummary {
  total_invoices: number;
  valid_invoices: number;
  invalid_invoices: number;
  error_counts: Record<string, number>;
  results: ValidationResult[];
}

export interface ExtractedData {
  invoices: Invoice[];
  validation: ValidationSummary;
}
