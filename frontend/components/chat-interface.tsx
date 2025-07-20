"use client";

import type React from "react";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { Document } from "@/types/document";
import type { ChatMessage, ChatResponse } from "@/types/message";

interface ChatInterfaceProps {
  documents: Document[];
}

export function ChatInterface({ documents }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || documents.length === 0) return;

    const userMessage: ChatMessage = {
      role: "user",
      message: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsLoading(true);

    try {
      const chatHistory = messages.map((msg) => ({
        role: msg.role,
        content: msg.message,
      }));

      chatHistory.push({
        role: "user",
        content: currentInput,
      });

      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentInput,
          documents: documents.map((doc) => doc.name),
          chat_history: chatHistory,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ChatResponse = await response.json();

      const assistantMessage: ChatMessage = {
        role: "assistant",
        message: result.message,
        timestamp: new Date(),
        sources: result.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Chat error:", error);

      // Add error message to chat
      const errorMessage: ChatMessage = {
        role: "assistant",
        message: "Sorry, I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat</h2>
        {documents.length === 0 && <p className="text-sm text-gray-500 mt-1">Upload documents to start chatting</p>}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            {documents.length > 0 ? (
              <>
                <p>Start a conversation about your documents</p>
                <p className="text-sm mt-2">Ask questions, request summaries, or explore insights</p>
              </>
            ) : (
              <>
                <p>Upload documents to start chatting</p>
                <p className="text-sm mt-2">Drag and drop files to begin</p>
              </>
            )}
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              {message.role === "assistant" && (
                <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Bot className="h-4 w-4 text-blue-600" />
                </div>
              )}

              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                }`}>
                <p className="text-sm whitespace-pre-wrap">{message.message}</p>
                {message.role === "assistant" && message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500 font-medium mb-1">Sources:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.sources.slice(0, 3).map((source, sourceIndex) => (
                        <span
                          key={sourceIndex}
                          className="inline-flex items-center px-2 py-1 rounded-md bg-gray-200 text-xs text-gray-600"
                          title={`${source.filename} - ${source.section_title}`}>
                          {source.filename.length > 20 ? `${source.filename.substring(0, 20)}...` : source.filename}
                          {source.section_title !== "unknown" && (
                            <span className="ml-1 text-gray-400">({source.section_title})</span>
                          )}
                        </span>
                      ))}
                      {message.sources.length > 3 && (
                        <span className="inline-flex items-center px-2 py-1 rounded-md bg-gray-200 text-xs text-gray-600">
                          +{message.sources.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {message.role === "user" && (
                <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-gray-600" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Bot className="h-4 w-4 text-blue-600" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={documents.length > 0 ? "Ask a question about your documents..." : "Upload documents first..."}
            disabled={documents.length === 0 || isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={!input.trim() || documents.length === 0 || isLoading}
            className="bg-blue-600 hover:bg-blue-700">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </Card>
  );
}
