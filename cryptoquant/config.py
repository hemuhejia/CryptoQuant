from dataclasses import dataclass


@dataclass(frozen=True)
class StrategyConfig:
    trend_symbols: tuple[str, ...] = ("BTC", "ETH")
    volume_spike_multiplier: float = 2.0


@dataclass(frozen=True)
class RiskConfig:
    max_daily_loss_ratio: float = 0.10
    max_single_symbol_margin_ratio: float = 0.20
    max_positions: int = 5
    max_total_margin_ratio: float = 1.00
    max_alloc_per_trade_ratio: float = 0.20


@dataclass(frozen=True)
class ExecutionConfig:
    leverage: int = 10
    isolated: bool = True
    slippage_ratio: float = 0.001
    stop_loss_ratio: float = 0.02
    take_profit_ratio: float = 0.05
