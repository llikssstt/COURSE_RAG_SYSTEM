import { apiClient } from "./client";
import type { LLMConfig, QuestionItem, QuestionRecord } from "../types";

export async function generateQuestions(courseId: number, payload: {
  scope: string;
  question_type: string;
  difficulty: string;
  count: number;
  with_answer: boolean;
  llm_config: LLMConfig;
}): Promise<{ questions: QuestionItem[]; sources: unknown[]; raw?: string }> {
  const { data } = await apiClient.post(`/api/courses/${courseId}/questions/generate`, payload);
  return data;
}

export async function listQuestionHistory(courseId: number): Promise<QuestionRecord[]> {
  const { data } = await apiClient.get<QuestionRecord[]>(`/api/courses/${courseId}/questions/history`);
  return data;
}
