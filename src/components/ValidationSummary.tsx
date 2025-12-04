import React from "react";
import { AlertCircle, CheckCircle } from "lucide-react";
import { ValidationSummary } from "../types";

interface ValidationSummaryProps {
  summary: ValidationSummary;
}

export function ValidationSummaryComponent({
  summary,
}: ValidationSummaryProps) {
  const validPercentage =
    summary.total_invoices > 0
      ? Math.round((summary.valid_invoices / summary.total_invoices) * 100)
      : 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="border-l-4 border-blue-500 pl-4">
          <p className="text-sm text-gray-600">Total Invoices</p>
          <p className="text-2xl font-bold text-gray-900">
            {summary.total_invoices}
          </p>
        </div>
        <div className="border-l-4 border-green-500 pl-4">
          <p className="text-sm text-gray-600">Valid Invoices</p>
          <p className="text-2xl font-bold text-green-600">
            {summary.valid_invoices}
          </p>
        </div>
        <div className="border-l-4 border-red-500 pl-4">
          <p className="text-sm text-gray-600">Invalid Invoices</p>
          <p className="text-2xl font-bold text-red-600">
            {summary.invalid_invoices}
          </p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-sm text-gray-600 mb-2">Pass Rate</p>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              validPercentage >= 80 ? "bg-green-500" : "bg-yellow-500"
            }`}
            style={{ width: `${validPercentage}%` }}
          />
        </div>
        <p className="text-sm text-gray-600 mt-1">{validPercentage}% valid</p>
      </div>

      {Object.keys(summary.error_counts).length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-3">
            Top Errors
          </p>
          <div className="space-y-2">
            {Object.entries(summary.error_counts)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([error, count]) => (
                <div
                  key={error}
                  className="flex justify-between items-center text-sm bg-gray-50 p-2 rounded"
                >
                  <span className="text-gray-700">{error}</span>
                  <span className="font-semibold text-gray-900">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
