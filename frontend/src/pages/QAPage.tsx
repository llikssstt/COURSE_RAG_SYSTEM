import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { BookMarked, Copy, MessageCircle, RefreshCcw, Search, Send, Sparkles, Trash2 } from "lucide-react";
import { getErrorMessage } from "../api/client";
import { askCourse, deleteQAHistoryItem, deleteQAHistoryItems, getQAHistoryItem, listQAHistory } from "../api/qa";
import { createWrongQuestion } from "../api/wrongQuestions";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { Field, Input, Textarea } from "../components/ui/Form";
import { SourceList } from "../components/ui/SourceList";
import { useAppStore } from "../store/useAppStore";
import type { QAHistoryItem, QAResponse, Source } from "../types";
import { parseSources } from "../utils/study";

export function QAPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const llmConfig = useAppStore((state) => state.llmConfig);
  const [question, setQuestion] = useState("");
  const [topK, setTopK] = useState(5);
  const [answer, setAnswer] = useState<QAResponse | null>(null);
  const [answerQuestion, setAnswerQuestion] = useState("");
  const [history, setHistory] = useState<QAHistoryItem[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<QAHistoryItem | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [keyword, setKeyword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refreshHistory() {
    if (!currentCourse) return;
    try {
      setError("");
      setHistory(await listQAHistory(currentCourse.id, { keyword, limit: 100 }));
      setSelectedIds([]);
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
      setMessage("");
      const asked = question.trim();
      const data = await askCourse(currentCourse.id, { question: asked, top_k: topK, llm_config: llmConfig });
      setAnswer(data);
      setAnswerQuestion(asked);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function openHistory(item: QAHistoryItem) {
    if (!currentCourse) return;
    try {
      setError("");
      const detail = await getQAHistoryItem(currentCourse.id, item.id);
      setSelectedHistory(detail);
      setAnswer({
        answer: detail.answer,
        sources: parseSources(detail.sources),
        retrieval_mode: "history",
        route_type: "history",
        retrieval_query: detail.question,
      });
      setAnswerQuestion(detail.question);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function removeOne(id: number) {
    if (!currentCourse) return;
    if (!window.confirm("确认删除这条问答历史吗？")) return;
    try {
      await deleteQAHistoryItem(currentCourse.id, id);
      setMessage("问答历史已删除。");
      if (selectedHistory?.id === id) setSelectedHistory(null);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function removeSelected() {
    if (!currentCourse) return;
    if (!selectedIds.length) return;
    if (!window.confirm(`确认删除选中的 ${selectedIds.length} 条问答历史吗？`)) return;
    try {
      const result = await deleteQAHistoryItems(currentCourse.id, selectedIds);
      setMessage(`已删除 ${result.deleted} 条问答历史。`);
      if (selectedHistory && selectedIds.includes(selectedHistory.id)) setSelectedHistory(null);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function copyAnswer(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setMessage("回答已复制到剪贴板。");
    } catch {
      setError("复制失败，当前浏览器可能未授权剪贴板访问。");
    }
  }

  async function addQAAsWrongCard(item?: QAHistoryItem) {
    if (!currentCourse) return;
    const sourceQuestion = item?.question || answerQuestion;
    const sourceAnswer = item?.answer || answer?.answer || "";
    const sourceSources = parseSources(item?.sources || answer?.sources || []);
    if (!sourceQuestion || !sourceAnswer) {
      setError("没有可加入错题本的问答内容。");
      return;
    }
    try {
      await createWrongQuestion(currentCourse.id, {
        question_id: null,
        source_type: "qa_history",
        question_type: "问答复习",
        difficulty: "",
        question_content: sourceQuestion,
        user_answer: "",
        correct_answer: sourceAnswer,
        analysis: sourceAnswer,
        knowledge_point: "",
        sources: sourceSources,
        note: "由问答历史加入",
      });
      setMessage("已加入错题本。");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function toggleSelected(id: number) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[1fr_460px]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h1 className="text-2xl font-black text-slate-900">智能问答</h1>
              <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}，只检索当前课程知识库。</p>
            </CardHeader>
            <CardBody className="space-y-4">
              {message && <Alert tone="success">{message}</Alert>}
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
                  <p className="leading-7">{answerQuestion}</p>
                </CardBody>
              </Card>
              <Card>
                <CardBody>
                  <div className="mb-4 flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-brand-600" />
                    <span className="font-bold text-slate-900">AI 回答</span>
                  </div>
                  <div className="markdown">
                    <ReactMarkdown>{answer.answer}</ReactMarkdown>
                  </div>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <Badge tone="green">检索策略：{answer.retrieval_mode || "-"}</Badge>
                    <Badge tone="blue">查询类型：{answer.route_type || "-"}</Badge>
                    <Badge tone="slate">检索查询：{answer.retrieval_query || "-"}</Badge>
                  </div>
                  <div className="mt-5 flex flex-wrap gap-3">
                    <Button variant="secondary" onClick={() => copyAnswer(answer.answer)}>
                      <Copy className="h-4 w-4" />
                      复制回答
                    </Button>
                    <Button variant="secondary" onClick={() => addQAAsWrongCard(selectedHistory || undefined)}>
                      <BookMarked className="h-4 w-4" />
                      加入错题本 / 复习卡片
                    </Button>
                  </div>
                </CardBody>
              </Card>
              <Card>
                <CardHeader>
                  <h2 className="text-lg font-bold text-slate-900">参考来源</h2>
                </CardHeader>
                <CardBody>
                  <SourceList sources={answer.sources as Source[]} />
                </CardBody>
              </Card>
            </div>
          )}
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xl font-bold text-slate-900">问答历史</h2>
              <Button variant="ghost" onClick={refreshHistory}>
                <RefreshCcw className="h-4 w-4" />
                刷新
              </Button>
            </div>
            <div className="mt-4 flex gap-2">
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索问题或回答" />
              <Button onClick={refreshHistory}>
                <Search className="h-4 w-4" />
              </Button>
            </div>
            {selectedIds.length > 0 && (
              <div className="mt-3">
                <Button variant="danger" onClick={removeSelected}>
                  <Trash2 className="h-4 w-4" />
                  批量删除 {selectedIds.length} 条
                </Button>
              </div>
            )}
          </CardHeader>
          <CardBody className="max-h-[780px] space-y-4 overflow-y-auto">
            {history.map((item) => (
              <div key={item.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                <div className="mb-3 flex items-start gap-3">
                  <input type="checkbox" checked={selectedIds.includes(item.id)} onChange={() => toggleSelected(item.id)} className="mt-1 h-4 w-4 accent-brand-500" />
                  <button className="flex-1 text-left" onClick={() => openHistory(item)}>
                    <p className="font-semibold leading-6 text-slate-900">{item.question}</p>
                    <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">{item.answer.slice(0, 220)}{item.answer.length > 220 ? "..." : ""}</p>
                    <p className="mt-3 text-xs text-slate-400">{item.created_at}</p>
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button variant="secondary" onClick={() => openHistory(item)}>查看详情</Button>
                  <Button variant="secondary" onClick={() => setQuestion(item.question)}>重新提问</Button>
                  <Button variant="secondary" onClick={() => copyAnswer(item.answer)}>复制回答</Button>
                  <Button variant="secondary" onClick={() => addQAAsWrongCard(item)}>加入错题本</Button>
                  <Button variant="ghost" onClick={() => removeOne(item.id)}>删除</Button>
                </div>
              </div>
            ))}
            {!history.length && <p className="py-10 text-center text-sm text-slate-500">暂无问答历史。</p>}
          </CardBody>
        </Card>
      </div>
    </PageContainer>
  );
}
