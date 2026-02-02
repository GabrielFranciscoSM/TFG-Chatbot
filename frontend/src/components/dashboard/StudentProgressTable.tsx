import { ChevronDown, ChevronRight, Clock, Target, TrendingUp } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { StudentProgress } from "@/types/dashboard";

// Simple relative time formatter without date-fns
function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return "Nunca";

  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Hace un momento";
  if (diffMins < 60) return `Hace ${diffMins} minutos`;
  if (diffHours < 24) return `Hace ${diffHours} horas`;
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  return `Hace ${Math.floor(diffDays / 30)} meses`;
}

interface StudentProgressTableProps {
  students: StudentProgress[];
}

function DifficultyBadges({
  distribution,
}: {
  distribution: StudentProgress["difficulty_distribution"];
}) {
  const total = distribution.basic + distribution.intermediate + distribution.advanced;
  if (total === 0) return <span className="text-muted-foreground text-sm">Sin actividad</span>;

  return (
    <div className="flex gap-1">
      {distribution.basic > 0 && (
        <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
          B: {distribution.basic}
        </Badge>
      )}
      {distribution.intermediate > 0 && (
        <Badge variant="outline" className="text-yellow-600 border-yellow-200 bg-yellow-50">
          I: {distribution.intermediate}
        </Badge>
      )}
      {distribution.advanced > 0 && (
        <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50">
          A: {distribution.advanced}
        </Badge>
      )}
    </div>
  );
}

function TopicMasteryList({ topics }: { topics: StudentProgress["topics"] }) {
  if (topics.length === 0) {
    return <span className="text-muted-foreground text-sm">Sin temas registrados</span>;
  }

  return (
    <div className="space-y-2 py-2">
      {topics.map((topic) => (
        <div key={topic.topic} className="space-y-1">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium capitalize">{topic.topic}</span>
            <span className="text-muted-foreground">{Math.round(topic.level * 100)}% dominio</span>
          </div>
          <Progress value={topic.level * 100} className="h-2" />
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span>{topic.interactions_count} interacciones</span>
            {topic.test_questions > 0 && (
              <span>
                {topic.correct_answers}/{topic.test_questions} correctas
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function StudentRow({ student }: { student: StudentProgress }) {
  const [expanded, setExpanded] = useState(false);

  const lastActiveText = formatRelativeTime(student.last_active);

  return (
    <>
      <TableRow className="cursor-pointer hover:bg-muted/50" onClick={() => setExpanded(!expanded)}>
        <TableCell>
          <button type="button" className="flex items-center gap-2">
            {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            <div>
              <div className="font-medium">{student.username}</div>
              <div className="text-sm text-muted-foreground">{student.email}</div>
            </div>
          </button>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            {student.total_interactions}
          </div>
        </TableCell>
        <TableCell>
          <DifficultyBadges distribution={student.difficulty_distribution} />
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-muted-foreground" />
            {student.tests_taken}
            {student.average_test_score !== null && (
              <Badge variant="secondary">{Math.round(student.average_test_score * 100)}%</Badge>
            )}
          </div>
        </TableCell>
        <TableCell>
          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="h-4 w-4" />
            <span className="text-sm">{lastActiveText}</span>
          </div>
        </TableCell>
      </TableRow>
      {expanded && (
        <TableRow>
          <TableCell colSpan={5} className="bg-muted/30">
            <div className="p-4">
              <h4 className="font-medium mb-2">Dominio por Temas</h4>
              <TopicMasteryList topics={student.topics} />
            </div>
          </TableCell>
        </TableRow>
      )}
    </>
  );
}

export function StudentProgressTable({ students }: StudentProgressTableProps) {
  if (students.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Progreso de Estudiantes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            No hay estudiantes matriculados en esta asignatura.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Progreso de Estudiantes</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Estudiante</TableHead>
              <TableHead>Interacciones</TableHead>
              <TableHead>Dificultad</TableHead>
              <TableHead>Tests</TableHead>
              <TableHead>Última Actividad</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {students.map((student) => (
              <StudentRow key={student.username} student={student} />
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
