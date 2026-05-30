import type { Source } from "../../types";
import { Badge } from "./Badge";

function sourceTitle(source: Source): string {
  const loc = source.page_number
    ? `第 ${source.page_number} 页`
    : source.slide_number
      ? `第 ${source.slide_number} 页幻灯片`
      : source.section_title || "";
  return [source.source_file || "课程资料", loc].filter(Boolean).join(" · ");
}

export function SourceList({ sources }: { sources?: Source[] }) {
  if (!sources?.length) {
    return <p className="text-sm text-slate-500">暂无来源信息。</p>;
  }
  return (
    <div className="space-y-2">
      {sources.map((source, index) => (
        <div key={index} className="rounded-2xl border border-slate-100 bg-slate-50 p-3">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge tone="slate">{sourceTitle(source)}</Badge>
            {typeof source.score === "number" ? <Badge tone="green">score {source.score.toFixed(3)}</Badge> : null}
          </div>
          {(source.chunk_text || source.text) && (
            <p className="line-clamp-3 text-sm leading-6 text-slate-600">{String(source.chunk_text || source.text)}</p>
          )}
        </div>
      ))}
    </div>
  );
}
