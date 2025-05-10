// src/components/ProductsChart.tsx
import React, { useRef } from 'react';
import { 
  PieChart, 
  Pie, 
  Cell, 
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

interface ProductsChartProps {
  data: any[];
  title?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ProductsChart: React.FC<ProductsChartProps> = ({ 
  data, 
  title = 'Best-Selling Products'
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
    downloadAsImage(chartRef.current, 'top-products');
    handleDownloadClose();
  };
  
  const handleDownloadPDF = () => {
    downloadAsPDF(chartRef.current, 'top-products', title);
    handleDownloadClose();
  };

  // If no data is available, show placeholder
  if (!data || data.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="h6" color="textSecondary">
          No product data available
        </Typography>
      </Paper>
    );
  }

  // Custom tooltip formatter
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="subtitle2">{item.name}</Typography>
          <Typography variant="body2">Revenue: ${item.value.toFixed(2)}</Typography>
          <Typography variant="body2">Percentage: {item.percent.toFixed(2)}%</Typography>
        </Paper>
      );
    }
    return null;
  };

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
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={150}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            >
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default ProductsChart;