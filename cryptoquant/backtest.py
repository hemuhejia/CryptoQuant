from __future__ import annotations

from statistics import fmean, pstdev

from cryptoquant.models import BacktestReport, TradeRecord


class Backtester:
    """每日回测统计聚合器。"""

    def summarize(self, records: list[TradeRecord], initial_equity: float) -> BacktestReport:
        pnls: list[float] = []
        fees = 0.0
        funding = 0.0
        wins = 0

        # 演示：若订单到达止盈则记盈利，否则记小亏损
        for rec in records:
            notional = rec.order.price * rec.order.quantity
            est_pnl = notional * 0.01
            pnls.append(est_pnl - rec.fee - rec.funding_cost)
            fees += rec.fee
            funding += rec.funding_cost
            if est_pnl > 0:
                wins += 1

        trades = len(records)
        net = sum(pnls)
        ret_pct = (net / initial_equity * 100) if initial_equity else 0.0
        win_rate = wins / trades if trades else 0.0

        gross_profit = sum(x for x in pnls if x > 0)
        gross_loss = abs(sum(x for x in pnls if x < 0))
        profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

        max_dd = self._max_drawdown(pnls, initial_equity)
        sharpe = self._sharpe_ratio(pnls)

        return BacktestReport(
            trades=trades,
            return_pct=ret_pct,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            net_profit=net,
            fees=fees,
            funding_cost=funding,
            sharpe_ratio=sharpe,
            raw_returns=pnls,
        )

    def _max_drawdown(self, pnls: list[float], initial_equity: float) -> float:
        equity = initial_equity
        peak = equity
        max_dd = 0.0
        for pnl in pnls:
            equity += pnl
            peak = max(peak, equity)
            if peak > 0:
                max_dd = max(max_dd, (peak - equity) / peak)
        return max_dd

    def _sharpe_ratio(self, returns: list[float]) -> float:
        if len(returns) < 2:
            return 0.0
        avg = fmean(returns)
        sd = pstdev(returns)
        if sd == 0:
            return 0.0
        return avg / sd
