import { useMemo } from "react";
import {
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  ScatterChart,
  Scatter,
  Cell,
  ZAxis,
} from "recharts";
import { Card } from "@/components/ui/card";
import type { TopicDetails } from "@/types/topics";

interface TopicsHeatmapProps {
  docTopicMatrix: number[][];
  topics: TopicDetails[];
}

const HEATMAP_COLORS = [
  "#f0f4ff", // near-zero
  "#c7d7fe", // very low
  "#93b4fd", // low
  "#6490fb", // medium-low
  "#3b6cf7", // medium
  "#2152d9", // medium-high
  "#1a3fad", // high
  "#122b7a", // very high
];

function getHeatColor(value: number, max: number): string {
  if (max === 0) return HEATMAP_COLORS[0];
  const ratio = Math.min(value / max, 1);
  const idx = Math.min(Math.floor(ratio * (HEATMAP_COLORS.length - 1)), HEATMAP_COLORS.length - 1);
  return HEATMAP_COLORS[idx];
}

interface HeatmapCell {
  x: number;
  y: number;
  value: number;
  docLabel: string;
  topicLabel: string;
}

export function TopicsHeatmap({ docTopicMatrix, topics }: TopicsHeatmapProps) {
  const { cells, maxVal } = useMemo(() => {
    const result: HeatmapCell[] = [];
    let max = 0;

    for (let docIdx = 0; docIdx < docTopicMatrix.length; docIdx++) {
      const row = docTopicMatrix[docIdx];
      for (let topicIdx = 0; topicIdx < row.length; topicIdx++) {
        const val = row[topicIdx];
        if (val > max) max = val;
        result.push({
          x: topicIdx,
          y: docIdx,
          value: val,
          docLabel: `Doc ${docIdx + 1}`,
          topicLabel: topics[topicIdx]?.topic_name ?? `Tópico ${topicIdx + 1}`,
        });
      }
    }

    return { cells: result, maxVal: max };
  }, [docTopicMatrix, topics]);

  const numTopics = topics.length;
  const numDocs = docTopicMatrix.length;

  if (numDocs === 0 || numTopics === 0) {
    return (
      <Card className="flex items-center justify-center p-12 text-center text-muted-foreground">
        <p>No hay datos de distribución documento-tópico disponibles.</p>
      </Card>
    );
  }

  // For large datasets, limit displayed docs
  const maxDisplayDocs = Math.min(numDocs, 60);
  const displayedCells = cells.filter((c) => c.y < maxDisplayDocs);

  const cellSize = 28;
  const chartHeight = Math.max(300, Math.min(maxDisplayDocs * cellSize + 80, 700));

  return (
    <Card className="w-full overflow-hidden border bg-white shadow-sm">
      <div className="p-4 border-b bg-muted/20">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold">Distribución Documento-Tópico</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Intensidad de cada tópico por documento ({numDocs} documentos × {numTopics} tópicos)
            </p>
          </div>
          {/* Color scale legend */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-muted-foreground mr-1">Baja</span>
            {HEATMAP_COLORS.map((color) => (
              <div key={color} className="w-4 h-3 rounded-sm" style={{ backgroundColor: color }} />
            ))}
            <span className="text-xs text-muted-foreground ml-1">Alta</span>
          </div>
        </div>
      </div>

      <div className="p-4 overflow-x-auto">
        <ResponsiveContainer width="100%" height={chartHeight}>
          <ScatterChart margin={{ top: 10, right: 20, bottom: 40, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis
              type="number"
              dataKey="x"
              domain={[-0.5, numTopics - 0.5]}
              ticks={Array.from({ length: numTopics }, (_, i) => i)}
              tickFormatter={(val: number) =>
                topics[val]?.topic_name?.substring(0, 12) ?? `T${val + 1}`
              }
              tick={{ fontSize: 11, fill: "#64748b" }}
              label={{ value: "Tópicos", position: "insideBottom", offset: -10, fontSize: 12 }}
            />
            <YAxis
              type="number"
              dataKey="y"
              domain={[-0.5, maxDisplayDocs - 0.5]}
              ticks={
                maxDisplayDocs <= 20
                  ? Array.from({ length: maxDisplayDocs }, (_, i) => i)
                  : Array.from({ length: Math.ceil(maxDisplayDocs / 5) }, (_, i) => i * 5)
              }
              tickFormatter={(val: number) => `Doc ${val + 1}`}
              tick={{ fontSize: 11, fill: "#64748b" }}
              reversed
              label={{
                value: "Documentos",
                angle: -90,
                position: "insideLeft",
                offset: -10,
                fontSize: 12,
              }}
            />
            <ZAxis range={[cellSize * cellSize * 0.8, cellSize * cellSize * 0.8]} />
            <Tooltip
              content={({ payload }: Record<string, unknown>) => {
                const items = payload as Array<{ payload: HeatmapCell }> | undefined;
                if (!items || items.length === 0) return null;
                const data = items[0].payload;
                return (
                  <div className="bg-white border rounded-md shadow-lg p-2 text-xs">
                    <p className="font-semibold">{data.topicLabel}</p>
                    <p className="text-muted-foreground">{data.docLabel}</p>
                    <p className="mt-1">
                      Peso: <span className="font-mono font-semibold">{data.value.toFixed(4)}</span>
                    </p>
                  </div>
                );
              }}
            />
            <Scatter data={displayedCells} shape="square">
              {displayedCells.map((cell) => (
                <Cell key={`${cell.x}-${cell.y}`} fill={getHeatColor(cell.value, maxVal)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {numDocs > maxDisplayDocs && (
        <div className="px-4 pb-3 text-xs text-muted-foreground text-center">
          Mostrando {maxDisplayDocs} de {numDocs} documentos.
        </div>
      )}
    </Card>
  );
}
