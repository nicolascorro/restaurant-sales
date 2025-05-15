// src/pages/Products.tsx
import React, { useEffect, useState, useRef } from 'react';
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
  Divider,
  Menu,
  MenuItem
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import ProductsChart from '../components/ProductsChart';
import { getTopProducts } from '../api/endpoints';
import { downloadAsImage, downloadAsPDF, downloadProductsAsCSV } from '../utils/downloadUtils';
import { ProductDetail } from '../types/ProductDetail';

const Products: React.FC = () => {
  const navigate = useNavigate();
  const { fileId, productsData, setProductsData } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  // For download menu
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

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

  // Handle table download menu
  const handleTableMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleTableMenuClose = () => {
    setAnchorEl(null);
  };

  const handleDownloadTableImage = () => {
    downloadAsImage(tableRef.current, 'product-details');
    handleTableMenuClose();
  };

  const handleDownloadTablePDF = () => {
    downloadAsPDF(tableRef.current, 'product-details', 'Product Details');
    handleTableMenuClose();
  };

  const handleDownloadTableCSV = () => {
    if (productsData?.product_details) {
      downloadProductsAsCSV(productsData.product_details, 'product-details');
    }
    handleTableMenuClose();
  };

  // Render loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ textAlign: 'center', py: 8 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Analyzing product sales data... Please wait while we crunch the numbers.<br />
          <br />
          Processing time depends on your file size: <br />
          - Small files: 1-2 minutes <br />
          - Medium files: 5-10 minutes <br />
          - Large files: 15+ minutes <br />
          <br />
          We're identifying your best-selling products and preparing detailed visualizations.
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
            <ProductsChart
              data={productsData?.chart_data || []}
              title="Revenue Contribution by Product"
            />
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
          <Paper elevation={3} sx={{ p: 3 }} ref={tableRef}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Product Details
              </Typography>

              {productsData?.product_details && productsData.product_details.length > 0 && (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleTableMenuClick}
                    size="small"
                  >
                    Download
                  </Button>

                  <Menu
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleTableMenuClose}
                    MenuListProps={{
                      'aria-labelledby': 'download-button',
                    }}
                  >
                    <MenuItem onClick={handleDownloadTableImage}>Download as PNG</MenuItem>
                    <MenuItem onClick={handleDownloadTablePDF}>Download as PDF</MenuItem>
                    <MenuItem onClick={handleDownloadTableCSV}>Download as CSV</MenuItem>
                  </Menu>
                </>
              )}
            </Box>

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