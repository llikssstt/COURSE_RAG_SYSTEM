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

export async function listQAHistory(courseId: number): Promise<QAHistoryItem[]> {
  const { data } = await apiClient.get<QAHistoryItem[]>(`/api/courses/${courseId}/qa/history`);
  return data;
}
