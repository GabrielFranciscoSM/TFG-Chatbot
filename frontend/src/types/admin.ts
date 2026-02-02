// Admin dashboard types

export interface AdminStats {
  total_students: number;
  total_professors: number;
  total_admins: number;
  total_sessions: number;
  total_subjects: number;
  sessions_last_7_days: { date: string; count: number }[];
}

export interface UserInfo {
  username: string;
  email: string;
  role: "student" | "professor" | "admin";
  subjects: string[];
}

export interface EnrollRequest {
  username: string;
  subject: string;
}

export interface PromoteRequest {
  username: string;
  new_role: "student" | "professor" | "admin";
}

// Subject management types
export interface SubjectInfo {
  name: string;
  display_name: string;
  guia_url: string | null;
  guia_indexed: boolean;
  created_at: string;
  created_by: string;
  student_count: number;
  professor_count: number;
}

export interface SubjectPublic {
  name: string;
  display_name: string;
}

export interface CreateSubjectRequest {
  name: string;
  display_name: string;
  guia_url?: string;
}

export interface BatchEnrollRequest {
  usernames: string[];
  subject: string;
}

export interface BatchEnrollResponse {
  status: string;
  subject: string;
  enrolled: string[];
  enrolled_count: number;
  not_found: string[];
  not_students: string[];
}
