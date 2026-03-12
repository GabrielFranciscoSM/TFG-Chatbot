import { BarChart2, Loader2, Settings2 } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTopics } from "@/hooks/useTopics";
import type { TopicExtractRequest } from "@/types/topics";
import { TopicsGraph } from "./TopicsGraph";

interface TopicsDashboardProps {
  subject: string | null;
}

export function TopicsDashboard({ subject }: TopicsDashboardProps) {
  const { topics, isLoading, isExtracting, error, extractTopics } = useTopics(subject);

  const [vectorizerType, setVectorizerType] = useState<string>("tfidf");
  const [costFunction, setCostFunction] = useState<string>("frobenius");
  const [kValue, setKValue] = useState<string>("auto");

  const handleExtract = async () => {
    if (!subject) return;

    const options: Omit<TopicExtractRequest, "subject"> = {
      vectorizer_type: vectorizerType,
      cost_function: costFunction,
      k: kValue === "auto" ? null : parseInt(kValue, 10),
    };

    await extractTopics(options);
  };

  if (!subject) return null;

  // The topics array from backend returns a list of extractions.
  // We'll show the most recent extraction (which is the first one).
  const latestExtraction = topics.length > 0 ? topics[0] : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Dashboard de Tópicos</h2>
          <p className="text-muted-foreground">
            Asignatura: <span className="uppercase font-medium">{subject}</span>
          </p>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <Settings2 className="h-5 w-5" />
            Configuración de Extracción
          </CardTitle>
          <CardDescription>Ajusta los parámetros para el modelado de tópicos (NMF)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="space-y-2">
              <label htmlFor="k-value" className="text-sm font-medium">
                Número de Tópicos (k)
              </label>
              <Select value={kValue} onValueChange={setKValue}>
                <SelectTrigger id="k-value">
                  <SelectValue placeholder="Automático" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Automático (Óptimo)</SelectItem>
                  <SelectItem value="2">2 Tópicos</SelectItem>
                  <SelectItem value="3">3 Tópicos</SelectItem>
                  <SelectItem value="4">4 Tópicos</SelectItem>
                  <SelectItem value="5">5 Tópicos</SelectItem>
                  <SelectItem value="6">6 Tópicos</SelectItem>
                  <SelectItem value="8">8 Tópicos</SelectItem>
                  <SelectItem value="10">10 Tópicos</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label htmlFor="vectorizer-type" className="text-sm font-medium">
                Vectorizador
              </label>
              <Select value={vectorizerType} onValueChange={setVectorizerType}>
                <SelectTrigger id="vectorizer-type">
                  <SelectValue placeholder="TF-IDF" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="tfidf">TF-IDF</SelectItem>
                  <SelectItem value="bow">Bag of Words (BoW)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label htmlFor="cost-function" className="text-sm font-medium">
                Función de Coste
              </label>
              <Select value={costFunction} onValueChange={setCostFunction}>
                <SelectTrigger id="cost-function">
                  <SelectValue placeholder="Frobenius" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="frobenius">Frobenius</SelectItem>
                  <SelectItem value="kl">Divergencia KL</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <Button onClick={handleExtract} disabled={isExtracting} className="w-full md:w-auto">
            {isExtracting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Extrayendo...
              </>
            ) : (
              <>
                <BarChart2 className="mr-2 h-4 w-4" />
                Extraer Tópicos
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && <div className="bg-destructive/15 text-destructive p-4 rounded-md">{error}</div>}

      {isLoading ? (
        <div className="flex justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : !latestExtraction ? (
        <Card className="flex items-center justify-center p-12 text-center text-muted-foreground">
          <div className="flex flex-col items-center">
            <BarChart2 className="h-12 w-12 mb-4 opacity-20" />
            <p className="text-lg">No hay tópicos extraídos para esta asignatura.</p>
            <p className="text-sm">
              Usa el botón "Extraer Tópicos" para generarlos a partir de los documentos.
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          <div className="flex gap-2 items-center">
            <h3 className="text-lg font-semibold">Resultados de la Extracción</h3>
            <Badge variant="outline">
              {new Date(latestExtraction.created_at || "").toLocaleDateString()}
            </Badge>
            <Badge variant="secondary">Chunks analizados: {latestExtraction.source_chunks}</Badge>
          </div>

          <Tabs defaultValue="tarjetas" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="tarjetas">Tarjetas</TabsTrigger>
              <TabsTrigger value="grafo">Grafo de Conceptos</TabsTrigger>
            </TabsList>

            <TabsContent value="tarjetas" className="mt-0 outline-none">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {latestExtraction.topics.map((topic, index) => (
                  <Card key={`topic-${topic.topic_name}-${index}`} className="flex flex-col h-full">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-md font-semibold">{topic.topic_name}</CardTitle>
                        <Badge className="bg-primary/20 text-primary border-0">
                          Peso: {topic.weight.toFixed(2)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="flex flex-wrap gap-2">
                        {topic.terms.map((term) => (
                          <Badge
                            key={`term-${term}`}
                            variant="secondary"
                            className="font-normal text-sm"
                          >
                            {term}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="grafo" className="mt-0 outline-none">
              {latestExtraction.concept_map ? (
                <TopicsGraph
                  conceptMap={latestExtraction.concept_map}
                  topics={latestExtraction.topics}
                />
              ) : (
                <Card className="flex items-center justify-center p-12 text-center text-muted-foreground w-full">
                  <p>El mapa de conceptos no está disponible para esta extracción.</p>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}
