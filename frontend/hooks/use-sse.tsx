import { useEffect, useState, useCallback, useRef } from "react";

export interface ProcessingEvent {
  event_type: string;
  session_id: string;
  filename: string;
  status: string;
  progress: number;
  chunks?: number;
  embeddings?: number;
  processing_time?: number;
  error?: string;
}

export interface UseSSEOptions {
  onEvent?: (event: ProcessingEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnect?: boolean;
  reconnectInterval?: number;
}

export interface UseSSEReturn {
  isConnected: boolean;
  events: ProcessingEvent[];
  connect: (sessionId: string) => void;
  disconnect: () => void;
  clearEvents: () => void;
  latestEvent: ProcessingEvent | null;
}

export function useSSE(options: UseSSEOptions = {}): UseSSEReturn {
  const {
    onEvent,
    onError,
    onOpen,
    onClose,
    reconnect = false,
    reconnectInterval = 3000,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<ProcessingEvent[]>([]);
  const [latestEvent, setLatestEvent] = useState<ProcessingEvent | null>(null);

  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const currentSessionIdRef = useRef<string | null>(null);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setIsConnected(false);
    currentSessionIdRef.current = null;
  }, []);

  const connect = useCallback(
    (sessionId: string) => {
      // Disconnect existing connection
      disconnect();

      currentSessionIdRef.current = sessionId;

      try {
        // Use the backend API URL from environment or fallback to localhost
        const baseUrl =
          process.env.NEXT_PUBLIC_UPLOAD_API_URL || "http://localhost:8000";
        const eventSource = new EventSource(
          `${baseUrl}/api/documents/events/${sessionId}`
        );

        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
          setIsConnected(true);
          onOpen?.();
        };

        eventSource.onmessage = (event) => {
          try {
            const data: ProcessingEvent = JSON.parse(event.data);
            setEvents((prev) => [...prev, data]);
            setLatestEvent(data);
            onEvent?.(data);
          } catch (error) {
            console.error("Failed to parse SSE event:", error);
          }
        };

        eventSource.onerror = (error) => {
          console.error("SSE error:", error);
          setIsConnected(false);
          onError?.(error);

          // Check if connection was closed (readyState === 2)
          if (eventSource.readyState === EventSource.CLOSED) {
            onClose?.();
          }

          // Attempt to reconnect if enabled and connection is closed
          if (
            reconnect &&
            currentSessionIdRef.current &&
            eventSource.readyState === EventSource.CLOSED
          ) {
            reconnectTimeoutRef.current = setTimeout(() => {
              if (currentSessionIdRef.current) {
                connect(currentSessionIdRef.current);
              }
            }, reconnectInterval);
          }
        };
      } catch (error) {
        console.error("Failed to create EventSource:", error);
        setIsConnected(false);
      }
    },
    [
      disconnect,
      onEvent,
      onError,
      onOpen,
      onClose,
      reconnect,
      reconnectInterval,
    ]
  );

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLatestEvent(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    events,
    connect,
    disconnect,
    clearEvents,
    latestEvent,
  };
}
