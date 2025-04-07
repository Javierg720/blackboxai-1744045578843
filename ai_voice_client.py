import requests
import json
import logging

class AIVoiceClient:
    def __init__(self, api_key, service_type="retell"):
        self.api_key = api_key
        self.service_type = service_type
        self.base_url = "https://api.retellai.com/v1" if service_type == "retell" else "https://api.vapi.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_call(self, phone_number, script_id, webhook_url):
        """Create a new outbound call using the AI voice service"""
        endpoint = f"{self.base_url}/calls"
        
        # Different payload structures based on service
        if self.service_type == "retell":
            payload = {
                "to": phone_number,
                "script_id": script_id,
                "webhook_url": webhook_url
            }
        else:  # vapi
            payload = {
                "phone_number": phone_number,
                "assistant_id": script_id,
                "webhook_url": webhook_url
            }
            
        response = requests.post(endpoint, headers=self.headers, json=payload)
        return response.json()

    def get_call_status(self, call_id):
        """Get status of an ongoing call"""
        endpoint = f"{self.base_url}/calls/{call_id}"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def end_call(self, call_id):
        """End an ongoing call"""
        endpoint = f"{self.base_url}/calls/{call_id}/end"
        response = requests.post(endpoint, headers=self.headers)
        return response.json()

    def get_call_transcript(self, call_id):
        """Get the transcript of a completed call"""
        endpoint = f"{self.base_url}/calls/{call_id}/transcript"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()

    def get_call_analytics(self, call_id):
        """Get analytics data for a completed call"""
        endpoint = f"{self.base_url}/calls/{call_id}/analytics"
        response = requests.get(endpoint, headers=self.headers)
        return response.json()