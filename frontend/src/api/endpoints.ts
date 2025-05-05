// src/api/endpoints.ts
import apiClient from './index';

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const processData = async (fileId: string) => {
  const response = await apiClient.get(`/process/${fileId}`);
  return response.data;
};

export const getForecast = async (fileId: string) => {
  const response = await apiClient.get(`/forecast/${fileId}`);
  return response.data;
};

export const getTopProducts = async (fileId: string) => {
  const response = await apiClient.get(`/products/${fileId}`);
  return response.data;
};

export const generateReport = async (fileId: string) => {
  const response = await apiClient.post(`/report/${fileId}`);
  return response.data;
};