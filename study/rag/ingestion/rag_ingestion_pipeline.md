# RAG Ingestion Pipeline — Python Code

Based directly on the transcript. The pipeline has 3 steps:

1. Load source `.txt` documents
2. Chunk the documents
3. Embed chunks and store them in ChromaDB

## Dependencies

```bash
pip install langchain langchain-community langchain-text-splitters langchain-openai langchain-chroma python-dotenv
```

## Project Structure

```text
rag/
├── ingestion_pipeline.py
├── .env
├── docs/
│   ├── google.txt
│   ├── microsoft.txt
│   ├── nvidia.txt
│   ├── spacex.txt
│   └── tesla.txt
└── db/
    └── chromadb/
```

## Environment

`.env`

```env
OPENAI_API_KEY=your_openai_api_key
```

## `ingestion_pipeline.py`

```python
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
)
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def load_documents(docs_path):
    if not os.path.exists(docs_path):
        raise FileNotFoundError(
            f"Directory does not exist: {docs_path}"
        )

    loader = DirectoryLoader(
        docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
    )

    documents = loader.load()

    if len(documents) == 0:
        raise ValueError("No txt files were found")

    return documents


def chunk_documents(documents):
    text_splitter = CharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=0,
    )

    chunks = text_splitter.split_documents(documents)

    return chunks


def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./db/chromadb",
        collection_metadata={
            "hnsw:space": "cosine"
        },
    )

    print("Vector store created successfully.")

    return vector_store


def main():
    load_dotenv()

    docs = load_documents("./docs")
    chunks = chunk_documents(docs)
    vector_store = create_vector_store(chunks)

    print("RAG ingestion pipeline completed.")


if __name__ == "__main__":
    main()
```

## Pipeline Flow

```text
docs/*.txt
    ↓
DirectoryLoader + TextLoader
    ↓
LangChain Documents
    ↓
CharacterTextSplitter
    ↓
Chunks
    ↓
OpenAI text-embedding-3-small
    ↓
Vector Embeddings
    ↓
ChromaDB
    ↓
./db/chromadb
```

## Run

```bash
python3 ingestion_pipeline.py
```

The transcript uses **800 characters per chunk**, **0 overlap**, OpenAI's **`text-embedding-3-small`**, and a locally persisted **ChromaDB** using **cosine similarity**.
