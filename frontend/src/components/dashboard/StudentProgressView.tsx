import { ArrowLeft, Loader2 } from "lucide-react";
import { ProgressStats } from "@/components/dashboard/ProgressStats";
import { StudentProgressTable } from "@/components/dashboard/StudentProgressTable";
import { Button } from "@/components/ui/button";
import { useStudentProgress } from "@/hooks/useDashboard";

interface StudentProgressViewProps {
  subject: string;
  onBack: () => void;
}

export function StudentProgressView({ subject, onBack }: StudentProgressViewProps) {
  const { progress, isLoading, error } = useStudentProgress(subject);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-6 px-4 max-w-6xl">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver al dashboard
          </Button>
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-6 px-4 max-w-6xl">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver al dashboard
          </Button>
          <div className="text-center py-16">
            <p className="text-destructive">{error}</p>
            <Button variant="outline" onClick={onBack} className="mt-4">
              Volver
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!progress) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-6 px-4 max-w-6xl">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Volver al dashboard
        </Button>

        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight capitalize">Progreso de {subject}</h1>
          <p className="text-muted-foreground">
            Vista detallada del progreso de aprendizaje de los estudiantes
          </p>
        </div>

        <div className="space-y-6">
          <ProgressStats stats={progress.aggregated_stats} />
          <StudentProgressTable students={progress.students} />
        </div>
      </div>
    </div>
  );
}
