// src/api/index.ts
import axios from 'axios';

// default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',  // Backend URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;