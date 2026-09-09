# System Design

## What can go wrong?

1. Hallunication: Answers that Imanaginery; Not based on Prompt, Context or Memory
    - 'I do not know' response
    - Prompt and Loop Engineer for Validation Step in COT 
    - Valdiator as Agent (LLM as Judge)
    - Valdiator as Human (Human in Loop)
    - Above can be implement use Pydantic Validator Syntax (at attrubute or Object Level) at Interface 
2. Model Drift: Change in Data Input, Output and Input-Output Relations leading to Unseriable Responses
    - Continuous Evals
    - Monitoring Logs
    - Run Periodic Fune Tuning or (Retraining) of LLMs
    - Model Drift Fallback
3. Tool Call Failure: Tool calling failed
    - Error Handling
    - Retry
    - Timeout
    - Fallback
    - Circuit Breaker
    - Monitoring
4. Feedback loop poisoning: Model stores wrong rule or vector in DB
    - Eval
    - Archive
    - Validation by Human, LLM or Pydantic
    - Monitoring
    - Periodic Archival and Audit
    - Ask LLM to provide Evidence and Threshold
5. Orchestration Deadlock
    - No Deadlock
    - Timeput on every operation
6. Human in the Loop
    - Capacity Planning
    - Prioritize Task
    - Task delegation across Team
    - Ask Human's Feedback

----

## Degree of Automation and Human Intervention

1. Full Automation
2. Human verifies output
3. Easy Case automation, complex by AI
4. Human Decides and AI collects context
5. Human does main thing, AI is assistant

***Note***:
- Risk increses from 5 to 1
- Complexity is Risky
- As Complexity increases, Risk increases thus use of AI should decrease
- So, AI automation is good for greenfield projects then brownfield

----

## System Plan

| Phase                        | Concern                                                                  |
| ---------------------------- | ------------------------------------------------------------------------ |
| **0 Cognitive Design**       | What thinking should the system perform; autonomy level; HITL boundaries |
| **1 System Architecture**    | Boundaries, style, module graph, ADRs                                    |
| **2 Frontend**               | Dashboard shell, streaming, agent transparency                           |
| **3 Backend & API**          | FastAPI, webhook, idempotency, state                                     |
| **4 Workflow Orchestration** | Topology, checkpointing, parallel fan-out                                |
| **5 LLM & Reasoning**        | Model routing, structured output, prompt registry                        |
| **6 Memory Architecture**    | RAG, hybrid retrieval, the vector lane                                   |
| **7 Tooling & Sandboxing**   | Tool registry, permissions, Docker isolation                             |
| **8 Multi-Agent Systems**    | Roles, contracts, the aggregator                                         |
| **9 Evaluation**             | Golden datasets, LLM-as-judge, regression gates                          |
| **10 Observability**         | Traces, token cost, alerts – the events spine                            |
| **11 Security**              | Threat model, prompt injection, RBAC, Zero Trust                         |
| **12 Reliability**           | Circuit breakers, idempotency, checkpointing                             |
| **13 Infrastructure**        | Containers, queues, data-layer provisioning                              |
| **14 Data Engineering**      | Ingestion pipelines, schema, encoding                                    |
| **15 Governance**            | Audit trails, explainability, residency                                  |
| **16 Economics**             | Token cost attribution, budget caps, routing efficiency                  |
| **17 Developer Experience**  | Prompt playground, trace viewer, replay                                  |
| **18 CI/CD for AI**          | Prompt versioning, eval gates, canary releases                           |
| **19 Human-in-the-Loop**     | Approval workflows, escalation, dispute                                  |
| **20 Contiuous Learning**    | Feedback loops, drift detection                                          |

----

## Steps to Design
1. Find the Objective of Product to Deeper and Deeper Level
2. Machinify A Human and Prepare a Workflow
3. Think about Memory (Short Term, Long Term, Internal, External, Cached In, Cached Out, Lexical Data, Semantic Data etc.)
4. Think about Procedure (User Prompt, System Prompt, Loop, Plan, Chain of Thought, Flow Graph and Memory Graph, Human in Loop etc.)
5. Think about Evalutions (Golden DataSet, Production Tracktion, State and WorkFlow Tracking etc.)
6. Handle Failure Modes
7. Monitoring

----

## Components
1. LLM
2. API gateway
3. Prompt and Loop
4. Tools
5. Databases (Memory)
6. Ingestion
7. Trigger
8. Observability


