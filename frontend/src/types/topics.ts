export interface ConceptNode {
  id: string;
  group: string;
  label: string;
}

export interface ConceptLink {
  source: string;
  target: string;
  value: number;
}

export interface ConceptMap {
  nodes: ConceptNode[];
  links: ConceptLink[];
}

export interface TopicDetails {
  cluster: number;
  topic_name: string;
  terms: string[];
  weight: number;
}

export interface TopicResult {
  _id?: string;
  status: string;
  subject?: string;
  clusters_formed: number;
  topics: TopicDetails[];
  concept_map?: ConceptMap;
  doc_topic_matrix?: number[][];
  created_at?: string;
  source_chunks: number;
  message?: string;
}

export interface TopicExtractRequest {
  subject: string;
  vectorizer_type?: string;
  k?: number | null;
  cost_function?: string;
}
