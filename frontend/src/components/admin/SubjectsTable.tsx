import { useState } from "react";
import { toast } from "sonner";
import { BookOpen, CheckCircle, XCircle, Trash2, AlertTriangle, RefreshCw } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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
import { useDeleteSubject, useSubjects } from "@/hooks/useAdmin";
import { getErrorMessage } from "@/lib/errors";
import type { SubjectInfo } from "@/types/admin";

export function SubjectsTable() {
  const { data, isLoading, error } = useSubjects();
  const deleteMutation = useDeleteSubject();
  const [deleteTarget, setDeleteTarget] = useState<SubjectInfo | null>(null);
  const [forceDelete, setForceDelete] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return <div className="text-center py-8 text-destructive">Error al cargar las asignaturas</div>;
  }

  const subjects = data?.subjects || [];

  if (subjects.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <BookOpen className="mx-auto h-8 w-8 mb-2" />
        <p>No hay asignaturas creadas todavía.</p>
        <p className="text-sm">Crea la primera asignatura usando el botón "Crear Asignatura".</p>
      </div>
    );
  }

  const handleDelete = async () => {
    if (!deleteTarget) return;

    try {
      await deleteMutation.mutateAsync({
        subjectName: deleteTarget.name,
        force: forceDelete,
      });
      toast.success(`Asignatura "${deleteTarget.display_name}" eliminada`);
      setDeleteTarget(null);
      setForceDelete(false);
    } catch (error) {
      // If error is about enrolled users, prompt for force delete
      const message = getErrorMessage(error, "");
      if (message.includes("enrolled users") && !forceDelete) {
        setForceDelete(true);
        return;
      }
      toast.error(getErrorMessage(error, "Error al eliminar asignatura"));
      setDeleteTarget(null);
      setForceDelete(false);
    }
  };

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Asignatura</TableHead>
              <TableHead>Identificador</TableHead>
              <TableHead className="text-center">Profesores</TableHead>
              <TableHead className="text-center">Estudiantes</TableHead>
              <TableHead className="text-center">Guía Docente</TableHead>
              <TableHead className="text-right">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {subjects.map((subject) => (
              <TableRow key={subject.name}>
                <TableCell className="font-medium">{subject.display_name}</TableCell>
                <TableCell className="font-mono text-sm text-muted-foreground">
                  {subject.name}
                </TableCell>
                <TableCell className="text-center">
                  <Badge variant="secondary">{subject.professor_count}</Badge>
                </TableCell>
                <TableCell className="text-center">
                  <Badge variant="outline">{subject.student_count}</Badge>
                </TableCell>
                <TableCell className="text-center">
                  {subject.guia_indexed ? (
                    <CheckCircle className="h-5 w-5 text-green-500 mx-auto" />
                  ) : subject.guia_url ? (
                    <AlertTriangle className="h-5 w-5 text-yellow-500 mx-auto" />
                  ) : (
                    <XCircle className="h-5 w-5 text-muted-foreground mx-auto" />
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    onClick={() => setDeleteTarget(subject)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {forceDelete ? "¿Eliminar forzadamente?" : "¿Eliminar asignatura?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {forceDelete ? (
                <>
                  <span className="text-destructive font-medium">
                    Esta asignatura tiene {deleteTarget?.student_count || 0} estudiantes y{" "}
                    {deleteTarget?.professor_count || 0} profesores asignados.
                  </span>
                  <br />
                  Al eliminarla, se desasignará de todos los usuarios. Esta acción no se puede
                  deshacer.
                </>
              ) : (
                <>
                  ¿Estás seguro de que deseas eliminar la asignatura{" "}
                  <strong>"{deleteTarget?.display_name}"</strong>? Esta acción no se puede deshacer.
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setForceDelete(false)}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={handleDelete}
            >
              {deleteMutation.isPending
                ? "Eliminando..."
                : forceDelete
                  ? "Sí, eliminar"
                  : "Eliminar"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
