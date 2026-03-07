export type FaqStatus = "draft" | "published";

export interface Faq {
  id: string;
  subject_id: string;
  question: string;
  answer: string;
  cluster_id?: number | null;
  status: FaqStatus;
  created_at: string;
  updated_at: string;
}

export interface FaqUpdate {
  question?: string;
  answer?: string;
  status?: FaqStatus;
}
