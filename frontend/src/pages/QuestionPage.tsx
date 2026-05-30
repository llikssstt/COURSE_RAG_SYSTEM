import { useEffect, useState } from "react";
import { FileQuestion, ListChecks, Wand2 } from "lucide-react";
import { getErrorMessage } from "../api/client";
import { generateQuestions, listQuestionHistory } from "../api/questions";
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

function normalizeOptions(options: QuestionItem["options"]): Array<{ key: string; text: string }> {
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
  return [];
}

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
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refreshHistory() {
    if (!currentCourse) return;
    try {
      setHistory(await listQuestionHistory(currentCourse.id));
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
      setQuestions([]);
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

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[420px_1fr]">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h1 className="text-2xl font-black text-slate-900">自动出题</h1>
              <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}</p>
            </CardHeader>
            <CardBody className="space-y-4">
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
              <h2 className="text-xl font-bold text-slate-900">历史题目记录</h2>
            </CardHeader>
            <CardBody className="max-h-[520px] space-y-3 overflow-y-auto">
              {history.map((item) => (
                <div key={item.id} className="rounded-2xl border border-slate-100 bg-slate-50 p-4">
                  <div className="mb-2 flex flex-wrap gap-2">
                    <Badge tone="green">{item.question_type}</Badge>
                    <Badge tone="slate">{item.difficulty}</Badge>
                  </div>
                  <p className="line-clamp-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{item.question_content}</p>
                </div>
              ))}
              {!history.length && <p className="py-8 text-center text-sm text-slate-500">暂无题目记录。</p>}
            </CardBody>
          </Card>
        </div>
        <div className="space-y-5">
          {questions.map((item, index) => {
            const options = normalizeOptions(item.options);
            return (
              <Card key={index}>
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
                            name={`question-${index}`}
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
                      <p><b>你的选择：</b>{selectedAnswers[index] || "未选择"}</p>
                      <p><b>答案：</b>{item.answer || "-"}</p>
                      <p><b>解析：</b>{item.analysis || "-"}</p>
                      <p><b>知识点：</b>{item.knowledge_point || "-"}</p>
                      <p><b>来源：</b>{typeof item.sources === "string" ? item.sources || "见下方公共来源" : "见下方公共来源"}</p>
                    </div>
                  </details>
                </CardBody>
              </Card>
            );
          })}
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
          {!questions.length && <Alert>设置知识范围、题型、难度和数量后生成题目。答案与解析默认折叠，适合先自测再查看。</Alert>}
        </div>
      </div>
    </PageContainer>
  );
}
