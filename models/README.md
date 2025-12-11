# Models Directory

Place your trained machine learning models here.

## Expected Files

- `xgboost_model.pkl` - Trained XGBoost model

## How to Train Models

1. Use the `train_models.py` script in the parent directory to train models
2. Save the trained XGBoost model using pickle:

```python
import pickle

# After training
with open('project/models/xgboost_model.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)
```

## Mock Model

If no trained model is found, the system will use a mock model that generates random predictions for demonstration purposes.

**⚠️ Replace the mock model with a real trained model before production use!**

