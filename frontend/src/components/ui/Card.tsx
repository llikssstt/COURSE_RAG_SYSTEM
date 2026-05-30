import type { HTMLAttributes, ReactNode } from "react";

export function Card({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div className={`rounded-card border border-slate-200 bg-white shadow-sm ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardHeader({ className = "", children }: { className?: string; children: ReactNode }) {
  return <div className={`border-b border-slate-100 px-6 py-5 ${className}`}>{children}</div>;
}

export function CardBody({ className = "", children }: { className?: string; children: ReactNode }) {
  return <div className={`p-6 ${className}`}>{children}</div>;
}
