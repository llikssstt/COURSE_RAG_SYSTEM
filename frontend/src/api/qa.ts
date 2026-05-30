import { apiClient } from "./client";
import type { LLMConfig, QAHistoryItem, QAResponse } from "../types";

export async function askCourse(courseId: number, payload: {
  question: string;
  top_k: number;
  llm_config: LLMConfig;
}): Promise<QAResponse> {
  const { data } = await apiClient.post<QAResponse>(`/api/courses/${courseId}/qa`, payload);
  return data;
}

export async function listQAHistory(
  courseId: number,
  filters: { keyword?: string; limit?: number; offset?: number } = {},
): Promise<QAHistoryItem[]> {
  const { data } = await apiClient.get<QAHistoryItem[]>(`/api/courses/${courseId}/qa/history`, { params: filters });
  return data;
}

export async function getQAHistoryItem(courseId: number, qaId: number): Promise<QAHistoryItem> {
  const { data } = await apiClient.get<QAHistoryItem>(`/api/courses/${courseId}/qa/history/${qaId}`);
  return data;
}

export async function deleteQAHistoryItem(courseId: number, qaId: number): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/qa/history/${qaId}`);
  return data;
}

export async function deleteQAHistoryItems(courseId: number, ids: number[]): Promise<{ deleted: number }> {
  const { data } = await apiClient.delete<{ deleted: number }>(`/api/courses/${courseId}/qa/history`, { data: { ids } });
  return data;
}
