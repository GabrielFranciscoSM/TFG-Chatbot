import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";
import type { TopicExtractRequest, TopicResult } from "@/types/topics";

export function useTopics(subject: string | null) {
  const [topics, setTopics] = useState<TopicResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTopics = useCallback(async () => {
    if (!subject) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<TopicResult[]>(
        `/professor/subjects/${encodeURIComponent(subject)}/topics`,
      );
      setTopics(response.data);
    } catch (err) {
      console.error("Error fetching topics:", err);
      setError("Error al cargar los tópicos");
    } finally {
      setIsLoading(false);
    }
  }, [subject]);

  const extractTopics = useCallback(
    async (options: Omit<TopicExtractRequest, "subject"> = {}) => {
      if (!subject) return;

      setIsExtracting(true);
      setError(null);
      try {
        await api.post(`/professor/subjects/${encodeURIComponent(subject)}/topics/extract`, {
          subject,
          ...options,
        });
        // Refresh the topics after extracting
        await fetchTopics();
      } catch (err) {
        console.error("Error extracting topics:", err);
        setError("Error al extraer los tópicos. Puede que el servicio no esté disponible.");
        throw err;
      } finally {
        setIsExtracting(false);
      }
    },
    [subject, fetchTopics],
  );

  useEffect(() => {
    if (subject) {
      fetchTopics();
    } else {
      setTopics([]);
    }
  }, [subject, fetchTopics]);

  return {
    topics,
    isLoading,
    isExtracting,
    error,
    refetch: fetchTopics,
    extractTopics,
  };
}
