import { useState, useEffect, useCallback } from "react";
import api from "@/lib/api";
import type { ChatSession } from "@/types/chat";

interface UseSessionsReturn {
  sessions: ChatSession[];
  isLoading: boolean;
  error: string | null;
  createSession: (title: string, subject: string) => Promise<ChatSession | null>;
  deleteSession: (sessionId: string) => Promise<boolean>;
  refreshSessions: () => Promise<void>;
}

export function useSessions(): UseSessionsReturn {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await api.get<ChatSession[]>("/sessions");
      // Sort by last_active descending
      const sorted = response.data.sort(
        (a, b) => new Date(b.last_active).getTime() - new Date(a.last_active).getTime()
      );
      setSessions(sorted);
    } catch (err) {
      console.error("Error fetching sessions:", err);
      setError("Error al cargar las sesiones");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const createSession = useCallback(async (title: string, subject: string): Promise<ChatSession | null> => {
    try {
      const response = await api.post<ChatSession>("/sessions", {
        title,
        subject,
      });
      const newSession = response.data;
      setSessions(prev => [newSession, ...prev]);
      return newSession;
    } catch (err) {
      console.error("Error creating session:", err);
      setError("Error al crear la sesión");
      return null;
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: string): Promise<boolean> => {
    try {
      await api.delete(`/sessions/${sessionId}`);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      return true;
    } catch (err) {
      console.error("Error deleting session:", err);
      setError("Error al eliminar la sesión");
      return false;
    }
  }, []);

  return {
    sessions,
    isLoading,
    error,
    createSession,
    deleteSession,
    refreshSessions: fetchSessions,
  };
}
