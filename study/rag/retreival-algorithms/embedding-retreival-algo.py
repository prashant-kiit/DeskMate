"""
Simple, from-scratch illustrations of vector search algorithms from
Chip Huyen, "AI Engineering", Chapter 6, pp. 261-263.

Each demo uses the same tiny toy dataset of 2D "vectors" (in reality
embeddings have hundreds of dimensions -- 2D is just so the mechanics
are easy to see) and only NumPy, so nothing needs to be installed.

Run: python3 vector_search_demo.py
"""

import numpy as np

rng = np.random.default_rng(0)

# 200 toy "embeddings" clustered into 4 groups, so nearby vectors are
# genuinely similar -- like documents about similar topics.
CENTERS = np.array([[10, 10], [10, 50], [50, 10], [50, 50]], dtype=float)
DB = np.vstack([c + rng.normal(scale=1.2, size=(50, 2)) for c in CENTERS])
QUERY = np.array([11.0, 11.0])  # close to the cluster around (10, 10)


def similarity(a, b):
    return -np.linalg.norm(a - b, axis=-1)   # higher = more similar


# ---------------------------------------------------------------------
# 1. k-NN (exact)
# "Compute the similarity scores between the query embedding and all
# vectors in the database... Rank all vectors... Return k vectors with
# the highest similarity scores." (p. 262)
# ---------------------------------------------------------------------
def knn_exact(query, db, k=5):
    sims = similarity(query, db)          # compare against EVERY vector
    top_k = np.argsort(-sims)[:k]         # rank, take the best k
    return top_k, sims[top_k]


# ---------------------------------------------------------------------
# 2. LSH (locality-sensitive hashing)
# "Hashing similar vectors into the same buckets to speed up similarity
# search, trading some accuracy for efficiency." (p. 263)
#
# One simple LSH scheme: draw random hyperplanes through the space.
# A vector's "hash" is which side of each hyperplane it falls on.
# Similar vectors tend to fall on the same side of most planes, so
# they land in the same bucket.
# ---------------------------------------------------------------------
def lsh_hash(vectors, planes):
    return tuple((vectors @ planes.T > 0).astype(int).tolist())

def lsh_search(query, db, k=5, n_planes=3):
    planes = rng.normal(size=(n_planes, db.shape[1]))   # random hyperplanes
    buckets = {}
    for i, v in enumerate(db):
        h = lsh_hash(v, planes)
        buckets.setdefault(h, []).append(i)
    q_hash = lsh_hash(query, planes)
    candidates = buckets.get(q_hash, [])                # only search this bucket!
    if not candidates:
        return np.array([], dtype=int), np.array([])
    sims = similarity(query, db[candidates])
    order = np.argsort(-sims)[:k]
    idx = np.array(candidates)[order]
    return idx, sims[order]


# ---------------------------------------------------------------------
# 3. IVF (inverted file index)
# "Uses K-means clustering to organize similar vectors into the same
# cluster. During querying, IVF finds the cluster centroids closest to
# the query embedding, and the vectors in these clusters become
# candidate neighbors." (p. 263)
# ---------------------------------------------------------------------
def kmeans(db, n_clusters=4, iters=10):
    centroids = db[rng.choice(len(db), n_clusters, replace=False)]
    for _ in range(iters):
        dists = np.linalg.norm(db[:, None] - centroids[None, :], axis=2)
        assign = dists.argmin(axis=1)
        for c in range(n_clusters):
            if (assign == c).any():
                centroids[c] = db[assign == c].mean(axis=0)
    return centroids, assign

def ivf_search(query, db, k=5, n_clusters=4, n_probe=1):
    centroids, assign = kmeans(db, n_clusters)
    # step 1: find the nearest cluster centroid(s) to the query
    c_dists = np.linalg.norm(centroids - query, axis=1)
    nearest_clusters = np.argsort(c_dists)[:n_probe]
    # step 2: only search vectors inside those clusters
    candidates = np.where(np.isin(assign, nearest_clusters))[0]
    sims = similarity(query, db[candidates])
    order = np.argsort(-sims)[:k]
    idx = candidates[order]
    return idx, sims[order]


# ---------------------------------------------------------------------
# 4. Product Quantization
# "Reducing each vector into a much simpler, lower-dimensional
# representation by decomposing each vector into multiple subvectors.
# The distances are then computed using the lower-dimensional
# representations, which are much faster to work with." (p. 263)
#
# Simplified PQ: split each vector into 2 sub-vectors, run k-means on
# each sub-space separately, and replace every vector with a pair of
# small integer codes (its nearest sub-centroid ids). Distance between
# two vectors is then approximated using only those codes.
# ---------------------------------------------------------------------
def product_quantize(db, n_subvectors=2, n_codes=4):
    dim = db.shape[1]
    sub_dim = dim // n_subvectors
    codebooks, codes = [], []
    for s in range(n_subvectors):
        sub = db[:, s * sub_dim:(s + 1) * sub_dim]
        centroids, assign = kmeans(sub, n_clusters=n_codes)
        codebooks.append(centroids)
        codes.append(assign)
    return codebooks, np.stack(codes, axis=1)   # shape: (n_vectors, n_subvectors)

def pq_search(query, db, k=5, n_subvectors=2, n_codes=4):
    dim = db.shape[1]
    sub_dim = dim // n_subvectors
    codebooks, codes = product_quantize(db, n_subvectors, n_codes)
    approx_dists = np.zeros(len(db))
    for s in range(n_subvectors):
        q_sub = query[s * sub_dim:(s + 1) * sub_dim]
        # precompute distance from query's sub-vector to each sub-centroid
        centroid_dists = np.linalg.norm(codebooks[s] - q_sub, axis=1)
        # look up each database vector's distance via its small integer code
        approx_dists += centroid_dists[codes[:, s]]
    order = np.argsort(approx_dists)[:k]
    return order, approx_dists[order]


# ---------------------------------------------------------------------
# HNSW (Hierarchical Navigable Small World)
# "Constructs a multi-layer graph where nodes represent vectors, and
# edges connect similar vectors, allowing nearest-neighbor searches by
# traversing graph edges." (p. 263)
#
# A real HNSW build is intricate (multiple layers, probabilistic level
# assignment). This is a *single-layer* graph-traversal sketch that
# shows the core search idea only: connect each vector to its nearest
# neighbors, then search by greedily hopping to closer neighbors --
# never touching the full database.
# ---------------------------------------------------------------------
def build_graph(db, n_neighbors=5):
    graph = {}
    for i, v in enumerate(db):
        dists = np.linalg.norm(db - v, axis=1)
        dists[i] = np.inf
        graph[i] = np.argsort(dists)[:n_neighbors].tolist()
    return graph

def hnsw_like_search(query, db, k=5, n_neighbors=5, entry=0):
    graph = build_graph(db, n_neighbors)
    current = entry
    visited = {current}
    best = current
    best_dist = np.linalg.norm(db[current] - query)
    improved = True
    while improved:                        # greedily walk toward the query
        improved = False
        for neighbor in graph[current]:
            d = np.linalg.norm(db[neighbor] - query)
            if d < best_dist:
                best, best_dist, current = neighbor, d, neighbor
                improved = True
        visited.add(current)
    # once near the target, gather the best k from the local neighborhood explored
    local = sorted(set(visited) | set(graph[best]))
    sims = similarity(query, db[local])
    order = np.argsort(-sims)[:k]
    idx = np.array(local)[order]
    return idx, sims[order], len(visited)   # also return how few nodes we touched


if __name__ == "__main__":
    print(f"Database: {len(DB)} vectors, 4 natural clusters. "
          f"Query is near the cluster around (10, 10).\n")

    idx, sims = knn_exact(QUERY, DB, k=5)
    print(f"1. k-NN (exact)      -> top 5 idx {idx.tolist()}  "
          f"(compared against all {len(DB)} vectors)")

    idx, sims = lsh_search(QUERY, DB, k=5)
    print(f"2. LSH               -> top {len(idx)} idx {idx.tolist()}  "
          f"(compared against only its hash bucket)")

    idx, sims = ivf_search(QUERY, DB, k=5, n_probe=1)
    print(f"3. IVF                -> top 5 idx {idx.tolist()}  "
          f"(compared against only its nearest cluster)")

    idx, dists = pq_search(QUERY, DB, k=5)
    print(f"4. Product Quantization -> top 5 idx {idx.tolist()}  "
          f"(distances approximated from small integer codes, not raw vectors)")

    idx, sims, touched = hnsw_like_search(QUERY, DB, k=5)
    print(f"5. HNSW-like graph walk -> top 5 idx {idx.tolist()}  "
          f"(only visited {touched}/{len(DB)} nodes while walking the graph)")

    print("\nAll five should mostly agree on returning vectors from the "
          "(10, 10) cluster -- exact k-NN is the ground truth; the others "
          "are approximations that get there by touching far fewer vectors.")