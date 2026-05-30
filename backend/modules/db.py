from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from config import DB_PATH


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                parse_status TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                source_file TEXT NOT NULL,
                page_number INTEGER,
                slide_number INTEGER,
                section_title TEXT,
                vector_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id),
                FOREIGN KEY(document_id) REFERENCES documents(id)
            );

            CREATE TABLE IF NOT EXISTS qa_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );

            CREATE TABLE IF NOT EXISTS question_bank (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                question_type TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question_content TEXT NOT NULL,
                answer TEXT,
                analysis TEXT,
                knowledge_point TEXT,
                sources TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );
            """
        )


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def create_course(name: str, description: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO courses(name, description, created_at) VALUES (?, ?, ?)",
            (name.strip(), description.strip(), now()),
        )
        return int(cur.lastrowid)


def list_courses() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM courses ORDER BY created_at DESC").fetchall()
        return rows_to_dicts(rows)


def get_course(course_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
        return dict(row) if row else None


def add_document(course_id: int, file_name: str, file_type: str, file_path: Path) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO documents(course_id, file_name, file_type, file_path, upload_time, parse_status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (course_id, file_name, file_type, str(file_path), now(), "uploaded"),
        )
        return int(cur.lastrowid)


def update_document_status(document_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE documents SET parse_status = ? WHERE id = ?", (status, document_id)
        )


def list_documents(course_id: int) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM documents WHERE course_id = ? ORDER BY upload_time DESC",
            (course_id,),
        ).fetchall()
        return rows_to_dicts(rows)


def get_document(document_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (document_id,)).fetchone()
        return dict(row) if row else None


def delete_document_chunks(document_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))


def delete_course_chunks(course_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM chunks WHERE course_id = ?", (course_id,))


def add_chunk(
    course_id: int,
    document_id: int,
    chunk_text: str,
    source_file: str,
    page_number: int | None,
    slide_number: int | None,
    section_title: str | None,
    vector_id: str,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO chunks(
                course_id, document_id, chunk_text, source_file, page_number,
                slide_number, section_title, vector_id, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
                document_id,
                chunk_text,
                source_file,
                page_number,
                slide_number,
                section_title,
                vector_id,
                now(),
            ),
        )
        return int(cur.lastrowid)


def list_chunks(course_id: int, limit: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM chunks WHERE course_id = ? ORDER BY id DESC"
    params: tuple[Any, ...] = (course_id,)
    if limit:
        sql += " LIMIT ?"
        params = (course_id, limit)
    with get_conn() as conn:
        return rows_to_dicts(conn.execute(sql, params).fetchall())


def count_chunks(course_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM chunks WHERE course_id = ?", (course_id,)
        ).fetchone()
        return int(row["count"])


def count_documents(course_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM documents WHERE course_id = ?", (course_id,)
        ).fetchone()
        return int(row["count"])


def count_qa_history(course_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM qa_history WHERE course_id = ?", (course_id,)
        ).fetchone()
        return int(row["count"])


def count_question_records(course_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM question_bank WHERE course_id = ?", (course_id,)
        ).fetchone()
        return int(row["count"])


def add_qa_history(course_id: int, question: str, answer: str, sources: list[dict[str, Any]]) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO qa_history(course_id, question, answer, sources, created_at) VALUES (?, ?, ?, ?, ?)",
            (course_id, question, answer, json.dumps(sources, ensure_ascii=False), now()),
        )


def list_qa_history(course_id: int, limit: int = 20) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM qa_history WHERE course_id = ? ORDER BY created_at DESC LIMIT ?",
            (course_id, limit),
        ).fetchall()
        return rows_to_dicts(rows)


def add_question_record(
    course_id: int,
    question_type: str,
    difficulty: str,
    question_content: str,
    answer: str,
    analysis: str,
    knowledge_point: str,
    sources: list[dict[str, Any]],
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO question_bank(
                course_id, question_type, difficulty, question_content, answer,
                analysis, knowledge_point, sources, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
                question_type,
                difficulty,
                question_content,
                answer,
                analysis,
                knowledge_point,
                json.dumps(sources, ensure_ascii=False),
                now(),
            ),
        )


def list_question_records(course_id: int, limit: int = 30) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM question_bank WHERE course_id = ? ORDER BY created_at DESC LIMIT ?",
            (course_id, limit),
        ).fetchall()
        return rows_to_dicts(rows)
