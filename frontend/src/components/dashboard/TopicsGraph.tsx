import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ForceGraphMethods, LinkObject, NodeObject } from "react-force-graph-2d";
import ForceGraph2D from "react-force-graph-2d";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { ConceptMap, ConceptNode, TopicDetails } from "@/types/topics";

interface TopicsGraphProps {
  conceptMap: ConceptMap;
  topics: TopicDetails[];
}

const COLORS = [
  "#3b82f6", // blue
  "#10b981", // emerald
  "#f59e0b", // amber
  "#8b5cf6", // violet
  "#ef4444", // red
  "#06b6d4", // cyan
  "#f97316", // orange
  "#6366f1", // indigo
  "#84cc16", // lime
  "#d946ef", // fuchsia
  "#14b8a6", // teal
  "#f43f5e", // rose
];

interface EnrichedNode extends ConceptNode, Omit<NodeObject, "id"> {
  color: string;
  val: number;
}

export function TopicsGraph({ conceptMap, topics }: TopicsGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 600 });
  const graphRef = useRef<ForceGraphMethods | undefined>(undefined);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: 600,
        });
      }
    };

    updateDimensions();
    window.addEventListener("resize", updateDimensions);

    // Slight delay to ensure parent has rendered fully
    const timeout = setTimeout(updateDimensions, 100);
    return () => {
      window.removeEventListener("resize", updateDimensions);
      clearTimeout(timeout);
    };
  }, []);

  const graphData = useMemo(() => {
    // Generate topic color mapping
    const topicColors: Record<string, string> = {};
    topics.forEach((topic, i) => {
      topicColors[topic.topic_name] = COLORS[i % COLORS.length];
    });

    // We mutate node objects directly so force-graph handles them easily
    const enrichedNodes: EnrichedNode[] = conceptMap.nodes.map((node) => {
      let color = "#94a3b8"; // default gray
      let val = 1;

      if (node.group === "subject") {
        color = "#0f172a"; // dark for subject
        val = 15; // largest node
      } else if (node.group === "topic") {
        color = topicColors[node.id] || color;
        // Size proportional to weight roughly
        const topicInfo = topics.find((t) => t.topic_name === node.id);
        val = topicInfo ? Math.max(5, topicInfo.weight * 3) : 5;
      } else if (node.group === "term") {
        val = 2; // smaller for terms
      }

      return {
        ...node,
        color,
        val,
      };
    });

    // Second pass to color terms based on their connected topic
    conceptMap.links.forEach((link) => {
      const sourceId =
        typeof link.source === "object" ? (link.source as NodeObject).id : link.source;
      const targetId =
        typeof link.target === "object" ? (link.target as NodeObject).id : link.target;

      const sourceNode = enrichedNodes.find((n) => n.id === sourceId);
      const targetNode = enrichedNodes.find((n) => n.id === targetId);

      // If source is a topic and target is a term, copy color
      if (sourceNode?.group === "topic" && targetNode?.group === "term") {
        // slightly less opaque for terms
        targetNode.color = `${sourceNode.color}cc`;
      }
    });

    return {
      nodes: enrichedNodes,
      links: conceptMap.links.map((link) => ({ ...link })), // clone links
    };
  }, [conceptMap, topics]);

  // Add zoom to fit after graph loads
  useEffect(() => {
    if (graphRef.current && graphData.nodes.length > 0) {
      setTimeout(() => {
        graphRef.current?.zoomToFit(400, 50);
      }, 500);
    }
  }, [graphData]);

  // Keep colors based on the node's group
  const drawNode = useCallback(
    (node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const enrichedNode = node as EnrichedNode;
      const label = enrichedNode.label;
      const fontSize = Math.max(12 / globalScale, 2); // Keep font size readable
      ctx.font = `${fontSize}px Sans-Serif`;

      // Draw the circle
      ctx.beginPath();
      const nx = enrichedNode.x ?? 0;
      const ny = enrichedNode.y ?? 0;
      ctx.arc(nx, ny, Math.sqrt(enrichedNode.val) * 2, 0, 2 * Math.PI, false);
      ctx.fillStyle = enrichedNode.color;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 0.5 / globalScale;
      ctx.stroke();

      // Draw text label below node
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = enrichedNode.group === "subject" ? "#000000" : "#334155"; // Darker text for more contrast

      // Only draw text if zoomed in enough or if it's an important node
      if (globalScale > 0.8 || enrichedNode.group === "subject" || enrichedNode.group === "topic") {
        const textY = ny + Math.sqrt(enrichedNode.val) * 2 + 2 / globalScale;
        ctx.fillText(label, nx, textY);
      }
    },
    [],
  );

  return (
    <Card
      className="w-full flex flex-col overflow-hidden border bg-white shadow-sm"
      style={{ animation: "fadeIn 0.5s ease-out" }}
    >
      <div className="p-4 border-b bg-muted/20">
        <div className="flex flex-wrap gap-2 items-center mb-2">
          <span className="text-sm font-medium mr-2">Leyenda:</span>
          <Badge className="bg-[#0f172a] hover:bg-[#0f172a]">Asignatura</Badge>
          {topics.map((topic, i) => (
            <Badge
              key={topic.topic_name}
              style={{
                backgroundColor: `${COLORS[i % COLORS.length]}22`,
                color: COLORS[i % COLORS.length],
                borderColor: COLORS[i % COLORS.length],
              }}
              variant="outline"
              className="text-xs"
            >
              {topic.topic_name}
            </Badge>
          ))}
          <Badge variant="secondary" className="bg-gray-100 text-gray-500">
            Término
          </Badge>
        </div>
        <span className="text-xs text-muted-foreground flex items-center">
          Ratón: Arrastrar (pan) • Rueda: Zoom • Click y arrastrar nodo: Fijar
        </span>
      </div>
      <style>{`@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }`}</style>
      <div
        ref={containerRef}
        className="w-full relative bg-slate-50/50"
        style={{ height: "600px" }}
      >
        {dimensions.width > 0 && (
          <ForceGraph2D
            ref={graphRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            nodeLabel="label"
            nodeColor="color"
            nodeVal="val"
            nodeCanvasObject={drawNode}
            linkColor={() => "#cbd5e1"}
            linkWidth={(link: LinkObject) =>
              Math.max(0.5, (link as unknown as { value?: number }).value ?? 1)
            }
            d3VelocityDecay={0.3}
            onNodeDragEnd={(node) => {
              if (node.x !== undefined && node.y !== undefined) {
                node.fx = node.x;
                node.fy = node.y;
              }
            }}
            onNodeClick={(node) => {
              // Center view on node
              if (graphRef.current && node.x !== undefined && node.y !== undefined) {
                graphRef.current.centerAt(node.x, node.y, 1000);
                graphRef.current.zoom(2, 1000);
              }
            }}
          />
        )}
      </div>
    </Card>
  );
}
