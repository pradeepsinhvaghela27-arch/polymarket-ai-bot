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

    def execute_trade(self, token_id, side="BUY", size_usd=1.0):
        """Executes a real market order on Polymarket"""
        from py_clob_client.clob_types import MarketOrderArgs, OrderType
        
        print(f"   [ACTION] Attempting to execute {side} order for ${size_usd}...")
        try:
            # Create the order arguments
            order_args = MarketOrderArgs(
                token_id=token_id,
                amount=size_usd,
            )
            # Create and sign the order
            signed_order = self.client.create_market_order(order_args)
            # Submit the order (Fill or Kill means it executes immediately at market price or cancels)
            response = self.client.post_order(signed_order, OrderType.FOK)
            
            print(f"   [SUCCESS] Trade executed! Transaction details: {response}")
            return True
        except Exception as e:
            print(f"   [ERROR] Trade failed: {e}")
            return False