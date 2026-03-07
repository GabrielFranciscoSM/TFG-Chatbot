import { BookOpen } from "lucide-react";
import { useState } from "react";
import { FaqSection } from "@/components/chat/FaqSection";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/context/AuthContext";
import { useSubjectsPublic } from "@/hooks/useAdmin";

export default function StudentFaqPage() {
  const { user } = useAuth();
  const [selectedSubject, setSelectedSubject] = useState<string>("");

  const { data: allSubjects = [], isLoading } = useSubjectsPublic();

  // Filter subjects based on user enrollment
  const userSubjects = user?.subjects?.map((s) => s.toLowerCase()) ?? [];
  const availableSubjects =
    user?.role === "student"
      ? allSubjects.filter(
          (s) => s.name === "general" || userSubjects.includes(s.name.toLowerCase()),
        )
      : allSubjects;

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="flex flex-col px-6 py-8 border-b bg-muted/20">
        <h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
          <BookOpen className="h-8 w-8 text-primary" />
          Explorar FAQs
        </h1>
        <p className="text-muted-foreground mt-2 max-w-2xl">
          Selecciona una asignatura para consultar sus dudas frecuentes. Estas preguntas han sido
          recopiladas a partir del uso de la plataforma y curadas por los profesores.
        </p>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Subject Selector */}
          <div className="space-y-4 bg-card border rounded-lg p-6 shadow-sm">
            <h2 className="text-lg font-semibold">1. Elige tu asignatura</h2>
            <Select value={selectedSubject} onValueChange={setSelectedSubject}>
              <SelectTrigger className="max-w-md bg-background">
                <SelectValue
                  placeholder={isLoading ? "Cargando..." : "Selecciona una asignatura..."}
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

          {/* Faq Section */}
          {selectedSubject ? (
            <div className="bg-card border rounded-lg shadow-sm w-full relative">
              <FaqSection subjectId={selectedSubject} />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-12 text-center text-muted-foreground border-2 border-dashed rounded-lg bg-muted/10">
              <BookOpen className="h-12 w-12 mb-4 opacity-20" />
              <p className="text-lg font-medium">Ninguna asignatura seleccionada</p>
              <p className="text-sm mt-1">
                Selecciona una asignatura en el menú desplegable superior para ver sus preguntas
                frecuentes.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
