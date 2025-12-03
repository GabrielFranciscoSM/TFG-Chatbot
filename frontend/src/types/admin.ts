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
