import { useEffect, useMemo, useState } from "react";
import { BookMarked, CheckCircle, RefreshCcw, Search, Trash2 } from "lucide-react";
import {
  deleteWrongQuestion,
  deleteWrongQuestions,
  getWrongQuestion,
  listWrongQuestions,
  markWrongQuestionReviewed,
  updateWrongQuestion,
} from "../api/wrongQuestions";
import { getErrorMessage } from "../api/client";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { Field, Input, Select, Textarea } from "../components/ui/Form";
import { SourceList } from "../components/ui/SourceList";
import { useAppStore } from "../store/useAppStore";
import type { WrongQuestion } from "../types";
import { parseSources } from "../utils/study";

export function WrongBookPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const [items, setItems] = useState<WrongQuestion[]>([]);
  const [detail, setDetail] = useState<WrongQuestion | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [keyword, setKeyword] = useState("");
  const [status, setStatus] = useState("");
  const [knowledgePoint, setKnowledgePoint] = useState("");
  const [noteDraft, setNoteDraft] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const stats = useMemo(() => {
    const total = items.length;
    const mastered = items.filter((item) => item.status === "已掌握").length;
    const unmastered = items.filter((item) => item.status === "未掌握").length;
    const today = new Date().toISOString().slice(0, 10);
    const reviewedToday = items.filter((item) => item.last_reviewed_at?.startsWith(today)).length;
    return { total, mastered, unmastered, reviewedToday };
  }, [items]);

  async function refresh() {
    if (!currentCourse) return;
    try {
      setError("");
      const data = await listWrongQuestions(currentCourse.id, {
        keyword,
        status,
        knowledge_point: knowledgePoint,
        limit: 100,
      });
      setItems(data);
      setSelectedIds([]);
      if (detail) {
        const updated = data.find((item) => item.id === detail.id);
        if (updated) {
          setDetail(updated);
          setNoteDraft(updated.note || "");
        }
      }
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    refresh();
  }, [currentCourse?.id]);

  if (!currentCourse) {
    return (
      <PageContainer>
        <EmptyCourseNotice />
      </PageContainer>
    );
  }

  async function openDetail(item: WrongQuestion) {
    if (!currentCourse) return;
    try {
      const data = await getWrongQuestion(currentCourse.id, item.id);
      setDetail(data);
      setNoteDraft(data.note || "");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function saveNote() {
    if (!currentCourse) return;
    if (!detail) return;
    try {
      const updated = await updateWrongQuestion(currentCourse.id, detail.id, { note: noteDraft });
      setDetail(updated);
      setMessage("备注已保存。");
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function setDetailStatus(nextStatus: "未掌握" | "已掌握") {
    if (!currentCourse) return;
    if (!detail) return;
    try {
      const updated = await updateWrongQuestion(currentCourse.id, detail.id, { status: nextStatus });
      setDetail(updated);
      setMessage(`已标记为${nextStatus}。`);
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function reviewOnce() {
    if (!currentCourse) return;
    if (!detail) return;
    try {
      const updated = await markWrongQuestionReviewed(currentCourse.id, detail.id);
      setDetail(updated);
      setMessage("已记录复习一次。");
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function removeOne(id: number) {
    if (!currentCourse) return;
    if (!window.confirm("确认删除这道错题吗？")) return;
    try {
      await deleteWrongQuestion(currentCourse.id, id);
      setMessage("错题已删除。");
      if (detail?.id === id) setDetail(null);
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function removeSelected() {
    if (!currentCourse) return;
    if (!selectedIds.length) return;
    if (!window.confirm(`确认删除选中的 ${selectedIds.length} 道错题吗？`)) return;
    try {
      const result = await deleteWrongQuestions(currentCourse.id, selectedIds);
      setMessage(`已删除 ${result.deleted} 道错题。`);
      if (detail && selectedIds.includes(detail.id)) setDetail(null);
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function toggleSelected(id: number) {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }

  return (
    <PageContainer>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <BookMarked className="h-7 w-7 text-brand-600" />
              <div>
                <h1 className="text-2xl font-black text-slate-900">错题本</h1>
                <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}</p>
              </div>
            </div>
          </CardHeader>
          <CardBody className="space-y-5">
            {message && <Alert tone="success">{message}</Alert>}
            {error && <Alert tone="error">{error}</Alert>}
            <div className="grid gap-4 md:grid-cols-4">
              <div className="rounded-2xl bg-brand-50 p-4"><p className="text-2xl font-black text-brand-700">{stats.total}</p><p className="text-sm text-slate-500">错题总数</p></div>
              <div className="rounded-2xl bg-red-50 p-4"><p className="text-2xl font-black text-red-600">{stats.unmastered}</p><p className="text-sm text-slate-500">未掌握</p></div>
              <div className="rounded-2xl bg-blue-50 p-4"><p className="text-2xl font-black text-blue-600">{stats.mastered}</p><p className="text-sm text-slate-500">已掌握</p></div>
              <div className="rounded-2xl bg-slate-50 p-4"><p className="text-2xl font-black text-slate-900">{stats.reviewedToday}</p><p className="text-sm text-slate-500">今日复习</p></div>
            </div>
            <div className="grid gap-3 lg:grid-cols-[1fr_160px_180px_auto]">
              <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="关键词搜索" />
              <Select value={status} onChange={(event) => setStatus(event.target.value)}>
                <option value="">全部状态</option>
                <option>未掌握</option>
                <option>已掌握</option>
              </Select>
              <Input value={knowledgePoint} onChange={(event) => setKnowledgePoint(event.target.value)} placeholder="知识点筛选" />
              <Button onClick={refresh}>
                <Search className="h-4 w-4" />
                筛选
              </Button>
            </div>
          </CardBody>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[460px_1fr]">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-bold text-slate-900">错题列表</h2>
                <Button variant="ghost" onClick={refresh}>
                  <RefreshCcw className="h-4 w-4" />
                  刷新
                </Button>
              </div>
              {selectedIds.length > 0 && (
                <div className="mt-3">
                  <Button variant="danger" onClick={removeSelected}>
                    <Trash2 className="h-4 w-4" />
                    批量删除 {selectedIds.length} 道
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardBody className="max-h-[760px] space-y-3 overflow-y-auto">
              {items.map((item) => (
                <div key={item.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                  <div className="mb-3 flex items-start gap-3">
                    <input type="checkbox" checked={selectedIds.includes(item.id)} onChange={() => toggleSelected(item.id)} className="mt-1 h-4 w-4 accent-brand-500" />
                    <button className="flex-1 text-left" onClick={() => openDetail(item)}>
                      <div className="mb-2 flex flex-wrap gap-2">
                        <Badge tone={item.status === "已掌握" ? "blue" : "amber"}>{item.status}</Badge>
                        <Badge tone="green">{item.question_type || "题目"}</Badge>
                        {item.difficulty && <Badge tone="slate">{item.difficulty}</Badge>}
                      </div>
                      <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{item.question_content.slice(0, 260)}{item.question_content.length > 260 ? "..." : ""}</p>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                        <span>知识点：{item.knowledge_point || "-"}</span>
                        <span>复习：{item.review_count} 次</span>
                        <span>{item.created_at}</span>
                      </div>
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="secondary" onClick={() => openDetail(item)}>查看详情</Button>
                    <Button variant="ghost" onClick={() => removeOne(item.id)}>删除</Button>
                  </div>
                </div>
              ))}
              {!items.length && <p className="py-10 text-center text-sm text-slate-500">暂无错题。</p>}
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-xl font-bold text-slate-900">错题详情</h2>
            </CardHeader>
            <CardBody>
              {detail ? (
                <div className="space-y-5">
                  <div className="flex flex-wrap gap-2">
                    <Badge tone={detail.status === "已掌握" ? "blue" : "amber"}>{detail.status}</Badge>
                    <Badge tone="green">{detail.question_type || "题目"}</Badge>
                    {detail.difficulty && <Badge tone="slate">{detail.difficulty}</Badge>}
                    <Badge tone="slate">复习 {detail.review_count} 次</Badge>
                  </div>
                  <p className="whitespace-pre-wrap text-base font-semibold leading-8 text-slate-900">{detail.question_content}</p>
                  <div className="rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                    <p><b>我的答案：</b>{detail.user_answer || "-"}</p>
                    <p><b>正确答案：</b>{detail.correct_answer || "-"}</p>
                    <p><b>解析：</b>{detail.analysis || "-"}</p>
                    <p><b>知识点：</b>{detail.knowledge_point || "-"}</p>
                    <p><b>最近复习：</b>{detail.last_reviewed_at || "-"}</p>
                  </div>
                  <Field label="我的备注">
                    <Textarea value={noteDraft} onChange={(event) => setNoteDraft(event.target.value)} />
                  </Field>
                  <SourceList sources={parseSources(detail.sources)} />
                  <div className="flex flex-wrap gap-3">
                    <Button onClick={saveNote}>保存备注</Button>
                    <Button variant="secondary" onClick={() => setDetailStatus("已掌握")}>
                      <CheckCircle className="h-4 w-4" />
                      标记为已掌握
                    </Button>
                    <Button variant="secondary" onClick={() => setDetailStatus("未掌握")}>标记为未掌握</Button>
                    <Button variant="secondary" onClick={reviewOnce}>复习一次</Button>
                    <Button variant="ghost" onClick={() => removeOne(detail.id)}>删除</Button>
                  </div>
                </div>
              ) : (
                <p className="py-16 text-center text-sm text-slate-500">点击左侧错题查看完整详情。</p>
              )}
            </CardBody>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
