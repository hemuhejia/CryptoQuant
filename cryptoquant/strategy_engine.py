from __future__ import annotations

from .config import StrategyConfig
from .indicators import ma20_volume
from .market_scanner import MarketDataSource, MarketSnapshot
from .models import Side, Signal, Trend


class StrategyEngine:
    def __init__(self, data_source: MarketDataSource, config: StrategyConfig) -> None:
        self.data_source = data_source
        self.config = config

    def evaluate(self, snapshot: MarketSnapshot) -> Signal | None:
        trend = snapshot.tradable_trend
        if trend == Trend.RANGE:
            return None

        volumes = self.data_source.get_volumes(snapshot.symbol, "1m", 21)
        current_volume = volumes[-1]
        avg20 = ma20_volume(volumes[:-1])
        if current_volume <= self.config.volume_spike_multiplier * avg20:
            return None

        side = Side.LONG if trend == Trend.BULLISH else Side.SHORT
        return Signal(
            symbol=snapshot.symbol,
            side=side,
            reason=f"trend={trend.value}, volume_spike={current_volume/avg20:.2f}x",
        )
