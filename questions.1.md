# Technical Interview Question Bank

**Source:** AI Engineer interview transcript (24-08-2026)
**Scope:** Technical questions only — rephrased as self-contained study questions, in original interview order.

---

## Section A — RAG Architecture & Vector Retrieval

**1. Describe the end-to-end architecture of a RAG pipeline you have built, covering document ingestion, chunking strategy, embedding, storage in a vector database, retrieval, reranking, and response generation.**

- 1.1 Follow-up: Which similarity search (ANN indexing) algorithm did you use for retrieval from the vector database, and what was the reasoning behind that choice?
  - 1.1.1 Sub-question: Explain how Hierarchical Navigable Small World (HNSW) works internally — how nodes and edges represent vectors, how the hierarchy of "small worlds" is layered, and how traversal proceeds from the coarsest layer to the nearest neighbour.
  - 1.1.2 Sub-question: What is the complexity and latency advantage of HNSW over a linear/exhaustive vector scan, and what accuracy trade-off does that approximation introduce?
  - 1.1.3 Sub-question: How does Locality Sensitive Hashing (LSH) work — how does it partition the vector space using random hyperplanes, and how are hash collisions used to place similar vectors into the same bucket?
  - 1.1.4 Sub-question: Why would you choose HNSW over LSH for a production RAG retrieval layer, given that LSH also places semantically similar vectors into similar hash buckets?
  - 1.1.5 Sub-question: In HNSW, on what basis are the small worlds constructed, and what determines which node leads to the next depth level of the search?

---



## Section B — PII / PHI Redaction in a Document Processing Pipeline

**2. You must process documents (PDF, image, or plain text — a multi-modal system) and send them to an LLM hosted on a third-party server. The LLM may be used, but no PII or PHI may ever reach it. For a task such as summarization, how do you design the pipeline to strip PII/PHI before the payload leaves your environment, targeting roughly 90% detection accuracy rather than 100%?**

- 2.1 Follow-up: The requirement is redaction, not blocking — chunks containing PII still carry useful information. How do you redact only the sensitive spans while preserving the rest of the chunk for retrieval and generation?
- 2.2 Follow-up: In a prescription, a patient's name may appear abbreviated or as initials rather than in the full form stored in your Postgres database. How do you detect sensitive entities when there is no exact string match against your known-values table?
- 2.3 Follow-up: Vector similarity is designed for matching, not for differentiation or classification. Given that, what are the limits of using embedding similarity (or a "negative" similarity search) to identify PII spans?
- 2.4 Follow-up: You will not always have the entity in your own database — the document may reference a user outside your system, or a doctor or company name you have never seen. How do you handle detection of unknown entities?
- 2.5 Follow-up: Assume no GPU and no LLM for the redaction step, since hosting LLMs is expensive — only lightweight CPU inference on a standard compute instance. Which class of models or techniques would you use for this task?
  - 2.5.1 Sub-question: Vectorization can also run on CPU and embeddings do not have to be semantic. How can non-semantic vector representations such as bag-of-words be used for CPU-based entity recognition?

---



## Section C — Recommendation Engine Design

**3. Describe the design and internal flow of a recommendation engine you have built — how items are attributed, how user activity is logged, and how candidate items are matched and ranked for display.**

- 3.1 Follow-up: Did you consider representing posts and user preferences as vectors and using vector mathematics for matching, instead of relational attribute filtering?
  - 3.1.1 Sub-question: If each dimension of a vector maps to one attribute of a post (business domain, region, content type), how would you construct that vector and use a distance metric such as Euclidean distance to retrieve the best-matching items?
  - 3.1.2 Sub-question: Does vectorizing deterministic attributes cause a loss of exactness, given that a post's attributes are fixed and vectorization is itself a deterministic function?
  - 3.1.3 Sub-question: What is the difference between passing data through an embedding *model* and through a hand-written embedding *function*, and why do embeddings not always have to be semantic?
  - 3.1.4 Sub-question: What advantages does a vector store with multi-dimensional attribute vectors offer over relational filtering that requires maintaining a large set of tables — for example, supporting multiple distance metrics or building a runtime classifier on top of the vectors?
  - 3.1.5 Sub-question: Should AI techniques be reserved only for non-deterministic problems, or do small statistical ML models (Bayesian networks, KNN or linear classifiers) have a legitimate place in deterministic use cases?

---



## Section D — Hybrid Search

**4. Have you implemented hybrid search in a RAG system, combining vector (semantic) search with lexical (term-based) search? Describe how you combined the two.**

- 4.1 Follow-up: Do you run lexical search first and then apply semantic similarity search over its results, or run both searches in parallel and fuse the outputs? Explain how rank fusion across both result sets works.

**5. Which lexical search algorithm did you use in your hybrid search implementation?**

- 5.1 Follow-up: Was it a simple exact-token or "contains" match, or a fuzzy matching algorithm such as Levenshtein distance? In what situations would you choose fuzzy matching over exact term matching?

**6. What are the weaknesses and failure scenarios of a hybrid search design that runs lexical search first and then performs vector search only over the lexically matched results?**

- 6.1 Follow-up: Which scenarios cause this ordering to lose relevant context or fail to retrieve sufficient context, as opposed to merely increasing latency?
- 6.2 Follow-up: Your corpus stores chunks using the term "influenza" but the user queries "flu" — a typo, abbreviation, or synonym. What happens to retrieval in that case?
- 6.3 Follow-up: Parallel hybrid search with summed rank fusion does not always mitigate this, because a poor lexical result can drag down a chunk that vector search ranked correctly. What other mitigations exist for recovering those missed chunks or widening the vector search space?
- 6.4 Follow-up: How does LLM-based query expansion before retrieval — expanding a query with related terms while preserving the original intent, rather than rewriting it — improve recall for this class of failure?

---



## Section E — Conversational Memory Architecture

**7. Design the memory architecture for a chatbot that supports very long conversations — 100, 200, or 500+ messages with no fixed limit. How do you retain context without exceeding the context window?**

- 7.1 Follow-up: At 300 turns you have roughly 600 messages. Database sharding addresses storage load but not context retention or latency. If the conversation shifted topics over time (writing Python code, then porting it to Java, then writing test cases and penetration tests) and the model must still recall all of it, how do you manage that memory so that latency does not grow with every additional message?
- 7.2 Follow-up: How do you extend this memory so it persists *across* sessions — a user has a 500-message conversation today and starts a new session tomorrow that references it, potentially across a hundred prior conversations?
- 7.3 Follow-up: Fetching all previous session summaries through a simple API call does not scale — the model would be flooded with a hundred old chats on the first message. How do you decide which past context is relevant and should be retrieved?
- 7.4 Follow-up: Describe that cross-session memory architecture at a high level — the orchestration layer, the agent tools, the databases, and the key functions involved.
  - 7.4.1 Sub-question: Which orchestration framework would you use for the agentic flow, and how would you distribute tool calls across the SQL database and the vector database?
  - 7.4.2 Sub-question: Would the design include a dedicated summarization tool for conversation turns that fall out of the rolling window, alongside the hot (recent) memory? How do the rolling window and the summarized history get combined into the final context?

---



## Section F — LLM-as-a-Judge & Evaluation

**8. Use case: a retrieval-based system takes user requirements as input and recommends telecom plans, with a system prompt instructing it to suggest the "best" plan and maximize company profit. For about 10% of users the recommended plan is too expensive or over-provisioned relative to what they actually asked for, while the system works well for the other 90%. Changing the system prompt's definition of "best" creates a regression risk for the working majority. Propose a high-level solution.**

- 8.1 Follow-up: How do you define "expensive" — relative to user attributes, or relative to the stated need in the user's request (for example, a user who only wants to stream music being sold a 7 GB/day plan)?
- 8.2 Follow-up: Are you proposing an LLM-as-a-judge validation layer between generation and the final response? How would the retry or regeneration cycle work when the judge rejects a recommendation?
- 8.3 Follow-up: What exactly should be passed as input to that judge layer — the generator's output, the judge's own prompt, and any retrieval-augmented context such as the plan catalogue?
- 8.4 Follow-up: If the first agent returns both its reasoning and the final plan, would you pass the reasoning to the judge along with the output?
  - 8.4.1 Sub-question: How does passing the generator's reasoning bias the judge toward validating the generator's chain of thought rather than independently evaluating the final output? When, if ever, should the reasoning be passed?
  - 8.4.2 Sub-question: What role does analysing production logs — correlating inputs, outputs, and the reasoning given for undesirable responses — play in deciding what the judge should evaluate and how its prompt should be written?

**9. When running an LLM-as-a-judge alongside a worker model, should the judge be a stronger model, a weaker/smaller model, or the same model as the worker?**

- 9.1 Follow-up: Why not use a weaker or an identical model as the judge? What does the evaluation task demand in terms of reasoning capability, and when might this default change based on the use case?

