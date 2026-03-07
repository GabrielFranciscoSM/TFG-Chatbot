import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";
import type { Faq, FaqUpdate } from "@/types/faqs";

export function useFaqs(subject: string | null) {
  const [faqs, setFaqs] = useState<Faq[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFaqs = useCallback(async () => {
    if (!subject) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<Faq[]>(
        `/professor/subjects/${encodeURIComponent(subject)}/faqs`,
      );
      setFaqs(response.data);
    } catch (err) {
      console.error("Error fetching FAQs:", err);
      setError("Error al cargar las FAQs");
    } finally {
      setIsLoading(false);
    }
  }, [subject]);

  const generateFaqs = useCallback(async () => {
    if (!subject) return;

    setIsGenerating(true);
    setError(null);
    try {
      await api.post(`/professor/subjects/${encodeURIComponent(subject)}/faqs/generate`, {});
      // Refresh the FAQs after generating
      await fetchFaqs();
    } catch (err) {
      console.error("Error generating FAQs:", err);
      setError("Error al generar las FAQs. Puede que el servicio no esté disponible.");
      throw err;
    } finally {
      setIsGenerating(false);
    }
  }, [subject, fetchFaqs]);

  const updateFaq = useCallback(
    async (faqId: string, data: FaqUpdate) => {
      if (!subject) return;
      setError(null);
      try {
        await api.put(
          `/professor/subjects/${encodeURIComponent(subject)}/faqs/${encodeURIComponent(faqId)}`,
          data,
        );
        await fetchFaqs();
      } catch (err) {
        console.error("Error updating FAQ:", err);
        setError("Error al actualizar la FAQ");
        throw err;
      }
    },
    [subject, fetchFaqs],
  );

  const deleteFaq = useCallback(
    async (faqId: string) => {
      if (!subject) return;
      setError(null);
      try {
        await api.delete(
          `/professor/subjects/${encodeURIComponent(subject)}/faqs/${encodeURIComponent(faqId)}`,
        );
        await fetchFaqs();
      } catch (err) {
        console.error("Error deleting FAQ:", err);
        setError("Error al eliminar la FAQ");
        throw err;
      }
    },
    [subject, fetchFaqs],
  );

  const publishFaq = useCallback(
    async (faqId: string) => {
      if (!subject) return;
      setError(null);
      try {
        await api.patch(
          `/professor/subjects/${encodeURIComponent(subject)}/faqs/${encodeURIComponent(faqId)}/publish`,
        );
        await fetchFaqs();
      } catch (err) {
        console.error("Error publishing FAQ:", err);
        setError("Error al publicar la FAQ");
        throw err;
      }
    },
    [subject, fetchFaqs],
  );

  useEffect(() => {
    if (subject) {
      fetchFaqs();
    } else {
      setFaqs([]);
    }
  }, [subject, fetchFaqs]);

  return {
    faqs,
    isLoading,
    isGenerating,
    error,
    refetch: fetchFaqs,
    generateFaqs,
    updateFaq,
    deleteFaq,
    publishFaq,
  };
}
