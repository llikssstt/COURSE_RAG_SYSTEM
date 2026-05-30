import { AlertCircle, Info } from "lucide-react";
import type { ReactNode } from "react";

export function Alert({
  children,
  tone = "info",
}: {
  children: ReactNode;
  tone?: "info" | "error" | "success";
}) {
  const styles = {
    info: "border-blue-100 bg-blue-50 text-blue-800",
    error: "border-red-100 bg-red-50 text-red-700",
    success: "border-brand-100 bg-brand-50 text-brand-700",
  };
  const Icon = tone === "error" ? AlertCircle : Info;
  return (
    <div className={`flex gap-3 rounded-2xl border p-4 text-sm ${styles[tone]}`}>
      <Icon className="mt-0.5 h-5 w-5 shrink-0" />
      <div>{children}</div>
    </div>
  );
}
