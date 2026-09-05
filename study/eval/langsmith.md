Below is a **step-by-step LangSmith evaluation workflow**, strictly based on the transcript, with concise code examples.

## 1. Set up LangSmith

Create a LangSmith API key and configure tracing.

```bash
export LANGCHAIN_API_KEY="your-api-key"
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT="QA-eval"
```

Verify the environment:

```bash
python verify_environment.py
```

LangSmith provides visibility into LLM calls, including inputs, outputs, latency, and token usage. 

---

## 2. Create a simple LLM application

The tutorial uses a Python QA application with `ChatOpenAI`.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")

response = llm.invoke(question)
```

The response can then be traced in the LangSmith dashboard. 

---

## 3. Inspect traces

A trace captures the execution of an LLM/agent workflow.

Typical information:

```text
Input
  ↓
LLM / Agent
  ↓
Tools
  ↓
Output

Metrics:
- latency
- tokens
- cost
```

For an agent, LangSmith can show individual tool calls and their token consumption. 

---

# Building Evaluation Data

## 4. Create an evaluation dataset

A dataset contains test inputs and optionally reference answers.

```python
from langsmith import Client

client = Client()

dataset = client.create_dataset(
    dataset_name="QA-eval-dataset",
    description="Q&A evaluation data set"
)
```



---

## 5. Add examples with ground truth

```python
client.create_example(
    inputs={"question": "What is the capital of France?"},
    outputs={"answer": "Paris"},
    dataset_id=dataset.id
)
```

The transcript also demonstrates importing datasets through CSV or JSONL. 

---

## 6. Build a good "golden" dataset

A strong dataset should contain:

```text
Normal cases
Difficult cases
Edge cases
Adversarial inputs
Ground-truth answers
Metadata/tags
```

Example:

```python
{
    "question": "Can I return this?",
    "answer": "I need more details. What product would you like to return and when was it purchased?",
    "metadata": {"tag": "ambiguous"}
}
```

The transcript emphasizes **edge-case coverage, balanced intents, ground truth, and real-world production scenarios**. 

---

## 7. Add metadata/tags

Tags allow evaluation by category.

```python
metadata = {
    "tag": "edge_case",
    "category": "returns"
}
```

Then evaluate only a particular category, such as:

```text
edge_case
adversarial
factual
```

This avoids relying only on one overall accuracy number. 

---

## 8. Version datasets

Create a new dataset version instead of modifying the existing benchmark.

```python
dataset_v2 = client.create_dataset(
    dataset_name="golden-product-support-v2"
)
```

Why?

```text
v1 → reproduce old experiments
v2 → evaluate new scenarios
```

Dataset versioning allows historical results to be reproduced and improvements tracked. 

---

# Building Evaluators

## 9. Start with Exact Match

Exact Match compares the complete prediction with the reference.

```python
def exact_match(run, example):
    prediction = run.outputs.get("output", "")
    reference = example.outputs.get("answer", "")

    return {
        "score": 1.0
        if prediction.strip().lower() == reference.strip().lower()
        else 0.0
    }
```

**Problem:** even a correct rephrasing can score `0`.

```text
Reference: "30-day return policy"
Output:    "You can return items within 30 days"

Exact Match → 0
```



---

## 10. Use Contains for more flexibility

```python
def contains(run, example):
    prediction = run.outputs.get("output", "")
    reference = example.outputs.get("answer", "")

    return {
        "score": 1.0
        if reference.strip().lower() in prediction.strip().lower()
        else 0.0
    }
```

This passes when the reference answer appears anywhere in the response. 

---

## 11. Build a keyword-coverage evaluator

Extract important words from the reference and measure how many appear in the response.

```python
def keyword_coverage(run, example):
    prediction = run.outputs.get("output", "").lower()
    reference = example.outputs.get("answer", "").lower()

    keywords = reference.split()
    matches = sum(k in prediction for k in keywords)

    return {
        "score": matches / len(keywords)
        if keywords else 0.0
    }
```

This is more flexible than Exact Match but still deterministic. 

---

## 12. Use LLM-as-a-Judge

For subjective responses, another LLM evaluates the answer using a rubric.

```python
rubric = f"""
Question: {question}
Response: {response}
Reference: {reference}

Score from 1-5 based on correctness,
helpfulness, relevance and completeness.
"""
```

Then send the rubric to the judge LLM:

```python
judge_response = judge_llm.invoke(judge_prompt)
```

The transcript emphasizes that LLM-as-a-judge handles semantic equivalence and subjective quality better than exact matching. 

**Risk:** the judge itself can have biases or inconsistencies. 

---

# Running Experiments

## 13. Run an evaluation experiment

Conceptually:

```python
evaluate(
    qa_pipeline,
    data="QA-eval-dataset",
    evaluators=[exact_match]
)
```

An experiment runs the application over the entire dataset and applies the evaluators. 

---

## 14. Run multiple evaluators

```python
evaluate(
    qa_pipeline,
    data="offline-eval-golden",
    evaluators=[
        keyword_coverage,
        llm_judge
    ]
)
```

Now each example gets multiple scores:

```text
Example       Keyword    Helpfulness
------------------------------------
Q1              0.80         1.0
Q2              0.60         0.8
Q3              1.00         1.0
```

Multiple evaluators provide a **multi-dimensional view of quality**. 

---

# Comparing Prompts

## 15. Create Prompt V2

```python
prompt_v2 = """
You're a product support assistant.
Answer product questions concisely using
exact values from the catalog.
Match the reference answer format.
"""
```

Run it as another experiment:

```python
evaluate(
    qa_pipeline_v2,
    data="offline-eval-golden",
    evaluators=[keyword_coverage, llm_judge],
)
```

---

## 16. Compare experiments

In LangSmith:

```text
Dataset
   ↓
Experiment V1 ──┐
                ├── Side-by-side comparison
Experiment V2 ──┘
```

Compare:

```text
Keyword Coverage
Helpfulness
Latency
Tokens
Cost
```

This shows whether the prompt change actually improved quality rather than relying on guesswork. 

---

# Production Readiness

## 17. Define quality thresholds

The tutorial uses:

```python
keyword_threshold = 0.6
helpfulness_threshold = 0.7
```

Then:

```python
status = (
    "PASS"
    if score >= threshold
    else "FAIL"
)
```

Finally:

```text
Keyword Coverage  ≥ 0.60 → PASS
Helpfulness        ≥ 0.70 → PASS

Both pass → GO FOR PRODUCTION
Otherwise → NOT READY
```



---

# 18. Monitor production

Offline evaluation is done **before deployment**:

```text
Golden Dataset
      ↓
Evaluators
      ↓
Experiment
      ↓
Analysis
      ↓
Deploy
```

Online evaluation happens **after deployment** using real user interactions.

```text
Real User Traces
      ↓
Evaluators
      ↓
Quality Monitoring
      ↓
Failures / Regressions
      ↓
Add failures back to Dataset
```

 

---

## Final Workflow

```text
1. Enable LangSmith tracing
          ↓
2. Build application
          ↓
3. Create Golden Dataset
          ↓
4. Add ground truth + metadata
          ↓
5. Build Evaluators
   ├── Exact Match
   ├── Contains
   ├── Keyword Coverage
   └── LLM-as-Judge
          ↓
6. Run Experiment
          ↓
7. Collect metrics
   ├── Quality
   ├── Latency
   ├── Tokens
   └── Cost
          ↓
8. Compare experiments
          ↓
9. Apply quality thresholds
          ↓
10. Go / No-Go decision
          ↓
11. Monitor production
          ↓
12. Feed production failures back into dataset
```

The transcript's core offline evaluation order is explicitly **Dataset → Evaluators → Experiment → Analysis**. 
