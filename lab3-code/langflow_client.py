"""
Langflow API Client
Handles communication with the Langflow API endpoint created in Lab 2
"""

import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LangflowClient:
    """Client for interacting with Langflow API"""
    
    def __init__(self):
        self.api_url = os.getenv("LANGFLOW_API_URL")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        
        if not self.api_url or not self.api_key:
            raise ValueError(
                "LANGFLOW_API_URL and LANGFLOW_API_KEY must be set in .env file"
            )
    
    async def query_agent(self, message: str, employee_id: str = None) -> Dict[str, Any]:
        """
        Send a query to the Langflow agent
        
        Args:
            message: The user's message/query
            employee_id: Optional employee ID for context
            
        Returns:
            Dictionary containing the agent's response and any extracted data
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "input": message,
            "tweaks": {
                "employee_id": employee_id
            } if employee_id else {}
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return self._parse_response(result)
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to call Langflow API: {str(e)}",
                "response": None
            }
    
    def _parse_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the Langflow API response and extract relevant information
        
        Args:
            result: Raw response from Langflow API
            
        Returns:
            Parsed response with extracted data
        """
        try:
            # Extract the main response text
            response_text = result.get("output", {}).get("text", "")
            
            # Extract any structured data from the response
            # This is a simplified parser - adjust based on your Langflow output format
            parsed_data = {
                "success": True,
                "response": response_text,
                "employee_id": None,
                "leave_balance": None,
                "days_requested": None,
                "leave_type": None,
                "start_date": None,
                "end_date": None
            }
            
            # Try to extract structured data if present
            if "data" in result:
                data = result["data"]
                parsed_data.update({
                    "employee_id": data.get("employee_id"),
                    "leave_balance": data.get("leave_balance"),
                    "days_requested": data.get("days_requested"),
                    "leave_type": data.get("leave_type"),
                    "start_date": data.get("start_date"),
                    "end_date": data.get("end_date")
                })
            
            return parsed_data
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "response": None
            }
    
    def extract_leave_request_info(self, text: str) -> Dict[str, Any]:
        """
        Extract leave request information from text using simple pattern matching
        This is a fallback if Langflow doesn't return structured data
        
        Args:
            text: Text to parse
            
        Returns:
            Dictionary with extracted information
        """
        import re
        from datetime import datetime
        
        info = {
            "days_requested": None,
            "leave_type": None,
            "start_date": None,
            "end_date": None
        }
        
        # Extract number of days
        days_match = re.search(r'(\d+)\s*days?', text, re.IGNORECASE)
        if days_match:
            info["days_requested"] = int(days_match.group(1))
        
        # Extract leave type
        leave_types = ["vacation", "sick", "personal"]
        for leave_type in leave_types:
            if leave_type in text.lower():
                info["leave_type"] = leave_type
                break
        
        # Extract dates (simplified - you may want more robust date parsing)
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = re.findall(date_pattern, text)
        if len(dates) >= 2:
            info["start_date"] = dates[0]
            info["end_date"] = dates[1]
        
        return info

# Made with Bob
