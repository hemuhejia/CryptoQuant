from __future__ import annotations

from dataclasses import dataclass

from cryptoquant.models import Portfolio, RiskConfig, StrategySignal


@dataclass(slots=True)
class ApprovedTrade:
    signal: StrategySignal
    margin_to_use: float


class RiskEngine:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or RiskConfig()

    def approve(self, signal: StrategySignal, portfolio: Portfolio) -> ApprovedTrade | None:
        # 1) 当日最大亏损
        if portfolio.day_pnl <= -portfolio.equity * self.config.daily_max_loss_ratio:
            return None

        # 2) 单标的仓位上限
        existing = portfolio.positions.get(signal.symbol)
        existing_margin = existing.margin_used if existing else 0.0
        if existing_margin >= portfolio.equity * self.config.max_margin_per_symbol_ratio:
            return None

        # 3) 最大持仓标的数量
        if signal.symbol not in portfolio.positions and len(portfolio.positions) >= self.config.max_positions:
            return None

        # 4) 总保证金上限
        if portfolio.margin_ratio() >= self.config.max_total_margin_ratio:
            return None

        # 5) 单次最多分配总资金20%
        max_trade_margin = portfolio.equity * self.config.max_allocation_per_trade_ratio
        remaining_symbol_room = (
            portfolio.equity * self.config.max_margin_per_symbol_ratio - existing_margin
        )
        remaining_total_room = portfolio.equity * self.config.max_total_margin_ratio - portfolio.total_margin

        margin = min(max_trade_margin, remaining_symbol_room, remaining_total_room)
        if margin <= 0:
            return None
        return ApprovedTrade(signal=signal, margin_to_use=margin)
