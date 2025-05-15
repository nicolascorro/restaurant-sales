# File: backend/services/data_cleaning.py
"""
Data cleaning and preprocessing module.
Handles missing values, normalization, and data transformation.
"""
import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    """Cleans and preprocesses restaurant sales data from CSV files."""
    
    def __init__(self):
        self.clean_df = None
        self.original_columns = None
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """Reads CSV file into a DataFrame."""
        try:
            df = pd.read_csv(file_path)
            self.original_columns = df.columns.tolist()
            return df
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main cleaning function that orchestrates all cleaning steps."""
        # Create a copy to avoid modifying the original
        self.clean_df = df.copy()
        
        # Apply cleaning steps
        self.clean_df = self.handle_missing_values(self.clean_df)
        self.clean_df = self.normalize_text_fields(self.clean_df)
        self.clean_df = self.convert_dates(self.clean_df)
        self.clean_df = self.prepare_for_ml(self.clean_df)
        
        return self.clean_df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handles missing values in the dataset."""
        # Check for missing values
        missing_summary = df.isnull().sum()
        if missing_summary.sum() > 0:
            print("Missing values found:")
            print(missing_summary[missing_summary > 0])
        
        # Strategy for different column types:
        # Numeric columns: fill with median
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df[col] = df[col].fillna(df[col].median())
        
        # Text columns: fill with 'Unknown' or most frequent value
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].fillna('Unknown')
        
        return df
    
    def normalize_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalizes text fields like food names and categories."""
        text_columns = df.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            # Convert to string type
            df[col] = df[col].astype(str)
            # Strip whitespace
            df[col] = df[col].str.strip()
            # Convert to lowercase (except proper names if needed)
            if col not in ['pizza_name_id']:  # Keep pizza IDs as is
                df[col] = df[col].str.lower()
            # Replace multiple spaces with single space
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        
        return df
    
    def convert_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts date fields to datetime format."""
        # Handle the order_date specifically since it's in dd/mm/yyyy format
        if 'order_date' in df.columns:
            try:
                df['order_date'] = pd.to_datetime(df['order_date'], format='%d/%m/%Y')
            except Exception as e:
                print(f"Error converting order_date: {str(e)}")
                # Try with dayfirst=True as fallback
                try:
                    df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True)
                except Exception as e:
                    print(f"Error with dayfirst conversion: {str(e)}")
        
        # Handle order_time if present
        if 'order_time' in df.columns:
            try:
                # First ensure order_time is in string format
                df['order_time'] = df['order_time'].astype(str)
            except Exception as e:
                print(f"Error converting order_time to string: {str(e)}")
        
        # Create datetime column if both date and time are present
        if 'order_date' in df.columns and 'order_time' in df.columns:
            try:
                # Convert date to string format for concatenation
                date_str = df['order_date'].dt.strftime('%Y-%m-%d')
                # Remove any whitespace from time
                time_str = df['order_time'].str.strip()
                # Combine and convert to datetime
                df['datetime'] = pd.to_datetime(date_str + ' ' + time_str)
                
                # Extract useful time features
                df['hour'] = df['datetime'].dt.hour
                df['day_of_week'] = df['datetime'].dt.dayofweek
                df['month'] = df['datetime'].dt.month
                df['year'] = df['datetime'].dt.year
            except Exception as e:
                print(f"Error creating datetime column: {str(e)}")
        
        return df
    
    def prepare_for_ml(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for machine learning models."""
        # Ensure we have a datetime column if not already created
        if 'datetime' not in df.columns and 'order_date' in df.columns and 'order_time' in df.columns:
            try:
                # Convert date to string format for concatenation
                date_str = df['order_date'].dt.strftime('%Y-%m-%d')
                # Remove any whitespace from time
                time_str = df['order_time'].str.strip()
                # Combine and convert to datetime
                df['datetime'] = pd.to_datetime(date_str + ' ' + time_str)
            except Exception as e:
                print(f"Error in prepare_for_ml datetime creation: {str(e)}")
        
        # Create total revenue column if not exists
        if 'total_price' in df.columns:
            # Ensure price columns are numeric
            numeric_cols = ['unit_price', 'total_price', 'quantity']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def encode_categorical_variables(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encodes categorical variables for ML models."""
        pass
    
    def get_clean_data(self) -> pd.DataFrame:
        """Returns the cleaned DataFrame."""
        return self.clean_df