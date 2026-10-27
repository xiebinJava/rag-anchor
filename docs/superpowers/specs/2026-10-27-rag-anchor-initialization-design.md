# RAGAnchor Initialisation Design

## Intent

建立一个可公开维护、可被贡献者快速验证的 RAGAnchor 工程骨架，并让每次 push 或 pull request 自动执行一致的质量检查。这个阶段的目标是验证项目边界、API 约定和开发工具链，不提前接入具体厂商知识源或真实模型。

## Goals

- 统一使用 `RAGAnchor`、`rag_anchor` 和 `rag-anchor` 作为项目标识。
- 建立 Python `src/` 布局、测试目录、配置入口和公开项目文档。
- 提供最小 FastAPI 应用和健康检查接口，作为后续 API 扩展的可运行基线。
- 提供统一响应信封 `{code, msg, trace_id, data}`。
- 提供接口测试和 OpenAPI Schema 测试。
- 启用 GitHub Actions CI，执行格式、静态类型、测试和 Schema 检查。
- CI 使用本地 fixture 和 Fake Provider，不依赖私有连接器、真实模型或生产凭证。

## Non-goals

- 本阶段不实现具体厂商知识源连接器。
- 本阶段不实现真实 Embedding、LLM、PostgreSQL/pgvector 查询或异步同步 Worker。
- 本阶段不配置自动部署、生产密钥或外部服务凭证。
- 本阶段不构建 Web UI。

## Approaches

### CI-only

只添加 GitHub Actions 配置。优点是改动最小；缺点是当前仓库没有可运行的 Python 工程和稳定测试入口，CI 很快会退化成占位检查。

### Initial runnable scaffold — recommended

先建立最小 FastAPI 应用、健康检查、统一响应模型、接口测试、OpenAPI 测试和 CI。它提供一个真实可运行的基线，同时不提前锁定知识源和模型实现。后续 RAG 功能可以沿着已有目录和接口逐步增加。

### Full RAG vertical slice

直接加入数据库、分片、Embedding、pgvector 和回答生成。它能更快看到完整效果，但会同时引入模型配置、数据库迁移和外部服务依赖，不适合在项目身份和 CI 基线刚建立时一次性展开。

本阶段采用 `Initial runnable scaffold`；完整 RAG vertical slice 作为下一阶段单独规划。

## Quality gates

- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run pyright`
- `uv run pytest`
- OpenAPI 路径、响应模型和安全声明测试通过。
- 工作流在 push、pull request 和手动触发时运行，不执行自动部署。

## Completion criteria

本设计完成后，仓库应能在干净环境中安装依赖并启动最小应用；健康检查和 OpenAPI 测试通过；GitHub Actions 在不提供任何私有密钥的情况下通过全部质量门禁；项目内不出现组织、内部系统或具体厂商连接器信息。
