**Feedback poisoning** = when bad, malicious, biased, or low-quality user feedback gets treated as ground truth and is used to improve an LLM/agent.

### How to prevent it

1. **Never trust raw feedback**

   * Treat user feedback as *untrusted data*, not labels.
   * Don't directly fine-tune from thumbs-up/down or user edits.

2. **Validate feedback**

   * Check consistency, correctness, duplicates, and anomalies.
   * Use automated quality checks + human review for high-impact data.

3. **Use trusted evaluators**

   * Combine user feedback with:

     * Expert/human labels
     * Rule-based checks
     * LLM-as-judge
     * Ground-truth datasets

4. **Weight feedback by trust**

   ```text
   Final Score =
       0.5 × Expert
     + 0.2 × Automated Eval
     + 0.2 × Trusted User
     + 0.1 × Unknown User
   ```

5. **Detect coordinated attacks**

   * Monitor sudden spikes in similar feedback.
   * Detect repeated users/accounts/IP/device patterns.
   * Look for unusually high agreement or adversarial feedback.

6. **Keep a clean evaluation set**

   * Maintain a **frozen, trusted benchmark** that feedback cannot modify.
   * Evaluate every new model against it before deployment.

7. **Quarantine new feedback**

   ```text
   User Feedback
        ↓
   Validation
        ↓
   Anomaly Detection
        ↓
   Quarantine
        ↓
   Human/Automated Review
        ↓
   Approved Dataset
        ↓
   Fine-tuning
   ```

8. **Version your training data/models**

   * Dataset version → Model version → Evaluation results.
   * Makes poisoned-data rollback possible.

9. **Limit feedback influence**

   * Don't let one user or small group contribute disproportionately.
   * Apply per-user and per-source contribution caps.

10. **Continuous monitoring**
    Track:

* Feedback distribution
* Label disagreement
* Model performance drift
* Data-source contribution
* Sudden behavioral changes

### For an AI Agent

The key rule is:

> **Feedback → Evidence, not Truth.**

Don't let an agent automatically turn user feedback into **memory, RAG documents, policies, or fine-tuning data** without validation.

**Best architecture:**

```text
User
 ↓
Feedback
 ↓
Untrusted / Quarantine Store
 ↓
Validation + Abuse Detection
 ↓
Trusted Feedback Dataset
 ↓
Human Approval (for critical changes)
 ↓
Training / RAG / Agent Memory
 ↓
Offline Evaluation
 ↓
Production
```

This is essentially **data poisoning defense + feedback governance**.
