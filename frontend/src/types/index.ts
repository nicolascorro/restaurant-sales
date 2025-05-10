// src/types/index.ts

export * from './ProductDetail';

export interface OrderDetails {
  order_details_id: number;
  order_id: number;
  food_id: number;
  quantity: number;
  order_date: string;
  unit_price: number;
  total_price: number;
  food_category: string;
}

export interface FoodItem {
  food_id: number;
  food_category: string;
  food_name: string;
  food_ingredients?: string;
}

export interface PredictionResult {
  prediction_model_type: string;
  accuracy_score: number;
  prediction_date: string;
  predicted_value: number;
  confidence_interval?: number[];
}

// Frontend-specific types
export interface ForecastChartData {
  date: string;
  actual?: number;
  predicted: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface ProductChartData {
  name: string;
  value: number;
  percent: number;
  quantity?: number;
}

export interface ModelComparisonData {
  model_name: string;
  rmse: number;
  mae?: number;
  r2?: number;
  accuracy: number;
  is_best: boolean;
}

export interface UploadResponse {
  file_id: string;
  filename: string;
  status: string;
}

export interface ProcessResponse {
  file_id: string;
  status: string;
  rows_processed: number;
  features_created: string[];
}

export interface ReportData {
  summary: string;
  insights: string[];
  recommendations: string[];
  future_outlook: string;
}