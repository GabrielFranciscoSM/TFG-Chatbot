import { File, FileText, Loader2, Trash2, Upload } from "lucide-react";
import { useRef, useState } from "react";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { DocumentInfo } from "@/types/dashboard";

interface DocumentManagerProps {
  documents: DocumentInfo[];
  subject: string;
  isLoading?: boolean;
  isUploading?: boolean;
  onUpload: (file: File, tipoDocumento: string, autoIndex: boolean) => Promise<void>;
  onDelete: (filePath: string) => Promise<void>;
}

const DOCUMENT_TYPES = [
  { value: "teoria", label: "Teoría" },
  { value: "ejercicios", label: "Ejercicios" },
  { value: "examenes", label: "Exámenes" },
  { value: "practicas", label: "Prácticas" },
  { value: "otros", label: "Otros" },
];

export function DocumentManager({
  documents,
  subject,
  isLoading,
  isUploading,
  onUpload,
  onDelete,
}: DocumentManagerProps) {
  const [selectedType, setSelectedType] = useState("teoria");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await onUpload(file, selectedType, true);
      toast.success("Documento subido correctamente");
    } catch {
      toast.error("Error al subir el documento");
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (filePath: string, filename: string) => {
    try {
      await onDelete(filePath);
      toast.success(`"${filename}" eliminado`);
    } catch {
      toast.error("Error al eliminar el documento");
    }
  };

  const formatSize = (sizeKb: number) => {
    if (sizeKb < 1024) {
      return `${sizeKb.toFixed(1)} KB`;
    }
    return `${(sizeKb / 1024).toFixed(1)} MB`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="capitalize">Documentos de {subject}</CardTitle>
            <CardDescription>
              Gestiona los documentos disponibles para los estudiantes
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Upload Section */}
        <div className="flex items-center gap-4 p-4 border rounded-lg bg-muted/30">
          <div className="flex-1">
            <Select value={selectedType} onValueChange={setSelectedType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Tipo de documento" />
              </SelectTrigger>
              <SelectContent>
                {DOCUMENT_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.txt,.md,.docx"
            onChange={handleFileSelect}
          />
          <Button onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Subiendo...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Subir documento
              </>
            )}
          </Button>
        </div>

        {/* Documents Table */}
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No hay documentos en esta asignatura</p>
            <p className="text-sm">Sube el primer documento para empezar</p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Tamaño</TableHead>
                <TableHead className="w-[100px]">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.path}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <File className="h-4 w-4 text-muted-foreground" />
                      {doc.filename}
                    </div>
                  </TableCell>
                  <TableCell className="capitalize">{doc.tipo_documento}</TableCell>
                  <TableCell>{formatSize(doc.size_kb)}</TableCell>
                  <TableCell>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>¿Eliminar documento?</AlertDialogTitle>
                          <AlertDialogDescription>
                            Esta acción eliminará "{doc.filename}" permanentemente. No se puede
                            deshacer.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancelar</AlertDialogCancel>
                          <AlertDialogAction
                            onClick={() => handleDelete(doc.path, doc.filename)}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          >
                            Eliminar
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
