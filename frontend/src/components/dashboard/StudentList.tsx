import { User, UserPlus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { EnrollStudentDialog } from "@/components/admin/EnrollStudentDialog";
import { StudentsTable } from "@/components/dashboard/StudentsTable";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useUnenrollStudent } from "@/hooks/useAdmin";
import { getErrorMessage } from "@/lib/errors";
import type { StudentInfo } from "@/types/dashboard";

interface StudentListProps {
  students: StudentInfo[];
  subject: string;
  isLoading?: boolean;
  onStudentChange?: () => void;
}

export function StudentList({ students, subject, isLoading, onStudentChange }: StudentListProps) {
  const [enrollDialogOpen, setEnrollDialogOpen] = useState(false);
  const [unenrollDialogOpen, setUnenrollDialogOpen] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const unenrollMutation = useUnenrollStudent();

  const handleUnenroll = async () => {
    if (!selectedStudent) return;
    try {
      await unenrollMutation.mutateAsync({ username: selectedStudent, subject });
      toast.success(`${selectedStudent} desmatriculado de ${subject}`);
      setUnenrollDialogOpen(false);
      setSelectedStudent(null);
      onStudentChange?.();
    } catch (error) {
      toast.error(getErrorMessage(error, "Error al desmatricular"));
    }
  };

  const handleEnrollSuccess = () => {
    setEnrollDialogOpen(false);
    onStudentChange?.();
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="capitalize">Estudiantes de {subject}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <CardTitle className="capitalize">
            Estudiantes de {subject}
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({students.length})
            </span>
          </CardTitle>
        </div>
        <Button onClick={() => setEnrollDialogOpen(true)} size="sm" className="w-full sm:w-auto">
          <UserPlus className="h-4 w-4 mr-2" />
          Matricular
        </Button>
      </CardHeader>
      <CardContent>
        {students.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <User className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No hay estudiantes matriculados en esta asignatura</p>
          </div>
        ) : (
          <StudentsTable
            students={students}
            isLoading={isLoading}
            onUnenroll={(username) => {
              setSelectedStudent(username);
              setUnenrollDialogOpen(true);
            }}
          />
        )}
      </CardContent>

      {/* Enroll Dialog */}
      <EnrollStudentDialog
        open={enrollDialogOpen}
        onOpenChange={setEnrollDialogOpen}
        subject={subject}
        onSuccess={handleEnrollSuccess}
      />

      {/* Unenroll Confirmation */}
      <AlertDialog open={unenrollDialogOpen} onOpenChange={setUnenrollDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>¿Desmatricular estudiante?</AlertDialogTitle>
            <AlertDialogDescription>
              ¿Estás seguro de que quieres desmatricular a <strong>{selectedStudent}</strong> de{" "}
              <strong>{subject}</strong>?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleUnenroll}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Desmatricular
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
