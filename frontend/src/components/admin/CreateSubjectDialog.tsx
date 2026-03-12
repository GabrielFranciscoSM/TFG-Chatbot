import { BookOpen, ExternalLink, Plus } from "lucide-react";
import { useEffect, useState } from "react";
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
import { useCreateSubject } from "@/hooks/useAdmin";
import { getErrorMessage } from "@/lib/errors";

interface CreateSubjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateSubjectDialog({ open, onOpenChange }: CreateSubjectDialogProps) {
  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [guiaUrl, setGuiaUrl] = useState("");

  const createMutation = useCreateSubject();

  // Auto-generate name from display name
  useEffect(() => {
    const generatedName = displayName
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "") // Remove diacritics
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "");
    setName(generatedName);
  }, [displayName]);

  // Reset state when dialog closes
  useEffect(() => {
    if (!open) {
      setName("");
      setDisplayName("");
      setGuiaUrl("");
    }
  }, [open]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !displayName.trim()) return;

    try {
      await createMutation.mutateAsync({
        name: name.trim(),
        display_name: displayName.trim(),
        guia_url: guiaUrl.trim() || undefined,
      });
      toast.success(`Asignatura "${displayName}" creada correctamente`);
      onOpenChange(false);
    } catch (error) {
      toast.error(getErrorMessage(error, "Error al crear asignatura"));
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Crear Nueva Asignatura
          </DialogTitle>
          <DialogDescription>
            Crea una nueva asignatura que podrá ser asignada a profesores y estudiantes.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="displayName">Nombre de la asignatura</Label>
              <Input
                id="displayName"
                placeholder="Infraestructura Virtual"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                autoComplete="off"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="name">Identificador (se genera automáticamente)</Label>
              <Input
                id="name"
                placeholder="infraestructura-virtual"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Este identificador se usará internamente y en URLs. Solo minúsculas, números y
                guiones.
              </p>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="guiaUrl" className="flex items-center gap-2">
                URL de la Guía Docente
                <span className="text-xs text-muted-foreground">(opcional)</span>
              </Label>
              <div className="relative">
                <Input
                  id="guiaUrl"
                  type="url"
                  placeholder="https://grados.ugr.es/informatica/..."
                  value={guiaUrl}
                  onChange={(e) => setGuiaUrl(e.target.value)}
                  className="pr-8"
                />
                {guiaUrl && (
                  <a
                    href={guiaUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
              <p className="text-xs text-muted-foreground">
                Si proporcionas la URL, el sistema intentará extraer automáticamente la información
                de la guía docente.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button
              type="submit"
              disabled={createMutation.isPending || !name.trim() || !displayName.trim()}
            >
              {createMutation.isPending ? (
                <>
                  <Plus className="mr-2 h-4 w-4 animate-spin" />
                  Creando...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Asignatura
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
