from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.services.data_service import DataService
from app.services.trading_service import TradingService


@dataclass
class PortfolioState:
    cash: float
    position: float
    equity: float
    ts: str


class BacktestService:
    def __init__(self):
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set a callback function for progress updates."""
        self.progress_callback = callback

    def update_progress(self, progress: float, message: str = ""):
        """Update progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(progress, message)

    def run(self, symbol: str, start_date: str, end_date: str, initial_cash: float) -> dict:
        self.update_progress(5, "Fetching market data...")

        data = DataService().fetch(symbol, start_date, end_date, "daily")
        if not data:
            self.update_progress(100, "No data available")
            return {
                "final_cash": initial_cash,
                "trades": [],
                "snapshots": [],
                "summary": "no data",
                "max_drawdown": 0.0,
                "buy_hold_return": 0.0,
                "strategy_return": 0.0,
                "total_fees": 0.0
            }

        self.update_progress(10, f"Processing {len(data)} data points...")

        # Trading strategy backtest
        cash = initial_cash
        position = 0.0
        trades: List[dict] = []
        snapshots: List[dict] = []
        total_fees = 0.0
        fee_rate = 0.001  # 0.1% trading fee

        svc = TradingService()
        peak_equity = initial_cash

        total_bars = len(data)
        for i, bar in enumerate(data):
            # Update progress periodically (every 10% or so)
            if i % max(1, total_bars // 10) == 0:
                progress = 10 + (i / total_bars) * 70  # 10-80% range for processing
                self.update_progress(progress, f"Processing {i+1}/{total_bars} data points...")

            price = bar["close"]
            decision = svc.decide(symbol, "daily", cash)
            action = decision["action"]
            qty = decision["quantity"]

            if action == "BUY" and cash > 0 and price > 0:
                max_qty = cash / price
                qty = min(qty, max_qty)
                if qty > 0:
                    cost = qty * price
                    fee = cost * fee_rate
                    cash -= (cost + fee)
                    position += qty
                    total_fees += fee
                    trades.append({"ts": bar["ts"], "action": "BUY", "price": price, "quantity": qty, "fees": fee})
            elif action == "SELL" and position > 0 and price > 0:
                qty = position  # sell all
                proceeds = qty * price
                fee = proceeds * fee_rate
                cash += (proceeds - fee)
                total_fees += fee
                trades.append({"ts": bar["ts"], "action": "SELL", "price": price, "quantity": qty, "fees": fee})
                position = 0.0

            equity = cash + position * price
            peak_equity = max(peak_equity, equity)
            snapshots.append({"ts": bar["ts"], "cash": cash, "position": position, "equity": equity})

        self.update_progress(80, "Calculating performance metrics...")

        final_equity = snapshots[-1]["equity"] if snapshots else initial_cash
        strategy_return = (final_equity - initial_cash) / initial_cash

        # Calculate max drawdown
        self.update_progress(85, "Analyzing drawdown...")
        max_drawdown = 0.0
        current_peak = initial_cash
        for snapshot in snapshots:
            equity = snapshot["equity"]
            current_peak = max(current_peak, equity)
            drawdown = (current_peak - equity) / current_peak
            max_drawdown = max(max_drawdown, drawdown)

        # Buy-and-hold baseline
        self.update_progress(90, "Comparing with buy-and-hold strategy...")
        initial_price = data[0]["close"]
        final_price = data[-1]["close"]
        buy_hold_shares = initial_cash / initial_price
        buy_hold_final_value = buy_hold_shares * final_price
        buy_hold_return = (buy_hold_final_value - initial_cash) / initial_cash

        self.update_progress(95, "Generating summary...")

        summary = (
            f"Ran {len(data)} bars; trades={len(trades)}; "
            f"final_equity=${final_equity:.2f}; max_drawdown={max_drawdown:.2%}; "
            f"strategy_return={strategy_return:.2%}; buy_hold_return={buy_hold_return:.2%}; "
            f"total_fees=${total_fees:.2f}"
        )

        self.update_progress(100, "Backtest completed successfully!")

        return {
            "final_cash": cash,
            "final_equity": final_equity,
            "trades": trades,
            "snapshots": snapshots,
            "summary": summary,
            "max_drawdown": max_drawdown,
            "strategy_return": strategy_return,
            "buy_hold_return": buy_hold_return,
            "total_fees": total_fees
        }


