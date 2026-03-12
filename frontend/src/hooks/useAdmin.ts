import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import type { AdminStats, EnrollRequest, PromoteRequest, UserInfo } from "@/types/admin";

// Fetch admin stats
export function useAdminStats() {
  return useQuery<AdminStats>({
    queryKey: ["admin", "stats"],
    queryFn: async () => {
      const response = await api.get("/admin/stats");
      return response.data;
    },
  });
}

// Fetch users list
export function useUsers(role?: "student" | "professor" | "admin") {
  return useQuery<UserInfo[]>({
    queryKey: ["admin", "users", role],
    queryFn: async () => {
      const params = role ? { role } : {};
      const response = await api.get("/admin/users", { params });
      return response.data;
    },
  });
}

// Search users with autocomplete (debounced)
export function useUserSearch(query: string, role?: "student" | "professor" | "admin") {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(timer);
  }, [query]);

  return useQuery<UserInfo[]>({
    queryKey: ["admin", "users", "search", debouncedQuery, role],
    queryFn: async () => {
      if (debouncedQuery.length < 2) return [];
      const params: Record<string, string> = { q: debouncedQuery };
      if (role) params.role = role;
      const response = await api.get("/admin/users/search", { params });
      return response.data;
    },
    enabled: debouncedQuery.length >= 2,
  });
}

// Enroll student in subject
export function useEnrollStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EnrollRequest) => {
      const response = await api.post("/admin/enroll", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["professor", "subjects"] });
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });
}

// Unenroll student from subject
export function useUnenrollStudent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EnrollRequest) => {
      const response = await api.post("/admin/unenroll", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["professor", "subjects"] });
      queryClient.invalidateQueries({ queryKey: ["students"] });
    },
  });
}

// Assign subject to professor (admin only)
export function useAssignSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EnrollRequest) => {
      const response = await api.post("/admin/assign-subject", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });
}

// Remove subject from professor (admin only)
export function useRemoveSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: EnrollRequest) => {
      const response = await api.post("/admin/remove-subject", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });
}

// Promote user (admin only)
export function usePromoteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PromoteRequest) => {
      const response = await api.post("/admin/promote", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

// --- Subject management hooks ---

import type {
  BatchEnrollRequest,
  BatchEnrollResponse,
  CreateSubjectRequest,
  SubjectInfo,
  SubjectPublic,
} from "@/types/admin";

// Fetch all subjects (admin view with full info)
export function useSubjects() {
  return useQuery<{ subjects: SubjectInfo[]; total: number }>({
    queryKey: ["admin", "subjects"],
    queryFn: async () => {
      const response = await api.get("/admin/subjects");
      return response.data;
    },
  });
}

// Fetch public subjects list (no auth required)
export function useSubjectsPublic() {
  return useQuery<SubjectPublic[]>({
    queryKey: ["subjects", "public"],
    queryFn: async () => {
      const response = await api.get("/subjects");
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Create subject
export function useCreateSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateSubjectRequest) => {
      const response = await api.post<SubjectInfo>("/admin/subjects", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "subjects"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["subjects", "public"] });
    },
  });
}

// Delete subject
export function useDeleteSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ subjectName, force }: { subjectName: string; force?: boolean }) => {
      const params = force ? { force: "true" } : {};
      const response = await api.delete(`/admin/subjects/${subjectName}`, { params });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "subjects"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "stats"] });
      queryClient.invalidateQueries({ queryKey: ["subjects", "public"] });
    },
  });
}

// Batch enroll students
export function useBatchEnroll() {
  const queryClient = useQueryClient();

  return useMutation<BatchEnrollResponse, Error, BatchEnrollRequest>({
    mutationFn: async (data: BatchEnrollRequest) => {
      const response = await api.post<BatchEnrollResponse>("/admin/enroll-batch", data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "subjects"] });
    },
  });
}
