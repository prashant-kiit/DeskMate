RAG Architecture in Production:
* Chunking
* VectorDB
* Hybrid Retrieval
* Caching
* Scaling and Optmizations
* Patterns

----

Steps:

* Procssing
* Retrivel
* Caching
* Monitoring

----

Caching - Same QnA
Vector + Key Value Search 
Streaming
Horizontal Scaling for Compute and Memory

-----

Document Porcessing
* Chunking
* Fixed Size - Struggle with Contexts
* Structure - Para, headers etc.
* Different Type - Pdf, Legal, Research Paper, etc.
* Recursive - Big to Small, Stop at a partialur Size
* Semantics - Menaing 
* Overlap - Chunk - Common - Chunk

Big - Imprecision + Context
Small - Prcisiso n + No COnext
balance based on Use case

-----

Metadata Arch:
* Ranking & Filtering
* Conext Info
* Source, Time, Vcersion, Doc Type
* Pre retrreiveal fliltering -> Semantics : More Performance and Response, Domain & Time Filtering
* Metdata + Embedding 
* Query -> Metadata Schema

---

Embedding
* Costly <- Model and Chunk size, Check The provider, Dimessions 
* Update the old/stale one based on Time metadata to save cost
* More Dimesion, Cost and Procision
* Embeding Optimization
    * Max request batch 
    * Less then Rate Limit
    * Caching for depulicates/update with Metadata key for identifications
    * Save reducnt API calls
    * use quality emanediing model for prevent requeruies to VectorDB and LLM to get precise answer 

----

VectorDB Selection
* Cost vs Operatioal Simpilicity
* Managed -> Small Team, No DevOps, Demanding Customer, Auto Scaling, Varying Prices (High in general)
* Slef Hosted -> Low cost, DevOps Team, Scale and Control, Operations High, Big Team
* Query Volume,
* Storage Size,
* Start with managed -> scale big -> self hosted

----

Vector DB Arch:
* Index NN
* Search
* HNSW (O(logn))
    * M: is a hyperparameter that defines the maximum number of bidirectional connections (edges/neighbors) created for each node (vector) per layer in the graph
    * ef_search: Defines how many candidate neighbors are evaluated at each step of the graph search.
* Brute - linear search (O(n))
* Linear is Exact NN is Approx.
* Index in Memory for Traversal (Increases Memory/compute(cost) + high latency)
* M and ef_search High -> high memory/compute (cost) + high latency
* Balance of Tradeoff
* Do not use Default parameter and hypermeter
* Hot and cold Storage
* Hot - Recent Data, Big Index
* Cold - Old Data, Small Index

----

Sharding:
* High Latency , High Resource
* High index, Query/time, hardware, Vector Dimesinlaity etc.
* Hot Docs in Hot Shards , Cold in Cold
* Less Shard to More Shard
* Perform Load/Stress Shard

----

Hybrid Search
* Vector - Semantics - Meaning (Cosine Similarity Score)
* Keyword - Syntax - Exact (BM25 Score)
* Parallel/Concurrent -> Reduce Latency (Usauall  avoid Sequentential operation if not use case demands)
* RRF both -> Postionial Combinitn
* Deduplicate or we can pick the common ones
* Merge -> Reranking (Vector + Keyword)
* Semantics Query -> Smeatics
* Exact Query -> Keyword
* Hybrid Search -> Good Response -> Less Retries -> Less Cost
* Error Hanling, Retrey, Timeout, Circuit Break, Bulkhead and Monitoring

----

Reranking
* cross encoder (query and document together) vs bi coder (separately)
* Use cross encoder -> More accurate
* adds latency -> more computation but user gets better ux
* filter the best from reranked data thus make pipeline lean and accurate

-----

Context Assembly
* After Reranking
* Add Chunk with metadata such as Document Name, Page No, Section Name etc.
* Stay within the Model Context Window and Keep Clearing the Chat Session

----

Diversity Constraint
* Add Diversity Constraint (Kinf off Deduplications)

----

Fallback
* If retreival Score is less than return a error message

-----

LLM integration Architecture:
* Prompt = System + User + RAG (Context)
* System -> Boundary, Use Context, Use Documents
* Stream Message (Time to First Token is More Important Total Response Generation Time, Early Termination, Saves Money)
* Retry Logic, Timeout, Fallback, Circuit Breakers to Cache Previous Response

----

Prompt Engineering:
* Role
* Rules, Input, Context, Behaviour, Format, Concise and Complete, Cite Sources, If No Context/Answer then Say 'Don't Know'
* Delimitation and Label
* User Query at the End
* Good Structure
* Do A/B Testing on Golden Data -> Experiment

----

Multi Layer Cache:
* (Query + Context) Response Cache
* RAG/Tool Indexing (Query + Context) Request Cache
* RAG/Tool Retreival Response Cache
* LLM Response Cache
* Useful in Repitative Queries Use Case
* Cache Removal: Revlidation, Hashing (Version Control), TTL
* Cache Implementation

----

Cost Optimization:
* Model Provider
* Model
* Context Types
* Context Types
* Rate Limiting
* Per Query Cost
* Per Response Cost
* Per Token Cost
* Infra Cost
* Mehtods:
    * Caching
    * Hybrid Approach
    * Lean down the Request and Repsonse Cycle by Chunking and Streaming
    * Quality Request and Response to Prevent Looping
    * Parallel Processing
    * Archival of Relevant Data
    * Smart Infra Choice
    * Log. Algo for Less Time and Space Complexity
    * Monitoring the Cost of each Component to narrow down the high cost part
    * High Quality DB and Model can also Reduce cost by Prevent Looping
    * Model toggling

----

Observability
* Response Quality
* Monitor No of Follow Up Questions and Abandonment Rate
* Responses are Fast
* Traffic
* Availabilty
* Cost
* Security
* Cache hit rates
* Error rates
* Setup Alerts

----

Evaluations:
* Human as Judge
* LLM as Judge
* Feedback
* Normal Tests
* Steps:
    * Dataset: Simple query, Thinking Query, Mutli answer Query, Query is insufficent COntext
    * Isolate Retreival and Generation
    * Retreival - Precision, Recall, nDCG (Normalized Discounted Cumulative Gain) measures how well a ranked list puts the most relevant results near the top, giving higher weight to higher-ranked positions.
    * Generation - No Halucination, Accurate and Precise
* CI/CD
* Have GroundhTruths and Thresholds

---

Scaling
* Shard based on Type for Scaling
