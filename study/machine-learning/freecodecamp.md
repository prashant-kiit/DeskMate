### Resource:
- https://www.youtube.com/watch?v=i_LwzRVP7bg


### Topics:
- Features (X) and Label (Y)
- Model Training
- Data Preparation 
    - Training Data
        - Scale
    - Test Data
- KNN
    - Classification
    - Cluster Size for Classification

- Metrics
    - Precision - Relevance
    - Recall - Groundedness
    - Accuracy - Correctness

- Bayes Theorem 
    - P(H|E) / P(E|H) = P(H) / P(E)
    - Information flow is birectional: E -> H and H -> E
    - Stronger of H or E will win
    - P(H|E) = P(E|H).P(H)/(P(H).P(E|H)+P(H').P(E|H'))
    - P(H) -> Prior, P(E) -> Evidence, P(E|H) -> Likelihood, P(H|E) -> Posterior
    - Reference: https://www.youtube.com/watch?v=HZGCoVF3YvM   
    - Proof:

    P(A|B) = P(A ∩ B) / P(B)
    Similarly,
    P(B|A) = P(A ∩ B) / P(A)
    P(A ∩ B) = P(B|A) × P(A)
    P(A|B) = [P(B|A) × P(A)] / P(B)
    - Example:

    | Actual \ Predicted | Positive | Negative |
    |---|---|---|
    | Sick | A (TP) | B (FN) |
    | Healthy | C (FP) | D (TN) |

    P(FP) = C / Total = 0.05
    P(FN) = B / Total = 0.01
    P(Disease) = A + B / Total = 0.1

    P(Disease | Postive Test) = A / A + C = ?

    P(Disease | Postive Test) 
    = A / A + C
    = (A / Total) / ((A + C) / Total)
    = P(TP) / (A / Total + C / Total)
    = P(TP) / (P(TP) + P(FP))
    = 1 / (1 + P(FP)/P(TP))
    = 1 / (1 + P(FP)/(P(Disease) - P(FN)))
    = 1 / (1 + 0.05/(0.1 - 0.01))
    = 0.64285714285

    A + B / Total = A / Total + B / Total
    P(Disease) = P(TP) + P(FN)
    P(TP) = P(Disease) - P(FN)
- Navie Bayes Theorem: 
    - All X (Features) are independent of each other
    - **P(C|X₁, ..., Xₙ) ∝ P(C) × ∏ P(Xᵢ|C)**
- MAP
    - Maximum A Posteriori
    - Argmax P(C) × ∏ P(Xᵢ|C) among all values if i

Clustering:
- Recursively Tile/Mine the Vector Space 
- Classify Vector Points into Classes/Categories/Clsuters using below methods:
    - Distance Formula
    - Cosine Similarity
    - Navie Bayesian Theorem
- Having a Max Threshold to Prevent Overfitting (Too Less Contextuatlization, Too More Generalization) [Vector Regualarization]



Note:
- Intelligence
    - Data [x, y]
    - Algorithm [ f ]
    - f(x) = y, x belongs in Rx and for each x, y belongs in Ry
    - Broader the Rx and Narrower the Ry; Intelligence = Rx/Ry
    - Ability to take decision on Everything with Exactness is Intelligence
    - P (Y | X) should be close 1 for more intelligence
    - X is Pre and Y is Post