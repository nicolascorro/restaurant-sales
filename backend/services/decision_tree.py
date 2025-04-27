# File: backend/services/decision_tree.py
"""
Decision tree model implementation for sales prediction.
"""
from sklearn.tree import DecisionTreeRegressor, export_graphviz
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np
import joblib
import io
from pathlib import Path
import matplotlib.pyplot as plt


class DecisionTreeModel:
    """Implements decision tree for sales forecasting."""
    
    def __init__(self, max_depth=10, min_samples_split=2, min_samples_leaf=1):
        """
        Initialize the decision tree model with hyperparameters.
        
        Args:
            max_depth: Maximum depth of the tree
            min_samples_split: Minimum samples required to split a node
            min_samples_leaf: Minimum samples required at a leaf node
        """
        self.model = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42  # For reproducibility
        )
        self.results = {}
        self.feature_names = None
        self.hyperparams = {
            'max_depth': max_depth,
            'min_samples_split': min_samples_split,
            'min_samples_leaf': min_samples_leaf
        }
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Trains the decision tree model.
        
        Args:
            X_train: Training features as a pandas DataFrame
            y_train: Target variable as a pandas Series
            
        Returns:
            The trained model
        """
        # Store feature names for later use
        self.feature_names = X_train.columns.tolist()
        
        # Handle missing values if any
        X_train = X_train.fillna(0)
        y_train = y_train.fillna(y_train.mean())
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Store training results and tree information
        self.results['training_complete'] = True
        self.results['tree_depth'] = self.model.get_depth()
        self.results['n_leaves'] = self.model.get_n_leaves()
        
        # Get feature importance
        feature_importance = pd.Series(
            self.model.feature_importances_, 
            index=X_train.columns
        ).sort_values(ascending=False)
        
        self.results['feature_importance'] = feature_importance.to_dict()
        
        return self.model
    
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
            'model_type': 'decision_tree'
        }
        
        # Update the results dictionary
        self.results.update(evaluation)
        
        return evaluation
    
    def visualize_tree(self, output_file: str = None, feature_names=None, class_names=None):
        """
        Exports the decision tree visualization to a DOT file or returns DOT data.
        
        Args:
            output_file: If provided, the visualization will be saved to this file
            feature_names: Feature names to use in visualization
            class_names: Class names to use in visualization
            
        Returns:
            str or None: DOT data if output_file is None, otherwise None
        """
        if not self.results.get('training_complete', False):
            raise ValueError("Model must be trained before visualization.")
        
        # Use stored feature names if not provided
        if feature_names is None and self.feature_names is not None:
            feature_names = self.feature_names
        
        # Create DOT data
        dot_data = io.StringIO()
        export_graphviz(
            self.model,
            out_file=dot_data,
            feature_names=feature_names,
            class_names=class_names,
            filled=True,
            rounded=True,
            special_characters=True
        )
        
        if output_file:
            # Save to file
            with open(output_file, 'w') as f:
                f.write(dot_data.getvalue())
            return None
        else:
            # Return DOT data
            return dot_data.getvalue()
    
    def plot_feature_importance(self, output_file: str = None, top_n: int = 10):
        """
        Plot feature importance and optionally save to file.
        
        Args:
            output_file: If provided, the plot will be saved to this file
            top_n: Number of top features to display
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        if 'feature_importance' not in self.results:
            raise ValueError("Model must be trained and feature importance must be calculated.")
        
        # Get feature importance
        importances = pd.Series(self.results['feature_importance'])
        
        # Sort and get top N features
        importances = importances.sort_values(ascending=False).head(top_n)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        importances.plot.bar(ax=ax)
        ax.set_title('Feature Importance')
        ax.set_ylabel('Importance')
        ax.set_xlabel('Feature')
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        
        return fig
    
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
            
            self.model = model_data['model']
            self.results = model_data['results']
            self.feature_names = model_data['feature_names']
            self.hyperparams = model_data.get('hyperparams', {})
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {file_path}")