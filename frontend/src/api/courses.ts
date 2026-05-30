import { apiClient } from "./client";
import type { Course, CourseStats } from "../types";

export async function listCourses(): Promise<Course[]> {
  const { data } = await apiClient.get<Course[]>("/api/courses");
  return data;
}

export async function createCourse(payload: { name: string; description?: string }): Promise<Course> {
  const { data } = await apiClient.post<Course>("/api/courses", payload);
  return data;
}

export async function getCourse(courseId: number): Promise<Course> {
  const { data } = await apiClient.get<Course>(`/api/courses/${courseId}`);
  return data;
}

export async function getCourseStats(courseId: number): Promise<CourseStats> {
  const { data } = await apiClient.get<CourseStats>(`/api/courses/${courseId}/stats`);
  return data;
}
