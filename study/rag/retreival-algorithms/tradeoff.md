# Tradeoffs between the two retrieval methods

| | Term-based | Embedding-based |
|---|---|---|
| **Speed** | Much faster than embedding-based, at both indexing and query time — term extraction beats embedding generation, and inverted-index lookup beats nearest-neighbor search | Query embedding generation and vector search can be slow |
| **Performance** | Strong out of the box, but has fewer knobs to tune further; can retrieve wrong documents due to term ambiguity | Can outperform term-based with finetuning; focuses on semantics rather than terms, allowing more natural queries. But converting to embeddings can obscure exact keywords, like error codes (`EADDRNOTAVAIL`) or product names |
| **Cost** | Much cheaper | Embedding generation, vector storage, and vector search can all be expensive — the book notes vector database spend is sometimes a fifth to half of a company's model-API spend |

Two more distinctions the book draws:

- **Maturity vs. improvability** — term-based solutions (Elasticsearch, BM25) are mature and reliable immediately, but simplicity means there's less to improve. Embedding-based retrieval can be finetuned — the embedding model, the retriever, or the whole system jointly with the generator — so it has more room to grow over time.
- **Fewer moving parts vs. more** — term-based retrieval doesn't need an embedding model, a vector database, or vector-search tuning at all; embedding-based retrieval introduces all three as new failure points and new things to evaluate (the book calls out MTEB specifically for evaluating embedding quality).

The book's own resolution to this tradeoff is **hybrid search** — combining both, either sequentially (cheap term-based retriever fetches candidates → precise reranker narrows them) or in parallel via reciprocal rank fusion — rather than picking one exclusively.

## When to use VectorDB vs. non-VectorDB

The book doesn't frame this as a binary "pick vector DB or don't" decision — it frames it as **picking a retrieval mechanism (term-based vs. embedding-based vs. hybrid) first**, and the storage layer follows from that choice. A few things worth pulling out explicitly:

**Use term-based / non-vector retrieval when:**
- Speed and cost matter most, especially at high query volume
- Your queries hinge on exact matches — error codes, product SKUs, names — where embeddings tend to blur precision
- You want something that works well immediately with minimal setup

**Use embedding-based / vector DB when:**
- Queries are semantic and phrased naturally rather than as keywords — the "transformer architecture" ambiguity example is the canonical failure mode term-based retrieval can't solve
- You have room and budget to finetune the retriever over time for better performance
- You're doing multimodal or cross-lingual retrieval (implied by the *RAG Beyond Texts* section — embeddings generalize to images, audio, tabular data in ways term matching can't)

**For actually choosing a solution**, the book gives an explicit checklist (*Evaluating Retrieval Solutions*, p. 272):
- What retrieval mechanisms does it support — does it support hybrid search?
- If it's a vector database: which embedding models and vector-search algorithms does it support?
- How scalable is it for your data volume and traffic pattern?
- How long does indexing take, and how much bulk add/delete can it handle at once?
- What's query latency across different retrieval algorithms?
- If managed, is pricing based on document/vector volume or query volume?

**For actually choosing a solution (Concise)**,
- Infra Cost
- Latency (Quick Response)
- Scale (For Everyone)
- Available (Across all the time and region)
To determine above factors understand:
- Architecture (Microservices) of Agent and Model
- Design (DSA) of Agent and Model
