from pathlib import Path

import streamlit as st

from config import CHAT_MODEL, OPENAI_COMPATIBLE_API_KEY, OPENAI_COMPATIBLE_BASE_URL, UPLOAD_DIR
from modules import db
from modules.document_parser import parse_document
from modules.question_generator import generate_questions
from modules.rag_qa import ask_course
from modules.review_summary import generate_summary
from modules.text_splitter import split_parsed_items
from modules.vector_store import CourseVectorStore


st.set_page_config(page_title="多课程 RAG 智能复习系统", layout="wide")
db.init_db()


def init_llm_config() -> None:
    if "llm_config" not in st.session_state:
        st.session_state.llm_config = {
            "api_key": OPENAI_COMPATIBLE_API_KEY,
            "base_url": OPENAI_COMPATIBLE_BASE_URL,
            "model": CHAT_MODEL,
        }


init_llm_config()


def get_current_course():
    course_id = st.session_state.get("current_course_id")
    return db.get_course(course_id) if course_id else None


def require_course():
    course = get_current_course()
    if not course:
        st.warning("请先在“课程管理”页面选择当前课程。")
        return None
    return course


def source_label(source: dict) -> str:
    position = []
    if source.get("page_number"):
        position.append(f"第 {source['page_number']} 页")
    if source.get("slide_number"):
        position.append(f"第 {source['slide_number']} 张幻灯片")
    if source.get("section_title"):
        position.append(str(source["section_title"]))
    suffix = " / ".join(position) if position else "位置未标注"
    return f"{source.get('source_file', '')} - {suffix}"


def normalize_options(options) -> list[tuple[str, str]]:
    if isinstance(options, dict):
        return [(str(key), str(value)) for key, value in options.items()]
    if isinstance(options, list):
        normalized = []
        for idx, value in enumerate(options):
            label = chr(ord("A") + idx)
            text = str(value)
            if len(text) >= 2 and text[1] in {".", "、", "．"} and text[0].isalpha():
                label, text = text[0].upper(), text[2:].strip()
            normalized.append((label, text))
        return normalized
    return []


def render_llm_config_sidebar() -> None:
    st.subheader("LLM API 配置")
    current = st.session_state.llm_config
    api_key = st.text_input(
        "OPENAI_COMPATIBLE_API_KEY",
        value=current.get("api_key", ""),
        type="password",
        help="兼容旧配置；DeepSeek API Key 也填在这里。",
    )
    base_url = st.text_input(
        "OPENAI_COMPATIBLE_BASE_URL",
        value=current.get("base_url") or "https://api.deepseek.com",
    )
    model = st.text_input("CHAT_MODEL", value=current.get("model") or "deepseek-chat")
    st.session_state.llm_config = {
        "api_key": api_key.strip(),
        "base_url": base_url.strip() or "https://api.deepseek.com",
        "model": model.strip() or "deepseek-chat",
    }
    if st.session_state.llm_config["api_key"]:
        st.caption("API Key 已配置，仅保存在当前会话。")
    else:
        st.warning("未配置 API Key，出题和总结会提示配置错误。")


def build_document(course_id: int, document: dict) -> int:
    store = CourseVectorStore()

    parsed = parse_document(document["file_path"])
    chunks = split_parsed_items(parsed)
    for chunk in chunks:
        chunk["course_id"] = course_id
        chunk["document_id"] = document["id"]

    vector_ids = store.add_chunks(course_id, chunks)
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


def rebuild_course_knowledge_base(course_id: int, documents: list[dict]) -> int:
    store = CourseVectorStore()
    store.reset_course_collection(course_id)
    db.delete_course_chunks(course_id)

    total = 0
    for document in documents:
        total += build_document(course_id, document)
    return total


def render_home():
    st.title("基于 RAG 的多课程资料智能问答与习题生成系统")
    st.write(
        "面向期末复习场景，系统为每门课程建立独立知识库，支持课程资料上传、"
        "基于资料的智能问答、自动生成习题和复习总结。"
    )
    st.subheader("功能流程")
    st.markdown(
        """
1. 新建并选择课程。
2. 上传 PDF、DOCX、PPTX 课程资料。
3. 解析文本，切分 chunk，并写入当前课程独立 Chroma collection。
4. 在当前课程知识库中检索相关资料，完成问答、出题和总结。
5. SQLite 保存课程、文件、chunk、问答历史和题目记录。
        """
    )
    st.info("默认使用 DeepSeek-compatible API。请在侧边栏配置 API Key 后进行问答、出题和总结。")


def render_course_page():
    st.title("课程管理")
    with st.form("create_course"):
        name = st.text_input("课程名称", placeholder="例如：操作系统")
        description = st.text_area("课程描述", placeholder="课程范围、教材或复习说明")
        submitted = st.form_submit_button("新建课程")
        if submitted:
            if not name.strip():
                st.error("课程名称不能为空。")
            else:
                try:
                    course_id = db.create_course(name, description)
                    st.session_state.current_course_id = course_id
                    st.success("课程已创建并设为当前课程。")
                except Exception as exc:
                    st.error(f"新建课程失败：{exc}")

    courses = db.list_courses()
    st.subheader("课程列表")
    if not courses:
        st.caption("暂无课程。")
        return

    options = {f"{c['name']}（ID: {c['id']}）": c["id"] for c in courses}
    current_id = st.session_state.get("current_course_id", courses[0]["id"])
    labels = list(options.keys())
    default_label = next((k for k, v in options.items() if v == current_id), labels[0])
    selected = st.selectbox("选择当前课程", labels, index=labels.index(default_label))
    st.session_state.current_course_id = options[selected]

    course = get_current_course()
    if course:
        col1, col2, col3 = st.columns(3)
        col1.metric("当前课程", course["name"])
        col2.metric("资料数量", len(db.list_documents(course["id"])))
        col3.metric("知识库 chunk", db.count_chunks(course["id"]))
        st.write(course.get("description") or "无课程描述。")


def render_upload_page():
    st.title("资料上传与知识库构建")
    course = require_course()
    if not course:
        return
    st.caption(f"当前课程：{course['name']}，向量库 collection：course_{course['id']}")

    uploaded_files = st.file_uploader(
        "上传 PDF、DOCX、PPTX",
        type=["pdf", "docx", "pptx"],
        accept_multiple_files=True,
    )
    if uploaded_files and st.button("保存上传文件"):
        course_dir = UPLOAD_DIR / f"course_{course['id']}"
        course_dir.mkdir(parents=True, exist_ok=True)
        for file in uploaded_files:
            target = course_dir / file.name
            with target.open("wb") as f:
                f.write(file.getbuffer())
            db.add_document(course["id"], file.name, Path(file.name).suffix.lower(), target)
        st.success("文件已保存。")

    docs = db.list_documents(course["id"])
    st.subheader("已上传文件")
    if docs:
        st.dataframe(
            [
                {
                    "ID": d["id"],
                    "文件名": d["file_name"],
                    "类型": d["file_type"],
                    "上传时间": d["upload_time"],
                    "解析状态": d["parse_status"],
                }
                for d in docs
            ],
            use_container_width=True,
        )
        if st.button("构建或更新当前课程知识库"):
            total = 0
            try:
                CourseVectorStore().reset_course_collection(course["id"])
                db.delete_course_chunks(course["id"])
            except Exception as exc:
                st.error(f"重置当前课程向量库失败：{exc}")
                return

            progress = st.progress(0)
            for idx, document in enumerate(docs, start=1):
                try:
                    count = build_document(course["id"], document)
                    total += count
                except Exception as exc:
                    db.update_document_status(document["id"], f"failed: {exc}")
                    st.error(f"{document['file_name']} 解析失败：{exc}")
                progress.progress(idx / len(docs))
            st.success(f"知识库更新完成，共写入 {total} 个 chunk。")
            st.rerun()
    else:
        st.info("当前课程还没有上传资料。")


def render_qa_page():
    st.title("智能问答")
    course = require_course()
    if not course:
        return
    st.caption(f"当前课程：{course['name']}")

    question = st.text_area("输入问题", placeholder="例如：请求分页和基本分页有什么区别？")
    top_k = st.slider("检索数量 top_k", 1, 10, 5)
    if st.button("提交问题"):
        try:
            result = ask_course(course["id"], question, top_k)
            st.caption(
                f"检索策略：{result.get('retrieval_mode')}；"
                f"查询类型：{result.get('route_type')}；"
                f"检索查询：{result.get('retrieval_query')}"
            )
            st.markdown(result["answer"])
            st.subheader("参考来源")
            if result["sources"]:
                for source in result["sources"]:
                    st.write("- " + source_label(source))
            else:
                st.write("无明确来源。")
        except Exception as exc:
            st.error(str(exc))

    st.subheader("问答历史")
    for item in db.list_qa_history(course["id"]):
        with st.expander(f"{item['created_at']} - {item['question']}"):
            st.markdown(item["answer"])
            st.caption(item.get("sources") or "")


def render_question_page():
    st.title("自动出题")
    course = require_course()
    if not course:
        return
    st.caption(f"当前课程：{course['name']}")

    col1, col2 = st.columns(2)
    scope = col1.text_input("知识范围或关键词", placeholder="例如：虚拟内存")
    question_type = col2.selectbox("题型", ["选择题", "判断题", "填空题", "简答题"])
    col3, col4 = st.columns(2)
    difficulty = col3.selectbox("难度", ["简单", "中等", "困难"], index=1)
    count = col4.number_input("题目数量", min_value=1, max_value=20, value=5)
    st.caption("系统会生成答案和解析，但默认折叠隐藏，适合先自测再查看。")

    if st.button("生成题目"):
        try:
            result = generate_questions(
                course_id=course["id"],
                scope=scope,
                question_type=question_type,
                difficulty=difficulty,
                count=int(count),
                with_answer=True,
            )
            st.session_state.last_generated_questions = result
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.get("last_generated_questions")
    if result:
        st.subheader("生成结果")
        for idx, item in enumerate(result["questions"], start=1):
            st.markdown(f"#### 第 {idx} 题")
            st.markdown(str(item.get("question_content", "")))
            options = normalize_options(item.get("options"))
            if options:
                option_labels = [f"{label}. {text}" for label, text in options]
                st.radio("选择你的答案", option_labels, key=f"answer_choice_{idx}", index=None)
            with st.expander("查看答案与解析", expanded=False):
                st.write("答案：", item.get("answer", ""))
                st.write("解析：", item.get("analysis", ""))
                st.write("知识点：", item.get("knowledge_point", ""))
                if item.get("sources"):
                    st.write("模型来源说明：", item.get("sources"))
                if item.get("parse_error"):
                    st.warning("模型返回不是标准 JSON，以上为原始输出。")
            st.divider()
        st.subheader("资料来源")
        for source in result["sources"]:
            st.write("- " + source_label(source))

    st.subheader("题目记录")
    records = db.list_question_records(course["id"])
    if records:
        st.dataframe(
            [
                {
                    "时间": r["created_at"],
                    "题型": r["question_type"],
                    "难度": r["difficulty"],
                    "题干": r["question_content"][:80],
                    "知识点": r["knowledge_point"],
                }
                for r in records
            ],
            use_container_width=True,
        )
    else:
        st.caption("暂无题目记录。")


def render_summary_page():
    st.title("复习总结")
    course = require_course()
    if not course:
        return
    st.caption(f"当前课程：{course['name']}")

    summary_type = st.selectbox("总结类型", ["课程复习提纲", "重点知识总结", "易混淆知识点", "考前速记卡片"])
    scope = st.text_input("知识范围，可留空", placeholder="例如：进程管理")
    top_k = st.slider("参考资料数量", 3, 20, 12)
    if st.button("生成总结"):
        try:
            result = generate_summary(course["id"], summary_type, scope, top_k)
            st.markdown(result["summary"])
        except Exception as exc:
            st.error(str(exc))


PAGES = {
    "首页 / 项目介绍": render_home,
    "课程管理": render_course_page,
    "资料上传": render_upload_page,
    "智能问答": render_qa_page,
    "自动出题": render_question_page,
    "复习总结": render_summary_page,
}


with st.sidebar:
    st.header("导航")
    page = st.radio("页面", list(PAGES.keys()))
    st.divider()
    render_llm_config_sidebar()
    st.divider()
    course = get_current_course()
    if course:
        st.success(f"当前课程：{course['name']}")
    else:
        st.warning("未选择课程")

PAGES[page]()
