import { Workflow } from "lucide-react";
import { Card, CardBody } from "../ui/Card";

const steps = [
  "新建并选择课程",
  "上传 PDF、DOCX、PPTX 课程资料",
  "解析文本、切分 chunk，并写入当前课程独立知识库",
  "在当前课程知识库中检索相关资料，完成问答、出题和总结",
  "SQLite 保存课程、文件、chunk、问答历史和题目记录",
];

export function FlowCard() {
  return (
    <Card>
      <CardBody>
        <div className="mb-6 flex items-center gap-3">
          <Workflow className="h-7 w-7 text-brand-600" />
          <h2 className="text-xl font-bold text-slate-900">功能流程</h2>
        </div>
        <div className="space-y-5">
          {steps.map((step, index) => (
            <div key={step} className="flex items-start gap-4">
              <div className="relative flex flex-col items-center">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500 text-sm font-bold text-white">{index + 1}</span>
                {index < steps.length - 1 && <span className="mt-1 h-8 w-px bg-brand-100" />}
              </div>
              <p className="pt-1 text-sm leading-7 text-slate-700">{step}</p>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
