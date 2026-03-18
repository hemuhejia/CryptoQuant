from __future__ import annotations

from dataclasses import dataclass

from .config import RiskConfig
from .models import PortfolioState, Signal


@dataclass
class RiskDecision:
    approved: bool
    allocation: float = 0.0
    message: str = ""


class RiskEngine:
    def __init__(self, config: RiskConfig) -> None:
        self.config = config

    def evaluate(self, signal: Signal, portfolio: PortfolioState) -> RiskDecision:
        if portfolio.daily_loss_ratio > self.config.max_daily_loss_ratio:
            return RiskDecision(False, message="daily loss limit exceeded")

        if len(portfolio.positions) >= self.config.max_positions and signal.symbol not in portfolio.positions:
            return RiskDecision(False, message="max positions reached")

        if portfolio.total_margin_ratio >= self.config.max_total_margin_ratio:
            return RiskDecision(False, message="total margin ratio limit reached")

        max_alloc = portfolio.equity * self.config.max_alloc_per_trade_ratio

        existing = portfolio.positions.get(signal.symbol)
        if existing:
            symbol_ratio = existing.margin_used / portfolio.equity
            if symbol_ratio >= self.config.max_single_symbol_margin_ratio:
                return RiskDecision(False, message="single symbol margin limit reached")
            remaining = (self.config.max_single_symbol_margin_ratio * portfolio.equity) - existing.margin_used
            max_alloc = max(0.0, min(max_alloc, remaining))

        if max_alloc <= 0:
            return RiskDecision(False, message="no allocatable margin")

        return RiskDecision(True, allocation=max_alloc, message="approved")
