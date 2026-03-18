from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List

from cryptoquant.indicators import calc_trend
from cryptoquant.models import Candle, MarketSnapshot, Trend


@dataclass(slots=True)
class ScanInput:
    symbol: str
    candles_5m: List[Candle]
    candles_15m: List[Candle]


class MarketScanner:
    """扫描 BTC/ETH，筛选5m+15m同向均线趋势。"""

    symbols: Iterable[str] = ("BTC", "ETH")

    def scan(self, market_data: Dict[str, Dict[str, List[Candle]]]) -> List[MarketSnapshot]:
        snapshots: List[MarketSnapshot] = []
        for symbol in self.symbols:
            frames = market_data.get(symbol)
            if not frames:
                continue
            closes_5m = [x.close for x in frames["5m"]]
            closes_15m = [x.close for x in frames["15m"]]
            trend_5m = Trend(calc_trend(closes_5m))
            trend_15m = Trend(calc_trend(closes_15m))
            snap = MarketSnapshot(symbol=symbol, trend_5m=trend_5m, trend_15m=trend_15m)
            if snap.aligned_trend != Trend.RANGE:
                snapshots.append(snap)
        return snapshots


def latest_ts(candles: List[Candle]) -> datetime:
    return max(c.ts for c in candles)
