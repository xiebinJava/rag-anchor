# Platform Guide

## Local development

Install dependencies with `uv sync --dev` and start the ASGI application for interactive testing.

## Health endpoint

The health route returns a JSON envelope where `data.status` is `ok` when the process is alive.

## Query API

Clients send `POST /api/v1/query` with a `question` field and optional `top_k` between 1 and 5.
