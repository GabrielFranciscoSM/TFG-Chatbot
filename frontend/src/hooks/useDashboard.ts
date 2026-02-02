import { useCallback, useEffect, useState } from "react";
import api from "@/lib/api";
import type {
  DashboardStats,
  DocumentInfo,
  StudentInfo,
  SubjectInfo,
  SubjectProgressResponse,
} from "@/types/dashboard";

// Hook for fetching professor's subjects
export function useSubjects() {
  const [subjects, setSubjects] = useState<SubjectInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<SubjectInfo[]>("/professor/subjects");
      setSubjects(response.data);
    } catch (err) {
      console.error("Error fetching subjects:", err);
      setError("Error al cargar las asignaturas");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  return { subjects, isLoading, error, refetch: fetchSubjects };
}

// Hook for fetching students of a specific subject
export function useStudents(subject: string | null) {
  const [students, setStudents] = useState<StudentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStudents = useCallback(async () => {
    if (!subject) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<StudentInfo[]>(
        `/professor/subjects/${encodeURIComponent(subject)}/students`,
      );
      setStudents(response.data);
    } catch (err) {
      console.error("Error fetching students:", err);
      setError("Error al cargar los estudiantes");
    } finally {
      setIsLoading(false);
    }
  }, [subject]);

  useEffect(() => {
    if (subject) {
      fetchStudents();
    } else {
      setStudents([]);
    }
  }, [subject, fetchStudents]);

  return { students, isLoading, error, refetch: fetchStudents };
}

// Hook for managing documents of a specific subject
export function useDocuments(subject: string | null) {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    if (!subject) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<DocumentInfo[]>(
        `/professor/subjects/${encodeURIComponent(subject)}/documents`,
      );
      setDocuments(response.data);
    } catch (err) {
      console.error("Error fetching documents:", err);
      setError("Error al cargar los documentos");
    } finally {
      setIsLoading(false);
    }
  }, [subject]);

  const uploadDocument = useCallback(
    async (file: File, tipoDocumento: string = "teoria", autoIndex: boolean = true) => {
      if (!subject) return;

      setIsUploading(true);
      setError(null);
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("tipo_documento", tipoDocumento);
        formData.append("auto_index", autoIndex.toString());

        await api.post(`/professor/subjects/${encodeURIComponent(subject)}/documents`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        // Refresh document list after upload
        await fetchDocuments();
      } catch (err) {
        console.error("Error uploading document:", err);
        setError("Error al subir el documento");
        throw err;
      } finally {
        setIsUploading(false);
      }
    },
    [subject, fetchDocuments],
  );

  const deleteDocument = useCallback(
    async (filePath: string) => {
      if (!subject) return;

      setError(null);
      try {
        await api.delete(
          `/professor/subjects/${encodeURIComponent(subject)}/documents/${encodeURIComponent(filePath)}`,
        );

        // Refresh document list after deletion
        await fetchDocuments();
      } catch (err) {
        console.error("Error deleting document:", err);
        setError("Error al eliminar el documento");
        throw err;
      }
    },
    [subject, fetchDocuments],
  );

  useEffect(() => {
    if (subject) {
      fetchDocuments();
    } else {
      setDocuments([]);
    }
  }, [subject, fetchDocuments]);

  return {
    documents,
    isLoading,
    isUploading,
    error,
    refetch: fetchDocuments,
    uploadDocument,
    deleteDocument,
  };
}

// Hook for fetching dashboard statistics
export function useStats() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<DashboardStats>("/professor/stats");
      setStats(response.data);
    } catch (err) {
      console.error("Error fetching stats:", err);
      setError("Error al cargar las estadísticas");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, isLoading, error, refetch: fetchStats };
}

// Hook for fetching student progress in a subject
export function useStudentProgress(subject: string | null) {
  const [progress, setProgress] = useState<SubjectProgressResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProgress = useCallback(async () => {
    if (!subject) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await api.get<SubjectProgressResponse>(
        `/professor/subjects/${encodeURIComponent(subject)}/progress`,
      );
      setProgress(response.data);
    } catch (err) {
      console.error("Error fetching student progress:", err);
      setError("Error al cargar el progreso de los estudiantes");
    } finally {
      setIsLoading(false);
    }
  }, [subject]);

  useEffect(() => {
    if (subject) {
      fetchProgress();
    } else {
      setProgress(null);
    }
  }, [subject, fetchProgress]);

  return { progress, isLoading, error, refetch: fetchProgress };
}
