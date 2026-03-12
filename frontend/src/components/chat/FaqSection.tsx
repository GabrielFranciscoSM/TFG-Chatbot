import { Loader2, MessageCircleQuestion } from "lucide-react";
import { useEffect, useState } from "react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import api from "@/lib/api";
import type { Faq } from "@/types/faqs";

interface FaqSectionProps {
  subjectId: string;
}

export function FaqSection({ subjectId }: FaqSectionProps) {
  const [faqs, setFaqs] = useState<Faq[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    const fetchPublicFaqs = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.get<Faq[]>(`/subjects/${encodeURIComponent(subjectId)}/faqs`);
        if (mounted) {
          setFaqs(response.data);
        }
      } catch (err) {
        console.error("Error fetching public FAQs:", err);
        if (mounted) {
          setError("No se pudieron cargar las preguntas frecuentes.");
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    if (subjectId) {
      fetchPublicFaqs();
    }

    return () => {
      mounted = false;
    };
  }, [subjectId]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-muted-foreground">
        <Loader2 className="h-8 w-8 animate-spin mb-4" />
        <p>Cargando FAQs...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-center text-sm text-destructive bg-destructive/10 rounded-md m-4">
        {error}
      </div>
    );
  }

  if (faqs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg m-4">
        <MessageCircleQuestion className="h-12 w-12 mb-4 opacity-20" />
        <p className="text-lg font-medium">No hay FAQs disponibles</p>
        <p className="text-sm">
          El profesor aún no ha publicado preguntas frecuentes para esta asignatura.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <MessageCircleQuestion className="h-5 w-5" />
          Preguntas Frecuentes
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Aquí encontrarás las dudas más comunes resueltas por tu profesor.
        </p>
      </div>
      <div className="flex-1 overflow-y-auto p-4">
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq) => (
            <AccordionItem key={faq.id} value={faq.id}>
              <AccordionTrigger className="text-left text-sm font-medium">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-sm text-muted-foreground whitespace-pre-wrap">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </div>
  );
}
