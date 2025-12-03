import { useState } from "react";
import { ArrowLeft, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SubjectCard } from "@/components/dashboard/SubjectCard";
import { StudentList } from "@/components/dashboard/StudentList";
import { DocumentManager } from "@/components/dashboard/DocumentManager";
import { StatsOverview } from "@/components/dashboard/StatsOverview";
import {
  useSubjects,
  useStudents,
  useDocuments,
  useStats,
} from "@/hooks/useDashboard";

type View = "overview" | "students" | "documents";

export default function DashboardPage() {
  const [currentView, setCurrentView] = useState<View>("overview");
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);

  const { subjects, isLoading: loadingSubjects } = useSubjects();
  const { students, isLoading: loadingStudents } = useStudents(selectedSubject);
  const {
    documents,
    isLoading: loadingDocuments,
    isUploading,
    uploadDocument,
    deleteDocument,
  } = useDocuments(selectedSubject);
  const { stats, isLoading: loadingStats } = useStats();

  const handleViewStudents = (subject: string) => {
    setSelectedSubject(subject);
    setCurrentView("students");
  };

  const handleViewDocuments = (subject: string) => {
    setSelectedSubject(subject);
    setCurrentView("documents");
  };

  const handleEnrollStudent = (subject: string) => {
    // TODO: Implement enroll student dialog
    console.log("Enroll student in", subject);
  };

  const handleBack = () => {
    setCurrentView("overview");
    setSelectedSubject(null);
  };

  // Show subject detail view
  if (currentView !== "overview" && selectedSubject) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-6 px-4 max-w-6xl">
          <Button
            variant="ghost"
            onClick={handleBack}
            className="mb-4"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Volver al dashboard
          </Button>

          {currentView === "students" && (
            <StudentList
              students={students}
              subject={selectedSubject}
              isLoading={loadingStudents}
            />
          )}

          {currentView === "documents" && (
            <DocumentManager
              documents={documents}
              subject={selectedSubject}
              isLoading={loadingDocuments}
              isUploading={isUploading}
              onUpload={uploadDocument}
              onDelete={deleteDocument}
            />
          )}
        </div>
      </div>
    );
  }

  // Main dashboard view
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-6 px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Gestiona tus asignaturas, estudiantes y documentos
          </p>
        </div>

        <Tabs defaultValue="subjects" className="space-y-6">
          <TabsList>
            <TabsTrigger value="subjects">Mis Asignaturas</TabsTrigger>
            <TabsTrigger value="stats">Estadísticas</TabsTrigger>
          </TabsList>

          {/* Subjects Tab */}
          <TabsContent value="subjects" className="space-y-6">
            {loadingSubjects ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-48 rounded-lg bg-muted animate-pulse"
                  />
                ))}
              </div>
            ) : subjects.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-medium">No tienes asignaturas asignadas</h3>
                <p className="text-muted-foreground">
                  Contacta con un administrador para que te asigne asignaturas
                </p>
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {subjects.map((subject) => (
                  <SubjectCard
                    key={subject.name}
                    subject={subject}
                    onViewStudents={handleViewStudents}
                    onViewDocuments={handleViewDocuments}
                    onEnrollStudent={handleEnrollStudent}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* Stats Tab */}
          <TabsContent value="stats">
            <StatsOverview stats={stats} isLoading={loadingStats} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
