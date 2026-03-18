from __future__ import annotations

from .backtest import BacktestEngine, TradePnL
from .config import ExecutionConfig, RiskConfig, StrategyConfig
from .execution_engine import ExecutionEngine
from .market_scanner import MarketScanner, MockMarketDataSource
from .portfolio_monitor import PortfolioMonitor
from .risk_engine import RiskEngine
from .strategy_engine import StrategyEngine
from .models import PortfolioState


def _mock_data() -> dict[tuple[str, str, str], list[float]]:
    up = [100 + i * 0.3 for i in range(120)]
    down = [200 - i * 0.2 for i in range(120)]
    vol_normal = [100 + (i % 7) for i in range(40)]

    return {
        ("BTC", "5m", "close"): up,
        ("BTC", "15m", "close"): up,
        ("BTC", "1m", "volume"): vol_normal[:-1] + [250],
        ("ETH", "5m", "close"): down,
        ("ETH", "15m", "close"): down,
        ("ETH", "1m", "volume"): vol_normal[:-1] + [240],
    }


def run_once() -> None:
    data_source = MockMarketDataSource(_mock_data())

    scanner = MarketScanner(data_source, symbols=("BTC", "ETH"))
    strategy = StrategyEngine(data_source, StrategyConfig())
    risk = RiskEngine(RiskConfig())
    execution = ExecutionEngine(ExecutionConfig())
    monitor = PortfolioMonitor(data_source)

    portfolio = PortfolioState(equity=10000, daily_start_equity=10000)

    for snapshot in scanner.scan():
        signal = strategy.evaluate(snapshot)
        if not signal:
            continue
        decision = risk.evaluate(signal, portfolio)
        if not decision.approved:
            continue
        execution.execute(
            signal=signal,
            allocation=decision.allocation,
            mark_price=50000 if signal.symbol == "BTC" else 3000,
            previous_candle_low=49500 if signal.symbol == "BTC" else 2900,
            portfolio=portfolio,
        )

    actions = monitor.check(portfolio)

    backtest = BacktestEngine()
    metrics = backtest.run_daily(
        [TradePnL(pnl=80, fee=5, funding=2), TradePnL(pnl=-40, fee=4, funding=1)],
        initial_equity=10000,
    )

    print("Trades:", len(execution.trade_log))
    print("Risk actions:", actions)
    print("Backtest:", metrics)


if __name__ == "__main__":
    run_once()
