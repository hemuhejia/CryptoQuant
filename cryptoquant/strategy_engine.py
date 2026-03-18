from __future__ import annotations

from typing import Dict, List

from cryptoquant.indicators import ma20_volume
from cryptoquant.market_scanner import latest_ts
from cryptoquant.models import Candle, MarketSnapshot, Side, StrategySignal, Trend


class OneMinuteVolumeStrategy:
    """1分钟放量策略：趋势一致 + 1m成交量 > MA20*2。"""

    volume_multiplier: float = 2.0

    def evaluate(
        self,
        snapshots: List[MarketSnapshot],
        candles_1m: Dict[str, List[Candle]],
    ) -> List[StrategySignal]:
        signals: List[StrategySignal] = []
        for snap in snapshots:
            if snap.aligned_trend == Trend.RANGE:
                continue
            c1 = candles_1m.get(snap.symbol, [])
            if len(c1) < 20:
                continue
            volumes = [x.volume for x in c1]
            vol_ma20 = ma20_volume(volumes)
            latest = c1[-1]
            if latest.volume <= vol_ma20 * self.volume_multiplier:
                continue
            side = Side.LONG if snap.aligned_trend == Trend.BULL else Side.SHORT
            signals.append(
                StrategySignal(
                    symbol=snap.symbol,
                    side=side,
                    ts=latest_ts(c1),
                    reason="trend_aligned_and_volume_breakout",
                    ref_price=latest.close,
                    latest_1m_volume=latest.volume,
                    volume_ma20_1m=vol_ma20,
                )
            )
        return signals
