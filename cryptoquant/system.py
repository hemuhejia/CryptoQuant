from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from cryptoquant.backtest import Backtester
from cryptoquant.execution_engine import ExecutionEngine
from cryptoquant.market_scanner import MarketScanner
from cryptoquant.models import Candle, Portfolio, Position
from cryptoquant.portfolio_monitor import PortfolioMonitor
from cryptoquant.risk_engine import RiskEngine
from cryptoquant.strategy_engine import OneMinuteVolumeStrategy


@dataclass(slots=True)
class RunResult:
    trades_executed: int
    reduced_positions: int


class HyperliquidQuantSystem:
    def __init__(self) -> None:
        self.scanner = MarketScanner()
        self.strategy = OneMinuteVolumeStrategy()
        self.risk = RiskEngine()
        self.execution = ExecutionEngine()
        self.monitor = PortfolioMonitor()
        self.backtester = Backtester()

    def run_once(self, market_data: Dict[str, Dict[str, List[Candle]]], portfolio: Portfolio) -> RunResult:
        snapshots = self.scanner.scan(market_data)
        signals = self.strategy.evaluate(snapshots, {k: v["1m"] for k, v in market_data.items() if "1m" in v})

        trades = 0
        for sig in signals:
            approved = self.risk.approve(sig, portfolio)
            if not approved:
                continue
            order = self.execution.build_order(approved)
            self.execution.execute(order)

            margin = approved.margin_to_use
            portfolio.positions[sig.symbol] = Position(
                symbol=sig.symbol,
                side=sig.side,
                size=order.quantity,
                entry_price=order.price,
                margin_used=margin,
            )
            trades += 1

        reduced = 0
        for symbol, position in list(portfolio.positions.items()):
            c1 = market_data.get(symbol, {}).get("1m", [])
            if len(c1) < 20:
                continue
            latest_volume = c1[-1].volume
            volume_ma20 = sum(x.volume for x in c1[-20:]) / 20
            action = self.monitor.evaluate(position, latest_volume, volume_ma20)
            if not action:
                continue
            if action.action == "close":
                del portfolio.positions[symbol]
            else:
                position.size *= 1 - action.reduce_ratio
                position.margin_used *= 1 - action.reduce_ratio
            reduced += 1

        return RunResult(trades_executed=trades, reduced_positions=reduced)
