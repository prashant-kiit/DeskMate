Accuracy - Is answer correct?
Precision - Is answer detailed?
Hallucination - Is the answer relevant to answer context or is imaginery?
Recall Ability - Is answer correct?
Mean Reciprocal Rank - To what extend the correct answer is correct?

----

Precision and recall are key classification metrics. Precision measures how many predicted positive cases are actually correct (avoiding false positives). Recall measures how many of the actual positive cases the model managed to find (avoiding false negatives). They usually have an inverse trade-off.
Understanding the Core Definitions 

• Precision: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$ 

	• Focuses on the quality of the positive predictions. 
	• High precision means fewer false alarms.

• Recall: $\frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$ 

	• Focuses on the quantity of actual positives captured. 
	• High recall means fewer missed real cases.

The Trade-Off 

• As you tune a model to be stricter, it makes fewer false positive errors, raising precision. 
• However, being stricter causes it to miss more actual positive items, lowering recall. 
• Relaxing the threshold catches everything (high recall) but increases false alarms (low precision). 

When to Use Which 

• Prioritize Precision when False Positives are Costly: 

	• Example: Spam filters. You do not want important real emails going to the spam folder.

• Prioritize Recall when False Negatives are Costly: 

	• Example: Medical diagnosis or airport security. Missing a disease or a threat is far more dangerous than a false alarm.

• Balance Both via F1 Score: 

	• Use the F1 Score Guide to compute the harmonic mean when you need a balance of both metrics.

----

Low Temp / Low Top-K  ───► Focuses on High Precision (Accurate, safe, factual)
High Temp / High Top-K ───► Focuses on High Recall (Creative, broad, exhaustive)

----

nDCG (Normalized Discounted Cumulative Gain) measures how well a ranked list puts the most relevant results near the top, giving higher weight to higher-ranked positions.