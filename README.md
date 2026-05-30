# 基于 RAG 的多课程资料智能问答与习题生成系统

这是一个面向期末复习场景的课程设计项目。系统为每门课程建立独立知识库，支持上传 PDF、DOCX、PPTX 课程资料，并基于当前课程资料完成智能问答、自动出题和复习总结。

当前版本已从 Streamlit 单体应用重构为：

- 后端：FastAPI + SQLite + Chroma，复用原有 `modules/` RAG 核心代码。
- 前端：React + Vite + TypeScript + Tailwind CSS，教育类 SaaS Dashboard 风格。
- 旧版 Streamlit 入口保留为 `legacy_app.py`，用于对照。

## 目录结构

```text
COURSE_RAG_SYSTEM/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── core/
│   ├── modules/
│   ├── prompts/
│   ├── config.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
├── data/
│   ├── uploads/
│   ├── chroma/
│   └── app.db
├── legacy_app.py
├── README.md
└── .gitignore
```

## 后端启动

建议使用 Python 3.10+。

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

前端 API 地址通过 `frontend/.env` 配置，可参考 `frontend/.env.example`：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## LLM API 配置

前端首页提供 LLM API 配置卡片，配置只保存在浏览器 localStorage，不写入数据库：

- `OPENAI_COMPATIBLE_API_KEY`
- `OPENAI_COMPATIBLE_BASE_URL`，默认 `https://api.deepseek.com`
- `CHAT_MODEL`，默认 `deepseek-chat`

每次问答、出题、总结请求都会把当前配置放入请求体的 `llm_config` 字段。后端不会持久化 API Key。

后端也兼容环境变量：

```bash
set OPENAI_COMPATIBLE_API_KEY=你的APIKey
set OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com
set CHAT_MODEL=deepseek-chat
```

兼容旧变量：

```bash
set DEEPSEEK_API_KEY=你的DeepSeek API Key
```

显式调试时可使用 mock：

```bash
set MOCK_MODE=true
```

## Embedding 模型

默认使用本地中文 BGE：

```text
EMBEDDING_PROVIDER=bge
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DIM=512
```

可通过 ModelScope 下载：

```bash
python scripts/download_bge_modelscope.py
```

模型目录：

```text
data/models/bge-small-zh-v1.5
```

如果从旧的 384 维 mock embedding 切换到 512 维 BGE，必须重新构建课程知识库。上传资料页的“构建或更新当前课程知识库”会重置当前课程 collection 并重新写入向量。

## 核心功能

1. 课程管理：新建课程、选择当前课程、查看资料数、chunk 数、问答数和题目数。
2. 资料上传：支持 PDF、DOCX、PPTX，多文件上传到 `data/uploads/course_{course_id}/`。
3. 知识库构建：解析文本、切分 chunk、写入 SQLite 和当前课程独立 Chroma collection。
4. 智能问答：只检索当前课程知识库，返回答案、检索策略、查询类型、检索查询和参考来源。
5. 自动出题：支持选择题、判断题、填空题、简答题；答案与解析默认折叠，适合先自测。
6. 复习总结：支持课程复习提纲、重点知识总结、易混淆知识点、考前速记卡片。

## API 概览

- `GET /api/health`
- `GET /api/courses`
- `POST /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/courses/{course_id}/stats`
- `POST /api/courses/{course_id}/documents/upload`
- `GET /api/courses/{course_id}/documents`
- `POST /api/courses/{course_id}/knowledge-base/rebuild`
- `POST /api/courses/{course_id}/qa`
- `GET /api/courses/{course_id}/qa/history`
- `POST /api/courses/{course_id}/questions/generate`
- `GET /api/courses/{course_id}/questions/history`
- `POST /api/courses/{course_id}/summaries/generate`
- `GET /api/config/defaults`

## 演示流程

1. 进入“课程管理”，新建课程“操作系统”。
2. 选择“操作系统”为当前课程。
3. 进入“资料上传”，上传操作系统 PPTX、DOCX 或 PDF。
4. 点击“构建或更新当前课程知识库”。
5. 进入“智能问答”，提问“请求分页和基本分页有什么区别？”。
6. 查看答案、检索策略和参考来源。
7. 进入“自动出题”，输入知识范围“虚拟内存”，选择“选择题”“中等”“5 题”。
8. 先作答，再展开“查看答案与解析”。
9. 进入“复习总结”，生成“课程复习提纲”或“易混淆知识点”。

## 课程设计报告要点

### 立项目的

解决学生期末复习中多课程资料分散、知识点难以整合、缺少自测题的问题，构建一个基于课程资料的智能复习系统。

### 可行性调研

RAG 技术适合把大模型与本地课程资料结合。SQLite、Chroma、FastAPI、React + Vite 都适合轻量级课程设计项目，PDF/DOCX/PPTX 解析也有成熟 Python 库支持。

### 需求分析

系统需要支持课程隔离、资料解析、知识库构建、基于资料问答、自动出题、复习总结和历史记录保存。重点是可运行、可演示和结构清晰。

### 系统总体设计

前端负责页面交互和 LLM 配置保存；后端负责 API、业务服务、SQLite 持久化、Chroma 检索和 LLM 调用；RAG 核心模块保留在 `backend/modules/`。

### 功能模块设计

- 课程模块：课程 CRUD 与统计。
- 文档模块：上传、保存、解析状态管理。
- 知识库模块：解析、切分、embedding、向量入库。
- 问答模块：混合检索、Prompt 组装、答案生成、历史保存。
- 出题模块：按题型、难度、范围生成题目。
- 总结模块：按总结类型生成 Markdown 复习内容。

### 数据库设计

SQLite 包含 `courses`、`documents`、`chunks`、`qa_history`、`question_bank`。所有业务记录都绑定 `course_id`，保证多课程隔离。

### RAG 工作流程

上传资料后解析为带来源的文本片段，切分为 chunk，生成 embedding 并写入 `course_{course_id}` collection。问答、出题和总结时只检索当前课程 collection，并把检索结果注入 Prompt。

### 自动出题流程

用户设置范围、题型、难度和数量；系统检索当前课程资料；LLM 根据资料生成题干、选项、答案、解析、知识点和来源；题目保存到 `question_bank`。

### 测试用例

| 用例 | 输入 | 预期结果 |
| --- | --- | --- |
| 未选择课程访问上传页 | 进入资料上传 | 提示先选择课程 |
| 新建课程 | 操作系统 | 返回课程并可选中 |
| 上传 DOCX | 有效 DOCX | documents 表新增记录 |
| 构建知识库 | 点击重建 | 当前课程 chunks 和 collection 更新 |
| 空知识库问答 | 未构建直接提问 | 返回清晰错误 |
| 多课程隔离 | 两门课分别上传资料 | 检索只命中当前课程 |
| 自动出题 | 虚拟内存、5 道选择题 | 题目展示，答案解析折叠 |

### 项目创新点

- 面向多课程复习，而不是普通聊天机器人。
- 每门课程独立 Chroma collection，避免资料混杂。
- 同时支持问答、出题、总结三类复习任务。
- 前端化 LLM 配置，API Key 不落库。
- 答案解析折叠展示，符合学生自测流程。

### 后续改进方向

- 增加扫描版 PDF OCR。
- 支持题目导出 Word/PDF。
- 支持文档删除和局部增量更新。
- 增加来源原文预览。
- 引入更强的重排序模型和答案可信度评分。

## 注意事项

- `data/app.db`、`data/chroma/`、`data/uploads/`、本地模型缓存、`frontend/node_modules/`、`frontend/dist/` 都已加入 `.gitignore`。
- 如果上传扫描版 PDF，当前普通文本解析可能提取不到内容，需要后续接入 OCR。
- API Key 只保存在前端 localStorage 或通过环境变量读取，不写入 SQLite。
