import os
import json
from dotenv import load_dotenv
from polymarket_client import PolymarketClient
from ai_engine import AIEngine
from risk_manager import RiskManager

# Load environment variables
load_dotenv()
print(f"DEBUG: OpenRouter Key loaded? {bool(os.getenv('OPENROUTER_API_KEY'))}")

# Initialize Risk Manager with $5 starting capital
STARTING_CAPITAL = 5.0

def main():
    print("=== Polymarket AI Bot Initializing ===")
    
    poly_client = PolymarketClient()
    ai_engine = AIEngine()
    risk_manager = RiskManager(initial_balance=STARTING_CAPITAL)
    
    print("3. Checking balance...")
    poly_client.check_balance()
    
    print("\n4. Fetching top 5 active markets by volume...")
    markets = poly_client.get_active_markets(limit=5)
    
    if not markets:
        print("No markets found. Exiting.")
        return

    print(f"Found {len(markets)} markets. Sending to AI for analysis...\n")
    
    current_balance = STARTING_CAPITAL
    
    for market in markets:
        question = market.get('question', 'Unknown Market')
        print(f"Market: {question}")
        
        # Ask AI what to do
        decision = ai_engine.get_decision(market)
        
        print(f"-> AI Decision: {decision.get('decision')} (Confidence: {decision.get('confidence')}%)")
        print(f"-> Reasoning: {decision.get('reasoning')}")
        
        # If AI says BUY, check with Risk Manager
        if decision.get('decision') == 'BUY_YES':
            proposed_size = 1.00 # Propose a $1.00 trade (Polymarket minimum)
            can_trade = risk_manager.check_can_trade(current_balance, proposed_size)
            
            if can_trade:
                print("   [ACTION] Executing live trade...")
                
                # Extract the YES Token ID from market data
                clob_token_ids = market.get('clobTokenIds', '[]')
                try:
                    token_ids = json.loads(clob_token_ids)
                    yes_token_id = token_ids[0] if len(token_ids) > 0 else None
                    
                    if yes_token_id:
                        # FIRE THE TRADE
                        success = poly_client.execute_trade(
                            token_id=yes_token_id, 
                            side="BUY", 
                            size_usd=proposed_size
                        )
                        if success:
                            risk_manager.record_trade(-proposed_size) # Deduct from balance
                except Exception as e:
                    print(f"   [ERROR] Could not parse token ID: {e}")
            else:
                print("   [ACTION] Trade blocked by Risk Manager.")
        
        print("-" * 50)

if __name__ == "__main__":
    main()