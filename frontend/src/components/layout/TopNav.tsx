import { NavLink } from "react-router-dom";
import { BarChart3, BookOpen, ClipboardList, FileQuestion, Home, MessageCircle, Upload, User } from "lucide-react";
import { useAppStore } from "../../store/useAppStore";

const navItems = [
  { to: "/", label: "首页 / 项目介绍", icon: Home },
  { to: "/courses", label: "课程管理", icon: BookOpen },
  { to: "/upload", label: "资料上传", icon: Upload },
  { to: "/qa", label: "智能问答", icon: MessageCircle },
  { to: "/questions", label: "自动出题", icon: FileQuestion },
  { to: "/wrong-book", label: "错题本", icon: ClipboardList },
  { to: "/summary", label: "复习总结", icon: BarChart3 },
];

export function TopNav() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center gap-6 px-6">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-500 text-white">
            <BookOpen className="h-6 w-6" />
          </div>
          <div className="hidden min-w-0 lg:block">
            <p className="truncate text-lg font-bold text-slate-900">基于 RAG 的多课程资料智能问答与习题生成系统</p>
            <p className="truncate text-xs text-slate-500">{currentCourse ? `当前课程：${currentCourse.name}` : "当前课程：未选择"}</p>
          </div>
        </div>
        <nav className="flex flex-1 items-center justify-center gap-1 overflow-x-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `group relative flex h-[72px] shrink-0 items-center gap-2 px-3 text-sm font-semibold transition ${
                  isActive ? "text-brand-600" : "text-slate-600 hover:text-brand-600"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon className="h-5 w-5" />
                  <span className="hidden xl:inline">{item.label}</span>
                  <span className={`absolute bottom-0 left-2 right-2 h-0.5 rounded-full ${isActive ? "bg-brand-500" : "bg-transparent"}`} />
                </>
              )}
            </NavLink>
          ))}
        </nav>
        <button className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <User className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
