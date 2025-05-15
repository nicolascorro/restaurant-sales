# File: backend/services/feature_engineering.py
"""
Feature engineering module for preparing data for machine learning models.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

class FeatureEngineer:
    """Performs feature engineering for restaurant sales data."""
    
    def __init__(self):
        self.encoders = {}
        self.scaler = StandardScaler()
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main function to prepare features for ML models."""
        # Create a copy to avoid modifying the original
        df_engineered = df.copy()
        
        # Extract time-based features
        df_engineered = self.extract_time_features(df_engineered)
        
        # Create aggregate features
        df_engineered = self.create_aggregate_features(df_engineered)
        
        # Encode categorical variables
        df_engineered = self.encode_categorical(df_engineered)
        
        return df_engineered
    
    def extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract time-based features from datetime columns."""
        if 'datetime' in df.columns:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df['datetime']):
                df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Extract features
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
            df['day_of_month'] = df['datetime'].dt.day
            df['month'] = df['datetime'].dt.month
            df['year'] = df['datetime'].dt.year
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # Create time of day categories
            try:
                df['time_of_day'] = pd.cut(df['hour'], 
                                         bins=[0, 6, 12, 18, 24], 
                                         labels=['night', 'morning', 'afternoon', 'evening'])
            except Exception as e:
                print(f"Error creating time_of_day feature: {str(e)}")
        
        return df
    
    def create_aggregate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create aggregate features for sales prediction."""
        # Daily sales aggregation
        if 'order_date' in df.columns and 'total_price' in df.columns:
            daily_sales = df.groupby('order_date')['total_price'].sum().reset_index()
            daily_sales.columns = ['date', 'daily_total_sales']
            
            # Calculate rolling averages
            daily_sales['rolling_7day_avg'] = daily_sales['daily_total_sales'].rolling(window=7).mean()
            daily_sales['rolling_30day_avg'] = daily_sales['daily_total_sales'].rolling(window=30).mean()
        
        # Product popularity features based on actual column names
        if 'pizza_name' in df.columns or 'pizza_id' in df.columns:
            pizza_col = 'pizza_name' if 'pizza_name' in df.columns else 'pizza_id'
            try:
                product_popularity = df.groupby(pizza_col).agg({
                    'quantity': 'sum',
                    'total_price': 'sum',
                    'order_id': 'count'
                }).reset_index()
                product_popularity.columns = [pizza_col, 'total_quantity', 'total_revenue', 'total_orders']
                product_popularity['avg_order_value'] = product_popularity['total_revenue'] / product_popularity['total_orders']
                
                # Save this for visualization later
                product_popularity.to_csv('product_popularity.csv', index=False)
            except Exception as e:
                print(f"Error creating product popularity features: {str(e)}")
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical variables for ML models."""
        # Identify categorical columns based on data type and content
        potential_categorical = ['pizza_category', 'pizza_size', 'pizza_name', 'pizza_name_id']
        existing_categorical = [col for col in potential_categorical if col in df.columns]
        
        for col in existing_categorical:
            try:
                # Use LabelEncoder for ordinal data like pizza size
                if col == 'pizza_size' and col in df.columns:
                    size_order = {'s': 0, 'm': 1, 'l': 2, 'xl': 3, 'xxl': 4}
                    df[f'{col}_encoded'] = df[col].map(size_order)
                    # Fill any unmapped values with -1
                    df[f'{col}_encoded'] = df[f'{col}_encoded'].fillna(-1).astype(int)
                    self.encoders[col] = size_order
                else:
                    # First check if the column has too many unique values
                    n_unique = df[col].nunique()
                    if n_unique > 50:  # Too many for one-hot encoding
                        print(f"Skipping {col} - too many unique values ({n_unique})")
                        continue
                    
                    df_encoded = pd.get_dummies(df[col], prefix=col)
                    df = pd.concat([df, df_encoded], axis=1)
            except Exception as e:
                print(f"Error encoding {col}: {str(e)}")
        
        return df
    
    def prepare_for_prediction(self, df: pd.DataFrame) -> tuple:
        """Prepare data specifically for prediction models."""
        # Ensure datetime features are extracted
        if 'datetime' not in df.columns and 'order_date' in df.columns and 'order_time' in df.columns:
            try:
                # Convert date to string format for concatenation
                date_str = df['order_date'].dt.strftime('%Y-%m-%d')
                time_str = df['order_time'].str.strip()
                df['datetime'] = pd.to_datetime(date_str + ' ' + time_str)
            except Exception as e:
                print(f"Error creating datetime for prediction: {str(e)}")
        
        # Extract features
        df = self.extract_time_features(df)
        
        # Define features and target
        numeric_features = ['hour', 'day_of_week', 'day_of_month', 'month', 'year', 'is_weekend']
        if 'quantity' in df.columns:
            numeric_features.append('quantity')
        if 'unit_price' in df.columns:
            numeric_features.append('unit_price')
        
        # Add encoded categorical features
        categorical_features = []
        for col in ['pizza_category', 'pizza_size', 'pizza_name']:
            if col in df.columns:
                if col == 'pizza_size':
                    if f'{col}_encoded' in df.columns:
                        categorical_features.append(f'{col}_encoded')
                else:
                    # Find all one-hot encoded columns for this category
                    encoded_cols = [c for c in df.columns if c.startswith(f'{col}_')]
                    categorical_features.extend(encoded_cols)
        
        # Combine all features
        feature_columns = numeric_features + categorical_features
        
        # Check which features are available
        available_features = [col for col in feature_columns if col in df.columns]
        
        # Prepare X and y
        X = df[available_features]
        y = df['total_price'] if 'total_price' in df.columns else None
        
        # Convert all feature columns to numeric
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        
        # Fill any NaN values with 0
        X = X.fillna(0)
        
        return X, y, available_features
    
    def save_encoders(self, filepath: str):
        """Save encoders for future use."""
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(self.encoders, f)
    
    def load_encoders(self, filepath: str):
        """Load previously saved encoders."""
        import pickle
        with open(filepath, 'rb') as f:
            self.encoders = pickle.load(f)