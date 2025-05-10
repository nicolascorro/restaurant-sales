// src/pages/Forecast.tsx
import React, { useEffect, useState } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  Button,
  Box,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import SalesChart from '../components/SalesChart';
import AnalysisResults from '../components/AnalysisResults';
import { getForecast } from '../api/endpoints';

const Forecast: React.FC = () => {
  const navigate = useNavigate();
  const { fileId, forecastData, setForecastData } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  // Redirect if no fileId is set
  useEffect(() => {
    if (!fileId) {
      navigate('/upload');
    }
  }, [fileId, navigate]);
  
  // Fetch forecast data if needed
  useEffect(() => {
    const fetchData = async () => {
      if (fileId && (!forecastData || retryCount > 0)) {
        try {
          setLoading(true);
          setError(null);
          
          const data = await getForecast(fileId);
          setForecastData(data);
          setRetryCount(0); // Reset retry count on success
          
        } catch (err: any) {
          console.error('Error fetching forecast data:', err);
          // Extract error message from response if available
          const errorMessage = err.response?.data?.detail || 'Failed to load forecast data. The server may still be processing your data. Please try again.';
          setError(errorMessage);
          
          // If the error is "Data has not been processed yet", we might want to retry
          if (errorMessage.includes("not been processed yet") && retryCount < 3) {
            // Wait 2 seconds before retrying
            setTimeout(() => {
              setRetryCount(prev => prev + 1);
            }, 2000);
          }
        } finally {
          setLoading(false);
        }
      }
    };
    
    fetchData();
  }, [fileId, forecastData, setForecastData, retryCount]);
  
  // Render loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
        Hang tight! We’re generating your sales forecast. <br/> 
        This usually takes about 1–2 minutes.
        </Typography>
        {retryCount > 0 && (
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Retrying... (Attempt {retryCount}/3)
          </Typography>
        )}
      </Container>
    );
  }
  
  // Render error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="contained" 
            onClick={() => navigate('/upload')}
          >
            Return to Upload
          </Button>
          {retryCount < 3 && (
            <Button 
              variant="outlined"
              onClick={() => setRetryCount(prev => prev + 1)}
            >
              Retry
            </Button>
          )}
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Sales Forecast
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {/* Analysis Results */}
        <Box>
          <AnalysisResults 
            predictionResults={forecastData?.prediction_results} 
          />
        </Box>
        
        {/* Sales Chart */}
        <Box>
          <SalesChart 
            data={forecastData?.chart_data || []} 
            title="Monthly Sales Forecast"
          />
        </Box>
        
        {/* Model Details */}
        {forecastData?.model_details && (
          <Box>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Model Details
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
                {Object.entries(forecastData.model_details).map(([key, value]) => (
                  <Box sx={{ flex: '1 1 30%', minWidth: '250px' }} key={key}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>
                          {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </Typography>
                        <Typography variant="body2">
                          {typeof value === 'number' 
                            ? value.toFixed(4) 
                            : String(value)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default Forecast;