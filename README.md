# 基于 RAG 的多课程资料智能问答与习题生成系统

本项目是一个适合课程设计展示的 Python + Streamlit 应用。系统面向期末复习场景，为每门课程建立独立知识库，支持上传 PDF、DOCX、PPTX 资料，完成基于资料的智能问答、自动出题和复习总结。

## 1. 系统设计方案

系统采用轻量模块化设计：

- 前端展示：Streamlit，包含首页、课程管理、资料上传、智能问答、自动出题、复习总结。
- 结构化数据库：SQLite，保存课程、文件、chunk、问答历史、题目记录。
- 向量数据库：Chroma，每门课程使用独立 collection，命名为 `course_{course_id}`。
- 文档解析：PDF 使用 `pypdf`，DOCX 使用 `python-docx`，PPTX 使用 `python-pptx`。
- Embedding：封装在 `modules/llm_client.py`，默认 mock hashing embedding，可替换 OpenAI-compatible embedding。
- 大模型调用：封装 OpenAI-compatible Chat API，默认 `MOCK_MODE=true`，无 API Key 也能演示流程。

核心 RAG 流程参考了 Datawhale `all-in-rag` 的实战项目思路：数据准备、索引构建、检索优化、生成集成四段式流水线。本项目保留课程设计所需的轻量实现，没有直接引入完整 LangChain/FAISS 工程栈，而是在 Chroma 版本中实现了相同的关键思想：

- 文本切分参考 `RecursiveCharacterTextSplitter`：按 `\n\n`、`\n`、句号、分号、逗号、空格、字符级递归切分。
- 检索优化参考“向量检索 + BM25 + RRF 融合”：语义召回和关键词召回分别排序，再用 RRF 合并。
- 生成集成参考“查询路由 + 查询改写 + 基于检索上下文生成”：课程问答中保留 `list/detail/general` 路由和轻量查询改写。
- 多课程场景做了额外适配：每门课程仍使用独立 Chroma collection，例如 `course_1`、`course_2`。

核心约束：

- 必须先选择课程。
- 上传资料、chunk、向量、问答历史、题目记录都绑定 `course_id`。
- 检索只访问当前课程的 Chroma collection，避免课程内容混杂。
- 问答、出题、总结均基于当前课程资料，资料不足时必须提示依据不足。

## 2. 项目目录结构

```text
course_rag_system/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── data/
│   ├── uploads/
│   ├── chroma/
│   └── app.db
├── modules/
│   ├── db.py
│   ├── document_parser.py
│   ├── text_splitter.py
│   ├── vector_store.py
│   ├── llm_client.py
│   ├── rag_qa.py
│   ├── question_generator.py
│   └── review_summary.py
└── prompts/
    ├── qa_prompt.txt
    ├── question_prompt.txt
    └── summary_prompt.txt
```

## 3. 安装与运行

建议使用 Python 3.10 或 3.11。

```bash
cd course_rag_system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

默认使用 DeepSeek OpenAI-compatible Chat API。可以直接在 Streamlit 侧边栏配置，也可以使用环境变量：

```bash
set OPENAI_COMPATIBLE_API_KEY=你的DeepSeek或兼容APIKey
set OPENAI_COMPATIBLE_BASE_URL=https://api.example.com/v1
set CHAT_MODEL=你的模型名
```

DeepSeek 默认值：

```bash
set OPENAI_COMPATIBLE_BASE_URL=https://api.deepseek.com
set CHAT_MODEL=deepseek-chat
```

也兼容：

```bash
set DEEPSEEK_API_KEY=你的DeepSeek API Key
```

只有在离线调试时才建议打开 mock：

```bash
set MOCK_MODE=true
```

## 3.1 Embedding 模型

当前默认 embedding 已替换为本地中文 BGE：

```text
EMBEDDING_PROVIDER=bge
EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
EMBEDDING_DIM=512
```

模型通过 ModelScope 下载，地址：

```text
https://www.modelscope.cn/models/BAAI/bge-small-zh-v1.5
```

首次运行前可以执行：

```bash
python scripts/download_bge_modelscope.py
```

脚本会把模型保存到：

```text
data/models/bge-small-zh-v1.5
```

如果本地模型不可用，系统默认会 fallback 到 mock embedding，避免课堂演示时因为模型下载失败导致系统不可用。需要强制使用真实 BGE 时：

```bash
set EMBEDDING_FALLBACK_TO_MOCK=false
```

注意：Chroma collection 的 embedding 维度是固定的。项目从 mock embedding 的 384 维切换到 BGE 的 512 维后，需要在“资料上传”页点击“构建或更新当前课程知识库”，系统会删除当前课程旧 collection 并用 BGE 重新构建。

## 3.2 前端 API 配置与自测出题

Streamlit 侧边栏提供三个运行时配置项：

- `OPENAI_COMPATIBLE_API_KEY`：DeepSeek 或兼容接口 Key，仅保存在当前会话。
- `OPENAI_COMPATIBLE_BASE_URL`：默认 `https://api.deepseek.com`。
- `CHAT_MODEL`：默认 `deepseek-chat`。

自动出题页面会先展示题干和选项，答案与解析默认折叠隐藏。学生可以先选择自己的答案，再展开“查看答案与解析”进行自测。

## 4. 数据库设计

### courses

| 字段 | 说明 |
| --- | --- |
| id | 课程 ID |
| name | 课程名称 |
| description | 课程描述 |
| created_at | 创建时间 |

### documents

| 字段 | 说明 |
| --- | --- |
| id | 文件 ID |
| course_id | 所属课程 |
| file_name | 文件名 |
| file_type | 文件类型 |
| file_path | 文件路径 |
| upload_time | 上传时间 |
| parse_status | 解析状态 |

### chunks

| 字段 | 说明 |
| --- | --- |
| id | chunk ID |
| course_id | 所属课程 |
| document_id | 所属文档 |
| chunk_text | chunk 文本 |
| source_file | 来源文件 |
| page_number | PDF 页码 |
| slide_number | PPT 页码 |
| section_title | 章节标题 |
| vector_id | Chroma 向量 ID |
| created_at | 创建时间 |

### qa_history

保存课程问答历史，包括问题、答案、来源和时间。

### question_bank

保存题目类型、难度、题干、答案、解析、知识点、来源和时间。

## 5. RAG 工作流程

1. 用户选择当前课程。
2. 上传 PDF、DOCX、PPTX。
3. 系统解析文本并保留来源信息。
4. 文本清洗并切分为 chunk。
5. 生成 embedding。
6. 写入当前课程独立 Chroma collection：`course_{course_id}`。
7. 用户提问时，先进行轻量查询路由和查询改写。
8. 只在当前课程 collection 中执行向量检索，并从同一课程 collection 读取文本做 BM25 关键词召回。
9. 使用 BM25 关键词检索补充召回，再通过 RRF 合并排序。
10. 将检索资料和问题填入问答 Prompt。
11. LLM 输出简明答案、详细解释和参考来源。
12. SQLite 保存问答历史。

## 5.1 all-in-rag 参考点与本项目适配

| all-in-rag 思路 | 本项目实现 |
| --- | --- |
| 数据加载、清洗、文本分块 | `document_parser.py` + `text_splitter.py` |
| RecursiveCharacterTextSplitter | 自实现递归分隔符切分，避免额外重依赖 |
| BGE embedding + FAISS/向量库 | `llm_client.py` 中的 BGE embedding + Chroma |
| BM25 + 向量检索混合召回 | `vector_store.py` 中 `bm25_search`、`vector_search` |
| RRF 融合排序 | `vector_store.py` 中 `_rrf_fuse` |
| 查询路由与查询改写 | `rag_qa.py` 中 `route_query`、`rewrite_query` |
| 生成集成 | `rag_qa.py`、`question_generator.py`、`review_summary.py` |

## 6. 自动出题流程

1. 用户选择课程、题型、难度、题目数量和知识范围。
2. 系统使用知识范围在当前课程知识库检索资料。
3. 将检索结果和出题要求填入自动出题 Prompt。
4. LLM 生成题干、选项、答案、解析、知识点和来源。
5. 系统保存题目记录到 `question_bank`。

## 7. Prompt 模板

Prompt 单独保存在 `prompts/`：

- `qa_prompt.txt`：要求严格基于课程资料回答，不得编造。
- `question_prompt.txt`：要求输出 JSON 题目数组，题目必须来自资料。
- `summary_prompt.txt`：要求生成复习提纲、重点知识、易混淆点和速记卡片。

## 8. 异常处理

系统处理了以下常见情况：

- 未选择课程：页面提示先选择课程。
- 未上传资料：资料页面显示空状态。
- 文件解析失败：写入 `parse_status=failed: ...` 并提示错误。
- 知识库为空：问答、出题、总结前拦截。
- API Key 未配置：默认 mock 模式；关闭 mock 且未配置 Key 时给出明确错误。

## 9. 演示流程

1. 打开系统首页，查看项目介绍。
2. 进入“课程管理”，新建课程“操作系统”。
3. 进入“资料上传”，上传操作系统 PPTX、DOCX 或 PDF。
4. 点击“构建或更新当前课程知识库”。
5. 进入“智能问答”，提问：`请求分页和基本分页有什么区别？`
6. 查看回答和参考来源。
7. 进入“自动出题”，输入知识范围：`虚拟内存`。
8. 选择题型：选择题；难度：中等；数量：5。
9. 点击生成，查看题目、答案、解析和来源。
10. 进入“复习总结”，生成课程复习提纲或易混淆知识点。

## 10. 课程设计报告支持

### 立项目的

解决学生期末复习中多课程资料分散、重点难以整合、缺少自测题的问题，构建一个基于课程资料的智能复习系统。

### 可行性调研

RAG 技术适合将大模型与本地课程资料结合。Streamlit 能快速完成可视化演示，SQLite 和 Chroma 都适合轻量课程设计项目，PDF/DOCX/PPTX 解析均有成熟 Python 库支持。

### 需求分析

系统需要支持课程管理、资料上传、文档解析、知识库构建、基于资料问答、自动出题、复习总结和历史记录保存。重点是多课程知识隔离与可演示性。

### 系统总体设计

采用前端页面 + 业务模块 + 数据层的结构。Streamlit 负责用户交互，模块层负责解析、切分、向量检索、Prompt 组装和模型调用，SQLite 与 Chroma 负责持久化。

### 功能模块设计

- 课程管理模块：创建、查看、选择课程。
- 文档解析模块：按文件类型提取文本和来源位置。
- 知识库模块：清洗切分文本，写入 Chroma。
- 智能问答模块：检索课程资料并生成答案。
- 自动出题模块：按题型、难度和范围生成题目。
- 复习总结模块：生成提纲、重点和易混淆点。

### 数据库设计

数据库包含 `courses`、`documents`、`chunks`、`qa_history`、`question_bank` 五张表。所有业务数据都包含 `course_id`，保证课程级隔离。

### RAG 工作流程

文档解析后切分为 chunk，生成 embedding 存入课程独立向量库。问答时根据问题检索当前课程 chunk，将资料片段注入 Prompt，限制大模型只基于资料回答。

### 自动出题流程

系统先根据知识范围检索当前课程资料，再把资料、题型、难度、数量传给模型。模型输出题目、答案、解析、知识点和来源，最终保存到题库。

### 测试用例

| 用例 | 输入 | 预期结果 |
| --- | --- | --- |
| 未选择课程问答 | 直接进入问答页 | 提示先选择课程 |
| 新建课程 | 操作系统 | 课程创建成功 |
| 上传 DOCX | 有效 DOCX 文件 | 文件保存并显示 uploaded |
| 构建知识库 | 点击构建 | 状态显示 parsed: n chunks |
| 知识库为空问答 | 未构建直接提问 | 提示知识库为空 |
| 多课程隔离 | A/B 两课分别上传资料 | A 课检索不到 B 课资料 |
| 自动出题 | 虚拟内存、5 道选择题 | 生成题目并保存记录 |

### 项目创新点

- 面向多课程复习，而非普通聊天机器人。
- 每门课程独立 Chroma collection，避免知识混杂。
- 同时支持问答、出题和总结三类复习任务。
- 支持 mock 模式，便于课堂演示和无 API 环境运行。

### 后续改进方向

- 接入更强中文 embedding 模型，例如 bge-small-zh 或通义千问 embedding。
- 增加文件删除与知识库重建策略。
- 支持按章节浏览 chunk 和来源原文。
- 增加题目导出 Word/PDF。
- 加入更严格的引用校验和答案可信度评分。
