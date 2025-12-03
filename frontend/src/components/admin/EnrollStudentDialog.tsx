import { User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
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
import { useEnrollStudent, useUserSearch } from "@/hooks/useAdmin";

interface EnrollStudentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  subject: string;
  onSuccess?: () => void;
}

export function EnrollStudentDialog({
  open,
  onOpenChange,
  subject,
  onSuccess,
}: EnrollStudentDialogProps) {
  const [username, setUsername] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const enrollMutation = useEnrollStudent();
  const { data: suggestions = [], isLoading: searchLoading } = useUserSearch(username, "student");

  // Reset state when dialog closes
  useEffect(() => {
    if (!open) {
      setUsername("");
      setShowSuggestions(false);
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    try {
      await enrollMutation.mutateAsync({
        username: username.trim(),
        subject,
      });
      toast.success(`Estudiante ${username} matriculado en ${subject}`);
      setUsername("");
      onOpenChange(false);
      onSuccess?.();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Error al matricular estudiante");
    }
  };

  const selectUser = (selectedUsername: string) => {
    setUsername(selectedUsername);
    setShowSuggestions(false);
  };

  // Close suggestions when clicking outside
  const handleBlur = () => {
    // Delay to allow click on suggestion to register
    setTimeout(() => setShowSuggestions(false), 150);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Matricular Estudiante</DialogTitle>
          <DialogDescription>
            Añade un estudiante a la asignatura <strong>{subject}</strong>
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2 relative">
              <Label htmlFor="username">Nombre de usuario</Label>
              <Input
                ref={inputRef}
                id="username"
                placeholder="Escribe para buscar..."
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={handleBlur}
                autoComplete="off"
              />

              {/* Suggestions dropdown */}
              {showSuggestions && username.length >= 2 && (
                <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-popover border rounded-md shadow-lg max-h-48 overflow-auto">
                  {searchLoading ? (
                    <div className="p-2 text-sm text-muted-foreground">Buscando...</div>
                  ) : suggestions.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground">
                      No se encontraron estudiantes
                    </div>
                  ) : (
                    suggestions.map((user) => (
                      <div
                        key={user.username}
                        className="w-full px-3 py-2 text-left hover:bg-accent flex items-center gap-2 cursor-pointer"
                        onMouseDown={(e) => {
                          e.preventDefault(); // Prevent blur before click
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
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={enrollMutation.isPending || !username.trim()}>
              {enrollMutation.isPending ? "Matriculando..." : "Matricular"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
