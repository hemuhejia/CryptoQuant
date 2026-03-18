from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Trend(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    RANGE = "range"


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class Signal:
    symbol: str
    side: Side
    reason: str


@dataclass
class Position:
    symbol: str
    side: Side
    qty: float
    entry_price: float
    margin_used: float


@dataclass
class PortfolioState:
    equity: float
    daily_start_equity: float
    used_margin: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)

    @property
    def daily_loss_ratio(self) -> float:
        if self.daily_start_equity <= 0:
            return 0.0
        loss = max(0.0, self.daily_start_equity - self.equity)
        return loss / self.daily_start_equity

    @property
    def total_margin_ratio(self) -> float:
        if self.equity <= 0:
            return 1.0
        return self.used_margin / self.equity
