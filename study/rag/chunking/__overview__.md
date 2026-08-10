Here's the full detail on each, drawn from Chapter 6, "RAG and Agents" → *Retrieval Optimization* → *Chunking strategy* (pp. 267–269).

## 1. Fixed-length chunking

The simplest approach: split documents into chunks of equal length, measured in a unit you choose. The book names four candidate units:

- **Characters** — e.g., every 2,048 characters becomes a chunk. Unit-agnostic, works identically regardless of language or content.
- **Words** — e.g., every 512 words. More linguistically meaningful than raw characters, but word count varies with how verbose the writing is.
- **Sentences** — e.g., every 20 sentences. Preserves grammatical units rather than cutting mid-sentence.
- **Paragraphs** — each paragraph becomes its own chunk. The coarsest of the four, but respects the author's own structural boundaries.

**The core weakness:** none of these units know anything about *meaning*. A fixed count of characters or words can still land in the middle of a thought, a table, or a list — the boundary is arbitrary with respect to content, only respecting the counting unit itself.

## 2. Recursive chunking

Splits using progressively smaller units, only descending further when a piece is still too large:

```
document → sections → (still too long?) → paragraphs → (still too long?) → sentences
```

You start coarse and only fragment further where necessary. The book's stated benefit: *"This reduces the chance of related texts being arbitrarily broken off."* The intuition — a section that's already short enough doesn't need to be shredded into sentences just because your pipeline defaults to sentence-level splitting; recursive chunking only cuts as finely as each specific piece of text requires. This makes it adaptive in a way fixed-length chunking isn't: dense sections get split further, naturally short ones are left intact.

## 3. Content-specific / creative chunking

Rather than a general algorithm, this is a category of splitters tailored to what the document actually is:

- **Programming-language-specific splitters** — code has its own structural units (functions, classes, blocks) that character or sentence counting would ignore or break apart mid-syntax.
- **Q&A documents** — split by question/answer pair, so each pair is one self-contained chunk. This preserves the unit that's actually meaningful for retrieval: a question separated from its answer is retrieval-useless.
- **Language-specific handling** — the book's example is that Chinese text needs different splitting logic than English. This gestures at a real technical issue: many chunking heuristics (word boundaries via whitespace, for instance) assume space-delimited languages and simply don't apply to languages that aren't.

The unifying idea here isn't a specific algorithm — it's the principle that the "right" chunk boundary is defined by the document's own internal structure, not a generic character/word/sentence count.

## 4. Token-based chunking

Chunk using the **generative model's own tokenizer** as the splitting unit. The book's worked example: if you're using Llama 3 as your generator, you first tokenize documents with Llama 3's tokenizer, then split on token boundaries rather than character or word boundaries.

**Benefit:** tighter alignment with the downstream model — since context limits and cost are measured in tokens, not characters or words, chunking in the same unit you'll be constrained by later avoids mismatches between "how big I thought this chunk was" and "how much context it actually consumes."

**Explicit tradeoff the book flags:** if you switch to a different generative model with a different tokenizer, you have to **reindex your entire dataset** — the chunk boundaries were defined by a tokenizer that no longer matches your new model. This is the one strategy the book pairs with a concrete cost, making it clear this isn't a free upgrade over the simpler unit choices.

## 5. Overlapping chunks

Not a fifth alternative to the four above — a modifier you layer on top of whichever one you pick. Instead of chunks butting up against each other with hard boundaries, adjacent chunks share a small region of overlapping text.

**Why it exists — the book's own example:** the sentence *"I left my wife a note"* split cleanly at the midpoint becomes *"I left my wife"* and *"a note"* — and neither fragment conveys the original meaning. A hard cut with no overlap can sever the exact information a query is looking for, right at the seam between two chunks. Overlap ensures that boundary-straddling information appears intact in at least one of the two adjacent chunks.

**Suggested proportion:** for a 2,048-character chunk size, the book suggests roughly 20 characters of overlap — a small fraction of the chunk, just enough to catch boundary content without meaningfully duplicating chunk contents across your whole index.

---

## Chunk size — cutting across all five

Whichever strategy you use, **how big** each chunk is interacts with the strategy rather than being independent of it:

- **Smaller chunks** → more chunks fit into the model's context window (halve the size, roughly double how many chunks fit) → the model sees a wider range of distinct information → **but** risk losing information that appears only once in a source document, if the relevant chunk isn't the one retrieved; and computational cost rises, since embedding-based retrieval now has twice as many vectors to generate, store, and search.
- **Larger chunks** → less risk of splitting an idea awkwardly, cheaper to index → but coarser retrieval granularity, and fewer distinct chunks can be packed into the same context budget.
- **Hard ceiling either way:** chunk size can never exceed the generative model's context length, and for embedding-based retrieval, it additionally can't exceed the embedding model's own context limit — whichever of the two is smaller becomes your real ceiling.

The book closes this subsection without prescribing a default: *"There is no universal best chunk size or overlap size. You have to experiment to find what works best for you."*

**My own observation, not the book's:** taken together, these five aren't competing alternatives so much as a spectrum from *content-blind* (fixed-length) to *content-aware* (creative/token-based), with recursive chunking and overlap functioning as general-purpose patches that make any of the cruder strategies less lossy. If you're building a real system, the book's own ordering is a reasonable adoption path — start with fixed-length or recursive since they need no domain logic, add overlap immediately since it's nearly free, and only reach for content-specific or token-based splitting once you've measured that boundary-cutting is actually hurting your retrieval metrics.