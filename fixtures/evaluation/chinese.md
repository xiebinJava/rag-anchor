# 部署与开发

本地开发使用 uv sync --dev 安装依赖，并通过 ASGI 进程启动 HTTP 服务。

# 健康检查

健康检查端点返回 JSON 封装，其中 data.status 为 ok 表示进程正常。

# 评估配置

环境变量 RAG_ANCHOR_EVAL_MODE 可设置为 lexical 或 fixed_vector。
