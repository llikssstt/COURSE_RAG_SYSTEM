import type { ReactNode } from "react";

export function PageContainer({ children }: { children: ReactNode }) {
  return <main className="mx-auto w-full max-w-7xl px-6 py-8">{children}</main>;
}
