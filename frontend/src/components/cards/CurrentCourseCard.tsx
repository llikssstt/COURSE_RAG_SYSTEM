import { BookOpen } from "lucide-react";
import { useAppStore } from "../../store/useAppStore";

export function CurrentCourseCard() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  return (
    <div className="flex items-center gap-4 rounded-card border border-brand-100 bg-gradient-to-r from-brand-50 to-white p-6 shadow-sm">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500 text-white">
        <BookOpen className="h-7 w-7" />
      </div>
      <div className="min-w-0">
        <span className="text-lg font-bold text-slate-900">当前课程：</span>
        <span className="ml-2 text-2xl font-black text-brand-700">{currentCourse?.name || "未选择课程"}</span>
      </div>
    </div>
  );
}
