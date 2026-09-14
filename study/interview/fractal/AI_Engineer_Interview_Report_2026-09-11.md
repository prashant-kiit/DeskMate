# AI Engineer Interview Report

## Overall Score

**5.5/10 — Borderline / Risky for a strongly Agentic-AI-focused client round**

**Main issue:** The candidate demonstrated practical AI/RAG/agent exposure, but several answers on evaluation, fine-tuning, and security were technically weak or inaccurate. The interviewer explicitly questioned the depth of AI experience.

## Questions & Answer Assessment

| # | Interview Question | Answer Summary | Score |
|---|---|---|---:|
| 1 | What AI/Agentic experience have you had in the last 3 years? | Described RAG chatbot, LLM evaluation platform, AI security, interview moderator. | **7/10** |
| 2 | What was your role in the RAG/chat application? | Claimed end-to-end SDLC: requirements, architecture, implementation, testing, deployment. | **7/10** |
| 3 | How did you manage memory in the chat application? | User memory + session memory in Postgres; sliding-window summarization; LangGraph checkpoints. | **8/10** |
| 4 | How did you handle queries requiring more details / human input? | Initially answered access-control/intent; after clarification, explained Human-in-the-Loop using graph interrupt + FastAPI resume flow. | **6/10** |
| 5 | What evaluation framework did you use? | LangSmith. | **7/10** |
| 6 | What did LangSmith trace and how was it configured? | Described node/edge traces, checkpoints, stronger LLM judge, configuration/API key. | **6/10** |
| 7 | How did you ensure end-to-end traceability? | Frontend activity tracing + LangSmith backend tracing; described passing tracing configuration to graph compilation. | **6/10** |
| 8 | Explain your prompt-injection mitigation. | LLM-based detection, few-shot examples, regex/deterministic removal, fallback LLM rewriting. | **4/10** |
| 9 | Give examples of prompt-injection few-shots. | Used “ignore previous prompts” type example and structured LLM output. | **4/10** |
| 10 | What quantitative metrics did you use for evaluation? | Precision and recall; described golden dataset. | **3/10** |
| 11 | How can precision/recall work when LLM answers differ from golden answers? | Proposed an LLM comparison approach, but incorrectly claimed fine-tuning was required. | **2/10** |
| 12 | Did you fine-tune the model? | Said yes, using PyTorch. Later admitted detailed fine-tuning was handled by a separate data-science team. | **1/10** |
| 13 | Which model did you fine-tune? | Claimed GPT-5 on AWS Bedrock. | **0/10** |
| 14 | How did you fine-tune it? | Gave vague PyTorch/hyperparameter explanation and claimed a private GPT-5 instance in Bedrock/VPC. | **1/10** |
| 15 | Why did you fine-tune the model? | Said fine-tuning was needed so the LLM judge could understand correctness against the golden dataset. | **2/10** |
| 16 | How large was the fine-tuning dataset? | Claimed 1,000+ rows. | **3/10** |
| 17 | What AWS experience did you have? | Confirmed AWS use for the chatbot. | **5/10** |
| 18 | Describe your RAG architecture/components. | Query → retriever → vector DB → cross-encoder reranker → prompt → LLM; ingestion/chunking/embedding pipeline. | **8/10** |
| 19 | How did you evaluate each RAG component? | Admitted no separate RAG evaluation; mainly end-to-end evaluation. | **3/10** |
| 20 | How do you evaluate a retriever logically? | Identified relevant-document retrieval and primarily recall; later acknowledged precision. | **5/10** |
| 21 | Why not precision for retrieval? | Initially emphasized recall/groundedness; accepted precision after interviewer challenge. | **4/10** |

## Strong Answers

- **Memory architecture:** User memory, session memory, summarization, sliding window and LangGraph checkpoints were clearly described.
- **RAG architecture:** Good high-level understanding of ingestion, chunking, embeddings, vector search and cross-encoder reranking.
- **Human-in-the-loop:** Correctly described interrupting an agent graph and resuming after human action.
- **Practical breadth:** RAG, evaluation, security, MCP, agents and AI interview moderation were all discussed.

## Weak / Risk Areas

### 1. Fine-tuning — Critical
The biggest problem in the interview.

The transcript shows claims around **“GPT-5 on Bedrock,” private GPT-5 instances, PyTorch fine-tuning and 1,000-row fine-tuning data** that the interviewer challenged repeatedly. The candidate eventually acknowledged that the detailed work was done by a separate data-science team.

**Impact: Very High.**

### 2. LLM Evaluation
The answer conflated:
- Golden dataset
- LLM-as-a-Judge
- Fine-tuning
- Precision/recall

The interviewer specifically challenged how precision/recall apply to free-form generated answers.

**Impact: High.**

### 3. RAG Evaluation
The candidate could explain the RAG pipeline but could not confidently explain component-level evaluation, especially retriever evaluation.

**Impact: High.**

### 4. Prompt Injection
The proposed approach relied heavily on an LLM to detect/clean malicious instructions and regex removal. It lacked a strong explanation of layered defenses, instruction/data separation, tool authorization and downstream impact.

**Impact: Medium-High.**

### 5. Communication
Several answers were indirect and became defensive when the interviewer challenged details. The interviewer repeatedly had to narrow/restate the question.

**Impact: Medium.**

## Interviewer Signal

The strongest negative signal was explicit:

> The interviewer said the candidate did not appear to have enough Agentic-AI experience and that the client interview would be **very focused on Agentic AI**.

This concern is directly visible in the transcript. fileciteturn0file0L745-L815

## Final Assessment

| Area | Score |
|---|---:|
| RAG fundamentals | **7.5/10** |
| Agent architecture | **6/10** |
| Memory/state | **8/10** |
| Evaluation | **3/10** |
| RAG evaluation | **4/10** |
| AI Security | **4/10** |
| Fine-tuning | **1/10** |
| AWS/Cloud | **5/10** |
| Communication | **5/10** |
| **Overall** | **5.5/10** |

## Priority Preparation

1. **LLM evaluation:** golden dataset, rubric, LLM-as-Judge, classification-based scoring, human evaluation, eval metrics.
2. **RAG evaluation:** Recall@K, Precision@K, MRR, NDCG, context precision/recall, faithfulness, answer relevance.
3. **Fine-tuning:** when/why to fine-tune, PEFT/LoRA, SFT, dataset requirements, evaluation and deployment.
4. **Agentic AI:** planning, tool calling, state, memory, retries, HITL, multi-agent orchestration, MCP/A2A.
5. **AI security:** prompt injection, indirect injection, tool authorization, least privilege, output validation, sandboxing, data exfiltration.
6. **Be precise about ownership:** clearly separate **“I implemented”**, **“I integrated”**, and **“the data-science team handled.”**
