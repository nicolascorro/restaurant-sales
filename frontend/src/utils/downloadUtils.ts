// src/utils/downloadUtils.ts
import { toPng, toJpeg } from 'html-to-image';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { ProductDetail } from '../types';


 //Converts an HTML element to a PNG and downloads it

export const downloadAsImage = async (
  element: HTMLElement | null,
  fileName: string
): Promise<void> => {
  if (!element) {
    console.error('Element not found');
    return;
  }

  try {
    // Use original dimensions
    const dataUrl = await toPng(element, {
      quality: 0.95,
      backgroundColor: '#FFFFFF',
    });

    // Create a link element to trigger download
    const link = document.createElement('a');
    link.download = `${fileName}.png`;
    link.href = dataUrl;
    link.click();
  } catch (error) {
    console.error('Error downloading image:', error);
  }
};


 //Converts an HTML element to a PDF and downloads it

export const downloadAsPDF = async (
  element: HTMLElement | null,
  fileName: string,
  title?: string
): Promise<void> => {
  if (!element) {
    console.error('Element not found');
    return;
  }

  try {
    // First convert the element to an image
    const dataUrl = await toJpeg(element, {
      quality: 0.95,
      backgroundColor: '#FFFFFF',
    });

    // Create a new PDF document
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
    });

    // Add title if provided
    if (title) {
      pdf.setFontSize(16);
      pdf.text(title, 105, 15, { align: 'center' });
      pdf.setFontSize(12);
    }

    // Get the dimensions of the PDF page
    const pageWidth = pdf.internal.pageSize.getWidth();
    
    // Create an Image element to get dimensions
    const img = new Image();
    img.src = dataUrl;
    
    // Add the image when it's loaded
    img.onload = () => {
      // Calculate proper dimensions
      const pdfWidth = pageWidth - 20; // margins
      const pdfHeight = (img.height * pdfWidth) / img.width;
      
      // Add the image to the PDF
      pdf.addImage(dataUrl, 'JPEG', 10, title ? 25 : 10, pdfWidth, pdfHeight);
      
      // Save the PDF
      pdf.save(`${fileName}.pdf`);
    };

  } catch (error) {
    console.error('Error downloading PDF:', error);
  }
};

 //Generates a report PDF from text content
export const downloadReportAsPDF = (
  reportData: {
    summary: string;
    insights: string[];
    recommendations: string[];
    future_outlook: string;
  },
  fileName: string
): void => {
  // Create a new PDF document
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
  });

  // Add title
  pdf.setFontSize(18);
  pdf.text('Business Intelligence Report', 105, 15, { align: 'center' });

  // Add current date
  const currentDate = new Date().toLocaleDateString();
  pdf.setFontSize(10);
  pdf.text(`Generated on: ${currentDate}`, 105, 22, { align: 'center' });

  // Add divider
  pdf.setDrawColor(200, 200, 200);
  pdf.line(10, 25, 200, 25);

  let yPosition = 35;

  // Add summary
  pdf.setFontSize(14);
  pdf.text('Business Summary', 10, yPosition);
  yPosition += 8;
  pdf.setFontSize(11);
  
  // Split long text into multiple lines
  const splitSummary = pdf.splitTextToSize(reportData.summary, 180);
  pdf.text(splitSummary, 10, yPosition);
  yPosition += (splitSummary.length * 6) + 10;

  // Add insights
  pdf.setFontSize(14);
  pdf.text('Key Insights', 10, yPosition);
  yPosition += 8;
  pdf.setFontSize(11);
  
  reportData.insights.forEach((insight, index) => {
    const insightText = `${index + 1}. ${insight}`;
    const splitInsight = pdf.splitTextToSize(insightText, 180);
    pdf.text(splitInsight, 10, yPosition);
    yPosition += (splitInsight.length * 6) + 5;
  });
  
  yPosition += 5;

  // Add recommendations
  pdf.setFontSize(14);
  pdf.text('Recommendations', 10, yPosition);
  yPosition += 8;
  pdf.setFontSize(11);
  
  reportData.recommendations.forEach((recommendation, index) => {
    const recText = `${index + 1}. ${recommendation}`;
    const splitRec = pdf.splitTextToSize(recText, 180);
    
    // Check if we need a new page
    if (yPosition + (splitRec.length * 6) > 270) {
      pdf.addPage();
      yPosition = 20;
    }
    
    pdf.text(splitRec, 10, yPosition);
    yPosition += (splitRec.length * 6) + 5;
  });
  
  yPosition += 5;

  // Add future outlook
  if (yPosition > 240) {
    pdf.addPage();
    yPosition = 20;
  }
  
  pdf.setFontSize(14);
  pdf.text('Future Outlook', 10, yPosition);
  yPosition += 8;
  pdf.setFontSize(11);
  
  const splitOutlook = pdf.splitTextToSize(reportData.future_outlook, 180);
  pdf.text(splitOutlook, 10, yPosition);

  // Add footer with page numbers
  const pageCount = pdf.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    pdf.setPage(i);
    pdf.setFontSize(10);
    pdf.text(`Page ${i} of ${pageCount}`, 105, 287, { align: 'center' });
  }

  // Save the PDF
  pdf.save(`${fileName}.pdf`);
};


 // Converts product data to CSV and downloads it

export const downloadProductsAsCSV = (
  productDetails: ProductDetail[],
  fileName: string
): void => {
  // Create CSV header
  let csvContent = "Rank,Name,Category,Revenue,Quantity,Contribution(%)\n";
  
  // Add data rows
  productDetails.forEach((product, index) => {
    const row = [
      index + 1,
      `"${product.name}"`,
      `"${product.category}"`,
      product.revenue.toFixed(2),
      product.quantity,
      product.percentage.toFixed(2)
    ].join(',');
    
    csvContent += row + "\n";
  });
  
  // Create a Blob with the CSV content
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  
  // Create a download link
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', `${fileName}.csv`);
  link.style.visibility = 'hidden';
  
  // Append to the document, click and remove
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};