import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { BarChart3, Sparkles } from "lucide-react";
import { getErrorMessage } from "../api/client";
import { generateSummary } from "../api/summaries";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { Field, Input, Select } from "../components/ui/Form";
import { SourceList } from "../components/ui/SourceList";
import { useAppStore } from "../store/useAppStore";
import type { SummaryResponse } from "../types";

export function SummaryPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const llmConfig = useAppStore((state) => state.llmConfig);
  const [summaryType, setSummaryType] = useState("课程复习提纲");
  const [scope, setScope] = useState("");
  const [topK, setTopK] = useState(12);
  const [result, setResult] = useState<SummaryResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!currentCourse) {
    return (
      <PageContainer>
        <EmptyCourseNotice />
      </PageContainer>
    );
  }

  async function handleGenerate() {
    if (!currentCourse) return;
    try {
      setLoading(true);
      setError("");
      const data = await generateSummary(currentCourse.id, {
        summary_type: summaryType,
        scope,
        top_k: topK,
        llm_config: llmConfig,
      });
      setResult(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <Card>
          <CardHeader>
            <h1 className="text-2xl font-black text-slate-900">复习总结</h1>
            <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}</p>
          </CardHeader>
          <CardBody className="space-y-4">
            {error && <Alert tone="error">{error}</Alert>}
            <Field label="总结类型">
              <Select value={summaryType} onChange={(event) => setSummaryType(event.target.value)}>
                <option>课程复习提纲</option>
                <option>重点知识总结</option>
                <option>易混淆知识点</option>
                <option>考前速记卡片</option>
              </Select>
            </Field>
            <Field label="知识范围">
              <Input value={scope} onChange={(event) => setScope(event.target.value)} placeholder="可留空，例如：进程管理" />
            </Field>
            <Field label="参考资料数量 top_k">
              <Input type="number" min={1} max={30} value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
            </Field>
            <Button onClick={handleGenerate} disabled={loading} className="w-full">
              <Sparkles className="h-4 w-4" />
              {loading ? "生成中..." : "生成总结"}
            </Button>
          </CardBody>
        </Card>
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <BarChart3 className="h-5 w-5 text-brand-600" />
                <h2 className="text-xl font-bold text-slate-900">总结内容</h2>
              </div>
            </CardHeader>
            <CardBody>
              {result ? (
                <div className="markdown max-w-none">
                  <ReactMarkdown>{result.summary}</ReactMarkdown>
                </div>
              ) : (
                <p className="py-16 text-center text-sm text-slate-500">选择总结类型后生成课程复习材料。</p>
              )}
            </CardBody>
          </Card>
          {result && (
            <Card>
              <CardHeader>
                <h2 className="text-lg font-bold text-slate-900">资料来源</h2>
              </CardHeader>
              <CardBody>
                <SourceList sources={result.sources} />
              </CardBody>
            </Card>
          )}
        </div>
      </div>
    </PageContainer>
  );
}
