### Four core reasons foundation models are harder to evaluate than traditional ML
- [Find the Business Domain and Application Objective]
    - Model Scope can expand, which increases or shifts the focus of Evalution 
- [Find how the Request to Response Journey happens as Lower Level as possible]
    - Models are Black Boxes (Private Repos or Developer have no idea), So only White Box Evaluation is possible which makes to diffcult to expose the flaws at minute level 
    - More and Complex Reasoning can lead to More Possible Responses; Judging which one is correct and wrong becomes difficult 
    - Advanced Models are more difficult to Test due to More Data and Complex Reasoning 
- [Do not settle with a Evaluation Metric and Benchmark Standards, Keep iterating with User, SME, AI and Code Test Feedback]
    - Public Benchmarks (Not Custom Ones) become obselete quickly as Models are imporving rapidly and Customer demands are changing rapidly 

### Understanding Language Modeling Metrics
- Entropy : 
    - More Entropy = More Information = More Tokens = More Bits = = More Generative = Lesser Predictibilty = Tougher to Evaluate => Difficult to be Replace by Deterministic Code
    - Less Entropy = Less Information = Less Tokens = Less Bits = = Less Generative = Higher Predictibilty = Easier to Evaluate => Easier to be Replaced by Deterministic Code
    - AI Systems which are tougher to Evaluate add More Value by More Being Generative
- Cross Entropy:
    - Entropy of Model seen in reference to DataSet
    - Model Entropy vs DataSet Entropy
    - Called KL Divergence : Kullback–Leibler (KL) divergence measures how much one original probability distribution differs from a reference probability distribution
    - Perplexity = Expentential Cross Entropy
    - Three general rules for what affects expected perplexity:
        - More structured data (Gives Better Reasoning) → lower perplexity
        - Longer context (Gives More Data as Background for Reasoning to happens) → lower perplexity

### Exact/Non Exact Evaluation
- Functional Correctness: Any business task with a genuinely measurable (Exact or Non Exact) objective, can be evaluated on what it's actually supposed to do. eg: Code generation
- Human:
  - Exact: Yes or No (N-nary Reference/Preference) / (Closed-ended question)
    - Lexical : Levenstein Distance / N-Gram Similarity
    - Semantics : Cosine Similarity 
  - Non Exact: Not Yes or No (Open-ended question Reference/Preference)
    - Lexical : Levenstein Distance / N-Gram Similarity
    - Semantics : Cosine Similarity 
- Machine:
  - Exact: Yes or No (N-nary Reference/Preference) / (Closed-ended question) [Deterministic System]
    - Lexical : Levenstein Distance / N-Gram Similarity
    - Semantics : Cosine Similarity 
  - Non Exact: Not Yes or No (Open-ended question Reference/Preference) [Non-Determinitic System]
    - Lexical : Levenstein Distance / N-Gram Similarity
    - Semantics : Cosine Similarity 
- Preference: A/B Testing; Reference: Desired Response Testing
- Non Functional Correctness: Performance, Cost etc. measurement

### AI as a Judge (Machine:Non Exact) and Evaluate AI Systems 
- Score based below criteria based on Reasoning + Human Factor against a Reference (Normal) or Preference (AB):
    - correctness/relevance (precision)
    - wholesomeness (recall)
    - hallucination/factual (groundedness)
    - synchopancy (sycophancy rate)
    - toxicity/safety (tonality, prompt injection)
- System Prompt for AI- Judge:
  - Role (QA Tester)
  - Objctive (Evalute the XYZ Agent)
  - Criteria (As Mentioned above)
  - Score Rubric (Class <- Discret <- Continous) 
  - Output Format (Case + Score + Reason)
  - Examples (Few Shots)
- Stronger vs Same vs Weaker AI Judge — Use Cases
  - Stronger Judge → High-stakes / complex evaluation
    - Medical, legal, financial, safety-critical outputs
    - Complex reasoning or nuanced quality assessment
    - When accuracy of evaluation matters more than cost
    - Example: GPT-5.6 judges a cheaper model's financial analysis
  - Same Model → Self-evaluation / iterative improvement
    - Self-critique and revision
    - Detecting obvious mistakes before returning an answer
    - Improving response quality through reflection
    - Example: Model generates → critiques its answer → revises
  - Weaker / Small Specialized Judge → High-volume, narrow evaluation
    - Simple, repetitive checks at large scale
    - Domain-specific evaluation where a small model can be trained specifically for the task
    - Cost/latency-sensitive production monitoring
    - Example: Small classifier checks whether generated customer-support answers follow company policy

### Design Your Evaluation Pipeline
- Evaluate All Components in a System
  - per task, per turn, per intermediate output; not just on the final output. (a turn can span multiple steps/messages; a task can span multiple turns)
  - Turn-based evaluates the quality of each individual output; task-based evaluates whether the overall goal got accomplished
  - task-based evaluation matters more, since it's what users actually care about
- Create an Evaluation Guideline
  - Define evaluation criteria: Criteria as above (A Good Response should have Answer, Reasons and Next Steps) 
  - Create scoring rubrics with examples
  - pick a scoring system (binary, 1–5, 0–1, or ternary like –1/0/1 for contradiction/neutral/entailment) per criterion, then build a rubric with concrete examples of what each score looks like and why
  - Have Threshold for each metric score
  - Connect AI quality to real business value
    - example: mapping factual-consistency percentages to how much support volume can be automated
    - ***The problem is that if the company rewards more engagement, the AI/product may learn to produce content that keeps people hooked—even if that content is unhealthy, extreme, or addictive. Make sure business incentives don't harm users.***
- Define Evaluation Methods and Data
  - Build annotated evaluation data. The annotation should follow the same rubric defined earlier.
  - Don't rely only on one overall score. Break your data into meaningful groups.
  - Your dataset should be large enough for reliable results but small enough to run affordably. Detecting smaller improvements requires much more data.
  - Evaluate the evaluation pipeline itself
    - Do genuinely better responses get higher scores?
    - Does the same input produce the same evaluation result repeatedly?
    - Are the metrics useful? Perfectly correlated metrics → probably redundant; Zero correlation → either useful complementary information or an unreliable metric
    - Measure the latency and cost added by the evaluation pipeline.
  - Iterate, but track everything
    - Evaluation criteria and rubrics will change as the product and user behavior change. But changing them too frequently makes it difficult to tell whether the model is actually improving.
    - log every variable that affects evaluation: Evaluation dataset, Rubric, Judge prompt, Sampling configuration



### Machine Matrix (From Automata Theory):

|        | Deterministic | Non-Deterministic |
|--------|---------------|-------------------|
| Finite | Easy Decison Tree with Closed-Ended Output (Simple Rule Based Compute) | Easy Decison Tree with Open-Ended Output (Simple AI) |
| Infinite | Tough Decison Tree with Closed-Ended Output (Complex Rule Based Compute) | Tough Decison Tree with Open-Ended Output (Complex AI) |

***Note*** : Limitations of AI:
- Inconsistency — The same AI judge can give different scores for the same answer in different runs.
- Criteria ambiguity — Different tools can measure the same thing differently, so their scores cannot be directly compared.
- Judge drift — If the judge model or prompt changes, score changes may not mean the application actually improved.
- Cost & latency — Using an AI to generate and judge responses increases both API cost and response time.
- Self-bias — AI judges may prefer answers generated by themselves.
- First-position bias — AI judges may prefer the answer shown first in a comparison.
- Verbosity bias — AI judges may prefer longer answers even when shorter answers are more correct.
- Privacy/IP exposure — Using an external AI judge means sending your application data to that model provider.

***Note***: Eval DataSet can be used for Post Training (Fine Tuning and RAG) DataSet and vice versa

***Note***: Since different models tokenize differently (words vs. characters), raw bits-per-token isn't comparable across models. BPC (bits-per-character) normalizes for this: e.g., 6 bits/token ÷ 2 characters/token = BPC of 3. But character-encoding schemes vary too (ASCII = 7 bits/char, UTF-8 = 8–32 bits/char), so BPB (bits-per-byte) standardizes further: BPC of 3 ÷ (7/8 byte) = BPB of 3.43. Cross entropy in this form tells you compression efficiency — a BPB of 3.43 means the model compresses original 8-bit bytes down to 3.43 bits, less than half the original size.