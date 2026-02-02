import { BookOpen, Brain, Target, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { AggregatedStats } from "@/types/dashboard";

interface ProgressStatsProps {
  stats: AggregatedStats;
}

export function ProgressStats({ stats }: ProgressStatsProps) {
  const totalDifficulty =
    stats.difficulty_distribution.basic +
    stats.difficulty_distribution.intermediate +
    stats.difficulty_distribution.advanced;

  const getPercentage = (value: number) => {
    if (totalDifficulty === 0) return 0;
    return Math.round((value / totalDifficulty) * 100);
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Estudiantes</CardTitle>
          <BookOpen className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_students}</div>
          <p className="text-xs text-muted-foreground">matriculados en esta asignatura</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Interacciones</CardTitle>
          <TrendingUp className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_interactions}</div>
          <p className="text-xs text-muted-foreground">preguntas realizadas en total</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Tests Completados</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.total_tests}</div>
          <p className="text-xs text-muted-foreground">evaluaciones realizadas</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Distribución</CardTitle>
          <Brain className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-green-600">Básico</span>
              <span>{getPercentage(stats.difficulty_distribution.basic)}%</span>
            </div>
            <Progress value={getPercentage(stats.difficulty_distribution.basic)} className="h-1" />
            <div className="flex items-center justify-between text-xs">
              <span className="text-yellow-600">Intermedio</span>
              <span>{getPercentage(stats.difficulty_distribution.intermediate)}%</span>
            </div>
            <Progress
              value={getPercentage(stats.difficulty_distribution.intermediate)}
              className="h-1"
            />
            <div className="flex items-center justify-between text-xs">
              <span className="text-red-600">Avanzado</span>
              <span>{getPercentage(stats.difficulty_distribution.advanced)}%</span>
            </div>
            <Progress
              value={getPercentage(stats.difficulty_distribution.advanced)}
              className="h-1"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
