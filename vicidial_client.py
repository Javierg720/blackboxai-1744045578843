import requests
import json
import logging

class ViciDialClient:
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.auth = {
            'user': username,
            'pass': password
        }

    def get_leads(self, campaign_id, limit=10):
        """Retrieve leads from ViciDial campaign"""
        endpoint = f"{self.server_url}/agc/api.php"
        params = {
            **self.auth,
            'function': 'get_leads',
            'campaign_id': campaign_id,
            'limit': limit,
            'stage': 'ready',
            'format': 'json'
        }
        
        response = requests.get(endpoint, params=params)
        return response.json()

    def update_lead_status(self, lead_id, status):
        """Update lead status after call completion"""
        endpoint = f"{self.server_url}/agc/api.php"
        params = {
            **self.auth,
            'function': 'update_lead',
            'lead_id': lead_id,
            'status': status,
            'format': 'json'
        }
        
        response = requests.post(endpoint, data=params)
        return response.json()

    def initiate_call(self, lead_id, phone_number, campaign_id):
        """Initiate outbound call through ViciDial"""
        endpoint = f"{self.server_url}/agc/api.php"
        params = {
            **self.auth,
            'function': 'external_dial',
            'lead_id': lead_id,
            'phone_number': phone_number,
            'campaign_id': campaign_id,
            'format': 'json'
        }
        
        response = requests.post(endpoint, data=params)
        return response.json()