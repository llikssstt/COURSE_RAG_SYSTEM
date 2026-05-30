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

export async function listQuestionHistory(
  courseId: number,
  filters: { keyword?: string; question_type?: string; difficulty?: string; limit?: number; offset?: number } = {},
): Promise<QuestionRecord[]> {
  const { data } = await apiClient.get<QuestionRecord[]>(`/api/courses/${courseId}/questions/history`, { params: filters });
  return data;
}

export async function searchQuestionHistory(
  courseId: number,
  filters: { keyword?: string; question_type?: string; difficulty?: string; limit?: number; offset?: number } = {},
): Promise<QuestionRecord[]> {
  return listQuestionHistory(courseId, filters);
}

export async function getQuestionRecord(courseId: number, questionId: number): Promise<QuestionRecord> {
  const { data } = await apiClient.get<QuestionRecord>(`/api/courses/${courseId}/questions/${questionId}`);
  return data;
}

export async function deleteQuestionRecord(courseId: number, questionId: number): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/questions/${questionId}`);
  return data;
}

export async function deleteQuestionRecords(courseId: number, ids: number[]): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/questions`, { data: { ids } });
  return data;
}
