import { useEffect, useState } from "react";
import { MessageCircle, Send, Sparkles } from "lucide-react";
import { getErrorMessage } from "../api/client";
import { askCourse, listQAHistory } from "../api/qa";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { Field, Input, Textarea } from "../components/ui/Form";
import { SourceList } from "../components/ui/SourceList";
import { useAppStore } from "../store/useAppStore";
import type { QAHistoryItem, QAResponse } from "../types";

export function QAPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const llmConfig = useAppStore((state) => state.llmConfig);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [answer, setAnswer] = useState<QAResponse | null>(null);
  const [history, setHistory] = useState<QAHistoryItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refreshHistory() {
    if (!currentCourse) return;
    try {
      setHistory(await listQAHistory(currentCourse.id));
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    refreshHistory();
  }, [currentCourse?.id]);

  if (!currentCourse) {
    return (
      <PageContainer>
        <EmptyCourseNotice />
      </PageContainer>
    );
  }

  async function handleAsk() {
    if (!currentCourse) return;
    if (!question.trim()) {
      setError("请输入问题。");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const data = await askCourse(currentCourse.id, { question: question.trim(), top_k: topK, llm_config: llmConfig });
      setAnswer(data);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[1fr_420px]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h1 className="text-2xl font-black text-slate-900">智能问答</h1>
              <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}，只检索当前课程知识库。</p>
            </CardHeader>
            <CardBody className="space-y-4">
              {error && <Alert tone="error">{error}</Alert>}
              <Field label="问题">
                <Textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="例如：请求分页和基本分页有什么区别？" />
              </Field>
              <Field label="检索数量 top_k">
                <Input type="number" min={1} max={20} value={topK} onChange={(event) => setTopK(Number(event.target.value))} />
              </Field>
              <Button onClick={handleAsk} disabled={loading}>
                <Send className="h-4 w-4" />
                {loading ? "生成中..." : "提交问题"}
              </Button>
            </CardBody>
          </Card>

          {answer && (
            <div className="space-y-4">
              <Card className="bg-slate-900 text-white">
                <CardBody>
                  <div className="mb-3 flex items-center gap-2">
                    <MessageCircle className="h-5 w-5 text-brand-300" />
                    <span className="font-semibold">用户问题</span>
                  </div>
                  <p className="leading-7">{question}</p>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-brand-600" />
                    <span className="font-bold text-slate-900">AI 回答</span>
                  </div>
                  <div className="whitespace-pre-wrap leading-8 text-slate-700">{answer.answer}</div>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <Badge tone="green">检索策略：{answer.retrieval_mode || "-"}</Badge>
                    <Badge tone="blue">查询类型：{answer.route_type || "-"}</Badge>
                    <Badge tone="slate">检索查询：{answer.retrieval_query || "-"}</Badge>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-bold text-slate-900">参考来源</h2>
                </CardHeader>
                <CardBody>
                  <SourceList sources={answer.sources} />
                </CardBody>
              </Card>
            </div>
          )}
        </div>
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-slate-900">问答历史</h2>
          </CardHeader>
          <CardBody className="max-h-[760px] space-y-4 overflow-y-auto">
            {history.map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-semibold text-slate-900">{item.question}</p>
                <p className="mt-2 line-clamp-4 whitespace-pre-wrap text-sm leading-6 text-slate-600">{item.answer}</p>
                <p className="mt-3 text-xs text-slate-400">{item.created_at}</p>
              </div>
            ))}
            {!history.length && <p className="py-10 text-center text-sm text-slate-500">暂无问答历史。</p>}
          </CardBody>
        </Card>
      </div>
    </PageContainer>
  );
}
