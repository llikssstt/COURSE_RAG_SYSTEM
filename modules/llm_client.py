from __future__ import annotations

import hashlib
import json
import sys
from typing import Any

import requests

from config import (
    CHAT_MODEL,
    BGE_LOCAL_MODEL_DIR,
    EMBEDDING_DIM,
    EMBEDDING_FALLBACK_TO_MOCK,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    MODEL_CACHE_DIR,
    MOCK_MODE,
    OPENAI_COMPATIBLE_API_KEY,
    OPENAI_COMPATIBLE_BASE_URL,
)


class EmbeddingClient:
    _sentence_model = None
    last_provider = "unknown"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        provider = EMBEDDING_PROVIDER.lower()
        if provider == "mock":
            EmbeddingClient.last_provider = "mock"
            return [self._mock_embed(text) for text in texts]
        if provider in {"bge", "sentence-transformers", "sentence_transformers", "local"}:
            return self._bge_embed(texts)
        if provider in {"openai", "openai-compatible", "api"}:
            return self._openai_compatible_embed(texts)
        return self._openai_compatible_embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def _mock_embed(self, text: str) -> list[float]:
        # Deterministic hashing embedding. It is enough for local demos and tests.
        vec = [0.0] * EMBEDDING_DIM
        tokens = [t for t in text.lower().replace("\n", " ").split(" ") if t]
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % EMBEDDING_DIM
            sign = 1.0 if int(digest[8:10], 16) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]

    def _openai_compatible_embed(self, texts: list[str]) -> list[list[float]]:
        if not OPENAI_COMPATIBLE_API_KEY:
            raise RuntimeError("未配置 OPENAI_COMPATIBLE_API_KEY，请开启 MOCK_MODE 或配置 API Key。")
        resp = requests.post(
            f"{OPENAI_COMPATIBLE_BASE_URL.rstrip('/')}/embeddings",
            headers={
                "Authorization": f"Bearer {OPENAI_COMPATIBLE_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"model": EMBEDDING_MODEL, "input": texts},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return [item["embedding"] for item in sorted(data, key=lambda x: x["index"])]

    def _bge_embed(self, texts: list[str]) -> list[list[float]]:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "缺少 sentence-transformers，无法加载 BGE。请运行 pip install -r requirements.txt，"
                "或设置 EMBEDDING_PROVIDER=mock。"
            ) from exc

        if EmbeddingClient._sentence_model is None:
            model_name_or_path = (
                str(BGE_LOCAL_MODEL_DIR)
                if (BGE_LOCAL_MODEL_DIR / "config.json").exists()
                else EMBEDDING_MODEL
            )
            try:
                EmbeddingClient._sentence_model = SentenceTransformer(
                    model_name_or_path,
                    cache_folder=str(MODEL_CACHE_DIR),
                )
            except Exception:
                if EMBEDDING_FALLBACK_TO_MOCK:
                    EmbeddingClient.last_provider = "mock_fallback"
                    return [self._mock_embed(text) for text in texts]
                raise

        embeddings = EmbeddingClient._sentence_model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        EmbeddingClient.last_provider = f"bge:{EMBEDDING_MODEL}"
        return embeddings.tolist()


class LLMClient:
    def _runtime_config(self, override: dict[str, str] | None = None) -> dict[str, str]:
        config = {
            "api_key": OPENAI_COMPATIBLE_API_KEY,
            "base_url": OPENAI_COMPATIBLE_BASE_URL,
            "model": CHAT_MODEL,
        }
        try:
            if "streamlit" not in sys.modules:
                raise RuntimeError("Streamlit is not loaded.")
            import streamlit as st
            from streamlit.runtime.scriptrunner import get_script_run_ctx

            if get_script_run_ctx() is not None:
                session_config = st.session_state.get("llm_config", {})
                config.update({k: v for k, v in session_config.items() if v})
        except Exception:
            pass
        if override:
            config.update({k: v for k, v in override.items() if v})
        return config

    def chat(self, prompt: str, config: dict[str, str] | None = None) -> str:
        if MOCK_MODE:
            return self._mock_chat(prompt)
        runtime = self._runtime_config(config)
        api_key = runtime["api_key"]
        base_url = runtime["base_url"].rstrip("/")
        model = runtime["model"]
        if not api_key:
            raise RuntimeError("请在侧边栏配置 OPENAI_COMPATIBLE_API_KEY，或设置 DEEPSEEK_API_KEY 环境变量。")
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "你是严谨的课程资料问答与出题助手。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=90,
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise RuntimeError(f"LLM API 请求失败：{resp.status_code} {resp.text[:500]}") from exc
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"LLM API 返回格式异常：{data}") from exc

    def _mock_chat(self, prompt: str) -> str:
        context = self._between(prompt, "【课程资料】", "【用户问题】") or self._between(
            prompt, "【课程资料】", "【生成要求】"
        )
        snippets = [line.strip() for line in context.splitlines() if line.strip()]
        basis = "\n".join(snippets[:8]) or "当前课程资料中未找到明确依据。"
        if "题型" in prompt and "题目数量" in prompt:
            return self._mock_questions(prompt, basis)
        if "复习提纲" in prompt or "易混淆" in prompt:
            return (
                "## 结构化复习提纲\n"
                f"1. 围绕资料中的核心概念复习：{basis[:180]}\n\n"
                "## 重点知识\n"
                "1. 优先掌握资料中反复出现的定义、流程、组成部分和对比关系。\n\n"
                "## 易混淆知识点\n"
                "1. 对名称相近、流程相似、适用条件不同的概念进行表格化对比。\n\n"
                "## 考前速记卡片\n"
                "1. 概念 - 定义 - 适用场景 - 常见考法。"
            )
        return (
            "## 简明答案\n"
            f"根据当前课程资料，相关依据主要是：{basis[:220]}\n\n"
            "## 详细解释\n"
            "以上回答由检索到的课程片段整理而来。若需要更精确的结论，请补充更完整的课程资料或缩小问题范围。\n\n"
            "## 参考来源\n"
            "见页面下方检索来源。"
        )

    def _mock_questions(self, prompt: str, basis: str) -> str:
        count = self._extract_int(prompt, "题目数量", default=3)
        qtype = self._extract_field(prompt, "题型", default="选择题")
        difficulty = self._extract_field(prompt, "难度", default="中等")
        items: list[dict[str, Any]] = []
        for idx in range(1, count + 1):
            content = f"根据课程资料，概括以下知识点的关键含义：{basis[:80]}（第 {idx} 题）"
            if qtype == "选择题":
                content += "\nA. 与资料核心概念一致\nB. 与资料无关\nC. 与资料相反\nD. 无法判断"
                answer = "A"
            elif qtype == "判断题":
                content = f"判断：课程资料认为该知识点需要结合上下文理解。"
                answer = "正确"
            elif qtype == "填空题":
                content = f"填空：该知识点的复习应基于课程资料中的____、流程和对比关系。"
                answer = "定义"
            else:
                answer = basis[:160]
            items.append(
                {
                    "question_content": content,
                    "answer": answer,
                    "analysis": f"本题为 mock 模式生成，难度为{difficulty}，依据检索到的课程资料片段。",
                    "knowledge_point": "课程资料核心知识点",
                    "sources": "见检索来源",
                }
            )
        return json.dumps(items, ensure_ascii=False, indent=2)

    @staticmethod
    def _between(text: str, start: str, end: str) -> str:
        if start not in text:
            return ""
        left = text.split(start, 1)[1]
        return left.split(end, 1)[0] if end in left else left

    @staticmethod
    def _extract_int(text: str, label: str, default: int) -> int:
        import re

        match = re.search(label + r"[:：]\s*(\d+)", text)
        return int(match.group(1)) if match else default

    @staticmethod
    def _extract_field(text: str, label: str, default: str) -> str:
        import re

        match = re.search(label + r"[:：]\s*([^\n]+)", text)
        return match.group(1).strip() if match else default
