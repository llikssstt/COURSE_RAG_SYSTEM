import { Link } from "react-router-dom";
import { BookOpen } from "lucide-react";
import { Button } from "./Button";
import { Card, CardBody } from "./Card";

export function EmptyCourseNotice() {
  return (
    <Card>
      <CardBody className="flex flex-col items-center justify-center gap-4 py-16 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-brand-600">
          <BookOpen className="h-7 w-7" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900">请先在课程管理页面选择当前课程。</h2>
          <p className="mt-2 text-sm text-slate-500">资料上传、智能问答、自动出题和复习总结都基于当前课程的独立知识库。</p>
        </div>
        <Link to="/courses">
          <Button>前往课程管理</Button>
        </Link>
      </CardBody>
    </Card>
  );
}
