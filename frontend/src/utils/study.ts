import type { QuestionItem, QuestionRecord, Source } from "../types";

export function parseSources(value: unknown): Source[] {
  if (!value) return [];
  if (Array.isArray(value)) return value.filter((item): item is Source => typeof item === "object" && item !== null);
  if (typeof value === "string") {
    try {
      const parsed = JSON.parse(value);
      return Array.isArray(parsed) ? parsed : [{ source_file: value }];
    } catch {
      return value.trim() ? [{ source_file: value }] : [];
    }
  }
  return [];
}

export function normalizeAnswer(value?: string): string {
  const text = (value || "").trim();
  const choice = text.match(/[A-D]/i);
  if (choice) return choice[0].toUpperCase();
  if (/正确|对|true|√/i.test(text)) return "正确";
  if (/错误|错|false|×/i.test(text)) return "错误";
  return text.replace(/^答案[:：]\s*/, "").trim();
}

export function extractOptionsFromText(text: string): Array<{ key: string; text: string }> {
  const lines = text.split(/\r?\n/);
  return lines
    .map((line) => {
      const match = line.trim().match(/^([A-D])[\.\、\s]+(.+)$/i);
      return match ? { key: match[1].toUpperCase(), text: match[2].trim() } : null;
    })
    .filter((item): item is { key: string; text: string } => item !== null);
}

export function normalizeOptions(options: QuestionItem["options"], fallbackText = ""): Array<{ key: string; text: string }> {
  if (Array.isArray(options)) {
    return options.map((option, index) => {
      const text = String(option);
      const match = text.match(/^([A-D])[\.\、\s]+(.+)$/i);
      return { key: match?.[1]?.toUpperCase() || String.fromCharCode(65 + index), text: match?.[2] || text };
    });
  }
  if (options && typeof options === "object") {
    return Object.entries(options).map(([key, value]) => ({ key, text: String(value) }));
  }
  return extractOptionsFromText(fallbackText);
}

export function questionRecordToItem(record: QuestionRecord): QuestionItem {
  return {
    question_content: record.question_content,
    answer: record.answer,
    analysis: record.analysis,
    knowledge_point: record.knowledge_point,
    sources: record.sources,
  };
}
