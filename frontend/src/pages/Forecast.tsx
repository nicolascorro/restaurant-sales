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
import DownloadIcon from '@mui/icons-material/Download';
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
  
  // Redirect if no fileId is set
  useEffect(() => {
    if (!fileId) {
      navigate('/upload');
    }
  }, [fileId, navigate]);
  
  // Fetch forecast data if needed
  useEffect(() => {
    const fetchData = async () => {
      if (fileId && !forecastData) {
        try {
          setLoading(true);
          setError(null);
          
          const data = await getForecast(fileId);
          setForecastData(data);
          
        } catch (err) {
          console.error('Error fetching forecast data:', err);
          setError('Failed to load forecast data. Please try again.');
        } finally {
          setLoading(false);
        }
      }
    };
    
    fetchData();
  }, [fileId, forecastData, setForecastData]);
  
  // Download chart as image (placeholder function)
  const handleDownloadChart = () => {
    // This would be implemented with a library like html2canvas
    alert('Download chart functionality would be implemented here');
  };
  
  // Render loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Generating sales forecast...
        </Typography>
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
        <Button 
          variant="contained" 
          onClick={() => navigate('/upload')}
        >
          Return to Upload
        </Button>
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
          <Box sx={{ position: 'relative' }}>
            <SalesChart 
              data={forecastData?.chart_data || []} 
              title="Monthly Sales Forecast"
            />
            
            {forecastData && (
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadChart}
                sx={{ position: 'absolute', top: 16, right: 16 }}
              >
                Download Chart
              </Button>
            )}
          </Box>
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