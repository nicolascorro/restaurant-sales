// src/components/SalesChart.tsx
import React, { useRef } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  Typography, 
  Paper, 
  Box, 
  Button,
  Menu,
  MenuItem
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { downloadAsImage, downloadAsPDF } from '../utils/downloadUtils';

interface SalesChartProps {
  data: any[];
  title?: string;
}

const SalesChart: React.FC<SalesChartProps> = ({ 
  data, 
  title = 'Monthly Sales Forecast'
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  
  const handleDownloadClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleDownloadClose = () => {
    setAnchorEl(null);
  };
  
  const handleDownloadImage = () => {
    downloadAsImage(chartRef.current, 'sales-forecast');
    handleDownloadClose();
  };
  
  const handleDownloadPDF = () => {
    downloadAsPDF(chartRef.current, 'sales-forecast', title);
    handleDownloadClose();
  };
  
  // If no data is available, show placeholder
  if (!data || data.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h6" color="textSecondary">
          No forecast data available
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }} ref={chartRef}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{title}</Typography>
        
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          onClick={handleDownloadClick}
          size="small"
        >
          Download
        </Button>
        
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleDownloadClose}
          MenuListProps={{
            'aria-labelledby': 'download-button',
          }}
        >
          <MenuItem onClick={handleDownloadImage}>Download as PNG</MenuItem>
          <MenuItem onClick={handleDownloadPDF}>Download as PDF</MenuItem>
        </Menu>
      </Box>
      
      <Box sx={{ height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip formatter={(value) => [`$${value}`, 'Revenue']} />
            <Legend />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#8884d8"
              name="Historical Sales"
              dot={true}
              activeDot={{ r: 8 }}
            />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#82ca9d"
              name="Predicted Sales"
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default SalesChart;