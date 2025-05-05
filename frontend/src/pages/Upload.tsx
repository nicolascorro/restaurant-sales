// src/pages/Upload.tsx
import React from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Box
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import InfoIcon from '@mui/icons-material/Info';
import FileUpload from '../components/FileUpload';

const Upload: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Upload Restaurant Sales Data
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 3, mb: 4 }}>
        <Paper elevation={3} sx={{ p: 3, flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            <InfoIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Data Requirements
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" paragraph>
            Your CSV file should contain the following information about restaurant orders:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Order IDs and dates" 
                secondary="Each order should have a unique identifier and order date"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Food items and quantities" 
                secondary="Details of items ordered and their quantities"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Prices" 
                secondary="Unit prices and total prices for each order/item"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Food categories" 
                secondary="Categories that each food item belongs to"
              />
            </ListItem>
          </List>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
            Don't worry if your data isn't perfectly formatted - our system will clean and process it automatically.
          </Typography>
        </Paper>
        
        <Paper elevation={3} sx={{ p: 3, flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            <InfoIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            What Happens Next?
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" paragraph>
            After you upload your data, our system will:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Clean and process your data" 
                secondary="Handle missing values, normalize text fields, convert dates"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Apply machine learning models" 
                secondary="Use Linear Regression, Decision Trees, and SVM to forecast sales"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Generate visualizations" 
                secondary="Create sales forecast charts and product popularity charts"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <CheckCircleOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Create AI-powered business report" 
                secondary="Provide insights and recommendations for your restaurant"
              />
            </ListItem>
          </List>
        </Paper>
      </Box>
      
      <FileUpload />
    </Container>
  );
};

export default Upload;