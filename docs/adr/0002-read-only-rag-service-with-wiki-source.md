---
status: accepted
---

# Start with a read-only RAG service and a Wiki/cloud-document source

第一阶段将项目定位为企业知识库 RAG 服务：通过 HTTP API 提供查询，通过 CLI 支持本地调试、数据导入和检索评估；首个真实知识源为 Wiki/云文档，本地 Markdown 作为离线 fixture。第一阶段只读，先验证检索、引用和无答案行为，不直接写入其他业务系统。具体厂商连接器不进入核心领域模型，并通过可选适配器接入。

这种边界能够先验证核心知识问答质量，并将数据源差异隔离在适配层中；Web UI、多数据源、自动业务操作和复杂 Agent 编排延后到核心检索闭环稳定之后。
