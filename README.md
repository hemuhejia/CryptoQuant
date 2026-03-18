# CryptoQuant - Hyperliquid 全量化交易系统

该仓库实现了一个可运行的分层交易系统骨架，对应你的六层需求：

1. 市场扫描引擎：仅扫描 BTC/ETH，筛选 5m + 15m 同向均线结构（EMA8, EMA21, MA50）。
2. 策略引擎：1m 放量策略（最新成交量 > MA20 的 2 倍）。
3. 系统风控：日亏损、单标的仓位、总仓位数量、总保证金占比、单次资金分配限制。
4. 执行交易：逐仓、默认 10x、市价+滑点、止损止盈计算、交易记录。
5. 回测层：统计交易次数、收益率、胜率、盈亏比、最大回撤、净利润、手续费、资金费、夏普。
6. 持仓监控：量能 >5x 时减仓 50%，>10x 时平仓。

## 快速开始

```bash
python -m pip install -e .[dev]
pytest -q
```

## 代码结构

- `cryptoquant/market_scanner.py`: 行情扫描与趋势过滤
- `cryptoquant/strategy_engine.py`: 1分钟放量策略
- `cryptoquant/risk_engine.py`: 投资组合风控
- `cryptoquant/execution_engine.py`: 下单参数与执行记录
- `cryptoquant/portfolio_monitor.py`: 主动减仓逻辑
- `cryptoquant/backtest.py`: 回测统计汇总
- `cryptoquant/system.py`: 总编排入口

