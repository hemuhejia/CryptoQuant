from __future__ import annotations

from dataclasses import dataclass

from .indicators import ma20_volume
from .market_scanner import MarketDataSource
from .models import PortfolioState


@dataclass
class PositionAction:
    symbol: str
    action: str
    ratio: float


class PortfolioMonitor:
    def __init__(self, data_source: MarketDataSource) -> None:
        self.data_source = data_source

    def check(self, portfolio: PortfolioState) -> list[PositionAction]:
        actions: list[PositionAction] = []
        for symbol, pos in list(portfolio.positions.items()):
            volumes = self.data_source.get_volumes(symbol, "1m", 21)
            current = volumes[-1]
            avg20 = ma20_volume(volumes[:-1])
            ratio = current / avg20 if avg20 else 0.0

            if ratio >= 10:
                portfolio.used_margin -= pos.margin_used
                del portfolio.positions[symbol]
                actions.append(PositionAction(symbol, "close_all", ratio))
                continue

            if ratio >= 5:
                pos.qty *= 0.5
                released = pos.margin_used * 0.5
                pos.margin_used *= 0.5
                portfolio.used_margin -= released
                actions.append(PositionAction(symbol, "reduce_50pct", ratio))
        return actions
