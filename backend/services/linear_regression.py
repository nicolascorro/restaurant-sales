# File: backend/services/linear_regression.py
"""
Linear regression model implementation for sales prediction.
"""
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np
import joblib
from pathlib import Path


class LinearRegressionModel:
    """Implements linear regression for sales forecasting."""
    
    def __init__(self):
        """Initialize the linear regression model."""
        self.model = LinearRegression()
        self.results = {}
        self.feature_names = None
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Trains the linear regression model.
        
        Args:
            X_train: Training features as a pandas DataFrame
            y_train: Target variable as a pandas Series
        """
        # Store feature names for later use
        self.feature_names = X_train.columns.tolist()
        
        # Handle missing values if any
        X_train = X_train.fillna(0)
        y_train = y_train.fillna(y_train.mean())
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Store training results
        self.results['coefficients'] = dict(zip(X_train.columns, self.model.coef_))
        self.results['intercept'] = self.model.intercept_
        self.results['training_complete'] = True
        
        # Log the most important features based on coefficient magnitude
        coef_importance = pd.Series(self.model.coef_, index=X_train.columns).abs().sort_values(ascending=False)
        self.results['feature_importance'] = coef_importance.to_dict()
        
        return self.model
    
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Makes predictions using the trained model.
        
        Args:
            X_test: Test features as a pandas DataFrame
        
        Returns:
            numpy.ndarray: Predicted values
        
        Raises:
            ValueError: If model hasn't been trained yet
        """
        if not self.results.get('training_complete', False):
            raise ValueError("Model must be trained before making predictions.")
        
        # Ensure X_test has the same features as training data
        missing_cols = set(self.feature_names) - set(X_test.columns)
        for col in missing_cols:
            X_test[col] = 0  # Add missing columns with default value
        
        # Select only the features the model was trained on
        X_test = X_test[self.feature_names]
        
        # Handle missing values
        X_test = X_test.fillna(0)
        
        # Make predictions
        predictions = self.model.predict(X_test)
        
        # Ensure predictions are non-negative (sales can't be negative)
        predictions = np.maximum(0, predictions)
        
        return predictions
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """
        Evaluates model performance.
        
        Args:
            X_test: Test features as a pandas DataFrame
            y_test: True target values as a pandas Series
        
        Returns:
            dict: Performance metrics
        """
        # Make predictions
        predictions = self.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # Store and return the results
        evaluation = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'model_type': 'linear_regression'
        }
        
        # Update the results dictionary
        self.results.update(evaluation)
        
        return evaluation
    
    def save_model(self, file_path: str) -> str:
        """
        Saves the trained model to disk.
        
        Args:
            file_path: Path where to save the model
        
        Returns:
            str: Path where the model was saved
        
        Raises:
            ValueError: If model hasn't been trained yet
        """
        if not self.results.get('training_complete', False):
            raise ValueError("Model must be trained before saving.")
        
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save the model and results
        model_data = {
            'model': self.model,
            'results': self.results,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, file_path)
        
        return file_path
    
    def load_model(self, file_path: str):
        """
        Loads a trained model from disk.
        
        Args:
            file_path: Path to the saved model
        
        Raises:
            FileNotFoundError: If the model file doesn't exist
        """
        try:
            model_data = joblib.load(file_path)
            
            self.model = model_data['model']
            self.results = model_data['results']
            self.feature_names = model_data['feature_names']
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {file_path}")