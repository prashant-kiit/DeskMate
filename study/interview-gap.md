# Technical AI/ML Interview Prep Report
**Candidate:** Prashant Kumar Singh &nbsp;|&nbsp; **Interviewer:** Rohan Kapoor (ML Engineer, Programming.com)

---

## A. Interviewer Profile Summary

**AI/ML experience:** ~6 years of continuous, hands-on ML/AI work — Deep Learning Intern at IIT Bombay (Sep 2020) → Data Scientist at Pyrsquare Analytics (Apr 2021–Dec 2023) → ML Engineer at Onelab Ventures, Gloify, and now Programming.com (Jan 2024–present). Unlike a typical backend-to-AI transition, his *entire* career has been AI/ML-titled.

**Strongest technical areas:**
- **Agentic AI & multi-agent systems** — built a multi-agent e-commerce chatbot (PydanticAI), an agentic finance copilot with custom MCP-based ERP integration, an agentic RAG chatbot (LangGraph + Qdrant), and a voice-driven calendar agent with human-in-the-loop confirmation.
- **MCP (Model Context Protocol)** — has *built* two MCP servers from scratch (ERP/BAQ exposure; CAD `.stp` file automation via python-OCC), plus multiple MCP/Claude-related certifications. This is a demonstrated build-depth skill, not just tool usage.
- **RAG at production scale** — Azure AI Search with hybrid search + reranking; Qdrant for agentic RAG; explicit RBAC, rate limiting, and guardrails work.
- **Computer Vision** — anomaly detection, object detection (X-rays, medical kits), OCR (Attention OCR, 87% accuracy on 100K images), pose-based quality checks (PoseNet).
- **Speech** — trained/deployed a custom NeMo speech-to-text model on SageMaker (12% WER), used Whisper for quality checks.
- **Classical ML & evaluation rigor** — Cmax drug-response prediction with leave-one-batch-out cross-validation, SHAP explainability, synthetic-data self-training loop.
- **LLM Ops / cost & observability** — cut LLM infra cost 50% via agent-flow profiling, prompt caching, and structured tracing (Logfire, LangSmith).
- **Edge deployment** — Google Coral, Intel NCS, Raspberry Pi, Redis Pub/Sub for device communication.
- Full end-to-end ML lifecycle ownership: data prep → fine-tuning → deployment, across AWS, GCP, and Azure.

**Likely questioning areas:** MCP internals, agent orchestration design choices, retrieval quality & hybrid search, LLM cost/latency trade-offs, guardrails/observability, and — given his classical-ML background — rigor of your evaluation methodology (not just "did you use LLM-as-Judge" but "how did you validate it").

---

## B. My Profile Summary

**AI/ML-specific experience:** ~2 years (Sept 2024–present, across Neuro Spark and TAO Digital). Total SWE experience is 5+ years, but the Cognizant tenure (Jul 2021–Sept 2024) was traditional backend/systems engineering — search, notifications, encryption, DB migration, payments — with no AI/ML tooling in that stack.

**Strongest areas:**
- Production RAG (PgVector-backed report generator over transcripts/meetings/video).
- LLM evaluation (built a platform benchmarking 4 models on accuracy, hallucination rate, latency, and token cost via LLM-as-Judge).
- Multi-agent orchestration — led a 4-engineer team building an orchestrator-worker SDLC harness; personally built the orchestrator and agent-handoff protocol.
- AI log-analysis agent doing cross-service root-cause correlation.
- Real-time transcription with PII/PHI redaction (compliance-sensitive, healthcare domain).
- Strong system-design instincts — you consistently articulate explicit trade-offs (PgVector vs. dedicated vector DB, orchestrator-worker vs. decentralized agents, event-driven vs. polling), which mirrors how Rohan frames his own decisions. This is a real communication strength to lean on.

**Relevant projects:** AI interview moderator, RAG report generator, log-analysis agent, multi-agent SDLC harness, content moderation service, recommendation engine (ranking component), LLM eval platform.

---

## C. Experience Gap

| Area | My Experience | Interviewer's Experience | Gap | Interview Risk |
|---|---|---|---|---|
| RAG / retrieval | PgVector, small scale (~20k vectors), single-DB co-location | Azure AI Search with **hybrid search + reranking**, Qdrant | Moderate — you have real prod RAG, but not hybrid/reranking or scale | 🟠 High |
| MCP | Listed in tech stack (Aug 2025–present); no described build | **Built 2 MCP servers** from scratch; certified in MCP | Large — usage vs. architecture | 🔴 Very High |
| Multi-agent orchestration | Orchestrator-worker pattern (custom), agent-handoff protocol | PydanticAI, LangGraph, orchestration + guardrails + observability | Small-moderate — both have real depth, different frameworks | 🟡 Medium |
| LLM evaluation | LLM-as-Judge across accuracy/hallucination/latency/cost | Similar LLM-centric evaluation, plus rigorous classical-ML eval (CV, SHAP) | Small on LLM eval; large on classical rigor | 🟡 Medium |
| Computer vision | None | Object detection, OCR, anomaly detection, pose estimation | Full gap | 🟠 High |
| Speech/NLP model training | Whisper used as a tool (integration only) | Trained/deployed custom NeMo STT model | Moderate | 🟡 Medium |
| Cost/latency optimization | Not quantified in profile | 50% LLM cost reduction via profiling, caching, tracing | Moderate | 🟡 Medium |
| Cloud/deployment | AWS (non-AI, at Cognizant) | AWS, GCP, Azure — all for AI workloads, incl. edge | Moderate | 🟢 Low-Medium |
| Guardrails/RBAC/PII handling | PII/PHI redaction pipeline | RBAC, rate limiting, prompt-based guardrails | Small — overlapping domain, different angle | 🟢 Low |
| Backend/API design | FastAPI, gRPC, microservices | FastAPI, LangChain gateway design | Small | 🟢 Low |

**Overall:** Rohan has roughly 3x your AI-specific tenure and a noticeably broader surface (CV, speech modeling, classical ML, edge, multi-cloud). Your depth is narrower but real and recent — production agentic AI, RAG, and LLM evaluation shipped in the last ~12 months. Expect him to test judgment and trade-offs more than raw definitions, since your production experience overlaps meaningfully with his own.

---

## D. High-Risk Topics (Ranked)

1. 🔴 **Very High — MCP architecture/internals.** He's built two MCP servers; you list MCP as a tool. This gap is the most exposed one.
2. 🔴 **Very High — Hybrid search & retrieval at scale.** PgVector at ~20k vectors vs. his Azure AI Search hybrid+reranking system.
3. 🟠 **High — Computer vision / OCR / object detection.** Zero overlap; he has extensive CV work.
4. 🟠 **High — Classical ML evaluation rigor** (cross-validation methodology, explainability/SHAP, statistical significance) beyond LLM-as-Judge.
5. 🟡 **Medium — Multi-agent framework philosophy** (your custom orchestrator vs. his PydanticAI/LangGraph choices).
6. 🟡 **Medium — Quantified cost/latency optimization** for LLM systems.
7. 🟢 **Low — RAG fundamentals, LLM eval basics, agent orchestration basics.** Both have genuine production experience; this should feel like comfortable ground.
8. 🟢 **Low — Guardrails/PII/compliance handling.** Your redaction work is a strong, directly relevant answer here.

---

## E. Most Likely Questions

### Topic: MCP
**Probability:** High &nbsp;|&nbsp; **Expected Depth:** 🟠 Advanced–🔴 Expert
**Likely question:** "You've listed MCP in your stack — walk me through how you used it. Did you build a server, or just consume one?"
**Follow-ups:**
1. How does MCP differ from a regular REST tool-calling setup?
2. How would you design an MCP server that exposes both structured data (SQL) and unstructured actions?
3. How do you handle auth/permissions inside an MCP server?
**Progression he may use:** "What is MCP?" → "Why would you use it over a custom tool schema?" → "How would you version an MCP server's tools without breaking existing agents?" → "How would you secure it in production?"
**Why he may ask:** He's built two MCP servers and holds MCP-specific certifications — this is clearly a current area of personal investment for him, and your tech stack mentions MCP without a supporting bullet, which is a natural probe point.

### Topic: RAG / Retrieval Quality
**Probability:** High &nbsp;|&nbsp; **Expected Depth:** 🟠 Advanced
**Likely question:** "You used PgVector at ~20k vectors — how would that decision change at 10M+ vectors?"
**Follow-ups:**
1. What's the difference between dense retrieval and hybrid (BM25 + vector) search, and when does hybrid win?
2. How would you evaluate retrieval quality separately from generation quality?
3. What would you do if retrieved chunks were topically relevant but the answer was still wrong?
**Progression:** "What is RAG?" → "Why did PgVector make sense at your scale?" → "What breaks as vectors grow?" → "How would you add reranking?" → "How do you know reranking actually helped?"
**Why he may ask:** Direct overlap with his Azure AI Search hybrid+reranking work — he can meaningfully probe past your documented architecture note.

### Topic: Multi-Agent Orchestration
**Probability:** High &nbsp;|&nbsp; **Expected Depth:** 🟠 Advanced
**Likely question:** "Why orchestrator-worker instead of decentralized agents for your SDLC harness?"
**Follow-ups:**
1. How does your agent-handoff protocol handle a failed or ambiguous handoff?
2. How would this scale if you needed 10+ specialized agents instead of a handful?
3. How do PydanticAI/LangGraph's abstractions compare to what you built by hand?
**Why he may ask:** Both of you have real orchestration experience with explicit trade-off reasoning — this is a strong overlap area where he can go deep on design judgment.

### Topic: LLM Evaluation Methodology
**Probability:** Medium-High &nbsp;|&nbsp; **Expected Depth:** 🟡 Intermediate–🟠 Advanced
**Likely question:** "How did you validate that your LLM-as-Judge scores were trustworthy?"
**Follow-ups:**
1. What biases can LLM-as-Judge introduce, and how do you control for them?
2. How do you separate hallucination rate from factual-but-irrelevant answers?
3. How would you set up an evaluation pipeline that catches regressions before deployment?
**Why he may ask:** His Cmax project used leave-one-batch-out CV and SHAP — he clearly values evaluation rigor, so he's likely to press on *how* you validated your metric, not just what you measured.

### Topic: Cost & Latency Optimization
**Probability:** Medium &nbsp;|&nbsp; **Expected Depth:** 🟡 Intermediate
**Likely question:** "What did you do to control latency/cost as your agent systems scaled?"
**Follow-ups:**
1. Prompt caching — have you used it, and what's the cache-invalidation story?
2. How do you decide when to route to a smaller/cheaper model?
3. How do you profile where time/tokens are actually going in an agent flow?
**Why he may ask:** He achieved a 50% LLM cost reduction via profiling and caching — a concrete number you don't have an equivalent for, so he may probe whether you think about this dimension at all.

### Topic: Computer Vision (awareness check)
**Probability:** Medium &nbsp;|&nbsp; **Expected Depth:** 🟢 Basic–🟡 Intermediate
**Likely question:** "Have you worked with any vision models — object detection, OCR?" (likely a scoping question, not deep probing, since it's outside your stated experience)
**Follow-ups:** If you say no — "How would you approach adding an OCR step to one of your pipelines?"
**Why he may ask:** It's a major part of his background; he'll likely check for awareness even though it's clearly not your area, per the system's rule not to assume experience you don't have.

### Topic: Guardrails, RBAC & PII/PHI Handling
**Probability:** Medium &nbsp;|&nbsp; **Expected Depth:** 🟡 Intermediate
**Likely question:** "Walk me through your PII/PHI redaction pipeline — what's the failure mode if redaction misses something?"
**Follow-ups:**
1. How do you test redaction coverage?
2. How does this compare to prompt-based guardrails for agent outputs?
**Why he may ask:** He built RBAC/guardrails for the finance copilot — genuine overlap, and this is a strength area for you (healthcare compliance context is concrete and defensible).

---

## F. Common vs. Uncommon Areas

**Common expertise → expect deep, probing questions:**
- RAG pipelines (PgVector vs. Azure AI Search/Qdrant)
- Multi-agent orchestration (custom orchestrator-worker vs. PydanticAI/LangGraph)
- MCP (usage vs. server-building — the biggest asymmetry within a "common" area)
- LLM evaluation (LLM-as-Judge on both sides)
- Guardrails / PII / compliance-sensitive AI
- Backend/API design (FastAPI common to both)

**Interviewer-only expertise → expect conceptual/awareness-level questions, not deep drilling:**
- Computer vision (object detection, OCR, anomaly detection, pose estimation)
- Speech-to-text model training/fine-tuning (NeMo)
- Classical ML + explainability (SHAP, cross-validation, forecasting)
- Edge/embedded deployment
- Multi-cloud AI deployment (GCP/Azure specifically)
- Synthetic data generation for training

---

## G. Likely Weaknesses

| Topic | Why it's a weakness | Evidence | Likely question | Depth | What to revise |
|---|---|---|---|---|---|
| MCP server design | You use MCP but haven't described building one | Tech stack mention only, no supporting bullet | "Have you built an MCP server yourself?" | 🟠 Advanced | MCP spec basics: tools/resources/prompts, transport (stdio/SSE), how a client discovers capabilities |
| Retrieval at scale | Your only vector DB experience is small-scale, single-purpose | ~20k vectors, explicit trade-off for low ops overhead | "What changes past 1M vectors?" | 🟠 Advanced | Hybrid search (BM25+dense), reranking models, ANN index types (HNSW/IVF) |
| Classical ML evaluation | All your eval experience is LLM-centric | LLM-as-Judge across 4 models; no CV/statistical methodology mentioned | "How do you validate an eval metric statistically?" | 🟡 Intermediate | Cross-validation basics, why LLM-as-Judge needs calibration against human labels |
| Computer vision | No CV work in your history | Not present anywhere in resume | Basic awareness question | 🟢 Basic | Just enough to discuss OCR/object detection conceptually |
| Quantified cost optimization | No cost/latency numbers in your bullets | Contrast with his documented 50% cost reduction | "What's your approach to LLM cost control?" | 🟡 Intermediate | Prompt caching, model routing, token budgeting patterns |

---

## H. Final Preparation Priority (Top 12, Ranked by Expected Impact)

1. **MCP fundamentals + be ready to honestly frame your usage** (integration vs. building) — the single highest-risk gap.
2. **Hybrid search & reranking concepts**, and a clear answer for "how would PgVector need to change at scale?"
3. **Multi-agent orchestration trade-offs** — rehearse your orchestrator-worker vs. decentralized reasoning; you're strong here, make it shine.
4. **RAG evaluation methodology** — separating retrieval metrics from generation metrics.
5. **LLM-as-Judge validation/calibration** — how do you know your judge model is trustworthy?
6. **Cost/latency optimization playbook** — caching, model routing, profiling (even if hypothetical for your systems).
7. **Guardrails/RBAC framing for your PII/PHI redaction work** — a genuine strength, prepare it as a strong story.
8. **Vector DB landscape awareness** (Qdrant, Azure AI Search, Pinecone) even without hands-on use.
9. **End-to-end production AI system design** — be ready to whiteboard a RAG/agent system from ingestion to guardrails.
10. **Basic classical ML evaluation concepts** (cross-validation, why explainability matters) — just enough to not be caught flat-footed.
11. **Basic computer vision awareness** (object detection, OCR at a conceptual level).
12. **Agent-handoff protocol deep dive** — your own SDLC harness is a strength; prepare to go deep since it's genuinely yours.

**Overall framing:** Lean into your architecture-trade-off communication style — it mirrors his own, and it's your best tool for turning "I haven't done X" into "here's how I'd reason about X given what I have done."