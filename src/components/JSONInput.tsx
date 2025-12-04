import React, { useState } from "react";
import { validateJSON } from "../api";

interface JSONInputProps {
  onSubmit: (data: any) => void;
  isLoading: boolean;
}

export function JSONInput({ onSubmit, isLoading }: JSONInputProps) {
  const [json, setJson] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    try {
      setError("");
      const data = JSON.parse(json);

      // ⭐ Call FASTAPI backend here
      const result = await validateJSON(data);

      // ⭐ Send backend result to parent
      onSubmit(result);

    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Invalid JSON format"
      );
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-3">
        Or Paste JSON
      </h3>
      <div className="space-y-3">
        <textarea
          value={json}
          onChange={(e) => setJson(e.target.value)}
          placeholder="Paste invoice JSON array here..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          disabled={isLoading}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          onClick={handleSubmit}
          disabled={isLoading || !json.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {isLoading ? "Validating..." : "Validate JSON"}
        </button>
      </div>
    </div>
  );
}
