# File: backend/services/ai_report_generation.py
"""
AI-powered report generation using Anthropic's Claude API.
Creates business insights based on analysis results.
"""
import os
import json
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv

class AIReportGenerator:
    """Generates business insights reports using Claude."""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.claude_api_url = "https://api.anthropic.com/v1/messages"
        
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
    
    def generate_report(self, forecast_data: Dict[str, Any], products_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates comprehensive report based on chart data and analysis results.
        
        Args:
            forecast_data: Dictionary containing sales forecast data
            products_data: Dictionary containing product performance data
            
        Returns:
            Dictionary with the AI-generated report
        """
        if not self.api_key:
            return self._generate_fallback_report(forecast_data, products_data)
        
        try:
            # Format input data for the AI
            prompt = self._construct_ai_prompt(forecast_data, products_data)
            
            # Call Claude API
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": "claude-3-opus-20240229",
                "max_tokens": 1500,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "system": "You are a business analyst specializing in restaurant sales data analysis. Provide specific, data-driven insights based on the information provided."
            }
            
            response = requests.post(
                self.claude_api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                print(f"Error from Claude API: {response.status_code}")
                print(response.text)
                return self._generate_fallback_report(forecast_data, products_data)
            
            # Parse the response
            response_data = response.json()
            report_text = response_data["content"][0]["text"]
            
            # Split the report into sections based on headers
            report = self._parse_ai_response(report_text)
            
            return report
            
        except Exception as e:
            print(f"Error generating AI report: {str(e)}")
            return self._generate_fallback_report(forecast_data, products_data)
    
    def _construct_ai_prompt(self, forecast_data: Dict[str, Any], products_data: Dict[str, Any]) -> str:
        """Constructs a detailed prompt for the AI based on data."""
        
        # Convert data to readable format for AI
        prompt = "Generate a detailed restaurant business report based on the following sales and product data:\n\n"
        
        # Add sales forecast data
        if forecast_data:
            prompt += "## SALES FORECAST DATA\n"
            
            # Add prediction results summary
            if "prediction_results" in forecast_data and "prediction_summary" in forecast_data["prediction_results"]:
                summary = forecast_data["prediction_results"]["prediction_summary"]
                prompt += f"- Average predicted daily sales: ${summary.get('avg_predicted_sales', 0):.2f}\n"
                prompt += f"- Highest sales day: {summary.get('max_predicted_day', '')}, Amount: ${summary.get('max_predicted_value', 0):.2f}\n"
                prompt += f"- Lowest sales day: {summary.get('min_predicted_day', '')}, Amount: ${summary.get('min_predicted_value', 0):.2f}\n"
                prompt += f"- Sales trend: {summary.get('trend', 'stable')}, Change: {summary.get('trend_percentage', 0):.1f}%\n\n"
            
            # Add best model information
            if "prediction_results" in forecast_data and "best_model" in forecast_data["prediction_results"]:
                best_model = forecast_data["prediction_results"]["best_model"]
                prompt += f"- Best prediction model: {best_model.get('model_type', '').replace('_', ' ')}\n"
                prompt += f"- Model accuracy: {best_model.get('accuracy_score', 0) * 100:.1f}%\n\n"
            
            # Add chart data summary if available
            if "chart_data" in forecast_data and forecast_data["chart_data"]:
                chart_data = forecast_data["chart_data"]
                prompt += "- Sales data points:\n"
                
                # Limit to first 10 points to avoid overwhelming the AI
                for i, data_point in enumerate(chart_data[:10]):
                    prompt += f"  - {data_point.get('date', '')}: Actual ${data_point.get('actual', 0):.2f}, Predicted ${data_point.get('predicted', 0):.2f}\n"
                
                if len(chart_data) > 10:
                    prompt += f"  - (Plus {len(chart_data) - 10} more data points...)\n\n"
        
        # Add product data
        if products_data:
            prompt += "## PRODUCT PERFORMANCE DATA\n"
            
            # Add product summary
            if "summary" in products_data:
                summary = products_data["summary"]
                prompt += f"- Total unique products: {summary.get('total_products', 0)}\n"
                prompt += f"- Top 5 products percentage: {summary.get('top_five_percentage', 0):.1f}%\n"
                prompt += f"- Top category: {summary.get('top_category', '')}, Percentage: {summary.get('top_category_percentage', 0):.1f}%\n"
                prompt += f"- Highest margin product: {summary.get('highest_margin_product', '')}\n\n"
            
            # Add top products data
            if "product_details" in products_data and products_data["product_details"]:
                prompt += "- Top products (revenue):\n"
                
                # List top 5 products for brevity
                top_products = products_data["product_details"][:5]
                for i, product in enumerate(top_products):
                    prompt += f"  - #{i+1}: {product.get('name', '')}, Category: {product.get('category', '')}, Revenue: ${product.get('revenue', 0):.2f}, Percentage: {product.get('percentage', 0):.1f}%\n"
        
        # instructions for the AI
        prompt += "\n## REPORT STRUCTURE\n"
        prompt += "Please generate a comprehensive business report with the following sections:\n"
        prompt += "1. SUMMARY: A concise overview of the restaurant's sales performance and key findings.\n"
        prompt += "2. KEY_INSIGHTS: 4-6 specific, data-backed insights from the sales and product data.\n"
        prompt += "3. RECOMMENDATIONS: 4-6 actionable recommendations for improving sales and business performance.\n"
        prompt += "4. FUTURE_OUTLOOK: Projections for future performance and potential challenges/opportunities.\n\n"
        prompt += "Use clear section headings and ensure recommendations are specific to this restaurant's data."
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parses AI response into structured sections."""
        
        # Initialize sections
        report = {
            "summary": "",
            "insights": [],
            "recommendations": [],
            "future_outlook": ""
        }
        
        # Extract sections using headers as delimiters
        current_section = None
        section_text = ""
        
        for line in response_text.split('\n'):
            # Check for section headers
            lower_line = line.lower()
            
            if "summary" in lower_line and (":" in line or "#" in line):
                if current_section and section_text:
                    self._update_report_section(report, current_section, section_text)
                current_section = "summary"
                section_text = ""
            elif any(keyword in lower_line for keyword in ["key insights", "insights", "key_insights"]) and (":" in line or "#" in line):
                if current_section and section_text:
                    self._update_report_section(report, current_section, section_text)
                current_section = "insights"
                section_text = ""
            elif any(keyword in lower_line for keyword in ["recommendations", "recommendation"]) and (":" in line or "#" in line):
                if current_section and section_text:
                    self._update_report_section(report, current_section, section_text)
                current_section = "recommendations"
                section_text = ""
            elif any(keyword in lower_line for keyword in ["future outlook", "outlook", "projection", "future_outlook"]) and (":" in line or "#" in line):
                if current_section and section_text:
                    self._update_report_section(report, current_section, section_text)
                current_section = "future_outlook"
                section_text = ""
            elif current_section:
                # Add line to current section
                if line.strip():  # Ignore empty lines
                    section_text += line + "\n"
        
        # Add the last section
        if current_section and section_text:
            self._update_report_section(report, current_section, section_text)
        
        # Clean up the report
        self._clean_report(report)
        
        return report
    
    def _update_report_section(self, report: Dict[str, Any], section: str, text: str) -> None:
        """Updates the report with content from a section."""
        
        if section in ["summary", "future_outlook"]:
            report[section] = text.strip()
        elif section in ["insights", "recommendations"]:
            # Process list items
            items = []
            current_item = ""
            
            # Split by lines and process
            for line in text.split('\n'):
                stripped_line = line.strip()
                
                # Skip empty lines
                if not stripped_line:
                    continue
                
                # Check if this is a new item (starts with number, dash, or asterisk)
                if stripped_line[0].isdigit() or stripped_line[0] in ['-', '*', '•']:
                    # If we have a current item, add it to the list
                    if current_item:
                        items.append(current_item.strip())
                    
                    # Start a new item, removing the marker
                    current_item = stripped_line.lstrip('0123456789.-*• ')
                else:
                    # Continue the current item
                    current_item += " " + stripped_line
            
            # Add the last item
            if current_item:
                items.append(current_item.strip())
            
            # Update the report
            report[section] = items
    
    def _clean_report(self, report: Dict[str, Any]) -> None:
        """Cleans up the report for better presentation."""
        
        # Ensure all sections have content
        if not report["summary"]:
            report["summary"] = "Analysis of your restaurant sales data reveals trends and opportunities for growth."
        
        if not report["insights"]:
            report["insights"] = [
                "Your top products contribute significantly to overall revenue.",
                "Sales show periodic fluctuations throughout the week.",
                "There are clear customer preferences for certain food categories."
            ]
        
        if not report["recommendations"]:
            report["recommendations"] = [
                "Focus marketing efforts on your top-performing products.",
                "Consider promotions during slower sales periods.",
                "Optimize inventory based on sales patterns."
            ]
        
        if not report["future_outlook"]:
            report["future_outlook"] = "Based on current trends, sales are expected to remain stable. Monitor market conditions and adapt strategies accordingly."
    
    def _generate_fallback_report(self, forecast_data: Dict[str, Any], products_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a fallback report when AI API is not available.
        Uses template-based approach with the actual data.
        """
        # Initialize with basic template
        report = {
            "summary": "Analysis of your restaurant sales data reveals important patterns and opportunities for growth.",
            "insights": [],
            "recommendations": [],
            "future_outlook": "Based on the analysis, continue monitoring sales trends and product performance for ongoing optimization."
        }
        
        # Add data-driven insights based on available information
        insights = []
        recommendations = []
        
        # Extract product insights
        if products_data and "summary" in products_data:
            summary = products_data["summary"]
            top_category = summary.get("top_category", "")
            top_category_pct = summary.get("top_category_percentage", 0)
            top_product = summary.get("highest_margin_product", "")
            top_five_pct = summary.get("top_five_percentage", 0)
            
            if top_product:
                insights.append(f"Your top product '{top_product}' is your revenue leader.")
            
            if top_category:
                insights.append(f"The '{top_category}' category represents {top_five_pct:.1f}% of your sales, showing strong customer preference.")
            
            if top_five_pct > 60:
                insights.append(f"Your top 5 products contribute {top_five_pct:.1f}% of revenue, indicating a concentrated product portfolio.")
                recommendations.append("Consider diversifying your menu while maintaining focus on top performers.")
            
            if "product_details" in products_data and products_data["product_details"]:
                recommendations.append(f"Feature '{top_product}' prominently in marketing materials to leverage its popularity.")
        
        # Extract forecast insights
        if forecast_data and "prediction_results" in forecast_data:
            if "prediction_summary" in forecast_data["prediction_results"]:
                summary = forecast_data["prediction_results"]["prediction_summary"]
                trend = summary.get("trend", "")
                trend_pct = summary.get("trend_percentage", 0)
                
                if trend == "up" and trend_pct > 0:
                    insights.append(f"Sales are trending upward by {trend_pct:.1f}%, indicating positive business momentum.")
                    future_trend = "upward"
                elif trend == "down" and trend_pct > 0:
                    insights.append(f"Sales are showing a downward trend of {trend_pct:.1f}%, which requires attention.")
                    recommendations.append("Implement targeted promotions to reverse the declining sales trend.")
                    future_trend = "downward"
                else:
                    insights.append("Sales patterns are relatively stable, providing a consistent revenue base.")
                    future_trend = "stable"
                
                best_day = summary.get("max_predicted_day", "")
                worst_day = summary.get("min_predicted_day", "")
                
                if best_day and worst_day:
                    insights.append(f"{best_day} shows the highest predicted sales, while {worst_day} shows the lowest.")
                    recommendations.append(f"Consider special promotions on {worst_day} to boost sales during slower periods.")
            
            # Add model insights
            if "best_model" in forecast_data["prediction_results"]:
                best_model = forecast_data["prediction_results"]["best_model"]
                model_type = best_model.get("model_type", "").replace("_", " ")
                accuracy = best_model.get("accuracy_score", 0) * 100
                
                if model_type and accuracy > 0:
                    report["future_outlook"] = f"Based on the {model_type} model analysis, sales are showing a {future_trend} trend. "
                    
                    if future_trend == "upward":
                        report["future_outlook"] += "Consider investing in additional capacity and staff training to meet increased demand."
                    elif future_trend == "downward":
                        report["future_outlook"] += "Focus on marketing and customer retention strategies to reverse this trend."
                    else:
                        report["future_outlook"] += "Maintain current operations while looking for opportunities to increase efficiency and profit margins."
        
        # Add some generic recommendations if we don't have enough
        if len(recommendations) < 3:
            recommendations.extend([
                "Regularly analyze sales data to identify emerging trends and adjust strategy accordingly.",
                "Train staff to recommend high-margin items to increase average order value.",
                "Optimize inventory management based on sales forecasts to reduce waste."
            ])
        
        # Add some generic insights if we don't have enough
        if len(insights) < 3:
            insights.extend([
                "Customer ordering patterns show clear time-based preferences that can be leveraged.",
                "Product performance varies significantly, with clear leaders and opportunities.",
                "Historical sales patterns provide a reliable basis for future planning."
            ])
        
        # Update the report
        report["insights"] = insights[:6]  # Limit to 6 insights
        report["recommendations"] = recommendations[:6]  # Limit to 6 recommendations
        
        return report