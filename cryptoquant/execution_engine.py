from __future__ import annotations

from datetime import datetime

from cryptoquant.models import ExecutionConfig, OrderRequest, Side, TradeRecord
from cryptoquant.risk_engine import ApprovedTrade


class ExecutionEngine:
    def __init__(self, config: ExecutionConfig | None = None) -> None:
        self.config = config or ExecutionConfig()

    def build_order(self, approved: ApprovedTrade) -> OrderRequest:
        signal = approved.signal
        price = signal.ref_price
        # 模拟市价单滑点
        fill_base = price * (1 + self.config.slippage) if signal.side == Side.LONG else price * (1 - self.config.slippage)
        quantity = (approved.margin_to_use * self.config.leverage) / fill_base

        stop_loss = self._stop_loss(signal.side, fill_base)
        take_profit = self._take_profit(signal.side, fill_base)

        return OrderRequest(
            symbol=signal.symbol,
            side=signal.side,
            quantity=quantity,
            price=fill_base,
            leverage=self.config.leverage,
            isolated=self.config.isolated,
            slippage=self.config.slippage,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    def _stop_loss(self, side: Side, price: float) -> float:
        if side == Side.LONG:
            return price * (1 - self.config.stop_loss_pct)
        return price * (1 + self.config.stop_loss_pct)

    def _take_profit(self, side: Side, price: float) -> float:
        if side == Side.LONG:
            return price * (1 + self.config.take_profit_pct)
        return price * (1 - self.config.take_profit_pct)

    def execute(self, order: OrderRequest) -> TradeRecord:
        # 此处可替换为Hyperliquid实际下单API
        notional = order.quantity * order.price
        fee = notional * 0.0005
        funding = notional * 0.0001
        return TradeRecord(order=order, filled_price=order.price, fee=fee, funding_cost=funding, ts=datetime.utcnow())
