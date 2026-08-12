# Chunking Algorithms

## 1. Fixed-length chunking

The simplest approach: split documents into chunks of equal length, measured in a unit you choose. Units can be:

a. **Characters** 
* e.g., every 2,048 characters becomes a chunk
* Unit-agnostic, works identically regardless of language or content.

b. **Words** 
* e.g., every 512 words. 
* More linguistically meaningful than raw characters, but word count varies with how verbose the writing is.

c. **Sentences**
* e.g., every 20 sentences. 
* Preserves grammatical units rather than cutting mid-sentence.

d. **Paragraphs**
* each paragraph becomes its own chunk. 
* The coarsest of the four, but respects the author's own structural boundaries.

**The core weakness:** 
+ None of these units know much about *meaning*. (Semantic Point)
    + There is possibility of stripping out the content that can us loss the meaning
    + Thers is possibility of aggregating the units can lead to addition sematically unrelated units
+ These chunks struggle wih *Context* and *Halluncination*. (Syntactical Point)
    + The Bigger Chunk the More Context it has and makes more Context but can lead to Hallunication as well
    + The Smaller Chunk can Reduce Hallunication but Context is missing
+ ***In Short We need to have a combination of Big and Small Chunk based on the Score (Semantics + Synatax) Match***

**Best for:** homogeneous content with no inherent structure — server logs, transcripts. 

----

## 2. Recursive chunking

Splits using progressively smaller units, only descending further when a piece is still too large:

```
document → sections → (still too long?) → paragraphs → (still too long?) → sentences
```

* Tackales this problem: ***In Short We need to have a combination of Big and Small Chunk based on the Score (Semantics + Synatax) Match***
* You start coarse and only fragment further where necessary. Recursive chunking only cuts as finely as each specific piece of text requires. 
* This reduces the chance of related texts being arbitrarily broken off and unrelated texts being put together
* The intuition
    + a section that's already short enough doesn't need to be shredded into sentences just because your pipeline defaults to sentence-level splitting; 
    + a section that's already big needs to be shredded into smaller units just because your pipeline defaults to paragragh-level splitting;
* This makes it adaptive in a way fixed-length chunking isn't: dense sections get split further, naturally short ones are left intact.

----

## 3. Content-specific / creative chunking

Split the Document into categories on there Unit Structure and then use Recusrive Chunking

- **Programming-language-specific splitters** — structural units (functions, classes, blocks).
- **Q&A documents** — structural units (question/answer pair).
- **Language-specific handling** — Chinese structural units (Column Delimited); English structural units (Row Delimited)

----

## 4. Overlapping chunks

* Tackales this problem: ***In Short We need to have a combination of Big and Small Chunk based on the Score (Semantics + Synatax) Match***
* Join the small and big chunks in grapgh of close semantics and syntax based score
* A modifier layer on top of other strategies. 
* Instead of chunks divided with hard boundaries, adjacent chunks share a small region of overlapping text.
* 20%-30% overlapping is fine 

----

***Guru Mantra***
* There is universally correct chunking strategy. 
* "right" chunk boundary is defined by the **document's own internal structure** and your **query patterns**., not a generic character/word/sentence count.
* Start to Fixed Length strategies then move to Creative strategies

----

## 5. Token-based chunking

Chunk using the **generative model's own tokenizer** as the splitting unit. The book's worked example: if you're using Llama 3 as your generator, you first tokenize documents with Llama 3's tokenizer, then split on token boundaries rather than character or word boundaries.

**Benefit:** tighter alignment with the downstream model — since context limits and cost are measured in tokens, not characters or words, chunking in the same unit you'll be constrained by later avoids mismatches between "how big I thought this chunk was" and "how much context it actually consumes."

**Best for:** roughly **15–40% improvement in retrieval precision** on documents with clear topical structure — technical documentation, research papers, structured reports. This depends heavily on content: if your documents have no clear topic transitions, you may see little improvement over fixed chunking.

**Cost:** 
* computational overhead. You generate embeddings *during* chunking, not just for the final chunks. Across a large collection, that adds meaningful cost and time to the ingestion pipeline.
* if you switch to a different generative model with a different tokenizer, you have to **reindex your entire dataset** — the chunk boundaries were defined by a tokenizer that no longer matches your new model. This is the one strategy the book pairs with a concrete cost, making it clear this isn't a free upgrade over the simpler unit choices.

## 6. Semantic Based Chunking
Instead of splitting at arbitrary token boundaries, use embeddings to find natural topic boundaries.

## Advanced pattern: parent–child chunking

Create small chunks (~256 tokens) for precise vector search. When a small chunk matches, return its larger **parent** chunk (~1,024 tokens) to the language model.

You get retrieval precision from the child and context completeness from the parent.

----

## Chunk size — cutting across all five

Whichever strategy you use, **how big** each chunk is interacts with the strategy rather than being independent of it:

- **Smaller chunks** 
* more chunks fit into the model's context window (halve the size, roughly double how many chunks fit)
* the model sees a wider range of distinct information
* risk losing information that appears only once in a source document, if the relevant chunk isn't the one retrieved
* computational cost rises, since embedding-based retrieval now has twice as many vectors to generate, store, and search.

- **Larger chunks**
* fewer distinct chunks can be packed into the same context budget
* the model sees a wider range of similar information
* less risk of splitting an idea awkwardly
* cheaper to index → but coarser retrieval granularity

----

# The algorithm

1. RAG Agent Step
    * Chunk the document into units recursively based on the Document Type (Internal Structure) while have a overlapping Graph Based Relation ship among chunks.

2. Category Model Step
    * Generate an embedding vector for each chunk by passing each on them through a Transformer (Consisting of Layers of Neural Network). [This is Recursive Process Like any Graph Traversal]
    * Feed Forward Starts
    * Tokenize (Done based on Dictionary/Map of Lexicons which in turn is product of Model Training/Fine-Tuning) by Neural Network
    * Parsed (Syntax - Relation Ship b/w Tokens; Those Relationships are in turn a product of Model Training/Fine-Tuning) by Neural Network
    * Semantically Understood (Attention; The Contextual meaning of Relationships are in turn a product of Model Training/Fine-Tuning) by Neural Network
    * Here in each step above cosine similarity (or any other NN) between each pair embedding is measured.
    * Feed Backward Back Propagates
3. This results in a Vector Embedding Space of all Chunks
4. Where similarity drops significantly below a threshold (or hits a local minimum), you have found a topic boundary in Vector Embedding Space.
5. Group the sentences between boundaries into a single chunk repr. by K-Mean Centroid and store in VectorDB.

**Store metadata with every chunk:** section title, heading hierarchy, source file path. This enables filtered retrieval (searching within a specific section) and tells the LLM where the information came from.

----

# Architecture Scenario

An enterprise documentation search system serving **10,000 engineers** across **300,000 documents**.

### Ingestion pipeline

```
Document sources
       │
       ▼
┌──────────────────┐
│ Document Router  │  ← examines file type, picks a strategy
└──────────────────┘
   │    │    │    │
   │    │    │    └── .log            → Fixed-size chunker
   │    │    └─────── .pdf            → Semantic chunker
   │    └──────────── .py .js .go     → Function chunker
   └───────────────── .md             → Header chunker
                  │
                  ▼
        Chunks + metadata
                  │
                  ▼
        Embedding generation
                  │
                  ▼
            Vector store
```

### Retrieval path

```
User query → embed → vector search → reranker → top results → LLM context
```

The reranker sits between search and the LLM to improve precision on the final result set.

