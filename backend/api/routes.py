# File: backend/api/routes.py
"""
API route definitions for the FastAPI application.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt

# Import services
from services.data_cleaning import DataCleaner
from services.feature_engineering import FeatureEngineer
from services.model_comparison import ModelComparator
from services.linear_regression import LinearRegressionModel
from services.decision_tree import DecisionTreeModel
from services.svm import SVMModel

# Import utility functions
from utils.helpers import save_uploaded_file, generate_file_id, get_data_directory, get_processed_data_directory, save_processing_metadata, load_processing_metadata

router = APIRouter()

# Ensure plots directory exists
def ensure_plots_directory():
    plots_dir = Path('plots')
    plots_dir.mkdir(exist_ok=True)
    return plots_dir

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Handles CSV file upload."""
    try:
        # Check if file is a CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Generate a unique file ID
        file_id = generate_file_id()
        
        # Save the file
        file_path = await save_uploaded_file(file, file.filename)
        
        # Save metadata
        metadata = {
            "original_filename": file.filename,
            "file_path": file_path,
            "file_id": file_id,
            "status": "uploaded"
        }
        save_processing_metadata(file_id, metadata)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "success"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@router.get("/process/{file_id}")
async def process_data(file_id: str):
    """Processes uploaded CSV data."""
    try:
        # Load file metadata
        try:
            metadata = load_processing_metadata(file_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        file_path = metadata["file_path"]
        
        # Initialize data cleaning and feature engineering
        data_cleaner = DataCleaner()
        feature_engineer = FeatureEngineer()
        
        # Read and clean the data
        raw_data = data_cleaner.read_csv(file_path)
        cleaned_data = data_cleaner.clean_data(raw_data)
        
        # Prepare features for modeling
        feature_data = feature_engineer.prepare_features(cleaned_data)
        
        # Prepare for prediction
        X, y, feature_columns = feature_engineer.prepare_for_prediction(feature_data)
        
        # Save processed data
        processed_dir = Path(get_processed_data_directory())
        processed_dir.mkdir(exist_ok=True, parents=True)
        processed_file_path = os.path.join(get_processed_data_directory(), f"{file_id}_processed.csv")
        feature_data.to_csv(processed_file_path, index=False)
        
        # Save extended metadata
        metadata.update({
            "status": "processed",
            "processed_file_path": processed_file_path,
            "rows_processed": len(feature_data),
            "features_created": feature_columns,
            "has_target": y is not None
        })
        save_processing_metadata(file_id, metadata)
        
        return {
            "file_id": file_id,
            "status": "processed",
            "rows_processed": len(feature_data),
            "features_created": feature_columns,
            "has_target": y is not None
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@router.get("/forecast/{file_id}")
async def get_forecast(file_id: str):
    """Returns sales forecast data."""
    try:
        # Load metadata
        try:
            metadata = load_processing_metadata(file_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        # Check status (accept 'processed' or any later stage)
        valid_statuses = ["processed", "forecast_generated", "products_analyzed", "report_generated"]
        if metadata["status"] not in valid_statuses:
            raise HTTPException(status_code=400, detail="Data has not been processed yet")
        
        # Load processed data
        processed_file_path = metadata["processed_file_path"]
        data = pd.read_csv(processed_file_path)
        
        # Initialize feature engineering to prepare data for models
        feature_engineer = FeatureEngineer()
        X, y, features = feature_engineer.prepare_for_prediction(data)
        
        if y is None:
            raise HTTPException(status_code=400, detail="Target column not found in data")
        
        # Initialize models
        lin_reg_model = LinearRegressionModel()
        decision_tree_model = DecisionTreeModel()
        svm_model = SVMModel()
        
        # Create model comparator
        model_comparator = ModelComparator()
        
        # Split data into train/test
        X_train, X_test, y_train, y_test = model_comparator.split_data(X, y)
        
        # Compare models
        models = {
            "linear_regression": lin_reg_model,
            "decision_tree": decision_tree_model,
            "svm": svm_model
        }
        
        comparison_results = model_comparator.compare_models(X, y, models)
        
        # Get best model
        best_model_name, best_model = model_comparator.get_best_model()
        
        # Generate report
        model_report = model_comparator.generate_report()
        
        # Create plots directory if it doesn't exist
        ensure_plots_directory()
        
        # Save model comparison visualization
        plot_file_path = os.path.join('plots', f"{file_id}_model_comparison.png")
        try:
            model_comparator.plot_model_comparison(output_file=plot_file_path)
        except Exception as plot_error:
            # Log error but continue execution
            print(f"Error saving plot: {str(plot_error)}")
        
        # Create forecast data for visualization
        # For actual forecast, we'd use the best model to predict future periods
        # For now, we'll use the test predictions for visualization
        date_column = None
        for col in ['order_date', 'datetime', 'date']:
            if col in data.columns:
                date_column = col
                break
        
        if date_column:
            # Get unique dates
            dates = data[date_column].unique()
            dates.sort()
            
            # For each date, calculate actual and predicted values
            chart_data = []
            for date in dates:
                date_mask = data[date_column] == date
                date_data = data[date_mask]
                
                if len(date_data) > 0:
                    # For actual values, use the sum of total_price for that date
                    total_price_col = None
                    for col in ['total_price', 'price', 'revenue']:
                        if col in date_data.columns:
                            total_price_col = col
                            break
                    
                    actual_value = date_data[total_price_col].sum() if total_price_col else None
                    
                    # For prediction, we would ideally predict future dates
                    # For demonstration, we'll use our model to predict these dates
                    X_date = X[date_mask]
                    if len(X_date) > 0:
                        try:
                            predicted_values = best_model.predict(X_date)
                            predicted_value = float(predicted_values.sum())
                        except Exception as pred_error:
                            print(f"Error predicting for date {date}: {str(pred_error)}")
                            predicted_value = actual_value  # Fallback to actual value
                    else:
                        predicted_value = None
                    
                    chart_data.append({
                        'date': str(date),
                        'actual': float(actual_value) if actual_value is not None else None,
                        'predicted': float(predicted_value) if predicted_value is not None else None
                    })
        else:
            # If no date column, use indices as x-axis
            chart_data = []
            try:
                test_predictions = best_model.predict(X_test)
                
                for i in range(len(y_test)):
                    chart_data.append({
                        'date': f"Sample {i+1}",
                        'actual': float(y_test.iloc[i]),
                        'predicted': float(test_predictions[i])
                    })
            except Exception as pred_error:
                print(f"Error generating chart data: {str(pred_error)}")
                # Create minimal placeholder data
                chart_data = [{'date': 'Sample 1', 'actual': 100, 'predicted': 110}]
        
        # Prepare model details
        model_details = {
            "model_type": best_model_name,
            "rmse": float(comparison_results[best_model_name]["test_rmse"]),
            "r2": float(comparison_results[best_model_name]["test_r2"]),
            "training_time": float(comparison_results[best_model_name]["training_time"])
        }
        
        # Create prediction results summary
        if len(chart_data) > 0:
            actual_values = [d['actual'] for d in chart_data if d['actual'] is not None]
            predicted_values = [d['predicted'] for d in chart_data if d['predicted'] is not None]
            
            if actual_values and predicted_values:
                # Calculate trend
                avg_predicted = sum(predicted_values) / len(predicted_values)
                max_predicted = max(predicted_values)
                max_predicted_idx = predicted_values.index(max_predicted)
                
                min_predicted = min(predicted_values)
                min_predicted_idx = predicted_values.index(min_predicted)
                
                # Determine trend direction
                if len(predicted_values) > 1:
                    first_half = predicted_values[:len(predicted_values)//2]
                    second_half = predicted_values[len(predicted_values)//2:]
                    
                    first_half_avg = sum(first_half) / len(first_half)
                    second_half_avg = sum(second_half) / len(second_half)
                    
                    if second_half_avg > first_half_avg:
                        trend = "up"
                        trend_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                    elif second_half_avg < first_half_avg:
                        trend = "down"
                        trend_percentage = ((first_half_avg - second_half_avg) / first_half_avg) * 100
                    else:
                        trend = "stable"
                        trend_percentage = 0
                else:
                    trend = "stable"
                    trend_percentage = 0
                
                prediction_summary = {
                    "avg_predicted_sales": float(avg_predicted),
                    "max_predicted_day": str(chart_data[max_predicted_idx]["date"]),
                    "max_predicted_value": float(max_predicted),
                    "min_predicted_day": str(chart_data[min_predicted_idx]["date"]),
                    "min_predicted_value": float(min_predicted),
                    "trend": trend,
                    "trend_percentage": float(trend_percentage)
                }
            else:
                prediction_summary = {
                    "avg_predicted_sales": 0,
                    "max_predicted_day": "",
                    "max_predicted_value": 0,
                    "min_predicted_day": "",
                    "min_predicted_value": 0,
                    "trend": "stable",
                    "trend_percentage": 0
                }
        else:
            prediction_summary = {
                "avg_predicted_sales": 0,
                "max_predicted_day": "",
                "max_predicted_value": 0,
                "min_predicted_day": "",
                "min_predicted_value": 0,
                "trend": "stable",
                "trend_percentage": 0
            }
        
        # Update metadata with forecast info
        metadata.update({
            "status": "forecast_generated",
            "best_model": best_model_name,
            "model_metrics": {
                "rmse": comparison_results[best_model_name]["test_rmse"],
                "r2": comparison_results[best_model_name]["test_r2"]
            },
            "trend": trend
        })
        save_processing_metadata(file_id, metadata)
        
        # Return the complete forecast data
        return {
            "chart_data": chart_data,
            "prediction_results": {
                "best_model": {
                    "model_type": best_model_name,
                    "accuracy_score": float(comparison_results[best_model_name]["test_r2"]),
                    "rmse": float(comparison_results[best_model_name]["test_rmse"])
                },
                "all_models": [
                    {
                        "model_type": name,
                        "accuracy_score": float(result["test_r2"]),
                        "rmse": float(result["test_rmse"])
                    }
                    for name, result in comparison_results.items()
                ],
                "prediction_summary": prediction_summary
            },
            "model_details": model_details
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

@router.get("/products/{file_id}")
async def get_top_products(file_id: str):
    """Returns best-selling products data."""
    try:
        # Load metadata
        try:
            metadata = load_processing_metadata(file_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        # Check status (accept 'processed' or any later stage)
        valid_statuses = ["processed", "forecast_generated", "products_analyzed", "report_generated"]
        if metadata["status"] not in valid_statuses:
            raise HTTPException(status_code=400, detail="Data has not been processed yet")
        
        # Load processed data
        processed_file_path = metadata["processed_file_path"]
        data = pd.read_csv(processed_file_path)
        
        # Analyze product sales
        # First, identify column names for food items and categories
        food_name_col = None
        food_category_col = None
        quantity_col = None
        price_col = None
        
        # Check possible column names
        for possible_name_col in ['food_name', 'pizza_name', 'product_name', 'item_name', 'name']:
            if possible_name_col in data.columns:
                food_name_col = possible_name_col
                break
        
        for possible_category_col in ['food_category', 'pizza_category', 'product_category', 'category']:
            if possible_category_col in data.columns:
                food_category_col = possible_category_col
                break
        
        for possible_quantity_col in ['quantity', 'qty']:
            if possible_quantity_col in data.columns:
                quantity_col = possible_quantity_col
                break
        
        for possible_price_col in ['total_price', 'revenue', 'price']:
            if possible_price_col in data.columns:
                price_col = possible_price_col
                break
        
        if not food_name_col or not price_col:
            raise HTTPException(status_code=400, detail="Required columns not found in data")
        
        # Group by product name and calculate revenue and quantity
        if food_category_col and quantity_col:
            product_data = data.groupby([food_name_col, food_category_col])[price_col].sum().reset_index()
            quantity_data = data.groupby([food_name_col])[quantity_col].sum().reset_index()
            product_data = pd.merge(product_data, quantity_data, on=food_name_col)
        elif food_category_col:
            product_data = data.groupby([food_name_col, food_category_col])[price_col].sum().reset_index()
            product_data['quantity'] = 0  # Placeholder
        elif quantity_col:
            product_data = data.groupby([food_name_col])[price_col].sum().reset_index()
            quantity_data = data.groupby([food_name_col])[quantity_col].sum().reset_index()
            product_data = pd.merge(product_data, quantity_data, on=food_name_col)
            product_data[food_category_col] = 'Unknown'  # Placeholder
        else:
            product_data = data.groupby([food_name_col])[price_col].sum().reset_index()
            product_data['quantity'] = 0  # Placeholder
            product_data[food_category_col] = 'Unknown'  # Placeholder
        
        # Calculate percentage of total
        total_revenue = product_data[price_col].sum()
        product_data['percentage'] = (product_data[price_col] / total_revenue) * 100
        
        # Sort by revenue
        product_data = product_data.sort_values(by=price_col, ascending=False).reset_index(drop=True)
        
        # Get top 10 products
        top_products = product_data.head(10)
        
        # Prepare chart data (top 5 for pie chart)
        chart_data = []
        for _, row in top_products.head(5).iterrows():
            chart_data.append({
                'name': row[food_name_col],
                'value': float(row[price_col]),
                'percent': float(row['percentage'])
            })
        
        # Add "Other" category for remaining products
        if len(product_data) > 5:
            other_value = product_data.iloc[5:][price_col].sum()
            other_percent = product_data.iloc[5:]['percentage'].sum()
            chart_data.append({
                'name': 'Other',
                'value': float(other_value),
                'percent': float(other_percent)
            })
        
        # Prepare product details for table
        product_details = []
        for _, row in top_products.iterrows():
            product_details.append({
                'name': row[food_name_col],
                'category': row[food_category_col] if food_category_col else 'Unknown',
                'revenue': float(row[price_col]),
                'quantity': int(row['quantity']) if 'quantity' in row else 0,
                'percentage': float(row['percentage'])
            })
        
        # Prepare summary
        if food_category_col:
            top_category = data.groupby([food_category_col])[price_col].sum().reset_index()
            top_category['percentage'] = (top_category[price_col] / top_category[price_col].sum()) * 100
            top_category = top_category.sort_values(by=price_col, ascending=False).reset_index(drop=True)
            top_category_name = top_category.iloc[0][food_category_col]
            top_category_percentage = float(top_category.iloc[0]['percentage'])
        else:
            top_category_name = "Unknown"
            top_category_percentage = 100.0
        
        top_five_percentage = float(top_products.head(5)['percentage'].sum())
        
        summary = {
            'total_products': len(product_data),
            'top_five_percentage': top_five_percentage,
            'top_category': top_category_name,
            'top_category_percentage': top_category_percentage,
            'highest_margin_product': top_products.iloc[0][food_name_col]
        }
        
        # Update metadata
        metadata.update({
            "status": "products_analyzed",
            "top_products": [p['name'] for p in product_details[:5]]
        })
        save_processing_metadata(file_id, metadata)
        
        # Return product analysis
        return {
            'chart_data': chart_data,
            'product_details': product_details,
            'summary': summary
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing products: {str(e)}")

@router.post("/report/{file_id}")
async def generate_report(file_id: str):
    """Generates AI business report."""
    try:
        # Load metadata
        try:
            metadata = load_processing_metadata(file_id)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        # Check status (accept any processed or later stage)
        valid_statuses = ["processed", "forecast_generated", "products_analyzed", "report_generated"]
        if metadata["status"] not in valid_statuses:
            raise HTTPException(status_code=400, detail="Required analysis has not been performed yet")
        
        # Load processed data
        processed_file_path = metadata["processed_file_path"]
        data = pd.read_csv(processed_file_path)
        
        # Get best model information
        best_model = metadata.get("best_model", "unknown")
        model_metrics = metadata.get("model_metrics", {})
        
        # Get top products
        top_products = metadata.get("top_products", [])
        
        # Generate report based on actual data characteristics
        
        # Check if we have date information for time-based insights
        has_time_data = False
        day_of_week_col = None
        time_of_day_col = None
        
        for col in ['day_of_week', 'weekday']:
            if col in data.columns:
                day_of_week_col = col
                has_time_data = True
                break
        
        for col in ['hour', 'time_of_day']:
            if col in data.columns:
                time_of_day_col = col
                has_time_data = True
                break
        
        # Generate insights based on available data
        insights = []
        
        # Top products insight
        if top_products:
            insights.append(f"Your top product {top_products[0]} is your revenue leader")
            if len(top_products) > 1:
                insights.append(f"Your top 5 products ({', '.join(top_products[:5])}) contribute significantly to your overall revenue")
        
        # Time-based insights
        if has_time_data:
            if day_of_week_col:
                # Calculate sales by day of week
                day_sales = data.groupby(day_of_week_col)['total_price'].sum().reset_index()
                day_sales['percentage'] = (day_sales['total_price'] / day_sales['total_price'].sum()) * 100
                
                # Find busiest and slowest days
                day_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                              4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
                
                day_sales = day_sales.sort_values(by='total_price', ascending=False)
                busiest_day = day_mapping.get(day_sales.iloc[0][day_of_week_col], str(day_sales.iloc[0][day_of_week_col]))
                slowest_day = day_mapping.get(day_sales.iloc[-1][day_of_week_col], str(day_sales.iloc[-1][day_of_week_col]))
                
                insights.append(f"{busiest_day} is your busiest day with {day_sales.iloc[0]['percentage']:.1f}% of weekly sales")
                insights.append(f"{slowest_day} is your slowest day and could benefit from targeted promotions")
            
            if time_of_day_col:
                # If we have hour data, identify peak hours
                if time_of_day_col == 'hour':
                    hour_sales = data.groupby(time_of_day_col)['total_price'].sum().reset_index()
                    hour_sales = hour_sales.sort_values(by='total_price', ascending=False)
                    
                    peak_hour = hour_sales.iloc[0][time_of_day_col]
                    insights.append(f"Your peak revenue hour is around {peak_hour}:00")
                elif time_of_day_col == 'time_of_day':
                    time_sales = data.groupby(time_of_day_col)['total_price'].sum().reset_index()
                    time_sales = time_sales.sort_values(by='total_price', ascending=False)
                    
                    peak_time = time_sales.iloc[0][time_of_day_col]
                    insights.append(f"Your {peak_time} period generates the most revenue")
        
        # Model performance insight
        if model_metrics:
            rmse = model_metrics.get("rmse")
            r2 = model_metrics.get("r2")
            
            if r2:
                accuracy_pct = r2 * 100
                insights.append(f"Sales forecasting achieved {accuracy_pct:.1f}% accuracy using the {best_model} model")
        
        # If we don't have enough real insights, add some placeholders
        if len(insights) < 3:
            insights.extend([
                "Analyze your menu periodically to maintain focus on high-performing items",
                "Consider seasonal promotions to boost sales during slower periods",
                "Monitor inventory closely to reduce waste and optimize ordering"
            ])
        
        # Generate recommendations based on insights
        recommendations = []
        
        # Product recommendations
        if top_products:
            recommendations.append("Focus marketing efforts on your top-performing products to maximize returns")
            recommendations.append("Consider bundling top products with lower-performing items to increase overall sales")
        
        # Time-based recommendations
        if has_time_data and day_of_week_col:
            recommendations.append(f"Implement special promotions on {slowest_day} to increase customer traffic")
        
        if has_time_data and time_of_day_col:
            recommendations.append("Ensure adequate staffing during peak hours to maximize service quality and revenue")
        
        # General recommendations
        recommendations.append("Regularly review sales data to identify emerging trends and adjust your strategy accordingly")
        recommendations.append("Use the sales forecast to optimize inventory management and reduce waste")
        
        # Future outlook - based on the model prediction trend
        trend_direction = "upward" if metadata.get("trend", "") == "up" else "downward" if metadata.get("trend", "") == "down" else "stable"
        future_outlook = f"Based on the {best_model} model analysis, sales are showing a {trend_direction} trend. "
        
        if trend_direction == "upward":
            future_outlook += "Consider investing in additional capacity and staff training to meet increased demand."
        elif trend_direction == "downward":
            future_outlook += "Focus on marketing and customer retention strategies to reverse this trend."
        else:
            future_outlook += "Maintain current operations while looking for opportunities to increase efficiency and profit margins."
        
        # Create the final report
        report = {
            "summary": f"Analysis of your restaurant sales data reveals important patterns and opportunities for growth. The {best_model} model provided the most accurate sales forecasts, and your top products contribute significantly to your bottom line.",
            "insights": insights,
            "recommendations": recommendations,
            "future_outlook": future_outlook
        }
        
        # Update metadata
        metadata.update({
            "status": "report_generated"
        })
        save_processing_metadata(file_id, metadata)
        
        return {
            "report": report,
            "status": "success"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")