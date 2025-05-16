// src/api/index.ts
import axios from 'axios';

const getBaseUrl = () => {
  if (import.meta.env.MODE === 'production') {
    return 'https://restaurant-sales.onrender.com';  // Production backend URL
  }
  return '/api';  // In development, it uses relative URLs that go through the Vite proxy
};

// default config
const apiClient = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;