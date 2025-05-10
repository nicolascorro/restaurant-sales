// src/pages/Report.tsx
import React, { useEffect, useState } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  Button,
  Box,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import RecommendIcon from '@mui/icons-material/Recommend';
import TimelineIcon from '@mui/icons-material/Timeline';
import DownloadIcon from '@mui/icons-material/Download';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { generateReport } from '../api/endpoints';

// Define interfaces for report data
interface ReportData {
  summary: string;
  insights: string[];
  recommendations: string[];
  future_outlook: string;
}

const Report: React.FC = () => {
  const navigate = useNavigate();
  const { fileId, reportData, setReportData } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  
  // Redirect if no fileId is set
  useEffect(() => {
    if (!fileId) {
      navigate('/upload');
    }
  }, [fileId, navigate]);
  
  // Generate report if needed
  useEffect(() => {
    const fetchData = async () => {
      if (fileId && (!reportData || retryCount > 0)) {
        try {
          setLoading(true);
          setError(null);
          
          const data = await generateReport(fileId);
          setReportData(JSON.stringify(data.report));
          setRetryCount(0); // Reset retry count on success
          
        } catch (err: any) {
          console.error('Error generating report:', err);
          // Extract error message from response if available
          const errorMessage = err.response?.data?.detail || 'Failed to generate business report. The server may still be processing your data. Please try again.';
          setError(errorMessage);
          
          // If the error is about required analysis, we might want to retry
          if ((errorMessage.includes("not been processed") || errorMessage.includes("Required analysis")) && retryCount < 3) {
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
  }, [fileId, reportData, setReportData, retryCount]);
  
  // Download report as PDF (placeholder function)
  const handleDownloadReport = () => {
    // This would be implemented with a library like jsPDF
    alert('Download report functionality would be implemented here');
  };
  
  // Render loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Generating AI business report...
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          This may take a few moments as we analyze your data and create insights.
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
            onClick={() => navigate('/forecast')}
          >
            View Forecast First
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
  
  // Parse the report data
  const parsedReport: ReportData = reportData ? JSON.parse(reportData) : {
    summary: "This is a placeholder for the AI-generated business summary...",
    insights: [
      "First key insight about the business trends",
      "Second key insight about customer behavior",
      "Third key insight about product performance"
    ],
    recommendations: [
      "First business recommendation based on the data",
      "Second business recommendation to improve sales",
      "Third business recommendation about inventory management"
    ],
    future_outlook: "Placeholder for future outlook analysis..."
  };
  
  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mb: 4, position: 'relative' }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Business Intelligence Report
        </Typography>
        <Typography variant="subtitle1" paragraph align="center" sx={{ mb: 3 }}>
          AI-generated insights and recommendations based on your sales data
        </Typography>
        
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleDownloadReport}
          sx={{ position: 'absolute', top: 20, right: 20 }}
        >
          Download Report
        </Button>
        
        <Divider sx={{ mb: 4 }} />
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUpIcon sx={{ mr: 1 }} /> Business Summary
          </Typography>
          <Typography variant="body1" paragraph>
            {parsedReport.summary}
          </Typography>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <LightbulbIcon sx={{ mr: 1 }} /> Key Insights
          </Typography>
          <List>
            {parsedReport.insights.map((insight: string, index: number) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Chip label={`#${index + 1}`} color="primary" size="small" />
                </ListItemIcon>
                <ListItemText primary={insight} />
              </ListItem>
            ))}
          </List>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <RecommendIcon sx={{ mr: 1 }} /> Recommendations
          </Typography>
          <List>
            {parsedReport.recommendations.map((recommendation: string, index: number) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Chip label={`#${index + 1}`} color="secondary" size="small" />
                </ListItemIcon>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        </Box>
        
        <Box>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TimelineIcon sx={{ mr: 1 }} /> Future Outlook
          </Typography>
          <Typography variant="body1" paragraph>
            {parsedReport.future_outlook}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Report;