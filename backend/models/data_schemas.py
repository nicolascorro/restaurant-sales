# File: backend/models/data_schemas.py
"""
Pydantic models for data validation and typing.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class OrderDetails(BaseModel):
    """Schema for order details entries."""
    order_details_id: int
    order_id: int
    food_id: int
    quantity: int
    order_date: datetime
    unit_price: float
    total_price: float
    food_category: str

class FoodItem(BaseModel):
    """Schema for food items."""
    food_id: int
    food_category: str
    food_name: str
    food_ingredients: Optional[str]

class PredictionResult(BaseModel):
    """Schema for prediction results."""
    prediction_model_type: str
    accuracy_score: float
    prediction_date: datetime
    predicted_value: float
    confidence_interval: Optional[List[float]]
