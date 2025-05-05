// src/api/index.ts
import axios from 'axios';

// Create an axios instance with default config
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // FastAPI server URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;