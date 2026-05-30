import { apiClient } from "./client";
import type { LLMConfig, SummaryResponse } from "../types";

export async function generateSummary(courseId: number, payload: {
  summary_type: string;
  scope?: string;
  top_k: number;
  llm_config: LLMConfig;
}): Promise<SummaryResponse> {
  const { data } = await apiClient.post<SummaryResponse>(`/api/courses/${courseId}/summaries/generate`, payload);
  return data;
}
