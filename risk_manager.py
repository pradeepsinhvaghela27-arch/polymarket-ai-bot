class RiskManager:
    def __init__(self, initial_balance):
        self.initial = initial_balance
        self.peak = initial_balance
        self.daily_pnl = 0
        self.trades_today = 0
        self.max_trades_per_day = 5  # Max 5 trades a day for a $5 account
        self.max_position_pct = 0.20 # Risk 20% ($1.00) per trade to allow growth

    def check_can_trade(self, current_balance, proposed_size):
        # 1. Check daily loss limit (If down $1.00 in a day, stop)
        if self.daily_pnl < -self.initial * 0.20:
            print("   [RISK] DAILY STOP: Trading halted for the day.")
            return False

        # 2. Check drawdown (If down $2.50 total, stop)
        if current_balance > self.peak:
            self.peak = current_balance
        drawdown = (self.peak - current_balance) / self.peak
        if drawdown > 0.50:
            print("   [RISK] DRAWDOWN HALT: Manual restart required.")
            return False

        # 3. Check total loss (If down to $2.00, stop completely)
        if current_balance < self.initial * 0.40:
            print("   [RISK] TOTAL LOSS HALT: Capital preserved.")
            return False

        # 4. Cap position size (Max $1.00 per trade)
        max_size = self.initial * self.max_position_pct
        if proposed_size > max_size:
            print(f"   [RISK] Position capped at ${max_size:.2f}")
            proposed_size = max_size

        # 5. Check trade count
        if self.trades_today >= self.max_trades_per_day:
            print("   [RISK] Max trades for today reached.")
            return False

        return True

    def record_trade(self, pnl):
        self.daily_pnl += pnl
        self.trades_today += 1

    def reset_daily(self):
        self.daily_pnl = 0
        self.trades_today = 0