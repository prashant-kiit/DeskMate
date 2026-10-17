### Resource:
- https://www.youtube.com/watch?v=i_LwzRVP7bg


### Topics:
- Features and Label
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

        
Actual\Predicted  Postive Negative
Sick              A (TP)  B (FN)
Healthy           C (FP)  D (TN)

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

Bayes Theorem:
- P(H|E) / P(E|H) = P(H) / P(E)
- Information flow is birectional: E -> H and H -> E
- Stronger of H or E will win
- P(H|E) = P(E|H).P(H)/(P(H).P(E|H)+P(H').P(E|H'))
- Reference: https://www.youtube.com/watch?v=HZGCoVF3YvM

Note:
- Intelligence
    - Data [x, y]
    - Algorithm [ f ]
    - f(x) = y, x belongs in Rx and for each x, y belongs in Ry
    - Broader the Rx and Narrower the Ry; Intelligence = Rx/Ry
    - Ability to take decision on Everything with Exactness is Intelligence
    - P (Y | X) should be close 1 for more intelligence
    - X is Pre and Y is Post