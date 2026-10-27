---
status: accepted
---

# Use Python, FastAPI, PostgreSQL and pgvector as the initial technical baseline

当前项目采用 Python + FastAPI 提供 HTTP API，使用 PostgreSQL 保存业务和文档元数据，并使用 pgvector 承载第一阶段的向量存储和相似度检索；本地开发通过 Docker Compose，后续以容器方式部署。这样可以用一个数据库同时维护文档版本、分片、向量和检索过滤条件，先验证 RAG 质量，避免过早绑定专用向量数据库或云厂商服务。

向量存储通过小型 `VectorStore` 接口隔离。小规模 fixture 和初始数据集优先使用精确近邻搜索；只有在基准数据证明需要时，才启用 HNSW 等近似索引，并同时验证同步范围过滤下的召回率。

只有在持续的检索延迟、错误率、索引构建竞争、过滤召回率或独立扩缩容需求达到目标约束时，才评估迁移到专用向量后端。迁移前必须保留当前实现作为对照，完成数据回填或双写，并用固定 RAG 评估集比较召回和回答质量。

LLM、Embedding 和外部知识源通过独立适配层隔离，具体供应商不进入核心领域模型。
