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

            CREATE TABLE IF NOT EXISTS wrong_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                question_id INTEGER,
                source_type TEXT NOT NULL,
                question_type TEXT,
                difficulty TEXT,
                question_content TEXT NOT NULL,
                user_answer TEXT,
                correct_answer TEXT,
                analysis TEXT,
                knowledge_point TEXT,
                sources TEXT,
                note TEXT,
                status TEXT NOT NULL DEFAULT '未掌握',
                review_count INTEGER NOT NULL DEFAULT 0,
                last_reviewed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id),
                FOREIGN KEY(question_id) REFERENCES question_bank(id)
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


def get_qa_history_item(course_id: int, qa_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM qa_history WHERE course_id = ? AND id = ?",
            (course_id, qa_id),
        ).fetchone()
        return dict(row) if row else None


def search_qa_history(
    course_id: int,
    keyword: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM qa_history WHERE course_id = ?"
    params: list[Any] = [course_id]
    if keyword.strip():
        like = f"%{keyword.strip()}%"
        sql += " AND (question LIKE ? OR answer LIKE ?)"
        params.extend([like, like])
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_conn() as conn:
        return rows_to_dicts(conn.execute(sql, tuple(params)).fetchall())


def delete_qa_history_item(course_id: int, qa_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM qa_history WHERE course_id = ? AND id = ?",
            (course_id, qa_id),
        )
        return int(cur.rowcount)


def delete_qa_history_items(course_id: int, ids: list[int]) -> int:
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    with get_conn() as conn:
        cur = conn.execute(
            f"DELETE FROM qa_history WHERE course_id = ? AND id IN ({placeholders})",
            (course_id, *ids),
        )
        return int(cur.rowcount)


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


def get_question_record(course_id: int, question_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM question_bank WHERE course_id = ? AND id = ?",
            (course_id, question_id),
        ).fetchone()
        return dict(row) if row else None


def search_question_records(
    course_id: int,
    keyword: str = "",
    question_type: str = "",
    difficulty: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM question_bank WHERE course_id = ?"
    params: list[Any] = [course_id]
    if keyword.strip():
        like = f"%{keyword.strip()}%"
        sql += " AND (question_content LIKE ? OR knowledge_point LIKE ? OR answer LIKE ? OR analysis LIKE ?)"
        params.extend([like, like, like, like])
    if question_type.strip():
        sql += " AND question_type = ?"
        params.append(question_type.strip())
    if difficulty.strip():
        sql += " AND difficulty = ?"
        params.append(difficulty.strip())
    sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_conn() as conn:
        return rows_to_dicts(conn.execute(sql, tuple(params)).fetchall())


def delete_question_record(course_id: int, question_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM question_bank WHERE course_id = ? AND id = ?",
            (course_id, question_id),
        )
        return int(cur.rowcount)


def delete_question_records(course_id: int, ids: list[int]) -> int:
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    with get_conn() as conn:
        cur = conn.execute(
            f"DELETE FROM question_bank WHERE course_id = ? AND id IN ({placeholders})",
            (course_id, *ids),
        )
        return int(cur.rowcount)


def _serialize_sources(sources: Any) -> str:
    if sources is None:
        return "[]"
    if isinstance(sources, str):
        return sources
    return json.dumps(sources, ensure_ascii=False)


def add_wrong_question(
    course_id: int,
    question_id: int | None,
    source_type: str,
    question_type: str = "",
    difficulty: str = "",
    question_content: str = "",
    user_answer: str = "",
    correct_answer: str = "",
    analysis: str = "",
    knowledge_point: str = "",
    sources: Any = None,
    note: str = "",
) -> int:
    timestamp = now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO wrong_questions(
                course_id, question_id, source_type, question_type, difficulty,
                question_content, user_answer, correct_answer, analysis,
                knowledge_point, sources, note, status, review_count,
                last_reviewed_at, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                course_id,
                question_id,
                source_type,
                question_type,
                difficulty,
                question_content,
                user_answer,
                correct_answer,
                analysis,
                knowledge_point,
                _serialize_sources(sources),
                note,
                "未掌握",
                0,
                None,
                timestamp,
                timestamp,
            ),
        )
        return int(cur.lastrowid)


def list_wrong_questions(
    course_id: int,
    keyword: str = "",
    status: str = "",
    knowledge_point: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM wrong_questions WHERE course_id = ?"
    params: list[Any] = [course_id]
    if keyword.strip():
        like = f"%{keyword.strip()}%"
        sql += " AND (question_content LIKE ? OR correct_answer LIKE ? OR analysis LIKE ? OR note LIKE ? OR knowledge_point LIKE ?)"
        params.extend([like, like, like, like, like])
    if status.strip():
        sql += " AND status = ?"
        params.append(status.strip())
    if knowledge_point.strip():
        sql += " AND knowledge_point LIKE ?"
        params.append(f"%{knowledge_point.strip()}%")
    sql += " ORDER BY updated_at DESC, created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    with get_conn() as conn:
        return rows_to_dicts(conn.execute(sql, tuple(params)).fetchall())


def get_wrong_question(course_id: int, wrong_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM wrong_questions WHERE course_id = ? AND id = ?",
            (course_id, wrong_id),
        ).fetchone()
        return dict(row) if row else None


def update_wrong_question(
    course_id: int,
    wrong_id: int,
    note: str | None = None,
    status: str | None = None,
    user_answer: str | None = None,
) -> int:
    updates = []
    params: list[Any] = []
    if note is not None:
        updates.append("note = ?")
        params.append(note)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    if user_answer is not None:
        updates.append("user_answer = ?")
        params.append(user_answer)
    if not updates:
        return 0
    updates.append("updated_at = ?")
    params.append(now())
    params.extend([course_id, wrong_id])
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE wrong_questions SET {', '.join(updates)} WHERE course_id = ? AND id = ?",
            tuple(params),
        )
        return int(cur.rowcount)


def delete_wrong_question(course_id: int, wrong_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM wrong_questions WHERE course_id = ? AND id = ?",
            (course_id, wrong_id),
        )
        return int(cur.rowcount)


def delete_wrong_questions(course_id: int, ids: list[int]) -> int:
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    with get_conn() as conn:
        cur = conn.execute(
            f"DELETE FROM wrong_questions WHERE course_id = ? AND id IN ({placeholders})",
            (course_id, *ids),
        )
        return int(cur.rowcount)


def mark_wrong_question_reviewed(course_id: int, wrong_id: int) -> int:
    timestamp = now()
    with get_conn() as conn:
        cur = conn.execute(
            """
            UPDATE wrong_questions
            SET review_count = review_count + 1,
                last_reviewed_at = ?,
                updated_at = ?
            WHERE course_id = ? AND id = ?
            """,
            (timestamp, timestamp, course_id, wrong_id),
        )
        return int(cur.rowcount)


def count_wrong_questions(course_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count FROM wrong_questions WHERE course_id = ?",
            (course_id,),
        ).fetchone()
        return int(row["count"])
