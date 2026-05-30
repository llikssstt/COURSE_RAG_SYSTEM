# COURSE_RAG_SYSTEM Backend

FastAPI 后端，复用 `modules/` 中的文档解析、文本切分、Chroma 检索、RAG 问答、自动出题和复习总结逻辑。

## 启动

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 接口

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

LLM API Key 不在后端持久化。前端会在问答、出题、总结请求中传入 `llm_config`。
