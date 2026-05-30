import re
from typing import Any

from config import CHUNK_OVERLAP, CHUNK_SIZE

SEPARATORS = ["\n\n", "\n", "。", "；", "，", " ", ""]
MIN_CHUNK_LEN = 20


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text or "").strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", "", text)
    return text.strip()


def _merge_splits(parts: list[str], separator: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for part in parts:
        if not part:
            continue
        piece_len = len(part) + (len(separator) if current else 0)
        if current and current_len + piece_len > chunk_size:
            merged = separator.join(current).strip()
            if len(merged) >= MIN_CHUNK_LEN:
                chunks.append(merged)

            if overlap > 0:
                overlap_text = merged[-overlap:]
                current = [overlap_text] if overlap_text else []
                current_len = len(overlap_text)
            else:
                current = []
                current_len = 0

        current.append(part)
        current_len += piece_len

    if current:
        merged = separator.join(current).strip()
        if len(merged) >= MIN_CHUNK_LEN:
            chunks.append(merged)
    return chunks


def _recursive_split(text: str, separators: list[str], chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if len(text) >= MIN_CHUNK_LEN else []

    separator = separators[-1]
    rest = []
    for candidate in separators:
        if candidate == "" or candidate in text:
            separator = candidate
            rest = separators[separators.index(candidate) + 1 :]
            break

    if separator == "":
        parts = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]
    else:
        parts = text.split(separator)

    good_parts: list[str] = []
    chunks: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= chunk_size:
            good_parts.append(part)
        else:
            if good_parts:
                chunks.extend(_merge_splits(good_parts, separator, chunk_size, overlap))
                good_parts = []
            chunks.extend(_recursive_split(part, rest or [""], chunk_size, overlap))

    if good_parts:
        chunks.extend(_merge_splits(good_parts, separator, chunk_size, overlap))
    return chunks


def split_one(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = clean_text(text)
    if len(text) < MIN_CHUNK_LEN:
        return []
    return _recursive_split(text, SEPARATORS, chunk_size, overlap)


def split_parsed_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks = []
    for item in items:
        for idx, text in enumerate(split_one(item["text"]), start=1):
            chunk = dict(item)
            chunk["chunk_text"] = text
            chunk["chunk_index"] = idx
            chunk["chunk_size"] = len(text)
            chunk.pop("text", None)
            chunks.append(chunk)
    return chunks
