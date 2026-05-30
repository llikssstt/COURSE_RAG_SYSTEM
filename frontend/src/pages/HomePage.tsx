import { useState } from "react";
import { BarChart3, BookOpen, CheckCircle, FileQuestion, HelpCircle, MessageCircle, Settings, Upload } from "lucide-react";
import { FeatureCard } from "../components/cards/FeatureCard";
import { HeroCard } from "../components/cards/HeroCard";
import { FlowCard } from "../components/cards/FlowCard";
import { CurrentCourseCard } from "../components/cards/CurrentCourseCard";
import { PageContainer } from "../components/layout/PageContainer";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card, CardBody } from "../components/ui/Card";
import { Field, Input } from "../components/ui/Form";
import { defaultLLMConfig, useAppStore } from "../store/useAppStore";

const features = [
  { title: "课程管理", description: "新建、查看或切换课程，管理课程基本信息", icon: BookOpen, to: "/courses" },
  { title: "资料上传", description: "上传 PDF、DOCX、PPTX 等课程资料", icon: Upload, to: "/upload" },
  { title: "智能问答", description: "基于课程知识库进行智能问答", icon: MessageCircle, to: "/qa" },
  { title: "自动出题", description: "基于课程资料自动生成练习题", icon: FileQuestion, to: "/questions" },
  { title: "复习总结", description: "生成课程复习总结，梳理重点知识", icon: BarChart3, to: "/summary" },
];

export function HomePage() {
  const llmConfig = useAppStore((state) => state.llmConfig);
  const setLLMConfig = useAppStore((state) => state.setLLMConfig);
  const [draft, setDraft] = useState(llmConfig || defaultLLMConfig);
  const [saved, setSaved] = useState(false);

  return (
    <PageContainer>
      <div className="space-y-8">
        <HeroCard />
        <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </section>
        <section className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <FlowCard />
          <Card>
            <CardBody>
              <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Settings className="h-7 w-7 text-brand-600" />
                  <h2 className="text-xl font-bold text-slate-900">LLM API 配置</h2>
                </div>
                <HelpCircle className="h-5 w-5 text-slate-400" />
              </div>
              <div className="space-y-4">
                <Field label="OPENAI_COMPATIBLE_API_KEY">
                  <Input
                    type="password"
                    value={draft.api_key}
                    placeholder="请输入 DeepSeek 或 OpenAI-compatible API Key"
                    onChange={(event) => setDraft({ ...draft, api_key: event.target.value })}
                  />
                </Field>
                <Field label="OPENAI_COMPATIBLE_BASE_URL">
                  <Input value={draft.base_url} onChange={(event) => setDraft({ ...draft, base_url: event.target.value })} />
                </Field>
                <Field label="CHAT_MODEL">
                  <Input value={draft.model} onChange={(event) => setDraft({ ...draft, model: event.target.value })} />
                </Field>
                <Button
                  onClick={() => {
                    setLLMConfig(draft);
                    setSaved(true);
                  }}
                  className="w-full"
                >
                  <CheckCircle className="h-4 w-4" />
                  保存到当前浏览器
                </Button>
                <p className="text-sm text-slate-500">
                  {draft.api_key ? "API Key 已配置，仅保存在当前浏览器。" : "API Key 未配置，问答、出题和总结会由后端返回明确提示。"}
                </p>
                {saved && <Alert tone="success">配置已保存到 localStorage，后续请求会随请求体发送给后端。</Alert>}
              </div>
            </CardBody>
          </Card>
        </section>
        <section className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
          <CurrentCourseCard />
          <Alert>默认使用 DeepSeek-compatible API。请先配置 API Key 后进行问答、出题和总结。</Alert>
        </section>
      </div>
    </PageContainer>
  );
}
