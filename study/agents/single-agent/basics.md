# Agentic AI Tutorial: The Full Ladder

This tutorial climbs a ladder — starting from a single AI model, all the way up to a fully working AI agent.

## 1. What Is a Large Language Model (LLM)?

An LLM is a **prediction machine**. You give it text, and its whole job is to predict the next most likely piece of text.

- Think of it as the smartest autocomplete ever built. It has read most of the internet, every book, every Wikipedia article, and huge amounts of code, and learned the patterns of how humans put words together.
- It scales this idea up to billions of parameters, letting it write essays, debug code, and explain physics.
- It works one small piece at a time. These pieces are called **tokens** — a token can be a word, part of a word, or a punctuation mark. The model reads input as tokens and generates output as tokens, one at a time.

## 2. Why the Same Question Gets Different Answers

Language models are **not deterministic**. Ask the same question twice, get two different answers. Here's why:

- When predicting the next token, the model doesn't pick one single answer. It produces a whole list of possible next tokens, each with a probability (e.g., "blue" 80%, "clear" 10%, "grey" 5%).
- Instead of always picking the top choice, the model rolls a weighted dice and samples from that list.
- This is controlled by a setting called **temperature**. Lower temperature = more predictable output. Higher temperature = more creative, surprising output.
- This unpredictability is not a bug — it's a feature. It's why models feel creative instead of robotic.

## 3. The Transformer Model

The invention that made modern AI possible.

- In 2017, a Google team published a paper called "Attention Is All You Need."
- Before this, models read text one word at a time, left to right, and forgot the beginning by the time they reached the end.
- The big idea was **attention** — it lets the model look at all words at once and decide which ones matter to each other.
- Example: "The trophy didn't fit in the suitcase because it was too big." Attention lets the model figure out "it" means the trophy, not the suitcase.

### Encoder and Decoder
The original transformer had two halves:
- **Encoder** = the reader. It deeply understands your input and turns your words into a rich internal meaning.
- **Decoder** = the writer. It takes that understanding and produces output, one token at a time.
- The original model used both, because it was built for translation (listen to French = encoder, speak English = decoder).

### Decoder-Only Models (Today's Standard)
- For open-ended generation (writing, chatting, coding), you don't need a separate understanding stage.
- You can just use the decoder, have it pay attention to everything that came before (including your prompt), and keep predicting the next token.
- Almost every model today — GPT, Claude, Gemini, Llama — is **decoder-only**.

### A Quick History
- In 2018, the top model was BERT (also from Google) — **encoder-only**. Great at understanding, classifying text, and search, but couldn't write a fluent five-paragraph essay.
- Then decoder-only generative models (the GPT family) took over — trained to just "keep the story going," predicting the next word forever. This unlocked the chat assistants we use today.

## 4. Modalities: Giving the Model Senses

What a model can take in and put out is called its **modality**.

- Plain LLM: text in, text out.
- **VLM (Vision Language Model)**: can take images/video as input too — e.g., show it a photo of your fridge and ask what to cook.
- **Image generation model**: produces images as output (e.g., Midjourney, DALL-E).
- **Video generation model**: produces video as output (e.g., Veo, Sora).
- **Multimodal model**: can juggle several of these at once — text and images in, text out; or text in, images out.

The underlying idea (prediction machine) never changes. Only what flows in and out changes.

## 5. From Prompt Engineering to Context Engineering

Prompt engineering isn't dead — it evolved.

- **Early days**: your raw text went straight to the model. The whole skill was in wording your prompt cleverly.
- **Today**: your message does NOT go straight to the model. There's a whole layer of "plumbing" in between that transforms, wraps, and enriches your prompt first.

### Restaurant Analogy
You don't walk into the kitchen and hand the chef your raw request. A waiter writes it down, the kitchen has standing rules on plating, and pulls the right ingredients — only then does the finished plate come back. The LLM is just the chef — not the whole restaurant.

### System Prompt vs. User Prompt
- **User prompt**: what you typed — your specific request right now.
- **System prompt**: the persistent set of instructions that stay with the model across the whole conversation (like a job description, while the user prompt is today's specific task).

### Context Engineering
- The model only knows what's inside its **context window** — the limit of what it can process at any given time (its short-term working memory).
- The model has no idea who you are or what happened yesterday, unless you put that information into its context.
- **Context engineering** = the discipline of deciding what goes into the context window, in what order, and how much of it.

### Components That Feed Into Context
1. System prompt (persistent instructions)
2. User prompt (current request)
3. Conversation history (what you said earlier)
4. Retrieved knowledge (relevant documents pulled in from outside — this is RAG)
5. Tool definitions (descriptions of actions the model is allowed to take)
6. Memory (longer-term facts about you and the task)

## 6. RAG (Retrieval Augmented Generation)

RAG is how you make a model that knows everything in general actually know something about **your specific world**.

**Analogy**: A language model alone is like a brilliant student taking a closed-book exam — limited to what it memorized during training, which has a cutoff date. RAG turns it into an open-book exam — before answering, the student can flip to the exact right page of the textbook.

### Three Parts of RAG
1. **Retrieval** — the model finds the most relevant information, usually from a **vector database**. A vector database stores documents in a way that lets the system search by meaning, not just keywords.
   - This relies on **embeddings**: converting text, audio, image, or PDF data into numbers (vectors). You combine the original text, its vector embedding, and metadata, and store them in the vector database.
2. **Augmentation** — the retrieved documents are post-processed before being handed to the model: re-ranked so the best ones come first, irrelevant parts trimmed, and everything cleaned and formatted neatly into the context.
3. **Generation** — the model takes your question plus the clean retrieved documents and generates an answer grounded in real, current, specific information — instead of relying only on its frozen training memory.

## 7. Reasoning Models

One more upgrade to the "brain" before we get to agents.

- A regular model answers fast — it blurts out the most likely next token, almost on instinct.
- A **reasoning model** thinks before it speaks. It generates a private chain of thought, working through the problem step by step before giving the final answer.
- This is like a student who works through a problem on scratch paper first, instead of shouting out the first thing that comes to mind.
- For hard tasks (math, logic, complex coding), this scratch-paper thinking makes a big difference in accuracy. Models like OpenAI's o-series and DeepSeek R1 made this approach famous.
- Reasoning models are the engine of choice for most serious agentic work.

## 8. Model vs. Agent — The Key Distinction

- A language model is the **brain** — it does thinking, reasoning, and processing. But a brain floating in a jar can't actually do anything. It can think brilliant thoughts about booking your flight, but it can't book your flight.
- It becomes an **agent** the moment you give that brain a body — hands and legs (**tools**) that can go and actually do something in the world.
- **Tools** might be: the ability to search the web, run code, query a database, send an email, or call another API.
- When the brain can decide to reach for a tool, use it, see what happened, and decide what to do next — that's no longer just a model, it's an **AI agent**.

## 9. How the Loop Works: ReAct

The most fundamental agent pattern is **ReAct** = Reason + Act.

- The agent reasons about what to do → takes an action by calling a tool → observes the result → reasons again about what to do next.
- Pattern: **Think → Act → Observe → Think → Act → Observe...**
- It's exactly how a detective works a case: form a theory, check a clue, see what it reveals, update the theory, check the next clue.
- The agent loops through this cycle until the job is done. This loop is the heartbeat of almost every agent being built today.

## 10. Four Agentic Design Patterns (Andrew Ng)

1. **Reflection** — the agent critiques and improves its own work, like a writer editing their own draft.
2. **Tool Use** — giving the brain hands (covered above).
3. **Planning** — the agent breaks a big goal into a sequence of steps before actually executing.
4. **Multi-Agent Collaboration** — several specialized agents work together like a team (e.g., a researcher, a writer, and a reviewer passing work to each other).

## 11. AI Evals (Evaluations)

This is what separates a cool demo from something you can actually trust in production.

- AI agents are non-deterministic (remember the weighted dice) — the same agent can behave differently on the same task.
- **Evals** = how you measure whether your AI system is doing its job well.
- Regular software testing is simple: the answer is right or wrong (2+2=4). Agentic systems live in a world of **qualitative judgment**: Was the answer helpful? Was it grounded in a source? Did it make something up? Was the tone right? Was it safe?
- Every agentic system is specific and niche — a medical intake agent, a customer support agent, and a coding agent all need to be judged by completely different standards.
- The real work of evals is turning fuzzy, qualitative things you care about into concrete, quantitative metrics you can track. You define what "good" looks like, turn it into numbers, and measure relentlessly — because you can't improve what you can't measure.

## Summary: The Full Ladder

| Layer | What It Adds |
|---|---|
| **Model** | The brain — predicts the next token |
| **Modality** | Senses — text, image, video in/out |
| **Context Engineering** | What you feed the brain (system prompt, user prompt, history, RAG, tools, memory) |
| **Reasoning** | The brain thinks step-by-step before answering |
| **Tools** | Turns thinking into doing (hands and legs) |
| **Agent Loop (ReAct)** | Reason → Act → Observe, repeated |
| **Design Patterns** | Reflection, Tool Use, Planning, Multi-Agent Collaboration |
| **Evals** | How you know if the agent is actually working |

Once you see this ladder, you can understand any new AI system or product launch in about 30 seconds.