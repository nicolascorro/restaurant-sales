// src/components/AnalysisResults.tsx
import React from 'react';
import { 
  Paper, 
  Typography, 
  Card, 
  CardContent, 
  Divider,
  Chip,
  Box
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface ModelResult {
  model_type: string;
  accuracy_score: number;
  rmse?: number;
  mae?: number;
  r2?: number;
}

interface AnalysisResultsProps {
  predictionResults?: {
    best_model: ModelResult;
    all_models: ModelResult[];
    prediction_summary: {
      avg_predicted_sales: number;
      max_predicted_day: string;
      max_predicted_value: number;
      min_predicted_day: string;
      min_predicted_value: number;
      trend: 'up' | 'down' | 'stable';
      trend_percentage: number;
    };
  };
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ predictionResults }) => {
  // If no results available, show placeholder
  if (!predictionResults) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" align="center" color="textSecondary">
          No analysis results available yet
        </Typography>
        <Typography variant="body2" align="center" color="textSecondary" sx={{ mt: 1 }}>
          Upload a CSV file to generate prediction results
        </Typography>
      </Paper>
    );
  }

  const { best_model, prediction_summary } = predictionResults;
  
  // Generate color based on trend
  const trendColor = prediction_summary.trend === 'up' 
    ? 'success.main' 
    : prediction_summary.trend === 'down' 
      ? 'error.main' 
      : 'info.main';

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>Analysis Results</Typography>
      <Divider sx={{ mb: 3 }} />
      
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Best Model Card */}
        <Box sx={{ flex: '1 1 30%', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Best Prediction Model
              </Typography>
              <Chip 
                icon={<CheckCircleIcon />} 
                label={best_model.model_type.replace('_', ' ').toUpperCase()} 
                color="primary" 
                sx={{ mb: 2 }}
              />
              <Typography variant="body2">
                Accuracy Score: {(best_model.accuracy_score * 100).toFixed(2)}%
              </Typography>
              {best_model.rmse && (
                <Typography variant="body2">
                  RMSE: {best_model.rmse.toFixed(2)}
                </Typography>
              )}
              {best_model.r2 && (
                <Typography variant="body2">
                  R² Score: {best_model.r2.toFixed(2)}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
        
        {/* Prediction Summary Card */}
        <Box sx={{ flex: '1 1 30%', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales Forecast Summary
              </Typography>
              <Typography variant="body2">
                Average Predicted Daily Sales: ${prediction_summary.avg_predicted_sales.toFixed(2)}
              </Typography>
              <Typography variant="body2">
                Highest Day: {prediction_summary.max_predicted_day} (${prediction_summary.max_predicted_value.toFixed(2)})
              </Typography>
              <Typography variant="body2">
                Lowest Day: {prediction_summary.min_predicted_day} (${prediction_summary.min_predicted_value.toFixed(2)})
              </Typography>
            </CardContent>
          </Card>
        </Box>
        
        {/* Trend Card */}
        <Box sx={{ flex: '1 1 30%', minWidth: '250px' }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Sales Trend
              </Typography>
              <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
                {prediction_summary.trend === 'up' ? (
                  <TrendingUpIcon sx={{ color: trendColor, mr: 1 }} />
                ) : prediction_summary.trend === 'down' ? (
                  <TrendingDownIcon sx={{ color: trendColor, mr: 1 }} />
                ) : (
                  <TrendingUpIcon sx={{ color: trendColor, mr: 1 }} />
                )}
                <Typography variant="h4" sx={{ color: trendColor }}>
                  {prediction_summary.trend_percentage.toFixed(1)}%
                </Typography>
              </Box>
              <Typography variant="body2">
                {prediction_summary.trend === 'up' 
                  ? 'Forecast shows an upward trend'
                  : prediction_summary.trend === 'down'
                    ? 'Forecast shows a downward trend'
                    : 'Forecast shows a stable trend'}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Paper>
  );
};

export default AnalysisResults;