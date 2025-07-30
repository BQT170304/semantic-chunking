"use client";

import React, { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Plus, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { LoadingState } from "@/components/loading-state";

interface Conversation {
  id: string;
  title?: string;
  created_at?: string;
  document_count?: number;
}

interface ConversationSidebarProps {
  selectedId: string | null;
  onSelect: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  userId: string;
  handleCreate: () => void;
  reloadTrigger?: number; // Add trigger for external reload
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  selectedId,
  onSelect,
  isCollapsed,
  onToggleCollapse,
  userId,
  handleCreate,
  reloadTrigger,
}: ConversationSidebarProps) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const fetchConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/conversation/user/${userId}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch conversations");
      const data = await res.json();
      setConversations(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  // Listen for external reload trigger
  useEffect(() => {
    if (reloadTrigger) {
      fetchConversations();
    }
  }, [reloadTrigger]);

  const formatDate = (dateString?: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return date.toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  return (
    <div
      className={`bg-white border-r border-gray-200 transition-all duration-300 ${
        isCollapsed ? "w-16" : "w-80"
      } flex flex-col`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        {!isCollapsed && <h3 className="font-bold text-lg text-gray-900">Conversations</h3>}
        <div className="flex items-center gap-2">
          {!isCollapsed && (
            <Button size="sm" onClick={handleCreate} disabled={creating} className="bg-blue-600 hover:bg-blue-700">
              {creating ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={onToggleCollapse} className="p-1">
            {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {loading ? (
          <LoadingState message="Loading conversations..." size="sm" />
        ) : error ? (
          <div className="text-red-500 text-sm p-2">{error}</div>
        ) : conversations.length === 0 ? (
          <div className="text-center text-gray-500 p-4">
            {!isCollapsed && (
              <>
                <MessageSquare className="mx-auto h-8 w-8 text-gray-300 mb-2" />
                <p className="text-sm">No conversations yet</p>
                <p className="text-xs mt-1">Create your first conversation</p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {conversations.map((conv) => (
              <Card
                key={conv.id}
                className={`cursor-pointer transition-all duration-200 ${
                  selectedId === conv.id ? "bg-blue-50 border-blue-200 shadow-sm" : "hover:bg-gray-50 border-gray-100"
                }`}
                onClick={() => onSelect(conv.id)}>
                <div className="p-3">
                  {isCollapsed ? (
                    <div className="flex items-center justify-center">
                      <MessageSquare
                        className={`h-5 w-5 ${selectedId === conv.id ? "text-blue-600" : "text-gray-400"}`}
                      />
                    </div>
                  ) : (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-sm text-gray-900 truncate">
                          {conv.title || `Conversation ${conv.id.slice(-4)}`}
                        </h4>
                        {conv.document_count && conv.document_count > 0 && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                            {conv.document_count}
                          </span>
                        )}
                      </div>
                      {conv.created_at && <p className="text-xs text-gray-500">{formatDate(conv.created_at)}</p>}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationSidebar;
