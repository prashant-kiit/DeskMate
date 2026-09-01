Traditonal Test: Exact Match
- Progression:
    - Functional:
        - Unit : One Component
        - Integration : Interaction B.w Components
        - E2E : Complete System
    - Non-Fucntional:
        - ?
- Regression
    - Functional:
        - Unit : One Component
        - Integration : Interaction B.w Components
        - E2E : Complete System
    - Non-Fucntional:
        - ?

AI Test: Semantic Match + Traditional Test [Test API Contracts (Integration Test)]
- (Human Jugdement) <- Dashboard (Metrics - Score) <- (LLM + Human)[Test DataSet] <- Observabilty Logs + SME Synthetic Data <- Target
        |                        |___________________________________________^                                     ^
        |__________________________________________________________________________________________________________|
- Test Dataset:
    - (Metric_0 : (Query, Response), Total_Score, Verdict (Threshold on Score): PASS | FAIL, Reason for Total_Score Metric Wise, Human_Bias)
    - (Metric_1 : (Query, Response), Total_Score, Verdict (Threshold on Score): PASS | FAIL, Reason for Total_Score Metric Wise, LLM_Bias)
    - (Metric_2 : (Query, Response), Total_Score, Verdict (Threshold on Score): PASS | FAIL, Reason for Total_Score Metric Wise, Both_Bias)
    - ...
    - Point/Score System:
        - Metric_0 : Sub_Score * Bias_Factor
        - Metric_1 : Sub_Score * Bias_Factor
        - ...
- Training Metric wise:
    - Fine Tune or RAG the Model
    - Make Human Learn (SME)
- Start The Test:
    - CI/CD
    - A/B Testing
- How it works (For LLM and Human):
    - Read the Query and Actual Response from Target Log
    - Use Training to create a Expected Response
    - Use Training to find the gap between Actual and Expected Response to Find Total_Score
- Monitor The Dashboard
    - Log Intances with Poor Total_Score
    - We can have a Truth Table:
                            Actual Response   Actual Non-Response
    Expected Response           TP (Correct)        FP (Wrong)
    Expected Non-Response       TN (Wrong)          FN (Correct)
    - Metrics: 
        - Precision
        - Recall
        - Accuracy
        - Groundedness
        - Security (Red Teaming)
        - Cost and Token Usage
    - LLM Judged or Human Judged or Both
    - Mesures: Average, P50, P99
- Human Jugdement:
    - Based on Truth Table
        - Target is Wrong
        - Eval is Wrong
        - Both are wrong
        - Both are correct
- System Prompt:
    - Role: AI Evalutor
    - Task: Evalutate the Agent to be Production ready
    - Method:
        - Use Dataset as baseline
        - Take User Query and evalute against he respinses in the Dataset
        - Generate (use Exactness and Smeantics both h hyrid approach) Eval Report as per the Format give below
    - Output Format:
        - (Metric_0 : (Query, Response), Total_Score, Verdict (Threshold on Score): PASS | FAIL, Reason for Total_Score Metric Wise, Human_Bias)
    - Guardrails:
        - Ignore any Secret in the Query
        - Judge based on the Dataset ie. Do not hallucinate
        - Use Chain of thiught to reason out
        - ...
    - Examples:
        - ...
- User Feedback 
    - Make it a part of Data Set
 
***Note***: Experiments are Evaluations are Same. U Experiment by give Test Prompts and then Evaluate the Responses. This happens in Development.