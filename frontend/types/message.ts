export interface Source {
  filename: string;
  section_title: string;
  content: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  message: string;
  timestamp?: Date;
  sources?: Source[];
}

export interface ChatResponse {
  message: string;
  sources?: Source[];
}
