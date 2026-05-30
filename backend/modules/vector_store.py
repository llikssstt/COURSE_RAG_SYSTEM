from typing import Any
import math
import re

import chromadb
from chromadb.config import Settings

from config import CHROMA_DIR
from modules.llm_client import EmbeddingClient


def _tokenize(text: str) -> list[str]:
    text = (text or "").lower()
    words = re.findall(r"[a-zA-Z0-9_]+", text)
    chinese = re.findall(r"[\u4e00-\u9fff]", text)
    bigrams = [text[i : i + 2] for i in range(len(text) - 1) if re.match(r"[\u4e00-\u9fff]{2}", text[i : i + 2])]
    return words + chinese + bigrams


def _rrf_fuse(ranked_lists: list[list[dict[str, Any]]], top_k: int, k: int = 60) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            item_id = item["id"]
            if item_id not in fused:
                fused[item_id] = dict(item)
                fused[item_id]["rrf_score"] = 0.0
                fused[item_id]["rank_sources"] = []
            fused[item_id]["rrf_score"] += 1.0 / (k + rank)
            fused[item_id]["rank_sources"].append(item.get("retrieval_type", "unknown"))
    return sorted(fused.values(), key=lambda x: x["rrf_score"], reverse=True)[:top_k]


class CourseVectorStore:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.embedder = EmbeddingClient()

    @staticmethod
    def collection_name(course_id: int) -> str:
        return f"course_{course_id}"

    def get_collection(self, course_id: int):
        return self.client.get_or_create_collection(
            name=self.collection_name(course_id),
            metadata={"hnsw:space": "cosine"},
        )

    def reset_course_collection(self, course_id: int):
        name = self.collection_name(course_id)
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
        return self.get_collection(course_id)

    def delete_document_vectors(self, course_id: int, document_id: int) -> None:
        collection = self.get_collection(course_id)
        try:
            collection.delete(where={"document_id": int(document_id)})
        except Exception:
            # Chroma raises when no ids match in some versions; this is harmless.
            pass

    def add_chunks(self, course_id: int, chunks: list[dict[str, Any]]) -> list[str]:
        if not chunks:
            return []
        collection = self.get_collection(course_id)
        texts = [chunk["chunk_text"] for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)
        ids = [
            f"course_{course_id}_doc_{chunk['document_id']}_chunk_{idx}"
            for idx, chunk in enumerate(chunks, start=1)
        ]
        metadatas = []
        for chunk in chunks:
            metadatas.append(
                {
                    "course_id": int(course_id),
                    "document_id": int(chunk["document_id"]),
                    "source_file": chunk.get("source_file") or "",
                    "page_number": chunk.get("page_number") or 0,
                    "slide_number": chunk.get("slide_number") or 0,
                    "section_title": chunk.get("section_title") or "",
                    "chunk_index": chunk.get("chunk_index") or 0,
                    "chunk_size": chunk.get("chunk_size") or len(chunk["chunk_text"]),
                }
            )
        try:
            collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        except Exception as exc:
            if "dimension" in str(exc).lower():
                raise RuntimeError(
                    "当前课程的 Chroma collection 维度与当前 embedding 模型不一致。"
                    "请在资料上传页点击“构建或更新当前课程知识库”完整重建。"
                ) from exc
            raise
        return ids

    def vector_search(self, course_id: int, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        collection = self.get_collection(course_id)
        if collection.count() == 0:
            return []
        try:
            result = collection.query(
                query_embeddings=[self.embedder.embed_query(query)],
                n_results=max(1, top_k),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            if "dimension" in str(exc).lower():
                raise RuntimeError(
                    "当前课程知识库仍是旧 embedding 维度。请到资料上传页重新构建当前课程知识库。"
                ) from exc
            raise
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        ids = result.get("ids", [[]])[0]
        items = []
        for item_id, text, meta, distance in zip(ids, docs, metas, distances):
            items.append(
                {
                    "id": item_id,
                    "chunk_text": text,
                    "metadata": meta,
                    "distance": distance,
                    "retrieval_type": "vector",
                }
            )
        return items

    def bm25_search(self, course_id: int, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        collection = self.get_collection(course_id)
        if collection.count() == 0:
            return []

        data = collection.get(include=["documents", "metadatas"])
        ids = data.get("ids", [])
        docs = data.get("documents", [])
        metas = data.get("metadatas", [])
        tokenized_docs = [_tokenize(doc) for doc in docs]
        query_terms = _tokenize(query)
        if not query_terms:
            return []

        doc_count = len(tokenized_docs)
        avgdl = sum(len(tokens) for tokens in tokenized_docs) / max(doc_count, 1)
        df: dict[str, int] = {}
        for tokens in tokenized_docs:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1

        k1 = 1.5
        b = 0.75
        scored = []
        for item_id, doc, meta, tokens in zip(ids, docs, metas, tokenized_docs):
            term_freq: dict[str, int] = {}
            for token in tokens:
                term_freq[token] = term_freq.get(token, 0) + 1
            score = 0.0
            doc_len = len(tokens) or 1
            for term in query_terms:
                if term not in term_freq:
                    continue
                idf = math.log(1 + (doc_count - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5))
                tf = term_freq[term]
                score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_len / max(avgdl, 1)))
            if score > 0:
                scored.append(
                    {
                        "id": item_id,
                        "chunk_text": doc,
                        "metadata": meta,
                        "bm25_score": score,
                        "retrieval_type": "bm25",
                    }
                )
        return sorted(scored, key=lambda x: x["bm25_score"], reverse=True)[:top_k]

    def hybrid_search(self, course_id: int, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        candidate_k = max(top_k * 4, 10)
        vector_results = self.vector_search(course_id, query, candidate_k)
        bm25_results = self.bm25_search(course_id, query, candidate_k)
        return _rrf_fuse([vector_results, bm25_results], top_k=top_k)

    def search(self, course_id: int, query: str, top_k: int = 5, mode: str = "hybrid") -> list[dict[str, Any]]:
        if mode == "vector":
            return self.vector_search(course_id, query, top_k)
        if mode == "bm25":
            return self.bm25_search(course_id, query, top_k)
        return self.hybrid_search(course_id, query, top_k)
