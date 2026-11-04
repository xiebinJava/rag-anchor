# 部署指南

## 服务启动

本地开发时使用 `uv sync --dev` 安装依赖，然后通过 ASGI 进程启动 HTTP 服务。

## 健康检查

健康检查端点返回 `status` 字段，值为 `ok` 表示进程正常响应。

## 配置说明

评估模式可通过环境变量 `RAG_ANCHOR_EVAL_MODE` 设置为 `lexical` 或 `fixed_vector`。
