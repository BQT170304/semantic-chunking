"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  Database,
  Layers,
  Clock,
  TrendingUp,
  Users,
  Activity,
} from "lucide-react";
import type { Document } from "@/types/document";

interface DocumentStatsProps {
  documents: Document[];
}

export function DocumentStats({ documents }: DocumentStatsProps) {
  const totalDocuments = documents.length;
  const processedDocuments = documents.filter(
    (doc) => doc.status === "processed"
  ).length;
  const totalChunks = documents.reduce(
    (sum, doc) => sum + (doc.chunks || 0),
    0
  );
  const totalEmbeddings = documents.reduce(
    (sum, doc) => sum + (doc.embeddings || 0),
    0
  );
  const avgProcessingTime =
    documents.length > 0
      ? documents
          .filter((doc) => doc.processingTime)
          .reduce((sum, doc) => sum + (doc.processingTime || 0), 0) /
        documents.filter((doc) => doc.processingTime).length
      : 0;

  const typeStats = documents.reduce((acc, doc) => {
    acc[doc.type] = (acc[doc.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (totalDocuments === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Documents</p>
            <p className="text-2xl font-bold text-gray-900">{totalDocuments}</p>
            <p className="text-xs text-green-600">
              {processedDocuments} processed
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-100 rounded-lg">
            <Layers className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Chunks</p>
            <p className="text-2xl font-bold text-gray-900">{totalChunks}</p>
            <p className="text-xs text-gray-500">
              {totalChunks > 0 ? (totalChunks / totalDocuments).toFixed(1) : 0}{" "}
              avg/doc
            </p>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-100 rounded-lg">
            <Database className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Embeddings</p>
            <p className="text-2xl font-bold text-gray-900">
              {totalEmbeddings}
            </p>
            <p className="text-xs text-gray-500">Vector database</p>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-orange-100 rounded-lg">
            <Clock className="h-5 w-5 text-orange-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600">Avg Time</p>
            <p className="text-2xl font-bold text-gray-900">
              {avgProcessingTime > 0 ? avgProcessingTime.toFixed(1) : "0"}s
            </p>
            <p className="text-xs text-gray-500">Per document</p>
          </div>
        </div>
      </Card>

      {Object.keys(typeStats).length > 1 && (
        <Card className="p-4 md:col-span-2 lg:col-span-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            File Types
          </h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(typeStats).map(([type, count]) => (
              <Badge
                key={type}
                variant="outline"
                className="flex items-center gap-1"
              >
                <span className="uppercase">{type}</span>
                <span className="text-gray-500">({count})</span>
              </Badge>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
