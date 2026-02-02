// Types for professor dashboard

export interface StudentInfo {
  username: string;
  email: string;
}

export interface SubjectInfo {
  name: string;
  student_count: number;
  document_count: number;
}

export interface DocumentInfo {
  filename: string;
  path: string;
  size_kb: number;
  tipo_documento: string;
}

export interface SubjectStats {
  subject: string;
  session_count: number;
  message_count: number;
}

export interface DailySessionCount {
  date: string;
  count: number;
}

export interface DashboardStats {
  total_students: number;
  total_sessions: number;
  total_documents: number;
  subjects: SubjectStats[];
  sessions_last_7_days: DailySessionCount[];
}

export interface UploadDocumentRequest {
  file: File;
  tipo_documento: string;
  auto_index: boolean;
}

// --- Student Progress Types ---

export interface TopicProgress {
  topic: string;
  level: number; // 0-1 mastery level
  interactions_count: number;
  test_questions: number;
  correct_answers: number;
}

export interface StudentProgress {
  username: string;
  email: string;
  total_interactions: number;
  difficulty_distribution: {
    basic: number;
    intermediate: number;
    advanced: number;
  };
  topics: TopicProgress[];
  tests_taken: number;
  average_test_score: number | null;
  last_active: string | null;
}

export interface AggregatedStats {
  total_students: number;
  total_interactions: number;
  total_tests: number;
  difficulty_distribution: {
    basic: number;
    intermediate: number;
    advanced: number;
  };
}

export interface SubjectProgressResponse {
  subject: string;
  students: StudentProgress[];
  aggregated_stats: AggregatedStats;
}
