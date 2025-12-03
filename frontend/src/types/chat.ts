// Types for chat functionality

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  subject: string;
  created_at: string;
  last_active: string;
}

export interface ChatRequest {
  query: string;
  id: string;
  asignatura?: string;
}

export interface InterruptInfo {
  action: string;
  question_num: number;
  total_questions: number;
  question_text: string;
}

// Backend message format
export interface ChatMessage {
  type: string; // 'ai', 'human', 'tool', 'system'
  content: string;
}

// Response from /chat and /resume_chat - only returns the last message
export interface ChatResponse {
  message: ChatMessage | null;
  interrupted: boolean;
  interrupt_info?: InterruptInfo;
}

// Response from /history - returns all messages
export interface HistoryResponse {
  messages: ChatMessage[];
}

export interface ResumeRequest {
  id: string;
  user_response: string;
}
