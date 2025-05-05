// src/pages/Products.tsx
import React, { useEffect, useState } from 'react';
import { 
  Container, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import ProductsChart from '../components/ProductsChart';
import { getTopProducts } from '../api/endpoints';

// Define interface for product details
interface ProductDetail {
  name: string;
  category: string;
  revenue: number;
  quantity: number;
  percentage: number;
}

const Products: React.FC = () => {
  const navigate = useNavigate();
  const { fileId, productsData, setProductsData } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Redirect if no fileId is set
  useEffect(() => {
    if (!fileId) {
      navigate('/upload');
    }
  }, [fileId, navigate]);
  
  // Fetch products data if needed
  useEffect(() => {
    const fetchData = async () => {
      if (fileId && !productsData) {
        try {
          setLoading(true);
          setError(null);
          
          const data = await getTopProducts(fileId);
          setProductsData(data);
          
        } catch (err) {
          console.error('Error fetching products data:', err);
          setError('Failed to load product data. Please try again.');
        } finally {
          setLoading(false);
        }
      }
    };
    
    fetchData();
  }, [fileId, productsData, setProductsData]);
  
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
          Analyzing product sales data...
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
        Best-Selling Products
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {/* Chart and Summary Section */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {/* Products Chart */}
          <Box sx={{ flex: '1 1 45%', minWidth: '300px' }}>
            <Box sx={{ position: 'relative' }}>
              <ProductsChart 
                data={productsData?.chart_data || []} 
                title="Revenue Contribution by Product"
              />
              
              {productsData && (
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
          
          {/* Product Performance Summary */}
          <Box sx={{ flex: '1 1 45%', minWidth: '300px' }}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Product Performance Summary
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              {productsData?.summary ? (
                <>
                  <Typography variant="body1" paragraph>
                    {productsData.summary.total_products} distinct products were analyzed.
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Top 5 products account for {productsData.summary.top_five_percentage.toFixed(1)}% of total revenue.
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Most popular category: {productsData.summary.top_category} 
                    ({productsData.summary.top_category_percentage.toFixed(1)}% of sales)
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Highest profit margin product: {productsData.summary.highest_margin_product}
                  </Typography>
                </>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No product summary data available
                </Typography>
              )}
            </Paper>
          </Box>
        </Box>
        
        {/* Product Details Table */}
        <Box>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Product Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {productsData?.product_details && productsData.product_details.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Rank</TableCell>
                      <TableCell>Product Name</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Total Revenue</TableCell>
                      <TableCell align="right">Quantity Sold</TableCell>
                      <TableCell align="right">Contribution (%)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {productsData.product_details.map((product: ProductDetail, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{index + 1}</TableCell>
                        <TableCell>{product.name}</TableCell>
                        <TableCell>{product.category}</TableCell>
                        <TableCell align="right">${product.revenue.toFixed(2)}</TableCell>
                        <TableCell align="right">{product.quantity}</TableCell>
                        <TableCell align="right">{product.percentage.toFixed(2)}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No product details available
              </Typography>
            )}
          </Paper>
        </Box>
      </Box>
    </Container>
  );
};

export default Products;