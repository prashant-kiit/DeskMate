### Source: 
- https://www.youtube.com/watch?v=BacJ6sEhqMo
- https://www.youtube.com/watch?v=aYfZN8t6AQs
- Mem0 Sections from Piyush Garg Udemy Course https://www.udemy.com/course/full-stack-ai-with-python/
- https://www.youtube.com/watch?v=bfdTWkjsu8k
- https://www.youtube.com/watch?v=mY3bR9qjZr4

---

### Memory Layer (Memory Taxonomy) Architecture
- LLM are Stateless Machines ie. Do not Store Memory. So, a Agentic Memory Layer is required.
- Types of Agent Memory :
    - Main Memory
        - Factual Memory:
            - All Data Fed into System Prompt as Context
            - Business Memory:
                - Lexical Memory:
                    - User + Agent + Tool + Business Factual Information (Like Auth)
                    - SQL
                    - ROM Based
                    - MetaData (CreatedAt, UpdatedAt, CreatedBy, DeDuplication Hash, Lemma Version, Expiration Date)
                - Semantic Memory:
                    - User + Agent + Tool + Business Factual Information
                    - VectorDB
                    - ROM Based
                    - Vectors
                - GraphDB :
                    - Knowledge Graph
                    - GraphDB [Knowledge Graph of Entity + Relations] (Entity Memory)
                    - Supports the Procedure Memory on every turn of the loops
                    - Query-Response on outer most loops
                    - Stores Procedure and Converstion in the Session
                    - Used for Guided Agentic Processing
                - [Single Entity: Lexical and Semantic Memory Link by RecordID (Hashed) and VectorID (Hashed)]
            - User Memory:
                - User Details
                - SQL
                - ROM Based
                - Conflict Resolution Based:
                    - Provenance
                    - Recency
            - Agent Memory:
                - Agent Details
                - SQL
                - ROM Based
                - Conflict Resolution Based:
                    - Provenance
                    - Recency
            - Tool Memory:
                - MCP Tool/Server Details
        - Procedural Memory:
            - Agent and Tool Code File that later Ran in Sandbox
            - ROM based
    
    - Working Memory (Short Term Memory): 
        - RAM
        - State of Flow Graph
    - Session Memory:
        - Sliding Window Ranged over Session
        - SQL
        - ROM Based
        - ***Memory Ingestion*** Checkpint Based Memory: 
            - Conversation (Query and Response) [User Memory]
            - Intermidary Steps from Query to Response [Agent Memory or Tool Memory]
    - Episodic Memory (Long Term Memory) / (Secondary Memory)
        - Past Sessions Trasactions
        - Sessions Combined
        - ***Memory Ingestion*** Compressed/Summarized Past Sessions beyond Sliding Window (Session Memory) using a Background Job for Memory Ingestion
            - Lexical component and Semantical component (Hybrid)
            - Input: User Memory Summary + Recent Session Trasactions from Sliding Window from Session Memory + Creation Date + Similar Memory from Current Episodic Memory
        - Different/External to Conversational Memory
        - Lexical + Semantic [Single Entity] using Possibly a Knowledge Graph
        - Here, Sliding Window is build using 
            - Most High Scoring Session Memory (Procedural and Converstional Memory)
            - Time Based
    - Log Memory:
        - User Activity Log
        - System/Application Log
        - Audit Log

### Memory Storage Layer
- Agent Memory Cache:
    - Query-Response Cache
    - Lexical or Semantic Nature
    - Expiration;
        - Time
        - Scoreing
        - Usage Frequeny    
        - ***Weight Bias -> Move Down by One Layer -> Eject***
- Reference to Other Memory Storage Layers
    - Computer Memory : Cache <-> RAM <-> Disk <- Data Sources
    - Application Memory : In Memory Cache <-> DataBase -> Data Warehouse <- Data Sources
    - Agent Memory : Cache <- Session -> Main -> Episodic 
                                          ^
                                     Data Sources

### Memory Retrieval
- [User Prompt + System Prompt] + [Tools (For Each Step in COT/Plan) + Agents (For Each Step in Plan/COT)]
- Plan the Steps and then Execute those Steps, that makes the whole flow Multi-Turn [Plan and Execute Design]
- For Each Plan-Step, generate a Chain of Thought that makes each step Multi-Turn
- The COT-Steps will be guided by Knowledge Graph's Entity Relationships [Reason and Act and Observe Design]
    - Search first happens in Main Memory then in Similar/Identical (hybrid) in Secondary Memory based on Similarity/Identicality Thresholded-Score
        - Main Memory (Short Term / Session): KnowledgeGraph -> SQL Records + VectorDB Vectors
        - Secondary Memory (Long Term / Episodic): KnowledgeGraph -> SQL Records + VectorDB Vectors
    - Reranking using Lexical or Semantic Method + an Offset Marker like Top N
    - ***Note***: Here Lexical Operation with happen in SQL Metadata and Semantical Operation in VectorDB Vector Space
- Context : User Prompt + System Prompt (Role + Objective + Method + Guardrails + Tone + Output Format) + Retreived Memory (Business Memory + User Memory + Agent Memory)

---

### Agent Memory Failure Modes
- Staleness 
    - Old Data is expired 
    - Data with less weightage & bais is ignored
- Wrong Retreival 
    - Metadata lexical filtering + Semantic Search (Hybrid)
    - Ingest Conservatively + Retreive Agressively    
- Model Drift or Data/Context (RAG Source or Fine Tuning Source) Drift <- Poisoning (Weight and Baises of Vectors in Data Source or Model changed in such a way that deviates the Agent from its functionality) <- Internal (such as Data Ingestion Bugs) Reason or External (such as Feedback) Reason 
    - Read Isolation By Default (Agent should read only the relevant data/context for the given task not everything, this way it will avoid the poisoned data/context)
    - Model or Data/Context Sanitization (Detect/remove prompt-injection patterns); then Output Validation (Validate what the agent has done in output)
    - Model or Data/Context Scoping / Namespaces (Separate vector space; do not one space poison the other)
    - Re-adjust the Weights & Baises by Re-Embedding or Re-Finetuning
- Token Explosion (Context to the Model increases with Every Turn)
    - Have a Data Budget Cap on Every Memory Layer; if Exceeded then Summarize/Compress to Deeper Layer with Vector & Metadata 
    - Expire the Data
    - Decrease the Weightage & Bais
- User and Agent Privacy
    - Tag Data with User ID 
    - Tag Data with Target ID
    - Scope the Data Retreival to User and Target ID 

### Memory Management and Query Rewriting are related
- Use the Memory to infuse User Query with relavant Information so that it becomes independent of other User Queries 
- This Rewritten User Query should be used down stream
- How to Infuse is below in ***Routing to Memory Layer*** Section

### Routing to Memory Layer
- Hybrid Approach
- Rule Based [Regex for Keywords] + LLM [Conditions in System Prompt with]
- Rule Cheap and Structured Prompt
- LLM Expensive and Unstructure Prompt
- Fused Rank from Both Approach
- Return will be the order of the Memory Layer to Retreived

---

***Note***:
- Equailty :
    - Semantics - Exact, TF-IDF (BM25), Lexical - Exact, TF-IDF (BM25) 
    - Semantics - Cosine Similarity (ANN), Lexical - Levenstein Distance (Fuzzy)
- Indexing:
    - Lexical (Normalization) - Tree + Map + Linked-List
    - Semantics (Clustering/Segmentation) - LSH + HSWN + Quantization/Centroid + TextTiling
- RAG is nothing but Factual Memory

