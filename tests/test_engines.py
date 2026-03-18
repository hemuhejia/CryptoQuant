from datetime import datetime, timedelta

from cryptoquant.backtest import Backtester
from cryptoquant.execution_engine import ExecutionEngine
from cryptoquant.market_scanner import MarketScanner
from cryptoquant.models import Candle, Portfolio, Position, Side, Trend
from cryptoquant.portfolio_monitor import PortfolioMonitor
from cryptoquant.risk_engine import RiskEngine
from cryptoquant.strategy_engine import OneMinuteVolumeStrategy


def _candles(symbol: str, timeframe: str, closes: list[float], volumes: list[float]) -> list[Candle]:
    t0 = datetime(2024, 1, 1)
    out = []
    for i, (c, v) in enumerate(zip(closes, volumes)):
        out.append(
            Candle(
                symbol=symbol,
                timeframe=timeframe,
                ts=t0 + timedelta(minutes=i),
                open=c,
                high=c,
                low=c,
                close=c,
                volume=v,
            )
        )
    return out


def test_market_scan_and_strategy_signal():
    up = [float(i) for i in range(1, 80)]
    vols = [100.0] * 25
    vols[-1] = 250.0
    data = {
        "BTC": {
            "5m": _candles("BTC", "5m", up, [10.0] * len(up)),
            "15m": _candles("BTC", "15m", up, [10.0] * len(up)),
            "1m": _candles("BTC", "1m", up[:25], vols),
        }
    }
    scanner = MarketScanner()
    snaps = scanner.scan(data)
    assert len(snaps) == 1
    assert snaps[0].aligned_trend == Trend.BULL

    strategy = OneMinuteVolumeStrategy()
    signals = strategy.evaluate(snaps, {"BTC": data["BTC"]["1m"]})
    assert len(signals) == 1
    assert signals[0].side == Side.LONG


def test_risk_engine_limits_and_execution():
    portfolio = Portfolio(equity=10_000)
    sig = type("S", (), {})()
    sig.symbol = "BTC"
    sig.side = Side.LONG
    sig.ref_price = 100.0

    from cryptoquant.models import StrategySignal

    signal = StrategySignal(
        symbol="BTC",
        side=Side.LONG,
        ts=datetime.utcnow(),
        reason="test",
        ref_price=100.0,
        latest_1m_volume=200,
        volume_ma20_1m=80,
    )

    risk = RiskEngine()
    approved = risk.approve(signal, portfolio)
    assert approved is not None
    assert approved.margin_to_use == 2000

    exe = ExecutionEngine()
    order = exe.build_order(approved)
    assert order.leverage == 10
    assert order.isolated is True
    assert order.stop_loss < order.price
    assert order.take_profit > order.price


def test_monitor_and_backtest():
    monitor = PortfolioMonitor()
    position = Position(symbol="ETH", side=Side.SHORT, size=1, entry_price=1000, margin_used=100)
    action = monitor.evaluate(position, latest_volume=1000, volume_ma20=100)
    assert action is not None
    assert action.action == "close"

    from cryptoquant.models import OrderRequest, TradeRecord

    rec = TradeRecord(
        order=OrderRequest(
            symbol="BTC",
            side=Side.LONG,
            quantity=1,
            price=100,
            leverage=10,
            isolated=True,
            slippage=0.001,
            stop_loss=98,
            take_profit=105,
        ),
        filled_price=100,
        fee=0.05,
        funding_cost=0.01,
        ts=datetime.utcnow(),
    )
    report = Backtester().summarize([rec], initial_equity=1000)
    assert report.trades == 1
    assert report.net_profit > 0
