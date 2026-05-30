from __future__ import annotations

from pathlib import Path
from typing import Any

from modules import db
from modules.llm_client import LLMClient
from modules.vector_store import CourseVectorStore


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "qa_prompt.txt"


def route_query(question: str) -> str:
    detail_keywords = ["区别", "比较", "为什么", "如何", "过程", "原理", "解释", "分析"]
    list_keywords = ["列出", "有哪些", "总结", "提纲", "要点"]
    if any(keyword in question for keyword in list_keywords):
        return "list"
    if any(keyword in question for keyword in detail_keywords):
        return "detail"
    return "general"


def rewrite_query(question: str) -> str:
    cleaned = question.strip()
    suffix_terms = ["定义", "特点", "区别", "联系", "原理", "应用场景"]
    if any(term in cleaned for term in suffix_terms):
        return cleaned
    return f"{cleaned} 定义 特点 原理"


def format_sources(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = []
    seen = set()
    for item in results:
        meta = item["metadata"]
        source = {
            "source_file": meta.get("source_file", ""),
            "page_number": meta.get("page_number") or None,
            "slide_number": meta.get("slide_number") or None,
            "section_title": meta.get("section_title", ""),
        }
        key = tuple(source.items())
        if key not in seen:
            sources.append(source)
            seen.add(key)
    return sources


def ask_course(
    course_id: int,
    question: str,
    top_k: int = 5,
    llm_config: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not question.strip():
        raise ValueError("请输入问题。")
    if db.count_chunks(course_id) == 0:
        raise RuntimeError("当前课程知识库为空，请先上传资料并构建知识库。")

    store = CourseVectorStore()
    route_type = route_query(question)
    retrieval_query = question if route_type == "list" else rewrite_query(question)
    results = store.search(course_id, retrieval_query, top_k, mode="hybrid")
    if not results:
        answer = "当前课程资料中未找到明确依据。"
        sources: list[dict[str, Any]] = []
    else:
        context = "\n\n".join(
            f"[来源：{r['metadata'].get('source_file')} "
            f"页码：{r['metadata'].get('page_number') or '-'} "
            f"幻灯片：{r['metadata'].get('slide_number') or '-'}]\n{r['chunk_text']}"
            for r in results
        )
        prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
        prompt = prompt_template.format(context=context, question=question)
        answer = LLMClient().chat(prompt, llm_config)
        sources = format_sources(results)
    db.add_qa_history(course_id, question, answer, sources)
    return {
        "answer": answer,
        "sources": sources,
        "contexts": results,
        "route_type": route_type,
        "retrieval_query": retrieval_query,
        "retrieval_mode": "hybrid_rrf",
    }
