"""
SalesForecaster: использование модели для прогнозирования
"""
import numpy as np
import pickle
import os
from typing import Union


class MockXGBoostModel:
    """
    Mock XGBoost model for demonstration
    Replace this with real trained model later
    """
    
    def __init__(self):
        """Initialize mock model with random parameters"""
        self.feature_importances_ = None
        self.n_features = None
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Mock prediction: returns random sales values
        
        Args:
            X: Feature matrix (n_samples, n_features)
            
        Returns:
            Predicted sales values
        """
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Mock prediction: base value + some variation based on features
        # This is just a placeholder!
        base_sales = 6000.0
        variation = np.sum(X, axis=1) * 100  # Simple linear combination
        predictions = base_sales + variation
        
        # Ensure positive values
        predictions = np.maximum(predictions, 1000.0)
        
        return predictions
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Mock fit method (does nothing)"""
        self.n_features = X.shape[1]
        return self


class SalesForecaster:
    """
    Sales forecasting model wrapper
    Provides unified interface for XGBoost model
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize SalesForecaster
        
        Args:
            model_path: Path to trained model file (.pkl)
                       If None or file doesn't exist, uses mock model
        """
        self.model = None
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Load model from file or create mock model"""
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✅ Loaded trained model from {self.model_path}")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                print("Using mock model instead")
                self.model = MockXGBoostModel()
        else:
            print("⚠️ No trained model found. Using mock model.")
            print(f"   Place your trained XGBoost model at: {self.model_path}")
            self.model = MockXGBoostModel()
    
    def _load_model_from_file(self, model_path: str):
        """
        Load model from pickle file
        
        Args:
            model_path: Path to model file
            
        Returns:
            Loaded model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        return model
    
    def predict(self, X: Union[np.ndarray, list]) -> np.ndarray:
        """
        Predict sales for given features
        
        Args:
            X: Feature matrix or single feature vector
            
        Returns:
            Predicted sales values
        """
        # Convert to numpy array if needed
        if isinstance(X, list):
            X = np.array(X)
        
        # Ensure 2D array
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        # Predict
        predictions = self.model.predict(X)
        
        return predictions
    
    def predict_single(self, x: np.ndarray) -> float:
        """
        Predict sales for a single observation
        
        Args:
            x: Single feature vector
            
        Returns:
            Predicted sales value
        """
        prediction = self.predict(x.reshape(1, -1))
        return float(prediction[0])
    
    def is_mock_model(self) -> bool:
        """
        Check if currently using mock model
        
        Returns:
            True if mock model, False if real model
        """
        return isinstance(self.model, MockXGBoostModel)

