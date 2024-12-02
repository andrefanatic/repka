import time
import logging
import requests
from token_cache import TokenCache
from config import access_key, access_id

class APIClient:
    def __init__(self, auth_url, api_url, client_id, client_key, endpoint_config=None):
        self.auth_url = auth_url
        self.api_url = api_url
        self.client_id = client_id
        self.client_key = client_key
        
        # Initialize token cache
        self.token_cache = TokenCache()
        
        # Initialize token
        self.token = None

        self.endpoints = {
            "report": "report",
            "report_day": "report/day",
            "traffic_log": "traffic_log"
        }
        
        # Allow additional or overriding endpoints
        if endpoint_config:
            self.endpoints.update(endpoint_config)


    def get_token(self):
        """Retrieve a new authentication token"""
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json"
        }
        data = {
            "accessId": self.client_id,
            "accessKey": self.client_key
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, json=data)
            
            if response.status_code == 200:
                token_data = response.json()
                new_token = token_data["token"]
                
                # Save token to cache
                self.token_cache.save_token(new_token)
                
                # Update current token
                self.token = new_token
                
                logging.info("New token retrieved and cached")
                return new_token
            
            else:
                raise Exception(f"Token retrieval failed: {response.text}")
        
        except Exception as e:
            logging.error(f"Token retrieval error: {e}")
            raise

    def check_token(self):
        """Check and retrieve token if needed"""
        # Try to get cached token first
        cached_token = self.token_cache.get_token()
        
        if cached_token:
            self.token = cached_token
        else:
            # If no valid cached token, get a new one
            self.get_token()
        
        return self.token

    def make_request(self, endpoint_key, params=None):
        """Make an API request with token management"""
        # Ensure we have a valid token
        self.check_token()
        
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "cwauth-token": self.token
        }
        
        endpoint = self.endpoints.get(endpoint_key)
        if not endpoint:
            raise ValueError(f"Invalid endpoint key: {endpoint_key}")
        
        try:
            response = requests.get(f"{self.api_url}/{endpoint}", 
                                    headers=headers, 
                                    params=params)
            
            # Handle response as needed
            return response.json()
        
        except requests.RequestException as e:
            logging.error(f"API request failed: {e}")
            raise


params = {
    "include": "TRAFFIC",
    "column": ["day", "traffic-source-name", "visits", "conversions", "cost", "revenue", "profit", "roi"],
    "groupBy": ["traffic-source", "day"],
    "filter": "Rollerads_Andrey",
    "from": "2024-11-01",
    "to": "2024-11-30"
}


client = APIClient(
    auth_url = "https://api.voluum.com/auth/access/session",
    api_url = "https://api.voluum.com",
    client_id = access_id,
    client_key = access_key
)


try:
    result = client.make_request("report", params=params)
    print(result)
except Exception as e:
    print(e)