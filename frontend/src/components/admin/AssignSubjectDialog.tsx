import { useState, useRef, useEffect } from "react";
import { toast } from "sonner";
import { User } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAssignSubject, useUserSearch } from "@/hooks/useAdmin";

interface AssignSubjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  professorUsername?: string;
}

export function AssignSubjectDialog({
  open,
  onOpenChange,
  professorUsername,
}: AssignSubjectDialogProps) {
  const [username, setUsername] = useState(professorUsername || "");
  const [subject, setSubject] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const assignMutation = useAssignSubject();
  const { data: suggestions = [], isLoading: searchLoading } = useUserSearch(username, "professor");

  // Reset state when dialog closes or professorUsername changes
  useEffect(() => {
    if (!open) {
      setUsername(professorUsername || "");
      setSubject("");
      setShowSuggestions(false);
    }
  }, [open, professorUsername]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !subject.trim()) return;

    try {
      await assignMutation.mutateAsync({
        username: username.trim(),
        subject: subject.trim().toLowerCase(),
      });
      toast.success(`Asignatura ${subject} asignada a ${username}`);
      setUsername("");
      setSubject("");
      onOpenChange(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Error al asignar asignatura");
    }
  };

  const selectUser = (selectedUsername: string) => {
    setUsername(selectedUsername);
    setShowSuggestions(false);
  };

  // Close suggestions when clicking outside
  const handleBlur = () => {
    setTimeout(() => setShowSuggestions(false), 150);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Asignar Asignatura a Profesor</DialogTitle>
          <DialogDescription>
            Asigna una asignatura a un profesor para que pueda gestionarla.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2 relative">
              <Label htmlFor="username">Nombre de usuario del profesor</Label>
              <Input
                ref={inputRef}
                id="username"
                placeholder="Escribe para buscar profesor..."
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={handleBlur}
                disabled={!!professorUsername}
                autoComplete="off"
              />
              
              {/* Suggestions dropdown */}
              {showSuggestions && username.length >= 2 && !professorUsername && (
                <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-popover border rounded-md shadow-lg max-h-48 overflow-auto">
                  {searchLoading ? (
                    <div className="p-2 text-sm text-muted-foreground">Buscando...</div>
                  ) : suggestions.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground">
                      No se encontraron profesores
                    </div>
                  ) : (
                    suggestions.map((user) => (
                      <div
                        key={user.username}
                        className="w-full px-3 py-2 text-left hover:bg-accent flex items-center gap-2 cursor-pointer"
                        onMouseDown={(e) => {
                          e.preventDefault();
                          selectUser(user.username);
                        }}
                      >
                        <User className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="font-medium">{user.username}</div>
                          <div className="text-xs text-muted-foreground">{user.email}</div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="subject">Asignatura</Label>
              <Input
                id="subject"
                placeholder="ingenieria_de_software"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={assignMutation.isPending || !username.trim() || !subject.trim()}>
              {assignMutation.isPending ? "Asignando..." : "Asignar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
