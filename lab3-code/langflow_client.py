"""
Langflow API Client
Handles communication with the Langflow API endpoint created in Lab 2
Parses structured JSON responses to populate agent state
"""
import requests
import os
import json
import uuid
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class LangflowClient:
    """
    Client for interacting with the Langflow endpoint created in Lab 2.
    Parses structured JSON responses to populate agent state.
    """

    def __init__(self):
        self.url = os.getenv("LANGFLOW_API_URL")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        self.org_id = os.getenv("LANGFLOW_ORG_ID")
        self.session_id = str(uuid.uuid4())

    def query(self, message: str) -> Dict[str, Any]:
        """
        Send a query to the Langflow API and return parsed response.
        
        Returns:
            Dictionary containing:
            - conversational_response: Natural language response
            - query_flag: Boolean indicating if this is a simple query
            - data: Dictionary with structured fields (employee_id, leave_balance, etc.)
            - raw_text: Original response text (for fallback parsing)
        """
        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": message,
            "session_id": self.session_id
        }

        headers = {
            "X-DataStax-Current-Org": self.org_id,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            # Extract the text response from Langflow output
            raw_text = result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(raw_text)
                
                # Validate expected structure
                if "conversational_response" in parsed_json and "query_flag" in parsed_json:
                    return {
                        "conversational_response": parsed_json.get("conversational_response", ""),
                        "query_flag": parsed_json.get("query_flag", True),
                        "data": parsed_json.get("data", {}),
                        "raw_text": raw_text,
                        "parsed": True
                    }
            except json.JSONDecodeError:
                pass
            
            return {
                "conversational_response": raw_text,
                "query_flag": True,
                "data": {},
                "raw_text": raw_text,
                "parsed": False
            }

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making API request: {e}")
        except Exception as e:
            raise Exception(f"Error processing response: {e}")


# Usage example
if __name__ == "__main__":
    client = LangflowClient()
    response = client.query("What is my leave balance?")
    print(f"Conversational: {response['conversational_response']}")
    print(f"Data: {response['data']}")
