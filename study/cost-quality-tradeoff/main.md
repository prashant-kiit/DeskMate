## Cost Consideration in AI

---

### Cost and Performance Trade Off

- Cost Factors: 
  - Model Data and Reasoning because it consumes Memory and Compute resp.
  - DataSet Context Size for RAG and Fine Tuning (Memory Aspect)
  - Business UseCase Complexity (Reasoning Aspect)
  - Human Effort
- Cost and Performance Consideration:
  - Evaluate to identify the component consuming most cost
  - Identify the reason of the cost: Model. Context or Task at hand (Functionality)
- Model Factor:
  - Small Models are good for functionalities that need Less Data and Reasoning ie. Simpler Tasks but are Cheaper 
  - Big Models are good for functionalities that need Big Data and Reasoning ie. Complex Tasks but are Costlier
  - Using Small Model can be Expensive if we will use Multi Turn; And, Big Model can be Cheaper if we use Single Turn; Using Simple Plan and Execute can be helpful
  - Taking Data and Reasoning out of the Big Model to Knowledge Graph in GraphRAG + Small Model Architecture and help with Save Cost by Saving on Data and Reasoning; However downside is to Human Effort and Data Ingestion Cost; But Effort is Lesser then Fine Tuning
  - We downgrade a Big Model to Small Model Like Behaviour Re-tuning the Temp and Top K which reduces the Entropy by reducing Parameters thus reducing Data and Reasoning Requirements, which leads to Cost Saving
  - We can Use LLM gateway to route Requests to Big and Small Model based on Task Complexity. Or, Pass Every Request to Small Model and get it verified by the Big Model and if found of Low Quality then only ask the Big Model to Generate Response
  - Models can be hosted on Serverless Servers or Our own Infra using Ollama or other Model Engine; However, Own Infra Human Effort is an additional cost
  - Instead of Embedding Model, one can use TF-IDF based Vectorizer for Embedding
  - Use Prompt Caching of LLMs
  - For Non-Interactive Apps and Self Hosted Models, use Single Threaded or Multi Threaded Batch Processing on Model to utilize 100% GPU and RAM in ServerFul Infra
- Context Factor:
  - Store on the Relevant and Logically Structured Data in RAG and Fine Tuning Data Source, as it helps with Reducing the Size of Context and offloads some Reasoning work from the LLM
  - Same Applies for Memory Layer, where Moving the Data from Cache to Main and Main to Secondary should happen in Scheduled Manner on basis of Relevance and Recency so only important Data in there in Memory and thus form a Smaller Context 
  - Too much of Fine Tuning can be costly so use if only for Static Data while use RAG for Dynamic Data as it cheaper
  - Data Storage can be hosted on Serverless Servers
  - Use Tool and Other Agent Response in Minified Form
  - Return LLM Response should be Minified for Less Token Consumption
  - In RAG and Fine Tuning Ingestion Pipeline, Cache embeddings based on Hashing (SHA or Vector Book Method) for Version Identification
  - Have a Cache Layer for Memory and RAG Both
  - Use SQL and TextToQueryRetrevier (Lexical) for very Structured Data; For Unstructured Data very Need Semantics Search in Vector DB; This would save cost for Certain Use Cases
  - In VectorDB based RAG use Hybrid Approach with BM25 First and then Similarity Search
  - If Too much of Documents are in RAG Data Store then, Use Memory Taxonomy Principles and Remove Useless Data (Old and Irrelevant Data using Low Weight and Bias) or Move it to Cheaper Store
  - Rewrite the Query to Compress it to Save Cost and make it independent in terms of Context so it does not need to go through multi turns to get the write Context
- Business Usecase Factor:
  - Remove the Componets that do not Improve the Quality of the System
  - See if any Component can be implemented using Deterministic Code
  - If Business Use case very Repitative then use Cache of Query-Response to Save Cost
  - Use Exact Query retreiver not LLM based for FAQ style questions
  - Dividing the Task over Multiple Agents and Tools can increase (Too much Compute) and decrease (Less Context Each) based the Situation
  - If Model can be used to generate the Agents and Tools in Sandbox for Performing Repetitive Deterministic Task then that can Save Cost

---

## Architecture Evolution from Cost Perspective:

- Base Big Model + Query/Response Optimization + Cache + Batching
  - Lowest Upfront Cost
  - Highest Cost In Future
- Base Medium Model + RAG + Query/Response Optimization + Cache + Batching
  - Medium Upfront Cost
  - Medium Cost In Future
- Base Small Model + Fine Tuning + Query/Response Optimization + Cache + Batching
  - Highest Upfront Cost
  - Lowest Cost In Future

---

***Note***: 

- Experiment and find out the best Cost and Performance Configuration
- Small Mode for Classification, Medium Model for Summarization and Big Model for Technical Reasoning

