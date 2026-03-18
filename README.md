# Hyperliquid 全量化交易系统（参考实现）

这是一个按你给出的六层需求搭建的 Python 参考工程，包含：

1. 市场扫描引擎层（BTC/ETH，5m+15m 均线过滤）
2. 策略引擎层（1m 放量触发）
3. 系统风控层（账户、组合、持仓占比等限制）
4. 执行交易层（逐仓、杠杆、市价、滑点、止盈止损）
5. 回测层（按日汇总核心指标）
6. 持仓监控层（放量主动减仓/平仓）

> 说明：该项目是可运行的策略框架与逻辑实现，默认使用 `MockMarketDataSource` 进行演示；接入真实 Hyperliquid API 时只需实现同一数据源接口。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m cryptoquant.main
pytest
```

## 架构映射（对应需求）

- `cryptoquant/market_scanner.py`：扫描 BTC/ETH，判定 5m/15m 是否同向排列。
- `cryptoquant/strategy_engine.py`：在趋势通过后，检查 1m 成交量是否 > MA20 的 2 倍并发信号。
- `cryptoquant/risk_engine.py`：执行日亏损、单标的、持仓数量、保证金占比等风控。
- `cryptoquant/execution_engine.py`：生成订单参数（逐仓、10x、市价、滑点、止盈止损）。
- `cryptoquant/backtest.py`：产出交易次数、收益率、胜率、盈亏比、最大回撤、净利润、手续费、资金费、夏普。
- `cryptoquant/portfolio_monitor.py`：对持仓标的进行 5x/10x 放量减仓/平仓。

