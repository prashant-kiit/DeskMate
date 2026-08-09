# Term based Retreival (Lexical Nature)

## Definition

Given a query, the most straightforward way to find relevant documents is with keywords — some call this **lexical retrieval**. For the query "AI engineering," the system retrieves all documents that contain "AI engineering." It computes relevance at the lexical level — matching appearance, not meaning.

## The two problems it has to solve

**1. Too many documents contain the term.** The context window can't fit all of them. The fix is **term frequency (TF)**: the assumption that the more times a term appears in a document, the more relevant that document is, so you prioritize documents with higher term counts.

**2. Not every term in a query matters equally.** The book's example: "Easy-to-follow recipes for Vietnamese food to cook at home" has nine terms, but "for" and "at" carry far less signal than "vietnamese" and "recipes." The fix is **inverse document frequency (IDF)** — a term's importance is inversely proportional to how many documents contain it. If a term appears in 5 of 10 documents, its IDF is 10/5 = 2; the higher the IDF, the more important the term.

## TF-IDF

Combining both gives the TF-IDF score of document D for query Q:

Score(D, Q) = Σ IDF(tᵢ) × f(tᵢ, D)

summed across the query's terms, where f(tᵢ, D) is how often term tᵢ appears in D.

## Production implementations

- **Elasticsearch** (built on Lucene) — uses an **inverted index**, a dictionary mapping each term to the documents containing it (plus term frequency and document counts), enabling fast lookup.
- **BM25** (Okapi BM25, developed in the 1980s) — a modification of TF-IDF that additionally **normalizes term frequency by document length**, since longer documents naturally accumulate higher raw term counts. BM25 and its variants (BM25+, BM25F) remain widely used and serve as the standard baseline that newer methods like embedding-based retrieval are measured against.