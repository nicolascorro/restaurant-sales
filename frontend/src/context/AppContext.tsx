// src/context/AppContext.tsx
import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define types
interface AppContextType {
  fileId: string | null;
  setFileId: (id: string | null) => void;
  isProcessing: boolean;
  setIsProcessing: (status: boolean) => void;
  forecastData: any | null;
  setForecastData: (data: any) => void;
  productsData: any | null;
  setProductsData: (data: any) => void;
  reportData: string | null;
  setReportData: (data: string | null) => void;
}

// Create context with default values
const AppContext = createContext<AppContextType>({
  fileId: null,
  setFileId: () => {},
  isProcessing: false,
  setIsProcessing: () => {},
  forecastData: null,
  setForecastData: () => {},
  productsData: null,
  setProductsData: () => {},
  reportData: null,
  setReportData: () => {},
});

// Create provider component
export const AppProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [fileId, setFileId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [forecastData, setForecastData] = useState<any | null>(null);
  const [productsData, setProductsData] = useState<any | null>(null);
  const [reportData, setReportData] = useState<string | null>(null);

  return (
    <AppContext.Provider
      value={{
        fileId,
        setFileId,
        isProcessing,
        setIsProcessing,
        forecastData,
        setForecastData,
        productsData,
        setProductsData,
        reportData,
        setReportData,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Create custom hook for using the context
export const useAppContext = () => useContext(AppContext);

export default AppContext;