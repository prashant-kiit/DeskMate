"""
Simple, from-scratch BM25 implementation.

Book grounding (Chip Huyen, "AI Engineering", Chapter 6, pp. 259-260):
BM25 ("Okapi BM25, the 25th generation of the Best Matching algorithm")
is described as "a modification of TF-IDF. Compared to naive TF-IDF,
BM25 normalizes term frequency scores by document length. Longer
documents are more likely to contain a given term and have higher term
frequency values." The book gives the full formula for plain TF-IDF
(Score(D,Q) = sum of IDF(t) * f(t,D)) but does not spell out BM25's
formula -- that's standard information-retrieval math, reproduced below
for illustration, not something quoted from the book.

Run: python3 bm25_demo.py
"""

import math
from collections import Counter

# ------------------------------------------------------------- toy corpus
DOCS = [
    "the cat sat on the mat",
    "the dog sat on the log",
    "cats and dogs are great pets and cats are independent",
    "the quick brown fox jumps over the lazy dog",
]
QUERY = "cats dog"

# BM25's two tuning knobs, following the book's description that it
# "normalizes term frequency scores by document length":
K1 = 1.5   # controls how quickly term frequency saturates
B = 0.75   # controls how strongly document length is penalized (0 = off, 1 = full)


def tokenize(text):
    return text.lower().split()


def bm25_scores(query, docs, k1=K1, b=B):
    tokenized_docs = [tokenize(d) for d in docs]
    doc_lengths = [len(d) for d in tokenized_docs]
    avg_len = sum(doc_lengths) / len(doc_lengths)
    N = len(docs)

    # --- IDF: same intuition as TF-IDF -- rarer terms are more informative
    # "the more documents contain a term, the less informative this term is"
    def idf(term):
        n_containing = sum(1 for d in tokenized_docs if term in d)
        if n_containing == 0:
            return 0.0
        # BM25's IDF variant (avoids negative scores for very common terms)
        return math.log((N - n_containing + 0.5) / (n_containing + 0.5) + 1)

    query_terms = tokenize(query)
    scores = []
    for doc, doc_len in zip(tokenized_docs, doc_lengths):
        term_counts = Counter(doc)
        score = 0.0
        for term in query_terms:
            f = term_counts.get(term, 0)          # raw term frequency, f(t, D)
            if f == 0:
                continue
            # the core BM25 term: TF-IDF's f(t,D), but saturated and
            # normalized by how long this document is vs. the average
            numerator = f * (k1 + 1)
            denominator = f + k1 * (1 - b + b * (doc_len / avg_len))
            score += idf(term) * (numerator / denominator)
        scores.append(score)
    return scores


if __name__ == "__main__":
    scores = bm25_scores(QUERY, DOCS)

    print(f'Query: "{QUERY}"\n')
    ranked = sorted(zip(scores, DOCS), reverse=True)
    for rank, (score, doc) in enumerate(ranked, 1):
        print(f"{rank}. score={score:.3f}  \"{doc}\"")

    print("\n--- why document 3 wins ---")
    print('Doc 3 ("cats and dogs are great pets...") never matches "dog" at')
    print('all -- tokenization here is exact-word, and "dogs" != "dog". It')
    print('wins purely because "cats" appears twice.')

    print("\n--- term frequency saturation, isolated ---")
    print('Comparing a term appearing 1x, 2x, and 4x in otherwise-identical')
    print('documents shows BM25\'s contribution per repeat shrinking:')
    base = "cats like naps"
    for reps in (1, 2, 4):
        doc = " ".join(["cats"] * reps) + " like naps"
        s = bm25_scores("cats", [doc])[0]
        print(f"  \"cats\" x{reps}: score={s:.3f}")
    print("Score grows with repetition, but each additional occurrence")
    print("contributes less than the one before -- that's saturation,")
    print("controlled by K1. A plain word-count score would grow linearly")
    print("instead.")

    print("\n--- effect of B: length normalization ---")
    print("Turning off length normalization (b=0) changes the ranking:")
    scores_no_norm = bm25_scores(QUERY, DOCS, b=0.0)
    for doc, s_norm, s_nonorm in zip(DOCS, scores, scores_no_norm):
        print(f"  b=0.75: {s_norm:.3f}   b=0: {s_nonorm:.3f}   \"{doc[:40]}\"")