export type Course = {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
};

export type CourseStats = {
  course_id: number;
  document_count: number;
  chunk_count: number;
  qa_count: number;
  question_count: number;
  wrong_question_count?: number;
};

export type DocumentRecord = {
  id: number;
  course_id: number;
  file_name: string;
  file_type: string;
  file_path: string;
  upload_time: string;
  parse_status: string;
};

export type UploadResult = {
  file_name: string;
  status: string;
  document?: DocumentRecord;
  error?: string;
};

export type LLMConfig = {
  api_key: string;
  base_url: string;
  model: string;
};

export type Source = {
  source_file?: string;
  page_number?: number | null;
  slide_number?: number | null;
  section_title?: string | null;
  score?: number;
  chunk_text?: string;
  text?: string;
  [key: string]: unknown;
};

export type QAResponse = {
  answer: string;
  sources: Source[];
  retrieval_mode?: string;
  route_type?: string;
  retrieval_query?: string;
};

export type QAHistoryItem = {
  id: number;
  course_id: number;
  question: string;
  answer: string;
  sources: string | Source[];
  created_at: string;
};

export type QuestionItem = {
  question_content: string;
  options?: string[] | Record<string, string>;
  answer?: string;
  analysis?: string;
  knowledge_point?: string;
  sources?: string | Source[];
};

export type QuestionRecord = {
  id: number;
  course_id: number;
  question_type: string;
  difficulty: string;
  question_content: string;
  answer: string;
  analysis: string;
  knowledge_point: string;
  sources: string | Source[];
  created_at: string;
};

export type SummaryResponse = {
  summary: string;
  sources: Source[];
};

export type WrongQuestion = {
  id: number;
  course_id: number;
  question_id?: number | null;
  source_type: string;
  question_type?: string;
  difficulty?: string;
  question_content: string;
  user_answer?: string;
  correct_answer?: string;
  analysis?: string;
  knowledge_point?: string;
  sources?: string | Source[];
  note?: string;
  status: "未掌握" | "已掌握";
  review_count: number;
  last_reviewed_at?: string | null;
  created_at: string;
  updated_at: string;
};

export type WrongQuestionCreate = {
  question_id?: number | null;
  source_type: string;
  question_type?: string;
  difficulty?: string;
  question_content: string;
  user_answer?: string;
  correct_answer?: string;
  analysis?: string;
  knowledge_point?: string;
  sources?: Source[] | string;
  note?: string;
};

export type WrongQuestionUpdate = {
  note?: string;
  status?: "未掌握" | "已掌握";
  user_answer?: string;
};
