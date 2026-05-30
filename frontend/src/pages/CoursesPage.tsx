import { useEffect, useState } from "react";
import { BookOpen, CheckCircle, Database, FileQuestion, MessageCircle, Plus } from "lucide-react";
import { createCourse, getCourseStats, listCourses } from "../api/courses";
import { getErrorMessage } from "../api/client";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { Field, Input, Textarea } from "../components/ui/Form";
import { useAppStore } from "../store/useAppStore";
import type { Course, CourseStats } from "../types";

const statItems = [
  { key: "document_count", label: "资料数量", icon: Database },
  { key: "chunk_count", label: "Chunk 数", icon: BookOpen },
  { key: "qa_count", label: "问答历史", icon: MessageCircle },
  { key: "question_count", label: "题目数量", icon: FileQuestion },
] as const;

export function CoursesPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const setCurrentCourse = useAppStore((state) => state.setCurrentCourse);
  const [courses, setCourses] = useState<Course[]>([]);
  const [stats, setStats] = useState<Record<number, CourseStats>>({});
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try {
      setError("");
      const data = await listCourses();
      setCourses(data);
      const statPairs = await Promise.all(data.map(async (course) => [course.id, await getCourseStats(course.id)] as const));
      setStats(Object.fromEntries(statPairs));
    } catch (err) {
      setError(getErrorMessage(err));
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate() {
    if (!name.trim()) {
      setError("请输入课程名称。");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const course = await createCourse({ name: name.trim(), description: description.trim() });
      setName("");
      setDescription("");
      setCurrentCourse(course);
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <Card>
          <CardHeader>
            <h1 className="text-2xl font-black text-slate-900">课程管理</h1>
            <p className="mt-2 text-sm text-slate-500">每门课程对应一个独立 Chroma collection。</p>
          </CardHeader>
          <CardBody className="space-y-4">
            {error && <Alert tone="error">{error}</Alert>}
            <Field label="课程名称">
              <Input value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：操作系统" />
            </Field>
            <Field label="课程描述">
              <Textarea value={description} onChange={(event) => setDescription(event.target.value)} placeholder="课程范围、资料来源或复习说明" />
            </Field>
            <Button onClick={handleCreate} disabled={loading} className="w-full">
              <Plus className="h-4 w-4" />
              新建课程
            </Button>
          </CardBody>
        </Card>
        <div className="space-y-4">
          {courses.map((course) => {
            const courseStats = stats[course.id];
            const active = currentCourse?.id === course.id;
            return (
              <Card key={course.id} className={active ? "border-brand-200 bg-brand-50/50" : ""}>
                <CardBody>
                  <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                    <div>
                      <div className="mb-2 flex items-center gap-3">
                        <h2 className="text-xl font-bold text-slate-900">{course.name}</h2>
                        {active && <Badge>当前课程</Badge>}
                      </div>
                      <p className="text-sm leading-6 text-slate-500">{course.description || "暂无课程描述"}</p>
                      <p className="mt-2 text-xs text-slate-400">创建时间：{course.created_at || "-"}</p>
                    </div>
                    <Button variant={active ? "secondary" : "primary"} onClick={() => setCurrentCourse(course)}>
                      <CheckCircle className="h-4 w-4" />
                      {active ? "已选择" : "选择课程"}
                    </Button>
                  </div>
                  {courseStats && (
                    <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                      {statItems.map((item) => (
                        <div key={item.key} className="rounded-2xl border border-slate-100 bg-white p-4">
                          <item.icon className="mb-3 h-5 w-5 text-brand-600" />
                          <p className="text-2xl font-black text-slate-900">{courseStats[item.key]}</p>
                          <p className="text-xs text-slate-500">{item.label}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </CardBody>
              </Card>
            );
          })}
          {!courses.length && <Alert>暂无课程。请先创建一个课程，再上传资料并构建知识库。</Alert>}
        </div>
      </div>
    </PageContainer>
  );
}
