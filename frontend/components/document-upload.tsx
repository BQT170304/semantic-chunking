"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, ImageIcon, FileSpreadsheet, AlertCircle, CheckCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { Document, UploadResult, UploadResponse } from "@/types/document";

interface DocumentUploadProps {
  onUpload: (documents: Document[]) => void;
}

export function DocumentUpload({ onUpload }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  const getFileIcon = (type: string) => {
    if (type.includes("image")) return ImageIcon;
    if (type.includes("sheet") || type.includes("excel")) return FileSpreadsheet;
    return FileText;
  };

  const getFileType = (file: File): "pdf" | "docx" | "image" | "xlsx" => {
    if (file.type.includes("pdf")) return "pdf";
    if (file.type.includes("word") || file.name.endsWith(".docx")) return "docx";
    if (file.type.includes("image")) {
      console.log("Detected image file:", file.type);
      return "image";
    }
    if (file.type.includes("sheet") || file.type.includes("excel")) return "xlsx";
    return "pdf"; // default
  };

  const uploadToAPI = async (files: File[]): Promise<UploadResponse> => {
    const formData = new FormData();

    // Append all files to FormData
    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch("/api/document/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
    }

    return response.json();
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setIsUploading(true);
      setUploadError(null);
      setUploadSuccess(null);

      try {
        // Call the actual API
        const apiResponse = await uploadToAPI(acceptedFiles);

        // Convert API response to Document format for frontend
        const uploadedDocuments: Document[] = apiResponse.results
          .filter((result) => result.status === "success")
          .map((result, index) => ({
            id: Math.random().toString(36).substr(2, 9),
            name: result.filename,
            type: getFileType(acceptedFiles.find((f) => f.name === result.filename)!),
            size: acceptedFiles.find((f) => f.name === result.filename)?.size || 0,
            uploadedAt: new Date(),
            status: "processed" as const,
          }));

        // Handle partial success
        if (apiResponse.summary.failed_files > 0) {
          const failedFiles = apiResponse.results
            .filter((result) => result.status === "error")
            .map((result) => result.filename)
            .join(", ");

          setUploadError(`Failed to process: ${failedFiles}`);
        }

        // Show success message
        if (apiResponse.summary.successful_files > 0) {
          setUploadSuccess(
            `Successfully processed ${apiResponse.summary.successful_files} file(s). ` +
              `${apiResponse.summary.total_chunks_processed} chunks, ${apiResponse.summary.total_embeddings_created} embeddings created.`
          );
          setTimeout(() => {
            setUploadSuccess(null);
          }, 5000);
        }

        // Update parent component with successful uploads
        if (uploadedDocuments.length > 0) {
          onUpload(uploadedDocuments);
        }
      } catch (error) {
        console.error("Upload failed:", error);
        setUploadError(error instanceof Error ? error.message : "Upload failed. Please try again.");
        setTimeout(() => {
          setUploadSuccess(null);
        }, 5000);
      } finally {
        setIsUploading(false);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
      "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    },
    multiple: true,
    disabled: isUploading,
  });

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h2>

      {/* Success Alert */}
      {uploadSuccess && (
        <Alert className="mb-4 border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{uploadSuccess}</AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {uploadError && (
        <Alert className="mb-4 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{uploadError}</AlertDescription>
        </Alert>
      )}

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : isUploading
            ? "border-gray-300 bg-gray-50 cursor-not-allowed"
            : "border-gray-300 hover:border-gray-400"
        }`}>
        <input {...getInputProps()} />

        <Upload className={`mx-auto h-12 w-12 mb-4 ${isUploading ? "text-gray-300" : "text-gray-400"}`} />

        {isUploading ? (
          <div className="space-y-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-600">Processing documents...</p>
            <p className="text-xs text-gray-500">This may take a few moments</p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm text-gray-600">
              {isDragActive ? "Drop files here" : "Drag & drop files here, or click to select"}
            </p>
            <p className="text-xs text-gray-500">Supports PDF, DOCX, XLSX, and images</p>
          </div>
        )}
      </div>
    </Card>
  );
}
