# AI Evals: A Practical Tutorial

Concepts only. No specific tools, languages, or vendors. Everything here comes from the workshop transcript.

---

## 1. Why evals exist

An eval is a **structured test that checks how well your AI system performs**. It measures quality, reliability, and correctness across scenarios your users will actually hit.

You need them because:

- LLMs do not guarantee consistent performance. Hallucinations happen at a meaningful rate.
- Performance degrades when you change things. A prompt edit that looks like an improvement can regress the system.
- "Vibe checks" don't scale. You need an empirical way to say a change made things better or worse.

Questions evals answer:

- Which model should I use? What's the best cost for my use case?
- Does it handle the edge cases my users hit?
- Is the output consistent with my brand voice?
- Am I improving over time? Can I catch bugs and troubleshoot?

Business payoff: less dev time, automated review replacing manual review, faster iteration and releases, model cost optimization, and non-technical people (PMs, SMEs) able to weigh in on prompt and model choices.

---

## 2. The three ingredients

Every eval is built from exactly three parts.

### Task
The thing being tested. Code or prompt. Can be a single LLM call or a full agentic workflow — complexity is your choice. **The only requirement is that it has an input and an output.**

Variants that still fit this shape:
- **Templated prompt** — variables injected from each dataset row.
- **Multi-turn conversation** — pass the whole message chain (user, assistant, tool calls) and evaluate the entire context at once.
- **Tool use / retrieval** — the task can call external services or fetch context.
- **Chained prompts** — output of prompt 1 becomes input of prompt 2, and so on. Evaluate end to end.

### Dataset
The set of test cases pushed through the task. Three fields:

| Field | Required | What it is |
|---|---|---|
| `input` | Yes | The case fed to the task |
| `expected` | No | The ideal/anticipated output |
| `metadata` | No | Anything else you want attached to the row |

### Scorers
The grading logic. **A scorer must output a number between 0 and 1**, which becomes a percentage.

Two kinds:

- **LLM-as-judge** — for subjective or contextual criteria. Use when the question is qualitative: "would a human consider this complete?"
- **Code-based** — deterministic. Use for exact, binary, objective checks (e.g. does the output match the required format?).

Use **both**. They meet in the middle and cross-check each other.

---

## 3. Offline vs online evals

| | Offline | Online |
|---|---|---|
| When | Development | Production |
| Data | Curated dataset | Real user traffic |
| Purpose | Proactively find issues before shipping | Diagnose problems, monitor quality, capture user feedback |

Same three ingredients in both. The difference is where the input comes from.

---

## 4. What to fix: the score-vs-judgment matrix

You look at an output yourself and form an opinion. You compare it to the score. Four cases:

| | High score | Low score |
|---|---|---|
| **You think output is good** | Working correctly. Move on. | **Fix your evals** — the scorer disagrees with a human |
| **You think output is bad** | **Fix your evals** — the scorer is too generous | Evals working correctly. **Fix your app.** |

The point: a disagreement between your judgment and the score is a bug in the *scorer*, not in the app. Fix the measuring stick before you fix the thing being measured.

---

## 5. Building good datasets

- **Start small.** Ten rows and one or two scorers is already tremendously useful. Don't block yourself waiting for a "golden dataset" of 200 rows.
- **Synthetic data is a fine start.** Generate initial cases with an LLM to get moving.
- **Then ground it in reality.** Once you're logging real traffic — even just staging or internal use — pull real interactions into the dataset. Coverage moves toward the true domain of user behavior.
- **Add human review** to establish ground truth and improve the `expected` column.
- **Few-shot examples** can live in the metadata column, so each row carries its own examples into the prompt.

---

## 6. Writing good scorers

For LLM-as-judge:

- **Use a stronger model to judge a cheaper model.**
- **One criterion per judge.** Don't hand it four or five things to weigh. Separate accuracy, completeness, and formatting into separate scorers.
- **Spell out the reasoning steps** it should walk through.
- **Keep context tight.** Give it the relevant input and output, not everything you have.
- **Eval the judge.** Treat the judge prompt as a task and check that its scores match what humans think.
- **Read the rationale.** Judges explain why they picked 100% or 75%. That's your tuning signal.

If the judge returns categories (excellent / good / …), map those to numbers in the 0–1 range.

### On non-determinism
An LLM judge can return different scores on identical runs. Mitigations:
- Use a higher-quality judge model.
- Run trial evals — execute the same eval several times (e.g. five) and average.
- Cross-check with a deterministic code scorer measuring similar criteria. If the judge says 0 and the code scorer says 90%, something needs attention.

### On interpreting numbers
Don't fixate on absolute thresholds. A judge that returns 100% for everything means your evals are broken. A judge that returns 30% for everything isn't necessarily bad. **What matters is the baseline** — how did this score compare to yesterday, to last week's prompt, to the previous model.

---

## 7. Two workspaces: playground vs experiment

- **Playground** — ephemeral. Load in tasks, a dataset, and scorers; run them in parallel; A/B test two prompts or two models side by side. Fast iteration loop.
- **Experiment** — a saved snapshot. Long-lived, for historical comparison. Tracks how scores change across weeks and months, and aggregates work from the whole team.

Workflow: iterate in the playground, then save the run as an experiment so it becomes part of your history.

Historically experiments had more features, so teams gravitated there; the two are converging as playgrounds get built out.

---

## 8. UI vs SDK

Both are first-class. Neither limits what you can do; they suit different personas.

**UI** — good for fast prompt/model iteration and for non-technical reviewers.

**SDK** — define tasks, datasets, and scorers as code in your repo, then push them to the platform. Reach for this when you want:

- Source-controlled prompt versioning alongside your app code
- Consistent assets across environments
- Evals running in CI (open a PR → evals run against the change)
- Complex task structures the UI can't express (e.g. multi-agent flows where different actors play different roles — the playground doesn't delineate those)

Evals defined in code and evals run in the UI land in the same experiment history, so you can compare across both.

A middle option exists: **remote evals**, where the eval is defined via the SDK but exposed inside the playground UI.

---

## 9. Production logging

Once the feature ships, you need observability: how are users using it, where are the gaps, are they unhappy.

Typical instrumentation, in increasing order of effort:

1. **Initialize a logger** pointed at a project. This authenticates and routes logs.
2. **Wrap your LLM client** — roughly one line. You get prompt, response, token counts, latency, cost, and errors out of the box.
3. **Use OpenTelemetry** if you already have that pipeline.
4. **Decorate arbitrary functions** to trace non-LLM steps.
5. **Log explicitly on a span** when you want custom inputs, outputs, or metadata.

Metadata is what makes logs filterable later. Log it deliberately.

---

## 10. Online scoring

Apply your scorers to live traffic.

Configure a rule with:
- **Which scorers** to run
- **A sampling rate** — 1%, 100%, whatever you want. Start low, raise it once you trust the numbers.
- **Which span to score** — defaults to the root span, but you can target a nested child span. Targeting a specific span is also how you scope scoring to a particular condition, rather than sampling randomly.

What it buys you:
- Early regression alerts when a score drops below your baseline
- A/B testing in production — tag traces by prompt variant and compare scores
- Real-time quality measurement without waiting for a release cycle

---

## 11. Custom views

Logs are only useful if people can find the interesting ones. Save views built from filters, sorts, and custom columns, then share them with the team.

Useful examples:
- Accuracy score below 50%
- User feedback equals 0 (thumbs down)
- Filtered by a metadata field you logged

This is what lets a PM or domain expert open one link and see exactly the rows they care about.

---

## 12. Human in the loop

Automated scorers miss nuance. Bring in the people who actually know what a correct answer looks like — SMEs, PMs, and in regulated domains, actual practitioners (doctors, lawyers). Some organizations hire external annotation services or invite reviewers in with a restricted, review-only view.

Two channels:

**Human review** — reviewers enter a dedicated review mode that hides irrelevant fields, then manually label, score, and audit interactions. Define review scores as categorical options, free-form text, or sliders.

**End-user feedback** — thumbs up/down and comments from inside your app, logged back against the span as a score.

### Using humans to eval your judge
This is the highest-leverage use. Have reviewers score a batch on the criteria you care about. Feed those human scores in as ground truth. Then treat the judge prompt as a task in a playground and check whether it reproduces the human verdicts. Tune the judge until it does.

---

## 13. The flywheel

This is the whole loop:

```
synthetic dataset
   → offline eval (playground / CI)
   → ship
   → production logging
   → online scoring
   → filtered views + human review + user feedback
   → promote interesting spans back into the dataset
   → offline eval  ...
```

The key mechanic: when you find a log worth learning from — bad score, thumbs down, weird edge case — **add that span to your dataset**. Your offline test suite grows from real failures instead of guesses.

---

## 14. Keeping evals alive as the app changes

Your task will change. That's expected, and it's the reason evals exist — so you can tell whether the change improved or regressed things.

Two things keep this manageable:

- **Have the eval call the task dynamically**, pointing at the live application code rather than a frozen copy of its logic. When the app grows from three turns to five, the eval picks that up without you editing the eval definition. Run evals on the PR.
- **Write robust scorers.** Same discipline as traditional software testing: don't write a test that's obsolete in a week. Score the underlying qualities that survive refactors, not the incidental shape of this sprint's implementation.

---

## 15. Open questions and honest limits

Things the workshop explicitly did *not* have a settled answer for:

- **Deterministic vs LLM-as-judge.** Some teams go fully deterministic, others go fully judge-based. Both work. It's use-case dependent — experiment with both.
- **Traditional ML models as scorers** (intent classification, NER, sentiment, clustering) sit in a middle ground. No consensus yet on where they fit.
- **Few-shot from live traffic.** Pulling examples out of a dataset into prompts at request time isn't a native platform feature; you'd build that workflow yourself.

---

## 16. Getting started checklist

1. Pick one task with a clear input and output.
2. Write ~10 dataset rows. Synthetic is fine.
3. Write 1–2 scorers. One LLM-as-judge, one code-based.
4. Run it. Save the run as your baseline.
5. Change one thing — a prompt, a model. Compare to baseline.
6. Ship it. Add logging.
7. Turn on online scoring at a low sampling rate.
8. Build a view for low scores and thumbs-down feedback.
9. Promote interesting production spans into your dataset.
10. Repeat.

Do not wait until you have a perfect dataset. Get to step 4 fast; everything after that is iteration.