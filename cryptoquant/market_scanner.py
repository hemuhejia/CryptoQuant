from __future__ import annotations

from dataclasses import dataclass

from .indicators import ema, sma
from .models import Trend


@dataclass
class MarketSnapshot:
    symbol: str
    trend_5m: Trend
    trend_15m: Trend

    @property
    def tradable_trend(self) -> Trend:
        if self.trend_5m == self.trend_15m and self.trend_5m in {Trend.BULLISH, Trend.BEARISH}:
            return self.trend_5m
        return Trend.RANGE


class MarketDataSource:
    def get_close_prices(self, symbol: str, timeframe: str, limit: int) -> list[float]:
        raise NotImplementedError

    def get_volumes(self, symbol: str, timeframe: str, limit: int) -> list[float]:
        raise NotImplementedError


class MockMarketDataSource(MarketDataSource):
    def __init__(self, data: dict[tuple[str, str, str], list[float]]) -> None:
        self.data = data

    def get_close_prices(self, symbol: str, timeframe: str, limit: int) -> list[float]:
        return self.data[(symbol, timeframe, "close")][-limit:]

    def get_volumes(self, symbol: str, timeframe: str, limit: int) -> list[float]:
        return self.data[(symbol, timeframe, "volume")][-limit:]


class MarketScanner:
    def __init__(self, data_source: MarketDataSource, symbols: tuple[str, ...]) -> None:
        self.data_source = data_source
        self.symbols = symbols

    def _trend(self, closes: list[float]) -> Trend:
        ema8 = ema(closes, 8)
        ema21 = ema(closes, 21)
        ma50 = sma(closes, 50)
        if ema8 > ema21 > ma50:
            return Trend.BULLISH
        if ema8 < ema21 < ma50:
            return Trend.BEARISH
        return Trend.RANGE

    def scan(self) -> list[MarketSnapshot]:
        snapshots: list[MarketSnapshot] = []
        for symbol in self.symbols:
            close_5m = self.data_source.get_close_prices(symbol, "5m", 80)
            close_15m = self.data_source.get_close_prices(symbol, "15m", 80)
            snapshots.append(
                MarketSnapshot(
                    symbol=symbol,
                    trend_5m=self._trend(close_5m),
                    trend_15m=self._trend(close_15m),
                )
            )
        return snapshots
