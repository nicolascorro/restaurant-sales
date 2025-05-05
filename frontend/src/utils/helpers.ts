// src/utils/helpers.ts

/**
 * Formats a number as a currency string
 * @param value Number to format
 * @param currency Currency code
 * @returns Formatted currency string
 */
export const formatCurrency = (value: number, currency = 'USD'): string => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency,
      minimumFractionDigits: 2
    }).format(value);
  };
  
  /**
   * Formats a date string to a more readable format
   * @param dateString Date string to format
   * @param format Format style
   * @returns Formatted date string
   */
  export const formatDate = (
    dateString: string, 
    format: 'short' | 'medium' | 'long' = 'medium'
  ): string => {
    const date = new Date(dateString);
    
    switch (format) {
      case 'short':
        return date.toLocaleDateString('en-US');
      case 'long':
        return date.toLocaleDateString('en-US', { 
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      case 'medium':
      default:
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
    }
  };
  
  /**
   * Converts a CSV string to an array of objects
   * @param csv CSV string to parse
   * @returns Array of objects representing the CSV data
   */
  export const csvToJson = (csv: string): any[] => {
    const lines = csv.split('\n');
    const result = [];
    const headers = lines[0].split(',').map(header => header.trim());
  
    for (let i = 1; i < lines.length; i++) {
      if (!lines[i]) continue;
      const obj: Record<string, string | number> = {};
      const currentLine = lines[i].split(',');
  
      for (let j = 0; j < headers.length; j++) {
        // Try to convert numeric values
        const value = currentLine[j].trim();
        obj[headers[j]] = isNaN(Number(value)) ? value : Number(value);
      }
  
      result.push(obj);
    }
  
    return result;
  };
  
  /**
   * Calculates the percentage change between two values
   * @param oldValue Original value
   * @param newValue New value
   * @returns Percentage change
   */
  export const calculatePercentageChange = (oldValue: number, newValue: number): number => {
    if (oldValue === 0) return newValue > 0 ? 100 : 0;
    return ((newValue - oldValue) / Math.abs(oldValue)) * 100;
  };
  
  /**
   * Takes an array and returns the top N items
   * @param array Array to get top items from
   * @param n Number of items to return
   * @param sortKey Key to sort by (if array contains objects)
   * @returns Top N items
   */
  export const getTopItems = <T>(array: T[], n: number, sortKey?: keyof T): T[] => {
    if (!Array.isArray(array) || array.length === 0) return [];
    
    const sortedArray = [...array].sort((a, b) => {
      if (sortKey) {
        // If sortKey is provided, use it for sorting objects
        const aValue = a[sortKey] as unknown as number;
        const bValue = b[sortKey] as unknown as number;
        return bValue - aValue; // Descending order
      } else if (typeof a === 'number' && typeof b === 'number') {
        // If array contains numbers, sort numerically
        return b - a; // Descending order
      }
      // Default case
      return 0;
    });
    
    return sortedArray.slice(0, n);
  };
  
  /**
   * Generates a random color
   * @returns Random hex color string
   */
  export const getRandomColor = (): string => {
    return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
  };
  
  /**
   * Simulates a delay (useful for testing loading states)
   * @param ms Milliseconds to delay
   * @returns Promise that resolves after the delay
   */
  export const delay = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  };