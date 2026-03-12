import { AlertTriangle, BarChart2, Grid3X3, Loader2, Network, Settings2, Tag } from "lucide-react";
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
import { TopicsHeatmap } from "./TopicsHeatmap";

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

  const latestExtraction = topics.length > 0 ? topics[0] : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Dashboard de Tópicos</h2>
          <p className="text-muted-foreground">
            Asignatura: <span className="uppercase font-medium">{subject}</span>
          </p>
        </div>
      </div>

      {/* Configuration Card */}
      <Card className="border-2 border-dashed border-muted hover:border-primary/30 transition-colors duration-300">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg flex items-center gap-2">
            <Settings2 className="h-5 w-5 text-primary" />
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

      {/* Extracting overlay */}
      {isExtracting && (
        <Card className="border-primary/30 bg-primary/5 animate-in fade-in duration-300">
          <CardContent className="py-8 flex flex-col items-center gap-3">
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <p className="text-sm font-medium text-primary">Analizando documentos...</p>
            <p className="text-xs text-muted-foreground text-center max-w-md">
              Extrayendo vocabulario, calculando TF-IDF y aplicando NMF para encontrar los tópicos
              latentes. Esto puede tardar unos segundos.
            </p>
            <div className="w-full max-w-xs mt-2">
              <div className="h-1.5 bg-primary/20 rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full animate-pulse w-2/3" />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error state */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/5 animate-in fade-in duration-300">
          <CardContent className="py-6 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-destructive">Error en la extracción</p>
              <p className="text-sm text-destructive/80 mt-1">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading state */}
      {isLoading ? (
        <div className="flex justify-center p-8">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : !latestExtraction ? (
        /* Empty state */
        <Card className="flex items-center justify-center p-16 text-center text-muted-foreground bg-gradient-to-b from-muted/30 to-transparent animate-in fade-in duration-500">
          <div className="flex flex-col items-center">
            <div className="p-4 bg-muted/50 rounded-full mb-4">
              <BarChart2 className="h-12 w-12 opacity-30" />
            </div>
            <p className="text-lg font-medium">No hay tópicos extraídos</p>
            <p className="text-sm mt-1 max-w-sm">
              Usa el botón &quot;Extraer Tópicos&quot; para analizar los documentos y descubrir los
              temas latentes de la asignatura.
            </p>
          </div>
        </Card>
      ) : (
        /* Results */
        <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
          {/* Results header badges */}
          <div className="flex flex-wrap gap-2 items-center">
            <h3 className="text-lg font-semibold">Resultados de la Extracción</h3>
            <Badge variant="outline" className="gap-1">
              <Tag className="h-3 w-3" />
              {new Date(latestExtraction.created_at || "").toLocaleDateString()}
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <BarChart2 className="h-3 w-3" />
              {latestExtraction.topics.length} tópicos
            </Badge>
            <Badge variant="secondary" className="gap-1 bg-blue-100 text-blue-700 border-0">
              Chunks: {latestExtraction.source_chunks}
            </Badge>
          </div>

          <Tabs defaultValue="tarjetas" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="tarjetas" className="gap-1.5">
                <Tag className="h-3.5 w-3.5" />
                Tarjetas
              </TabsTrigger>
              <TabsTrigger value="heatmap" className="gap-1.5">
                <Grid3X3 className="h-3.5 w-3.5" />
                Heatmap
              </TabsTrigger>
              <TabsTrigger value="grafo" className="gap-1.5">
                <Network className="h-3.5 w-3.5" />
                Grafo de Conceptos
              </TabsTrigger>
            </TabsList>

            {/* Cards tab */}
            <TabsContent value="tarjetas" className="mt-0 outline-none">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {latestExtraction.topics.map((topic, index) => (
                  <Card
                    key={`topic-${topic.topic_name}-${index}`}
                    className="flex flex-col h-full hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5"
                    style={{
                      animationDelay: `${index * 80}ms`,
                      animation: "fadeSlideIn 0.4s ease-out backwards",
                    }}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-md font-semibold">{topic.topic_name}</CardTitle>
                        <Badge className="bg-primary/15 text-primary border-0 font-mono text-xs">
                          {topic.weight.toFixed(2)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="flex-1">
                      <div className="flex flex-wrap gap-1.5">
                        {topic.terms.map((term) => (
                          <Badge
                            key={`term-${term}`}
                            variant="secondary"
                            className="font-normal text-xs hover:bg-primary/10 transition-colors duration-200"
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

            {/* Heatmap tab */}
            <TabsContent value="heatmap" className="mt-0 outline-none">
              {latestExtraction.doc_topic_matrix ? (
                <TopicsHeatmap
                  docTopicMatrix={latestExtraction.doc_topic_matrix}
                  topics={latestExtraction.topics}
                />
              ) : (
                <Card className="flex items-center justify-center p-12 text-center text-muted-foreground w-full">
                  <div className="flex flex-col items-center gap-2">
                    <Grid3X3 className="h-8 w-8 opacity-20" />
                    <p>La distribución documento-tópico no está disponible para esta extracción.</p>
                    <p className="text-xs">Re-ejecuta la extracción para generar los datos.</p>
                  </div>
                </Card>
              )}
            </TabsContent>

            {/* Graph tab */}
            <TabsContent value="grafo" className="mt-0 outline-none">
              {latestExtraction.concept_map ? (
                <TopicsGraph
                  conceptMap={latestExtraction.concept_map}
                  topics={latestExtraction.topics}
                />
              ) : (
                <Card className="flex items-center justify-center p-12 text-center text-muted-foreground w-full">
                  <div className="flex flex-col items-center gap-2">
                    <Network className="h-8 w-8 opacity-20" />
                    <p>El mapa de conceptos no está disponible para esta extracción.</p>
                  </div>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        </div>
      )}

      {/* Global CSS keyframes for stagger animation */}
      <style>{`
        @keyframes fadeSlideIn {
          from {
            opacity: 0;
            transform: translateY(12px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
