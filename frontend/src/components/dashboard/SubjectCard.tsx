import {
  FileText,
  FolderOpen,
  MoreVertical,
  TrendingUp,
  UserPlus,
  Users,
  MessageSquare,
  BarChart2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { SubjectInfo } from "@/types/dashboard";

interface SubjectCardProps {
  subject: SubjectInfo;
  onViewStudents: (subject: string) => void;
  onViewDocuments: (subject: string) => void;
  onEnrollStudent: (subject: string) => void;
  onViewProgress?: (subject: string) => void;
  onViewFaqs?: (subject: string) => void;
  onViewTopics?: (subject: string) => void;
}

export function SubjectCard({
  subject,
  onViewStudents,
  onViewDocuments,
  onEnrollStudent,
  onViewProgress,
  onViewFaqs,
  onViewTopics,
}: SubjectCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-lg font-semibold capitalize">{subject.name}</CardTitle>
          <CardDescription>Asignatura</CardDescription>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onViewStudents(subject.name)}>
              <Users className="mr-2 h-4 w-4" />
              Ver estudiantes
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onViewDocuments(subject.name)}>
              <FolderOpen className="mr-2 h-4 w-4" />
              Gestionar documentos
            </DropdownMenuItem>
            {onViewFaqs && (
              <DropdownMenuItem onClick={() => onViewFaqs(subject.name)}>
                <FileText className="mr-2 h-4 w-4" />
                Gestionar FAQs
              </DropdownMenuItem>
            )}
            {onViewTopics && (
              <DropdownMenuItem onClick={() => onViewTopics(subject.name)}>
                <BarChart2 className="mr-2 h-4 w-4" />
                Extraer Tópicos
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={() => onEnrollStudent(subject.name)}>
              <UserPlus className="mr-2 h-4 w-4" />
              Matricular estudiante
            </DropdownMenuItem>
            {onViewProgress && (
              <DropdownMenuItem onClick={() => onViewProgress(subject.name)}>
                <TrendingUp className="mr-2 h-4 w-4" />
                Ver progreso
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <Users className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
            <div>
              <p className="text-2xl font-bold">{subject.student_count}</p>
              <p className="text-xs text-muted-foreground">Estudiantes</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <FileText className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
            <div>
              <p className="text-2xl font-bold">{subject.document_count}</p>
              <p className="text-xs text-muted-foreground">Documentos</p>
            </div>
          </div>
        </div>
        <div
          className={`mt-4 grid gap-2 ${onViewFaqs || onViewTopics ? "grid-cols-2 md:grid-cols-3" : "grid-cols-2"}`}
        >
          <Button
            variant="outline"
            size="default"
            className="w-full justify-start"
            onClick={() => onViewStudents(subject.name)}
          >
            <Users className="h-4 w-4 mr-2" />
            Estudiantes
          </Button>
          <Button
            variant="outline"
            size="default"
            className="w-full justify-start"
            onClick={() => onViewDocuments(subject.name)}
          >
            <FolderOpen className="h-4 w-4 mr-2" />
            Documentos
          </Button>
          {onViewFaqs && (
            <Button
              variant="outline"
              size="default"
              className="w-full justify-start"
              onClick={() => onViewFaqs(subject.name)}
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              FAQs
            </Button>
          )}
          {onViewTopics && (
            <Button
              variant="outline"
              size="default"
              className="w-full justify-start"
              onClick={() => onViewTopics(subject.name)}
            >
              <BarChart2 className="h-4 w-4 mr-2" />
              Tópicos
            </Button>
          )}
          {onViewProgress && (
            <Button
              variant="default"
              size="default"
              className={`w-full justify-center ${onViewFaqs ? "col-span-2 md:col-span-1" : "col-span-2"}`}
              onClick={() => onViewProgress(subject.name)}
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              Ver Progreso
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
