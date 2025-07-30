"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  FileText,
  ImageIcon,
  FileSpreadsheet,
  AlertCircle,
  CheckCircle,
  Settings,
  Users,
  Clock,
  HardDrive,
  Activity,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import type {
  Document,
  UploadResult,
  UploadResponse,
  UploadProgress,
  WorkerSettings,
} from "@/types/document";

interface DocumentUploadProps {
  onUpload: (documents: Document[]) => void;
}

export function DocumentUpload({ onUpload }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [workerSettings, setWorkerSettings] = useState<WorkerSettings>({
    maxWorkers: 4,
    enableAutoScale: true,
    memoryLimitPerWorkerMB: 512,
    timeoutPerFileSeconds: 300,
  });

  const getFileIcon = (type: string) => {
    if (type.includes("image")) return ImageIcon;
    if (type.includes("sheet") || type.includes("excel"))
      return FileSpreadsheet;
    return FileText;
  };

  const getFileType = (file: File): "pdf" | "docx" | "image" | "xlsx" => {
    if (file.type.includes("pdf")) return "pdf";
    if (file.type.includes("word") || file.name.endsWith(".docx"))
      return "docx";
    if (file.type.includes("image")) {
      console.log("Detected image file:", file.type);
      return "image";
    }
    if (file.type.includes("sheet") || file.type.includes("excel"))
      return "xlsx";
    return "pdf"; // default
  };

  const uploadToAPI = async (files: File[]): Promise<UploadResponse> => {
    const formData = new FormData();

    // Append all files to FormData
    files.forEach((file) => {
      formData.append("files", file);
    });

    // Add worker settings if not using auto-scale
    if (!workerSettings.enableAutoScale) {
      formData.append("max_workers", workerSettings.maxWorkers.toString());
    }

    const response = await fetch("/api/document/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Upload failed with status ${response.status}`
      );
    }

    return response.json();
  };

  const initializeProgress = (files: File[]) => {
    const progress: UploadProgress[] = files.map((file) => ({
      filename: file.name,
      status: "pending",
      progress: 0,
    }));
    setUploadProgress(progress);
  };

  const updateProgress = (
    filename: string,
    updates: Partial<UploadProgress>
  ) => {
    setUploadProgress((prev) =>
      prev.map((item) =>
        item.filename === filename ? { ...item, ...updates } : item
      )
    );
  };

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      setIsUploading(true);
      setUploadError(null);
      setUploadSuccess(null);
      initializeProgress(acceptedFiles);

      try {
        // Mark all files as processing
        acceptedFiles.forEach((file) => {
          updateProgress(file.name, { status: "processing", progress: 50 });
        });

        // Call the actual API
        const apiResponse = await uploadToAPI(acceptedFiles);

        // Update progress based on results
        apiResponse.results.forEach((result) => {
          updateProgress(result.filename, {
            status: result.status === "success" ? "completed" : "error",
            progress: result.status === "success" ? 100 : 0,
            processingTime: result.processing_time || undefined,
            chunks: result.processed_chunks,
            embeddings: result.embeddings_created,
            error: result.error || undefined,
          });
        });

        // Convert API response to Document format for frontend
        const uploadedDocuments: Document[] = apiResponse.results
          .filter((result) => result.status === "success")
          .map((result, index) => ({
            id: Math.random().toString(36).substr(2, 9),
            name: result.filename,
            type: getFileType(
              acceptedFiles.find((f) => f.name === result.filename)!
            ),
            size:
              acceptedFiles.find((f) => f.name === result.filename)?.size || 0,
            uploadedAt: new Date(),
            status: "processed" as const,
            processingTime: result.processing_time || undefined,
            chunks: result.processed_chunks,
            embeddings: result.embeddings_created,
          }));

        // Handle partial success
        if (apiResponse.summary.failed_files > 0) {
          const failedFiles = apiResponse.results
            .filter((result) => result.status === "error")
            .map((result) => result.filename)
            .join(", ");

          setUploadError(`Failed to process: ${failedFiles}`);
        }

        // Show success message with worker info
        if (apiResponse.summary.successful_files > 0) {
          const workerInfo =
            apiResponse.summary.workers_used > 1
              ? ` using ${apiResponse.summary.workers_used} workers`
              : "";

          setUploadSuccess(
            `Successfully processed ${apiResponse.summary.successful_files} file(s)${workerInfo}. ` +
              `${apiResponse.summary.total_chunks_processed} chunks, ${apiResponse.summary.total_embeddings_created} embeddings created ` +
              `in ${apiResponse.summary.total_processing_time.toFixed(2)}s.`
          );
          setTimeout(() => {
            setUploadSuccess(null);
          }, 8000);
        }

        // Update parent component with successful uploads
        if (uploadedDocuments.length > 0) {
          onUpload(uploadedDocuments);
        }
      } catch (error) {
        console.error("Upload failed:", error);

        // Mark all files as failed
        acceptedFiles.forEach((file) => {
          updateProgress(file.name, {
            status: "error",
            progress: 0,
            error: error instanceof Error ? error.message : "Upload failed",
          });
        });

        setUploadError(
          error instanceof Error
            ? error.message
            : "Upload failed. Please try again."
        );
        setTimeout(() => {
          setUploadError(null);
        }, 8000);
      } finally {
        setIsUploading(false);
        // Clear progress after a delay
        setTimeout(() => {
          setUploadProgress([]);
        }, 10000);
      }
    },
    [onUpload, workerSettings]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
      "image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    },
    multiple: true,
    disabled: isUploading,
  });

  return (
    <div className="space-y-4">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Upload Documents
          </h2>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              {workerSettings.enableAutoScale
                ? "Auto"
                : workerSettings.maxWorkers}{" "}
              workers
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Worker Settings */}
        {showSettings && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg space-y-4">
            <h3 className="text-sm font-medium text-gray-700">
              Worker Settings
            </h3>

            <div className="flex items-center justify-between">
              <Label htmlFor="auto-scale" className="text-sm">
                Auto-scale workers
              </Label>
              <Switch
                checked={workerSettings.enableAutoScale}
                onCheckedChange={(checked: boolean) =>
                  setWorkerSettings((prev) => ({
                    ...prev,
                    enableAutoScale: checked,
                  }))
                }
              />
            </div>

            {!workerSettings.enableAutoScale && (
              <div className="space-y-2">
                <Label htmlFor="max-workers" className="text-sm">
                  Max workers
                </Label>
                <Input
                  type="number"
                  min="1"
                  max="8"
                  value={workerSettings.maxWorkers}
                  onChange={(e) =>
                    setWorkerSettings((prev) => ({
                      ...prev,
                      maxWorkers: Math.max(
                        1,
                        Math.min(8, parseInt(e.target.value) || 1)
                      ),
                    }))
                  }
                  className="w-20"
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
              <div className="flex items-center gap-1">
                <HardDrive className="h-3 w-3" />
                Memory: {workerSettings.memoryLimitPerWorkerMB}MB/worker
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Timeout: {workerSettings.timeoutPerFileSeconds}s/file
              </div>
            </div>
          </div>
        )}

        {/* Success Alert */}
        {uploadSuccess && (
          <Alert className="mb-4 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">
              {uploadSuccess}
            </AlertDescription>
          </Alert>
        )}

        {/* Error Alert */}
        {uploadError && (
          <Alert className="mb-4 border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              {uploadError}
            </AlertDescription>
          </Alert>
        )}

        {/* Upload Progress */}
        {uploadProgress.length > 0 && (
          <div className="mb-4 space-y-3">
            <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Processing Files
            </h3>
            {uploadProgress.map((progress) => (
              <div key={progress.filename} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1 mr-2">
                    {progress.filename}
                  </span>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        progress.status === "completed"
                          ? "success"
                          : progress.status === "error"
                          ? "destructive"
                          : progress.status === "processing"
                          ? "warning"
                          : "secondary"
                      }
                      className="text-xs"
                    >
                      {progress.status}
                    </Badge>
                    {progress.processingTime && (
                      <span className="text-xs text-gray-500">
                        {progress.processingTime.toFixed(1)}s
                      </span>
                    )}
                  </div>
                </div>
                <Progress value={progress.progress} className="h-2" />
                {progress.chunks && progress.embeddings && (
                  <div className="text-xs text-gray-500 flex justify-between">
                    <span>{progress.chunks} chunks</span>
                    <span>{progress.embeddings} embeddings</span>
                  </div>
                )}
                {progress.error && (
                  <div className="text-xs text-red-600">{progress.error}</div>
                )}
              </div>
            ))}
          </div>
        )}

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-blue-500 bg-blue-50"
              : isUploading
              ? "border-gray-300 bg-gray-50 cursor-not-allowed"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />

          <Upload
            className={`mx-auto h-12 w-12 mb-4 ${
              isUploading ? "text-gray-300" : "text-gray-400"
            }`}
          />

          {isUploading ? (
            <div className="space-y-2">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600">Processing documents...</p>
              <p className="text-xs text-gray-500">
                {uploadProgress.length > 1
                  ? `Processing ${uploadProgress.length} files with ${
                      workerSettings.enableAutoScale
                        ? "auto-scaled"
                        : workerSettings.maxWorkers
                    } workers`
                  : "This may take a few moments"}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-gray-600">
                {isDragActive
                  ? "Drop files here"
                  : "Drag & drop files here, or click to select"}
              </p>
              <p className="text-xs text-gray-500">
                Supports PDF, DOCX, XLSX, and images
              </p>
              <p className="text-xs text-gray-400">
                Multi-file uploads will use concurrent processing for faster
                results
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
