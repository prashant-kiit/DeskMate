# AI Engineering Interview — Questions Asked

> Extracted only from the interview transcript. Wording is lightly cleaned for readability; no inferred questions added.

## GenAI / RAG

1. Can you walk me through one of your GenAI based projects in more detail? What was the problem statement and what kind of data were you dealing with?
2. Were the Confluence documents text-only, or did they contain images or tables?
3. How did you extract relevant context/info from text, images, and videos? What services did you use?
4. Can you detail the RAG ingestion pipeline: content extraction, chunking strategy and rationale, embeddings, enrichment/metadata/NER, and cloud services?
5. What additional metadata did you store with the chunks?
6. How did you maintain RBAC so users could not receive documents they did not have access to?
7. How did you handle source-document updates, new documents, and incremental loads?
8. What retrieval techniques did you use to extract relevant information from the vector database?
9. How does HNSW work on the backend? What is the concept behind it?
10. What post-retrieval steps did you use to improve response quality?
11. Did you use reranking to improve the chunks returned to the user?
12. How did you evaluate response quality? Did you use evaluation metrics or benchmarks?

## Agents / MCP

1. Have you worked on multi-agent orchestration using LangGraph and multiple agents to complete a workflow?
2. Did you use MCP protocols or agent-to-agent protocols?
3. What MCP methods/tools were available through the Confluence client? Was it one tool or multiple tools?

