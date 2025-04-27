# File: backend/services/svm.py
"""
Support Vector Machine implementation for sales prediction.
"""
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np
import joblib
from pathlib import Path


class SVMModel:
    """Implements SVM for sales forecasting."""
    
    def __init__(self, C=1.0, epsilon=0.1, kernel='rbf', gamma='scale'):
        """
        Initialize the SVM model with hyperparameters.
        
        Args:
            C: Regularization parameter
            epsilon: Epsilon in the epsilon-SVR model
            kernel: Kernel type to be used ('linear', 'poly', 'rbf', 'sigmoid')
            gamma: Kernel coefficient ('scale', 'auto' or float)
        """
        # Create a pipeline with scaling (important for SVM) and the SVR model
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('svr', SVR(C=C, epsilon=epsilon, kernel=kernel, gamma=gamma))
        ])
        
        self.model = self.pipeline  # For consistency with other model classes
        self.results = {}
        self.feature_names = None
        self.hyperparams = {
            'C': C,
            'epsilon': epsilon,
            'kernel': kernel,
            'gamma': gamma
        }
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Trains the SVM model.
        
        Args:
            X_train: Training features as a pandas DataFrame
            y_train: Target variable as a pandas Series
            
        Returns:
            The trained pipeline
        """
        # Store feature names for later use
        self.feature_names = X_train.columns.tolist()
        
        # Handle missing values if any
        X_train = X_train.fillna(0)
        y_train = y_train.fillna(y_train.mean())
        
        # Train the model
        self.pipeline.fit(X_train, y_train)
        
        # Store training results
        self.results['training_complete'] = True
        self.results['support_vectors_count'] = self.pipeline.named_steps['svr'].n_support_.sum()
        
        # Store hyperparameters for reference
        self.results['hyperparameters'] = self.hyperparams
        
        return self.pipeline
    
    def predict(self, X_test: pd.DataFrame) -> np.ndarray:
        """
        Makes predictions using trained model.
        
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
        
        # Make predictions using the pipeline (which includes scaling)
        predictions = self.pipeline.predict(X_test)
        
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
            'model_type': 'svm'
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
        
        # Save the pipeline and results
        model_data = {
            'pipeline': self.pipeline,
            'results': self.results,
            'feature_names': self.feature_names,
            'hyperparams': self.hyperparams
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
            
            self.pipeline = model_data['pipeline']
            self.model = self.pipeline  # For consistency
            self.results = model_data['results']
            self.feature_names = model_data['feature_names']
            self.hyperparams = model_data.get('hyperparams', {})
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {file_path}")
    
    def get_params(self):
        """
        Returns the hyperparameters of the SVM model.
        
        Returns:
            dict: Model hyperparameters
        """
        if hasattr(self.pipeline, 'named_steps') and 'svr' in self.pipeline.named_steps:
            svr_params = self.pipeline.named_steps['svr'].get_params()
            return {
                'C': svr_params['C'],
                'epsilon': svr_params['epsilon'],
                'kernel': svr_params['kernel'],
                'gamma': svr_params['gamma']
            }
        return self.hyperparams