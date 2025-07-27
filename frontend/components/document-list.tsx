"use client";

import {
  FileText,
  ImageIcon,
  FileSpreadsheet,
  Trash2,
  Check,
  Clock,
  Database,
  Layers,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Document } from "@/types/document";

interface DocumentListProps {
  documents: Document[];
  onDocumentDelete: (documentId: string) => void;
}

export function DocumentList({
  documents,
  onDocumentDelete,
}: DocumentListProps) {
  const getFileIcon = (type: string) => {
    switch (type) {
      case "image":
        return ImageIcon;
      case "xlsx":
        return FileSpreadsheet;
      default:
        return FileText;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (
      Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
    );
  };

  if (documents.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Documents</h2>
        <p className="text-sm text-gray-500 text-center py-8">
          No documents uploaded yet
        </p>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
        <span className="text-sm text-gray-500">
          {documents.length} document{documents.length !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="space-y-3">
        {documents.map((doc) => {
          const Icon = getFileIcon(doc.type);

          return (
            <div
              key={doc.id}
              className="flex items-center space-x-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300"
            >
              <Icon className="h-5 w-5 text-gray-500 flex-shrink-0" />

              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {doc.name}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-500">
                    {formatFileSize(doc.size)} • {doc.type.toUpperCase()}
                  </p>
                  {doc.processingTime && (
                    <Badge
                      variant="secondary"
                      className="text-xs flex items-center gap-1"
                    >
                      <Clock className="h-3 w-3" />
                      {doc.processingTime.toFixed(1)}s
                    </Badge>
                  )}
                </div>
                {(doc.chunks || doc.embeddings) && (
                  <div className="flex items-center gap-2 mt-1">
                    {doc.chunks && (
                      <Badge
                        variant="outline"
                        className="text-xs flex items-center gap-1"
                      >
                        <Layers className="h-3 w-3" />
                        {doc.chunks} chunks
                      </Badge>
                    )}
                    {doc.embeddings && (
                      <Badge
                        variant="outline"
                        className="text-xs flex items-center gap-1"
                      >
                        <Database className="h-3 w-3" />
                        {doc.embeddings} embeddings
                      </Badge>
                    )}
                  </div>
                )}
              </div>

              <div className="flex items-center space-x-2">
                {doc.status === "processed" && (
                  <Check className="h-4 w-4 text-green-500" />
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDocumentDelete(doc.id)}
                  className="text-gray-400 hover:text-red-500"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
