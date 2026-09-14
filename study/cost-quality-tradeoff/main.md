## Cost and Performance Trade Off
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
    - Taking Data and Reasoning out of the Big Model to Knowledge Graph in GraphRAG + Small Model Architecture and help with Save Cost by Saving on Data and Reasoning; However downside is to Human Effort and Data Ingestion Cost
    - We downgrade a Big Model to Small Model Like Behaviour Re-tuning the Temp and Top K which reduces the Entropy by reducing Parameters thus reducing Data and Reasoning Requirements, which leads to Cost Saving
    - We can Use LLM gateway to route Requests to Big and Small Model based on Task Complexity. Or, Pass Every Request to Small Model and get it verified by the Big Model and if found of Low Quality then only ask the Big Model to Generate Response
    - Models can be hosted on Serverless Servers or Our own Infra using Ollama or other Model Engine
    - Instead of Embedding Model, one can use TF-IDF based Vectorizer for Embedding

- Context Factor:
    - Store on the Relevant and Logically Structured Data in RAG and Fine Tuning Data Source, as it helps with Reducing the Size of Context and offloads some Reasoning work from the LLM
    - Same Applies for Memory Layer, where Moving the Data from Cache to Main and Main to Secondary should happen in Scheduled Manner on basis of Relevance and Recency so only important Data in there in Memory and thus form a Smaller Context 
    - Too much of Fine Tuning can be costly so use if only for Static Data while use RAG for Dynamic Data as it cheaper
    - Data Storage can be hosted on Serverless Servers

- Business Usecase Factor:
    - Remove the Componets that do not Improve the Quality of the System
    - See if any Component can be implemented using Deterministic Code
    - If Business Use case very Repitative then use Cache of Query-Response to Save Cost

***Note***: Experiment and find out the best Cost and Performance Configuration