import { useState } from "react";
import { Copy, Edit2, Loader2, Save, Trash2, X, CheckCircle, Globe } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useFaqs } from "@/hooks/useFaqs";
import type { Faq, FaqUpdate } from "@/types/faqs";

interface FaqManagerProps {
  subject: string | null;
}

export function FaqManager({ subject }: FaqManagerProps) {
  const { faqs, isLoading, isGenerating, error, generateFaqs, updateFaq, deleteFaq, publishFaq } =
    useFaqs(subject);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editQuestion, setEditQuestion] = useState("");
  const [editAnswer, setEditAnswer] = useState("");

  const handleEditClick = (faq: Faq) => {
    setEditingId(faq.id);
    setEditQuestion(faq.question);
    setEditAnswer(faq.answer);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditQuestion("");
    setEditAnswer("");
  };

  const handleSaveEdit = async (id: string) => {
    const updateData: FaqUpdate = {
      question: editQuestion,
      answer: editAnswer,
    };
    try {
      await updateFaq(id, updateData);
      setEditingId(null);
    } catch (e) {
      // Error is handled in the hook
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("¿Estás seguro de que quieres eliminar esta FAQ?")) {
      await deleteFaq(id);
    }
  };

  if (!subject) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Gestor de FAQs</h2>
          <p className="text-muted-foreground">
            Asignatura: <span className="uppercase font-medium">{subject}</span>
          </p>
        </div>
        <Button onClick={generateFaqs} disabled={isGenerating}>
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Generando...
            </>
          ) : (
            <>
              <Copy className="mr-2 h-4 w-4" />
              Generar FAQs
            </>
          )}
        </Button>
      </div>

      {error && <div className="bg-destructive/15 text-destructive p-4 rounded-md">{error}</div>}

      {isLoading ? (
        <div className="flex justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : faqs.length === 0 ? (
        <Card className="flex items-center justify-center p-12 text-center text-muted-foreground">
          <div className="flex flex-col items-center">
            <Copy className="h-12 w-12 mb-4 opacity-20" />
            <p className="text-lg">No hay FAQs generadas para esta asignatura.</p>
            <p className="text-sm">
              Usa el botón "Generar FAQs" para extraerlas de los documentos.
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-1">
          {faqs.map((faq) => (
            <Card key={faq.id} className="relative">
              {editingId === faq.id ? (
                // Edit Mode
                <>
                  <CardHeader>
                    <Input
                      value={editQuestion}
                      onChange={(e) => setEditQuestion(e.target.value)}
                      placeholder="Pregunta"
                      className="font-semibold"
                    />
                  </CardHeader>
                  <CardContent>
                    <textarea
                      value={editAnswer}
                      onChange={(e) => setEditAnswer(e.target.value)}
                      placeholder="Respuesta"
                      className="w-full min-h-[100px] flex rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    />
                  </CardContent>
                  <CardFooter className="justify-end space-x-2">
                    <Button variant="outline" size="sm" onClick={handleCancelEdit}>
                      <X className="h-4 w-4 mr-1" /> Cancelar
                    </Button>
                    <Button size="sm" onClick={() => handleSaveEdit(faq.id)}>
                      <Save className="h-4 w-4 mr-1" /> Guardar
                    </Button>
                  </CardFooter>
                </>
              ) : (
                // View Mode
                <>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg flex items-center gap-2">
                        {faq.question}
                      </CardTitle>
                      <div className="flex gap-2">
                        {faq.status === "published" ? (
                          <span className="flex items-center text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full dark:bg-green-900 dark:text-green-300">
                            <CheckCircle className="h-3 w-3 mr-1" /> Publicada
                          </span>
                        ) : (
                          <span className="flex items-center text-xs text-amber-600 bg-amber-100 px-2 py-1 rounded-full dark:bg-amber-900 dark:text-amber-300">
                            Borrador
                          </span>
                        )}
                        {faq.cluster_id !== undefined && faq.cluster_id !== null && (
                          <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded-full">
                            Tópico: {faq.cluster_id}
                          </span>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-foreground whitespace-pre-wrap">{faq.answer}</p>
                  </CardContent>
                  <CardFooter className="justify-end space-x-2 bg-muted/20 py-3">
                    {faq.status !== "published" && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => publishFaq(faq.id)}
                        className="text-primary border-primary/50 hover:bg-primary/10"
                      >
                        <Globe className="h-4 w-4 mr-1" /> Publicar
                      </Button>
                    )}
                    <Button variant="ghost" size="sm" onClick={() => handleEditClick(faq)}>
                      <Edit2 className="h-4 w-4 mr-1" /> Editar
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(faq.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4 mr-1" /> Eliminar
                    </Button>
                  </CardFooter>
                </>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
