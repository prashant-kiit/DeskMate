# Overview

**What is RAG**:

RAG is defined as a technique that enhances a model's generation by retrieving relevant information from external memory sources. Those sources can be an internal database, a user's previous chat sessions, or the internet. RAG is a special case of an agent where the retriever is simply one tool.

The key move is selectivity: only the information most relevant to the query, as determined by the retriever, gets put into the model. This yields more detailed responses while reducing hallucinations.

**Architecture**:

A RAG system has two components — a **retriever** that pulls information from external memory, and a **generator** that produces a response from what was retrieved. The retriever itself has two functions: *indexing* (processing data so it can be retrieved quickly later) and *querying* (sending a query to fetch relevant data). 

**Flow**:
The success of a RAG system depends on the quality of its retriever. In practice, documents are split into chunks rather than retrieved whole — otherwise context length becomes arbitrarily long — and the retrieved chunks are joined with the user prompt through minor post-processing to form the final prompt fed to the generator. 

**Types**:
Retrievers come in two families the book develops at length: term-based (BM25, Elasticsearch — lightweight, strong baselines) and embedding-based (heavier, potentially better). 

**RAG Eval**:
Retrieval quality is measured with **context precision** and **context recall** (p. 264).

Two framings from the chapter worth carrying forward: RAG was *originally* developed to overcome context-window limits, but it also enables more efficient use of information — better responses at lower cost (chapter Summary, p. 305). 

**RAG vs Fine Tuning**
And RAG is classed as a **prompt-based method**, meaning it improves output purely through inputs without modifying the model — which is why the book positions it opposite finetuning.