import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/context/AuthContext";
import { useSubjectsPublic } from "@/hooks/useAdmin";

interface NewSessionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateSession: (title: string, subject: string) => void;
}

export function NewSessionDialog({ open, onOpenChange, onCreateSession }: NewSessionDialogProps) {
  const { user } = useAuth();
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");

  // Fetch subjects from API
  const { data: allSubjects = [], isLoading: subjectsLoading } = useSubjectsPublic();

  // Filter subjects based on user enrollment (for students)
  // Students can only see "general" + subjects they're enrolled in
  // Professors/Admins can see all subjects
  // Normalize to lowercase for comparison
  const userSubjects = user?.subjects?.map((s) => s.toLowerCase()) ?? [];
  const availableSubjects =
    user?.role === "student"
      ? allSubjects.filter(
          (s) => s.name === "general" || userSubjects.includes(s.name.toLowerCase()),
        )
      : allSubjects;

  const handleSubmit = () => {
    if (title.trim() && subject) {
      onCreateSession(title.trim(), subject);
      setTitle("");
      setSubject("");
      onOpenChange(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      setTitle("");
      setSubject("");
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Nueva conversación</DialogTitle>
          <DialogDescription>
            Crea una nueva conversación. Elige una asignatura para recibir respuestas específicas.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="title">Título</Label>
            <Input
              id="title"
              placeholder="Ej: Dudas sobre Docker"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="subject">Asignatura</Label>
            <Select value={subject} onValueChange={setSubject}>
              <SelectTrigger id="subject">
                <SelectValue
                  placeholder={subjectsLoading ? "Cargando..." : "Selecciona una asignatura"}
                />
              </SelectTrigger>
              <SelectContent>
                {availableSubjects.map((s) => (
                  <SelectItem key={s.name} value={s.name}>
                    {s.display_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={!title.trim() || !subject}>
            Crear
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
