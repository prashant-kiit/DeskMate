## Hyperparameter

### Basics
- Data
    - Training Data (60%) + Evaluation Data (20%) + Cross Validation (20%)
    - Scale (Normalize and Regularize)
    - Cross Validation: Using 20% Data from Training Data to Evaluate in next Epoch
- Reinforcement Learning:
    - Data = Feature (X) + Labels (Y)

### The correct ML workflow is
- Split the data into training data and a final test set.
- Cross-validate on the training data to compare hyperparameters.
- Select the best hyperparameters based on average cross-validation performance.
- Train the final model using the selected hyperparameters and all the training data.
- Evaluate once on the test set to estimate how well the model performs on unseen data.
- Find Perplexity during Evaluation
- Next Epoch again Train of Training Data with Same Hyperparameters and then Evaluate

### Example

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. Load data
X, y = load_iris(return_X_y=True)

# 2. Keep 20% aside for final testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Configure 5-fold cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 4. Define hyperparameters to try
param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [3, 5, None]
}

# 5. Tune hyperparameters using training data only
search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=cv,
    scoring="accuracy",
    n_jobs=-1
)

search.fit(X_train, y_train)

# 6. Check cross-validation results
print("Best parameters:", search.best_params_)
print("CV accuracy:", search.best_score_)

# 7. Evaluate the best model on unseen test data
y_pred = search.predict(X_test)

print("Test accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

