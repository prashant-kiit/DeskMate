**What the book says** (Chapter 6, "RAG and Agents" — section *RAG Architecture*, pp. 256–257):

A RAG system has two components, sitting on top of an external memory store:**What the book says** (Chapter 6, "RAG and Agents" — section *RAG Architecture*, pp. 256–257), matching the book's own Figure 6-2:

**Two components sit on top of an external memory source:**

1. **Retriever** — pulls information from external memory. The book gives it exactly two jobs: **indexing** (processing data so it can be retrieved quickly later) and **querying** (sending a query to fetch data relevant to it). How you index depends entirely on how you plan to retrieve later.
2. **Generator** — a generative model that produces a response based on what the retriever hands it.

**The flow:** the user's prompt goes to the retriever, which pulls context relevant to that query from external memory and passes it — along with the original prompt, joined through minor post-processing — to the generative model, which returns the response.

**Design detail the book flags:** in the original 2020 paper, retriever and generator were trained jointly. In today's systems they're usually trained *separately*, often assembled from off-the-shelf parts — though Huyen notes end-to-end finetuning of the whole system can meaningfully improve performance.

**Why chunking exists:** a document can be 10 tokens or a million. Retrieving whole documents naively would make context arbitrarily long, so documents get split into manageable chunks before indexing, and it's chunks — not whole documents — that get retrieved per query. The book treats "document" and "chunk" as interchangeable terms for this reason, borrowing the convention from classical information retrieval.

**One line worth flagging as the book's explicit judgment, not neutral fact:** *"The success of a RAG system depends on the quality of its retriever"* — which is exactly why the chapter devotes far more space afterward to *Retrieval Algorithms* (term-based vs. embedding-based) and *Retrieval Optimization* (chunking strategy, reranking, query rewriting, contextual retrieval) than to the architecture diagram itself.

How it is decided what to fetch?

Retrieval Algorithms?

1. Term Retreival

- Write -> Raw Data is 
  - Chunked into Documents
  - Documents are Ranked based on Scores against a Representative Query 
  - Query Terms and Document are invertedly Indexed in Ranked Order for easy Read operation
- Read -> Documents are
  - Searched using Inverted Index of Query Terms to Document (These Indexes store in About Score also)
  - Documents are Sorted/Reranked and Filtered based in Score as per the Use Case 
  - Selected Documents are Aggregated into a Single Response
- Ranking During Writing
  - Same as Reading just use a Representative Query as per Business Use Case
- Ranking During Reading
  - Inverse Document Frequency for a Term in Query (IDF)
  - Query's each Term Frequency per Unit Length of Document (f)
  - For each Document Find Score (Query, Document) = Find Score(Term, Document) = IDF(Term) * f(Term, Document) for each Term in Query and Sum them all
  - Then Sort then in Desc Order based of the Score
  - Fetch the Documents with Highest Score
  - Here, Document is a Chunk 
  - Example Algo is BM25 (Data Structure used is Inverted Index ie. Term to Document Maps) used in SAAS called ElasticSearch

1. Embedding Retrevial

- Same as Term Retreival plus Embeddings
- Convert Documents to Embedding
- Convert Query to Embeddings
- Term Based Score + Embedding based Score for Ranking and Filtering
- Fetch the Documents with Highest Cumulative Score Score
- Embedding Based Scoring of a Document against at Query is Nearest-Neighbor (NN) problem. Solved by Various NN algorithms

What are the tradeoffs b/w the two retreival methods? When to use VectorDB or Non-VectorDB?

Retrieval Optimization? Chunking? Indexing?

How to eval the RAG? Context Recall and Context Precision? Benchmarks like **MTEB**, which scores embeddings across retrieval, classification, and clustering tasks?

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

