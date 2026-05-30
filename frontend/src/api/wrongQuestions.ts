import { apiClient } from "./client";
import type { WrongQuestion, WrongQuestionCreate, WrongQuestionUpdate } from "../types";

export async function listWrongQuestions(
  courseId: number,
  filters: { keyword?: string; status?: string; knowledge_point?: string; limit?: number; offset?: number } = {},
): Promise<WrongQuestion[]> {
  const { data } = await apiClient.get<WrongQuestion[]>(`/api/courses/${courseId}/wrong-questions`, { params: filters });
  return data;
}

export async function createWrongQuestion(courseId: number, payload: WrongQuestionCreate): Promise<WrongQuestion> {
  const { data } = await apiClient.post<WrongQuestion>(`/api/courses/${courseId}/wrong-questions`, payload);
  return data;
}

export async function getWrongQuestion(courseId: number, wrongId: number): Promise<WrongQuestion> {
  const { data } = await apiClient.get<WrongQuestion>(`/api/courses/${courseId}/wrong-questions/${wrongId}`);
  return data;
}

export async function updateWrongQuestion(courseId: number, wrongId: number, payload: WrongQuestionUpdate): Promise<WrongQuestion> {
  const { data } = await apiClient.patch<WrongQuestion>(`/api/courses/${courseId}/wrong-questions/${wrongId}`, payload);
  return data;
}

export async function markWrongQuestionReviewed(courseId: number, wrongId: number): Promise<WrongQuestion> {
  const { data } = await apiClient.post<WrongQuestion>(`/api/courses/${courseId}/wrong-questions/${wrongId}/review`);
  return data;
}

export async function deleteWrongQuestion(courseId: number, wrongId: number): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/wrong-questions/${wrongId}`);
  return data;
}

export async function deleteWrongQuestions(courseId: number, ids: number[]): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/wrong-questions`, { data: { ids } });
  return data;
}
