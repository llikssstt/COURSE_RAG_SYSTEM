import type { ReactNode } from "react";

export function Badge({ children, tone = "green" }: { children: ReactNode; tone?: "green" | "blue" | "slate" | "amber" }) {
  const tones = {
    green: "bg-brand-50 text-brand-700 ring-brand-100",
    blue: "bg-blue-50 text-blue-700 ring-blue-100",
    slate: "bg-slate-100 text-slate-700 ring-slate-200",
    amber: "bg-amber-50 text-amber-700 ring-amber-100",
  };
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ring-1 ${tones[tone]}`}>{children}</span>;
}
