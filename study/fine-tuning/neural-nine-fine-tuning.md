## Fine Tuning

### Training
- High Intrinsic Rank - Full
- [A] + Delta = [A']
- Delta has High Dimensionality
- [A'] is a Cross Product of Delta and External Nodes
- Visualize Neural Network like a Table and Graph Both

----

### Fine Tuning (LoRA)
- Low Intrinsic Rank - Partial
- [A] + Delta = [A']
- Delta has Low Dimensionality
- [A'] is a Cross Product of Delta and External Nodes
- Visualize Neural Network like a Table and Graph Both

----

### Process
- Google Collab
- CUDA Platfrom
- Parallel CPU + GPU Processing
- Model: Load Model -> Quantize & Compress (In Terms of Bits and Bytes) -> Initiate Model
- Data: Load Data -> Process (Clean, Tokenize etc.) -> Initiate Data
- FF Hyperparameter: Intrinsic Ranking, Weight & Bias, Query & Key & Value as Delta Target, Scaling/Normalization of Training Data, Scaling/Regularization of Training Data, Batch Size, Gradient Acculumation Steps, GPU Core Count, Learning Rate & Warmup (Degree of Delta in Weights & Biases after Each Training Step), Epochs, Estimators Count (No of Parallel Models), NN Depth (Influence of Delta), Checkpoints & Logging 
- Trainer: Model + Data + Hyperparameters
- Record Steps and Loss

----

### Evaluation
- Perplexity: Base Model Loss / Tuned Model Loss

----

### Libaries
1. Model
- Transformer
2. Learning: 
- Skit Learn - Classical AI Learning
- PyTorch - GenAI Learning
- PEFT - Fine Tuning Learning

----

### Flash Attention vs Self Attention (Standard)
- Fast vs Slow
- Input and Output Same vs Input and Output Same
- Less CPU and Memory vs More CPU and Memory
- Tiling vs No Tiling
- Memory Bound vs Compute Bound
- Analog:
    * You pack a small cooler box with a precise batch of ingredients from the fridge, bring it to your counter, cook that entire batch completely on your cutting board, and only walk back to the fridge when that block is fully finished.
    * ***vs***
    * You walk to the fridge, grab one ingredient, walk back to the cutting board, chop it, walk back to the fridge to put it away, and repeat this for all N × N combinations. The constant walking (memory traffic) slows you down completely.
- For I/O Interactive Systems vs For Heavy Processing Systems
