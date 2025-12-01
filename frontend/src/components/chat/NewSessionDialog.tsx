import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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

interface NewSessionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateSession: (title: string, subject: string) => void;
}

// Available subjects - could be fetched from backend in the future
const AVAILABLE_SUBJECTS = [
  { value: "IV", label: "Infraestructura Virtual" },
  { value: "TFG", label: "Trabajo Fin de Grado" },
  { value: "general", label: "General" },
];

export function NewSessionDialog({
  open,
  onOpenChange,
  onCreateSession,
}: NewSessionDialogProps) {
  const { user } = useAuth();
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("");

  // Filter subjects based on user enrollment (for students)
  // Students can only see "general" + subjects they're enrolled in
  // Professors can see all subjects
  const availableSubjects =
    user?.role === "student"
      ? AVAILABLE_SUBJECTS.filter(
          (s) => s.value === "general" || user.subjects.includes(s.value)
        )
      : AVAILABLE_SUBJECTS;

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
            Crea una nueva conversación. Elige una asignatura para recibir
            respuestas específicas.
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
                <SelectValue placeholder="Selecciona una asignatura" />
              </SelectTrigger>
              <SelectContent>
                {availableSubjects.map((s) => (
                  <SelectItem key={s.value} value={s.value}>
                    {s.label}
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
