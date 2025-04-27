# File: backend/services/model_comparison.py
"""
Model comparison module using cross-validation.
Determines which model has the highest accuracy.
"""
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from pathlib import Path
import time
from typing import Dict, List, Tuple, Any


class ModelComparator:
    """Compares different model performances."""
    
    def __init__(self, cv_folds=5, test_size=0.2, random_state=42):
        """
        Initialize the model comparator.
        
        Args:
            cv_folds: Number of cross-validation folds
            test_size: Proportion of data to use for testing
            random_state: Random seed for reproducibility
        """
        self.cv_folds = cv_folds
        self.test_size = test_size
        self.random_state = random_state
        self.results = {}
        self.best_model_name = None
        self.best_model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def split_data(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """`
        Split data into training and testing sets.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.test_size, 
            random_state=self.random_state
        )
        
        # Store for later use
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        return X_train, X_test, y_train, y_test
    
    def compare_models(self, X: pd.DataFrame, y: pd.Series, models: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Performs cross-validation on all models and compares accuracy.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            models: Dictionary of model instances with model name as key
            
        Returns:
            dict: Dictionary with model names as keys and performance results as values
        """
        # Split data if not already done
        if self.X_train is None or self.y_train is None:
            self.split_data(X, y)
        
        cv_results = {}
        
        # Define the cross-validation strategy
        kf = KFold(n_splits=self.cv_folds, shuffle=True, random_state=self.random_state)
        
        # Evaluate each model with cross-validation
        for model_name, model_instance in models.items():
            start_time = time.time()
            
            # Perform cross-validation
            cv_scores_rmse = []
            cv_scores_r2 = []
            
            for train_idx, val_idx in kf.split(self.X_train):
                # Split data for this fold
                X_fold_train = self.X_train.iloc[train_idx]
                y_fold_train = self.y_train.iloc[train_idx]
                X_fold_val = self.X_train.iloc[val_idx]
                y_fold_val = self.y_train.iloc[val_idx]
                
                # Train model
                model_instance.train(X_fold_train, y_fold_train)
                
                # Predict and evaluate
                y_pred = model_instance.predict(X_fold_val)
                fold_rmse = np.sqrt(mean_squared_error(y_fold_val, y_pred))
                fold_r2 = r2_score(y_fold_val, y_pred)
                
                cv_scores_rmse.append(fold_rmse)
                cv_scores_r2.append(fold_r2)
            
            # Calculate mean and standard deviation of cross-validation metrics
            mean_rmse = np.mean(cv_scores_rmse)
            std_rmse = np.std(cv_scores_rmse)
            mean_r2 = np.mean(cv_scores_r2)
            std_r2 = np.std(cv_scores_r2)
            
            # Train the model on the full training set
            model_instance.train(self.X_train, self.y_train)
            
            # Evaluate on the test set
            test_evaluation = model_instance.evaluate(self.X_test, self.y_test)
            
            # Record time taken
            training_time = time.time() - start_time
            
            # Store results
            cv_results[model_name] = {
                'cv_mean_rmse': mean_rmse,
                'cv_std_rmse': std_rmse,
                'cv_mean_r2': mean_r2,
                'cv_std_r2': std_r2,
                'test_mse': test_evaluation['mse'],
                'test_rmse': test_evaluation['rmse'],
                'test_mae': test_evaluation['mae'],
                'test_r2': test_evaluation['r2'],
                'training_time': training_time,
                'model_instance': model_instance
            }
            
            print(f"Evaluated {model_name}: CV RMSE = {mean_rmse:.4f} ± {std_rmse:.4f}, Test RMSE = {test_evaluation['rmse']:.4f}")
        
        # Store results
        self.results = cv_results
        
        # Determine the best model
        self._select_best_model()
        
        return cv_results
    
    def _select_best_model(self) -> str:
        """
        Determines the best model based on test RMSE.
        
        Returns:
            str: Name of the best performing model
        """
        if not self.results:
            raise ValueError("No model comparison results available. Run compare_models first.")
        
        # Find model with lowest test RMSE
        best_rmse = float('inf')
        best_model_name = None
        
        for model_name, result in self.results.items():
            if result['test_rmse'] < best_rmse:
                best_rmse = result['test_rmse']
                best_model_name = model_name
        
        self.best_model_name = best_model_name
        self.best_model = self.results[best_model_name]['model_instance']
        
        return best_model_name
    
    def get_best_model(self) -> Tuple[str, Any]:
        """
        Returns the name of the best performing model and the model instance.
        
        Returns:
            tuple: (best_model_name, best_model_instance)
            
        Raises:
            ValueError: If no comparison has been performed yet
        """
        if self.best_model_name is None or self.best_model is None:
            if self.results:
                self._select_best_model()
            else:
                raise ValueError("No model comparison has been performed yet. Run compare_models first.")
        
        return self.best_model_name, self.best_model
    
    def plot_model_comparison(self, metric='test_rmse', output_file=None):
        """
        Creates a bar chart comparing the models.
        
        Args:
            metric: Which metric to plot ('test_rmse', 'test_r2', 'cv_mean_rmse', etc.)
            output_file: If provided, the plot will be saved to this file
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        if not self.results:
            raise ValueError("No model comparison results available. Run compare_models first.")
        
        # Extract the metric values for each model
        models = list(self.results.keys())
        values = [self.results[model][metric] for model in models]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(models, values, color=['#3498db', '#2ecc71', '#e74c3c'])
        
        # Add labels and title
        ax.set_xlabel('Models')
        ax.set_ylabel(metric.replace('_', ' ').title())
        ax.set_title(f'Model Comparison by {metric.replace("_", " ").title()}')
        
        # Add data labels above bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height + 0.02 * max(values),
                f'{height:.4f}',
                ha='center', 
                va='bottom'
            )
        
        # Highlight the best model (lowest RMSE or highest R2)
        best_index = np.argmin(values) if 'rmse' in metric or 'mse' in metric or 'mae' in metric else np.argmax(values)
        bars[best_index].set_color('#f39c12')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        
        return fig
    
    def plot_prediction_vs_actual(self, model_instance=None, output_file=None):
        """
        Plots predictions vs actual values for a given model.
        
        Args:
            model_instance: Model to use for prediction (default: best model)
            output_file: If provided, the plot will be saved to this file
            
        Returns:
            matplotlib.figure.Figure: The figure object
        """
        if model_instance is None:
            if self.best_model is None:
                raise ValueError("No best model available. Run compare_models first.")
            model_instance = self.best_model
        
        if self.X_test is None or self.y_test is None:
            raise ValueError("Test data not available. Run split_data or compare_models first.")
        
        # Make predictions
        y_pred = model_instance.predict(self.X_test)
        
        # Create scatterplot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot points
        ax.scatter(self.y_test, y_pred, alpha=0.6, edgecolors='w', color='#3498db')
        
        # Add perfect prediction line
        max_val = max(self.y_test.max(), y_pred.max())
        min_val = min(self.y_test.min(), y_pred.min())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect Prediction')
        
        # Labels and title
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Actual vs Predicted Values')
        
        # Add R² value as annotation
        r2 = r2_score(self.y_test, y_pred)
        ax.annotate(f'R² = {r2:.4f}', 
                   xy=(0.05, 0.95), 
                   xycoords='axes fraction',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        
        return fig
    
    def save_results(self, file_path: str):
        """
        Saves the comparison results to a file.
        
        Args:
            file_path: Path where to save the results
            
        Returns:
            str: Path where the results were saved
        """
        if not self.results:
            raise ValueError("No model comparison results available. Run compare_models first.")
        
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create a copy of results without model instances for serialization
        serializable_results = {}
        for model_name, result in self.results.items():
            serializable_results[model_name] = {
                k: v for k, v in result.items() if k != 'model_instance'
            }
        
        # Add best model information
        comparison_data = {
            'results': serializable_results,
            'best_model_name': self.best_model_name,
            'cv_folds': self.cv_folds,
            'test_size': self.test_size,
            'random_state': self.random_state,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        joblib.dump(comparison_data, file_path)
        
        return file_path
    
    def generate_report(self) -> dict:
        """
        Generates a report of the model comparison results.
        
        Returns:
            dict: Report data
        """
        if not self.results:
            raise ValueError("No model comparison results available. Run compare_models first.")
        
        # Ensure best model is selected
        if self.best_model_name is None:
            self._select_best_model()
        
        # Create a table of results
        models_data = []
        for model_name, result in self.results.items():
            model_data = {
                'model_name': model_name,
                'test_rmse': result['test_rmse'],
                'test_r2': result['test_r2'],
                'cv_mean_rmse': result['cv_mean_rmse'],
                'cv_mean_r2': result['cv_mean_r2'],
                'training_time': result['training_time'],
                'is_best': (model_name == self.best_model_name)
            }
            models_data.append(model_data)
        
        # Calculate improvement over baseline
        baseline_rmse = max(model['test_rmse'] for model in models_data)
        best_model_data = next(model for model in models_data if model['is_best'])
        improvement = ((baseline_rmse - best_model_data['test_rmse']) / baseline_rmse) * 100
        
        # Generate report
        report = {
            'models_comparison': models_data,
            'best_model': {
                'name': self.best_model_name,
                'test_rmse': best_model_data['test_rmse'],
                'test_r2': best_model_data['test_r2'],
                'improvement': improvement
            },
            'cross_validation': {
                'folds': self.cv_folds,
                'test_size': self.test_size
            }
        }
        
        return report