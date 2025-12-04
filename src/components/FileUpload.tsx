import React, { useState } from "react";
import { Upload } from "lucide-react";

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  isLoading: boolean;
  acceptedFormats?: string;
}

export function FileUpload({
  onFilesSelected,
  isLoading,
  acceptedFormats = ".pdf",
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    onFilesSelected(files);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    onFilesSelected(files);
  };

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        dragActive
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-gray-400"
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        multiple
        accept={acceptedFormats}
        onChange={handleChange}
        className="hidden"
        id="file-input"
        disabled={isLoading}
      />
      <label htmlFor="file-input" className="cursor-pointer">
        <div className="flex flex-col items-center gap-2">
          <Upload className="w-8 h-8 text-gray-400" />
          <p className="text-sm font-medium text-gray-700">
            Drag and drop PDF files here or click to browse
          </p>
          <p className="text-xs text-gray-500">
            Upload one or more PDF invoices to extract and validate
          </p>
        </div>
      </label>
    </div>
  );
}
