import requests
from py_clob_client.client import ClobClient
from py_clob_client.order_builder.constants import BUY
import os

class PolymarketClient:
    def __init__(self):
        # Clean Private Key
        pk = os.getenv('POLYMARKET_PK', '').strip().replace('"', '').replace("'", '')
        if not pk.startswith('0x'):
            pk = '0x' + pk
            
        # Clean Funder Address
        funder = os.getenv('FUNDER_ADDRESS', '').strip().replace('"', '').replace("'", '')
        if not funder.startswith('0x'):
            funder = '0x' + funder
            
        print(f"DEBUG: Private key length: {len(pk)} (Need 66)")
        print(f"DEBUG: Funder address length: {len(funder)} (Need 42)")
            
        self.client = ClobClient(
            host='https://clob.polymarket.com',
            key=pk,
            chain_id=137,
            signature_type=1,
            funder=funder
        )
        
        # Derive API credentials with fallbacks for different SDK versions
        try:
            if hasattr(self.client, 'create_or_derive_api_key'):
                creds = self.client.create_or_derive_api_key()
            elif hasattr(self.client, 'derive_api_key'):
                creds = self.client.derive_api_key()
            elif hasattr(self.client, 'create_api_key'):
                creds = self.client.create_api_key()
            else:
                creds = None
                
            if creds:
                self.client.set_api_creds(creds)
                print("DEBUG: API Credentials derived successfully.")
            else:
                print("DEBUG: Could not find API key derivation method.")
        except Exception as e:
            print(f"DEBUG: Could not derive API creds: {e}")

    def get_active_markets(self, limit=5):
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            "active": "true", "closed": "false", 
            "order": "volume24hr", "ascending": "false", "limit": limit
        }
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
        print("Balance check skipped (Scout Mode active).")

    def execute_trade(self, token_id, side="BUY", size_usd=1.0):
        from py_clob_client.clob_types import MarketOrderArgs, OrderType
        
        print(f"   [ACTION] Attempting to execute BUY order for ${size_usd}...")
        try:
            order_args = MarketOrderArgs(token_id=token_id, amount=size_usd, side=BUY)
            signed_order = self.client.create_market_order(order_args)
            response = self.client.post_order(signed_order, OrderType.FOK)
            
            print(f"   [SUCCESS] Trade executed! Transaction details: {response}")
            return True
        except Exception as e:
            print(f"   [ERROR] Trade failed: {e}")
            return False