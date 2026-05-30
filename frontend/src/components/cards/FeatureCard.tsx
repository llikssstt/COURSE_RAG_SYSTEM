import { ArrowRight } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

export function FeatureCard({
  title,
  description,
  icon: Icon,
  to,
}: {
  title: string;
  description: string;
  icon: LucideIcon;
  to: string;
}) {
  return (
    <Link
      to={to}
      className="group rounded-card border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-brand-100 hover:shadow-md"
    >
      <div className="mb-8 flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-brand-600">
        <Icon className="h-7 w-7" />
      </div>
      <div className="flex items-end justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900">{title}</h3>
          <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
        </div>
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-50 text-brand-600 transition group-hover:bg-brand-500 group-hover:text-white">
          <ArrowRight className="h-5 w-5" />
        </span>
      </div>
    </Link>
  );
}
