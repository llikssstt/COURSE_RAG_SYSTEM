import { useEffect, useState } from "react";
import { BookMarked, FileQuestion, ListChecks, RefreshCcw, Search, Trash2, Wand2 } from "lucide-react";
import { getErrorMessage } from "../api/client";
import {
  deleteQuestionRecord,
  deleteQuestionRecords,
  generateQuestions,
  getQuestionRecord,
  listQuestionHistory,
} from "../api/questions";
import { createWrongQuestion } from "../api/wrongQuestions";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { Field, Input, Select } from "../components/ui/Form";
import { SourceList } from "../components/ui/SourceList";
import { useAppStore } from "../store/useAppStore";
import type { QuestionItem, QuestionRecord, Source } from "../types";
import { normalizeAnswer, normalizeOptions, parseSources, questionRecordToItem } from "../utils/study";

export function QuestionPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const llmConfig = useAppStore((state) => state.llmConfig);
  const [scope, setScope] = useState("虚拟内存");
  const [questionType, setQuestionType] = useState("选择题");
  const [difficulty, setDifficulty] = useState("中等");
  const [count, setCount] = useState(5);
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [sources, setSources] = useState<Source[]>([]);
  const [history, setHistory] = useState<QuestionRecord[]>([]);
  const [historyDetail, setHistoryDetail] = useState<QuestionRecord | null>(null);
  const [selectedHistoryIds, setSelectedHistoryIds] = useState<number[]>([]);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [historyKeyword, setHistoryKeyword] = useState("");
  const [historyType, setHistoryType] = useState("");
  const [historyDifficulty, setHistoryDifficulty] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refreshHistory() {
    if (!currentCourse) return;
    try {
      setError("");
      setHistory(
        await listQuestionHistory(currentCourse.id, {
          keyword: historyKeyword,
          question_type: historyType,
          difficulty: historyDifficulty,
          limit: 100,
        }),
      );
      setSelectedHistoryIds([]);
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

  async function handleGenerate() {
    if (!currentCourse) return;
    try {
      setLoading(true);
      setError("");
      setMessage("");
      setQuestions([]);
      setSelectedAnswers({});
      const result = await generateQuestions(currentCourse.id, {
        scope,
        question_type: questionType,
        difficulty,
        count,
        with_answer: true,
        llm_config: llmConfig,
      });
      setQuestions(result.questions || []);
      setSources((result.sources || []) as Source[]);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function openHistory(record: QuestionRecord) {
    if (!currentCourse) return;
    try {
      const detail = await getQuestionRecord(currentCourse.id, record.id);
      setHistoryDetail(detail);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function retryHistory(record: QuestionRecord) {
    setQuestions([questionRecordToItem(record)]);
    setSources(parseSources(record.sources));
    setSelectedAnswers({});
    setMessage("已载入历史题目，可重新练习。");
  }

  async function deleteOne(id: number) {
    if (!currentCourse) return;
    if (!window.confirm("确认删除这道历史题目吗？")) return;
    try {
      const result = await deleteQuestionRecord(currentCourse.id, id);
      setMessage(`已删除 ${result.deleted} 道题目。`);
      if (historyDetail?.id === id) setHistoryDetail(null);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function deleteSelected() {
    if (!currentCourse) return;
    if (!selectedHistoryIds.length) return;
    if (!window.confirm(`确认删除选中的 ${selectedHistoryIds.length} 道历史题目吗？`)) return;
    try {
      const result = await deleteQuestionRecords(currentCourse.id, selectedHistoryIds);
      setMessage(`已删除 ${result.deleted} 道题目。`);
      if (historyDetail && selectedHistoryIds.includes(historyDetail.id)) setHistoryDetail(null);
      await refreshHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  async function addToWrongBook(item: QuestionItem, index: number, record?: QuestionRecord) {
    if (!currentCourse) return;
    const itemSources = parseSources(record?.sources || item.sources || sources);
    try {
      await createWrongQuestion(currentCourse.id, {
        question_id: record?.id || null,
        source_type: record ? "question_bank" : "generated",
        question_type: record?.question_type || questionType,
        difficulty: record?.difficulty || difficulty,
        question_content: item.question_content,
        user_answer: selectedAnswers[index] || "",
        correct_answer: item.answer || "",
        analysis: item.analysis || "",
        knowledge_point: item.knowledge_point || "",
        sources: itemSources,
        note: "",
      });
      setMessage("已加入错题本。");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  function toggleSelected(id: number) {
    setSelectedHistoryIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  }

  function renderExercise(item: QuestionItem, index: number, record?: QuestionRecord) {
    const options = normalizeOptions(item.options, item.question_content);
    const selected = selectedAnswers[index] || "";
    const correct = normalizeAnswer(item.answer);
    const canJudge = options.length > 0 && selected;
    const isCorrect = canJudge && normalizeAnswer(selected) === correct;

    return (
      <Card key={`${record?.id || "generated"}-${index}`}>
        <CardBody>
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-50 text-brand-600">
              <FileQuestion className="h-5 w-5" />
            </div>
            <div>
              <h2 className="font-bold text-slate-900">第 {index + 1} 题</h2>
              <p className="text-xs text-slate-500">{item.knowledge_point || "课程资料知识点"}</p>
            </div>
          </div>
          <p className="whitespace-pre-wrap text-base font-semibold leading-8 text-slate-900">{item.question_content}</p>
          {options.length > 0 && (
            <div className="mt-4 space-y-3">
              {options.map((option) => (
                <label key={option.key} className="flex cursor-pointer items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 transition hover:border-brand-200 hover:bg-brand-50">
                  <input
                    type="radio"
                    name={`question-${index}-${record?.id || "generated"}`}
                    value={option.key}
                    checked={selectedAnswers[index] === option.key}
                    onChange={() => setSelectedAnswers({ ...selectedAnswers, [index]: option.key })}
                    className="mt-1 h-4 w-4 accent-brand-500"
                  />
                  <span className="text-sm leading-6 text-slate-700">
                    <b>{option.key}.</b> {option.text}
                  </span>
                </label>
              ))}
            </div>
          )}
          <details className="mt-5 rounded-2xl border border-slate-100 bg-white p-4">
            <summary className="cursor-pointer font-semibold text-brand-700">查看答案与解析</summary>
            <div className="mt-4 space-y-3 text-sm leading-7 text-slate-700">
              {options.length > 0 && selected && (
                <Alert tone={isCorrect ? "success" : "error"}>
                  {isCorrect ? "回答正确" : "回答错误，可加入错题本"}
                </Alert>
              )}
              <p><b>你的选择：</b>{selected || "未选择"}</p>
              <p><b>答案：</b>{item.answer || "-"}</p>
              <p><b>解析：</b>{item.analysis || "-"}</p>
              <p><b>知识点：</b>{item.knowledge_point || "-"}</p>
              <Button variant="secondary" onClick={() => addToWrongBook(item, index, record)}>
                <BookMarked className="h-4 w-4" />
                加入错题本
              </Button>
            </div>
          </details>
        </CardBody>
      </Card>
    );
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[460px_1fr]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h1 className="text-2xl font-black text-slate-900">自动出题</h1>
              <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}</p>
            </CardHeader>
            <CardBody className="space-y-4">
              {message && <Alert tone="success">{message}</Alert>}
              {error && <Alert tone="error">{error}</Alert>}
              <Field label="知识范围或关键词">
                <Input value={scope} onChange={(event) => setScope(event.target.value)} />
              </Field>
              <Field label="题型">
                <Select value={questionType} onChange={(event) => setQuestionType(event.target.value)}>
                  <option>选择题</option>
                  <option>判断题</option>
                  <option>填空题</option>
                  <option>简答题</option>
                </Select>
              </Field>
              <Field label="难度">
                <Select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                  <option>简单</option>
                  <option>中等</option>
                  <option>困难</option>
                </Select>
              </Field>
              <Field label="题目数量">
                <Input type="number" min={1} max={20} value={count} onChange={(event) => setCount(Number(event.target.value))} />
              </Field>
              <Button onClick={handleGenerate} disabled={loading} className="w-full">
                <Wand2 className="h-4 w-4" />
                {loading ? "生成中..." : "生成题目"}
              </Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-xl font-bold text-slate-900">历史题目记录</h2>
                <Button variant="ghost" onClick={refreshHistory}>
                  <RefreshCcw className="h-4 w-4" />
                  刷新
                </Button>
              </div>
              <div className="mt-4 grid gap-3">
                <Input value={historyKeyword} onChange={(event) => setHistoryKeyword(event.target.value)} placeholder="搜索题干、知识点、答案或解析" />
                <div className="grid grid-cols-2 gap-3">
                  <Select value={historyType} onChange={(event) => setHistoryType(event.target.value)}>
                    <option value="">全部题型</option>
                    <option>选择题</option>
                    <option>判断题</option>
                    <option>填空题</option>
                    <option>简答题</option>
                  </Select>
                  <Select value={historyDifficulty} onChange={(event) => setHistoryDifficulty(event.target.value)}>
                    <option value="">全部难度</option>
                    <option>简单</option>
                    <option>中等</option>
                    <option>困难</option>
                  </Select>
                </div>
                <Button onClick={refreshHistory}>
                  <Search className="h-4 w-4" />
                  搜索历史题目
                </Button>
                {selectedHistoryIds.length > 0 && (
                  <Button variant="danger" onClick={deleteSelected}>
                    <Trash2 className="h-4 w-4" />
                    批量删除 {selectedHistoryIds.length} 道
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardBody className="max-h-[680px] space-y-3 overflow-y-auto">
              {history.map((item) => (
                <div key={item.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                  <div className="mb-3 flex items-start gap-3">
                    <input type="checkbox" checked={selectedHistoryIds.includes(item.id)} onChange={() => toggleSelected(item.id)} className="mt-1 h-4 w-4 accent-brand-500" />
                    <button className="flex-1 text-left" onClick={() => openHistory(item)}>
                      <div className="mb-2 flex flex-wrap gap-2">
                        <Badge tone="green">{item.question_type}</Badge>
                        <Badge tone="slate">{item.difficulty}</Badge>
                      </div>
                      <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{item.question_content}</p>
                      <p className="mt-3 text-xs text-slate-400">{item.created_at}</p>
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="secondary" onClick={() => openHistory(item)}>查看详情</Button>
                    <Button variant="secondary" onClick={() => retryHistory(item)}>重新练习</Button>
                    <Button variant="secondary" onClick={() => addToWrongBook(questionRecordToItem(item), 0, item)}>加入错题本</Button>
                    <Button variant="ghost" onClick={() => deleteOne(item.id)}>删除</Button>
                  </div>
                </div>
              ))}
              {!history.length && <p className="py-8 text-center text-sm text-slate-500">暂无题目记录。</p>}
            </CardBody>
          </Card>
        </div>

        <div className="space-y-5">
          {historyDetail && (
            <Card className="border-brand-200">
              <CardHeader>
                <div className="flex flex-wrap items-center gap-2">
                  <Badge>{historyDetail.question_type}</Badge>
                  <Badge tone="slate">{historyDetail.difficulty}</Badge>
                  <span className="text-xs text-slate-400">{historyDetail.created_at}</span>
                </div>
              </CardHeader>
              <CardBody className="space-y-4">
                <h2 className="text-lg font-bold text-slate-900">历史题目详情</h2>
                <p className="whitespace-pre-wrap leading-8 text-slate-800">{historyDetail.question_content}</p>
                <div className="rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                  <p><b>答案：</b>{historyDetail.answer || "-"}</p>
                  <p><b>解析：</b>{historyDetail.analysis || "-"}</p>
                  <p><b>知识点：</b>{historyDetail.knowledge_point || "-"}</p>
                </div>
                <SourceList sources={parseSources(historyDetail.sources)} />
                <div className="flex flex-wrap gap-2">
                  <Button variant="secondary" onClick={() => retryHistory(historyDetail)}>重新练习</Button>
                  <Button variant="secondary" onClick={() => addToWrongBook(questionRecordToItem(historyDetail), 0, historyDetail)}>加入错题本</Button>
                  <Button variant="ghost" onClick={() => deleteOne(historyDetail.id)}>删除</Button>
                </div>
              </CardBody>
            </Card>
          )}

          {questions.map((item, index) => renderExercise(item, index))}
          {questions.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <ListChecks className="h-5 w-5 text-brand-600" />
                  <h2 className="text-lg font-bold text-slate-900">资料来源</h2>
                </div>
              </CardHeader>
              <CardBody>
                <SourceList sources={sources} />
              </CardBody>
            </Card>
          )}
          {!questions.length && !historyDetail && <Alert>设置知识范围、题型、难度和数量后生成题目。答案与解析默认折叠，适合先自测再查看。</Alert>}
        </div>
      </div>
    </PageContainer>
  );
}
