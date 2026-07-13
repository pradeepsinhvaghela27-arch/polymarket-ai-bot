import os
import json
import re
from openai import OpenAI

class AIEngine:
    def __init__(self):
        self.client = OpenAI(
            base_url='https://openrouter.ai/api/v1',
            api_key=os.getenv('OPENROUTER_API_KEY')
        )

        def get_decision(self, market_data, whale_context="No whale activity."):
        # Safely parse the outcome prices
        try:
            prices = json.loads(market_data.get('outcomePrices', '["0.5"]'))
            yes_price = float(prices[0]) if len(prices) > 0 else 0.5
        except:
            yes_price = 0.5

        # Parse the end date of the market
        end_date_str = market_data.get('endDate', 'Unknown')
        # We just pass the raw date string to the AI, it understands dates perfectly
        
        prompt = f"""
        Market Question: {market_data.get('question', 'Unknown')}
        Current YES price: ${yes_price:.2f}
        Volume: ${market_data.get('volume', 0)}
        Market End Date: {end_date_str}
        Whale Context: {whale_context}
        
        Based on your knowledge, the current date, and the market end date, does this event have a high probability of resolving YES?
        If the end date is very soon and the event hasn't happened, reduce confidence.
        Provide JSON response ONLY. Do not include markdown formatting.
        """

        response = self.client.chat.completions.create(
            model='deepseek/deepseek-chat',
            messages=[
                {'role': 'system', 'content': 'You are a prediction market quant. If whale context is positive, increase confidence slightly. Output strictly JSON: {"decision": "BUY_YES" | "NO_TRADE", "confidence": 0-100, "reasoning": "1 sentence"}'},
                {'role': 'user', 'content': prompt}
            ]
        )

        raw_response = response.choices[0].message.content
        try:
            clean_response = re.sub(r'^```json\s*|\s*```$', '', raw_response.strip(), flags=re.MULTILINE)
            return json.loads(clean_response)
        except Exception as e:
            print(f"   AI response parsing error: {e}")
            return {"decision": "NO_TRADE", "confidence": 0, "reasoning": "Error parsing"}