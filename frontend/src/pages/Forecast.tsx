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
import InfoIcon from '@mui/icons-material/Info';
import IconButton from '@mui/material/IconButton';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Tooltip from '@mui/material/Tooltip';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
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
  const [helpOpen, setHelpOpen] = useState(false);

  // Redirect if no fileId is set
  useEffect(() => {
    if (!fileId) {
      navigate('/upload');
    }
  }, [fileId, navigate]);

  const handleHelpOpen = () => {
    setHelpOpen(true);
  };
  
  const handleHelpClose = () => {
    setHelpOpen(false);
  };

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
          Hang tight! We’re generating your sales forecast. <br />
          <br />
          - Small files (under 1,000 rows): ~1-2 minutes <br />
          - Medium files (1,000-10,000 rows): ~5-10 minutes <br />
          - Large files (over 10,000 rows): ~15-20+ minutes <br />
          <br />
          Grab a coffee while our system analyzes your data. The results will be worth the wait!
        </Typography>
        {retryCount > 0 && (
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            Retrying... (Attempt {retryCount}/3)
          </Typography>
        )}
      </Container>
    );
  }

  const ModelMetricsHelp = () => (
    <Dialog
      open={helpOpen}
      onClose={handleHelpClose}
      aria-labelledby="metrics-help-dialog"
      maxWidth="md"
    >
      <DialogTitle id="metrics-help-dialog">Understanding Model Metrics</DialogTitle>
      <DialogContent>
        <Typography variant="body1" paragraph>
          These metrics help you understand how accurate the sales forecasting is. Here's a simple explanation of what each metric means:
        </Typography>
        
        <TableContainer component={Paper} sx={{ mb: 3 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Metric</strong></TableCell>
                <TableCell><strong>What it means</strong></TableCell>
                <TableCell><strong>What's a good value?</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>RMSE (Root Mean Square Error)</TableCell>
                <TableCell>
                  The average error in your sales predictions (in the same units as your sales figures). 
                  Lower values mean more accurate predictions.
                </TableCell>
                <TableCell>
                  ✅ Lower is better<br />
                  Ideally, less than 10% of your average sales value
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>R² (R-squared)</TableCell>
                <TableCell>
                  Measures how well the model explains variations in sales. 
                  Ranges from 0 to 1, with 1 meaning perfect predictions.
                </TableCell>
                <TableCell>
                  ✅ Higher is better<br />
                  &gt; 0.7: Excellent<br />
                  0.5 - 0.7: Good<br />
                  0.3 - 0.5: Fair<br />
                  &lt; 0.3: Poor
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Model Type</TableCell>
                <TableCell>
                  The algorithm used to make predictions. Different models work better for different patterns.
                </TableCell>
                <TableCell>
                  No "best" type - the system automatically selects the one that works best for your data
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Training Time</TableCell>
                <TableCell>
                  How long it took to analyze your data and create the prediction model.
                </TableCell>
                <TableCell>
                  Not a quality indicator - just informational
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
        
        <Typography variant="subtitle1" gutterBottom>
          In Plain Language:
        </Typography>
        <Typography variant="body1" paragraph>
          • If R² is close to 1.0, our predictions are very reliable<br />
          • If RMSE is small compared to your typical sales numbers, predictions are accurate<br />
          • The system automatically chose the best model type for your specific data
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleHelpClose}>Got it</Button>
      </DialogActions>
    </Dialog>
  );

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
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Model Details
              </Typography>
              <Tooltip title="What do these metrics mean?">
                <IconButton onClick={handleHelpOpen} size="small" color="primary">
                  <InfoIcon />
                </IconButton>
              </Tooltip>
            </Box>
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
          <ModelMetricsHelp />
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default Forecast;