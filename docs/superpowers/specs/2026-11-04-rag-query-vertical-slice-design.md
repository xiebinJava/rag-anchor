# RAG Query Vertical Slice Design

## Intent

为 RAGAnchor 增加第一个可端到端验证的查询闭环，让贡献者可以在不配置真实模型、外部知识源或向量数据库的情况下验证“问题 → 检索依据 → 回答 → 引用”的行为。

## Goals

- 增加 `POST /api/v1/query` 查询接口，并沿用 `{code, msg, trace_id, data}` 响应信封。
- 使用仓库内的本地 Markdown fixture 作为知识源。
- 使用确定性的分片和关键词检索，保证测试可重复、无需外部服务。
- 返回基于检索证据生成的确定性回答和可验证引用。
- 在没有足够证据时返回明确的 `no_answer` 结果，不猜测。
- 为 Swagger/OpenAPI、成功查询、无答案和输入校验增加接口测试。

## Non-goals

- 本阶段不接入真实 Wiki/cloud-document 连接器。
- 本阶段不引入 Embedding、LLM、PostgreSQL 或 pgvector 运行时依赖。
- 本阶段不实现用户级权限、同步 Worker、管理接口或 Web UI。

## Approaches

### Local lexical retrieval — selected

使用本地 Markdown 文档、确定性分片和关键词重叠评分，回答器只返回排名最高的证据文本，并附带来源元数据。优点是零外部依赖、行为稳定、可以先验证 API、引用和无答案语义；缺点是检索质量不代表最终语义检索质量。

### In-memory embeddings

在内存中加入 Embedding 和相似度计算。语义效果更接近后续方案，但会引入模型下载、维度和运行时配置，无法保持当前最小闭环的可复现性。

### PostgreSQL + pgvector first

直接建立数据库、迁移、Embedding 和向量检索。它更接近生产形态，但会把数据库基础设施问题和查询契约问题混在一起，违反当前“先验证核心闭环”的阶段目标。

本阶段采用 Local lexical retrieval；后续在固定评估集证明接口和引用语义稳定后，再替换检索实现。

## Public interface

`POST /api/v1/query` 接收：

```json
{"question": "Which database does RAGAnchor use?", "top_k": 3}
```

其中 `question` 必填且长度为 1–2000，`top_k` 可选，范围为 1–5，默认值为 3。

成功响应的 `data` 包含：

- `answer`: 有依据时的确定性回答，没有依据时为 `null`；
- `citations`: 引用列表，包含文档 ID、标题、来源地址、分片 ID、位置和文本片段；
- `no_answer`: 是否没有足够依据。

无答案是 HTTP 200 下的正常业务结果，`citations` 为空，不能通过异常或猜测代替。

## Module seams

- `KnowledgeSource`: 提供文档集合；本阶段由 Markdown fixture adapter 实现。
- `Retriever`: 根据问题返回有序的检索分片；本阶段由关键词检索实现。
- `AnswerGenerator`: 只基于检索分片生成回答；本阶段由确定性 fixture answerer 实现。
- HTTP query route: 负责请求校验、trace ID 和统一响应信封，不暴露内部实现细节。

## Acceptance criteria

- 命中已知 fixture 内容时，响应包含非空回答和至少一个可验证引用。
- 查询未知内容时，响应 `no_answer=true`、`answer=null`、引用为空。
- 非法问题或 `top_k` 被 FastAPI 校验为 4xx。
- OpenAPI 包含请求/响应模型、稳定标签、摘要和公开安全声明。
- 本地格式、Lint、Pyright 和 pytest 全部通过。
