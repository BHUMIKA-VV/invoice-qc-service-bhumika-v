import React, { useState } from "react";
import { AlertCircle, CheckCircle } from "lucide-react";
import { FileUpload } from "./components/FileUpload";
import { ValidationSummaryComponent } from "./components/ValidationSummary";
import { InvoiceResults } from "./components/InvoiceResults";
import { JSONInput } from "./components/JSONInput";
import { ValidationSummary, ExtractedData } from "./types";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [summary, setSummary] = useState<ValidationSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"upload" | "json">("upload");

  const handleFilesSelected = async (files: File[]) => {
    try {
      setError(null);
      setIsLoading(true);

      const formData = new FormData();
      files.forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch(
        `${API_URL}/extract-and-validate-pdfs`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: ExtractedData = await response.json();
      setSummary(data.validation);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process files");
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJSONSubmit = async (data: any) => {
    try {
      setError(null);
      setIsLoading(true);

      const invoices = Array.isArray(data) ? data : [data];

      const response = await fetch(
        `${API_URL}/validate-json`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(invoices),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const result: ValidationSummary = await response.json();
      setSummary(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to validate");
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setSummary(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
        {/* Header */}
        <div className="mb-8 sm:mb-12">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-2">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Invoice QC Console
            </h1>
          </div>
          <p className="text-gray-600 max-w-2xl">
            Extract and validate B2B invoices. Upload PDFs or paste JSON data
            to check for quality issues and compliance.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900">Error</p>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Main Content */}
        {!summary ? (
          <div className="space-y-6">
            {/* Tabs */}
            <div className="flex gap-2 bg-white rounded-lg p-1 border border-gray-200 w-fit">
              <button
                onClick={() => setActiveTab("upload")}
                className={`px-4 py-2 rounded font-medium transition-colors ${
                  activeTab === "upload"
                    ? "bg-blue-600 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Upload PDFs
              </button>
              <button
                onClick={() => setActiveTab("json")}
                className={`px-4 py-2 rounded font-medium transition-colors ${
                  activeTab === "json"
                    ? "bg-blue-600 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Paste JSON
              </button>
            </div>

            {/* Content */}
            {activeTab === "upload" ? (
              <FileUpload
                onFilesSelected={handleFilesSelected}
                isLoading={isLoading}
                acceptedFormats=".pdf"
              />
            ) : (
              <JSONInput onSubmit={handleJSONSubmit} isLoading={isLoading} />
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Results</h2>
              <button
                onClick={handleClear}
                className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Process New Files
              </button>
            </div>

            {/* Summary Card */}
            <ValidationSummaryComponent summary={summary} />

            {/* Results Table */}
            {summary.results.length > 0 && (
              <InvoiceResults results={summary.results} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
