import { useCallback, useEffect, useRef, useState } from "react";
import api from "@/lib/api";
import type { ChatMessage, ChatResponse, HistoryResponse, Message } from "@/types/chat";

interface UseChatOptions {
  sessionId: string | null;
  subject?: string;
}

interface UseChatReturn {
  messages: Message[];
  isLoading: boolean;
  isInterrupted: boolean;
  interruptInfo: ChatResponse["interrupt_info"] | null;
  sendMessage: (content: string) => Promise<void>;
  resumeTest: (answer: string) => Promise<void>;
  clearMessages: () => void;
}

// Helper to convert a single backend message to frontend format
function convertMessage(msg: ChatMessage, index: number): Message {
  return {
    id: `msg-${index}-${Date.now()}`,
    role: msg.type === "human" ? "user" : "assistant",
    content: msg.content,
    timestamp: new Date(),
  };
}

// Helper to convert backend messages array to frontend format
function convertMessages(backendMessages: ChatMessage[]): Message[] {
  return backendMessages
    .filter((msg) => msg.type === "human" || msg.type === "ai")
    .map((msg, index) => convertMessage(msg, index));
}

export function useChat({ sessionId, subject }: UseChatOptions): UseChatReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [interruptInfo, setInterruptInfo] = useState<ChatResponse["interrupt_info"] | null>(null);

  // Track current session to load history on session change
  const prevSessionRef = useRef<string | null>(null);

  useEffect(() => {
    if (prevSessionRef.current !== sessionId) {
      prevSessionRef.current = sessionId;

      // Clear current messages
      setMessages([]);
      setIsInterrupted(false);
      setInterruptInfo(null);

      // Load history for new session
      if (sessionId) {
        setIsLoading(true);
        api
          .get<HistoryResponse>(`/history/${sessionId}`)
          .then((response) => {
            const historyMessages = convertMessages(response.data.messages);
            setMessages(historyMessages);
          })
          .catch((error) => {
            console.error("Error loading history:", error);
            // Not a critical error - just start with empty messages
          })
          .finally(() => {
            setIsLoading(false);
          });
      }
    }
  }, [sessionId]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim()) return;

      // Add user message immediately
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await api.post<ChatResponse>("/chat", {
          query: content.trim(),
          id: sessionId,
          asignatura: subject,
        });

        const { message, interrupted, interrupt_info } = response.data;

        // Add the assistant's response message
        if (message) {
          const assistantMessage: Message = {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: message.content,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }

        setIsInterrupted(interrupted);
        setInterruptInfo(interrupt_info || null);
      } catch (error) {
        console.error("Error sending message:", error);
        // Add error message
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content:
            "Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, inténtalo de nuevo.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, subject],
  );

  const resumeTest = useCallback(
    async (answer: string) => {
      if (!sessionId || !answer.trim()) return;

      // Add user answer as message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: answer.trim(),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await api.post<ChatResponse>("/resume_chat", {
          id: sessionId,
          user_response: answer.trim(),
        });

        const { message, interrupted, interrupt_info } = response.data;

        // Add the assistant's response message
        if (message) {
          const assistantMessage: Message = {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: message.content,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
        }

        setIsInterrupted(interrupted);
        setInterruptInfo(interrupt_info || null);
      } catch (error) {
        console.error("Error resuming test:", error);
        const errorMessage: Message = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "Error al enviar tu respuesta. Por favor, inténtalo de nuevo.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId],
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setIsInterrupted(false);
    setInterruptInfo(null);
  }, []);

  return {
    messages,
    isLoading,
    isInterrupted,
    interruptInfo,
    sendMessage,
    resumeTest,
    clearMessages,
  };
}
