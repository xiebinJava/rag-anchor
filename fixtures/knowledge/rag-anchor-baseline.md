# RAGAnchor baseline knowledge

RAGAnchor uses PostgreSQL with the pgvector extension as its planned vector storage. The first local query path uses deterministic Markdown fixtures so contributors can verify retrieval and citations without external credentials.

Every grounded answer must cite the source document and the position of the supporting text. When the fixture contains no supporting evidence, the service returns no answer instead of guessing.
