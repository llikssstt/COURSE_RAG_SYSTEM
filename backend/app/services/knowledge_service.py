from modules import db
from modules.document_parser import parse_document
from modules.text_splitter import split_parsed_items
from modules.vector_store import CourseVectorStore
from app.services.course_service import ensure_course


def _build_document(course_id: int, document: dict) -> int:
    parsed = parse_document(document["file_path"])
    chunks = split_parsed_items(parsed)
    for chunk in chunks:
        chunk["course_id"] = course_id
        chunk["document_id"] = document["id"]

    vector_ids = CourseVectorStore().add_chunks(course_id, chunks)
    for chunk, vector_id in zip(chunks, vector_ids):
        db.add_chunk(
            course_id=course_id,
            document_id=document["id"],
            chunk_text=chunk["chunk_text"],
            source_file=chunk["source_file"],
            page_number=chunk.get("page_number"),
            slide_number=chunk.get("slide_number"),
            section_title=chunk.get("section_title"),
            vector_id=vector_id,
        )
    db.update_document_status(document["id"], f"parsed: {len(chunks)} chunks")
    return len(chunks)


def rebuild_course_knowledge_base(course_id: int) -> dict:
    ensure_course(course_id)
    documents = db.list_documents(course_id)
    store = CourseVectorStore()
    store.reset_course_collection(course_id)
    db.delete_course_chunks(course_id)

    total_chunks = 0
    failures = []
    for document in documents:
        try:
            total_chunks += _build_document(course_id, document)
        except Exception as exc:
            db.update_document_status(document["id"], f"failed: {exc}")
            failures.append({"file_name": document["file_name"], "error": str(exc)})

    return {
        "course_id": course_id,
        "total_chunks": total_chunks,
        "failures": failures,
        "message": "知识库更新完成" if not failures else "知识库更新完成，部分文件解析失败",
    }
