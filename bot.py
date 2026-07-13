import os
import json
import requests
from dotenv import load_dotenv
from polymarket_client import PolymarketClient
from ai_engine import AIEngine
from risk_manager import RiskManager

# Load environment variables
load_dotenv()

STARTING_CAPITAL = 5.88

def send_alert(message):
    """Sends a push notification to Discord"""
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not webhook_url:
        return # Skip if not configured
    
    payload = {"content": message}
    try:
        requests.post(webhook_url, json=payload)
    except:
        pass

def main():
    print("=== Starting Scheduled Market Scan ===")
    
    poly_client = PolymarketClient()
    ai_engine = AIEngine()
    risk_manager = RiskManager(initial_balance=STARTING_CAPITAL)
    
    print("Fetching top 5 active markets by volume...")
    markets = poly_client.get_active_markets(limit=5)
    
    if not markets:
        print("No markets found.")
        return

    current_balance = STARTING_CAPITAL
    
    for market in markets:
        question = market.get('question', 'Unknown Market')
        
        # Ask AI what to do
        decision = ai_engine.get_decision(market)
        
        print(f"\nMarket: {question}")
        print(f"-> AI Decision: {decision.get('decision')} (Confidence: {decision.get('confidence')}%)")
        
        # If AI says BUY_YES and confidence is 75% or higher
        if decision.get('decision') == 'BUY_YES' and decision.get('confidence', 0) >= 75:
            proposed_size = 1.00
            can_trade = risk_manager.check_can_trade(current_balance, proposed_size)
            
            if can_trade:
                send_alert(f"🚀 TRADE EXECUTED: {question}\nConfidence: {decision.get('confidence')}%")
                print("   [ACTION] Executing live trade! Confidence is high.")
                
                clob_token_ids = market.get('clobTokenIds', '[]')
                try:
                    token_ids = json.loads(clob_token_ids)
                    yes_token_id = token_ids[0] if len(token_ids) > 0 else None
                    if yes_token_id:
                        success = poly_client.execute_trade(token_id=yes_token_id, side="BUY", size_usd=proposed_size)
                        if success:
                            risk_manager.record_trade(-proposed_size)
                            send_alert(f"✅ SUCCESS: Bought YES on {question}")
                except Exception as e:
                    print(f"   [ERROR] Could not parse token ID: {e}")
                    send_alert(f"❌ ERROR parsing token ID for {question}")
                    
        # If AI says BUY_YES but confidence is below 75%
        elif decision.get('decision') == 'BUY_YES':
            msg = f"⏳ SKIP: {question}\nAI said YES, but confidence ({decision.get('confidence')}%) is below 75%."
            print(f"   {msg}")
            # Uncomment the line below if you want alerts for skipped trades too
            # send_alert(msg)

if __name__ == "__main__":
    main()