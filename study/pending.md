# PENDING TOPICS

* Combining retrieval algorithms.
* RAG generator step
* Mukul Raina
* AI System Design of projects in Resume. 
* One Indepth Project Design for each: 
RAG, Multi-Agent & Communication, Memory, MCP, Eval, Fine Tuning, Prompting & Looping, DataSets (MetaData etc.), Optimizations
* Later: LLM and Vector DB Internals

Based on our conversation so far, here's what's left within the *RAG* section of Chapter 6 (pp. 253–275):

**From Retrieval Optimization (partially covered — only Chunking strategy done):**
1. Reranking
2. Query rewriting
3. Contextual retrieval

**From RAG Beyond Texts (not yet covered):**
4. Multimodal RAG
5. RAG with tabular data (text-to-SQL)

**Also touched only briefly, not detailed:**
6. Combining retrieval algorithms / Hybrid search (sequential and parallel patterns, reciprocal rank fusion)
7. Evaluating retrieval solutions (the practical checklist for picking a retrieval system)
8. Context precision and context recall (retrieval evaluation metrics)
9. Finetuning and RAG (the book's explicit decision framework in Chapter 7, only lightly referenced so far)

If you also want the rest of Chapter 6 — since the chapter is titled "RAG and Agents" and RAG is formally positioned as a special case of agents — those unexplored sections are:

10. Agent Overview
11. Tools
12. Planning
13. Agent Failure Modes and Evaluation
14. Memory

----

How to eval the RAG? Context Recall and Context Precision? Benchmarks like **MTEB**, which scores embeddings across retrieval, classification, and clustering tasks?

What are Vector normalize embeddings?

How Probalility is used for Next Token Prediction?

Core AI Questions:

- How LLM and VectorDB works? 
- How tokenization of the Query or External Data happens inside LLM?
- Deep Dive in BM25 and NN Search

Core AI Topics/Hints:

- Tokenization. Eg: Split the String by WhiteSpace
- Make a Parse Tree ie. AST
- LLM -> Transformer -> Layers of Neural Network; NL ares Complex Decision Trees with Weights and Biases
- Entity, Parameters, Matrix row, Vector
- Tokenization -> Attention -> FeedForward -> Tokenization ... Recursive nature like DFS or BFS in Graphs
- In Vector DB, Graphs and Vectors both are Matrix based and can represent each other
- Matrix - C++ Vectors of C++ Vectors
- Value in Vectors are Humana Annotated (DataSet Engineering)
- Dimensions in Vectora are Human Curated (DataSet Engineering)
- These Values and Dimensions require a Bases to Bootstrap the Data Prep and Training, Thus Human Bias is embedded in Models
- These can be mutiple parallel biases embedded and Ranking of results depend on fusion of that
- These Vectors are stored in VectorDB of LLM as Dots, 
- Join Dots to make Lines, Join Lines to makes Planes, Join Planes to 3D Shapes
- Dots, Lines, Planes and Shapes have Weights and Biases (As per Geometry) That is represented in values and dimensions in Vectors
- Relatioship among Dimensions are also Vectors
- After Feed Forwarding the result trasnforms the Weights and Biases in Vector Space, Self Validates itself. Thus the top results get topper and low resulter get lower and thus even same query next time give the same but still different response 

Notes of AI Agent and RAG:
* Overiew
    * Document <-> DB: Indexed (SQL + Vector) <-> Filter (Human Bias Threshold or Time) <-> Sorted (Similarity/Comparsion: BM25 + NN) <-> Chunk (Term + Embedding) 
    * Lexicality or Semantics or Both: Lexical -> Semantics 
        * Sequentially
        * Parallelly
        * Result Fusion 

* Flow for RAG:
    * Request Contract
    * Chunk + MetaData
    * Sort & Filter
    * Insert
    * Index
    * Search
    * Sort & Filter
    * DeChunk + Metadata
    * Request Contract
    * ... cylce continues

* Agent Architecture:
    * Prompt (User + System) - Response
    * Prompt (User + System) - Plan - Response  
    * Prompt (User + System) - Plan - COT - Step1 - Step2 - …- Response  
    * Prompt (User + System) - Plan - COT - Step1 - Tool1 - Step2 - Tool2 …- Response
    * Prompt (User + System) - Plan - COT - Step1 - Tool1 (Context) - Step2 - Tool2 (Context) …- Response
    * Prompt (User + System) - Plan - COT - Agent1 (Context) - Agent2 (Context)… - Response
        * Agent1  : Step1 - Tool1 (Context) - Step2 - Tool2 (Context)…
        * Agent2  : Step1 - Tool1 (Context) - Step2 - Tool2 (Context)…
    * Prompt (User + System) - Plan - COT - Agent1 (Context) - Agent2 (Context)… - Response
        * Agent1  : Step1 - Tool1 (Determinitics-Context+Metadata) - Step2 - Tool2 (Indeterminitics-Context+Metadata)…
        * Agent2  : Step1 - Tool1 (Indeterminitics-Context+Metadata) - Step2 - Tool2 (Determinitics-Context+Metadata)…

* Tools 
    * Read + Write Agent
    * Read Only Agent (RAG)
    * Write Only  Agent