import React, { useState } from "react";
import { ChevronDown, ChevronUp, AlertCircle, CheckCircle } from "lucide-react";
import { ValidationResult } from "../types";

interface InvoiceResultsProps {
  results: ValidationResult[];
  filterValid?: boolean;
}

export function InvoiceResults({
  results,
  filterValid = false,
}: InvoiceResultsProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [localFilterValid, setLocalFilterValid] = useState(filterValid);

  const filteredResults = localFilterValid
    ? results.filter((r) => !r.is_valid)
    : results;

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Invoice Results
        </h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={localFilterValid}
            onChange={(e) => setLocalFilterValid(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300"
          />
          <span className="text-sm text-gray-600">Show only invalid</span>
        </label>
      </div>

      {filteredResults.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {localFilterValid
            ? "No invalid invoices found!"
            : "No results to display"}
        </div>
      ) : (
        filteredResults.map((result) => (
          <div
            key={result.invoice_id}
            className="border border-gray-200 rounded-lg overflow-hidden bg-white hover:shadow-md transition-shadow"
          >
            <button
              onClick={() => toggleExpand(result.invoice_id)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                {result.is_valid ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-500" />
                )}
                <div className="text-left">
                  <p className="font-medium text-gray-900">
                    {result.invoice_id}
                  </p>
                  <p className="text-sm text-gray-500">
                    {result.is_valid
                      ? "Valid"
                      : `${result.errors.length} error(s)`}
                  </p>
                </div>
              </div>
              {expandedId === result.invoice_id ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </button>

            {expandedId === result.invoice_id && (
              <div className="bg-gray-50 px-4 py-3 border-t border-gray-200">
                {result.errors.length > 0 ? (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">Errors:</p>
                    <ul className="space-y-1">
                      {result.errors.map((error, idx) => (
                        <li
                          key={idx}
                          className="text-sm text-red-600 flex items-start gap-2"
                        >
                          <span className="text-red-500 mt-0.5">•</span>
                          <span>{error}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="text-sm text-green-600">All validations passed</p>
                )}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
