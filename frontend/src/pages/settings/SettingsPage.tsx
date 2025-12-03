import { Bell, Bot, Database, Palette, Shield, User } from "lucide-react";
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

export default function SettingsPage() {
  const { user } = useAuth();

  const isAdmin = user?.role === "admin";
  const isProfessorOrAdmin = user?.role === "professor" || user?.role === "admin";

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

      {/* Notification Settings - All users */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            <CardTitle>Notificaciones</CardTitle>
          </div>
          <CardDescription>Configura cómo quieres recibir notificaciones</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Las notificaciones se implementarán próximamente
          </p>
        </CardContent>
      </Card>

      {/* Appearance - All users */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            <CardTitle>Apariencia</CardTitle>
          </div>
          <CardDescription>Personaliza la interfaz</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2">
            <Label htmlFor="theme">Tema</Label>
            <Select defaultValue="system">
              <SelectTrigger>
                <SelectValue placeholder="Selecciona un tema" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Claro</SelectItem>
                <SelectItem value="dark">Oscuro</SelectItem>
                <SelectItem value="system">Sistema</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Agent Settings - Professor and Admin only */}
      {isProfessorOrAdmin && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              <CardTitle>Configuración del Agente</CardTitle>
            </div>
            <CardDescription>
              Ajusta el comportamiento del chatbot para tus asignaturas
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="temperature">Creatividad de respuestas</Label>
              <Select defaultValue="balanced">
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un nivel" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="precise">Preciso (más factual)</SelectItem>
                  <SelectItem value="balanced">Balanceado</SelectItem>
                  <SelectItem value="creative">Creativo (más variado)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="context">Contexto RAG</Label>
              <Select defaultValue="medium">
                <SelectTrigger>
                  <SelectValue placeholder="Cantidad de contexto" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Poco (más rápido)</SelectItem>
                  <SelectItem value="medium">Medio</SelectItem>
                  <SelectItem value="high">Alto (más preciso)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <p className="text-muted-foreground text-xs">
              Estos ajustes afectan a todas tus asignaturas. Los cambios se aplicarán en la próxima
              versión.
            </p>
          </CardContent>
        </Card>
      )}

      {/* System Settings - Admin only */}
      {isAdmin && (
        <>
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                <CardTitle>Base de Datos RAG</CardTitle>
              </div>
              <CardDescription>Gestión del sistema de recuperación de documentos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Reindexar documentos</p>
                  <p className="text-sm text-muted-foreground">
                    Regenera los embeddings de todos los documentos
                  </p>
                </div>
                <Button variant="outline">Reindexar</Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Limpiar caché</p>
                  <p className="text-sm text-muted-foreground">Elimina la caché de consultas</p>
                </div>
                <Button variant="outline">Limpiar</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                <CardTitle>Seguridad</CardTitle>
              </div>
              <CardDescription>Configuración de seguridad del sistema</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-2">
                <Label>Proveedor LLM</Label>
                <Select defaultValue="gemini">
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona proveedor" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gemini">Gemini API</SelectItem>
                    <SelectItem value="vllm">vLLM Local</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <p className="text-muted-foreground text-xs">
                Cambiar el proveedor requiere reiniciar el servicio del chatbot.
              </p>
            </CardContent>
          </Card>
        </>
      )}

      {/* Save button */}
      <div className="flex justify-end">
        <Button>Guardar cambios</Button>
      </div>
    </div>
  );
}
