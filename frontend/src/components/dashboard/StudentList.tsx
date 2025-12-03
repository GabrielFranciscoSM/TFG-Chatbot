import { Mail, User, UserMinus, UserPlus } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { EnrollStudentDialog } from "@/components/admin/EnrollStudentDialog";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useUnenrollStudent } from "@/hooks/useAdmin";
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
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Error al desmatricular");
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
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="capitalize">
            Estudiantes de {subject}
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({students.length} estudiantes)
            </span>
          </CardTitle>
        </div>
        <Button onClick={() => setEnrollDialogOpen(true)} size="sm">
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
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuario</TableHead>
                <TableHead>Email</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {students.map((student) => (
                <TableRow key={student.username}>
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-muted-foreground" />
                      {student.username}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      {student.email}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                      onClick={() => {
                        setSelectedStudent(student.username);
                        setUnenrollDialogOpen(true);
                      }}
                    >
                      <UserMinus className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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
