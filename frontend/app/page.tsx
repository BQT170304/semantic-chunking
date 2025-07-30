"use client";

import { useState, useEffect } from "react";
import { DocumentUploadEnhanced } from "@/components/document-upload-enhanced";
import { ChatInterface } from "@/components/chat-interface";
import { UploadedFilesHeader } from "@/components/uploaded-files-header";
import type { Document } from "@/types/document";
import AuthForm from "@/components/auth-form";
import ConversationSidebar from "@/components/conversation-sidebar";

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [user, setUser] = useState<{ id: number; username: string; phone: string } | null>(null);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [showUpload, setShowUpload] = useState(true);

  useEffect(() => {
    const userInfo = typeof window !== "undefined" ? localStorage.getItem("user_info") : null;
    setUser(userInfo ? JSON.parse(userInfo) : null);
  }, []);

  const handleAuthSuccess = (userInfo: { id: number; username: string; phone: string }) => {
    setUser(userInfo);
  };

  if (!user) {
    return <AuthForm onAuthSuccess={handleAuthSuccess} />;
  }

  const handleDocumentUpload = (newDocuments: Document[]) => {
    setDocuments((prev: Document[]) => [...prev, ...newDocuments]);
    setShowUpload(false); // Hide upload after successful upload
  };

  const handleUploadCancel = () => {
    setShowUpload(true);
    setIsUploading(false);
  };

  const handleConversationSelect = (conversationId: string) => {
    setSelectedConversationId(conversationId);
    setShowUpload(false); // Hide upload when a conversation is selected
  };

  const handleDocumentsUpdate = (updatedDocuments: Document[]) => {
    setDocuments(updatedDocuments);
  };

  const handleNewConversation = () => {
    setSelectedConversationId(null);
    setDocuments([]);
    setShowUpload(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex h-screen">
        {/* Left Sidebar - Conversations */}
        <ConversationSidebar
          handleCreate={handleNewConversation}
          selectedId={selectedConversationId}
          onSelect={handleConversationSelect}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          userId={user.id.toString()}
        />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Semantic Document Processing</h1>
                <p className="text-gray-600 text-sm">
                  Upload documents and chat with them using AI-powered semantic search
                </p>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">Welcome, {user.username}</span>
                <button
                  onClick={() => {
                    localStorage.removeItem("user_info");
                    window.location.reload();
                  }}
                  className="text-sm text-red-600 hover:text-red-700">
                  Logout
                </button>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="flex-1 overflow-auto">
            <div className="container mx-auto px-6 py-6">
              <div className="grid grid-cols-1 gap-8">
                {/* Left Panel - Upload & Document Management */}
                {/* <div className="lg:col-span-1 space-y-6"> */}
                {/* Upload Section */}
                {showUpload && !selectedConversationId && (
                  <DocumentUploadEnhanced
                    userId={user.id.toString()}
                    onUpload={handleDocumentUpload}
                    onCancel={handleUploadCancel}
                    isUploading={isUploading}
                    setIsUploading={setIsUploading}
                  />
                )}
                {/* Right Panel - Chat Interface */}
                {!showUpload && (
                  <div className="space-y-4">
                    {/* Uploaded Files Header */}
                    <UploadedFilesHeader documents={documents} />

                    {/* Chat Interface */}
                    {selectedConversationId ? (
                      <ChatInterface
                        documents={documents}
                        conversationId={selectedConversationId}
                        onDocumentsUpdate={handleDocumentsUpdate}
                      />
                    ) : (
                      <div className="bg-white rounded-lg shadow p-8 text-center">
                        <div className="text-gray-500">
                          <p className="text-lg font-medium mb-2">Ready to Chat!</p>
                          <p className="text-sm">
                            Select a conversation from the sidebar to start chatting with your documents.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
