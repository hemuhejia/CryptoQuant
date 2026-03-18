from __future__ import annotations

from dataclasses import dataclass

from .config import ExecutionConfig
from .models import PortfolioState, Position, Side, Signal


@dataclass
class ExecutionReport:
    symbol: str
    side: Side
    qty: float
    entry_price: float
    stop_loss: float
    take_profit: float
    slippage_ratio: float


class ExecutionEngine:
    def __init__(self, config: ExecutionConfig) -> None:
        self.config = config
        self.trade_log: list[ExecutionReport] = []

    def execute(
        self,
        signal: Signal,
        allocation: float,
        mark_price: float,
        previous_candle_low: float,
        portfolio: PortfolioState,
    ) -> ExecutionReport:
        notional = allocation * self.config.leverage
        qty = notional / mark_price

        if signal.side == Side.LONG:
            stop_loss = max(mark_price * (1 - self.config.stop_loss_ratio), previous_candle_low)
            take_profit = mark_price * (1 + self.config.take_profit_ratio)
        else:
            stop_loss = mark_price * (1 + self.config.stop_loss_ratio)
            take_profit = mark_price * (1 - self.config.take_profit_ratio)

        report = ExecutionReport(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            entry_price=mark_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            slippage_ratio=self.config.slippage_ratio,
        )
        self.trade_log.append(report)

        portfolio.positions[signal.symbol] = Position(
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            entry_price=mark_price,
            margin_used=allocation,
        )
        portfolio.used_margin += allocation
        return report
