import { useEffect, useState } from "react";
import { Database, FileUp, RefreshCcw, Upload } from "lucide-react";
import { getErrorMessage } from "../api/client";
import { listDocuments, rebuildKnowledgeBase, uploadDocuments } from "../api/documents";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardBody, CardHeader } from "../components/ui/Card";
import { EmptyCourseNotice } from "../components/ui/EmptyCourseNotice";
import { useAppStore } from "../store/useAppStore";
import type { DocumentRecord } from "../types";

export function UploadPage() {
  const currentCourse = useAppStore((state) => state.currentCourse);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [files, setFiles] = useState<FileList | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [building, setBuilding] = useState(false);

  async function refresh() {
    if (!currentCourse) return;
    try {
      setDocuments(await listDocuments(currentCourse.id));
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

  async function handleUpload() {
    if (!currentCourse) return;
    if (!files?.length) {
      setError("请选择 PDF、DOCX 或 PPTX 文件。");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const results = await uploadDocuments(currentCourse.id, files);
      const failed = results.filter((item) => item.status !== "uploaded");
      setMessage(failed.length ? `上传完成，${failed.length} 个文件失败。` : "上传完成。");
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  async function handleBuild() {
    if (!currentCourse) return;
    try {
      setBuilding(true);
      setError("");
      const result = await rebuildKnowledgeBase(currentCourse.id);
      setMessage(`${result.message}，共生成 ${result.total_chunks} 个 chunk。`);
      if (result.failures?.length) {
        setError(result.failures.map((item) => `${item.file_name}: ${item.error}`).join("\n"));
      }
      await refresh();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBuilding(false);
    }
  }

  return (
    <PageContainer>
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <h1 className="text-2xl font-black text-slate-900">资料上传</h1>
            <p className="mt-2 text-sm text-slate-500">当前课程：{currentCourse.name}</p>
          </CardHeader>
          <CardBody className="space-y-5">
            {message && <Alert tone="success">{message}</Alert>}
            {error && <Alert tone="error"><pre className="whitespace-pre-wrap font-sans">{error}</pre></Alert>}
            <div className="rounded-card border border-dashed border-brand-200 bg-brand-50/40 p-8 text-center">
              <FileUp className="mx-auto mb-4 h-10 w-10 text-brand-600" />
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.pptx"
                onChange={(event) => setFiles(event.target.files)}
                className="mx-auto block max-w-md rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm"
              />
              <p className="mt-3 text-sm text-slate-500">支持多文件上传，文件会保存到 data/uploads/course_{currentCourse.id}/。</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={handleUpload} disabled={loading}>
                <Upload className="h-4 w-4" />
                {loading ? "上传中..." : "上传资料"}
              </Button>
              <Button onClick={handleBuild} disabled={building || documents.length === 0} variant="secondary">
                <RefreshCcw className={`h-4 w-4 ${building ? "animate-spin" : ""}`} />
                {building ? "构建中..." : "构建或更新当前课程知识库"}
              </Button>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5 text-brand-600" />
              <h2 className="text-xl font-bold text-slate-900">已上传资料</h2>
            </div>
          </CardHeader>
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="text-xs uppercase text-slate-500">
                  <tr>
                    <th className="border-b border-slate-100 py-3">文件名</th>
                    <th className="border-b border-slate-100 py-3">类型</th>
                    <th className="border-b border-slate-100 py-3">状态</th>
                    <th className="border-b border-slate-100 py-3">上传时间</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id}>
                      <td className="border-b border-slate-100 py-4 font-semibold text-slate-900">{doc.file_name}</td>
                      <td className="border-b border-slate-100 py-4">{doc.file_type}</td>
                      <td className="border-b border-slate-100 py-4">
                        <Badge tone={doc.parse_status.startsWith("failed") ? "amber" : "green"}>{doc.parse_status}</Badge>
                      </td>
                      <td className="border-b border-slate-100 py-4 text-slate-500">{doc.upload_time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {!documents.length && <p className="py-8 text-center text-sm text-slate-500">当前课程还没有上传资料。</p>}
          </CardBody>
        </Card>
      </div>
    </PageContainer>
  );
}
