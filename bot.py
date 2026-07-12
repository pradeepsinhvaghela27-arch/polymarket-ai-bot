import os
import json
import time
from dotenv import load_dotenv
from polymarket_client import PolymarketClient
from ai_engine import AIEngine
from risk_manager import RiskManager

# Load environment variables
load_dotenv()

STARTING_CAPITAL = 5.0

def run_bot_cycle():
    """Runs one full scan of the markets"""
    print("\n=== Starting New Market Scan ===")
    
    poly_client = PolymarketClient()
    ai_engine = AIEngine()
    risk_manager = RiskManager(initial_balance=STARTING_CAPITAL)
    
    markets = poly_client.get_active_markets(limit=5)
    
    if not markets:
        print("No markets found.")
        return

    current_balance = STARTING_CAPITAL
    
    for market in markets:
        question = market.get('question', 'Unknown Market')
        
        # Ask AI what to do
        decision = ai_engine.get_decision(market)
        
        print(f"Market: {question}")
        print(f"-> AI Decision: {decision.get('decision')} (Confidence: {decision.get('confidence')}%)")
        
        if decision.get('decision') == 'BUY_YES':
            proposed_size = 1.00
            can_trade = risk_manager.check_can_trade(current_balance, proposed_size)
            
            if can_trade:
                print("   [ACTION] Executing live trade...")
                clob_token_ids = market.get('clobTokenIds', '[]')
                try:
                    token_ids = json.loads(clob_token_ids)
                    yes_token_id = token_ids[0] if len(token_ids) > 0 else None
                    if yes_token_id:
                        success = poly_client.execute_trade(token_id=yes_token_id, side="BUY", size_usd=proposed_size)
                        if success:
                            risk_manager.record_trade(-proposed_size)
                except Exception as e:
                    print(f"   [ERROR] Could not parse token ID: {e}")

# Main 24/7 Loop
if __name__ == "__main__":
    print("Bot started in 24/7 Cloud Mode. Checking markets every 15 minutes.")
    while True:
        try:
            run_bot_cycle()
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
        
        # Sleep for 15 minutes (900 seconds) to save API costs
        print("\nSleeping for 15 minutes...") 
        time.sleep(900)