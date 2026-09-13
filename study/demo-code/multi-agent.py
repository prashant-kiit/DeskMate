# pip install openai

from openai import OpenAI

client = OpenAI()

# ---------------- AGENTS ----------------

def researcher(task):
    return ask_llm(
        f"""You are a Research Agent.
Research/analyze the task and provide useful facts.

Task: {task}"""
    )


def analyst(task, research):
    return ask_llm(
        f"""You are an Analysis Agent.
Analyze the research and derive the best solution.

Task: {task}
Research: {research}"""
    )


def reviewer(task, analysis):
    return ask_llm(
        f"""You are a Review Agent.
Check correctness, gaps and risks.
Return improvements if required.

Task: {task}
Analysis: {analysis}"""
    )


def ask_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# ---------------- ORCHESTRATOR ----------------

def orchestrator(task):
    # 1. PLAN
    plan = ask_llm(f"""
    Create a plan for this task.
    Decide which agents are needed and in what order.

    Task: {task}
    """)

    # 2. DELEGATE
    research = researcher(task)

    # 3. COLLABORATE
    analysis = analyst(task, research)

    # 4. REVIEW
    review = reviewer(task, analysis)

    # 5. REFLECT / ITERATE
    if "incorrect" in review.lower() or "missing" in review.lower():
        analysis = analyst(
            task,
            f"{research}\nReview feedback: {review}"
        )

    # 6. SYNTHESIZE
    final = ask_llm(f"""
    You are the Lead Agent.

    Produce the final answer using:
    Plan: {plan}
    Research: {research}
    Analysis: {analysis}
    Review: {review}

    Task: {task}
    """)

    return final


# ---------------- RUN ----------------

task = "Design a scalable RAG system for an enterprise."

print(orchestrator(task))