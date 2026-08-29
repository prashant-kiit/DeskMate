## Recommendation Engine

- User Activity Log (Implicit and Explicit Activity)
    - Kakfa
    - Split the Stream Based on Content Type
    - Timeseries
    - Event Trigger
    - Event Buffer
- RAG Query
    - System Query (Sameness for SQL and Similarity for Vector)
    - User Activity Log
- RAG Retreival : SQL + Vector (Hybrid)
    - SQL : Lexical, Fuzzy, Leventstein 
    - Vector : Semantic, Similarity, KNN
- Content Metadata for SQLDB Record (Content Info like Author, Post Day, Category etc.) and VectorDB Vector (Content like Video, Text etc.)
- Reranking [DB Query, Documents Retreived]
    - Lexical : Fuzzy, Leventstein Using Levenshtein-Library
    - Semantic : Similarity, KNN Using Encoder/Decoder
- RRF (Merge and DeDuplication)
- LLM Context:
    - User Prompt
    - System Prompt [Content Recommendation Criteria like Author, Content Category, Content Size etc.]
    - Retrevied Documents
- Context Rewriting
- LLM (BERT)
- Response containing Lexical Id (SQL Record SHA Hash) and Semantic Id (VectorDB Embedding Residual Quantizations)
- Use Lexical Id and Semantic Id to search and return Actual Documents from SQL DB and Vector DB [Leverage Pydantic and Text-To-Query having those IDs against Trie Index (Can Lie in GraphDB po vLLM-Trie as GrapghRAG) on DB Records and Vectors to Implement Constraint Encoding/Decoding]
- DB Query:
    - System Query (Lexical Id and Semantic Id)
    - Object Storage (Content like Video, Text etc.)
- Evaluations
    - Test Dataset : Log Trace (Synthetic for Development, Golden for Production) + Human's GroundTruths
    - Evals (Metrics : Precision (Relevance), Recall (Completeness))
    - RL : ?
- AB Testing
    - Compare Old and New System
    - Metrics : Precision (Relevance), Recall (Completeness)

-----

RAG Ingestion Pipeline
- Source: Object Storage
- Transform
    - Read, 
    - Research (use LLM) and Annotate the data
    - WebM Conversion for Standard Format, 
    - XML Conversion for Parsable Format, 
    - Parse Data to Standard Structure,
    - Clean Data to Remove Extras, 
    - Chunk Corpus into Units + Add Metadata to each Chunk,
    - Create Embedding from Units and Metadata 
    - Index (Clustering) : LSH (Bucketing), HSWN (Small Worlds), Quantization & Centroid, Cosine Similarity, TextTiling
    - Store
- Traget: VectorDB
- Create Knowledge Graph for RAG using LLM (NER for identifiy nodes and relationship types and Domain Models) by find relationships among Records and Vectors 

-----

LLM Retrieval vs RAG Retreival
- LLM : Static Data and Expensive
- RAG : Dyanmic Data and Cheap

-----

Classical RAG vs Graph RAG
- Classical : Dynamic Data, Simple Reasoning
- Graph : Static Data, Complex Reasoning

