# Generic AI Agent Design Process

This document is built from one source: *Designing an AI Pull-Request Review Agent*. That document designs a PR review agent step by step. Each step teaches a general lesson about building AI agents. This document pulls out those general lessons and shows the PR review agent as the working example.

---

## 1. Pick Up Reusable Thinking Tools Before You Design Anything

* **Step:** Before designing any specific agent, get four general tools ready: a way to turn a messy workflow into components, a list of common failure modes, a scale for how much a human should stay involved, and a phased build plan.
* **Reason:** These tools are not tied to one project. Using them early stops you from guessing your way through design. You apply the same tools to any agent you build next.
* **PR Review AI Agent Example:**
  * A **5-move template**: map the real workflow, name the exact trigger and output, sort each step into trigger / tool / LLM / deterministic logic / human checkpoint, choose how much autonomy to give, and plan for failure.
  * A **7-mode failure catalog** (hallucination, model drift, tool timeout, feedback poisoning, orchestration deadlock, human bottleneck, "almost-right" outputs).
  * A **5-level human-in-the-loop scale**, from full automation to full human control.
  * A **20-phase build lifecycle** that forces you to plan security, observability, evaluation, and cost — not just the "happy path."

---

## 2. Understand the Problem — Name the One Thing the System Fixes

* **Step:** Before designing a single component, ask why the system needs to exist at all. Find the one costly, scarce resource it is meant to save.
* **Reason:** If you cannot name the exact cost or bottleneck a system removes, you risk building a feature nobody needs. Naming the scarcity also tells you what "success" means later.
* **PR Review AI Agent Example:** Senior engineers' review time is the scarce resource — it is slow, inconsistent, and gets worse as reviewers get tired. The agent exists to free that time for judgment calls, not to replace human review completely. This is why the agent is designed to be **selective** (surface only high-value findings) instead of maximal.

---

## 3. Borrow Structure From a System That Already Solved a Version of This

* **Step:** Look for a mature system — human or engineered — that already does a version of the task well. Copy its decomposition instead of inventing one from scratch.
* **Reason:** Hard problems are usually solved problems in disguise. A working analogy hands you a ready-made breakdown of the work, saving you from reinventing structure that already exists.
* **PR Review AI Agent Example:** The design copies how a senior engineer reviews code. A good reviewer (1) brings codebase context, (2) reasons across separate concerns like security and testing, (3) stays skeptical, and (4) cites evidence. This directly becomes: retrieval, multiple specialist agents, and a "confidence + rationale" requirement on every finding.

---

## 4. Define the Exact Trigger, Output, and the Data Contract Between Components

* **Step:** State the exact event that starts the system and the exact result it produces, each in one sentence. Then design the shape of the object that flows between components.
* **Reason:** A system is really just components plus the contract between them. If the trigger, output, or the shared data shape is vague, every component built after it inherits that vagueness. The object passed between components usually matters more than the boxes themselves.
* **PR Review AI Agent Example:** Trigger: a GitHub `pull_request` webhook. Output: one structured review posted back to the PR. The shared object is a **Finding**, with fields for which agent raised it, severity, category, file/line, confidence, and rationale.

---

## 5. Study How the Industry Already Climbed This Problem — Find the Hidden Back Half

* **Step:** List the stages other teams have already gone through solving a similar problem, from the simplest attempt to the most capable one. Identify why each earlier stage falls short, and stand on the highest stage you can actually support.
* **Reason:** Every interesting problem has a "back half" that the simple, demo-friendly approach ignores. Naming the earlier, weaker attempts shows exactly what capability you are choosing to build.
* **PR Review AI Agent Example:** Linters → static analysis → single-LLM review → agentic fan-out. A single LLM reviewing the whole diff is the tempting shortcut, because it works in a demo — but it mixes concerns, is not grounded in the real codebase, and cannot be audited. The design commits to the fan-out stage: parallel specialist agents, each grounded and each producing evidence.

---

## 6. Ground the Agent With Relevant Context Before It Reasons

* **Step:** Give the agent only the specific information it needs for the current decision, fetched from a knowledge source — not everything, and not nothing.
* **Reason:** A model reasoning about something in isolation, without the surrounding context, tends to guess confidently instead of admitting uncertainty. This is a known failure mode (hallucination in a critical path). Retrieval-Augmented Generation (RAG) is the standard fix: fetch the relevant slice of information and put only that into the prompt.
* **PR Review AI Agent Example:** Each specialist agent retrieves relevant code, past decisions, and conventions from the codebase before judging a diff — instead of reasoning on the raw diff alone. This turns an "confident stranger" into a "colleague who has read the code."

---

## 7. Identify the Distinct Kinds of Memory or State the Agent Needs

* **Step:** Before choosing any storage technology, list the different kinds of information the agent must hold, based on how each kind is accessed (similarity search vs. exact history vs. small fixed rules).
* **Reason:** Not all state is the same shape. Mixing different access patterns into one undifferentiated bucket makes the system harder to reason about later. Naming the kinds of memory first is what should drive the storage design — not the other way around.
* **PR Review AI Agent Example:** Three memory kinds are named: **semantic** (the codebase itself — wants vector/similarity search), **episodic** (past reviews and disputes — wants time-stamped relational rows), and **procedural** (team conventions and rules — small and always loaded). A fourth kind, **time** (every action, in order), is added later for proof and audit.

---

## 8. Build a Proof Layer — Make the Agent Show Its Work

* **Step:** Record every meaningful action the agent takes — every reasoning step, every external call, every decision — as a durable, time-ordered event, from the start of the design rather than bolted on afterward.
* **Reason:** Any system making automated decisions that people might question needs to be able to defend or explain those decisions. Without a record of what was retrieved, what was asked, and what was returned, the system cannot be debugged, audited, trusted, or improved.
* **PR Review AI Agent Example:** Every span, LLM call, tool call, and decision becomes one row in a single event log. That one stream powers three things at once: a trace viewer (replay any review), an audit trail (defend or dispute a finding), and a cost ledger (see what each agent spent).

---

## 9. Decide How Much Autonomy the Agent Gets, and Let It Earn More Over Time

* **Step:** Use a confidence signal (and the stakes of being wrong) to route each case to full automation or to a human. Do not treat autonomy as one fixed setting for the whole system.
* **Reason:** Autonomy is not binary. The right amount of human involvement depends on how bad a mistake would be and how reversible it is. Starting with more human oversight and reducing it later is safer than the other way around — it's easier to remove a checkpoint than to recover from removing it too soon.
* **PR Review AI Agent Example:** High-confidence reviews with no critical findings post automatically. Low-confidence reviews go to a human approval queue. Any finding marked CRITICAL always escalates to a human, no matter the confidence score, because the cost of missing it is too high.

---

## 10. Design for Failure — Run Every Known Failure Mode Against Your System

* **Step:** Deliberately break each component on paper. For every known failure mode (timeouts, hallucination, deadlocks, poisoned feedback, human bottlenecks, and so on), decide the specific defense before it happens in production.
* **Reason:** Every agentic system fails eventually. The only real design choice is whether it fails safely. A system should always degrade to "slower but correct," never "fast but wrong" — a wrong answer delivered confidently is the worst outcome.
* **PR Review AI Agent Example:** Each general failure mode is matched to a specific defense already built into the design: grounding plus rationale defends against hallucination; retries and circuit breakers defend against timeouts; timeouts on every step defend against deadlock; a minimum-evidence threshold defends against poisoned feedback; an idempotency key defends against duplicate reviews.

---

## 11. Assemble the Full Reasoning Into One Mental Model Before Drawing Any Boxes

* **Step:** Before designing the technical architecture, write out — in plain language — how all the pieces gathered so far connect, from trigger to final output.
* **Reason:** Architecture diagrams drawn too early tend to lock in assumptions that were never checked. Writing the reasoning as prose first forces every component to justify its place, and reveals open questions (like "how many databases do we actually need?") before they get baked into infrastructure.
* **PR Review AI Agent Example:** A pull request triggers work, which is queued (not handled inline); an orchestrator fans the work out to four grounded specialists running in parallel; each specialist returns structured findings; an aggregator merges them and applies the confidence gate; every action is logged to one event stream; and a reliability layer keeps every step degrading safely.

---

## 12. Choose Storage by the Shape of the Data, Not by Habit or Trend

* **Step:** Resist reaching for a new, purpose-built database for every kind of data. First ask what shape the data actually is, and whether an existing, well-understood store can honestly handle that shape.
* **Reason:** Splitting data across many specialized stores adds real cost: more connection pools, more backups, more failure points, and no simple way to answer a question that spans more than one store. Consolidation is only good when the single store can genuinely support every shape of data being asked of it — not by hiding a workload it can't really handle.
* **PR Review AI Agent Example:** Memory (code embeddings), truth (review records), and time (the event log) look like three separate databases at first. The design instead uses one Postgres-compatible database (Tiger Cloud) with extensions for vector search, and time-partitioned tables for the event log — because a single question like "what did we retrieve, what did we decide, and what did it cost for this PR?" needs to be answerable without stitching together three systems.

---

## 13. Hide Hard or Uncertain Decisions Behind a Narrow Interface

* **Step:** When a decision is genuinely uncertain (a technology choice, a scaling strategy), don't over-invest in the "correct-looking" heavy option up front. Pick the cheaper option now, but hide it behind a small, stable interface so it can be swapped later without touching the rest of the system.
* **Reason:** Premature commitment to the "scalable" option is its own form of technical debt. A narrow interface turns an expensive, system-wide decision into a one-file swap later, once real usage data justifies the more complex option.
* **PR Review AI Agent Example:** The orchestration engine (LangGraph) is chosen over a heavier workflow engine (Temporal) because it needs zero extra infrastructure and fits today's scale. But all orchestrator code goes through one abstract interface (`run`, `resume`, `get_state`), so if scale later demands Temporal, only the implementation behind that interface changes.

---

## 14. Turn the Reasoning Model Into an Actual Architecture

* **Step:** Only after the reasoning above is settled, draw the real components: how requests enter the system, how work is coordinated, how specialist reasoning steps are merged, and how context is retrieved — each box traced back to a specific principle from the steps above.
* **Reason:** An architecture built this way is defensible — every component has a reason for existing, instead of being included because it seemed standard. This also makes the design easier to explain, review, and change later.
* **PR Review AI Agent Example:** A webhook is verified and queued, never handled inline (from the "design for failure" step). An orchestrator runs four specialist agents in parallel and checkpoints progress (from the "borrow structure" and "design for failure" steps). An aggregator merges findings and applies the human-in-the-loop gate (from the "autonomy" step). A hybrid retrieval layer (vector search plus keyword search) feeds each specialist (from the "grounding" step). One event stream feeds the trace viewer, audit trail, and cost tracker (from the "proof layer" step).

---

## 15. Plan the Build in Small, Independently Provable Phases

* **Step:** Break the build into ordered phases. Each phase should prove one specific thing works before the next phase begins, covering not just the "happy path" but also security, evaluation, observability, reliability, cost control, human-in-the-loop workflows, and continuous learning.
* **Reason:** Beginners tend to design only the happy path (receive input, reason, respond). A production-ready agent needs the "back half" too: how it is observed, secured, recovered, governed, and improved over time. Proving each phase before moving on keeps the whole system in a working state throughout the build, instead of discovering integration problems at the end.
* **PR Review AI Agent Example:** A 20-phase roadmap covering cognitive design, system architecture, frontend, backend, orchestration, LLM reasoning, memory, tooling, multi-agent coordination, evaluation, observability, security, reliability, infrastructure, data engineering, governance, economics, developer experience, CI/CD, human-in-the-loop, and continuous learning — each phase with a written "green gate" before the next one starts.

---

## Conclusion

Designing an AI agent is not picking a parts list off a menu. It is a chain of questions, each one earning the next piece of the design:

1. Get reusable thinking tools ready first.
2. Name the exact problem and the scarce resource being saved.
3. Borrow structure from a system that already solves something similar.
4. Nail down the exact trigger, output, and the data contract between parts.
5. Learn from how others have already approached this problem, and choose your stage deliberately.
6. Ground the agent's reasoning in relevant, retrieved context — never let it guess in isolation.
7. Name the different kinds of memory the agent needs, by how they're accessed.
8. Make the agent prove its own work with a durable, time-ordered record.
9. Let the agent earn autonomy case by case, based on confidence and stakes.
10. Design for every known failure mode before it happens in production.
11. Assemble the full reasoning into one mental model before drawing any boxes.
12. Choose storage by the actual shape of the data, not habit.
13. Hide uncertain decisions behind narrow interfaces so they're cheap to change later.
14. Turn the reasoning into an architecture where every component is traceable to a principle.
15. Build in small phases, each proven before the next begins.

If a piece of an agent's design cannot be traced back to a question you can defend, it is either missing its justification or it does not belong.