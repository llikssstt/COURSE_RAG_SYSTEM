export function HeroCard() {
  return (
    <section className="relative overflow-hidden rounded-card border border-slate-200 bg-gradient-to-br from-white via-white to-brand-50 p-8 shadow-sm md:p-12">
      <div className="relative z-10 max-w-3xl">
        <h1 className="text-3xl font-black leading-tight text-slate-900 md:text-4xl">基于 RAG 的多课程资料智能问答与习题生成系统</h1>
        <p className="mt-6 text-base leading-8 text-slate-600 md:text-lg">
          面向期末复习场景，系统为每门课程建立独立知识库，支持课程资料上传、基于资料的智能问答、自动生成习题和复习总结。
        </p>
      </div>
      <div className="pointer-events-none absolute right-16 top-10 hidden h-44 w-52 rotate-[-12deg] rounded-[28px] bg-brand-200/70 shadow-lg md:block" />
      <div className="pointer-events-none absolute right-24 top-20 hidden h-44 w-52 rotate-[-12deg] rounded-[28px] bg-brand-100/75 shadow-sm md:block" />
      <div className="pointer-events-none absolute right-32 top-32 hidden h-44 w-52 rotate-[-12deg] rounded-[28px] bg-white/60 shadow-sm md:block" />
    </section>
  );
}
