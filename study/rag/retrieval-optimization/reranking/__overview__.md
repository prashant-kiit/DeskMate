# What reranking is
The initial ranking a retriever produces isn't necessarily the final word — reranking takes those results and reorders them to be more accurate. 

----

## Use Case
- reranking is especially useful when you need to **reduce the number of retrieved documents**, either to fit within the model's context window 
- to cut down input token cost.

----

## Core pattern

***Term Based + Embedding Based Search and Reranker***
1. **Term Based** : cheap eg: BM25
2. **Embedding Based** : expensive eg: k-nearest neighbors

* Term -> Embedding Based (Mostly used as It Meaning Focussed): It will go less concise to more concise. For example:
    - **The "transformer" example:** term-based retrieval fetches every document containing the word "transformer" — the electrical device, the neural network architecture, the movie, all mixed together. Vector search then reranks *within that already-narrowed set* to surface the ones actually about the neural architecture.
    - **"Who's responsible for the most sales to X?"** — first fetch everything containing keyword X, then use vector search to rerank by relevance to the actual question being asked ("who's responsible for the most sales").

***LOGIC: The economic logic is straightforward: running an expensive, precise method (like a full embedding-based nearest-neighbor search, or an even heavier cross-comparison model) over your *entire* corpus would be costly. Running it only over a much smaller, pre-filtered candidate set — the output of the cheap first pass — gets most of the precision benefit at a fraction of the cost.***

* Embedding -> Term (Rarely used as It Term Focussed)

----

## Time-based reranking

Giving higher weight to more recent documents. For Example:
- News aggregation
- Chatting with your own emails (a chatbot answering questions about your inbox)
- Stock market analysis

***LOGIC: relevance genuinely decays with time***

----

## How Intermediate reranking differs from Final reranking

The book draws a sharp, explicit distinction here that's easy to miss:

- **Final reranking**:
    * For Humans
    * Exact position and Inclusion both critical
    * eg: Human user reads results top-to-bottom and often stops after the first few

- **Intermediate reranking** 
    * For Models/Machine
    * Inclusion is more critical than exact position
    * eg: That models tend to understand documents positioned at the **beginning and end** of the context better than those buried in the middle.

----

## How this connects to fusion (RRF)

Reranking via the cheap→expensive pattern is the *sequential* combination approach. The book also describes a *parallel* alternative — running multiple retrievers simultaneously and fusing their independent rankings via **reciprocal rank fusion (RRF)**:

$$\text{Score}(D) = \sum_{i=1}^{n} \frac{1}{k + r_i(D)}$$

where a document's final score sums `1/(k + rank)` across every retriever `i` that ranked it, and `k` (typically 60) dampens the influence of low-ranked results. A document ranked 1st by one retriever and 2nd by another scores `1/(60+1) + 1/(60+2) ≈ 0.0328`, using the book's stated typical k.

**My own note connecting this to something you already know:** RRF with k=60 is exactly the fusion method I'm using to answer your questions across this whole knowledge base — it's the book's own recommended default, not a coincidence.