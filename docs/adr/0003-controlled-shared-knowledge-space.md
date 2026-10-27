---
status: accepted
---

# Use a controlled shared knowledge space for the first permission boundary

第一阶段只同步专门的受控共享知识空间，并要求所有 RAG 目标用户都拥有该空间的阅读权限；RAG 不读取或服务于空间之外的文档，也不把高权限连接器账号的可读范围直接当成最终用户的可读范围。用户级细粒度 ACL、动态权限同步和跨空间检索延后到核心检索闭环稳定之后。

这个边界以较低的复杂度避免第一版发生权限绕过，同时保留后续接入用户身份委托和逐文档权限过滤的演进空间。
