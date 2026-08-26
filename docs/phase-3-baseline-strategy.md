# Phase 3 — First Baseline Strategy

## Objective

Build a minimal, deterministic baseline strategy that transforms market data into signals, market orders, and fills inside a real NautilusTrader backtest.

This phase does not attempt to produce a profitable strategy. It establishes a reproducible reference pipeline for later research.

## Research question

Can a simple SMA crossover strategy, built and tested in layers, produce real BUY and SELL fills in a NautilusTrader backtest on synthetic catalog data?

This phase does not attempt to answer whether a profitable strategy exists. It establishes a deterministic baseline pipeline that can later be measured and compared.

## What we learned

### Layered construction

The baseline was built and validated one layer at a time:

```text
Config
  ↓
SMA
  ↓
Crossover
  ↓
Signal
  ↓
Internal position
  ↓
Market order
  ↓
Real backtest
  ↓
BUY / SELL fills
```

Each layer has dedicated tests. Earlier layers remain independent of later ones.

### Configuration

`BaselineStrategyConfig` defines:

- `instrument_id`
- `bar_type`
- `short_window` (default 5)
- `long_window` (default 20)
- `trade_size` (default 1)

Validation rejects non-positive windows or size, and requires `long_window > short_window`.

`StrategyConfig` in NautilusTrader is a msgspec struct, so fields and `__post_init__` are used instead of a custom `__init__`.

### Indicators and signals

- Close prices are stored in a bounded deque.
- Short and long SMAs are computed with `statistics.fmean`.
- A crossover is a *transition*, not a level comparison:
  - short crossing above long → BUY candidate
  - short crossing below long → SELL candidate
- Signal generation is long-only:
  - BUY only when flat (`_position == 0`)
  - SELL only when long (`_position > 0`)

### Execution

Orders use the strategy instance `order_factory` and `submit_order`, consistent with Phase 2:

- BUY → `OrderSide.BUY`
- SELL → `OrderSide.SELL`

Unit tests of order intent mock `_submit_market_order` because `order_factory` is only available after the strategy is registered in a running engine.

### Integration backtest

`tests/test_baseline_backtest.py` reuses the Phase 2 pipeline:

1. Write instrument and synthetic bars to a Parquet catalog.
2. Load `BaselineStrategy` through `ImportableStrategyConfig`.
3. Run `BacktestNode` with `raise_exception=True` and `dispose_on_completion=False`.
4. Assert real orders and positions from the engine cache.

Synthetic closes with `short_window=2` and `long_window=3`:

```text
100, 100, 100, 110, 110, 90
                 ↑         ↑
                BUY       SELL
```

The backtest confirms:

- bars are consumed;
- at least one BUY is submitted and filled;
- at least one SELL is submitted and filled;
- no open positions remain at the end.

### Validation

Command:

```bash
uv run pytest -v
```

Result on 2026-08-26:

| Area | Tests | Status |
|------|-------|--------|
| Phase 2 environment / catalog / minimal backtest | 3 | passed |
| Baseline config | 7 | passed |
| SMA | 1 | passed |
| Crossover | 4 | passed |
| Signal / position | 6 | passed |
| Order submission (mocked factory layer) | 5 | passed |
| Integration backtest (real fills) | 1 | passed |

All 27 tests passed.

## Research principles established

A baseline strategy must be explainable and deterministic before any optimization.

Signal logic should be testable without the execution engine whenever possible.

Execution must still be proven in a real backtest, without mocks, before claiming the pipeline works.

A successful BUY/SELL cycle on synthetic data is infrastructure evidence, not evidence of a trading edge.

## What we are not doing

- We are not claiming profitability.
- We are not using machine learning.
- We are not optimizing parameters.
- We are not using real market data in this phase.
- We are not implementing take-profit or stop-loss.
- We are not implementing risk management.
- We are not modeling realistic fees, spread, or slippage in detail.
- We are not computing trading performance metrics in this phase (P&L summary, win rate, drawdown, Sharpe).
- We are not trading short positions.
- We are not connecting to a live exchange.

## Evaluation philosophy

Future experiments should be evaluated using appropriate measures such as:

- total return;
- volatility;
- maximum drawdown;
- win rate;
- average win and average loss;
- expectancy;
- profit factor;
- number of trades;
- exposure and turnover;
- fees, spread, and slippage;
- performance across different market regimes;
- out-of-sample performance;
- robustness to reasonable parameter changes.

No single metric, including raw profit, is sufficient on its own.

Phase 3 validates that a baseline strategy can execute end to end. It is not evidence of strategy quality. Recording and interpreting metrics belongs to Phase 4.

## Development workflow

Each phase follows the same loop:

1. Define the question.
2. Learn the required concepts.
3. Implement the smallest useful experiment.
4. Test it.
5. Record the result.
6. Review assumptions and limitations.
7. Commit the work.
8. Only then move to the next phase.

## Security

Secrets must never be committed. API credentials, private keys, exchange credentials, and local environment files remain outside version control.

## Exit criteria

Phase 3 is complete when:

- a baseline SMA strategy is implemented and documented;
- config, SMA, crossover, signal, and order layers are covered by tests;
- a real NautilusTrader backtest submits and fills BUY then SELL on synthetic data;
- the strategy finishes flat;
- limitations are recorded.

The next phase is backtesting evaluation: record basic trading metrics from backtest results (orders, fills, trades, P&L, win rate, trade count), still without claiming an edge.
