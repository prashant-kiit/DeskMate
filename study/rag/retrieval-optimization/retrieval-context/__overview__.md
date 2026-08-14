I now have the complete section.

**What the book says** (Chapter 6, "RAG and Agents" → *Retrieval Optimization* → *Contextual retrieval*, pp. 270–272):

## The core idea

Contextual retrieval augments each chunk with relevant context to make it easier to retrieve. The problem it solves is a direct consequence of chunking itself: once a document is split apart, individual chunks can lose the surrounding information that would have told a retriever what they're actually about.

## Three concrete techniques the book gives

**1. Metadata augmentation** — attach tags and keywords to a chunk. Domain examples:
- Ecommerce: a product chunk augmented with its description and reviews
- Images and video: retrieved by their titles or captions

**2. Extracted-entity metadata** — automatically pull out specific entities from the chunk and attach them as metadata. The book's worked example: if a document contains an exact error code like `EADDRNOTAVAIL (99)`, adding it to metadata lets the system retrieve that chunk by the literal code — **even after the chunk has been converted into embeddings**, where exact-string signals like error codes tend to get blurred (this connects directly back to the embedding-based retrieval weakness discussed earlier in the chapter).

**3. Question augmentation** — attach the questions a chunk can answer, not just its content. Customer-support example: an article on resetting a password gets augmented with related queries like "How to reset password?", "I forgot my password," "I can't log in," or "Help, I can't find my account." A footnote adds that some teams report their retrieval systems work best when data is organized in this question-and-answer format specifically.

## The deeper technique: whole-document context injection

Beyond attaching metadata, the book describes augmenting each chunk with **context from the original document itself** — its title and summary — so an isolated chunk doesn't lose its place within the larger whole.

The book cites **Anthropic's approach** (2024) as the detailed example: using an AI model to generate a short context — typically 50–100 tokens — that explains what the chunk is and how it relates to the original document. The book reproduces Anthropic's actual prompt template:

```
<document>
{{WHOLE_DOCUMENT}}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{{CHUNK_CONTENT}}
</chunk>

Please give a short succinct context to situate this chunk within the
overall document for the purposes of improving search retrieval of the
chunk. Answer only with the succinct context and nothing else.
```

**The pipeline:** the generated context is **prepended** to each chunk, and it's this augmented chunk — original text plus generated situating context — that gets indexed by the retrieval algorithm, not the raw chunk alone. The book references Figure 6-5, Anthropic's own visualization of this process from their "Introducing Contextual Retrieval" writeup.

## Where the section sits

Contextual retrieval closes out the four *Retrieval Optimization* tactics, and the book transitions directly from it into *Evaluating Retrieval Solutions* — the practical checklist for choosing a retrieval system — suggesting these four tactics are meant to be read as a toolkit you apply before you've even settled on your retrieval infrastructure, not after.

**My own observation, not the book's:** all three of the simpler techniques (metadata, entities, questions) and the Anthropic whole-document technique share one underlying move — they're compensating for information that chunking necessarily discards, by re-injecting a compressed version of "what this chunk is part of" back into the chunk itself. It's the same instinct as overlap (from *Chunking strategy*), but instead of preserving boundary text mechanically, it uses a model to write a *summary* of the missing context — trading a small amount of generation cost per chunk for retrieval accuracy.