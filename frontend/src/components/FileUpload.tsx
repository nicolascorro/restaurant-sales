// src/components/FileUpload.tsx
import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress,
  Alert 
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadFile, processData } from '../api/endpoints';
import { useAppContext } from '../context/AppContext';

const FileUpload: React.FC = () => {
  const { setFileId, setIsProcessing, isProcessing } = useAppContext();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      
      // Check if file is CSV
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please upload a CSV file');
        setFile(null);
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      
      // Upload file to server
      const uploadResponse = await uploadFile(file);
      const uploadedFileId = uploadResponse.file_id;
      
      setSuccess('File uploaded successfully. Processing data...');
      
      // Process the uploaded file
      await processData(uploadedFileId);
      
      // Update context with file ID
      setFileId(uploadedFileId);
      setSuccess('Data processed successfully!');
      
    } catch (err) {
      console.error('Error uploading file:', err);
      setError('Error uploading or processing file. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom align="center">
        Upload Restaurant Sales Data
      </Typography>
      
      <Typography variant="body2" color="textSecondary" paragraph align="center">
        Upload a CSV file containing your restaurant sales data to generate predictions and insights.
      </Typography>
      
      <Box
        sx={{
          border: '2px dashed #ccc',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          mb: 3,
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
          },
        }}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          type="file"
          id="file-input"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          accept=".csv"
        />
        <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 1 }} />
        <Typography variant="body1" gutterBottom>
          {file ? file.name : 'Click to select a CSV file'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Only CSV files are supported
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}
      
      <Button
        variant="contained"
        fullWidth
        disabled={!file || isProcessing}
        onClick={handleUpload}
        startIcon={isProcessing ? <CircularProgress size={20} color="inherit" /> : null}
      >
        {isProcessing ? 'Processing...' : 'Upload & Process Data'}
      </Button>
    </Paper>
  );
};

export default FileUpload;