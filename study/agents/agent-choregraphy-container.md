# Multi-Agent Systems on Kubernetes: A Complete Tutorial

> This tutorial is built from a conference talk about running coding agents (like Codex and Claude-based harnesses) as a fleet, using chat apps as the front end and Kubernetes as the back end. It follows the story from "one agent in a Discord channel" to "a Kubernetes-based orchestrator that spins up agents on demand." Two projects come up: **OpenClaw** (an open-source, Discord-first agent bot/harness that the speaker maintains) and an open-source **Kubernetes orchestrator** built at the speaker's company, TextCortex.

---

## 1. The Building Blocks: Harnesses and Protocols

Before building a multi-agent system, you need to understand the two layers every agent setup is made of: the **harness** (what runs the agent) and the **protocols** (how the agent talks to tools, humans, and other agents).

### 1.1 Agent Harness

**Concept:** A harness is the wrapper program around a language model that gives it memory, tools, and a place to run — a terminal, an IDE plugin, or a chat bot. Without a harness, a model is just a text-completion API; the harness is what turns it into something that can edit files, run commands, and hold a session.

**Key Points:**

- Examples discussed: **Codex** (OpenAI's coding agent), **Claude Code**, and **OpenClaw** (a community-built, Discord-native harness/bot).
- Harnesses evolve heavily over time — one speaker described their own harness as a "ship of Theseus": rebuilt so many times that little of the original code remains, yet it's still the same project.
- Different harnesses have different reliability profiles for different tasks (e.g., one model may be less reliable than another on complex, multi-step work at a given point in time — this changes as models improve).

**Practical Notes:** Pick a harness based on what adapters exist for it today, not just on paper capability — tooling maturity often decides which harness is usable in a given workflow.

### 1.2 MCP vs. ACP — Two Different Problems

**Concept:** People often confuse these two protocols because both have "agent" in the name, but they solve different problems.


| Protocol | Full Name              | Solves                                                                                                           |
| -------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **MCP**  | Model Context Protocol | Giving a model **tools** (APIs, data sources) to call                                                            |
| **ACP**  | Agent Client Protocol  | Standardizing how an **agent talks to whatever is presenting it to a human** (an editor, a chat app, a terminal) |


**Key Points:**

- ACP was created by the team behind **Zed**, a code editor written in Rust designed to use less memory than Electron-based editors.
- Before ACP, every editor/chat surface had to build its own custom plugin for every agent (a Codex plugin for VS Code, a separate one for Claude Code, etc.) — a lot of duplicated work.
- With ACP, you build the "client side" integration once, and any ACP-compatible agent can plug into it — and vice versa.

**How It Works:**

```
Human ↔ Client (editor / chat app, speaks ACP) ↔ Agent (Codex, Claude Code, etc.)
```

The client and the agent don't need to know anything custom about each other — they only need to both speak ACP.

**Practical Notes:** ACP adapters existed for Codex and Claude Code early on; that availability — not a technical preference — is why ACP was chosen as the starting protocol for the tooling described later in this tutorial.

### 1.3 Competing Standards: ACP vs. A2A

**Concept:** ACP is not the only agent-interop standard emerging.

**Key Points:**

- **A2A (Agent-to-Agent Protocol):** designed for **agent ↔ agent** communication.
- **ACP (Agent Client Protocol):** designed for **human ↔ agent** communication — but an agent can also use ACP to drive another agent (treating that second agent as if it were "the client").
- No single standard has "won" yet. As adoption grows, expect to support several of them side by side rather than betting on just one.

**Practical Notes:** Don't hard-lock your tooling to one protocol. Build the integration layer so a different protocol can be swapped in later without a rewrite — this is a recurring theme in the rest of this tutorial (see Section 9, "Interoperability").

---



## 2. Motivating Example: From Chat-Ops to a Real IDE



### 2.1 Discord-Driven Development

**Concept:** The whole system in this tutorial started from a simple idea: control a coding agent entirely from a chat app, so you can "code on the go."

**Key Points:**

- The workflow was jokingly called **"Telegram-Driven Development"** (because it spells TDD).
- Early version: a Claude-based bot in Discord relaying instructions to Codex, because Codex itself had no Discord connector yet.
- Problem: this meant "playing telephone" — you tell Claude what you want, Claude paraphrases it to Codex, and wording gets lost in translation. It sort of worked, but was fragile and imprecise.



### 2.2 Direct Integration Replaces the "Telephone Game"

**How It Works (evolution):**

```
v1:  You → Claude (in Discord) → paraphrases → Codex          (lossy, indirect)
v2:  You → Discord channel bound directly to Codex via ACP    (direct, no relay)
```

**Key Points:**

- The end state is effectively a **full IDE running inside Discord**: multiple channels, each bound to a separate agent session, running in parallel.
- A typical setup: 1–5 channels active at once (e.g., "Codex 1" through "Codex 5"), plus a channel running a different harness to test a specific feature (e.g., testing an ACP feature on Claude).
- This parallelism is what makes "weekend side projects" practical — you get an idea, kick off an agent, and check back later, potentially from your phone.

**Practical Notes:** This kind of tool is built by developers for themselves — it won't be fully polished, but the trade-offs are known and accepted because the productivity gain is worth it.

---



## 3. ACP-X: A CLI and Workflow Engine for Agents



### 3.1 The CLI: Bind Any Chat Channel to Any Agent

**Concept:** ACP-X started as a simple command-line tool: let one agent (or a chat channel) call any other agent over ACP.

**Key Points:**

- Built to bind a Discord channel directly to a Codex session via ACP (or via Codex's own "app server protocol").
- Originally built by another maintainer on the same team.
- Over time it grew from "one CLI command" into what the speaker calls a **"Swiss Army knife for ACP."**

**Code (illustrative CLI usage):**

```bash
# Bind a Discord channel to a Codex agent session over ACP
acpx bind --channel discord:#codex-1 --agent codex --protocol acp

# Ask the bound agent to do something (routed straight to Codex, no relay agent)
acpx send --channel discord:#codex-1 "convert docs/acp.md to a PDF"
```

**Practical Notes (a real limitation hit in practice):** Codex itself doesn't know it's running inside a chat harness, so it can't push a finished file (like a generated PDF) back into the Discord channel that triggered it. The workaround: tell the agent, in a *different* channel that the harness does understand, to deliver the file there instead.

### 3.2 ACP-X as a Workflow Engine

**Concept:** Once you can address an agent programmatically, you can chain multiple agent actions into a repeatable pipeline — effectively a workflow engine (similar in spirit to tools like n8n) that drives a Codex session step by step instead of a human doing it manually.

**Key Points:**

- Steps in a workflow can include: reproduce a bug → judge whether a refactor is superficial or fundamental → run a review pass → loop back if needed.
- The workflow captures its output as **structured JSON**, not free text, so later steps (or other tools) can consume it reliably.
- This engine is general-purpose — it's not limited to code review; any repeatable multi-step task involving an agent can be modeled this way.

**Code (illustrative structured output from a workflow step):**

```json
{
  "step": "review_pass",
  "verdict": "no_new_issues",
  "refactor_type": "superficial",
  "needs_human": false
}
```

**Practical Notes:** The philosophy here is "apply agents generously" — if a step is mechanical and repeatable, take the human out of the loop for that step, and only escalate to a human when the workflow decides it's a **fundamental** design decision, not a shallow fix.

---



## 4. Automating the Human Bottleneck: PR Review Workflows



### 4.1 The Scale Problem in Open Source

**Concept:** Once a project gets popular, the number of incoming contributions can outpace the maintainers' ability to review them by hand.

**Key Points:**

- The OpenClaw project has accumulated **60,000+ pull requests** in total, with **300–500 new PRs opened per day** on average.
- Tens of thousands of people want to add features — you cannot please everyone, and you must avoid merging low-effort "AI slop" while still using it as useful signal.



### 4.2 Triage as a Repeatable Workflow

**Concept:** Reviewing a PR is itself a repeatable sequence of checks — which means it's a good candidate for the workflow engine from Section 3.2.

**How It Works (the abstract review workflow):**

```
PR opened
  → Find the intent (what is this PR actually trying to do?)
  → Judge the implementation (is this the best possible fix? — usually no)
  → Check for merge conflicts
  → Check open review comments that still need addressing
  → Make sure CI passes
  → (ideally) all of the above resolved BEFORE a human maintainer looks at it
```

**Key Points:**

- Many PRs arrive with an AI-generated description and little human thought behind them — you still can't just discard them, because even a bad PR is a **data point**: it often reveals a real bug or a rough edge in the codebase, and should be triaged into a bucket rather than ignored.
- The realization that motivated automation: maintainers were doing the *same mechanical questions* ("what is this?", "is this the best fix?") over and over — a clear sign the process itself could be automated.
- Conflict resolution, specifically, is described as no longer something anyone needs to do by hand — agents handle it reliably now.



### 4.3 Review-Refactor Loops ("Ralph Loops")

**Concept:** Running an agent in a loop against a piece of code is often dismissed as something that produces low-quality "slop" — but the talk pushes back on that, with one condition.

**Key Points:**

- Looping an agent is fine **as long as you don't ask it to design something**. It's safe (and useful) when the loop's job is narrow: find and fix **shallow, well-defined bugs**.
- The workflow explicitly separates two refactor tiers:
  - **Superficial refactor** → let the agent just do it.
  - **Fundamental refactor** → escalate to a human; don't let the agent make architectural calls.
- Put together, this set of rules is really just a **Standard Operating Procedure (SOP)** for agents — the talk frames "workflow" as a fancier word for the same idea.

**Practical Notes:** This is the same workflow engine from Section 3.2, just pointed at PR review instead of a general task — reinforcing that one engine can serve many use cases.

---



## 5. From Personal to Enterprise Agents



### 5.1 The Personal vs. Enterprise Spectrum

**Concept:** Historically, the computer you used at work and the one you used at home were fairly similar. That symmetry breaks down with agents.

**Key Points:**

- At work, agents will consume far more inference (LLM usage) than at home, simply because of task volume and stakes.
- More inference consumption at work translates into more revenue opportunity — which is why enterprise adoption of agent tooling (like OpenClaw) is treated as a major opportunity, not just a technical curiosity.



### 5.2 On-Demand, Disposable Agents

**Concept:** The long-term vision is **one agent per task**, spun up on demand and thrown away when the task is done, rather than one long-lived general-purpose assistant.

**Key Points:**

- Each task-agent would ideally get its own identity (name, avatar) inside whatever chat tool you use.
- **Current blocker:** Slack, Teams, and Discord don't support multi-agent identity provisioning. Today, creating a second distinctly-named "agent" in these platforms means manually creating a whole new app + app manifest — not something that can be done programmatically on demand.
- Until chat platforms add that capability, task-agents that need their own identity have to live in a **separate custom UI** instead of natively inside the chat tool.
- The end vision: many agents running in parallel, each editing files independently, with all of their work kept synchronized.

**Practical Notes:** This limitation is a platform gap, not a tooling gap — it's the reason the architecture in the next section needs an external UI component alongside the chat integration.

---



## 6. Architecture: What Multi-Agent-at-Scale Actually Requires

**Concept:** To move from "a few Discord channels" to "many disposable agents running in parallel," four architectural pieces are needed together.

**Key Points:**


| Requirement                    | Why it's needed                                                                                                                                             |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Kubernetes**                 | Provides a place to spin up and tear down agent workloads on demand                                                                                         |
| **An agent harness**           | The actual thing doing the work — OpenClaw, Codex, or Claude Code, reachable via ACP                                                                        |
| **Read/write access**          | The agent needs real permission to create and edit files, not just read-only context                                                                        |
| **State/data synchronization** | Keeps each agent's file changes consistent — described as similar in spirit to `rsync`, or to whatever sync algorithm a file-sync product like Dropbox uses |


**How It Works:** Kubernetes provides the compute lifecycle, the harness provides the intelligence, access permissions let the agent actually act, and synchronization keeps multiple agents' outputs from conflicting with each other.

**Practical Notes:** None of these four pieces is optional — drop any one and the "many disposable agents" vision breaks down (e.g., without sync, two agents editing related code in parallel can silently diverge).

---



## 7. Implementation: An Open-Source Multi-Agent Orchestrator on Kubernetes

This is where the architecture from Section 6 becomes a real, deployable system — the project the speaker works on at TextCortex, separate from the OpenClaw maintainer work described earlier.

### 7.1 The Orchestrator Pattern

**Concept:** The orchestrator is built as a **Kubernetes Operator** — a controller whose job is to hide the complicated parts of running many agents (provisioning, lifecycle, wiring chat integrations) behind a simple interface for the end user.

**Key Points:**

- Motivating use case: a "concierge" agent exposed on Slack. This works fine for a small team, but bottlenecks once you have ~100 employees hitting the same single agent instance.
- Because Slack doesn't support spinning up new named agent identities on demand (see Section 5.2), the operator's answer is: when a new isolated task needs its own agent, spin up a **new Kubernetes pod** for it, and hand the user a **web link** to a dedicated UI for that agent instance instead of trying to force a new identity into Slack itself.
- The project is open source; it ships as **Helm charts** (Kubernetes's standard package format), and includes a React-based UI that runs inside the same cluster the charts are deployed to.



### 7.2 Deployment

**Code (illustrative Helm-style deployment):**

```bash
# Add the orchestrator's chart repo and install it into your cluster
helm repo add textcortex-agents https://charts.textcortex.example
helm install agent-orchestrator textcortex-agents/orchestrator \
  --namespace agents --create-namespace
```

**Key Points:**

- Deploying the Helm chart gives you: the operator itself, the web UI, and the wiring needed to connect chat platforms (e.g., Slack) to agent pods.
- Because it's just Helm charts on Kubernetes, it can be run **internally**, inside a company's own cluster — nothing about it requires a specific cloud vendor.



### 7.3 Walkthrough: Slack Bug-Triage Use Case

**How It Works (end-to-end flow):**

```
1. A bug is reported in Slack after a prod release.
2. A person asks the concierge bot in Slack to dispatch an agent to debug it.
3. The operator provisions a new Kubernetes pod for a dedicated debugging agent.
4. Since Slack can't host a full custom agent identity/UI, the bot replies with
   a link to a separate web UI (same cluster) where the actual agent session lives.
5. The conversation and the debugging work continue in that web UI.
6. The agent has a full Kubernetes pod — not just a lightweight sandbox — to work in.
```

**Practical Notes:**

- Giving the agent a **full pod** (a complete, isolated compute environment) rather than a minimal sandbox is deliberately "wasteful" in resource terms, but is treated as the better trade-off: a full computer gives the agent more power to actually solve problems, echoing the same lesson large coding-agent products have shown — more environment access tends to mean a more capable agent.
- This same setup is offered as a general-purpose "Codex-on-the-web, run internally" tool — useful for teams or open-source projects that need to process a high daily volume of issues (the talk mentions handling on the order of hundreds of issues per day).

---



## 8. Isolation Choices: Full Pods vs. MicroVMs

**Concept:** Giving an agent a real compute environment can be done at different levels of isolation, and this orchestrator isn't the only approach in the space.

**Key Points:**

- This orchestrator's choice: a **full Kubernetes pod** per agent.
- A different well-known approach (used by the OpenHands project, mentioned only as a comparison point) is **Firecracker** — lightweight virtual machines ("microVMs") originally built for serverless workloads, offering strong isolation with much less overhead than a full pod.
- The speaker is candid that they are still learning the trade-offs between these virtualization approaches, and chose full pods pragmatically because it's what they had working, not because it's proven to be the objectively best choice.

**Practical Notes:** When choosing an isolation strategy for your own agent infrastructure, weigh **resource cost** (pods are heavier) against **implementation complexity** (microVMs require more specialized tooling) rather than assuming one is universally correct.

---



## 9. Interoperability: Avoiding Lock-In

**Concept:** A recurring design goal across every layer of this system is: never hard-couple the platform to one specific agent.

**Key Points:**

- Because the integration layer is built on **ACP** (Section 1.2), the specific agent behind it — OpenClaw, Codex, or Claude Code — can be swapped without rebuilding the chat integration, the workflow engine, or the Kubernetes orchestrator.
- This mirrors the protocol-level lesson from Section 1.3: don't bet everything on one standard (ACP vs. A2A) or one vendor's agent — build the seams so either can change later.

**Practical Notes:** This is the payoff of putting ACP at the center of the stack early: every later layer (ACP-X, the workflow engine, the Kubernetes orchestrator) inherits that flexibility for free.

---



## 10. End-to-End Mental Model

Putting every section together, here is the full picture of how a request moves through the system:

```
 Chat platform (Discord / Slack / Teams)
        │  (human sends a request or a bug report)
        ▼
 ACP-X binding layer  ──speaks──▶  ACP (Agent Client Protocol)
        │
        ▼
 Agent harness (Codex / Claude Code / OpenClaw)
        │  (may run inside a workflow: intent → implementation → conflicts →
        │   CI → review loop, escalating only "fundamental" decisions to a human)
        ▼
 If the task needs its own isolated identity/environment:
        │
        ▼
 Kubernetes Operator (orchestrator)
        │  provisions a dedicated pod + hands back a web UI link
        ▼
 Agent runs with real read/write access inside its pod,
 with its state kept in sync with everything else
```

**Key takeaways to carry forward:**

1. **Separate the "what" from the "how much automation":** MCP gives an agent tools; ACP gives it a standard way to talk to whatever surface it lives on. Neither one is optional — most real systems need both.
2. **Chat-driven development scales from "one bot in one channel" to "a fleet of agents"** only once you stop relaying instructions through an intermediate model and bind agents directly.
3. **Treat repeatable review/triage steps as workflows**, not one-off manual chores — and only escalate to a human for genuinely fundamental (design-level) decisions.
4. **Enterprise use is where the volume — and the payoff — is**, which is why the same tooling that started as a personal side-project hobby extends naturally into a Kubernetes-backed, multi-tenant orchestrator.
5. **Isolation level (full pod vs. microVM) and protocol choice (ACP vs. A2A) are both still open design questions** — build for the ability to change your mind later.

