## How to deal with Stale Vectors in AI Agent or RAG Architecture? In Brief Only

- **Event-driven re-indexing** – trigger re-embeds from CDC/webhooks instead of relying on periodic batch jobs, so staleness stays in minutes, not days.
- **Chunk-level updates** – re-embed only the changed chunk, not the whole document.
- **Freshness metadata** – tag every vector with `last_updated`/`source_version`; filter or re-rank by recency at query time.
- **Tombstone deletes immediately** – flag removed content so it's excluded from retrieval before the async cleanup job runs.
- **TTL on volatile content** – expire vectors for fast-changing data (prices, inventory) and force refetch.
- **Pin embedding model versions** – never mix vectors from different model versions in one similarity space; migrate with a full re-embed + atomic swap.
- **Agent-side verification** – for high-stakes/volatile facts, have the agent confirm via a live tool call rather than trusting retrieval alone.
- **Monitor staleness** – track vector age as a metric with alerting, like any other data pipeline.