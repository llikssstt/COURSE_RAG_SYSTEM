import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Course, LLMConfig } from "../types";

type AppState = {
  currentCourse: Course | null;
  llmConfig: LLMConfig;
  setCurrentCourse: (course: Course | null) => void;
  setLLMConfig: (config: LLMConfig) => void;
};

export const defaultLLMConfig: LLMConfig = {
  api_key: "",
  base_url: "https://api.deepseek.com",
  model: "deepseek-chat",
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentCourse: null,
      llmConfig: defaultLLMConfig,
      setCurrentCourse: (course) => set({ currentCourse: course }),
      setLLMConfig: (config) => set({ llmConfig: config }),
    }),
    {
      name: "course-rag-system-store",
      partialize: (state) => ({
        currentCourse: state.currentCourse,
        llmConfig: state.llmConfig,
      }),
    },
  ),
);
