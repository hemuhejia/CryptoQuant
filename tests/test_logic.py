from cryptoquant.backtest import BacktestEngine, TradePnL
from cryptoquant.config import RiskConfig, StrategyConfig
from cryptoquant.market_scanner import MarketScanner, MockMarketDataSource
from cryptoquant.models import PortfolioState, Position, Side, Trend, Signal
from cryptoquant.portfolio_monitor import PortfolioMonitor
from cryptoquant.risk_engine import RiskEngine
from cryptoquant.strategy_engine import StrategyEngine


def _source() -> MockMarketDataSource:
    up = [100 + i * 0.5 for i in range(120)]
    down = [100 - i * 0.5 for i in range(120)]
    vol = [100] * 20 + [260]
    return MockMarketDataSource(
        {
            ("BTC", "5m", "close"): up,
            ("BTC", "15m", "close"): up,
            ("BTC", "1m", "volume"): vol,
            ("ETH", "5m", "close"): down,
            ("ETH", "15m", "close"): down,
            ("ETH", "1m", "volume"): vol,
        }
    )


def test_scanner_detects_trend_alignment():
    scanner = MarketScanner(_source(), symbols=("BTC", "ETH"))
    data = {s.symbol: s.tradable_trend for s in scanner.scan()}
    assert data["BTC"] == Trend.BULLISH
    assert data["ETH"] == Trend.BEARISH


def test_strategy_volume_spike_triggers_signal():
    ds = _source()
    scanner = MarketScanner(ds, symbols=("BTC",))
    strategy = StrategyEngine(ds, StrategyConfig())
    signal = strategy.evaluate(scanner.scan()[0])
    assert signal is not None
    assert signal.side == Side.LONG


def test_risk_rejects_when_daily_loss_exceeded():
    risk = RiskEngine(RiskConfig())
    portfolio = PortfolioState(equity=8500, daily_start_equity=10000)
    decision = risk.evaluate(Signal(symbol="BTC", side=Side.LONG, reason="x"), portfolio)
    assert not decision.approved


def test_monitor_reduces_and_closes():
    data = _source()
    monitor = PortfolioMonitor(data)
    p = PortfolioState(equity=10000, daily_start_equity=10000, used_margin=1000)
    p.positions["BTC"] = Position("BTC", Side.LONG, 1, 100, 1000)

    # first: 2.6x (no action)
    assert monitor.check(p) == []

    # 5x reduce
    data.data[("BTC", "1m", "volume")] = [100] * 20 + [600]
    actions = monitor.check(p)
    assert actions and actions[0].action == "reduce_50pct"

    # 10x close all
    data.data[("BTC", "1m", "volume")] = [100] * 20 + [1100]
    actions = monitor.check(p)
    assert actions and actions[0].action == "close_all"


def test_backtest_metrics():
    engine = BacktestEngine()
    result = engine.run_daily([TradePnL(100, 5, 2), TradePnL(-50, 4, 1)], 10000)
    assert result.trade_count == 2
    assert result.fees == 9
    assert result.funding == 3
