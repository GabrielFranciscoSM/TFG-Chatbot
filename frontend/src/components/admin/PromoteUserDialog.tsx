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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { usePromoteUser, useUserSearch } from "@/hooks/useAdmin";
import type { UserInfo } from "@/types/admin";

interface PromoteUserDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  user?: UserInfo;
}

const roleLabels = {
  student: "Estudiante",
  professor: "Profesor",
  admin: "Administrador",
};

export function PromoteUserDialog({
  open,
  onOpenChange,
  user: initialUser,
}: PromoteUserDialogProps) {
  const [username, setUsername] = useState(initialUser?.username || "");
  const [newRole, setNewRole] = useState<"student" | "professor" | "admin">(initialUser?.role || "student");
  const [currentRole, setCurrentRole] = useState<"student" | "professor" | "admin" | null>(initialUser?.role || null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  
  const promoteMutation = usePromoteUser();
  const { data: suggestions = [], isLoading: searchLoading } = useUserSearch(username);

  // Reset state when dialog closes or user changes
  useEffect(() => {
    if (!open) {
      setUsername(initialUser?.username || "");
      setNewRole(initialUser?.role || "student");
      setCurrentRole(initialUser?.role || null);
      setShowSuggestions(false);
    }
  }, [open, initialUser]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    try {
      await promoteMutation.mutateAsync({
        username: username.trim(),
        new_role: newRole,
      });
      toast.success(`${username} ahora es ${roleLabels[newRole]}`);
      setUsername("");
      onOpenChange(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Error al cambiar rol");
    }
  };

  const selectUser = (selectedUser: UserInfo) => {
    setUsername(selectedUser.username);
    setCurrentRole(selectedUser.role);
    setNewRole(selectedUser.role);
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
          <DialogTitle>Cambiar Rol de Usuario</DialogTitle>
          <DialogDescription>
            Modifica el rol de un usuario en el sistema.
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
                  setCurrentRole(null);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={handleBlur}
                disabled={!!initialUser}
                autoComplete="off"
              />
              
              {/* Suggestions dropdown */}
              {showSuggestions && username.length >= 2 && !initialUser && (
                <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-popover border rounded-md shadow-lg max-h-48 overflow-auto">
                  {searchLoading ? (
                    <div className="p-2 text-sm text-muted-foreground">Buscando...</div>
                  ) : suggestions.length === 0 ? (
                    <div className="p-2 text-sm text-muted-foreground">
                      No se encontraron usuarios
                    </div>
                  ) : (
                    suggestions.map((u) => (
                      <div
                        key={u.username}
                        className="w-full px-3 py-2 text-left hover:bg-accent flex items-center gap-2 cursor-pointer"
                        onMouseDown={(e) => {
                          e.preventDefault();
                          selectUser(u);
                        }}
                      >
                        <User className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="font-medium">{u.username}</div>
                          <div className="text-xs text-muted-foreground">
                            {u.email} • {roleLabels[u.role]}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="role">Nuevo rol</Label>
              <Select value={newRole} onValueChange={(value) => setNewRole(value as typeof newRole)}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un rol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="student">Estudiante</SelectItem>
                  <SelectItem value="professor">Profesor</SelectItem>
                  <SelectItem value="admin">Administrador</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {currentRole && currentRole !== newRole && (
              <p className="text-sm text-muted-foreground">
                Cambiar de <strong>{roleLabels[currentRole]}</strong> a{" "}
                <strong>{roleLabels[newRole]}</strong>
              </p>
            )}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button 
              type="submit" 
              disabled={promoteMutation.isPending || !username.trim() || (currentRole === newRole)}
            >
              {promoteMutation.isPending ? "Cambiando..." : "Cambiar Rol"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
