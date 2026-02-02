import { Bot, Info, Loader2, User } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useSystemInfo } from "@/hooks/useSystemInfo";
import { useUpdatePreferences, useUserPreferences } from "@/hooks/useUserPreferences";
import type { UserPreferences } from "@/types/preferences";

export default function SettingsPage() {
  const { user } = useAuth();
  const { data: preferences, isLoading: preferencesLoading } = useUserPreferences();
  const { data: systemInfo, isLoading: systemInfoLoading } = useSystemInfo();
  const updatePreferences = useUpdatePreferences();

  const isProfessorOrAdmin = user?.role === "professor" || user?.role === "admin";

  // Local state for form
  const [formState, setFormState] = useState<UserPreferences>({
    default_test_questions: 5,
    default_test_difficulty: "medium",
  });
  const [hasChanges, setHasChanges] = useState(false);

  // Sync form state with fetched preferences
  useEffect(() => {
    if (preferences) {
      setFormState(preferences);
      setHasChanges(false);
    }
  }, [preferences]);

  const handleQuestionsChange = (value: string) => {
    const newState = { ...formState, default_test_questions: Number.parseInt(value, 10) };
    setFormState(newState);
    setHasChanges(true);
  };

  const handleDifficultyChange = (value: "easy" | "medium" | "hard") => {
    const newState = { ...formState, default_test_difficulty: value };
    setFormState(newState);
    setHasChanges(true);
  };

  const handleSave = () => {
    updatePreferences.mutate(formState, {
      onSuccess: () => {
        toast.success("Preferencias guardadas correctamente");
        setHasChanges(false);
      },
      onError: () => {
        toast.error("Error al guardar las preferencias");
      },
    });
  };

  return (
    <div className="p-6 space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Configuración</h1>
        <p className="text-muted-foreground">Personaliza tu experiencia en el chatbot</p>
      </div>

      {/* Profile Settings - All users */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="h-5 w-5" />
            <CardTitle>Perfil</CardTitle>
          </div>
          <CardDescription>Información de tu cuenta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" value={user?.email || ""} disabled />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="username">Nombre de usuario</Label>
            <Input id="username" value={user?.username || ""} disabled />
          </div>
          <div className="grid gap-2">
            <Label>Rol</Label>
            <Input
              value={
                user?.role === "admin"
                  ? "Administrador"
                  : user?.role === "professor"
                    ? "Profesor"
                    : "Estudiante"
              }
              disabled
            />
          </div>
          <div className="grid gap-2">
            <Label>Asignaturas</Label>
            <Input value={user?.subjects?.join(", ") || "Ninguna asignatura asignada"} disabled />
          </div>
        </CardContent>
      </Card>

      {/* Test Configuration - Professor and Admin only */}
      {isProfessorOrAdmin && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <CardTitle>Configuración de Tests</CardTitle>
            </div>
            <CardDescription>
              Valores por defecto cuando los estudiantes solicitan tests de evaluación
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {preferencesLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <>
                <div className="grid gap-2">
                  <Label htmlFor="default-questions">Número de preguntas por defecto</Label>
                  <Select
                    value={String(formState.default_test_questions)}
                    onValueChange={handleQuestionsChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona cantidad" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">3 preguntas (rápido)</SelectItem>
                      <SelectItem value="5">5 preguntas (estándar)</SelectItem>
                      <SelectItem value="10">10 preguntas (completo)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="default-difficulty">Dificultad por defecto</Label>
                  <Select
                    value={formState.default_test_difficulty}
                    onValueChange={handleDifficultyChange}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecciona dificultad" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Fácil - Conceptos básicos</SelectItem>
                      <SelectItem value="medium">Media - Aplicación práctica</SelectItem>
                      <SelectItem value="hard">Difícil - Análisis y síntesis</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between pt-2">
                  <p className="text-muted-foreground text-xs">
                    Los estudiantes pueden solicitar valores diferentes.
                  </p>
                  <Button
                    onClick={handleSave}
                    disabled={!hasChanges || updatePreferences.isPending}
                    size="sm"
                  >
                    {updatePreferences.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Guardando...
                      </>
                    ) : (
                      "Guardar cambios"
                    )}
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* System Info - All users */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            <CardTitle>Información del Sistema</CardTitle>
          </div>
          <CardDescription>Estado actual de la plataforma</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {systemInfoLoading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-muted-foreground">Versión</span>
                <span className="text-sm font-medium">{systemInfo?.version || "unknown"}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-muted-foreground">Proveedor LLM</span>
                <span className="text-sm font-medium">{systemInfo?.llm_provider || "Unknown"}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b">
                <span className="text-sm text-muted-foreground">Modelo</span>
                <span className="text-sm font-medium">{systemInfo?.llm_model || "Unknown"}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-muted-foreground">Estado</span>
                <span
                  className={`text-sm font-medium ${systemInfo?.status === "operational" ? "text-green-600" : "text-yellow-600"}`}
                >
                  {systemInfo?.status === "operational" ? "Operativo" : "No disponible"}
                </span>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
