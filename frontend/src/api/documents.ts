import { apiClient } from "./client";
import type { DocumentRecord, UploadResult } from "../types";

export async function listDocuments(courseId: number): Promise<DocumentRecord[]> {
  const { data } = await apiClient.get<DocumentRecord[]>(`/api/courses/${courseId}/documents`);
  return data;
}

export async function uploadDocuments(courseId: number, files: FileList | File[]): Promise<UploadResult[]> {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("files", file));
  const { data } = await apiClient.post<UploadResult[]>(`/api/courses/${courseId}/documents/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function rebuildKnowledgeBase(courseId: number): Promise<{
  course_id: number;
  total_chunks: number;
  failures: Array<{ file_name: string; error: string }>;
  message: string;
}> {
  const { data } = await apiClient.post(`/api/courses/${courseId}/knowledge-base/rebuild`);
  return data;
}
