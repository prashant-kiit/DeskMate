## What it is Query rewriting

Query rewriting goes by several names in the book — **query reformulation, query normalization,** and sometimes **query expansion**. The core problem it solves: a user's literal query, taken verbatim, is often not the right thing to search with, because it depends on context that isn't in the query text itself.

## The book's worked example

A multi-turn conversation:

> **User:** When was the last time John Doe bought something from us?
> **AI:** John last bought a Fruity Fedora hat from us two weeks ago, on January 3, 2030.
> **User:** How about Emily Doe?

The final question — *"How about Emily Doe?"* — is meaningless on its own. If you feed that string directly into your retriever, you'll get irrelevant results, because nothing in it mentions purchases, dates, or "last time." The retriever has no way to know the question is actually about purchase history. The fix: rewrite the query into something that stands alone and captures the actual intent — in this case, *"When was the last time Emily Doe bought something from us?"* The book's stated bar for a good rewrite: **the new query should make sense on its own**, without needing the prior conversation turns to interpret it.

## Where it fits — not RAG-exclusive

The book places this discussion inside the RAG section, but is explicit that query rewriting isn't unique to RAG. It notes two eras of how it's been done:

- **Traditional search engines** — typically handled with heuristics.
- **AI applications** — can be done using other AI models entirely. The book gives a template prompt: *"Given the following conversation, rewrite the last user input to reflect what the user is actually asking,"* and shows (Figure 6-4) ChatGPT performing this rewrite in practice.

## Where it gets hard: identity resolution

The book flags that query rewriting can get significantly more complicated when it requires resolving *who or what* a pronoun or reference actually points to — what it calls **identity resolution** — or when it needs outside knowledge to complete the query.

**Worked example:** if the user asks *"How about his wife?"*, the rewriting step first has to query a database to figure out who "his wife" actually refers to before it can produce a standalone query. The book draws a sharp line here on failure behavior: **if that identity information isn't available, the rewriting model should say the query isn't solvable — not hallucinate a name.** Guessing a name that happens to sound plausible would silently corrupt everything downstream: the retriever would confidently fetch documents about the wrong person, and the final answer would be wrong in a way that looks correct.

**My own observation, not the book's:** that failure-mode instruction is worth noticing on its own — it's a small but pointed example of the book's broader stance (developed at length in Chapter 4's evaluation material) that a system silently guessing wrong is worse than a system that visibly declines. Query rewriting sits at a uniquely dangerous point in a RAG pipeline for exactly this reason: an error introduced here doesn't just affect the query — it propagates invisibly into which documents get retrieved and, from there, into the generated answer, with no natural point downstream where the mistake becomes obvious.