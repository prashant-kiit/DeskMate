# Theme Extraction for Presentation Documents
### A Production System Design (Senior AI Engineer perspective)

**Scope:** `.ppt` / `.pptx` only. 10M presentations to backfill, plus continuous new uploads.
**Audience:** software engineers who are not AI/ML experts. Every AI concept is explained in one plain sentence before it is used.

---

## Table of Contents

1. [Clarify the Problem](#1-clarify-the-problem)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Slide Content Extraction](#3-slide-content-extraction)
4. [AI/ML Approach](#4-aiml-approach)
5. [Theme Detection Algorithm](#5-theme-detection-algorithm)
6. [Theme Summarization](#6-theme-summarization)
7. [Storage Design](#7-storage-design)
8. [Vector DB vs SQL vs Object Storage](#8-vector-db-vs-sql-vs-object-storage)
9. [Processing Architecture](#9-processing-architecture)
10. [Backfilling 10 Million Presentations](#10-backfilling-10-million-presentations)
11. [Cost Optimization](#11-cost-optimization)
12. [Quality and Evaluation](#12-quality-and-evaluation)
13. [Handling Difficult Presentations](#13-handling-difficult-presentations)
14. [Versioning and Reprocessing](#14-versioning-and-reprocessing)
15. [API Design](#15-api-design)
16. [Reliability and Observability](#16-reliability-and-observability)
17. [Security](#17-security)
18. [Final Recommended Architecture](#18-final-recommended-architecture)
19. [Appendices: diagrams, schema, backfill plan, trade-offs, risks, stack](#appendix-a-architecture-diagram-one-page)

---

# 1. Clarify the Problem

## 1.1 What are we actually solving?

A presentation is a **linear document**. The author already thought in sections when they built it, but that structure is invisible to our platform. We only see 20 unlabelled slides.

We want to recover that hidden structure: **split each deck into a small number of meaningful sections, name each section, and describe it in one or two sentences.**

This is not really "clustering documents". It is **document segmentation + labelling**. That distinction drives almost every design decision later, so it is worth stating up front.

## 1.2 What is a Theme (working definition)

> A **Theme** is a contiguous-by-default group of slides that a human reader would describe as "one section of the deck", because the slides share a concept, topic, argument, or thesis.

Three practical rules we commit to:

- **Every slide belongs to exactly one theme.** (Primary assignment. Secondary links are a nice-to-have, see §5.9.)
- **Themes preserve slide order.** Theme 1 comes before Theme 2 because its slides come first.
- **Themes are usually contiguous ranges** (slides 5–9), because that is how decks are authored. We allow rare exceptions (§5.8).

## 1.3 Input

| Field | Value |
|---|---|
| File | `.pptx` (Open XML zip) or legacy `.ppt` (binary OLE) |
| Size | 5 to 500+ slides, typically 10–40 |
| Content | titles, bullets, text boxes, speaker notes, tables, charts, images, SmartArt, embedded video |
| Volume | 10M backfill + new uploads (assume ~50k/day) |
| Quality | anything from a clean corporate template to a scanned photo deck with zero real text |

## 1.4 Output

For each presentation, an ordered list of themes:

```json
{
  "presentation_id": "p_8f21",
  "pipeline_version": "v3",
  "themes": [
    {
      "theme_id": "t_01",
      "order": 1,
      "name": "Introduction",
      "summary": "Introduces the company and the problem of fragmented payment rails in Southeast Asia.",
      "keywords": ["fintech", "payments", "problem statement"],
      "slide_range": [1, 4],
      "slides": [1, 2, 3, 4],
      "confidence": 0.82
    },
    { "theme_id": "t_02", "order": 2, "name": "Market Analysis", "slide_range": [5, 9], "...": "..." }
  ]
}
```

Plus reusable by-products that other teams will consume: **per-slide clean text**, **per-slide embeddings**, **per-theme embeddings**.

## 1.5 Assumptions (state them, then design to them)

1. Average deck ≈ **25 slides** → ~250M slides total. This number drives all cost/throughput math.
2. Themes should number roughly **3–8 per deck**; a deck with 40 themes is useless to a user.
3. This is **asynchronous**. Nobody is waiting on a loading spinner. Target: themes visible within ~2 minutes of upload (p95), not 2 seconds.
4. **~15% of slides are visual-only** (image, chart, or diagram with no extractable text) and a smaller share of *decks* are visual-only.
5. Decks are **multilingual**; English dominates but not exclusively.
6. There is meaningful **duplication** across the corpus (re-uploads, shared templates, course material). Assume 10–20% exact-duplicate files.
7. We control our own inference for embeddings; LLM calls may be a vendor API or self-hosted.

## 1.6 What is genuinely hard here

| Hard part | Why |
|---|---|
| **No labels, no ground truth** | Nobody has ever annotated "correct" themes. We must build a golden set (§12). |
| **The number of themes is unknown** | It varies per deck. Fixed `k` clustering is wrong. |
| **Slides are short and sparse** | A slide may contain 6 words. Embeddings of short text are noisy. |
| **Repeated boilerplate** | Agenda slides, section dividers, thank-you slides, logo slides. They look similar to everything or nothing. |
| **Visual slides** | A slide that is one architecture diagram carries a lot of meaning and no text. |
| **Cost at 250M slides** | A naive "one LLM call per slide" design costs millions of dollars and takes months. |
| **Quality is subjective** | Two humans will disagree whether the boundary is at slide 9 or slide 10. Our metrics must tolerate that. |
| **Order matters** | Standard clustering (k-means) throws away order. We must not. |

---

# 2. High-Level Architecture

## 2.1 The one-line story

> A file lands in object storage → an event goes on a queue → a worker turns the deck into clean per-slide text → a GPU service turns each slide into a vector → an algorithm cuts the deck into sections → **one** LLM call names and summarizes all sections → results go into Postgres + a vector index → search and recommendations read from there.

## 2.2 Component map

```
                          ┌──────────────────────────────────────────┐
  User upload / backfill  │            INGESTION LAYER               │
  ─────────────────────►  │  API Gateway → Upload Service → S3       │
                          │  writes row in Postgres, emits event     │
                          └───────────────┬──────────────────────────┘
                                          │ (presentation_id, s3_key, hash)
                                          ▼
                          ┌──────────────────────────────────────────┐
                          │   MESSAGE BUS (Kafka)  +  ORCHESTRATOR    │
                          │   topics: ingest.high / ingest.backfill   │
                          │   Temporal workflow per presentation      │
                          └───────────────┬──────────────────────────┘
                                          ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  STAGE 1: EXTRACTION WORKER (CPU)                                          │
  │  .ppt→.pptx (LibreOffice) │ python-pptx parse │ render PNG │ OCR if needed  │
  │  → writes slides.json + slide PNGs to S3                                   │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  STAGE 2: REPRESENTATION + EMBEDDING (GPU service, batched)                │
  │  slide card text → embedding model → 250M vectors → S3 parquet + cache     │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  STAGE 3: THEME DETECTION (CPU, pure algorithm, no LLM)                    │
  │  order-preserving segmentation → candidate themes + boundary confidence    │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  STAGE 4: LLM NAMING + SUMMARIZATION (1 call per presentation)             │
  │  compact deck outline → JSON: names, summaries, optional boundary fixes    │
  │  → schema validation → grounding check → retry/fallback                    │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │  STAGE 5: PERSISTENCE                                                      │
  │  Postgres (themes, theme_slides, status)  │  Qdrant (theme vectors)         │
  │  S3 (slides.json, embeddings parquet, LLM I/O audit)                        │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      ▼
        Search API   │   Recommendations   │   Document understanding   │   Future AI
```

## 2.3 Each component in plain English

| Component | What it does | Why we need it |
|---|---|---|
| **Upload service + S3** | Stores the raw file, computes a content hash, creates the DB row. | The raw file is the source of truth; we will re-read it every time models change. |
| **Kafka** | A durable list of "work to do", with separate lanes for live traffic and backfill. | Decouples upload speed from processing speed. Backfill cannot starve live users. |
| **Temporal (orchestrator)** | Runs the 5 stages as a workflow, remembers where each presentation is, retries only the failed stage. | Without it, a failure in stage 4 means redoing extraction and embeddings — expensive. |
| **Extraction workers** | Open the deck, pull out text/tables/charts/notes, render images, OCR when needed. | Everything downstream depends on this text. Garbage in, garbage themes. |
| **Embedding service** | Turns each slide's text into a list of numbers (a vector) that captures meaning. | Lets us measure "are these two slides about the same thing?" cheaply and at scale. |
| **Theme detector** | Pure math. Finds where the topic changes and cuts the deck there. | Fast, deterministic, free, testable. Does 90% of the job without an LLM. |
| **LLM service** | Reads a compact outline of the deck and writes a name + summary per section. | Only an LLM can produce a human-quality label like "Go-To-Market Strategy". |
| **Postgres** | Stores themes, slide-theme links, processing status. | Relational, transactional, easy to query and join for the product API. |
| **Vector DB (Qdrant)** | Stores theme vectors for similarity search. | Powers "find decks about market sizing" and "more like this". |

---

# 3. Slide Content Extraction

> **Concept in one sentence:** extraction means converting a binary presentation file into plain, structured text that a model can read.

This stage is unglamorous and is where most real-world quality is won or lost.

## 3.1 File handling

| Case | Approach |
|---|---|
| `.pptx` | Parse directly with **python-pptx**. It is a zip of XML; fast, no rendering needed. |
| `.ppt` (legacy binary) | Convert with **LibreOffice headless** (`soffice --convert-to pptx`) in a sandboxed container, then treat as `.pptx`. ~10–15% of a legacy corpus. |
| Corrupted / password-protected | Fail fast, mark `status = EXTRACTION_FAILED` with a reason code, do not retry forever. |

Run LibreOffice and any rendering in a **locked-down container** (no network, read-only FS, CPU/memory/time limits). Office file parsers are a classic attack surface.

## 3.2 What we pull from every slide

| Element | How | Notes |
|---|---|---|
| **Title** | Placeholder of type `TITLE`/`CENTER_TITLE`; fallback = the topmost text box with the largest font. | Highest-signal field. Weighted heavily in the slide representation. |
| **Body text / bullets** | Walk all shapes, `shape.text_frame.paragraphs`, keep indent level. | Preserve reading order: sort shapes by (top, left), not by XML order. |
| **Speaker notes** | `slide.notes_slide.notes_text_frame`. | Often the richest text in a sparse deck. Frequently ignored — do not ignore it. |
| **Tables** | `shape.has_table` → flatten to `header: v1, v2 | header2: ...`. | Convert to a compact one-line-per-row form, truncate to first ~5 rows. |
| **Charts** | `shape.has_chart` → chart title, series names, category names. | Series names ("Revenue", "Churn") are strong topic signals. Never dump raw data points. |
| **SmartArt / grouped shapes** | Recurse into group shapes; SmartArt text lives in `dgm` XML parts. | Common in "process"/"architecture" slides. |
| **Images** | Record count, size, and position. Extract alt-text if present. | Alt-text is free OCR when it exists. |
| **Slide metadata** | index, layout name, section name (PowerPoint native sections!), hidden flag, animation count. | **Native PowerPoint sections, when present, are ground truth — use them directly.** |
| **Deck metadata** | title, author, created/modified date, language, template name. | Used for language routing and dedup. |

**Two easy wins that most designs miss:**

1. **Native sections.** `.pptx` supports author-defined sections (`p14:sectionLst`). If a deck has them, we skip detection entirely and only run summarization. Roughly 5–10% of decks. Free perfect accuracy.
2. **Layout names.** A layout literally named `Section Header` or `Divider` is an explicit boundary marker.

## 3.3 The OCR decision (cost control lives here)

We do **not** OCR everything. Rendering + OCR is 10–50× the cost of XML parsing.

```
extracted_chars = len(title + body + notes)

if extracted_chars >= 80:                      → no rendering, no OCR       (~70% of slides)
elif slide has images/SmartArt:                → render PNG @150dpi + OCR   (~25%)
    if OCR yields < 20 chars AND slide is picture-dominant:
                                               → queue for VISION LLM       (~3–5%)
else (genuinely empty slide):                  → mark EMPTY, inherit neighbour context
```

- **Renderer:** LibreOffice headless → PDF → `pdftoppm` PNG. Batch the whole deck in one LibreOffice invocation (process startup is the expensive part).
- **OCR:** PaddleOCR or Tesseract on CPU; PaddleOCR handles multilingual and rotated text better.
- **Vision LLM:** only for slides that are still empty after OCR — typically diagram/photo slides. One cheap vision call producing a 20-word description. Cap at **N=6 vision slides per deck** to bound cost.
- **Confidence:** store `ocr_confidence`. Below ~0.6 we treat the text as low-trust and down-weight it (§13).

## 3.4 The Slide Card — our canonical representation

Every slide becomes a small, fixed-shape text block. Consistency matters more than richness: the embedding model should see the same format every time.

```
[Slide 7 of 20]
TITLE: Competitive Landscape
BULLETS: Three incumbents hold 68% share; pricing is opaque;
         no incumbent offers real-time settlement
TABLE: Competitor | Share | Price — Acme 31% $$$ ; Bolt 22% $$ ; Cyx 15% $
CHART: "Market share by player" (series: 2022, 2023, 2024)
NOTES: Emphasise that Acme's share is shrinking 4pts/yr
IMAGE_TEXT(ocr): quadrant chart — ability to execute vs completeness
LAYOUT: Title and Content
```

Rules:
- Truncate to **~400 tokens**, dropping in this priority order: notes → OCR → table rows → bullets. Title is never dropped.
- Normalize whitespace, remove bullet glyphs, collapse repeated template junk (page numbers, company footer that appears on all slides).
- **Boilerplate stripping:** any exact text line that appears on >60% of slides in the deck is template chrome — remove it. This one rule dramatically improves embedding quality.
- Store the slide card in S3 (`slides.json`) and a truncated copy + hash in Postgres.

We also store a `text_hash` per slide card. It powers the embedding cache (§11) — template slides repeat across millions of decks.

---

# 4. AI/ML Approach

> **Concept in one sentence:** an *embedding* is a list of ~1000 numbers representing a piece of text's meaning, such that similar meanings produce vectors that point in similar directions.

## 4.1 The four candidate approaches

### Option A — Embeddings + generic clustering (k-means / HDBSCAN)
Embed every slide, cluster the vectors, call each cluster a theme.

- ✅ Cheap, fast, no LLM.
- ❌ **Destroys slide order.** k-means will happily put slides 2, 11, and 19 in one cluster.
- ❌ Needs `k` in advance (k-means) or produces unpredictable cluster counts and lots of "noise" points (HDBSCAN).
- ❌ On 10–30 short, noisy vectors per deck, density-based methods are unreliable. HDBSCAN needs more points than a typical deck has.

**Verdict:** wrong tool. Decks are sequences, not point clouds.

### Option B — LLM reads the whole deck and returns themes
Send all slide text to a large model, ask for sections.

- ✅ Best raw quality; understands narrative, rhetoric, implicit structure.
- ❌ Cost: ~10–20k input tokens × 10M decks = 100–200B tokens. Even at $1/M that is $100–200k, and at frontier prices far more.
- ❌ Long decks blow the context window or degrade ("lost in the middle").
- ❌ Non-deterministic boundaries; hard to unit-test; hallucinated slide numbers.
- ❌ Latency and vendor rate limits become the throughput ceiling for the whole backfill.

**Verdict:** too expensive and too fragile as the *primary* mechanism — but excellent for *labelling*.

### Option C — LLM classifies each slide into a topic
One call per slide.

- ❌ 250M calls. Dead on arrival for cost, and it still needs a grouping step afterwards.

**Verdict:** no.

### Option D — Hierarchical / agglomerative clustering
Merge the most similar items step by step, cut the tree at some height.

- ✅ No fixed `k`; produces a tree you can cut at different granularities.
- ✅ **Can be constrained to only merge adjacent items** (a "connectivity constraint"), which preserves order.
- ❌ On its own it still needs a rule for where to cut, and it cannot name a theme.

**Verdict:** the right backbone — if constrained to adjacency and paired with a good cut criterion.

## 4.2 ✅ Recommended: Hybrid — *order-aware embedding segmentation + one LLM call per deck*

```
Slides → Slide Cards → Embeddings → Adjacency-constrained segmentation
      → candidate sections (+ confidence) → ONE LLM call → names, summaries,
        optional boundary correction → validated JSON → storage
```

**Division of labour:**

| Job | Done by | Why |
|---|---|---|
| Understand each slide's meaning | Embedding model | Cheap (~$0.00002/slide self-hosted), batchable, deterministic, cacheable |
| Decide *where* sections start and end | Algorithm on embeddings | Deterministic, free, testable, order-preserving |
| Decide *what to call* a section, and describe it | LLM | Only an LLM writes "Go-To-Market Strategy" instead of "cluster_3" |
| Fix obviously wrong boundaries | Same LLM call, optional field | Catches semantic cases math misses, at zero extra cost |

**Why this wins:** the expensive, non-deterministic component (LLM) is invoked **once per presentation, not once per slide**. That is a **25× cost reduction** versus per-slide LLM calls, and it converts a $2M problem into a ~$10–30k problem.

## 4.3 Answers to the specific questions

**Where are embeddings used?**
1. Per slide, to measure topic similarity between neighbours (drives segmentation).
2. Per theme (mean of member slide vectors), stored for search and recommendations.

**Where is the LLM used?**
1. Once per presentation, for naming + summarization + optional boundary repair.
2. Rarely, as a **vision** model, for slides that are pure images (capped per deck).
3. Offline, as a **judge** during evaluation (§12).

**Is an LLM required for every slide?** No — and this is the single most important cost decision in the design. Text LLM: 0 calls per slide. Vision LLM: only for the ~3–5% of slides that are text-free, capped at 6 per deck.

**Can we skip the LLM entirely for some decks?**
Yes:
- Decks with **native PowerPoint sections** → skip detection, still summarize (or skip entirely if section names are good and product accepts no summary).
- Decks with **< 6 slides** → one theme, name = deck title, summary from a cheap template or a single tiny call.
- **Duplicate files** (same content hash) → copy the previous result. No compute at all.

**How do we handle very large presentations (200+ slides)?**
A three-level strategy:
1. **Segment locally.** Run segmentation over the full embedding sequence — it is O(n²) at worst but n=500 is trivial (a few ms).
2. **Two-level themes.** If a deck yields more than ~10 sections, merge adjacent sections into parent themes using the same algorithm applied to *section centroids*. Output parent themes (shown by default) with child sub-themes.
3. **Compress the LLM input.** Never send all 500 slides. Send, per section: the section's slide range, its 3 most-central slide titles, and the top keywords. This keeps LLM input at ~2–4k tokens **regardless of deck size** — a critical property for predictable cost.

**How do we maintain original slide order?**
By construction. Segmentation only ever cuts a sequence; it never reorders. Themes are stored with `theme_order`, and `theme_slides` carries `position_in_theme`. Even in the rare non-contiguous case (§5.8), the theme's sort key is its **first** slide index.

---

# 5. Theme Detection Algorithm

## 5.1 Step 1 — Chunking

**The chunk is the slide.** Do not sub-chunk. A slide is already a human-authored unit of thought, usually 20–150 words, which fits comfortably in any embedding model.

Two exceptions:
- **Very long slides** (>400 tokens, e.g. a dense appendix table): truncate rather than split, to keep one vector per slide.
- **Empty slides:** no meaningful vector. Mark them `EMPTY` and assign them to the *preceding* theme (a blank/divider slide belongs with the section it introduces or closes).

## 5.2 Step 2 — Embeddings

| Decision | Choice | Why |
|---|---|---|
| Model | **BGE-M3** or **multilingual-e5-large**, self-hosted on GPU | Multilingual (assumption #5), strong on short text, ~$0 marginal cost after hardware |
| Fallback / low-volume | `text-embedding-3-small` (API) | No infra to run; fine for live traffic, too costly at 250M scale |
| Dimensions | 1024 (or 768 to halve storage) | 1024 is a good quality/size trade-off |
| Normalization | L2-normalize | Makes cosine similarity a simple dot product |
| Batching | 64–256 slide cards per GPU batch, sorted by length | 5–10× throughput vs one-at-a-time |

Add a **title boost**: embed the slide card, and separately embed the title, then use `v = normalize(0.7 * v_card + 0.3 * v_title)`. Titles carry disproportionate topical signal, and this is cheaper and more robust than prompt-engineering the card format.

## 5.3 Step 3 — Similarity

For adjacent slides *i* and *i+1*, cosine similarity `sim(i, i+1) ∈ [-1, 1]`, where 1 = same topic.

Raw adjacent similarity is noisy (one odd slide creates a fake boundary). So we use a **smoothed block score**, in the spirit of the classic TextTiling algorithm:

```
left(i)  = mean vector of slides [i-w+1 .. i]        (w = 2 or 3)
right(i) = mean vector of slides [i+1 .. i+w]
depth(i) = 1 - cosine(left(i), right(i))
```

`depth(i)` is high when the topic genuinely changes between the block before and the block after position *i*. This is far more stable than single-pair similarity.

**Add non-semantic boundary evidence** — cheap and very effective:

| Signal | Bonus to depth |
|---|---|
| Slide layout is a section header / divider | +0.35 |
| Title matches an agenda item elsewhere in the deck | +0.20 |
| Title starts with a numeral/"Part N"/"Chapter" | +0.15 |
| Large gap in slide creation timestamps (`p:sld` rels) | +0.05 |
| Both neighbours share an identical title (continuation slide, "Results (2/3)") | −0.40 (suppress boundary) |

## 5.4 Step 4 — Clustering algorithm

**Chosen: adjacency-constrained agglomerative clustering (Ward linkage with a connectivity matrix), with dynamic-programming refinement.**

In plain terms: start with every slide as its own group, and repeatedly merge the two *neighbouring* groups that are most similar, until a stopping rule fires. Because only neighbours may merge, order is preserved automatically.

Implementation is one line of scikit-learn:

```python
AgglomerativeClustering(
    n_clusters=None,
    distance_threshold=T,
    linkage="ward",
    connectivity=path_graph(n_slides),   # ← this enforces adjacency
)
```

Optional refinement for decks ≥ 15 slides: given the chosen number of segments *k*, run a **dynamic program** that picks the *k−1* cut points minimizing total within-segment variance. This is O(k·n²), trivial at n≤500, and gives globally optimal boundaries rather than the greedy ones. It typically moves 1 boundary in 5 and is worth the 3ms.

**Why not k-means?** No order, needs k. **Why not HDBSCAN?** Too few points per deck; produces noise labels we then have to invent rules for. **Why not a fine-tuned segmentation transformer?** Best-in-class quality, but needs labelled data we don't have on day one. It is the right **v2** move once the golden set exists (§14).

## 5.5 Step 5 — Choosing the number of themes

Do not use a fixed `k` and do not use the silhouette score blindly (it is unreliable on 20 points). Use a **penalized objective** that encodes what the product wants:

```
score(k) = within_segment_cohesion(k) - λ * k
choose k* = argmax score(k)   over k ∈ [k_min, k_max]

k_min = max(1, round(n_slides / 12))
k_max = min(8, floor(n_slides / 3))
λ     = tuned on the golden set (start ~0.03)
```

Then apply hard product guardrails:
- **Min theme size = 2 slides** (except the deck is tiny, or the theme is slide 1 alone as a genuine title/intro).
- **Max theme size = 15 slides** → if exceeded, recursively split that theme with the same algorithm.
- **Max themes = 8** at the top level; beyond that, roll up into parent themes (§4.3).

## 5.6 Minimum / maximum size enforcement

Post-process passes, in order:
1. **Absorb runts:** any 1-slide segment merges into whichever neighbour it is more similar to.
2. **Split giants:** any segment > 15 slides is re-segmented recursively.
3. **Cap count:** if segments > 8, merge the two adjacent segments with the highest similarity, repeat.

These deterministic passes make output shape predictable, which matters more for product quality than squeezing out the last 2% of clustering accuracy.

## 5.7 Adjacent vs non-adjacent slides

Default is **adjacent only**. Rationale: decks are authored linearly; a user seeing "Theme: Market Analysis — slides 5,6,9,14" will think the system is broken.

## 5.8 The non-adjacent exception

Some decks genuinely revisit a topic (e.g. "Financials" at slide 8 and again at slide 22). Handling:
- Segments remain contiguous **spans**.
- After segmentation, compare segment centroids. If `cosine(A, B) > 0.88` and they are not adjacent, link them as **one theme with two spans**: `spans: [[8,11],[22,24]]`.
- The theme sorts by its first span. The UI can show "Financials (slides 8–11, 22–24)".
- This is a **nice-to-have**, off by default, enabled after evaluation shows it helps.

## 5.9 Outlier slides and multi-theme slides

| Case | Handling |
|---|---|
| **Blank / decorative slide** | Assign to preceding theme, `relevance_score ≈ 0.1`, flag `is_filler`. |
| **Thank-you / Q&A / contact slide** | Rule-based detector (title match + last-3-slides position) → own theme "Closing", or appended to Conclusion. |
| **A slide that bridges two topics** | Primary assignment goes to the higher-similarity theme. Store a **secondary link** in `theme_slides` with `is_primary = false` when `sim` to the runner-up is within 0.05. This is how we honour "slides that belong to multiple concepts" without breaking the clean one-slide-one-theme model. |
| **Genuinely unrelated slide** (a stray meme) | Low `relevance_score`; if a whole theme's cohesion is below threshold, name it "Miscellaneous" and lower `confidence`. |
| **Appendix** | Detect by title keyword + trailing position → dedicated theme, excluded from the "main narrative" in the UI. |

## 5.10 Ordering the final themes

Sort by `min(slide_index)` of member slides. Assign `theme_order = 1..k`. This is stable across reprocessing runs, which matters for caching and for diffing versions.

## 5.11 Worked example — a 10-slide deck

Slide titles:

| # | Title |
|---|---|
| 1 | AcmePay — Series A |
| 2 | The problem: settlement takes 3 days |
| 3 | Why existing rails fail |
| 4 | Market size: $12B SEA payments |
| 5 | Competitive landscape |
| 6 | Growth forecast 2024–2027 |
| 7 | Our architecture |
| 8 | Real-time ledger design |
| 9 | Traction: 40k merchants |
| 10 | Thank you / Contact |

**Adjacent similarities** (illustrative):

```
1→2: 0.71   2→3: 0.88   3→4: 0.52   4→5: 0.84   5→6: 0.86
6→7: 0.41   7→8: 0.91   8→9: 0.55   9→10: 0.33
```

**Smoothed depth scores** (w=2), boundary candidates where depth is locally maximal:

```
after slide 3: depth 0.44  ← strong
after slide 6: depth 0.55  ← strongest
after slide 8: depth 0.40  ← strong
after slide 9: depth 0.61  ← strongest (closing slide)
after slide 1: depth 0.26  ← weak, below threshold
```

**Segmentation** with `k_min = max(1, 10/12) = 1`, `k_max = min(8, 3) = 3`... note `floor(10/3) = 3`, so we allow up to 3 — but the closing-slide rule adds one more segment outside the cohesion objective. Result:

```
Theme 1: slides 1–3   "Problem Statement"
Theme 2: slides 4–6   "Market Analysis"
Theme 3: slides 7–8   "Technical Architecture"
Theme 4: slides 9–10  "Traction and Close"
```

Slide 1 (title slide) is absorbed into Theme 1 by the runt rule. Slide 10 is a detected closing slide and joins slide 9 rather than forming a 1-slide theme.

**Then one LLM call** turns these ranges into names and summaries (§6). The algorithm proposed the ranges; the LLM confirmed them and wrote the labels.

---

# 6. Theme Summarization

## 6.1 What goes into the LLM call

**One call per presentation**, containing a compact outline — never the raw deck.

```
SYSTEM
You name and summarize sections of a slide deck. Use ONLY the provided slide
content. Never invent facts, numbers, or company names. If a section's content
is unclear, name it descriptively and say so in the summary. Output JSON only.

USER
Deck title: "AcmePay Series A"
Language: en
Sections proposed by the segmentation system:

[S1] slides 1-3
  1. AcmePay — Series A | Seed-stage fintech, Singapore
  2. The problem: settlement takes 3 days | Merchants wait 72h; working capital locked
  3. Why existing rails fail | Batch processing; no ISO20022; correspondent banking hops

[S2] slides 4-6
  4. Market size: $12B SEA payments | TAM $12B, SAM $3.1B, growing 18% CAGR
  5. Competitive landscape | 3 incumbents, 68% share, opaque pricing
  6. Growth forecast 2024-2027 | chart: revenue by segment

[S3] slides 7-8   ...
[S4] slides 9-10  ...

For each section return: name (2-5 words), summary (1-2 sentences, <=40 words),
keywords (3-5), confidence (0-1).
Also return boundary_feedback: [] unless a section is clearly wrong; then propose
a corrected slide range with a one-line reason.
```

**Content budget per slide:** title (full) + first ~25 words of body. For sections with more than 6 slides, include only the 3 most-central slides (highest cosine to the segment centroid) plus the first and last, and note `(+4 more slides)`.

**Result: 2–4k input tokens per deck, independent of deck size.** This is the property that makes the cost math work.

## 6.2 Controlling token usage

| Lever | Effect |
|---|---|
| Outline instead of full text | 10–20k tokens → 2–4k |
| Centrality-based slide selection for big sections | Caps input for 500-slide decks |
| `max_tokens` on output (≈ 600) | Bounds worst case |
| One call for all sections, not one per section | 5× fewer calls, and gives the model cross-section context so names are mutually distinct ("Market Analysis" vs "Competition" rather than two "Market" themes) |
| Batch API for backfill | ~50% discount at most vendors |
| Prompt caching for the system prompt | System prompt is identical across 10M calls |
| Skip for tiny/duplicate decks | ~15–25% of calls avoided |

## 6.3 Preventing hallucination

Five layers, cheapest first:

1. **Constrain the input.** The model only sees slide text. It cannot cite a competitor that isn't in the deck if the deck is all it sees.
2. **Structured output.** JSON schema / tool-calling with strict validation. Reject and retry once on malformed output.
3. **Slide-range validation (deterministic).** Every returned range must be a contiguous subset of the deck, ranges must be disjoint, and their union must cover all slides. Violation → discard the LLM's boundary feedback, keep the algorithm's segmentation. **The algorithm always wins ties.**
4. **Grounding check.** Extract content words (nouns, numbers, proper nouns) from the summary; require that ≥80% appear in — or are close paraphrases of — the section's slide text. Numbers get a strict check: **any digit string in the summary must appear verbatim in the slides.** Fabricated numbers are the most damaging failure mode and the easiest to catch.
5. **Fallback ladder.** Fail grounding → retry once at temperature 0 with "quote only from slides" → still failing → fall back to an **extractive** summary (the section's most-central slide title + top keywords) and set `confidence = 0.3`, `generated_by = "extractive_fallback"`.

Set `temperature = 0.2` and log every prompt/response pair to S3 for audit and future fine-tuning data.

## 6.4 Ensuring the summary is grounded

Beyond the checks above:
- Ask the model to return, per section, the `evidence_slides` it drew from. Validate they are inside the range. Cheap, and a strong hallucination tell when they aren't.
- Sample 1% of outputs continuously into an **LLM-as-judge** groundedness scorer (§12) and alarm if the score drifts.

## 6.5 What if a theme is very large?

A 40-slide theme should usually have been split (max-size rule, §5.6). If a large theme survives:
1. **Map:** summarize in windows of ~10 slides.
2. **Reduce:** summarize the window summaries into the final theme summary.
3. Store the sub-summaries as `sub_themes` — free structure for the UI.

This map-reduce path costs 2–3 extra calls and applies to <1% of decks, so it does not move the overall cost needle.

---

# 7. Storage Design

## 7.1 Storage technology per data type

| Data | Store | Why |
|---|---|---|
| Raw `.ppt/.pptx` files | **S3** (object storage) | Large binaries, write-once, cheap, lifecycle rules to Glacier |
| Rendered slide PNGs | **S3** | Big, regenerable, only needed during processing and for thumbnails |
| `slides.json` (extracted content) | **S3** | Semi-structured, sometimes large, rarely queried by field — but *always* needed on reprocess. Keeping it means a model upgrade never re-parses 10M files. |
| Slide embeddings (all 250M) | **S3 as Parquet**, partitioned by presentation | Bulk, sequential access, cheap. Not a search workload. |
| Presentations, slides, themes, links, status | **PostgreSQL** | Relational joins, transactions, the product API's bread and butter |
| Theme embeddings (~50M) | **Vector DB (Qdrant)** | This *is* a search workload |
| Metrics/traces | **Prometheus + OpenTelemetry** | Time series, not business data |
| LLM prompt/response audit | **S3**, 90-day lifecycle | Debugging + future training data; not queried transactionally |

## 7.2 Relational schema (PostgreSQL)

```sql
-- ─────────────── PRESENTATION ───────────────
CREATE TABLE presentations (
    presentation_id   UUID PRIMARY KEY,
    tenant_id         UUID NOT NULL,
    owner_id          UUID NOT NULL,
    storage_key       TEXT NOT NULL,          -- s3://decks/ab/cd/<hash>.pptx
    content_hash      CHAR(64) NOT NULL,      -- sha256 of file bytes (dedup key)
    file_type         TEXT NOT NULL,          -- 'ppt' | 'pptx'
    file_size_bytes   BIGINT,
    slide_count       INT,
    title             TEXT,
    language          TEXT,                   -- detected, ISO-639-1
    has_native_sections BOOLEAN DEFAULT FALSE,
    uploaded_at       TIMESTAMPTZ NOT NULL,
    updated_at        TIMESTAMPTZ NOT NULL
);
CREATE INDEX ON presentations (tenant_id, uploaded_at DESC);
CREATE INDEX ON presentations (content_hash);

-- ─────────────── PROCESSING STATE (one row per version attempt) ───────────────
CREATE TABLE presentation_processing (
    presentation_id   UUID REFERENCES presentations,
    pipeline_version  TEXT NOT NULL,          -- 'v3'
    status            TEXT NOT NULL,          -- PENDING|EXTRACTING|EMBEDDING|
                                              -- SEGMENTING|SUMMARIZING|COMPLETED|
                                              -- FAILED|SKIPPED|PARTIAL
    stage_checkpoint  JSONB,                  -- {"extract":"done","embed":"done"}
    attempt_count     INT DEFAULT 0,
    error_code        TEXT,                   -- CORRUPT_FILE, OCR_TIMEOUT, LLM_5XX...
    error_detail      TEXT,
    input_tokens      INT,
    output_tokens     INT,
    cost_micros       BIGINT,
    started_at        TIMESTAMPTZ,
    finished_at       TIMESTAMPTZ,
    PRIMARY KEY (presentation_id, pipeline_version)
);
CREATE INDEX ON presentation_processing (status, pipeline_version);

-- ─────────────── SLIDE ───────────────
CREATE TABLE slides (
    slide_id          UUID PRIMARY KEY,
    presentation_id   UUID NOT NULL REFERENCES presentations,
    slide_index       INT NOT NULL,           -- 1-based, authoritative order
    title             TEXT,
    text_excerpt      TEXT,                   -- first ~1000 chars of slide card
    text_hash         CHAR(64),               -- embedding cache key
    char_count        INT,
    has_image         BOOLEAN,
    has_table         BOOLEAN,
    has_chart         BOOLEAN,
    has_notes         BOOLEAN,
    ocr_used          BOOLEAN,
    ocr_confidence    REAL,
    is_empty          BOOLEAN DEFAULT FALSE,
    layout_name       TEXT,
    native_section    TEXT,                   -- author-defined section, if any
    slides_json_key   TEXT,                   -- s3 pointer to full content
    embedding_ref     TEXT,                   -- s3://emb/<pid>.parquet#row=7&model=bge-m3
    extraction_version TEXT,
    UNIQUE (presentation_id, slide_index)
);

-- ─────────────── THEME ───────────────
CREATE TABLE themes (
    theme_id          UUID PRIMARY KEY,
    presentation_id   UUID NOT NULL REFERENCES presentations,
    pipeline_version  TEXT NOT NULL,
    theme_order       INT NOT NULL,           -- 1..k, display order
    name              TEXT NOT NULL,
    summary           TEXT,
    keywords          TEXT[],
    start_slide       INT NOT NULL,           -- denormalized for fast display
    end_slide         INT NOT NULL,
    slide_count       INT NOT NULL,
    spans             JSONB,                  -- [[8,11],[22,24]] when non-contiguous
    confidence        REAL,                   -- blended cohesion + LLM confidence
    cohesion_score    REAL,                   -- pure math: mean sim to centroid
    generated_by      TEXT,                   -- 'llm' | 'extractive_fallback' | 'native'
    parent_theme_id   UUID REFERENCES themes, -- for two-level themes on big decks
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMPTZ DEFAULT now(),
    UNIQUE (presentation_id, pipeline_version, theme_order)
);
CREATE INDEX ON themes (presentation_id, pipeline_version) WHERE is_active;

-- ─────────────── THEME ↔ SLIDE ───────────────
CREATE TABLE theme_slides (
    theme_id          UUID NOT NULL REFERENCES themes ON DELETE CASCADE,
    slide_id          UUID NOT NULL REFERENCES slides,
    slide_index       INT NOT NULL,           -- denormalized, avoids a join
    position_in_theme INT NOT NULL,           -- 1..n within the theme
    relevance_score   REAL,                   -- cosine(slide, theme centroid)
    is_primary        BOOLEAN DEFAULT TRUE,   -- false = secondary/multi-theme link
    PRIMARY KEY (theme_id, slide_id)
);
CREATE INDEX ON theme_slides (slide_id);
```

## 7.3 Design notes

- **Versioning is in the primary key, not in an `UPDATE`.** Producing `v4` themes never destroys `v3`. A single `is_active` flag (flipped in one transaction) controls what the API serves. Rollback is one UPDATE.
- **Denormalized `start_slide`/`end_slide`** on `themes` means the common query ("show me this deck's themes") needs zero joins.
- **`slides` has no version column for content**, only `extraction_version` — because extraction changes rarely. If extraction logic changes materially, bump `extraction_version` and rewrite the rows.
- **Partitioning:** at 250M `slides` rows and 50M `themes` rows, partition `slides` and `theme_slides` by `hash(presentation_id)` into 64 partitions. Every query filters by `presentation_id`, so partition pruning is perfect.
- **Read replicas** serve the product API; the writer takes pipeline writes only.

---

# 8. Vector DB vs SQL vs Object Storage

> **Concept in one sentence:** a vector database is a specialized index that answers "which of my 50 million vectors point in a similar direction to this one?" in milliseconds.

## 8.1 What goes where

| Question | Answer | Example |
|---|---|---|
| **What goes in Postgres?** | Anything you look up by an ID, filter by a field, or join. Small values. | "Give me the 5 themes of deck p_8f21, in order." |
| **What goes in S3?** | Anything big, write-once, and read whole. | The original 40MB pptx; the 250M-row embedding parquet set; slide PNGs. |
| **What goes in the vector DB?** | Only vectors you need to run *similarity search* over, plus the minimum filter fields. | "Find 20 themes across the library similar to this one." |

## 8.2 Do we actually need a vector database?

**Yes — but a much smaller one than the naive design implies.**

The naive answer is "index all 250M slide vectors". That is a large, expensive cluster (≈ 250M × 1024 dims × 4 bytes ≈ **1 TB of raw vectors**, plus HNSW graph overhead, meaning many hundreds of GB of RAM).

**Our answer: index theme vectors only.**

- 10M decks × ~5 themes = **50M theme vectors** → 1024-dim float32 ≈ 200 GB raw; with `int8` scalar quantization ≈ **50 GB**. That fits comfortably on a modest Qdrant cluster.
- Theme vectors are also **semantically better for search**. A query like "market sizing for fintech" matches a *section*, not a random bullet.
- Slide vectors are still produced and kept — in **S3 Parquet** — because reprocessing needs them and they cost ~$5/TB/month there instead of RAM prices.

**When would we index slide vectors?** If the product later wants slide-level "find me a slide with a similar architecture diagram", we add a second collection, possibly only for the top-N most active tenants, or with aggressive quantization. That is a **Phase 3** decision, not a day-1 one.

**Important nuance on the similarity used for segmentation:** it needs vectors for *one deck at a time* (10–500 vectors). That is a `numpy` operation in the worker's memory, not a database query. **Segmentation never touches the vector DB.** People routinely over-provision vector databases because they conflate these two very different uses of embeddings.

## 8.3 What should NOT be in the vector DB

| Do not store | Why | Where instead |
|---|---|---|
| Full slide text / summaries | Vector DBs are poor document stores; payload bloat kills memory efficiency | Postgres / S3 |
| Raw files or images | Obviously | S3 |
| Every slide vector (day 1) | 5× the cost for a use case we don't have yet | S3 Parquet |
| Historical versions (v1, v2 themes) | Only the active version is searchable | Postgres + S3 |
| Anything you need transactions or joins for | No ACID, no joins | Postgres |
| PII or sensitive raw content in payloads | Harder to redact/delete than in Postgres | Postgres, with deletion tooling |

**Qdrant collection design:**

```
collection: theme_vectors_v3
  vector: 1024-dim, cosine, int8 quantized, HNSW(m=16, ef_construct=128)
  payload (filterable, minimal):
    theme_id, presentation_id, tenant_id, theme_order,
    language, slide_count, pipeline_version, is_active
```

Filtering by `tenant_id` at query time is a **hard security requirement**, not an optimization (§17).

---

# 9. Processing Architecture

## 9.1 Journey of one newly uploaded presentation

```
1. POST /presentations (multipart)  →  Upload Service
2. Upload Service: stream to S3, compute sha256 while streaming
3. Dedup check: SELECT ... WHERE content_hash = ?
      hit  → copy themes from the existing presentation, status=COMPLETED (~50ms). Done.
      miss → INSERT presentations + presentation_processing(status=PENDING)
4. Emit Kafka event to topic `presentations.ingest.high`, key = presentation_id
5. Orchestrator (Temporal) starts workflow ProcessPresentation(pid, version=v3)
6.   Activity: extract      (CPU pool)   → slides.json in S3, slides rows in PG
7.   Activity: embed        (GPU pool)   → parquet in S3  [cache-checked per slide]
8.   Activity: segment      (CPU pool)   → candidate themes in workflow memory
9.   Activity: summarize    (LLM pool)   → validated JSON
10.  Activity: persist      (txn)        → themes + theme_slides + Qdrant upsert
11.  status=COMPLETED, emit `presentations.themes.ready` event
12. Search indexer and recommendation service consume that event
```

**p95 target: under 2 minutes.** Typical breakdown for a 25-slide deck: extract 3–8s (30s if OCR), embed 0.5s, segment 20ms, LLM 3–6s, persist 100ms. The rest is queue wait.

## 9.2 Why Kafka *and* Temporal

They solve different problems and it's worth being explicit:

- **Kafka** is the *front door and the buffer*. It absorbs upload bursts and backfill floods, gives us separate priority lanes (partitioned topics `ingest.high` / `ingest.backfill`), and lets other teams consume our completion events.
- **Temporal** is the *per-item state machine*. It remembers that presentation X finished extraction and embedding but failed at the LLM step, so a retry resumes at step 4 rather than redoing steps 1–3. Without this, every transient LLM 429 costs us a full re-extraction — at 10M items, that's a very expensive mistake.

A lighter-weight alternative if you don't want Temporal: SQS per stage (a chain of queues) + the `stage_checkpoint` JSONB column as the state store. It works, it's cheaper to run, but you hand-roll timeouts, retries, and visibility. For a 10M-item backfill I'd take Temporal.

## 9.3 Retries and failure handling

| Failure | Retryable? | Policy |
|---|---|---|
| LLM 429 / 5xx | Yes | Exponential backoff with jitter, 5 attempts, respect `Retry-After` |
| Embedding service OOM/timeout | Yes | 3 attempts; halve the batch size on retry |
| S3 read timeout | Yes | 3 attempts |
| LibreOffice conversion timeout | Yes, once | Second attempt with a longer deadline and lower render DPI |
| Corrupt/encrypted file | **No** | `FAILED(CORRUPT_FILE)` immediately → DLQ. Retrying is pure waste. |
| Unsupported format | **No** | `SKIPPED` |
| Schema-invalid LLM output | Yes, once | Then extractive fallback (§6.3) — **not** a hard failure |

**Dead-letter queue:** after max attempts, publish to `presentations.dlq` with `presentation_id`, stage, error code, and attempt history. DLQ is a *workbench*, not a graveyard: a daily job groups DLQ items by `error_code` so an engineer sees "180k items failed with `SMARTART_PARSE_ERROR`" and can fix one bug and replay in bulk.

## 9.4 Idempotency

The critical property at 10M scale — messages *will* be delivered twice.

- **Idempotency key = `(presentation_id, pipeline_version)`**, which is exactly the primary key of `presentation_processing`.
- Workers begin with a conditional claim:
  ```sql
  UPDATE presentation_processing
     SET status = 'EXTRACTING', attempt_count = attempt_count + 1,
         started_at = now(), worker_id = $1
   WHERE presentation_id = $2 AND pipeline_version = $3
     AND (status IN ('PENDING','FAILED')
          OR (status <> 'COMPLETED' AND started_at < now() - interval '30 minutes'))
  RETURNING 1;
  ```
  Zero rows returned → someone else owns it (or it's done) → ack the message and stop.
- The stale-claim clause (`started_at < now() - 30 min`) recovers from worker crashes without a separate reaper.
- **Persistence is one transaction:** delete any existing themes for `(pid, version)`, insert the new ones, commit. Re-running produces the same final state.
- Qdrant upserts use deterministic point IDs derived from `theme_id`, so a repeat write overwrites rather than duplicates.

## 9.5 Rate limits and backpressure

- A **central token-bucket limiter** (Redis) for the LLM vendor: workers acquire *tokens-per-minute* and *requests-per-minute* before calling. This prevents 500 workers from collectively blowing a shared quota.
- **Concurrency caps per stage**, not global: e.g. 800 extraction workers, 12 GPU replicas, 200 in-flight LLM calls.
- **Backpressure:** if Qdrant or Postgres write latency exceeds a threshold, the orchestrator pauses the backfill consumer group. Live traffic continues.
- **Priority:** live uploads and backfill are separate consumer groups with separate worker pools and separate LLM quota allocations (e.g. 70% backfill / 30% live, dynamically shifted). A backfill can never delay a real user's deck.

## 9.6 Partial processing

Not every failure should produce nothing.

- Extraction OK, LLM failing repeatedly → persist themes with **algorithmic names** (`"Slides 5–9"` + top keywords), `status = PARTIAL`, `generated_by = extractive_fallback`. Users get a usable structure; a repair job upgrades them later.
- 3 of 40 slides fail OCR → continue with 37, flag `slides.ocr_used = false` and `is_empty = true`.
- Qdrant write fails but Postgres succeeded → `COMPLETED_PENDING_INDEX`; a reconciliation job re-syncs. **Postgres is the source of truth; the vector index is derived and rebuildable.**

## 9.7 Reprocessing

Triggered by: new model version, prompt improvement, bug fix, user request, or a quality alert. Mechanics in §14.

---

# 10. Backfilling 10 Million Presentations

## 10.1 Strategy overview

Treat the backfill as a **separate, throttled, resumable, checkpointed campaign** — with its own queue, its own workers, and its own budget — that runs alongside (and always yields to) live traffic.

```
┌──────────────┐   1. cursor-based enumeration in 10k-row batches
│ backfill_jobs│   2. publish to ingest.backfill (low priority)
│   (Postgres) │   3. dedicated consumer group + worker pool
└──────┬───────┘   4. checkpoint after every batch
       │           5. adaptive rate control watches live-traffic SLO
       ▼
   Kafka: presentations.ingest.backfill  (64 partitions)
       │
       ├─► extraction pool  (spot instances, 600–1000 vCPU)
       ├─► embedding pool   (8–16 GPUs, spot)
       └─► LLM pool         (Batch API, 50% discount)
```

## 10.2 Batching and checkpointing

```sql
CREATE TABLE backfill_jobs (
    batch_id         BIGSERIAL PRIMARY KEY,
    cursor_start     UUID,       -- enumerate presentations ordered by (uploaded_at, id)
    cursor_end       UUID,
    pipeline_version TEXT,
    status           TEXT,       -- QUEUED|IN_PROGRESS|DONE|FAILED
    total            INT,
    succeeded        INT,
    failed           INT,
    published_at     TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ
);
```

Enumerate with a keyset cursor (never `OFFSET` — it degrades badly at 10M rows). 10M / 10k = **1,000 batches**. If the process dies, restart from the last `DONE` batch. Progress is a single SQL query: `SELECT sum(succeeded) FROM backfill_jobs`.

## 10.3 Avoiding double processing

Four independent defences:

1. **Content-hash dedup** — before enqueuing, group by `content_hash`. Process one representative; copy results to the rest. Saves an expected 10–20% of *all* work.
2. **The `(presentation_id, pipeline_version)` claim** (§9.4) — the real guarantee. Even if a message is delivered five times, only one worker proceeds.
3. **Batch status** — a `DONE` batch is never re-published.
4. **Enqueue filter** — `WHERE NOT EXISTS (SELECT 1 FROM presentation_processing WHERE pipeline_version='v3' AND status='COMPLETED')`.

Slide-level embedding caching (keyed on `text_hash`) adds a fifth layer: even a genuinely reprocessed deck skips embedding for slides whose text is unchanged.

## 10.4 Prioritization

Do not process in random order. Process in **value order**:

| Wave | Population | Rationale |
|---|---|---|
| 0 | 5k decks | Canary. Manual quality review before spending real money. |
| 1 | Top ~500k by views/downloads in last 90 days | 80% of user-visible value for 5% of the work. Ship the feature after this wave. |
| 2 | Decks in active/paying tenants | Revenue-linked. |
| 3 | Uploaded in the last 2 years | Recency correlates with relevance. |
| 4 | The long tail | Runs for weeks at low priority on spot capacity; nobody notices. |

This also de-risks the project: if quality is bad, we discover it after 5k decks, not after 10M.

## 10.5 Throughput model and time estimate

**Assumptions:** 25 slides/deck avg → 250M slides; 15% of decks need OCR/rendering; 15% duplicates → **8.5M decks actually processed**.

| Stage | Unit cost | Capacity assumption | Throughput | Wall clock |
|---|---|---|---|---|
| Extraction (parse only) | ~1.5 s CPU/deck | 800 vCPU | ~530 decks/s theoretical | — |
| Extraction (with render+OCR, 15%) | ~25 s CPU/deck | (same pool) | — | — |
| *Blended extraction* | ~5.0 s CPU/deck | 800 vCPU | **160 decks/s** | **~15 hours** |
| Embedding | 250M slides @ ~200 tok | 10 GPUs × ~1,200 slides/s | 12,000 slides/s | **~6 hours** |
| Segmentation | ~20 ms CPU/deck | trivial | — | negligible |
| LLM naming | 1 call, ~3.5k tok | 150 req/s sustained | 150 decks/s | **~16 hours** |
| Persistence | ~5 writes/deck | PG + Qdrant | 2,000/s | ~1.2 hours |

Stages run as a **pipeline**, so the wall clock is set by the slowest stage plus fill/drain, not the sum.

> **Estimate: ~20–24 hours at full throttle.**
> **Realistic plan: 5–10 days**, because we deliberately run at 30–50% capacity to protect live traffic, stay inside LLM quota, use spot capacity that gets reclaimed, and pause between waves for quality review.

The point of the estimate is not the number — it is that **extraction CPU and LLM request rate are the two bottlenecks**, so those are the two dials to buy more of. Embedding, famously assumed to be the hard part, is not.

## 10.6 Cost control during backfill

- **Hard budget ceiling** in the rate limiter: when cumulative spend for the day crosses the cap, the backfill consumer group pauses automatically. Live traffic is exempt.
- Track `cost_micros` per presentation → real-time `$/1k decks` dashboard. Alert if it exceeds the model by 25%.
- Backfill uses the **Batch API** (~50% cheaper, 24h SLA — completely acceptable for backfill). Live traffic uses the sync API.
- Extraction and embedding on **spot instances** (60–70% cheaper); Temporal makes reclaim events harmless.

## 10.7 Monitoring the campaign

A single dashboard: decks completed vs 10M, decks/hour, projected completion date, failure rate by `error_code`, DLQ depth, spend to date vs budget, and a rolling quality sample (100 random decks/day scored by LLM-as-judge). If the quality sample drops, **pause the backfill** — reprocessing 3M badly-themed decks is far more expensive than a day of lost throughput.

---

# 11. Cost Optimization

## 11.1 Where the money actually goes

Ranked, for the 10M backfill:

| Rank | Cost centre | Rough share | Why |
|---|---|---|---|
| 1 | **LLM calls** (10M × ~4k tokens) | 40–50% | Even at one call per deck, it's 35B+ tokens |
| 2 | **Extraction compute**, mostly rendering + OCR | 25–35% | LibreOffice is slow; OCR is slower; it's the CPU hog |
| 3 | **Embedding compute** | 10–15% | 250M inferences, but tiny model and huge batches |
| 4 | **Vector DB hosting** | 5–10% | Ongoing RAM cost, not one-off |
| 5 | **Storage (S3, PG)** | ~5% | Cheap; PG at 250M rows is the bigger piece |

**Illustrative order of magnitude** (plug in your own vendor prices):
- LLM: 8.5M calls × (3.5k in + 0.5k out). At a small-model batch price of ~$0.13/M in, ~$0.63/M out → ~$4k–$6k. At a mid-tier model's price, 5–10× that. **Model choice moves this number by an order of magnitude — it is the single biggest lever in the design.**
- Extraction: ~12,000 CPU-hours blended, on spot ≈ $0.01–0.02/vCPU-hr → ~$2k–4k.
- Embedding: ~60 GPU-hours on spot ≈ $500.
- **Total backfill: roughly $10k–30k** with a small model; **$100k+** if you route everything to a frontier model. This is why §4's "one LLM call per deck" decision matters more than any micro-optimization.

## 11.2 The optimization levers, in order of impact

| # | Lever | Saving | How |
|---|---|---|---|
| 1 | **One LLM call per deck, not per slide** | ~25× | The core architecture decision (§4.2) |
| 2 | **Right-size the model** | 5–20× | Small/cheap model for naming+summarizing an outline; it's an easy task. Reserve a bigger model for the ~5% of decks with `confidence < 0.5`. |
| 3 | **Outline, not full text, in the prompt** | 4–5× tokens | §6.1 |
| 4 | **Batch API for backfill** | ~50% | 24h SLA is fine offline |
| 5 | **File-level dedup by content hash** | 10–20% of everything | Free result copy |
| 6 | **Slide-level embedding cache by `text_hash`** | 20–40% of embedding | Template slides repeat massively across a corpus |
| 7 | **OCR only when text is sparse** | 50–70% of extraction | §3.3 routing |
| 8 | **Self-hosted embeddings** | 5–10× vs API | Batched GPU inference is very cheap per item |
| 9 | **Skip the LLM for trivial decks** | ~10% of calls | <6 slides, or native sections present |
| 10 | **Prompt caching for the system prompt** | 5–10% of input tokens | Identical prefix on 10M calls |
| 11 | **Spot instances** | 60–70% of compute | Safe because the workflow is checkpointed |
| 12 | **Incremental reprocessing** | Large, ongoing | On re-upload/edit, only re-embed changed slides and re-run segmentation; skip extraction of unchanged slides (§14) |
| 13 | **int8 quantization in Qdrant** | ~75% of vector RAM | Negligible recall loss at this task |

## 11.3 Things that look like savings but aren't

- **Skipping speaker notes** to save tokens — notes are often the highest-signal text; you lose quality to save ~3%.
- **Sub-chunking slides** — multiplies embedding count with no segmentation benefit.
- **Indexing all 250M slide vectors "because we might need them"** — 5× the vector DB bill for a hypothetical feature.
- **Aggressively cutting embedding dimensions to 256** — saves storage that was already cheap, costs measurable segmentation accuracy.

---

# 12. Quality and Evaluation

## 12.1 The metrics that matter

### Segmentation quality (are the boundaries right?)

> **Concept in one sentence:** WindowDiff and P_k are standard text-segmentation scores that slide a window across the document and count how often the predicted number of boundaries in the window differs from the true number — so a boundary that's off by one slide is penalized gently, not treated as a total miss.

| Metric | Target | Notes |
|---|---|---|
| **WindowDiff** (lower is better) | < 0.20 | The primary segmentation metric. Tolerant of near-misses, which matters because humans disagree by ±1 slide. |
| **Boundary F1 (±1 slide tolerance)** | > 0.75 | Intuitive to explain to product stakeholders |
| **Theme-count error** \|k_pred − k_true\| | ≤ 1 for 85% of decks | Catches over/under-segmentation |
| **Slide assignment accuracy** | > 0.85 | % of slides in the correct theme after optimal theme matching |

### Cluster/theme quality (are the groups coherent?)

| Metric | Definition |
|---|---|
| **Theme coherence** | Mean cosine of member slides to the theme centroid. Cheap, computable on 100% of production traffic, and a great drift monitor. |
| **Theme separation** | Mean cosine between adjacent theme centroids (lower = more distinct). |
| **Theme coverage** | % of slides assigned to a non-"Miscellaneous" theme. Target > 95%. |

### Summary quality

| Metric | How measured |
|---|---|
| **Groundedness / hallucination rate** | Automated number check (any digit in the summary must appear in slides) + LLM judge. **Target < 2%.** |
| **Name quality** | Human 1–5 rating: is the name specific, accurate, and 2–5 words? |
| **Summary usefulness** | Human 1–5: would this help someone decide whether to read the section? |
| **Duplicate names within a deck** | Should be ~0; a symptom of over-segmentation |

### System quality

| Metric | Target |
|---|---|
| End-to-end latency (upload → themes ready), p95 | < 2 min |
| Processing success rate | > 98% |
| Cost per presentation | < $0.005 |
| LLM fallback rate (extractive) | < 3% |

## 12.2 Building the golden evaluation dataset

**Target: 1,000 decks.** This is the highest-leverage week of work in the whole project — everything else is guesswork without it.

1. **Sample stratified, not random.** Explicitly include: short (5–8 slides), typical (15–30), huge (100+), image-heavy, text-heavy, non-English, decks with tables/charts, and decks with native sections (their author-defined sections are **free ground truth** — mine these first; they can supply several hundred labelled examples with zero annotation cost).
2. **Annotation task, simplified for humans.** Show a grid of slide thumbnails + titles. Ask only: *"Draw lines where a new section starts, and give each section a short name."* Do not ask for summaries — too slow, too subjective.
3. **Double-annotate 200 decks** by two people. Measure inter-annotator agreement (WindowDiff between humans). **This is your ceiling.** If humans only agree at WindowDiff 0.15, a model at 0.18 is essentially at human level, and chasing 0.05 is wasted effort. Reporting this number prevents a lot of pointless work.
4. **Split:** 200 dev (tune λ, thresholds, window size) / 800 test (touch rarely — it's your integrity check).
5. **Version the golden set** and re-annotate a slice quarterly as the corpus evolves.
6. **Add a regression set** of ~50 decks that previously failed in interesting ways. Every bug fixed becomes a permanent test case.

## 12.3 LLM-as-a-Judge

> **Concept in one sentence:** LLM-as-a-judge means using a second, usually stronger, model to score the first model's output against a rubric — cheap, fast, and scalable compared to human review.

**Use it for:**
- **Groundedness:** "Here are the slides. Here is the summary. Is every claim supported? Answer `supported` / `partially` / `unsupported` with the offending sentence." → this is the single best use; it's a near-verification task and models are reliable at it.
- **Name appropriateness:** score 1–5 with a rubric and 3 few-shot examples.
- **Pairwise comparison** during prompt iteration: "Which of these two summaries is better for this section?" — models are much more reliable at A/B than at absolute scoring.
- **Continuous monitoring:** judge 100 random production decks/day; alert on drift.

**Limitations — be honest about them:**

| Limitation | Mitigation |
|---|---|
| **Position bias** (prefers the first option in A/B) | Randomize order; run both orders and average |
| **Self-preference** (a model favours its own style) | Use a *different* model family as judge than as generator |
| **Verbosity bias** (longer looks better) | Constrain both candidates to similar length; state length limits in the rubric |
| **Scores cluster at 4/5** | Force a rubric with concrete anchors per score; prefer pairwise |
| **Judges are bad at segmentation** | **Never** use an LLM judge for boundary quality — that's what WindowDiff against human labels is for. Judges evaluate text, not structure. |
| **Correlation with humans is assumed, not proven** | **Calibrate:** run the judge on the 200 double-annotated golden decks and report judge↔human correlation. If it's below ~0.7, don't trust the judge for that dimension. |
| **Cost/latency at scale** | Sample (1%), don't judge everything |

**Rule of thumb:** the judge is a *regression detector and prioritizer*, not the source of truth. Ship decisions get a human review of 100+ decks. The judge tells you *which* 100 to look at.

## 12.4 Online signals (once the feature ships)

The strongest evaluation is user behaviour: theme click-through rate, "jump to section" usage, a lightweight 👍/👎 on each theme, manual theme-edit rate (if editing is offered), and search CTR on theme-matched results. Wire these from day one — a 👎 rate by tenant/language/deck-size cohort finds failure modes no offline set will.

---

# 13. Handling Difficult Presentations

| Case | Handling |
|---|---|
| **Very large (200–1000 slides)** | Segmentation is O(n²) but n is small — fine. Two-level themes (parents + children, §4.3). LLM input stays ~3k tokens via centroid-sampled slides. Hard cap at 1,500 slides → `SKIPPED(TOO_LARGE)` with a manual review flag. |
| **Almost no text** | If total deck text < 200 chars: render + OCR everything, then vision-caption up to 10 slides. If still empty → single theme named from the file name/deck title, `confidence = 0.2`, `status = LOW_CONFIDENCE`. Do not show low-confidence themes in the UI by default. |
| **Image-heavy** | Routed to OCR then vision captioning (§3.3). Slide vector is built from the caption text. Quality is lower; we flag it (`derived_from = vision`) so downstream consumers can discount it. |
| **Duplicate files** | `content_hash` match at ingest → copy themes, zero compute (§10.3). |
| **Duplicate/repeated slides inside a deck** | Detect identical `text_hash` within the deck. Repeated *template* content is stripped at the boilerplate step (§3.4). Repeated *content* slides (e.g. a recurring agenda) become explicit boundary evidence, not cluster members — an agenda slide reappearing usually *marks* a new section. |
| **Unrelated slides** | Low `relevance_score`; absorbed by the nearest neighbour theme (runt rule). If a theme's cohesion < 0.35, name it "Additional Material" and drop confidence. |
| **Very similar slides across the whole deck** (one topic throughout) | The penalized objective naturally chooses k=1. That's correct — some decks are one theme. Guard: never force k>1. Output one theme covering the deck. |
| **Slides in multiple themes** | Primary + secondary link via `is_primary` (§5.9). |
| **Tables/charts** | Extracted structurally, not as pixels (§3.2). Series names and headers become text. We never send raw data grids to the embedding model — they are noise. |
| **Poor OCR** | `ocr_confidence < 0.6` → down-weight the OCR text in the slide card (include it, but after the real text and truncated first). If a whole deck is low-confidence OCR, flag `LOW_CONFIDENCE` and exclude from search indexing until reviewed. |
| **Mixed languages** | Multilingual embedding model handles cross-language similarity natively (a Spanish and an English slide about pricing land near each other). Detect the deck's dominant language; instruct the LLM to write names/summaries in that language. Store `language` on the presentation for filtering and for language-specific quality dashboards. |
| **Corrupted / password-protected / macro-laden** | Fail fast, no retry, `error_code = CORRUPT_FILE / ENCRYPTED`. Never execute macros. Parse in a sandbox with no network and a hard CPU/wall-clock limit — a malformed zip bomb should kill one container, not a worker fleet. |
| **Zero slides / 1 slide** | Single theme, name = title. Skip the LLM. |

**Cross-cutting principle:** every difficult case degrades to *something useful with a low confidence score* rather than to an error. A user seeing "Slides 1–20: Presentation Content" is mildly disappointed; a user seeing a spinner forever is lost.

---

# 14. Versioning and Reprocessing

## 14.1 What gets versioned

Three independent version axes, all recorded:

| Axis | Field | Changes when |
|---|---|---|
| `extraction_version` | on `slides` | Parser logic, OCR engine, slide-card format changes |
| `embedding_model_version` | in `embedding_ref` + Qdrant collection name | New embedding model |
| `pipeline_version` | on `themes`, `presentation_processing` | **Any** change to prompts, LLM model, clustering, thresholds |

`pipeline_version` is the umbrella. A change to any component bumps it, because a theme's quality is a function of the whole chain.

Store the full recipe so any result is explainable years later:

```json
"pipeline_version": "v3",
"config": {
  "extraction_version": "e2",
  "embedding_model": "bge-m3@1024",
  "segmentation": {"algo": "ward-adjacent+dp", "lambda": 0.03, "window": 2,
                   "min_theme": 2, "max_theme": 15, "max_themes": 8},
  "llm": {"model": "small-v2", "prompt_hash": "a91f...", "temperature": 0.2}
}
```

## 14.2 Regenerating without breaking existing data

**Never mutate. Always write a new version and flip a pointer.**

```
1. Deploy v4 code. v3 remains ACTIVE and served.
2. Shadow run v4 on the 1,000-deck golden set → compare metrics vs v3.
   Gate: WindowDiff must not regress; hallucination rate must not rise.
3. Shadow run v4 on 10k random production decks. Diff v3 vs v4 themes.
   Review the 100 decks that changed most. This "diff review" catches
   the failures that aggregate metrics hide.
4. Canary: serve v4 to 1% of tenants. Watch 👎 rate and theme CTR for a week.
5. Ramp 1% → 10% → 50% → 100% by flipping is_active per presentation in batches.
6. Keep v3 rows for 90 days. Rollback = one UPDATE flipping is_active back.
7. After 90 days, archive v3 rows to S3 and delete from Postgres.
```

The API always reads `WHERE is_active` — it never knows which version it's serving. That indirection is what makes rollback a one-line operation instead of a re-run.

## 14.3 Cost-aware reprocessing (what to skip)

| What changed | Re-extract? | Re-embed? | Re-segment? | Re-LLM? | Cost of a full 10M pass |
|---|---|---|---|---|---|
| Prompt wording | ✗ | ✗ | ✗ | ✓ | ~50% of original |
| LLM model | ✗ | ✗ | ✗ | ✓ | ~50% |
| Clustering params | ✗ | ✗ | ✓ | ✓ | ~50% |
| Embedding model | ✗ | ✓ | ✓ | ✓ | ~70% |
| Parser/OCR fix | ✓ | ✓ | ✓ | ✓ | 100% |
| Theme *definition* changes | ✗ | ✗ | ✓ | ✓ | ~50% + new golden labels |

This table is the whole reason we persist `slides.json` and the embedding parquet in S3. **Most upgrades never touch the two most expensive stages.** A prompt improvement across 10M decks costs a few thousand dollars and a weekend, not a re-run of the entire campaign.

Reprocessing runs through the **same** backfill machinery (§10) — same queue, same checkpointing, same prioritization (hot decks first). No separate code path.

## 14.4 Handling changed theme definitions

If the product decides themes should be finer-grained ("we want 8–12, not 3–5"), that's a **product change, not a bug**: bump `pipeline_version`, re-annotate a slice of the golden set to the new definition (otherwise you'll measure the new model against the old definition and conclude it got worse), retune λ and `max_themes`, and roll out via §14.2.

## 14.5 Handling edited/re-uploaded presentations

Treat it as a new version of the presentation. Compute per-slide `text_hash` against the previous version: unchanged slides reuse their cached embeddings, changed slides are re-embedded, and segmentation + one LLM call re-run. A 3-slide edit to a 60-slide deck costs roughly the LLM call alone.

---

# 15. API Design

All endpoints are tenant-scoped and enforce document-level authorization (§17).

### `GET /v1/presentations/{presentation_id}/themes`
**Purpose:** the main read path — everything the UI needs to render the theme sidebar in one call.

```http
GET /v1/presentations/p_8f21/themes?include_slides=true
200 OK
{
  "presentation_id": "p_8f21",
  "status": "COMPLETED",
  "pipeline_version": "v3",
  "generated_at": "2026-08-20T10:14:22Z",
  "slide_count": 20,
  "themes": [
    {"theme_id":"t_01","order":1,"name":"Introduction",
     "summary":"Introduces the company and the settlement-delay problem.",
     "keywords":["fintech","payments","problem"],
     "slide_range":[1,4],"slides":[1,2,3,4],"confidence":0.82}
  ]
}
```

- `202 Accepted` with `{"status":"PROCESSING","eta_seconds":45}` when not ready — the client polls or listens for the websocket/SSE event. Never block.
- `include_slides=false` (default) omits the slide arrays for lighter payloads.
- ETag on `(presentation_id, pipeline_version, generated_at)` for cheap client caching.

### `GET /v1/presentations/{presentation_id}/themes/{theme_id}`
**Purpose:** detail view for one section — slides with per-slide relevance, thumbnails, and full text.

```json
{"theme_id":"t_02","name":"Market Analysis","summary":"...",
 "confidence":0.79,"cohesion_score":0.71,"generated_by":"llm",
 "slides":[{"slide_index":5,"title":"Market size: $12B SEA payments",
            "relevance_score":0.88,"is_primary":true,
            "thumbnail_url":"https://.../s5.png"}]}
```

### `POST /v1/presentations/{presentation_id}/reprocess`
**Purpose:** force regeneration — used by support, by the "themes look wrong" button, and by internal backfill tooling.

```json
Request:  {"pipeline_version":"v4","force_extraction":false,"priority":"high",
           "reason":"user_reported_bad_themes"}
Response: 202 {"job_id":"j_77c1","status":"QUEUED",
               "status_url":"/v1/jobs/j_77c1"}
```
- Idempotent: a second call while a job is in flight returns the same `job_id`.
- Rate-limited per user (e.g. 5/hour) so it can't be used as a compute amplifier.
- Requires write permission on the document.

### Supporting endpoints

| Endpoint | Purpose |
|---|---|
| `GET /v1/jobs/{job_id}` | Processing status, stage, error code, ETA |
| `GET /v1/presentations/{id}/themes/versions` | List available versions (internal/debug) |
| `POST /v1/themes/{theme_id}/feedback` | `{"vote":"down","reason":"wrong_slides"}` — the online quality signal (§12.4) |
| `POST /v1/search/themes` | `{"query":"market sizing fintech","top_k":20}` → embed the query, search Qdrant with a `tenant_id` filter, hydrate from Postgres |
| `GET /v1/presentations/{id}/similar` | Recommendations via theme-vector similarity |
| `POST /internal/backfill/batches` | Admin: enqueue a backfill wave |

---

# 16. Reliability and Observability

## 16.1 What we measure

**Pipeline health**

| Metric | Type |
|---|---|
| `presentations_processed_total{stage,status,version}` | counter |
| `processing_duration_seconds{stage}` | histogram (p50/p95/p99) |
| `queue_depth{topic}` and consumer lag | gauge |
| `retry_count{stage,error_code}` | counter |
| `dlq_size{reason}` | gauge |
| `worker_utilization{pool}` | gauge |

**AI-specific**

| Metric | Why it matters |
|---|---|
| `llm_latency_seconds` p50/p95 | Vendor degradation shows up here first |
| `llm_tokens_total{direction,model}` | Drives the cost dashboard |
| `llm_error_rate{code}` (429 vs 5xx separately) | 429 means throttle; 5xx means retry |
| `llm_fallback_rate` (extractive summaries) | Silent quality decay indicator |
| `embedding_failures_total` | GPU OOM, batch too large |
| `extraction_failures_total{error_code}` | Parser bugs cluster by code |
| `ocr_invocation_rate` | Sudden rise = cost spike incoming |
| `cost_per_presentation_micros` | The number leadership asks about |

**Quality (the one most teams forget to instrument)**

| Metric | Computed on |
|---|---|
| `theme_cohesion` distribution | 100% of traffic — it's free math |
| `themes_per_presentation` distribution | 100% — a shift means the algorithm drifted |
| `low_confidence_rate` | 100% |
| `hallucination_rate` (judge sample) | 1% sample |
| `user_thumbs_down_rate{language,deck_size}` | 100% of feedback events |

## 16.2 Alerts

| Severity | Alert | Threshold |
|---|---|---|
| **P1 page** | Processing success rate | < 90% over 15 min |
| **P1 page** | DLQ growth | > 1,000 items/hour |
| **P1 page** | Consumer lag on `ingest.high` | > 30 min of work |
| **P1 page** | Postgres or Qdrant write errors | > 1% |
| **P2 ticket** | LLM p95 latency | > 20s for 10 min |
| **P2 ticket** | LLM 429 rate | > 5% for 10 min |
| **P2 ticket** | Cost/presentation | > 1.5× the 7-day baseline |
| **P2 ticket** | `llm_fallback_rate` | > 5% |
| **P2 ticket** | Mean theme cohesion | drops > 10% week-over-week |
| **P3 ticket** | `themes_per_presentation` mean | shifts > 20% after a deploy |
| **P3 ticket** | Thumbs-down rate | > 8% in any cohort |

**Distributed tracing:** one trace per presentation, spans per stage, `presentation_id` as a searchable attribute. When someone reports bad themes, an engineer pastes the ID and sees the whole life of that document — including the exact prompt sent and response received (from the S3 audit log).

**Runbooks** for the top failure modes: LLM vendor outage (→ switch to secondary provider / degrade to extractive), Qdrant unavailable (→ queue index writes, serve Postgres-only), backfill overrunning budget (→ pause consumer group), and DLQ triage.

**Deliberate degradation ladder:**
```
Everything healthy      → full quality
LLM slow/limited        → algorithmic themes now, LLM repair job later (PARTIAL)
Embedding service down  → pause; do NOT fall back to keyword clustering (worse than waiting)
Vector DB down          → themes still served from Postgres; only search/recs degrade
Extraction down         → hard stop; nothing downstream is meaningful
```

---

# 17. Security

| Area | Approach |
|---|---|
| **Access control** | Every API call resolves `tenant_id` + document ACL from the auth token. Themes inherit the parent document's permissions exactly — there is no separate theme ACL, because divergence is how leaks happen. |
| **Document isolation** | `tenant_id` is a mandatory filter in Postgres (enforced via row-level security, not just application code) and a mandatory Qdrant payload filter. A search must never return a theme from another tenant. This gets a dedicated integration test in CI. |
| **Encryption** | TLS 1.3 in transit; S3 SSE-KMS at rest with per-tenant keys for enterprise tiers; Postgres and Qdrant volumes encrypted. Access to raw decks only via short-lived presigned URLs. |
| **API security** | OAuth2/JWT, per-user and per-tenant rate limits, strict request validation, no internal IDs or stack traces in error bodies, audit log of every reprocess and admin action. |
| **Sensitive content** | Run a PII/secret detector over extracted text. Redact obvious secrets (keys, tokens) before anything leaves our network. Tenants can set `ai_processing = off` (no themes generated) or `ai_processing = local_only` (self-hosted models only). |
| **Third-party LLM exposure** | The real risk in this design. Mitigations: (a) contract with **zero data retention** and **no training on our data**; (b) send **outlines, not full decks** — an architectural choice that happens to minimize exposure; (c) never send images/files, only text; (d) route flagged-sensitive tenants to a self-hosted model; (e) region-pinned endpoints for data-residency obligations. |
| **Logging hygiene** | Logs contain IDs, counts, and error codes — **never slide text**. The prompt/response audit log lives in a separate, restricted, encrypted S3 bucket with a 90-day lifecycle and its own access review. |
| **Sandboxing** | LibreOffice, python-pptx, and OCR run in containers with no network egress, read-only root FS, dropped capabilities, seccomp, and hard CPU/memory/wall-clock limits. Office parsers are a known exploit surface; assume any uploaded file is hostile. |
| **Deletion** | User deletes a deck → cascade delete slides, themes, `theme_slides`, Qdrant points, S3 objects, and cached embeddings, within the GDPR window. A `deletion_jobs` table tracks completion across all stores, because "we deleted it from Postgres" is not deletion. |

---

# 18. Final Recommended Architecture

## 18.1 The improved flow

The original flow in the brief is correct in outline. Five improvements:

| # | Improvement | Why |
|---|---|---|
| 1 | **Dedup + native-section check right after upload** | Skips 15–25% of all work before it starts |
| 2 | **Explicit Slide Card step** between extraction and embedding | Boilerplate stripping and consistent formatting are where embedding quality is won |
| 3 | **Segmentation is order-aware, not generic clustering** | Preserves slide order by construction |
| 4 | **One LLM call per deck that does naming + summarizing + boundary repair together** | 25× cheaper than per-slide; cross-section context yields distinct names |
| 5 | **Validation + fallback gate after the LLM** | The system degrades to useful output instead of failing |
| 6 | **Only theme vectors go to the vector DB; slide vectors go to S3 Parquet** | 5× smaller vector cluster, better search relevance |

```text
                    Presentation (.ppt / .pptx)
                              ↓
                    Upload Service ──► sha256 dedup ──► [HIT: copy themes, done]
                              ↓
                       Object Storage (S3)
                              ↓
                    Kafka  (high / backfill lanes)
                              ↓
                    Temporal workflow per presentation
                              ↓
   ┌──────────────────────────────────────────────────────────┐
   │ Content Extraction                                        │
   │  .ppt→.pptx │ python-pptx │ notes/tables/charts           │
   │  conditional render+OCR │ conditional vision caption      │
   │  native PowerPoint sections detected  ──────────┐         │
   └──────────────────────────┬──────────────────────│─────────┘
                              ↓                      │ (if present,
                    Slide Representation             │  skip detection)
                    ("Slide Card" + boilerplate strip)│
                              ↓                      │
                    Embedding Generation (BGE-M3, GPU, cached)
                              ↓                      │
                    Semantic Similarity (smoothed block depth)
                              ↓                      │
                    Order-Aware Segmentation ◄───────┘
                    (adjacency-constrained Ward + DP refinement)
                              ↓
                    Theme Formation (size/count guardrails, outliers)
                              ↓
                    LLM Naming + Summarization  (1 call / deck)
                              ↓
                    Validation & Grounding Gate → [fail → extractive fallback]
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   PostgreSQL           Qdrant (theme          S3 (slides.json,
   (themes, slides,      vectors, int8)         embeddings.parquet,
    links, status)                              LLM audit)
        └─────────────────────┼─────────────────────┘
                              ↓
        Search  │  Recommendations  │  Doc Understanding  │  Future AI
```

## 18.2 What / Why we need it / Why we chose it

| Component | What it does | Why we need it | Why this choice |
|---|---|---|---|
| **S3** | Stores raw decks, extracted JSON, embeddings, audit logs | Source of truth for reprocessing | Cheap, durable (11 nines), lifecycle tiering, everything integrates with it |
| **PostgreSQL** | Themes, slides, links, processing state | Relational reads and transactional writes for the product API | Mature, joins, partitioning, RLS for tenant isolation; the team already runs it |
| **Kafka** | Durable work buffer with priority lanes | Decouples upload rate from processing rate; lets other teams consume completion events | Replayable, high throughput, consumer groups map cleanly to priority lanes |
| **Temporal** | Per-presentation workflow state, retries, resumption | 10M items × 5 stages will fail constantly; resuming mid-workflow avoids re-paying for finished stages | Durable execution, built-in retry/timeout, visibility into stuck items |
| **python-pptx + LibreOffice** | Parse and convert decks | The only reliable way to read the formats | python-pptx is fast and pure-Python for pptx; LibreOffice covers legacy `.ppt` and rendering |
| **PaddleOCR** | Text from images | ~15% of slides carry text only as pixels | Strong multilingual + rotated-text support, runs on CPU |
| **BGE-M3 (self-hosted, GPU)** | Slide → vector | Cheap semantic similarity is the backbone of segmentation | Multilingual, strong on short text, ~10× cheaper than an API at 250M items |
| **scikit-learn + numpy** | Segmentation | Order-aware grouping | `AgglomerativeClustering` with a connectivity matrix does exactly what we need in a few lines; deterministic and testable |
| **Small/cheap LLM** | Names + summaries | Only an LLM writes human-quality labels | The task (label an outline) is easy; a small model is 5–20× cheaper and the cost driver of the whole system |
| **Qdrant** | Theme-vector search | Powers search and recommendations | Fast HNSW, first-class payload filtering (needed for `tenant_id`), int8 quantization, easy to self-host |
| **Redis** | Rate limiting, dedup cache, embedding cache | Prevents 500 workers from blowing the LLM quota | Fast, simple, standard |
| **Prometheus + Grafana + OTel** | Metrics, dashboards, traces | You cannot operate a 10M-item pipeline blind | Standard, cheap, good alerting |

## 18.3 Must Have → Nice to Have → Future

### ✅ Must Have (v1 — ship this)
- pptx + ppt extraction with notes, tables, charts, and conditional OCR
- Slide Card representation with boilerplate stripping
- Self-hosted embeddings with a text-hash cache
- Order-aware segmentation with size/count guardrails
- One LLM call per deck for names + summaries, with schema validation and grounding checks
- Extractive fallback (never fail to produce something)
- Postgres schema with `pipeline_version` and `is_active`
- Kafka + Temporal + idempotent claim + DLQ
- Content-hash dedup
- Backfill with waves, checkpointing, budget cap, and a canary
- 1,000-deck golden set + WindowDiff/boundary-F1 + inter-annotator ceiling
- Core dashboards and P1 alerts
- Tenant isolation enforced in both Postgres and Qdrant

### 🟡 Nice to Have (v1.5)
- Vision captioning for image-only slides
- Non-contiguous theme spans (§5.8)
- Two-level themes for 100+ slide decks
- Theme-vector search and "similar decks" recommendations
- LLM-as-judge continuous monitoring
- Confidence-based routing to a larger model for the worst 5%
- User feedback (👍/👎) and manual theme editing
- Cross-deck theme taxonomy (canonical theme names across the library)

### 🔵 Future
- Fine-tuned segmentation model trained on the golden set + accumulated user edits — the natural v2 that beats the heuristic
- Distilled small model fine-tuned on frontier-model summaries (10× cheaper at equal quality)
- Multimodal slide embeddings (image + text in one vector), removing the OCR/vision hop
- Extend to PDF and Google Slides
- Theme-level Q&A and RAG over the library
- Auto-generated deck outlines, chapter navigation, and "read just this section" features
- Personalized theme naming per tenant vocabulary

---

# Appendix A: Architecture Diagram (one page)

```text
 ┌────────────┐   upload    ┌──────────────┐   sha256 dedup hit → copy themes ✔
 │   Client   ├────────────►│Upload Service├──────────────────────────────────►
 └────────────┘             └──────┬───────┘
                                   │ miss: S3 put + PG insert + event
                                   ▼
                 ┌─────────────────────────────────┐
                 │ Kafka                            │
                 │  ingest.high     (live, 70% SLA) │
                 │  ingest.backfill (10M campaign)  │
                 └───────────────┬─────────────────┘
                                 ▼
                 ┌─────────────────────────────────┐
                 │ Temporal: ProcessPresentation    │
                 │  claim (pid, version) idempotent │
                 └───┬───────┬───────┬───────┬─────┘
             extract │ embed │ segment│ summarize│ persist
                     ▼       ▼       ▼        ▼      ▼
   ┌───────────┐ ┌────────┐ ┌──────┐ ┌──────────┐ ┌─────────────┐
   │CPU pool   │ │GPU pool│ │ CPU  │ │ LLM pool │ │ PG + Qdrant │
   │pptx/OCR   │ │BGE-M3  │ │Ward+ │ │small LLM │ │ + S3        │
   │sandboxed  │ │batched │ │  DP  │ │ +guardrail│ │ txn write   │
   └─────┬─────┘ └───┬────┘ └──┬───┘ └────┬─────┘ └──────┬──────┘
         │           │         │          │              │
      slides.json  parquet   themes    names/summaries  themes.ready
         │           │                                    │
         └───────────┴──────────► S3 ◄────────────────────┘
                                                          ▼
                        ┌──────────────────────────────────────────┐
                        │ Search API │ Recommendations │ Doc AI     │
                        └──────────────────────────────────────────┘
   Cross-cutting: Redis (rate limit + caches) │ Prometheus/Grafana/OTel │
                  DLQ + replay tooling        │ Budget guard            │
```

# Appendix B: End-to-End Data Flow

```
1  Client uploads deck.pptx
2  Upload Service streams to s3://decks/<hash>.pptx, computes sha256
3  Dedup: hash exists? → copy themes, respond COMPLETED, STOP
4  INSERT presentations, presentation_processing(status=PENDING, version=v3)
5  Produce Kafka event {presentation_id, s3_key, priority}
6  Temporal workflow starts; claims (pid, v3) with a conditional UPDATE
7  EXTRACT: .ppt→.pptx if needed → python-pptx → per-slide text, notes,
   tables, charts, layout, native sections → sparse slides rendered + OCR'd
   → slides.json to S3, INSERT slides rows
8  REPRESENT: build Slide Cards, strip boilerplate, hash each card
9  EMBED: cache lookup by text_hash → miss → GPU batch → vectors
   → embeddings.parquet to S3, embedding_ref on slides
10 SEGMENT: smoothed block-depth + layout signals → adjacency-constrained
   Ward + DP refinement → k* by penalized objective → guardrails
   → candidate themes with cohesion scores
11 SUMMARIZE: build compact outline (~3k tokens) → 1 LLM call →
   JSON {name, summary, keywords, confidence, boundary_feedback}
12 VALIDATE: schema → range coverage/disjointness → number grounding
   → pass? use it : retry once : extractive fallback
13 PERSIST (one txn): delete themes(pid,v3) → insert themes + theme_slides
   → compute theme centroids → upsert Qdrant → status=COMPLETED
14 EMIT presentations.themes.ready → search indexer, rec service, UI push
15 SERVE: GET /presentations/{id}/themes reads active version from PG
```

# Appendix C: Schema Summary

```
presentations ──1:N──► slides ──N:M──► themes
      │                   │      via theme_slides
      │                   │
      └──1:N──► presentation_processing (per pipeline_version)

S3:      decks/<hash>.pptx │ extracted/<pid>/slides.json
         embeddings/<pid>.parquet │ renders/<pid>/s<n>.png
         llm-audit/<date>/<pid>.json

Qdrant:  theme_vectors_v3 — vector(1024, cosine, int8)
         payload: theme_id, presentation_id, tenant_id, theme_order,
                  language, slide_count, pipeline_version, is_active

Redis:   ratelimit:llm:tokens │ emb:<text_hash> │ dedup:<content_hash>
```

Full DDL in §7.2.

# Appendix D: AI Pipeline Summary

```
Slide Card (≤400 tok)
   └─► BGE-M3 embedding (1024-d, L2-normalized, title-boosted 0.7/0.3)
         └─► depth(i) = 1 − cos(mean(left window), mean(right window))
               + layout/agenda/numbering boundary bonuses
               └─► adjacency-constrained Ward clustering
                     └─► DP boundary refinement (decks ≥15 slides)
                           └─► k* = argmax [cohesion(k) − λk], k ∈ [k_min, k_max]
                                 └─► guardrails: min 2, max 15, ≤8 themes
                                       └─► ONE LLM call: outline → names,
                                           summaries, keywords, confidence
                                             └─► validation + grounding gate
                                                   └─► themes + centroids
```

**LLM budget: 1 text call per presentation. 0 text calls per slide.**
**Vision calls: only for text-free slides, capped at 6 per deck (~3–5% of slides).**

# Appendix E: 10M Backfill Strategy (one page)

```
Wave 0: 5k canary        → manual review → GO/NO-GO
Wave 1: 500k hottest     → ship the feature
Wave 2: paying tenants
Wave 3: last 2 years
Wave 4: long tail (spot capacity, weeks, low priority)

Mechanics
  • Enumerate by keyset cursor into 1,000 batches of 10k (backfill_jobs table)
  • Publish to ingest.backfill (64 partitions), dedicated consumer group
  • Dedup by content_hash first  → ~8.5M decks actually processed
  • Claim (pid, version) → exactly-once effect despite at-least-once delivery
  • Checkpoint per batch; resume = "start from last DONE batch"
  • Budget guard pauses the consumer group at the daily cost ceiling
  • Live traffic has separate workers + LLM quota; backfill always yields
  • Batch LLM API (~50% off), spot instances for CPU/GPU (~65% off)

Throughput (blended)
  extraction  800 vCPU  → ~160 decks/s  → ~15 h   ← bottleneck #1
  embedding   10 GPUs   → 12k slides/s  → ~6 h
  LLM         150 rps   → 150 decks/s   → ~16 h   ← bottleneck #2
  persistence 2k/s      →               → ~1 h

Full throttle: ~20–24 hours.  Realistic plan: 5–10 days across waves.
Order-of-magnitude cost: $10k–30k with a small LLM; $100k+ with a frontier one.
```

# Appendix F: Key Trade-offs

| Decision | We chose | We gave up | Why it's right here |
|---|---|---|---|
| Segmentation vs free clustering | Order-aware segmentation | Ability to group non-adjacent slides by default | Decks are linear; users expect ranges. Non-adjacent is opt-in. |
| LLM per deck vs per slide | Per deck | Some per-slide nuance | 25× cost reduction; per-slide nuance isn't visible in a section label |
| Small LLM vs frontier | Small, with escalation for low-confidence 5% | A few % of summary polish | The task is easy; model choice is the dominant cost term |
| Self-hosted vs API embeddings | Self-hosted | Ops burden of a GPU service | 5–10× cheaper at 250M items; also better for sensitive tenants |
| Theme vectors only in Qdrant | Theme vectors | Slide-level similarity search | 5× smaller cluster; slide vectors kept in S3, indexable later |
| Heuristic segmentation vs trained model | Heuristic | Several points of accuracy | No labelled data on day one. The golden set makes the trained v2 possible. |
| Async vs sync | Async | Instant themes on upload | Nobody needs themes in 2 seconds; async makes cost and reliability tractable |
| Store slides.json + embeddings | Store them | ~$3–5k/yr of S3 | Turns most future model upgrades from a full re-run into a cheap partial one |
| Temporal vs plain queues | Temporal | Extra infra to run | Resumable per-stage retries save real money at 10M items |
| Degrade vs fail | Always degrade | Occasional mediocre themes | A low-confidence theme beats an error state for the user |

# Appendix G: Top 5 Engineering Risks

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| 1 | **Extraction quality is worse than assumed** — SmartArt, grouped shapes, and text-as-image are more common than 15%, so slide cards are thin and every downstream stage degrades | High. Silent, corpus-wide quality failure. | Measure `char_count` distribution on 10k real decks **before** designing thresholds; instrument `ocr_invocation_rate` and `is_empty` rate; treat extraction as the first thing to fix when quality complaints arrive |
| 2 | **Nobody agrees what a "correct" theme is** — the golden set is built to one definition, the product wants another, and the metric moves without quality moving | High. Wasted quarters. | Lock the theme definition with product **before** annotation; measure the inter-annotator ceiling and publish it; re-annotate when the definition changes |
| 3 | **Cost overrun during backfill** — a token estimate off by 3× or an OCR rate off by 2× turns $20k into $150k mid-campaign | High, and discovered late | Hard daily budget guard that pauses consumers; per-deck cost metric from day one; canary wave with measured (not estimated) cost/deck before Wave 1 |
| 4 | **LLM vendor dependency** — rate limits cap backfill throughput, a price change breaks the model, an outage stalls the pipeline, or output format drifts after a silent model update | Medium-High | Pin model versions explicitly; keep a second provider behind an abstraction; extractive fallback means an outage degrades rather than halts; contract for quota before the campaign |
| 5 | **Reprocessing 10M decks proves impractical** — a v2 model exists but the campaign is too slow/expensive to re-run, so quality freezes at v1 | Medium, compounding over years | Persist `slides.json` + embeddings so most upgrades skip extraction; version-and-flip design; prioritized reprocessing (hot decks first, tail maybe never) |

*Honourable mentions:* Postgres bloat at 250M+ slide rows (partition early), Qdrant memory growth as the library doubles, and a poisoned/hostile pptx crashing extraction workers (sandboxing is not optional).

# Appendix H: Final Recommended Technology Stack

| Layer | Technology | One-line reason |
|---|---|---|
| Language | Python 3.11 (pipeline), Go or Python (API) | The document/AI ecosystem is Python |
| Object storage | AWS S3 | Cheap, durable, tiered |
| Relational DB | PostgreSQL 16, partitioned, with read replicas | Joins, transactions, RLS, partition pruning |
| Vector DB | Qdrant (self-hosted), int8-quantized HNSW | Fast filtered search; `tenant_id` filtering is first-class |
| Message bus | Kafka (or SQS + SNS for a smaller team) | Durable buffer with priority lanes and replay |
| Orchestration | Temporal | Resumable, per-stage retries at 10M scale |
| Cache / limiter | Redis | Token buckets, embedding cache, dedup |
| Deck parsing | python-pptx | Fast, reliable, pure Python |
| Legacy `.ppt` + rendering | LibreOffice headless (sandboxed) | The only practical converter/renderer |
| OCR | PaddleOCR (CPU) | Multilingual, handles rotated text |
| Embeddings | BGE-M3 (or multilingual-e5-large) on GPU via vLLM/TEI | Multilingual, strong on short text, cheap in batch |
| Clustering | scikit-learn `AgglomerativeClustering` + custom DP, numpy | Adjacency constraint in one parameter; deterministic |
| LLM | Small/cheap instruct model (batch API for backfill), abstracted behind a provider interface | The task is easy; cost dominance makes size the key lever |
| Vision (rare) | Small vision model, capped per deck | Only for text-free slides |
| Serving | Kubernetes with separate node pools (CPU spot, GPU spot, LLM-caller) | Independent scaling per bottleneck |
| Observability | Prometheus, Grafana, OpenTelemetry, Loki | Standard, cheap, good alerting |
| Evaluation | Golden set in S3/DVC + a nightly eval job + LLM-as-judge sampling | Quality regressions must be caught automatically |
| CI/CD | GitHub Actions, versioned pipeline configs, shadow-run gate before promotion | No `pipeline_version` ships without passing the golden set |

---

## Closing note

The whole design rests on one idea worth repeating: **use cheap deterministic math for the structural decision (where do sections start and end) and the expensive model only for the linguistic decision (what should we call this section).** That single split is what makes 10 million presentations affordable, testable, resumable, and improvable — and it is the difference between a demo that works on one deck and a system a team can actually run.
