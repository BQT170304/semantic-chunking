"use client";

import { useState } from "react";
import { DocumentUpload } from "@/components/document-upload";
import { DocumentList } from "@/components/document-list";
import { ChatInterface } from "@/components/chat-interface";
import type { Document } from "@/types/document";

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);

  const handleDocumentUpload = (newDocuments: Document[]) => {
    setDocuments((prev) => [...prev, ...newDocuments]);
  };

  const handleDocumentDelete = (documentId: string) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== documentId));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Chat</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Document Management */}
          <div className="lg:col-span-1 space-y-6">
            <DocumentUpload onUpload={handleDocumentUpload} />
            <DocumentList documents={documents} onDocumentDelete={handleDocumentDelete} />
          </div>

          {/* Right Panel - Chat Interface */}
          <div className="lg:col-span-2">
            <ChatInterface documents={documents} />
          </div>
        </div>
      </div>
    </div>
  );
}
