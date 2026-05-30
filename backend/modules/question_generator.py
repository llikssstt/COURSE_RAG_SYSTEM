from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules import db
from modules.llm_client import LLMClient
from modules.rag_qa import format_sources
from modules.vector_store import CourseVectorStore


PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "question_prompt.txt"


def _parse_questions(raw: str) -> list[dict[str, Any]]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "questions" in data:
            data = data["questions"]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass
    return [
        {
            "question_content": raw,
            "answer": "",
            "analysis": "模型未返回标准 JSON，已保存原始内容，请调整提示词或重新生成。",
            "knowledge_point": "",
            "sources": "",
            "parse_error": True,
        }
    ]


def _format_question_for_storage(item: dict[str, Any]) -> str:
    content = str(item.get("question_content", "")).strip()
    options = item.get("options")
    if isinstance(options, dict):
        option_text = "\n".join(f"{key}. {value}" for key, value in options.items())
    elif isinstance(options, list):
        option_text = "\n".join(str(option) for option in options)
    else:
        option_text = ""
    return f"{content}\n{option_text}".strip()


def generate_questions(
    course_id: int,
    scope: str,
    question_type: str,
    difficulty: str,
    count: int,
    with_answer: bool,
    top_k: int = 8,
    llm_config: dict[str, str] | None = None,
) -> dict[str, Any]:
    if db.count_chunks(course_id) == 0:
        raise RuntimeError("当前课程知识库为空，请先上传资料并构建知识库。")
    query = scope.strip() or question_type
    store = CourseVectorStore()
    results = store.search(course_id, query, top_k)
    if not results:
        raise RuntimeError("当前课程资料中未找到可用于出题的依据。")

    context = "\n\n".join(
        f"[来源：{r['metadata'].get('source_file')} "
        f"页码：{r['metadata'].get('page_number') or '-'} "
        f"幻灯片：{r['metadata'].get('slide_number') or '-'}]\n{r['chunk_text']}"
        for r in results
    )
    prompt = PROMPT_PATH.read_text(encoding="utf-8").format(
        context=context,
        scope=scope or "不限，基于检索到的资料",
        question_type=question_type,
        difficulty=difficulty,
        count=count,
        with_answer="是" if with_answer else "否",
    )
    raw = LLMClient().chat(prompt, llm_config)
    questions = _parse_questions(raw)
    common_sources = format_sources(results)
    for item in questions:
        db.add_question_record(
            course_id=course_id,
            question_type=question_type,
            difficulty=difficulty,
            question_content=_format_question_for_storage(item),
            answer=str(item.get("answer", "")) if with_answer else "",
            analysis=str(item.get("analysis", "")) if with_answer else "",
            knowledge_point=str(item.get("knowledge_point", "")),
            sources=common_sources,
        )
    return {"questions": questions, "sources": common_sources, "raw": raw}
