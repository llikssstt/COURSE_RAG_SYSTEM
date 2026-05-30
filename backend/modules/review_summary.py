from __future__ import annotations

from pathlib import Path
from typing import Any

from modules import db
from modules.llm_client import LLMClient
from modules.vector_store import CourseVectorStore


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "summary_prompt.txt"


def generate_summary(
    course_id: int,
    summary_type: str,
    scope: str = "",
    top_k: int = 12,
    llm_config: dict[str, str] | None = None,
) -> dict[str, Any]:
    if db.count_chunks(course_id) == 0:
        raise RuntimeError("当前课程知识库为空，请先上传资料并构建知识库。")
    query = scope.strip() or summary_type
    results = CourseVectorStore().search(course_id, query, top_k)
    if not results:
        raise RuntimeError("当前课程资料中未找到可用于总结的依据。")
    context = "\n\n".join(
        f"[来源：{r['metadata'].get('source_file')} "
        f"页码：{r['metadata'].get('page_number') or '-'} "
        f"幻灯片：{r['metadata'].get('slide_number') or '-'}]\n{r['chunk_text']}"
        for r in results
    )
    prompt = PROMPT_PATH.read_text(encoding="utf-8").format(
        context=context,
        summary_type=summary_type,
        scope=scope or "全课程资料",
    )
    return {"summary": LLMClient().chat(prompt, llm_config), "contexts": results}
