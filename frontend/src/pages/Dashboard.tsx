// src/pages/Dashboard.tsx
import React from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  Button,
  Box,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import BarChartIcon from '@mui/icons-material/BarChart';
import PieChartIcon from '@mui/icons-material/PieChart';
import DescriptionIcon from '@mui/icons-material/Description';
import { useAppContext } from '../context/AppContext';

const Dashboard: React.FC = () => {
  const { fileId } = useAppContext();
  
  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Restaurant Sales Prediction Application
        </Typography>
        <Typography variant="subtitle1" paragraph align="center">
          Upload your restaurant sales data to get accurate forecasts, identify top-selling products,
          and receive AI-generated business insights.
        </Typography>
      </Paper>
      
      {!fileId ? (
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            mt: 4
          }}
        >
          <Typography variant="h5" gutterBottom>
            Get Started
          </Typography>
          <Typography variant="body1" paragraph align="center" sx={{ maxWidth: 600, mb: 3 }}>
            To begin analyzing your restaurant sales, you need to upload a CSV file 
            containing your order history data.
          </Typography>
          <Button
            component={RouterLink}
            to="/upload"
            variant="contained"
            size="large"
            startIcon={<FileUploadIcon />}
          >
            Upload Sales Data
          </Button>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
          {/* Sales Forecast Card */}
          <Box sx={{ flex: '1 1 30%', minWidth: '280px' }}>
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <BarChartIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                </Box>
                <Typography variant="h5" gutterBottom align="center">
                  Sales Forecast
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph align="center">
                  View monthly sales predictions and analyze revenue trends
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button 
                  component={RouterLink} 
                  to="/forecast" 
                  variant="outlined" 
                  color="primary"
                >
                  View Forecast
                </Button>
              </CardActions>
            </Card>
          </Box>
          
          {/* Top Products Card */}
          <Box sx={{ flex: '1 1 30%', minWidth: '280px' }}>
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <PieChartIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                </Box>
                <Typography variant="h5" gutterBottom align="center">
                  Top Products
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph align="center">
                  Discover your best-selling products and their contribution to revenue
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button 
                  component={RouterLink} 
                  to="/products" 
                  variant="outlined" 
                  color="primary"
                >
                  View Products
                </Button>
              </CardActions>
            </Card>
          </Box>
          
          {/* Business Report Card */}
          <Box sx={{ flex: '1 1 30%', minWidth: '280px' }}>
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <DescriptionIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                </Box>
                <Typography variant="h5" gutterBottom align="center">
                  Business Report
                </Typography>
                <Typography variant="body2" color="textSecondary" paragraph align="center">
                  Get AI-generated insights and recommendations for your restaurant
                </Typography>
              </CardContent>
              <CardActions sx={{ justifyContent: 'center', pb: 2 }}>
                <Button 
                  component={RouterLink} 
                  to="/report" 
                  variant="outlined" 
                  color="primary"
                >
                  View Report
                </Button>
              </CardActions>
            </Card>
          </Box>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;