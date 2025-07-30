"use client";

import React from "react";
import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { Document } from "@/types/document";

interface UploadedFilesHeaderProps {
  documents: Document[];
  onDocumentDelete?: (documentId: string) => void;
}

export function UploadedFilesHeader({ documents, onDocumentDelete }: UploadedFilesHeaderProps) {
  if (documents.length === 0) {
    return null;
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <Card className="p-4 mb-4 w-full">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-900">Uploaded Documents ({documents.length})</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        {documents.map((doc) => {
          return (
            <div
              key={doc.id}
              className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm">
              <div className="flex flex-col min-w-0">
                <span className="font-medium text-gray-900 truncate max-w-32">{doc.name}</span>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{formatFileSize(doc.size)}</span>
                  {doc.chunks && <span>• {doc.chunks} chunks</span>}
                  {doc.processingTime && <span>• {doc.processingTime.toFixed(1)}s</span>}
                </div>
              </div>
              {onDocumentDelete && (
                <button
                  onClick={() => onDocumentDelete(doc.id)}
                  className="ml-2 p-1 hover:bg-gray-200 rounded transition-colors"
                  title="Remove document">
                  <X className="h-3 w-3 text-gray-400 hover:text-gray-600" />
                </button>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}
