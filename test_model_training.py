# Test script for machine learning models
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import joblib

# Suppress warnings
warnings.filterwarnings('ignore')

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our model classes
from backend.services.linear_regression import LinearRegressionModel
from backend.services.decision_tree import DecisionTreeModel
from backend.services.svm import SVMModel
from backend.services.model_comparison import ModelComparator

def test_model_training():
    """Test the machine learning models with processed data."""
    print("Starting model training and comparison test...\n")
    
    try:
        # Load processed features and target data
        print("Loading processed data...")
        X = pd.read_csv("processed_features.csv")
        y = pd.read_csv("processed_target.csv")["total_price"]
        
        print(f"Loaded {len(X)} samples with {len(X.columns)} features")
        print(f"Feature names: {X.columns.tolist()}")
        
        # Initialize models
        print("\nInitializing models...")
        linear_model = LinearRegressionModel()
        decision_tree_model = DecisionTreeModel(max_depth=10, min_samples_split=5)
        svm_model = SVMModel(C=10.0, epsilon=0.2)
        
        # Initialize model comparator with 5-fold cross-validation
        comparator = ModelComparator(cv_folds=5, test_size=0.2)
        
        # Split data into training and test sets
        X_train, X_test, y_train, y_test = comparator.split_data(X, y)
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Create a dictionary of models
        models = {
            'Linear Regression': linear_model,
            'Decision Tree': decision_tree_model,
            'SVM': svm_model
        }
        
        # Compare models using cross-validation
        print("\nComparing models using cross-validation...")
        results = comparator.compare_models(X, y, models)
        
        # Get the best model
        best_model_name, best_model = comparator.get_best_model()
        print(f"\nBest model: {best_model_name}")
        
        # Save models
        print("\nSaving models...")
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        for name, model in models.items():
            filename = f"models/{name.lower().replace(' ', '_')}_model.joblib"
            model.save_model(filename)
            print(f"Saved {name} model to {filename}")
        
        # Save comparison results
        comparator.save_results("models/comparison_results.joblib")
        print("Saved comparison results to models/comparison_results.joblib")
        
        # Generate plots
        print("\nGenerating plots...")
        plots_dir = Path("plots")
        plots_dir.mkdir(exist_ok=True)
        
        # Model comparison plot
        comparator.plot_model_comparison(
            metric='test_rmse', 
            output_file="plots/model_comparison_rmse.png"
        )
        print("Created model comparison plot")
        
        # Actual vs Predicted plot for the best model
        comparator.plot_prediction_vs_actual(
            model_instance=best_model,
            output_file=f"plots/{best_model_name.lower().replace(' ', '_')}_predictions.png"
        )
        print("Created actual vs predicted plot for the best model")
        
        # Feature importance for Decision Tree
        if isinstance(best_model, DecisionTreeModel):
            best_model.plot_feature_importance(
                output_file="plots/feature_importance.png",
                top_n=10
            )
            print("Created feature importance plot for Decision Tree")
        
        # Generate and print report
        report = comparator.generate_report()
        print("\nModel Comparison Report:")
        print("========================")
        print(f"Best model: {report['best_model']['name']}")
        print(f"Test RMSE: {report['best_model']['test_rmse']:.4f}")
        print(f"Test R²: {report['best_model']['test_r2']:.4f}")
        print(f"Improvement over baseline: {report['best_model']['improvement']:.2f}%")
        print("\nModel comparison:")
        
        for model in report['models_comparison']:
            print(f"  {model['model_name']}:")
            print(f"    Test RMSE: {model['test_rmse']:.4f}")
            print(f"    Test R²: {model['test_r2']:.4f}")
            print(f"    CV Mean RMSE: {model['cv_mean_rmse']:.4f}")
            print(f"    Training Time: {model['training_time']:.2f} seconds")
        
        print("\nModel training and comparison completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print("Make sure to run test_data_processing.py first to generate the processed data files.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_model_training()