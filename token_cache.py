import os
import json
import time
import logging

class TokenCache:
    def __init__(self, cache_file='token_cache.json', max_age=7200):  # 2 hours default
        self.cache_file = cache_file
        self.max_age = max_age
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def save_token(self, token):
        cache_data = {
            'token': token,
            'timestamp': time.time()
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            logging.info(f"Token saved to {self.cache_file}")
        except IOError as e:
            logging.error(f"Could not write token to {self.cache_file}: {e}")

    def get_token(self):
        if not os.path.exists(self.cache_file):
            logging.info("No token cache file found")
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check token age
            current_time = time.time()
            token_age = current_time - cache_data.get('timestamp', 0)
            
            if token_age < self.max_age:
                logging.info("Valid token retrieved from cache")
                return cache_data['token']
            
            logging.info("Cached token has expired")
            return None
        
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error reading token cache: {e}")
            return None

    def is_token_valid(self):
        return self.get_token() is not None

    def clear(self):
        try:
            os.remove(self.cache_file)
            logging.info(f"Token cache file {self.cache_file} removed")
        except FileNotFoundError:
            logging.info(f"No token cache file found at {self.cache_file}")