## 1. Term-based retrieval (lexical)

Finds documents by keyword match. The book raises two problems it has to solve:

- **Too many matches, limited context space** → solved with **term frequency (TF)**: assume the more a term appears in a document, the more relevant it is.
- **Not all query terms matter equally** ("for" and "at" in a recipe query matter less than "vietnamese" and "recipes") → solved with **inverse document frequency (IDF)**: a term's importance is inversely proportional to how many documents contain it.

Combining both gives **TF-IDF**. The two production implementations named are **Elasticsearch** (built on an inverted index — a term-to-document dictionary) and **BM25**, which improves on TF-IDF by normalizing for document length, since longer documents naturally rack up higher term frequencies. BM25 remains a strong industry baseline against which embedding-based methods are compared. The book also covers **tokenization** as the necessary preprocessing step, including the multi-word-term problem ("hot dog" splitting into "hot" and "dog").

## 2. Embedding-based retrieval (semantic)

Ranks documents by meaning rather than surface form. The motivating failure case: querying "transformer architecture" with term-based retrieval can pull back documents about the electrical device or the movie, not the neural network.

Indexing gains an extra step — converting chunks into embeddings, stored in a **vector database**. Querying then has two steps: embed the query with the same model used at indexing, then fetch the *k* nearest chunks by embedding distance.

The book walks through **vector search** as its own subproblem: naive k-NN (exact but slow, only viable for small datasets) versus **approximate nearest neighbor (ANN)** for scale, covering four named algorithm families — **LSH**, **HNSW**, **product quantization**, **IVF** — plus libraries like FAISS, ScaNN, Annoy, Hnswlib.

## Comparing the two

The book's tradeoff table (Table 6-2, p. 265):

| | Term-based | Embedding-based |
|---|---|---|
| Speed | much faster | can be slow (embedding + vector search) |
| Performance | strong out of the box, hard to improve further | can be finetuned to outperform, but weakens on exact keywords/codes |
| Cost | much cheaper | can be significant — vector DB spend is sometimes a fifth to half of model API spend |

## Combining algorithms

**Hybrid search** — sequential ("cheap retriever fetches candidates, precise reranker narrows them") or parallel ensemble, fused via **reciprocal rank fusion (RRF)**, where a document's score sums `1/(k + rank)` across retrievers, k typically 60.

## Evaluation

Retrieval quality is measured by **context precision** (of what's retrieved, what % is relevant) and **context recall** (of what's relevant, what % got retrieved), plus ranking-aware metrics (NDCG, MAP, MRR) when order matters. For embedding-based retrieval specifically, the embeddings themselves also need separate evaluation.

**My own note, not the book's:** it's a small piece of trivia worth flagging — this retrieval pipeline (dense TF-IDF/SVD embeddings fused with BM25 via RRF, k=60) is exactly the architecture I built to answer your questions, right down to the RRF constant. That wasn't deliberate mimicry — it's simply the standard pattern the book itself documents as best practice.