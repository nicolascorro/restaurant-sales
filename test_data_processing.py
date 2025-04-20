# Test script for complete data processing pipeline
import sys
from pathlib import Path
import pandas as pd
import warnings

# Suppress the PyArrow warning
warnings.filterwarnings('ignore', message='.*PyArrow will become a required dependency.*')

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.services.data_cleaning import DataCleaner
from backend.services.feature_engineering import FeatureEngineer

def test_data_processing():
    """Test the complete data processing pipeline."""
    print("Starting data processing pipeline test...\n")
    
    # Initialize modules
    cleaner = DataCleaner()
    feature_engineer = FeatureEngineer()
    
    # Update this path to your actual CSV file
    file_path = "dataset_pizza.csv"  # Adjust this to match your CSV filename
    
    try:
        # Step 1: Read and clean the data
        print("Step 1: Reading and cleaning data...")
        df = cleaner.read_csv(file_path)
        print(f"Read {len(df)} rows and {len(df.columns)} columns")
        print(f"Columns in the dataset: {df.columns.tolist()}")
        
        cleaned_df = cleaner.clean_data(df)
        print(f"Cleaned data has {len(cleaned_df)} rows and {len(cleaned_df.columns)} columns")
        
        # Display sample of the data to verify cleaning
        print("\nSample of cleaned data:")
        print(cleaned_df.head())
        print(f"\nColumns after cleaning: {cleaned_df.columns.tolist()}")
        
        # Step 2: Feature engineering
        print("\nStep 2: Performing feature engineering...")
        engineered_df = feature_engineer.prepare_features(cleaned_df)
        print(f"Engineered data has {len(engineered_df)} rows and {len(engineered_df.columns)} columns")
        
        # Step 3: Prepare for prediction
        print("\nStep 3: Preparing data for prediction...")
        X, y, feature_names = feature_engineer.prepare_for_prediction(engineered_df)
        
        if y is not None:
            print(f"Features shape: {X.shape}")
            print(f"Target shape: {y.shape}")
            print(f"Feature names: {feature_names}")
            
            # Display some statistics
            print("\nBasic Statistics:")
            print(f"Total revenue: ${y.sum():.2f}")
            print(f"Average order value: ${y.mean():.2f}")
            print(f"Median order value: ${y.median():.2f}")
            
            # Save processed data
            X.to_csv("processed_features.csv", index=False)
            y.to_csv("processed_target.csv", index=False, header=['total_price'])
            print("\nProcessed data saved to 'processed_features.csv' and 'processed_target.csv'")
            
            # Also save the cleaned data for reference
            cleaned_df.to_csv("cleaned_pizza_sales.csv", index=False)
            print("Cleaned data saved to 'cleaned_pizza_sales.csv'")
        else:
            print("Target variable (total_price) not found in dataset")
        
        # Save the feature engineer's encoders for future use
        feature_engineer.save_encoders("encoders.pkl")
        print("Encoders saved to 'encoders.pkl'")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found. Please check the file path.")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_processing()