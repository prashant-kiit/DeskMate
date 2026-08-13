# AI Agents Tutorial

## 1. The Spectrum of AI Decision-Making

AI systems make decisions in different ways. There are three levels:

- **Rule-based system** — Like a vending machine. Press B4, get chips. No thinking, no adapting, no surprises. Fixed script: "if this, then that."
- **LLM (Large Language Model)** — Like a knowledgeable friend. You say "I'm hungry, want something salty but not heavy." It thinks, asks follow-up questions, and makes a judgment call. It reasons using patterns learned from huge amounts of text. But an LLM alone can only talk — it cannot *do* things. It's like a smart person in a room with no phone, no computer, no way to interact with the world.
- **AI Agent** — This is what happens when you give that smart person a phone, a computer, and internet access. Now it can search for information, run calculations, send emails, write code, and call external services. An AI agent = an LLM that can **perceive its environment, make decisions, and take actions**.

## 2. Core Components of an AI Agent

1. **Brain (the LLM)** — The reasoning engine. Decides what to do next based on the goal given.
2. **Tools** — How the agent interacts with the world. Tools are functions the agent can call (e.g., "search the web," "run this code," "call this API"). This is called **tool calling** — one of the most important concepts in agentic AI. The LLM decides *when* to do *what*; the system executes it.
3. **Memory** —
   - **Short-term memory**: conversation history in the current session.
   - **Long-term memory**: information stored and retrieved across different sessions.
   - Think of it as working memory vs. a notebook you can always refer back to.
4. **Planning & Reasoning** — The ability to break a big goal into smaller steps and figure out what to do first, second, third. This is what separates a truly agentic system from one that just answers a single question.

## 3. Levels of Autonomy

Not every AI agent is equally autonomous. Think of it like driving a car — fully manual on one end, fully self-driving on the other.

1. **Single question and answer** — The model answers, you verify, you move forward. Basically a smart chatbot.
2. **Model with tools** — It can search the web or run a calculation, but you approve every single step.
3. **Multi-step agent** — Can chain multiple steps together without checking in every time. Given a goal, it figures out the path. You act more like a supervisor reviewing output at the end.
4. **Fully autonomous agent** (rare and risky today) — Takes long sequences of actions across multiple systems, makes judgment calls, and only shows results when done.

**Key point:** More autonomy = more capability, but also more risk. A mistake at step 3 can compound through every step after it. Deciding how much to trust an agent to act alone is one of the most important design decisions.

## 4. Task Execution: Linear vs. Parallel

- **Linear execution** — One step at a time, in sequence. Finish task A, then move to B, then C. Simple, predictable, easy to debug.
- **Parallel execution** — Multiple independent tasks run at the same time (e.g., one agent checks flights, another checks hotels, another checks weather, another researches restaurants — all simultaneously). Much faster when tasks don't depend on each other, but requires careful design to integrate results properly at the end.
- **Hybrid** — In real production systems, some steps run in parallel where possible, and others run sequentially because one step genuinely depends on the output of a previous step.

## 5. Agentic Design Patterns

These are reusable strategies that define how an agent reasons and operates.

### Pattern 1: ReAct (Reason + Act)
The most foundational pattern. The agent alternates between thinking and doing:
**Thought → Action → Observation → Thought → Action → Observation...**

Example: "What's Apple's current stock price and how does it compare to its 52-week high?"
- Thought: "I need the current price." → Action: call a tool → Observation: got the result.
- Thought: "Now I need the 52-week high." → Action: call another tool → Observation: got the result.
- Thought: "Now compare and answer."

### Pattern 2: Reflection
The agent doesn't just act — it looks back at what it did and critiques itself, like an internal editor. Example: drafting an email — the agent writes a draft, reviews it ("Is this clear? Did I miss anything?"), and revises. This loop can run multiple times, usually producing a much better result than the first pass.

### Pattern 3: Plan and Execute
Different from ReAct, which is reactive (figures out the next step as it goes). Here, the agent first creates a **full plan** — a sequence of steps — and then executes the plan. Like a project manager creating a roadmap before writing a single line of code, vs. a developer who just starts coding and figures it out as they go. More structured, predictable, and often better for complex, multi-step tasks.

### Pattern 4: Multi-Agent Systems
Multiple AI agents work together, each with a specific role and specialization. Like a hospital: you don't have one doctor who does everything — you have specialists (surgery, X-rays, pharmacy). Example: a **research agent** finds information, a **writing agent** drafts content, a **review agent** critiques it, and an **orchestrator agent** coordinates everything — breaking down the task, delegating to the right specialist, and integrating the final results.

### Pattern 5: Swarm
Multi-agent systems taken to the extreme. Instead of a fixed hierarchy with a clear orchestrator, you have a collection of agents that **self-organize**. They communicate with each other, pass tasks fluidly, and collectively converge on a solution. Inspired by nature — ant colonies, bee swarms. No single ant has a master plan, but collectively they build complex structures. Swarm architectures are still being explored and refined but show promise for problems too large and dynamic for a single agent or fixed pipeline.

## 6. Popular Frameworks (2026)

### LangGraph
- Built on top of LangChain, designed for stateful, multi-step agents.
- You define your agent's logic as a **graph**: nodes are actions/decisions, edges define the flow between them.
- Gives strong control over how the agent moves through a task.
- Handles parallel execution, loops, and conditional branching.
- Because it's graph-based, you can visually see the structure of what your agent is doing.
- **Best for:** production use cases needing reliability and debuggability.

### CrewAI
- Optimized for multi-agent workflows where each agent has a defined role, goal, and backstory — like casting actors for a play.
- You define a "crew" (e.g., a researcher, an analyst, a writer), give each a personality and purpose, then define the task they do together.
- **Best for:** getting started quickly with multi-agent systems; clean, readable code. Good starting point for exploring role-based agent architecture.

### AutoGen
- Originally built by Microsoft. Built around **conversational multi-agent systems**.
- Agents solve problems by talking to each other.
- Supports **human-in-the-loop** (a human participates in the conversation alongside AI agents) or fully automated back-and-forth between agents. You can configure how much human oversight you want.
- **Best for:** research and enterprise settings needing flexible, conversation-driven coordination between multiple agents.

## 7. Which Framework Should You Use?

| Need | Framework |
|---|---|
| Fine-grained control, production robustness | LangGraph |
| Role-based collaboration, fast prototyping | CrewAI |
| Conversational multi-agent workflows with human oversight | AutoGen |

## Summary

- An **AI Agent** = an LLM (brain) + Tools + Memory + Planning, able to perceive, decide, and act.
- Agents exist on an **autonomy spectrum** — more autonomy means more power and more risk.
- Tasks can run **linearly** or **in parallel** (or a hybrid).
- Five key **design patterns**: ReAct, Reflection, Plan & Execute, Multi-Agent Systems, Swarm.
- Three key **frameworks** in 2026: LangGraph, CrewAI, AutoGen — pick based on your use case.