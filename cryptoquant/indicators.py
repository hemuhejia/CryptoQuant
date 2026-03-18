from __future__ import annotations


def sma(values: list[float], period: int) -> float:
    if period <= 0 or len(values) < period:
        raise ValueError("insufficient values for SMA")
    window = values[-period:]
    return sum(window) / period


def ema(values: list[float], period: int) -> float:
    if period <= 0 or len(values) < period:
        raise ValueError("insufficient values for EMA")
    k = 2 / (period + 1)
    ema_value = sum(values[:period]) / period
    for price in values[period:]:
        ema_value = price * k + ema_value * (1 - k)
    return ema_value


def ma20_volume(volumes: list[float]) -> float:
    return sma(volumes, 20)
