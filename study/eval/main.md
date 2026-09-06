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

### AI as a Judge (Machine:Non Exact)
- Score based below criteria based on Reasoning + Human Factor against a Reference (Normal) or Preference (AB):
    - correctness (precision)
    - wholesomeness (recall)
    - hallucination (groundedness)
    - synchopancy (sycophancy rate)
    - toxicity (tonality, prompt injection)
- System Prompt for AI- Judge:
  - Role (QA Tester)
  - Objctive (Evalute the XYZ Agent)
  - Criteria (As Mentioned above)
  - Score (Class <- Discret <- Continous) 
  - Output Format (Case + Score + Reasonse)
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

***Note*** : Limitations of AI:
- Inconsistency — The same AI judge can give different scores for the same answer in different runs.
- Criteria ambiguity — Different tools can measure the same thing differently, so their scores cannot be directly compared.
- Judge drift — If the judge model or prompt changes, score changes may not mean the application actually improved.
- Cost & latency — Using an AI to generate and judge responses increases both API cost and response time.
- Self-bias — AI judges may prefer answers generated by themselves.
- First-position bias — AI judges may prefer the answer shown first in a comparison.
- Verbosity bias — AI judges may prefer longer answers even when shorter answers are more correct.
- Privacy/IP exposure — Using an external AI judge means sending your application data to that model provider.




***Note***: Since different models tokenize differently (words vs. characters), raw bits-per-token isn't comparable across models. BPC (bits-per-character) normalizes for this: e.g., 6 bits/token ÷ 2 characters/token = BPC of 3. But character-encoding schemes vary too (ASCII = 7 bits/char, UTF-8 = 8–32 bits/char), so BPB (bits-per-byte) standardizes further: BPC of 3 ÷ (7/8 byte) = BPB of 3.43. Cross entropy in this form tells you compression efficiency — a BPB of 3.43 means the model compresses original 8-bit bytes down to 3.43 bits, less than half the original size.

---
## Chapter 3: Evaluation Methodology (pp. 113–159)

- **Challenges of Evaluating Foundation Models**
- **Understanding Language Modeling Metrics**
  - Entropy
  - Cross Entropy
  - Bits-per-Character and Bits-per-Byte
  - Perplexity
  - Perplexity Interpretation and Use Cases
- **Exact Evaluation**
  - Functional Correctness
  - Similarity Measurements Against Reference Data
  - Introduction to Embedding
- **AI as a Judge**
  - Why AI as a Judge?
  - How to Use AI as a Judge
  - Limitations of AI as a Judge
  - What Models Can Act as Judges?
- **Ranking Models with Comparative Evaluation**
  - Challenges of Comparative Evaluation
  - The Future of Comparative Evaluation
- **Summary**

## Chapter 4: Evaluate AI Systems (pp. 159–211)

- **Evaluation Criteria**
  - Domain-Specific Capability
  - Generation Capability
  - Instruction-Following Capability
  - Cost and Latency
- **Model Selection**
  - Model Selection Workflow
  - Model Build Versus Buy
  - Navigate Public Benchmarks
- **Design Your Evaluation Pipeline**
  - Step 1. Evaluate All Components in a System
  - Step 2. Create an Evaluation Guideline
  - Step 3. Define Evaluation Methods and Data
- **Summary**