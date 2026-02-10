"""
Langflow API Client
Handles communication with the Langflow API endpoint created in Lab 2
"""

import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()


class LangflowClient:
    """
    Client for interacting with the Langflow endpoint created in lab 2.
    """

    def __init__(self):
        self.url = os.getenv("LANGFLOW_API_URL")
        self.api_key = os.getenv("LANGFLOW_API_KEY")
        self.org_id = os.getenv("LANGFLOW_ORG_ID")
        self.session_id = str(uuid.uuid4())

    def query(self, message: str) -> str:
        """
        Send a query to the Langflow API and return the response.
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
            return result.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "No response")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making API request: {e}")
        except ValueError as e:
            raise Exception(f"Error parsing response: {e}")


# Usage example
if __name__ == "__main__":
    client = LangflowClient()
    response = client.query("What is the leave policy?")
    print(response)
