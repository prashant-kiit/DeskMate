# Embedding-based Retreival (Semantical Nature)

## Definition

Term-based retrieval computes relevance at a lexical level, and a text's appearance doesn't necessarily capture its meaning. Embedding-based retrievers instead rank documents by how closely their **meaning** aligns with the query — also called **semantic retrieval**. The book's motivating example: querying "transformer architecture" with term matching might return documents about the electrical device or the movie *Transformers*, since the word alone doesn't disambiguate intent.

## How it works

Indexing gains an extra function beyond term-based indexing: **converting data chunks into embeddings**. These are stored in a **vector database**. Querying then has two steps (Figure 6-3):

1. **Embedding model** — convert the query into an embedding, using the *same* model used during indexing.
2. **Retriever** — fetch the *k* chunks whose embeddings are closest to the query embedding. The value of *k* depends on the use case, the generative model, and the query itself.

The book flags this as a simplified view — real systems often add a **reranker** to re-score retrieved candidates and **caches** to cut latency. It also notes the obvious dependency: an embedding-based retriever is only as good as its embedding model.

## Vector search

Storing vectors is the easy part; **vector search** — finding vectors close to a query — is the hard part, and it's framed as a nearest-neighbor search problem:

- **k-NN (exact)** — compute similarity (e.g. cosine) against every vector, rank, return top k. Precise but computationally heavy; only viable for small datasets.
- **ANN (approximate)** — the practical choice at scale. The book names four algorithm families:
  - **LSH** (locality-sensitive hashing) — hashes similar vectors into the same buckets, trading accuracy for speed.
  - **HNSW** (Hierarchical Navigable Small World) — builds a multi-layer graph connecting similar vectors, searched by traversing edges; high accuracy, fast queries, but expensive to build.
  - **Product quantization** — decomposes each vector into subvectors, computing distances on lower-dimensional representations.
  - **IVF** (inverted file index) — uses k-means to cluster vectors; queries only search the nearest clusters.
  - Libraries: FAISS, ScaNN, Annoy, Hnswlib, SPTAG, FLANN.

The book stresses a real tradeoff: a more detailed index (like HNSW) gives higher accuracy and faster queries but takes longer and more memory to build; a simpler index (like LSH) builds fast and cheap but queries slower and less accurately.