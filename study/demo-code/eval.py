from openai import OpenAI

client = OpenAI()

# 1. EVALUATION DATASET
dataset = [
    {
        "input": "What is RAG?",
        "expected": "Retrieval-Augmented Generation",
        "criteria": "Answer should correctly explain RAG."
    }
]


# 2. SYSTEM UNDER TEST
def ai_app(question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


# 3. LLM-AS-A-JUDGE
def evaluate(example, output):
    prompt = f"""
You are an AI evaluator.

Input: {example['input']}
Expected answer: {example['expected']}
Actual output: {output}

Criteria: {example['criteria']}

Score the output from 1 to 5.
Return ONLY:
SCORE: <number>
REASON: <short reason>
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# 4. RUN EVALUATION
results = []

for example in dataset:

    # Generate
    output = ai_app(example["input"])

    # Evaluate
    evaluation = evaluate(example, output)

    # Store trace
    results.append({
        "input": example["input"],
        "output": output,
        "evaluation": evaluation
    })


# 5. REPORT + REGRESSION CHECK
print(results)

# Production: calculate metrics such as
# correctness, relevance, faithfulness,
# latency, token usage and cost.