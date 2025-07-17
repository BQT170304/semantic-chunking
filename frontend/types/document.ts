export interface Document {
  id: string;
  name: string;
  type: "pdf" | "docx" | "image" | "xlsx";
  size: number;
  uploadedAt: Date;
  status: "processing" | "processed" | "error";
}

export interface UploadResult {
  filename: string;
  status: "success" | "error";
  message: string;
  processed_chunks: number;
  embeddings_created: number;
  processing_time: number | null;
  error: string | null;
}

export interface UploadResponse {
  summary: {
    total_files: number;
    successful_files: number;
    failed_files: number;
    total_chunks_processed: number;
    total_embeddings_created: number;
  };
  results: UploadResult[];
}
