# Answer Key — AI Engineer Interview Question Bank

Brief study answers, in original question order.

---

## Section A — RAG Architecture & Vector Retrieval

### 1. End-to-end RAG pipeline

**Ingestion** → loaders per format (PDF via PyMuPDF/Unstructured, OCR for scans, HTML/DOCX parsers). Extract text + layout + metadata (source, page, section, date, access tags).

**Chunking** → structure-aware splitting (heading/section boundaries) with a token target (~300–800 tokens) and 10–15% overlap. Keep tables/code as atomic units. Attach parent-doc IDs for parent-document retrieval.

**Embedding** → batch encode chunks with a dense model (e.g. `text-embedding-3-large`, BGE, E5). Normalize vectors if using cosine. Store the embedding version so you can re-index on model change.

**Storage** → vector DB (Qdrant/pgvector/Milvus/Weaviate) with the vector, the raw chunk text, and filterable metadata payload. Index type: HNSW.

**Retrieval** → embed query, ANN top-k (k ≈ 20–50) with metadata pre-filters; usually hybrid with BM25.

**Reranking** → cross-encoder (bge-reranker, Cohere Rerank) over the candidate set, cut to top 3–8. This is where most of the precision comes from.

**Generation** → assemble prompt with the reranked chunks + citations, instruct grounding ("answer only from context"), generate, post-check for citation validity.

**Around it all** → eval harness (recall@k, faithfulness, answer relevance), logging, and an incremental re-indexing job.

---

### 1.1 Which ANN algorithm and why

**HNSW**, because it gives the best recall-vs-latency curve at the corpus sizes typical of RAG (10⁵–10⁷ vectors), supports incremental inserts (documents arrive continuously), and needs no training step. IVF-PQ is the alternative when RAM is the binding constraint — it compresses, but costs recall and requires a training pass. Flat/exhaustive is fine below ~50k vectors.

#### 1.1.1 How HNSW works internally

- Each **vector is a node**; **edges** connect a node to its approximate nearest neighbours. The result is a proximity graph — a "small world" where any node is reachable from any other in few hops.
- **Layering:** each node gets a maximum layer drawn from an exponentially decaying distribution (`floor(-ln(unif(0,1)) · m_L)`). So layer 0 holds *all* nodes with dense connectivity; each higher layer holds an exponentially smaller random sample with long-range links. It is a probabilistic skip-list generalised to a graph.
- **Traversal (search):** start at the single entry point in the top layer. Greedily hop to whichever neighbour is closer to the query; when no neighbour improves, drop to the next layer down using the current node as entry. Repeat. At layer 0, run a best-first search maintaining a candidate heap of size `efSearch`, and return the top-k.
- Top layers do **coarse, long-distance navigation** (zoom-in); layer 0 does **fine-grained local refinement**.
- Build parameters: `M` (edges per node), `efConstruction` (candidate list size at insert). A pruning heuristic keeps edges *diverse* in direction rather than just nearest, which preserves graph connectivity and avoids clusters becoming unreachable.

#### 1.1.2 HNSW vs exhaustive scan

- Exhaustive (flat) search is **O(N·d)** per query — every vector compared. Exact but linear.
- HNSW is roughly **O(log N)** hops with a constant factor from `efSearch` and `M`. In practice: milliseconds vs hundreds of milliseconds at millions of vectors.
- **Trade-off:** it's *approximate* — recall is typically 95–99%, not 100%. Some true nearest neighbours are missed when greedy descent lands in a local minimum. Recall is tunable via `efSearch` (higher = slower = more accurate). Costs: high memory (graph stored in RAM, ~`M·2·4` bytes/node overhead) and expensive deletes.

#### 1.1.3 How LSH works

- Family of hash functions where **collision probability increases with similarity**. For cosine similarity, the standard construction is **random hyperplane projection (SimHash)**: draw random vectors `r₁…r_b`; each bit of the hash is `sign(r_i · v)` — i.e. which side of that hyperplane the vector falls on.
- Vectors close in angle almost always land on the same side of a random hyperplane, so they share hash bits and land in the **same bucket**.
- Query time: hash the query, retrieve only its bucket(s), then do exact distance computation on that small candidate set.
- To control recall you use **L independent hash tables of b bits each** and union the buckets — more tables = higher recall, more memory.

#### 1.1.4 Why HNSW over LSH in production

- **Better recall at equal latency.** LSH is data-agnostic (random partitions ignore the actual distribution); HNSW's graph is built *from the data*, so it adapts to clustered, non-uniform embedding spaces.
- LSH needs many hash tables to reach high recall → memory blows up, and tuning `b`/`L` is fiddly and dataset-specific.
- **Bucket-boundary problem:** two near-identical vectors can fall on opposite sides of a hyperplane and never collide. Graph search has no hard partitions.
- HNSW degrades gracefully in high dimensions (768–3072); LSH's guarantees weaken and candidate sets get noisy.
- Ecosystem: HNSW is the default in essentially every vector DB, with mature filtering support. LSH remains attractive mainly for near-duplicate detection and billion-scale dedup where cheap binary codes matter more than recall.

#### 1.1.5 Basis of small-world construction & what leads to the next level

- **Construction:** when a node is inserted, its layer is assigned randomly (exponential decay). At each layer from its top down, a greedy search finds the `efConstruction` closest existing nodes; the pruning heuristic selects `M` of them as edges, favouring a *diverse* set of directions over the strictly nearest. Small worlds therefore form on **vector-space proximity**, not on any semantic label.
- **What leads deeper:** at each layer the search greedily moves to the neighbour with smallest distance to the query. The node where greedy descent **stops improving (the local minimum of that layer)** becomes the entry point for the layer below. So it is purely distance-to-query that determines the descent path.

---

## Section B — PII / PHI Redaction

### 2. Multi-modal redaction pipeline design

Layered defence, optimised for **recall** (missing PII is unacceptable; over-redaction is merely annoying):

1. **Normalise input** — PDF → text + bounding boxes (PyMuPDF); scans/images → OCR (Tesseract/PaddleOCR) with coordinates; plain text as-is. Keep offsets so you can redact the *original* rendering too.
2. **Detection ensemble** (union of signals, not a single model):
   - **Deterministic patterns:** SSN, MRN, phone, email, dates, insurance IDs, Aadhaar/PAN — regex + checksum validation (Luhn, verhoeff) to cut false positives.
   - **Gazetteer / known-values match** against your Postgres tables (patient names, doctor names, addresses) — fuzzy, not exact.
   - **Statistical NER** (CPU model) for PERSON / ORG / LOC / DATE / AGE — catches entities not in your DB.
   - **Context rules:** labels like `Patient:`, `Dr.`, `DOB:`, form-field proximity, table headers. Very high precision in structured documents like prescriptions.
3. **Merge & resolve spans** — union overlapping spans, take the widest, assign entity type and confidence.
4. **Redact** — replace with typed, stable placeholders (`<PERSON_1>`, `<MRN_1>`) and store the mapping in an encrypted vault keyed by request ID. Never send the mapping to the LLM.
5. **Egress guard** — a final regex/NER pass on the *outgoing payload* as a hard gate; block if anything high-risk survives. This is your last line of defence.
6. **Call the LLM**, then **re-hydrate** placeholders in the response inside your environment.
7. **Feedback loop** — sample outputs, human-review, add misses to gazetteers/rules, track recall per entity type.

**On the 90% target:** treat it as a *per-entity-type* recall SLO, not a global one. Structured identifiers (SSN, MRN) should be ~99% via regex; free-text names are the hard tail. Deliberately bias thresholds toward over-redaction, and reserve the residual risk for low-severity types.

**2.1 — Span-level redaction, not chunk blocking.** Redact only the detected character spans and keep everything else. Use *typed, consistent* placeholders so downstream meaning survives: "Patient `<PERSON_1>` was prescribed 500 mg metformin twice daily" still summarises perfectly. Consistency matters — the same person must map to the same token throughout the document, or coreference breaks. Also: embed and index the **redacted** text so the vector store never holds PII, and rehydrate only at the presentation layer for authorised users. Pseudonymisation (swapping in realistic fake names) preserves fluency better than `[REDACTED]` blocks, which distort embeddings.

**2.2 — No exact string match (initials, abbreviations).**
- Normalise both sides: lowercase, strip punctuation/titles, unify diacritics, sort tokens.
- **Fuzzy matching:** Levenshtein / Jaro-Winkler for typos and OCR errors; Jaro-Winkler is good for names because it weights prefix agreement.
- **Phonetic keys:** Soundex, Metaphone, NYSIIS — catches Kaur/Kour, Mohammed/Muhammad.
- **Initial expansion:** generate variants of every known name (`Rajesh Kumar` → `R. Kumar`, `R.K.`, `Kumar R`) and index those forms too; match `X. Surname` patterns against the surname alone.
- **Blocking + scoring:** use a cheap key (surname, Soundex, first letter + DOB) to shortlist candidates, then score with the expensive metric. Keeps it O(candidates) not O(table).
- **Context wins where matching fails:** if the token follows `Patient:` on a prescription, redact it regardless of whether it's in your DB. Position/label is a stronger signal than string identity.

**2.3 — Limits of embedding similarity for PII detection.**
- Embeddings encode **topical/semantic similarity, not identity or category membership.** "John Smith" and "Michael Jones" are near-neighbours because both are *name-like*, which tells you the **type** but never whether a specific span is sensitive.
- There is **no meaningful "negative similarity search."** Cosine distance gives you a ranking, not a decision boundary; "far from known PII" does not imply "not PII."
- **Granularity mismatch:** embeddings are computed over chunks/sentences, but redaction needs exact character spans. You cannot recover span boundaries from a chunk vector.
- **Threshold instability:** the similarity cut-off that works for one document type fails on another; no calibrated probability.
- **Discrimination failure:** the vector for a drug name, a doctor name and a hospital name may sit in overlapping regions — high false positive *and* false negative rates.
- **Verdict:** embeddings are usable as a weak *auxiliary* signal (e.g. clustering candidate spans, semantic type hints), never as the primary detector. Detection is a token-classification problem, not a retrieval problem.

**2.4 — Unknown entities not in your database.**
This is exactly why the gazetteer alone is insufficient and a **model-based NER layer is mandatory**. It generalises from *context*, not memorisation:
- Sequence labellers learn that "prescribed by Dr. ___", "signed, ___, MD", "referred to ___ Hospital" produce a PERSON/ORG regardless of the specific string.
- **Orthographic features** carry a lot: capitalisation pattern, word shape (`Xxxxx`), suffixes (`-son`, `-kumar`, `Ltd`, `Inc`, `Hospital`, `Clinic`), title prefixes.
- **Structural cues:** anything in a form field labelled `Name`, `Prescribed by`, `Address` is sensitive by position.
- **Format-based detection** for identifiers you've never seen — a 10-digit string next to "Phone" is a phone number regardless of whose it is.
- **Fail-safe policy:** for high-risk document classes, redact *any* detected PERSON/ORG/LOC span whether or not it resolves to a known record. Unknown ≠ safe.

**2.5 — No GPU, no LLM: which model class?**
- **Rules + regex engine** for structured identifiers — near-free, highest precision.
- **CRF (Conditional Random Fields)** over hand-engineered token features — the classic NER workhorse, trains in minutes on CPU, sub-millisecond inference, and handles label transitions (B-PER → I-PER) properly.
- **spaCy small/medium pipelines** (`en_core_web_sm`) — CNN-based, CPU-native, ~10k words/sec.
- **Distilled + quantised transformers** if you need more accuracy: DistilBERT/MiniLM NER exported to **ONNX Runtime with INT8 quantisation** — comfortably real-time on CPU for document-sized inputs.
- **Linear models** (logistic regression / linear SVM) over sparse features for binary "is this token sensitive" classification.
- **Microsoft Presidio** as the ready-made orchestration framework combining all of the above.
- Practical stack: regex + gazetteer + spaCy/CRF, ensembled by union, ONNX model only for the hard free-text cases.

**2.5.1 — Non-semantic vectors (bag-of-words) for CPU entity recognition.**
Embeddings need not be semantic — any deterministic map to ℝⁿ is an embedding.
- Build a **sparse feature vector per token** using a sliding window: the token itself, ±2 neighbouring tokens, character n-grams (3–5), word shape, capitalisation flags, is-digit, prefix/suffix, gazetteer-membership flag, position in line.
- Encode via **CountVectorizer / TF-IDF / HashingVectorizer** — the hashing trick avoids storing a vocabulary and keeps memory fixed.
- Feed the sparse vector to a **linear classifier or CRF** for BIO tagging.
- Why it works: PII detection depends heavily on **surface form and local context**, not deep semantics. "Dr." followed by a capitalised out-of-vocabulary token is a strong lexical pattern that BoW features capture directly.
- Costs: sparse matrix ops are extremely fast on CPU, fully interpretable (you can inspect which features fired), retrainable on a laptop. Limitation: no generalisation to unseen surface forms beyond the n-gram level, and no long-range context.

---

## Section C — Recommendation Engine Design

### 3. Design and internal flow

**Item attribution** — every post is tagged at creation with structured attributes (business domain, region, content type, language, author, freshness) plus derived tags from a classifier. Stored in Postgres with a tag/attribute join model.

**Activity logging** — event stream (Kafka/queue) of impressions, clicks, dwell time, saves, shares, follows, explicit dislikes. Written to an events table + aggregated into a user-preference profile (weighted attribute affinity vectors with time decay).

**Candidate generation** — pull a few hundred candidates cheaply from several sources: attribute match against the user profile, trending/popular in region, followed authors, collaborative-filtering neighbours, and an exploration slice.

**Filtering** — hard business rules: already-seen, blocked authors, geo/language eligibility, moderation status, recency window.

**Ranking** — score candidates by a weighted combination (or a learned model) of preference match, engagement prediction, recency, and author quality.

**Post-processing** — dedupe, diversity/MMR so the feed isn't monotone, pinning/boosting rules, pagination.

**Serving + feedback** — cache the ranked feed per user with short TTL; log what was shown so the loop closes and metrics (CTR, dwell) feed the next model version.

**3.1 — Did you consider vectors instead of relational filtering?**
Yes — the relational approach requires an attribute table per dimension and increasingly expensive multi-way joins as attributes grow, and it produces **boolean** matches with no natural ordering. A vector formulation collapses all attributes into one similarity computation and gives graded ranking for free. The pragmatic answer is hybrid: relational/metadata filters for *hard constraints* (region eligibility, moderation), vector similarity for *soft preference ranking*.

#### 3.1.1 Constructing the vector and using Euclidean distance

- **Encoding:** one-hot each categorical attribute and concatenate → e.g. domain (12 dims) + region (8) + content type (5) = 25-dim vector. Multi-valued attributes become multi-hot. Numeric attributes (freshness, popularity) are min-max scaled into a single dim.
- **User vector:** same layout, but values are *affinity weights* — the time-decayed, normalised frequency with which the user engaged with each attribute value. So a user vector is a soft distribution rather than a one-hot.
- **Weighting:** scale each attribute block by an importance coefficient (`domain × 3`, `region × 2`, `content type × 1`) before the distance is computed — this is how you encode "domain matters more than format."
- **Retrieval:** index post vectors in a vector store, query with the user vector, take k nearest by Euclidean (or cosine) distance.
- **Note:** on binary one-hot blocks, squared Euclidean distance is exactly proportional to weighted Hamming distance — i.e. "number of attributes that disagree." Cosine is usually preferable once magnitudes vary, since it ignores the number of active tags.

#### 3.1.2 Does vectorising deterministic attributes lose exactness?

**No, not inherently.** If the encoding is injective (one-hot is), the vector carries exactly the same information as the row — you can reconstruct the attributes from it. The mapping is deterministic and lossless.

What *does* introduce inexactness:
- **Lossy encodings** — hashing/feature-hashing collisions, dimensionality reduction (PCA), or learned embeddings that compress.
- **Weighting and aggregation** — once you sum attribute contributions into one scalar distance, you can no longer tell *which* attribute mismatched. Two posts can tie at equal distance for entirely different reasons.
- **ANN approximation** — HNSW/IVF may miss exact nearest neighbours.

The deeper point is a **change of semantics, not a loss of precision**: relational filtering answers "does this match?" (boolean), vector search answers "how close is this?" (ranked). For hard constraints you still want the exact predicate — which is why you keep them as metadata filters in the vector DB rather than folding them into the distance.

#### 3.1.3 Embedding *model* vs embedding *function*

| | Embedding model | Embedding function |
|---|---|---|
| Origin | Learned parameters from training data | Hand-written deterministic rule |
| Captures | Latent semantics, generalises to unseen inputs | Only what you explicitly encode |
| Dimensions | Uninterpretable | Each dim has a known meaning |
| Cost | Inference (GPU/CPU), model versioning, re-indexing on upgrade | Free, stable forever |
| Failure mode | Drift, opacity, unexpected neighbours | Brittle to new attribute values |

**Embeddings need not be semantic** — an embedding is simply a map from an object to a vector such that geometry encodes a relationship you care about. One-hot, TF-IDF, count vectors, colour histograms, audio spectrograms and graph node2vec vectors are all embeddings. "Semantic embedding" is one special case where the geometry encodes *meaning*, learned from data. When your attributes are already known and categorical, a hand-written function is often *better*: no training data needed, fully explainable, zero inference cost, and no drift.

#### 3.1.4 Advantages of a vector store with attribute vectors over relational filtering

- **One index instead of N tables** — no join explosion as attributes multiply; adding an attribute is adding dimensions, not a schema migration plus a join.
- **Graded ranking, not boolean sets** — you always get a *best* answer, even when nothing matches perfectly. Relational filtering returns an empty set and you have to hand-write fallback query relaxation.
- **Swappable distance metrics** — cosine for direction-of-preference, Euclidean for magnitude-sensitive matching, dot product for popularity-weighted scoring, Manhattan for robustness to outlier dims. Same data, different behaviours, no re-modelling.
- **A substrate for ML** — once items live as vectors you can run KNN, k-means clustering for segment discovery, a logistic-regression or Bayesian classifier over the same representation, or train a small ranker at runtime. Rows in a join don't give you that.
- **Sub-linear retrieval at scale** — ANN is O(log N) vs increasingly expensive multi-predicate scans.
- **Room to grow into learned embeddings** — you can later replace hand-written dims with learned ones without changing the retrieval architecture.
- **Caveat:** you lose transactional guarantees, exact aggregate queries, and easy explainability ("why was this shown?"), which is why production systems keep both.

#### 3.1.5 Should AI be reserved for non-deterministic problems?

No. The relevant question is not "is the data deterministic?" but **"is the objective specifiable as a rule?"** A post's attributes are deterministic, but *how much a given user will like it* is not — that's a learned preference, and small statistical models are the right tool.

- **KNN** — natural fit for the vector formulation; no training, instant updates, interpretable ("similar to these 5 items you liked").
- **Linear/logistic classifiers** — cheap, calibrated probabilities for CTR-style scoring, easy to inspect coefficients.
- **Naive Bayes / Bayesian networks** — good for sparse categorical data, handle uncertainty explicitly, work with little data.
- **Decision trees / gradient boosting** — often beat deep models on tabular attribute data.

Sensible division of labour: **deterministic rules own the hard constraints** (eligibility, compliance, moderation, business rules — these must never be probabilistic), and **small ML models own the soft ordering** (relevance, tie-breaking, personalisation, exploration). Reaching for an LLM here would be a mistake — wrong cost, wrong latency, wrong reliability profile. The principle is to use the smallest model that captures the uncertainty actually present in the problem.

---

## Section D — Hybrid Search

### 4. Hybrid search implementation

Yes — **BM25 (lexical) + dense vector (semantic)**, run in **parallel**, results fused by rank. Vector search catches paraphrase and conceptual matches; BM25 catches exact identifiers, product codes, rare proper nouns and acronyms that embeddings smear together. Each retrieves top-k (k ≈ 50), the union is fused, then a **cross-encoder reranks** the top ~30 down to the final 5–8. Metadata filters apply to both legs identically.

**4.1 — Sequential vs parallel, and how fusion works.**
**Parallel.** Both retrievers see the *full* corpus independently, so neither can cap the other's recall.

**Reciprocal Rank Fusion (RRF)** is the standard fusion method:

```
score(d) = Σ_over_retrievers  1 / (k + rank_i(d))      # k ≈ 60
```

Why RRF specifically:
- It uses **ranks, not raw scores**, so you never have to normalise BM25's unbounded scores against cosine's [-1, 1] — a normalisation that is notoriously unstable across queries.
- A document missing from one list simply contributes nothing from that leg; it is **not penalised**. So a chunk ranked #1 by vector search and absent from BM25 still surfaces strongly.
- The constant `k` damps the influence of top ranks, preventing one retriever from dominating.

The alternative is **weighted score fusion** (`α · norm(dense) + (1−α) · norm(bm25)`), which lets you tune the semantic/lexical balance per domain but requires per-query score normalisation (min-max or z-score over the result set) and is more brittle. Use RRF as the default; use weighted fusion when you have eval data to tune α.

### 5. Which lexical algorithm

**BM25 (Okapi BM25)** — via Elasticsearch/OpenSearch, or Postgres `tsvector`/`ts_rank`, or `rank_bm25` for small corpora. It improves on raw TF-IDF with term-frequency saturation (the 20th occurrence of a word adds almost nothing) and document-length normalisation. Qdrant/Weaviate now ship native sparse-vector BM25 support, which keeps everything in one store.

**5.1 — Exact vs fuzzy matching.**
The base layer is **analysed exact matching**: lowercasing, stemming/lemmatisation, stopword removal, synonym expansion at index time. Not naive "contains" — substring matching produces false positives (`cat` in `catalogue`) and misses morphology.

**Fuzzy matching (Levenshtein / edit distance)** is worth adding when:
- **User-typed queries with typos** — search boxes, chat interfaces.
- **OCR'd corpora** — scanned documents contain systematic character confusions (`rn` → `m`, `0` → `O`).
- **Proper nouns, names, drug names, place names** — high variant density and no stemmer helps.
- **Morphologically rich or transliterated languages** where stemming is weak.
- **Product codes / SKUs** where a single character differs.

Practical configuration: `fuzziness: AUTO` in Elasticsearch (edit distance 0 for short terms, 1 for medium, 2 for long) with a **prefix_length of 1–2** so the first characters must match — this keeps the candidate set small and precision acceptable. Avoid fuzzy on every term: it is expensive (automaton expansion over the term dictionary) and dilutes precision. Prefer exact matching when the corpus is clean, machine-generated, or when identifiers must match precisely.

### 6. Weaknesses of lexical-first-then-vector (cascading)

The fundamental flaw: **the first stage sets a hard recall ceiling.** Vector search can only rerank what BM25 already found; it can never *recover* a relevant chunk that lexical retrieval missed. You have turned a high-recall semantic retriever into a reranker.

Specific failure modes:
- **Vocabulary mismatch** — query and corpus express the same concept in different words → lexical returns nothing relevant → the semantic stage is given garbage.
- **Empty candidate set** — zero lexical hits means zero context, and the LLM either refuses or hallucinates.
- **Short/conceptual queries** — "how do I improve retention?" shares no distinctive terms with the answer chunk.
- **Stopword-dominated queries** — after analysis almost no meaningful terms remain to match on.
- **Popularity bias** — BM25 favours chunks that repeat the query term, which are often boilerplate rather than the substantive answer.
- **Filter-set size sensitivity** — if you cap the lexical stage at top-50, semantically ideal chunks at lexical rank 200 are invisible.
- Latency is genuinely *better* in this design (you only embed-compare a subset) — the cost is entirely in **recall**, which is the wrong thing to trade away in RAG.

**6.1 — Which scenarios lose context (vs merely add latency).**
- Synonyms and near-synonyms (`heart attack` / `myocardial infarction`).
- Abbreviations and acronyms (`BP` / `blood pressure`, `MI` / `myocardial infarction`).
- Layman vs domain jargon (`stomach ache` / `abdominal pain`).
- Paraphrased or question-form queries where the corpus is declarative.
- Cross-lingual or transliterated content.
- Misspellings and OCR noise on either side.
- Conceptual/thematic queries with no lexical anchor at all ("what are the risks here?").
- Coreference — the answer chunk says "the drug" while the query names it explicitly.
- Multi-hop questions where the relevant chunk shares terms with an *intermediate* concept, not the query.

**6.2 — Corpus says "influenza", user queries "flu".**
In the cascading design, BM25 for `flu` matches nothing (different token, and no stemmer relates the two) — so the candidate set is empty or filled with incidental matches. The vector stage then runs over a candidate set that **does not contain the influenza chunks**, so the correct context is never retrieved. The LLM receives no grounding and either declines or fabricates. Note the vector retriever *alone* would have handled this trivially, since `flu` and `influenza` are near-neighbours in embedding space — the architecture actively destroyed a capability the system already had. Same story for a typo (`influenzza`) or an abbreviation.

**6.3 — Mitigations beyond parallel + summed rank fusion.**
The problem with naive **summed** rank fusion is exactly as stated: adding a bad lexical rank to a good vector rank drags the chunk down. Fixes:

- **Use RRF, not rank summation.** RRF's `1/(k+rank)` is bounded and a document absent from the lexical list contributes zero rather than a large penalty. A #1 vector hit survives lexical failure.
- **Union, don't intersect.** Take the top-k of *each* retriever unconditionally, then rerank the union — guarantees the vector leg's best hits always reach the reranker.
- **Max-score / Borda fusion** instead of sum, so the strongest single signal wins.
- **Cross-encoder reranking over the union** — the reranker actually reads query and chunk together, so it corrects fusion mistakes. This is the single highest-leverage addition.
- **Widen the vector search space:** raise `k` and `efSearch`, retrieve 100+ candidates before reranking, and use **MMR** to keep the widened set diverse rather than redundant.
- **Synonym / abbreviation dictionaries** applied at index time and query time — the cheap deterministic fix for the influenza case, essential in medical, legal and telecom domains.
- **Multi-query retrieval** — generate 3–5 query variants, retrieve for each, fuse all result sets.
- **HyDE** — have the LLM write a hypothetical answer, embed *that*, and search with it; it matches the corpus's register far better than a short question does.
- **Fallback logic** — if lexical returns < N results or fusion confidence is low, fall through to pure vector search with a larger k.
- **Parent-document / sentence-window retrieval** — retrieve on small precise chunks but return their surrounding parent, so partial matches still deliver full context.
- **Fine-tune the embedding model** on domain query–passage pairs so `flu`/`influenza` are tight in *your* space.

**6.4 — LLM query expansion (expansion, not rewriting).**
Take `flu` → `flu, influenza, viral respiratory infection, seasonal flu, grippe` while **retaining the original query terms**. Effects:

- **Lexical recall** rises directly — BM25 now has `influenza` as a searchable token and hits the chunk it previously missed.
- **Dense recall** rises too — the expanded string embeds closer to the corpus's phrasing, and you can issue each variant as a separate probe and fuse (multi-query retrieval).
- **Bridges register gaps** — layman ↔ clinical, abbreviation ↔ expansion, colloquial ↔ formal.
- **Why expansion beats rewriting:** rewriting *replaces* the query and can drift from user intent — the model may resolve an ambiguity wrongly and you lose the original signal irrecoverably. Expansion is additive and monotone: the original terms are still there, so worst case you add some noise; best case you recover the missing chunk. It is a strictly safer operation.
- **Costs and controls:** adds an LLM call (~200–500 ms) before retrieval — mitigate with a small fast model, caching of common queries, and doing it only when initial retrieval confidence is low. Cap the number of added terms (over-expansion dilutes precision), and constrain the model to domain-appropriate synonyms via a prompt or a curated ontology. Reranking afterwards cleans up any precision loss.

---

## Section E — Conversational Memory Architecture

### 7. Memory architecture for unbounded conversations

Four tiers, assembled into a **fixed token budget** every turn:

1. **Hot / rolling window** — the last N turns verbatim (e.g. 10–20 messages, ~2–4k tokens). Preserves exact recent phrasing, code, and conversational flow.
2. **Warm / running summary** — a rolling summary of everything evicted from the window, updated incrementally in the background rather than regenerated from scratch.
3. **Cold / retrievable archive** — every turn stored in Postgres (source of truth) and chunked + embedded into a vector store, tagged with conversation ID, turn index, timestamp, topic segment. Retrieved on-demand by semantic search against the current query.
4. **Structured facts** — an extracted key–value/graph store of durable information (user's name, stack preferences, project constraints, decisions made). Small, always injected, cheap.

Final prompt = system + facts + retrieved cold chunks (top 3–5) + warm summary + hot window + current message. Everything is capped; nothing grows unboundedly.

**7.1 — 600 messages, topic drift, and constant latency.**

Sharding solves storage, not context — correct. The key insight is that **context size must be decoupled from conversation length.** Concretely:

- **Fixed token budget.** Turn 5 and turn 5,000 both assemble ~8k tokens of context. Latency is therefore flat, because LLM latency scales with tokens sent, not with rows in your database.
- **Hierarchical summarisation.** Turn-level → episode-level → topic-level. Summaries of summaries keep the compression ratio roughly constant as history grows. Older material is compressed more aggressively (recency-weighted fidelity).
- **Topic segmentation.** Detect topic boundaries (embedding drift between consecutive turns, or explicit LLM segmentation) and store each segment separately: `[Python implementation]`, `[Java port]`, `[unit tests]`, `[pen testing]`. Now "what did we decide about the Java exception handling?" retrieves *only* that episode instead of dragging the entire history along. This is precisely the scenario where a flat running summary fails — it blurs four distinct technical threads into mush.
- **Retrieval instead of replay.** The full 600 messages live in the DB and are searched, never wholesale loaded. Retrieval cost is O(log N) via ANN, not O(N).
- **Asynchronous summarisation.** When a turn falls out of the window, a background worker summarises and indexes it. The user-facing request path never blocks on summarisation.
- **Caching.** Prompt-prefix caching on the stable portions (system prompt, facts, older summaries) cuts both latency and cost substantially.
- **Entity/decision tracking.** Maintain a running list of artifacts and decisions (`file: parser.py → ported to Parser.java → tested in ParserTest.java`) so cross-topic references resolve without retrieving prose.

**7.2 — Persisting memory across sessions.**

Promote from conversation-scoped to **user-scoped long-term memory**:
- At session end (or incrementally), a background job writes a **session summary**, extracts **durable facts/preferences**, and records **entities and decisions**.
- Store these in a user-level memory index: vector store for semantic recall, Postgres for structured facts and metadata (session ID, timestamp, topic tags, project).
- On a new session: inject the small always-on facts profile immediately, and expose a **`search_memory` tool** the agent calls when the user's message references prior work.
- **Memory consolidation:** deduplicate and merge facts over time; supersede stale ones (`prefers Python 3.9` → `prefers Python 3.12`) rather than accumulating contradictions. Apply decay/TTL to low-importance memories.
- Keep provenance on every memory (which session, when) so the assistant can say "in our conversation last Tuesday…" and so the user can inspect and delete it.

**7.3 — Deciding what past context is relevant.**

Never bulk-load. Selection is a **scored retrieval problem**:
- **Semantic relevance** — embed the current query, ANN search over session summaries and turn chunks.
- **Recency weighting** — combine similarity with a time-decay factor; last week usually beats last year.
- **Importance score** — assigned at write time (explicit decisions, stated preferences and corrections score high; small talk scores low).
- **Frequency/reinforcement** — facts confirmed repeatedly are more reliable and score higher.
- **Metadata filters** — project, topic tag, entity mentioned, date range parsed from the query ("what we discussed in March").
- **Two-stage:** retrieve ~20 candidates, cross-encoder rerank, keep top 3–5. Small k is deliberate — flooding context degrades quality, not just latency ("lost in the middle").
- **Conditional retrieval** — a lightweight router (or simply letting the agent decide whether to call the memory tool) skips retrieval entirely for self-contained messages like "write me a for-loop." Most turns need no memory at all.
- **MMR** for diversity so five near-duplicate summaries don't crowd out the one relevant fact.

**7.4 — Cross-session architecture, high level.**

```
User message
  → Orchestration layer (agent)
      ├─ Context Assembler  ── builds final prompt under token budget
      ├─ Tools:
      │    search_memory(query, filters)      → vector DB
      │    get_session(id) / list_sessions()  → Postgres
      │    get_user_facts(user_id)            → Postgres
      │    save_memory(fact, importance)      → both
      ├─ LLM call
      └─ Response
Background workers:
      summarize_evicted_turns() → embed → index
      consolidate_facts()       → dedupe / supersede
```

**Datastores:** Postgres (users, sessions, messages, facts, summaries — source of truth, exact queries, time ranges) + vector DB (embedded summaries and turn chunks with metadata payload) + Redis (hot window cache, session state).

**Key functions:** `assemble_context()`, `retrieve_relevant_memory()`, `summarize_segment()`, `extract_facts()`, `consolidate()`, `evict_and_archive()`.

#### 7.4.1 Framework and tool distribution

**LangGraph** is the natural choice — memory management is a stateful graph with conditional branching (retrieve or skip? summarise now or later?), it has first-class checkpointing/persistence for conversation state, and it supports cycles for retry. LlamaIndex is a reasonable alternative if the workload is retrieval-dominant (it ships `ChatMemoryBuffer`, `VectorMemory`, composable memory out of the box). A plain custom orchestrator is defensible too — this doesn't strictly need a framework.

**Tool split by query type:**

| Goes to **SQL (Postgres)** | Goes to **Vector DB** |
|---|---|
| Last N turns of current session | "What did we discuss about X?" |
| Time-range queries ("yesterday") | Semantic recall across sessions |
| Session/conversation listings | Finding related past episodes |
| Structured user facts & preferences | Topic-similarity matching |
| Exact entity lookups, counts, joins | Fuzzy/paraphrased references |
| Audit, deletion (GDPR), ownership | |

The agent picks based on whether the reference is **exact/temporal** (SQL) or **semantic/vague** (vector). Best practice is to run both and fuse for ambiguous cases, and to always resolve the vector hit's chunk ID back to Postgres for the authoritative full text.

#### 7.4.2 Summarisation tool + combining rolling window and history

**Yes** — a dedicated summarisation component, run **asynchronously** on eviction, not inline (it must not sit in the user's latency path).

- Trigger: turn count or token threshold exceeded in the hot window.
- It summarises the evicted block preserving **decisions, constraints, code artifacts, unresolved items and user preferences**, while dropping pleasantries and redundancy. Structured output (JSON with `topic`, `decisions`, `artifacts`, `open_items`) is far more robust than free prose.
- Summaries are embedded and indexed so they are retrievable, and stored in Postgres linked to the turn range they cover — the raw turns are never deleted, so you can always drill back down.

**Assembly order** (most stable content first, to maximise prefix-cache hits, with the most relevant content nearest the query to avoid "lost in the middle"):

```
[system prompt]
[user facts / preferences]        — always, small
[retrieved relevant summaries]    — top 3–5, from search_memory
[running summary of this session] — the compressed middle
[rolling window: last N turns]    — verbatim
[current user message]
```

A **budget manager** enforces the cap: if the total exceeds the limit, it trims in reverse priority order (retrieved memories first, then older summary detail, never the current message or the most recent turns). Explicitly mark section boundaries in the prompt so the model knows what is verbatim history versus a compressed summary versus retrieved memory from another session — otherwise it will confuse a summary of last month's chat for something the user just said.

---

## Section F — LLM-as-a-Judge & Evaluation

### 8. Telecom plan recommender — 10% over-provisioned

**Do not fix this by editing the system prompt's definition of "best."** That is a global change to correct a 10% subpopulation, with no ability to verify you haven't broken the 90%. Proposed approach:

1. **Quantify first.** Mine production logs for the failing cases, label them, and build a **golden eval set** (both the 10% failures and a representative sample of the 90% successes). Without this you cannot detect regression, whatever you change.
2. **Define fit explicitly** as a measurable criterion (see 8.1) rather than leaving "best" to the model's judgement.
3. **Add a validation layer between generation and response** — an LLM-as-judge that checks the recommendation against the user's stated need and the plan catalogue, and rejects over-provisioned or over-priced recommendations. This is *additive*: it only fires on the bad cases and leaves the 90% untouched. That's the core reason to prefer it over prompt surgery.
4. **Deterministic guardrails alongside the judge** — a simple rule engine can catch the egregious cases cheaply (`if recommended_quota > 5 × estimated_need → flag`), with the LLM judge handling the nuanced ones.
5. **Retry loop** on rejection, with a rule-based fallback (cheapest plan satisfying all stated requirements) if retries exhaust.
6. **Address the root incentive** — a prompt that says "maximise company profit" *is* the bug. Reframe toward fit-and-retention; churn from mis-sold plans is negative profit. Consider showing a good/better/best set rather than a single push.
7. **Ship behind a flag with A/B evaluation**, monitoring both mis-sell rate and business metrics.

**8.1 — Defining "expensive."**
Anchor it primarily to the **stated need in the request**, not to user demographics. Demographic anchoring ("this user seems low-income") is a fairness and compliance hazard and is often simply wrong.

Concretely, make it a computable **fit score**:
- **Over-provisioning ratio** — `recommended_quota / estimated_requirement` from the stated use case. A music-streaming-only user needs ~1 GB/day; recommending 7 GB/day gives a ratio of 7 → flag above a threshold (say 2×).
- **Price delta vs cheapest sufficient plan** — is there a cheaper catalogue plan that satisfies *every* stated requirement? If yes, and the delta exceeds ~20–25%, flag. This is the strongest and most objective signal, and it's checkable deterministically.
- **Unused-feature count** — how many paid components of the plan the user never asked for (OTT bundles, international minutes).
- **Explicit user signals** — a stated budget, "cheapest option", "basic plan" are hard constraints and should be treated as non-negotiable.
- Secondary/contextual: stated household size, device count, current plan (a large jump warrants justification).

Keep it as a **rubric with numeric thresholds** so the judge's verdict is reproducible and auditable, rather than asking an LLM the vague question "is this too expensive?"

**8.2 — Judge as a validation layer, and the retry cycle.**

Yes — a generate → validate → (retry) → respond loop.

```
1. Generator produces recommendation
2. Judge evaluates against rubric + catalogue
3. PASS → return to user
   FAIL → append judge's structured feedback
          (violated criterion + constraint, e.g.
           "over-provisioned 7×; max 2 GB/day")
        → regenerate (attempt ≤ 2)
4. Retries exhausted → deterministic fallback:
   cheapest plan meeting all stated requirements,
   optionally with a human-review flag
5. Log everything: input, output, verdict, reason, attempt count
```

Design notes:
- **Hard cap the retries** (2 is usually right) — unbounded loops are a latency and cost hazard.
- **Feedback must be specific and actionable.** "Rejected" produces the same output again; "reduce data allowance to ≤2 GB/day, user only streams music" produces a fix.
- **Deterministic fallback is mandatory** — never let the loop fail open.
- **Latency budget:** the judge adds a round trip. Mitigate by running it only when a cheap pre-filter flags risk (over-provisioning ratio above threshold), so the 90% path stays fast and cheap.
- **Judge failures are also failures** — monitor false-rejection rate, or you'll trade a 10% mis-sell problem for a 15% over-correction problem.

**8.3 — What to pass to the judge.**

- **User's original request / stated requirements** — verbatim, unsummarised. This is the ground truth for the fit assessment.
- **The generator's final recommendation** — the plan, its price, and its full specification.
- **Retrieved plan catalogue** (or at least the viable alternatives) — essential, because the central question "does a cheaper sufficient plan exist?" is unanswerable without it. Filter to plans meeting the stated requirements so the judge isn't drowned in the full catalogue.
- **The judge's own prompt** — an independent rubric with explicit criteria, numeric thresholds, and few-shot examples of pass/fail drawn from labelled production cases.
- **A structured output schema** — `{verdict, violated_criteria[], severity, suggested_constraint, confidence}`. Forces consistency and makes verdicts machine-actionable and analysable.

Deliberately **exclude**: the generator's system prompt (especially the "maximise profit" instruction — that would import the very bias you're correcting), and the generator's reasoning (see below).

**8.4 — Should the generator's reasoning be passed?**
As a default, **no.** The judge should independently evaluate `(user requirement, recommended plan, catalogue)`. Passing the reasoning turns "is this recommendation right?" into "is this argument persuasive?" — a different and easier-to-pass test.

#### 8.4.1 How reasoning biases the judge

- **Anchoring / persuasion.** A fluent, confident justification is exactly what an LLM finds convincing. The judge follows the chain of thought and validates its internal coherence rather than checking the artifact against the user's actual requirement. Note that the generator's reasoning is *plausible* precisely in the failure cases — "the user may travel, so extra data provides flexibility" reads perfectly reasonably while being wrong.
- **Correlated errors.** If the reasoning contains the flawed premise (over-provisioning is a benefit), the judge inherits it. You lose the independence that makes the second opinion valuable at all.
- **Reduced scrutiny.** Given a pre-built argument, the judge tends to verify rather than evaluate — it grades the essay instead of checking the answer.
- **Post-hoc rationalisation.** The stated reasoning may not be the actual cause of the output, so the judge evaluates a fiction.

**When to pass it anyway:**
- **Faithfulness auditing** — when the explicit task is "does the reasoning support the conclusion?" or "did the model follow the required process/policy?"
- **Offline error analysis and debugging** — understanding *why* failures happen, to write better rubrics. Here bias doesn't matter because no decision is being gated.
- **Multi-step/agentic evaluation** where individual intermediate steps must be checked.
- **Compliance contexts** where the justification itself is the regulated artifact.
- Blind evaluation first, then optionally a second pass with reasoning shown, is the safest pattern when you need both.

#### 8.4.2 Role of production log analysis

Log analysis is what turns "the judge should catch bad recommendations" into a **specification**:

- **Discover real failure modes.** Correlating input → output → reasoning on the bad 10% reveals the actual patterns (e.g. the model over-weights "future-proofing", or it defaults to the highest-margin plan when the request is vague). You almost never guess these correctly a priori.
- **Derive rubric criteria and thresholds.** The distinction between acceptable headroom and over-provisioning, and the numeric cut-off, come from the data — not from intuition.
- **Build the labelled eval set.** Human-label a sample of logged cases; this is what you measure judge accuracy against and what protects the working 90% from regression.
- **Source few-shot examples.** Real borderline cases from logs make far better judge exemplars than synthetic ones.
- **Measure judge quality.** Compute agreement (Cohen's κ, precision/recall on the failure class) between judge verdicts and human labels *before* trusting it in the loop.
- **Detect drift.** New plans, new user phrasings, seasonal patterns — continuous log monitoring catches degradation and feeds rubric updates.
- **Close the loop.** Post-deployment, logged judge rejections and their outcomes become the next iteration's training and evaluation data.

### 9. Should the judge be stronger, weaker, or the same model?

Default: **stronger** (or an equally strong but *different* model family). Evaluation is generally harder than generation — it requires holding the criteria, the output and the alternatives in mind simultaneously and reasoning about their relationships. A model that can't produce a good answer usually can't reliably recognise one.

**9.1 — Why not weaker or identical.**

**Weaker:**
- Lacks the reasoning depth to catch subtle failures — the failures that need catching are precisely the plausible-looking ones.
- Poorly calibrated: tends to rubber-stamp fluent output, producing high false-pass rates.
- Struggles with multi-criteria rubrics, arithmetic checks (`7 GB/day vs 1 GB need`) and comparison against a catalogue.
- Inconsistent verdicts on identical inputs, which makes the evaluation itself untrustworthy.

**Identical model:**
- **Self-preference / self-enhancement bias** — models systematically rate their own outputs higher, a well-documented effect.
- **Shared blind spots** — same training data, same reasoning failure modes, same misconceptions. If the generator thinks over-provisioning is prudent, so does the judge. The errors are correlated exactly where you need independence.
- The second opinion adds cost and latency without adding information.

**What evaluation actually demands:** decomposing an output against explicit criteria, comparing against alternatives, verifying arithmetic and constraints, resisting fluent-but-wrong reasoning, and producing calibrated, consistent verdicts.

**When the default changes:**
- **Narrow, objective checks** — schema validity, format, presence of forbidden content, numeric bounds. Use code or a small model; an LLM is the wrong tool entirely. Deterministic checks should always come first, with the LLM judge reserved for the genuinely subjective residue.
- **High volume / tight latency / cost constraints** — distil a **small fine-tuned judge** from labels produced by a strong model. This often beats a general-purpose large model on the specific task, at a fraction of the cost.
- **Cascade** — cheap fast judge on everything, escalate low-confidence or borderline cases to the strong judge. Best cost/quality trade-off in practice.
- **Ensembles / juries** — several diverse mid-tier models voting can outperform one strong judge and reduce single-model bias.
- **Domain-specific tasks** — a specialised fine-tuned model may beat a generically stronger one.
- **Non-negotiable:** always validate the judge against human labels before trusting it, whatever its size.