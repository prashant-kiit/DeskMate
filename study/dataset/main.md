## Dataset Engineering

### Overview
- Model is a Transformer
- Transform is Layers of NN
- NN is Graph + BFS Based Decision Tree
- For Decision Tree to work, Data and Logic is Needed
- Why?
    - Node : Data + Function
    - Compare Function(Input) and Data to Decide
    - Based on the Decision, New Node (using an Edge) be chosen
- So, to Improve the Model, We need to work on Data and Reasoning_Function of NN in Model
- HOWEVER, IT IS BETTER TO USE MODEL FOR REASONING (FINE TUNE FOR REASONING) AND RAG FOR DATA

***Note***: Model Centric AI vs Data Centric AI

### Build Model for Reasoning
- Resource : https://www.youtube.com/watch?v=kCc8FmEb1nY&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ&index=7&t=1282s

### Training Model with Data
- Model Needs Pre Training and Post Training on DataSet
- Post Training Data Ingestion Mehtods : Fine Tuning or RAG
- Data + Infrastucture
- Data: Data Set Engineering
- Infrastructure: Data Pipeline Engineering
    - For Fine Tuning, Fine Tuning Pipeline
    - For RAG, RAG Pipeline

### Data Set Engineering
- Benefits:
    - Prevent Hallucination (Response is grounded to the Data)
    - Make Model more Reasonable (For Reasoning also Data is required, if better then better reasoning)
    - Learn Good Behaviour
    - Unlearn Bad Behaviour

### Data Curation
- Prepare of Data Set for Post or Pre Training is called Data Curation
- Curation depends on the Objective of the Agent
- Replicate the Objective of Agent in the Date Set
- Use it to Fine Tune the Model and RAG the Model in the Agent
- Data Set Format : ((Query, COT (Agent/Call), Response (GroundTruths)), Score, Verdict : PASS | FAIL, Reason For Score and Verdict)
- Data Set Should have these criteria: 
    - data quality (How Good is the Each Data Category)
    - data coverage (All Categories of Data)
    - data quantity (Amount of each Data Category)
- Data Set should Reflect ReAct Design Pattern: 
    - Chain of Thought (Re)
    - Agent/Loop Call (Act)

***Note***: Data Set Curated can be divided into two parts: 1. For Post Training (Fine Tuning, RAG) 2. Evals 

### Data Quality
- Relevant to the Business Domain and Specific Requirement
- Data Set Format Aligned to Requirement 
[As in here, ((Query, COT (Agent/Call), Response (GroundTruths)), Score, Verdict : PASS | FAIL, Reason For Score and Verdict)]
- Annotate (Give GroundTruths, Score) the Data in Consistent Way by a [Standard Rule, Use LLM For Standardization, Run Evals]
- Correct Input and Output Schema
- Data should be Law Compliant

### Data Coverage
- Based on the Business Domain Decide the dimensions/attributes of data diversity
- Good Diversity Prevents Bias towards one kind of Response and Makes Model/Agent handle wider range of use cases
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
- More the High Quality and Diverse the Better for Post Training because the More means strong neural connection or more Pattern Recognition or more generalization (So that Model can answer any kind of Questions)
- However beyond a certain Limit the Model Performance do not show much increase [Use Evals to Find a Limit]
- After that we have to use an Advanced Model

***Note***: A phenomenon called ossification, where pretraining can ossify (i.e., freeze) the model weights so that they don’t adapt as well to the finetuning data (Hernandez et al., 2021). Smaller models are more susceptible to ossification than larger models. This happens due to over training on the same kind of data.

***Note***: In short, if you have a small amount of data, you might want to use PEFT methods (LoRA) on more advanced models. If you have a large amount of data, use full finetuning with smaller models.

### Hyperparameters

### Approaches for Data Set Curation:
- Self-supervised → supervised
You want to finetune a model to answer legal questions. Your (question, answer) set is small, but you have many legal documents. You can first finetune your model on legal documents in a self-supervised manner, then further finetune the model on (question, answer) pairs.
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
    1. Find available datasets with the desirable characteristics. You might find one promising dataset with 10,000 examples.
    2. Remove low-quality instructions. Let’s say this leaves you with 9,000 examples.
    3. Set aside the instructions with low-quality responses. Let’s say you find 3,000 such examples. This leaves you with 6,000 examples of high-quality instructions and high-quality responses.
    4. Manually write responses for the 3,000 high-quality instructions. Now your dataset has a total of 9,000 high-quality examples.
    5. Realizing that there’s not enough data for topic X, manually create a set of 100instruction templates about X. Use an AI model to synthesize 2,000 instructions using these 10 templates.
    6. Manually annotate these 2,000 synthetic instructions. Now your dataset has a total of 11,000 examples.

### Data Generation
- Ways:
    1. Take Real Data Comparable to our Target Data 
    2. Mimic that Real Data to Synthensize (Derive) New Traget Data (Use AI)
    3. Deploy the Model and gather Real Production Data
    4. Augment the Real Production Data by extending (along similar patterns) it (Use AI)

### Data Synthezise
- Use when real-world data is scarce 
- Helps:
    - To increase data quantity
    - To increase data coverage
    - To increase data quality
    - Use when real-world data is scarce due to legal or some other reasons
- EG: Data Synthesis for Eval/FineTuning a PII, PHI Redactor Model
    - Take Real Conversation Transcripts of All Types: Doctor - Doctor, Nurse - Nurse, Doctor - Nurse etc. [Gives Coverage and Quality]
    - Take PHI Data from Open Medical Sources [Give Quality]
    - Asked AI to generate the PII Data based on Varying Factors of Country, Region, Religion, Professions, Experiences etc. [Gives Coverage]
    - Use LLM to generate the Test Data based Augmented by Above Three [Give Quanity]

### Methods of Gata Generation (Synthensis and Augmentation)
- Procedural generation : Software Used
- Manual generation : Human Used
- Non AI (Traditional)
    - Rule-Based: Predefined rules and templates + Randomizer, Data Perbutation (Add Noise to Data Deliberately for Testing Agents)
    - Simulate a Real World Scenario to Create Real Like Data like Developer faking to be a Interviewer to test AI Interviewer App
- AI
    - 

***Note***: Model distillation in LLMs is the process of training a smaller student LLM to mimic a larger teacher LLM by using the teacher’s generated outputs or token probabilities as targets; typically, the student is optimized using KL-divergence/distillation loss, resulting in a faster, cheaper model that retains much of the teacher’s performance.

Pending:
Standard Rule for Data Annotation : Features and Labels (https://www.youtube.com/results?search_query=how+to+label+data+for+ml)