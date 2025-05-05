// src/components/common/Header.tsx
import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box,
  useTheme
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import { useAppContext } from '../../context/AppContext';

const Header: React.FC = () => {
  const theme = useTheme();
  const { fileId } = useAppContext();
  
  // Navigation links - if fileId not set, only show Home and Upload
  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Upload Data', path: '/upload' },
    // Only show these if a file has been uploaded & processed
    ...(fileId ? [
      { name: 'Sales Forecast', path: '/forecast' },
      { name: 'Top Products', path: '/products' },
      { name: 'Report', path: '/report' }
    ] : [])
  ];

  return (
    <AppBar position="static" sx={{ mb: 3 }}>
      <Toolbar>
        <RestaurantIcon sx={{ mr: 1 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Restaurant Sales Prediction
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navLinks.map((link) => (
            <Button
              key={link.name}
              component={RouterLink}
              to={link.path}
              color="inherit"
              sx={{ 
                '&:hover': {
                  backgroundColor: theme.palette.primary.dark,
                },
              }}
            >
              {link.name}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;