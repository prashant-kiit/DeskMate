## Hyperparameter

### Basics
- Data
    - Training Data (60%) + Evaluation Data (20%) + Cross Validation (20%)
    - Scale (Normalize and Regularize)
    - Cross Validation: Using 20% Data from Training Data to Evaluate in next Epoch
- Reinforcement Learning:
    - Data = Feature (X) + Labels (Y)

### The correct ML workflow is:
- Split the data into training data and a final test set.
- Cross-validate on the training data to compare hyperparameters.
- Select the best hyperparameters based on average cross-validation performance.
- Train the final model using the selected hyperparameters and all the training data.
- Evaluate once on the test set to estimate how well the model performs on unseen data.
- Find Perplexity during Evaluation

