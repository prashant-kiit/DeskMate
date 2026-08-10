"""
Minimal illustration of the RAG architecture from
Chip Huyen, "AI Engineering", Chapter 6 (pp. 256-257).

Maps directly onto the book's Figure 6-2:

    User --prompt--> Retriever --context--> Generator --response--> User
                         ^
                         |
                  External memory

A retriever has exactly two jobs per the book: INDEXING (process data so
it can be retrieved quickly later) and QUERYING (fetch data relevant to
a given query). This demo uses simple term overlap as the relevance
score so it runs with no dependencies -- a real system would swap this
for BM25 (term-based) or embeddings (semantic), as covered later in the
same chapter.
"""

import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------------
# External memory: the book's example is "a database of documents, such
# as a company's memos, contracts, and meeting notes" (p. 256).
# ---------------------------------------------------------------------
EXTERNAL_MEMORY = [
    "The Q3 marketing budget was approved at $450,000, a 12% increase "
    "over Q2, driven by the new product launch campaign.",
    "Our return policy allows customers to return unused items within "
    "30 days of purchase for a full refund.",
    "The engineering team migrated the primary database to a new "
    "cluster in October to improve query latency.",
    "Employee onboarding now includes a mandatory two-day security "
    "training session in the first week.",
]


def chunk_document(text, max_words=25):
    """Naive chunking: split a document into ~max_words-word pieces.

    The book notes that a document can be 10 tokens or a million, and
    that naively retrieving whole documents can make context arbitrarily
    long -- hence chunking before indexing (p. 257).
    """
    words = text.split()
    return [" ".join(words[i : i + max_words]) for i in range(0, len(words), max_words)] or [text]


@dataclass
class Retriever:
    """A retriever has two functions per the book: indexing and querying."""

    index: list = field(default_factory=list)  # list of chunks

    def build_index(self, documents):
        """INDEXING: process raw documents into retrievable chunks."""
        for doc in documents:
            self.index.extend(chunk_document(doc))
        print(f"[retriever] indexed {len(self.index)} chunks from {len(documents)} documents")

    @staticmethod
    def _score(query, chunk):
        """Toy relevance score: fraction of query terms present in the
        chunk. A real retriever would use BM25 (term-based) or cosine
        similarity over embeddings (semantic) -- see 'Retrieval
        Algorithms', pp. 258-267."""
        q_terms = set(re.findall(r"\w+", query.lower()))
        c_terms = set(re.findall(r"\w+", chunk.lower()))
        return len(q_terms & c_terms) / len(q_terms) if q_terms else 0.0

    def query(self, user_query, top_k=1):
        """QUERYING: return the chunks most relevant to a query."""
        ranked = sorted(self.index, key=lambda c: self._score(user_query, c), reverse=True)
        context = [c for c in ranked[:top_k] if self._score(user_query, c) > 0]
        print(f"[retriever] retrieved {len(context)} chunk(s) for: {user_query!r}")
        return context


class Generator:
    """Stands in for the generative model. Reads the retrieved context
    and the original prompt to produce a response, per Figure 6-2."""

    def generate(self, prompt, context):
        if not context:
            return "I don't have relevant information to answer that."
        joined_context = " ".join(context)
        # A real system sends (prompt + context) to an LLM. This stub
        # just demonstrates that the generator's input is the union of
        # both, matching "post-processing is often needed to join the
        # retrieved data chunks with the user prompt" (p. 257).
        return (
            f"[generated response using {len(context)} retrieved "
            f"chunk(s)]\nContext used: {joined_context}\n"
            f"Answer to '{prompt}': based on the context above."
        )


class RAGSystem:
    """Ties the retriever and generator together, mirroring Figure 6-2:
    User -> Retriever -> Generator -> User."""

    def __init__(self, documents):
        self.retriever = Retriever()
        self.retriever.build_index(documents)
        self.generator = Generator()

    def ask(self, prompt):
        context = self.retriever.query(prompt)
        return self.generator.generate(prompt, context)


if __name__ == "__main__":
    rag = RAGSystem(EXTERNAL_MEMORY)

    for question in [
        "What is the marketing budget for Q3?",
        "How many days do I have to return an item?",
        "What color is the office painted?",  # nothing relevant indexed
    ]:
        print("\nUser:", question)
        print(rag.ask(question))
