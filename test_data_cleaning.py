# Test script for data cleaning functionality
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.services.data_cleaning import DataCleaner
import pandas as pd

def test_data_cleaning():
    """Test the data cleaning functionality with a sample dataset."""
    # Initialize the data cleaner
    cleaner = DataCleaner()
    
    # Read your CSV file
    file_path = "dataset_pizza.csv"  # Replace with your actual file path
    
    try:
        # Read the CSV
        df = cleaner.read_csv(file_path)
        print(f"Successfully read CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Print original columns
        print("\nOriginal columns:")
        print(df.columns.tolist())
        
        # Clean the data
        cleaned_df = cleaner.clean_data(df)
        
        # Check the results
        print("\nData types after cleaning:")
        print(cleaned_df.dtypes)
        
        print("\nMissing values after cleaning:")
        print(cleaned_df.isnull().sum())
        
        print("\nSample of cleaned data:")
        print(cleaned_df.head())
        
        # Show added features if any
        new_columns = set(cleaned_df.columns) - set(df.columns)
        if new_columns:
            print(f"\nNew columns added: {new_columns}")
        
        # Basic statistics
        if 'total_price' in cleaned_df.columns:
            print(f"\nTotal revenue: ${cleaned_df['total_price'].sum():.2f}")
            print(f"Average order value: ${cleaned_df['total_price'].mean():.2f}")
        
        # Save cleaned data to a new CSV
        cleaned_df.to_csv("cleaned_pizza_sales.csv", index=False)
        print("\nCleaned data saved to 'cleaned_pizza_sales.csv'")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_data_cleaning()