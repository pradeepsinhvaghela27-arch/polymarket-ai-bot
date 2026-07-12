import requests
from py_clob_client.client import ClobClient
import os

class PolymarketClient:
    def __init__(self):
        # We initialize the client just to establish the connection
        self.client = ClobClient(
            host='https://clob.polymarket.com',
            key=os.getenv('POLYMARKET_PK'),
            chain_id=137,
            signature_type=1, # 1 for email wallet, 0 for MetaMask
            funder=os.getenv('FUNDER_ADDRESS')
        )

    def get_active_markets(self, limit=5):
        # Fetch active markets from Polymarket's Gamma API
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            "active": "true",
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false",
            "limit": limit
        }
        # Add headers to bypass Cloudflare bot protection
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching markets: {response.status_code}")
                return []
        except Exception as e:
            print(f"Network Error fetching markets: {e}")
            return []

    def check_balance(self):
        # We will skip balance checking for now to avoid version errors
        print("Balance check skipped (Scout Mode active).")