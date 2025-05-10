// src/pages/Report.tsx
import React, { useEffect, useState, useRef } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  Button,
  Box,
  Divider,
  Chip,
  Menu,
  MenuItem,
  Tooltip,
  Card,
  CardContent
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import RecommendIcon from '@mui/icons-material/Recommend';
import TimelineIcon from '@mui/icons-material/Timeline';
import DownloadIcon from '@mui/icons-material/Download';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { generateReport } from '../api/endpoints';
import { downloadAsPDF, downloadReportAsPDF } from '../utils/downloadUtils';

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
  
  const reportRef = useRef<HTMLDivElement>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  
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
          const errorMessage = err.response?.data?.detail || 'Failed to generate AI business report. The server may still be processing your data. Please try again.';
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
  
  // Handle download menu
  const handleMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleMenuClose = () => {
    setAnchorEl(null);
  };
  
  const handleDownloadAsImage = () => {
    downloadAsPDF(reportRef.current, 'ai-business-report', 'AI Business Intelligence Report');
    handleMenuClose();
  };
  
  const handleDownloadAsPDF = () => {
    // Parse the report data
    if (reportData) {
      const parsedReport: ReportData = JSON.parse(reportData);
      downloadReportAsPDF(parsedReport, 'ai-business-report');
    }
    handleMenuClose();
  };
  
  // Render loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          AI is analyzing your data and generating insights... <br/>
          Please wait 1-5 minutes.
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          Our AI is examining your sales patterns, product performance, and forecasts to create a comprehensive business report.
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
      <Paper elevation={3} sx={{ p: 4, mb: 4, position: 'relative' }} ref={reportRef}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
          <RocketLaunchIcon sx={{ color: 'primary.main', fontSize: 28, mr: 1 }} />
          <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 0 }}>
            AI Business Intelligence Report
          </Typography>
        </Box>
        <Typography variant="subtitle1" paragraph align="center" sx={{ mb: 3 }}>
          Data-driven insights and recommendations generated by artificial intelligence
        </Typography>
        
        <Box sx={{ position: 'absolute', top: 20, right: 20 }}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleMenuClick}
          >
            Download Report
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            MenuListProps={{
              'aria-labelledby': 'download-button',
            }}
          >
            <MenuItem onClick={handleDownloadAsImage}>
              <PictureAsPdfIcon fontSize="small" sx={{ mr: 1 }} />
              Download as Enhanced PDF
            </MenuItem>
            <MenuItem onClick={handleDownloadAsPDF}>
              <PictureAsPdfIcon fontSize="small" sx={{ mr: 1 }} />
              Download as PDF Document
            </MenuItem>
          </Menu>
        </Box>
        
        <Divider sx={{ mb: 4 }} />
        
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TrendingUpIcon sx={{ color: 'primary.main', fontSize: 24, mr: 1 }} />
            <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>
              Business Summary
            </Typography>
            <Tooltip title="AI-generated overview of your restaurant's performance based on sales data analysis">
              <HelpOutlineIcon sx={{ ml: 1, color: 'text.secondary', fontSize: 18 }} />
            </Tooltip>
          </Box>
          <Typography variant="body1" paragraph>
            {parsedReport.summary}
          </Typography>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <LightbulbIcon sx={{ color: 'primary.main', fontSize: 24, mr: 1 }} />
            <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>
              Key Insights
            </Typography>
            <Tooltip title="Data-driven findings about your sales patterns and product performance">
              <HelpOutlineIcon sx={{ ml: 1, color: 'text.secondary', fontSize: 18 }} />
            </Tooltip>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {parsedReport.insights.map((insight: string, index: number) => (
              <Card variant="outlined" key={index} sx={{ flex: '1 1 45%', minWidth: 250 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                    <Chip 
                      label={`#${index + 1}`} 
                      color="primary" 
                      size="small" 
                      sx={{ mr: 1, mt: 0.5 }}
                    />
                    <Typography variant="body1">{insight}</Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <RecommendIcon sx={{ color: 'primary.main', fontSize: 24, mr: 1 }} />
            <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>
              AI Recommendations
            </Typography>
            <Tooltip title="Strategic action items to improve your restaurant's performance">
              <HelpOutlineIcon sx={{ ml: 1, color: 'text.secondary', fontSize: 18 }} />
            </Tooltip>
          </Box>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {parsedReport.recommendations.map((recommendation: string, index: number) => (
              <Card variant="outlined" key={index} sx={{ flex: '1 1 45%', minWidth: 250 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                    <Chip 
                      label={`#${index + 1}`} 
                      color="secondary" 
                      size="small" 
                      sx={{ mr: 1, mt: 0.5 }}
                    />
                    <Typography variant="body1">{recommendation}</Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        </Box>
        
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <TimelineIcon sx={{ color: 'primary.main', fontSize: 24, mr: 1 }} />
            <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>
              Future Outlook
            </Typography>
            <Tooltip title="Projected trends and business forecast based on data analysis">
              <HelpOutlineIcon sx={{ ml: 1, color: 'text.secondary', fontSize: 18 }} />
            </Tooltip>
          </Box>
          <Paper elevation={1} sx={{ p: 3, bgcolor: 'background.default', borderLeft: '4px solid', borderColor: 'primary.main' }}>
            <Typography variant="body1" paragraph>
              {parsedReport.future_outlook}
            </Typography>
          </Paper>
        </Box>
        
        <Box sx={{ mt: 4, pt: 3, borderTop: '1px dashed rgba(0, 0, 0, 0.12)' }}>
          <Typography variant="caption" color="text.secondary" align="center" display="block">
            This report was generated by an AI assistant analyzing your restaurant's sales data.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Report;