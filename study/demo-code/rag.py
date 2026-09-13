# pip install openai chromadb pypdf

from openai import OpenAI
import chromadb
from pypdf import PdfReader

client = OpenAI()
db = chromadb.PersistentClient(path="./chroma")
collection = db.get_or_create_collection("docs")


# 1. LOAD DOCUMENTS
def load_pdf(path):
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# 2. CHUNK
def chunk(text, size=800, overlap=100):
    return [
        text[i:i + size]
        for i in range(0, len(text), size - overlap)
    ]


# 3. EMBED + STORE
def index_document(path):
    text = load_pdf(path)
    chunks = chunk(text)

    embeddings = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    ).data

    collection.add(
        ids=[f"chunk-{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=[e.embedding for e in embeddings],
        metadatas=[{"source": path, "chunk": i} for i in range(len(chunks))]
    )


# 4. QUERY → EMBEDDING → RETRIEVAL
def retrieve(query, k=5):
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    return collection.query(
        query_embeddings=[embedding],
        n_results=k
    )


# 5. RERANK / FILTER (optional but ideal)
def rerank(results):
    # Production: use a cross-encoder/reranker
    return results["documents"][0]


# 6. AUGMENT + GENERATE
def ask(query):
    results = retrieve(query)
    context = "\n\n".join(rerank(results))

    prompt = f"""
Answer using ONLY the context below.
If the answer is not present, say "I don't know".

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# INGESTION
index_document("document.pdf")

# QUERY
print(ask("What is the main purpose of this document?"))