from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List


class Trend(str, Enum):
    BULL = "bull"
    BEAR = "bear"
    RANGE = "range"


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(slots=True)
class Candle:
    symbol: str
    timeframe: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class MarketSnapshot:
    symbol: str
    trend_5m: Trend
    trend_15m: Trend

    @property
    def aligned_trend(self) -> Trend:
        if self.trend_5m == self.trend_15m and self.trend_5m != Trend.RANGE:
            return self.trend_5m
        return Trend.RANGE


@dataclass(slots=True)
class StrategySignal:
    symbol: str
    side: Side
    ts: datetime
    reason: str
    ref_price: float
    latest_1m_volume: float
    volume_ma20_1m: float


@dataclass(slots=True)
class RiskConfig:
    daily_max_loss_ratio: float = 0.10
    max_margin_per_symbol_ratio: float = 0.20
    max_positions: int = 5
    max_total_margin_ratio: float = 1.0
    max_allocation_per_trade_ratio: float = 0.20


@dataclass(slots=True)
class ExecutionConfig:
    leverage: int = 10
    slippage: float = 0.001
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.05
    isolated: bool = True


@dataclass(slots=True)
class Position:
    symbol: str
    side: Side
    size: float
    entry_price: float
    margin_used: float


@dataclass(slots=True)
class Portfolio:
    equity: float
    day_pnl: float = 0.0
    positions: Dict[str, Position] = field(default_factory=dict)

    @property
    def total_margin(self) -> float:
        return sum(p.margin_used for p in self.positions.values())

    def margin_ratio(self) -> float:
        if self.equity <= 0:
            return 0.0
        return self.total_margin / self.equity


@dataclass(slots=True)
class OrderRequest:
    symbol: str
    side: Side
    quantity: float
    price: float
    leverage: int
    isolated: bool
    slippage: float
    stop_loss: float
    take_profit: float


@dataclass(slots=True)
class TradeRecord:
    order: OrderRequest
    filled_price: float
    fee: float
    funding_cost: float
    ts: datetime


@dataclass(slots=True)
class BacktestReport:
    trades: int
    return_pct: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    net_profit: float
    fees: float
    funding_cost: float
    sharpe_ratio: float
    raw_returns: List[float]
