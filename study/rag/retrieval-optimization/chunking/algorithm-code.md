## Chunking Algorithms Code Examples

### 2.1 Fixed-size chunking

Three parameters: the text, a `chunk_size` defaulting to 512 tokens, and an `overlap` defaulting to 50. The function encodes the text into tokens and walks a sliding window across it, advancing by `chunk_size - overlap` each iteration so consecutive chunks share the overlap.

```python
import tiktoken

def fixed_size_chunk(text, chunk_size=512, overlap=50):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(tokens), step):
        window = tokens[start:start + chunk_size]
        if not window:
            break
        chunks.append(enc.decode(window))
    return chunks
```

Roughly ten lines. This is your baseline.

---



### 2.2 Semantic chunking

Takes the text and a `similarity_threshold` defaulting to 0.5. Tokenize into sentences, embed each one, then walk adjacent pairs computing cosine similarity. When similarity drops below the threshold, close the current chunk and start a new one.

```python
import numpy as np
import nltk
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_chunk(text, similarity_threshold=0.5):
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return []

    embeddings = model.encode(sentences, normalize_embeddings=True)

    chunks, current = [], [sentences[0]]
    for i in range(1, len(sentences)):
        similarity = float(np.dot(embeddings[i - 1], embeddings[i]))
        if similarity < similarity_threshold:
            chunks.append(" ".join(current))   # topic boundary
            current = []
        current.append(sentences[i])

    chunks.append(" ".join(current))
    return chunks
```

Output: a list of chunks, each containing semantically related sentences.

---



### 2.3 Markdown / header chunking

Parses the markdown structure directly. Iterate through the lines; whenever a header (a line starting with `#`) is encountered, close the current chunk and start a new one with that header as metadata. Each output chunk carries its title, content, and full header path for filtered retrieval.

```python
import re

def markdown_chunk(text):
    chunks, current, path = [], None, []

    for line in text.splitlines():
        header = re.match(r"^(#{1,6})\s+(.*)", line)
        if header:
            if current:
                chunks.append(current)
            level, title = len(header.group(1)), header.group(2).strip()
            path = path[:level - 1] + [title]
            current = {"title": title, "header_path": " > ".join(path), "content": ""}
        elif current:
            current["content"] += line + "\n"

    if current:
        chunks.append(current)
    return chunks
```

---



### 2.4 Evaluating your chunking

This one is critical — you need to measure whether the strategy actually works. It takes your chunks, a set of test queries, and ground-truth relevance labels, then computes two metrics per query:

- **Recall** — how many of the relevant chunks appear in your top-*k* results
- **MRR (mean reciprocal rank)** — how highly the correct chunk is ranked

```python
def evaluate_chunking(chunks, test_queries, ground_truth, search_fn, k=5):
    recalls, reciprocal_ranks = [], []

    for query in test_queries:
        retrieved = search_fn(query, chunks, k=k)     # returns chunk ids, ranked
        relevant = set(ground_truth[query])

        hits = [i for i, cid in enumerate(retrieved, start=1) if cid in relevant]
        recalls.append(len(set(retrieved) & relevant) / max(len(relevant), 1))
        reciprocal_ranks.append(1 / hits[0] if hits else 0.0)

    return {
        "recall@k": sum(recalls) / len(recalls),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks),
    }
```

Run this comparing different chunking strategies **on your own data** before committing to one.