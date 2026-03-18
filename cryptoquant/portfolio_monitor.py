from __future__ import annotations

from dataclasses import dataclass

from cryptoquant.models import Position


@dataclass(slots=True)
class MonitorAction:
    symbol: str
    action: str
    reduce_ratio: float


class PortfolioMonitor:
    """持仓主动减仓规则。"""

    def evaluate(self, position: Position, latest_volume: float, volume_ma20: float) -> MonitorAction | None:
        if volume_ma20 <= 0:
            return None
        ratio = latest_volume / volume_ma20
        if ratio >= 10:
            return MonitorAction(symbol=position.symbol, action="close", reduce_ratio=1.0)
        if ratio >= 5:
            return MonitorAction(symbol=position.symbol, action="reduce", reduce_ratio=0.5)
        return None
