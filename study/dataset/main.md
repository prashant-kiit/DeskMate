## Dataset Engineering

### Overview
- Model
- Post Training : Fine Tuning or RAG
- Data + Infrastucture
- Data: Data Set Engineering
- Infrastructure: Data Pipeline Engineering

***Note***: Model Centric AI vs Data Centric AI

### Data: Data Set Engineering
- Benefits:
    - Prevent Hallucination 
    - Make Model more Reasonable
    - Learn Good Behaviour
    - Unlearn Bad Behaviour
- Data Curation
- ?

### Data Curation
- Prepare of Data Set for Post Training is called Data Curation
- Curation depends on the Objective of the Agent
- Replicate the Objective of Agent in the Date Set
- Use it to Fine Tune the Model and RAG the Model in the Agent
- Data Set Format : ((Query, Response), Score, PASS | FAIL, Reason)
- Data Set Should have these criteria: 
    - data quality (How Good is the Each Data Category)
    - data coverage (All Categories of Data)
    - data quantity (Amount of each Data Category)
- Data Set should Reflect ReAct Design Pattern: 
    - Chain of Thought (Re)
    - Agent/Loop Call (Act)

***Note***: Data Set Curated can be divided into two parts: 1. For Post Training (Fine Tuning, RAG) 2. Evals 

### Data Quality
- Relevant to the Business Domain
- Data Set Format Aligned to Requirement
- Annotate the Data in Consistent Way by a Standard Rule
- Correct Input and Output Schema
- Data should be Law Compliant

### Data Coverage
- Based on the Business Domain Decide the dimensions/attributes of data diversity
- Find the Right Mix using experiments/evals

### Data Quantity
- Finetuning techniques
    - Full Fine-Tuning: More Quantity
    - LoRA Fine Tuning: Less Quantity
- Task complexity
    - Simple : Less Data
    - Complex : More Data
- Base Model's Performance:
    - More Domain Specific: Less Data
    - Less Domain Specific: More Data

***Note***: A phenomenon called ossification, where pretraining can ossify (i.e., freeze) the model weights so that they don’t adapt as well to the finetuning data (Hernandez et al., 2021). Smaller models are more susceptible to ossification than larger models. This happens due to over training on the same kind od data.

***Note***: In short, if you have a small amount of data, you might want to use PEFT methods on more advanced models. If you have a large amount of data, use full finetuning with smaller models.

### Hyperparameters

### Approaches for Data Set Preparation:
- Self-supervised → supervised
You want to finetune a model to answer legal questions. Your(question, answer) set is small, but you have many legal documents. You can first finetune your model on legal documents in a self-supervised manner, then further finetune the model on (question, answer) pairs.
- Less-relevant data → relevant data
You want to finetune a model to classify sentiments for product reviews, but you have little product sentiment data and
much more tweet sentiment data. You can first finetune your model to classify tweet sentiments, then further finetune it to
classify product sentiments.
- Synthetic data → real data
You want to finetune a model to predict medical conditions from medical reports. Due to the sensitive nature of this task,
your data is limited. You can use AI models to synthesize a large amount of data to finetune your model first, then further
finetune it on your real data. This approach is harder to get right, as you’ll have to do two distinct finetuning jobs while
coordinating the transitioning between them. If you don’t know what you’re doing, you might end up using more compute just to produce a model worse than what you would’ve gotten by just finetuning with high-quality data.6

### Data acquisition
- Data acquisition involves gathering data
- Data Sources:
    - most important source of data, however, is typically data from your own application (User Logs and Feedbacks) (Data Flywheel)
    - Open Source
    - Proprietary Data
- Steps:
    1. Find available datasets with the desirable characteristics. You might find one
    promising dataset with 10,000 examples.
    2. Remove low-quality instructions. Let’s say this leaves you with 9,000 examples.
    3. Set aside the instructions with low-quality responses. Let’s say you find 3,000
    such examples. This leaves you with 6,000 examples of high-quality instructions
    and high-quality responses.
    4. Manually write responses for the 3,000 high-quality instructions. Now your data‐
    set has a total of 9,000 high-quality examples.
    5. Realizing that there’s not enough data for topic X, manually create a set of 100
    instruction templates about X. Use an AI model to synthesize 2,000 instructions
    using these 10 templates.
    6. Manually annotate these 2,000 synthetic instructions. Now your dataset has a
    total of 11,000 examples.



