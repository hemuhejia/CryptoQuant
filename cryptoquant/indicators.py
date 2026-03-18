from __future__ import annotations

from statistics import fmean
from typing import Iterable, List


def sma(values: Iterable[float], period: int) -> float:
    seq = list(values)
    if len(seq) < period:
        raise ValueError("insufficient data for SMA")
    return fmean(seq[-period:])


def ema(values: Iterable[float], period: int) -> float:
    seq = list(values)
    if len(seq) < period:
        raise ValueError("insufficient data for EMA")
    k = 2 / (period + 1)
    ema_val = fmean(seq[:period])
    for value in seq[period:]:
        ema_val = value * k + ema_val * (1 - k)
    return ema_val


def ma20_volume(volumes: Iterable[float]) -> float:
    return sma(list(volumes), 20)


def calc_trend(closes: List[float]) -> str:
    ema8 = ema(closes, 8)
    ema21 = ema(closes, 21)
    ma50 = sma(closes, 50)
    if ema8 > ema21 > ma50:
        return "bull"
    if ema8 < ema21 < ma50:
        return "bear"
    return "range"
