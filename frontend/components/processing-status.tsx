import React from "react";
import { ProcessingEvent } from "@/hooks/use-sse";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  CheckCircle,
  XCircle,
  Clock,
  FileText,
  Package,
  Zap,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ProcessingStatusProps {
  events: ProcessingEvent[];
  isConnected: boolean;
  className?: string;
}

const getEventIcon = (eventType: string) => {
  switch (eventType) {
    case "file_started":
      return <Clock className="h-4 w-4" />;
    case "parsing_completed":
      return <FileText className="h-4 w-4" />;
    case "chunking_completed":
      return <Package className="h-4 w-4" />;
    case "file_completed":
      return <CheckCircle className="h-4 w-4" />;
    case "file_failed":
      return <XCircle className="h-4 w-4" />;
    default:
      return <Zap className="h-4 w-4" />;
  }
};

const getEventColor = (eventType: string, status: string) => {
  if (status === "error") return "destructive";

  switch (eventType) {
    case "file_started":
      return "secondary";
    case "parsing_completed":
      return "outline";
    case "chunking_completed":
      return "outline";
    case "file_completed":
      return "default";
    case "file_failed":
      return "destructive";
    default:
      return "secondary";
  }
};

const formatEventType = (eventType: string) => {
  return eventType
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const formatProcessingTime = (time?: number) => {
  if (!time) return "";
  return time < 1 ? `${(time * 1000).toFixed(0)}ms` : `${time.toFixed(2)}s`;
};

export function ProcessingStatus({
  events,
  isConnected,
  className,
}: ProcessingStatusProps) {
  // Group events by filename
  const eventsByFile = events.reduce((acc, event) => {
    if (!acc[event.filename]) {
      acc[event.filename] = [];
    }
    acc[event.filename].push(event);
    return acc;
  }, {} as Record<string, ProcessingEvent[]>);

  const totalFiles = Object.keys(eventsByFile).length;
  const completedFiles = Object.values(eventsByFile).filter((fileEvents) =>
    fileEvents.some((event) => event.event_type === "file_completed")
  ).length;

  const failedFiles = Object.values(eventsByFile).filter((fileEvents) =>
    fileEvents.some((event) => event.event_type === "file_failed")
  ).length;

  if (events.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Processing Status
            <Badge variant={isConnected ? "default" : "secondary"}>
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            No processing events yet. Upload files to see real-time progress.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Processing Status</span>
          <div className="flex items-center gap-2">
            <Badge variant={isConnected ? "default" : "secondary"}>
              {isConnected ? "Connected" : "Disconnected"}
            </Badge>
            <Badge variant="outline">
              {completedFiles}/{totalFiles} completed
            </Badge>
            {failedFiles > 0 && (
              <Badge variant="destructive">{failedFiles} failed</Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {Object.entries(eventsByFile).map(([filename, fileEvents]) => {
          const latestEvent = fileEvents[fileEvents.length - 1];
          const isCompleted = fileEvents.some(
            (e) => e.event_type === "file_completed"
          );
          const isFailed = fileEvents.some(
            (e) => e.event_type === "file_failed"
          );

          return (
            <div key={filename} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getEventIcon(latestEvent.event_type)}
                  <span
                    className="font-medium text-sm truncate max-w-[200px]"
                    title={filename}
                  >
                    {filename}
                  </span>
                  <Badge
                    variant={getEventColor(
                      latestEvent.event_type,
                      latestEvent.status
                    )}
                    className="text-xs"
                  >
                    {formatEventType(latestEvent.event_type)}
                  </Badge>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {latestEvent.chunks && (
                    <span>{latestEvent.chunks} chunks</span>
                  )}
                  {latestEvent.embeddings && (
                    <span>{latestEvent.embeddings} embeddings</span>
                  )}
                  {latestEvent.processing_time && (
                    <span>
                      {formatProcessingTime(latestEvent.processing_time)}
                    </span>
                  )}
                </div>
              </div>

              {!isCompleted && !isFailed && (
                <Progress value={latestEvent.progress} className="h-2" />
              )}

              {latestEvent.error && (
                <div className="text-xs text-destructive bg-destructive/10 p-2 rounded">
                  {latestEvent.error}
                </div>
              )}

              {/* Show recent events for this file */}
              <div className="space-y-1">
                {fileEvents.slice(-3).map((event, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-xs text-muted-foreground pl-6"
                  >
                    {getEventIcon(event.event_type)}
                    <span>{formatEventType(event.event_type)}</span>
                    {event.chunks && <span>({event.chunks} chunks)</span>}
                    {event.processing_time && (
                      <span className="ml-auto">
                        {formatProcessingTime(event.processing_time)}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
