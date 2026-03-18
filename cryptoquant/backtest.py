from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class TradePnL:
    pnl: float
    fee: float
    funding: float


@dataclass
class BacktestMetrics:
    trade_count: int
    return_pct: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    net_profit: float
    fees: float
    funding: float
    sharpe: float


class BacktestEngine:
    def run_daily(self, trades: list[TradePnL], initial_equity: float) -> BacktestMetrics:
        equity = initial_equity
        peak = equity
        max_dd = 0.0

        gross_profit = 0.0
        gross_loss = 0.0
        wins = 0
        returns: list[float] = []

        total_fees = sum(t.fee for t in trades)
        total_funding = sum(t.funding for t in trades)

        for t in trades:
            net = t.pnl - t.fee - t.funding
            equity += net
            r = net / max(initial_equity, 1e-9)
            returns.append(r)

            if net > 0:
                wins += 1
                gross_profit += net
            elif net < 0:
                gross_loss += abs(net)

            peak = max(peak, equity)
            dd = (peak - equity) / max(peak, 1e-9)
            max_dd = max(max_dd, dd)

        trade_count = len(trades)
        net_profit = equity - initial_equity
        return_pct = (net_profit / initial_equity) * 100 if initial_equity else 0.0
        win_rate = (wins / trade_count) * 100 if trade_count else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

        sharpe = 0.0
        if returns:
            mean_r = sum(returns) / len(returns)
            variance = sum((x - mean_r) ** 2 for x in returns) / len(returns)
            std = math.sqrt(variance)
            sharpe = mean_r / std if std > 0 else 0.0

        return BacktestMetrics(
            trade_count=trade_count,
            return_pct=return_pct,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            net_profit=net_profit,
            fees=total_fees,
            funding=total_funding,
            sharpe=sharpe,
        )
