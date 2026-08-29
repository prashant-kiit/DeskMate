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
- Retreival : SQL + Vector (Hybrid)
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
- Use Lexical Id and Semantic Id to search and return Actual Documents from SQL DB and Vector DB
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

LLM Retrieval vs RAG Retreival
- LLM : Static Data and Expensive
- RAG : Dyanmic Data and Cheap

