# Phase 4 — Backtest Evaluation

## Objective

Measure what the Phase 3 baseline strategy produces in a backtest, using a small set of well-defined trading metrics.

This phase does not attempt to optimize parameters or claim a trading edge. It establishes how to evaluate a strategy correctly before searching for better ones.

## Research question

Given a completed NautilusTrader backtest of `BaselineStrategy`, can we compute reproducible trading metrics (trades, P&L, win rate, expectancy, and drawdown) from the resulting fills?

This phase does not attempt to answer whether a profitable strategy exists. It establishes a measurement layer that can later support comparison and robustness work.

## What we learned

### Layered construction

Evaluation was built in the same incremental style as Phase 3:

```text
Trade
  ↓
Metrics (unit-tested on synthetic trades)
  ↓
Position → Trade bridge
  ↓
Real baseline backtest
  ↓
GrossEvaluationReport
```

Each layer has dedicated tests. Metrics are validated independently before NautilusTrader wiring.

### Metrics module

`src/trading_research/evaluation/metrics.py` defines:

- `Trade` with P&L from `(exit_price - entry_price) × quantity`
- aggregate metrics: `trade_count`, `total_pnl`, `win_count`, `loss_count`, `win_rate`, `average_win`, `average_loss`, `expectancy`, `max_drawdown`
- `GrossEvaluationReport` via `evaluate_gross(trades)`
- `position_to_trade(position)` and `trades_from_closed_positions(positions)`

Signed conventions:

- `average_win` is positive
- `average_loss` is negative
- `expectancy = win_rate × average_win + (1 - win_rate) × average_loss`
- `max_drawdown` is the largest peak-to-trough decline on the cumulative realized P&L curve (reported as a positive magnitude)

Definitions used in this phase:

- A **trade** is a completed round trip: entry fill(s) closed by exit fill(s). For the long-only baseline, that means BUY then SELL.
- **P&L** for a trade is computed from fill prices and quantity, before modeling fees, spread, or slippage in detail.
- A **win** is a trade with P&L `> 0`.
- A **loss** is a trade with P&L `< 0`.
- A trade with P&L `== 0` is neither a win nor a loss; it still counts in `trade_count`.
- Metrics are guarded when there are zero trades (no division by zero).

Example with two trades (`+100`, `-50`):

```text
win_rate     = 0.5
average_win  = +100
average_loss = -50
expectancy   = 0.5 × 100 + 0.5 × (-50) = +25
max_drawdown = 50
```

`profit_factor` is deferred to later work.

### NautilusTrader bridge

Closed positions expose:

- `avg_px_open`
- `avg_px_close`
- `peak_qty` (not `quantity`, which is `0` after a position closes)

The bridge converts closed positions into `Trade` objects without modifying `BaselineStrategy`.

### Integration backtest

`tests/integration/test_baseline_backtest.py` reuses the Phase 3 pipeline and adds evaluation assertions:

1. Run the baseline backtest on synthetic catalog data.
2. Read closed positions from `engine.cache.positions()`.
3. Convert them to `Trade` objects.
4. Build a `GrossEvaluationReport` with `evaluate_gross()`.

Synthetic closes with `short_window=2` and `long_window=3`:

```text
100, 100, 100, 110, 110, 90
                 ↑         ↑
                BUY       SELL
```

Measured outcome:

| Metric | Value |
|--------|------:|
| `trade_count` | 1 |
| `total_pnl` | -20 |
| `win_count` | 0 |
| `loss_count` | 1 |
| `win_rate` | 0.0 |
| `average_win` | 0.0 |
| `average_loss` | -20.0 |
| `expectancy` | -20.0 |
| `max_drawdown` | 20.0 |

Trade detail: entry `110` → exit `90` × `1` → P&L `-20`.

Recorded results: [Phase 4 Results](../results/phase-4-results.md).

The backtest confirms:

- Phase 3 execution assertions still pass;
- one completed round-trip trade is measured;
- the evaluation report matches the expected synthetic loss.

### Validation

Command:

```bash
uv run pytest -v
```

Result on 2026-08-27:

| Area | Tests | Status |
|------|-------|--------|
| Phase 2 environment / catalog / minimal backtest | 3 | passed |
| Baseline config | 7 | passed |
| SMA | 1 | passed |
| Crossover | 4 | passed |
| Signal / position | 6 | passed |
| Order submission (mocked factory layer) | 5 | passed |
| Metrics unit tests | 25 | passed |
| Baseline backtest evaluation | 1 | passed |

All 52 tests passed.

A negative P&L on this scenario validates the measurement pipeline, not strategy quality.

Current limitations:

- tests use synthetic bars and a single forced BUY/SELL cycle, not real market data;
- only one completed trade is measured in the reference scenario;
- transaction costs, spread, and slippage are not yet modeled in detail;
- `profit_factor`, Sharpe, and other advanced statistics are not computed yet;
- no parameter search or out-of-sample validation has been performed;
- a profitable or unprofitable result on synthetic data must not be interpreted as strategy evidence.

## Research principles established

Measurement must be defined and tested independently of the strategy and the engine whenever possible.

A metric module that fails on known synthetic trades is not ready to interpret a backtest.

A positive or negative P&L on synthetic data does not imply an edge. It only shows that measurement and execution are consistent for that scenario.

No parameter search belongs in this phase. Correct measurement comes before optimization.

Reporting must stay separate from interpretation: metrics describe what happened; conclusions about edge require later phases.

## What we are not doing

- We are not claiming profitability.
- We are not optimizing `short_window` / `long_window`.
- We are not searching for the “best” parameter set.
- We are not using real historical market data yet.
- We are not modeling realistic fees, spread, or slippage in detail.
- We are not implementing risk management, take-profit, or stop-loss.
- We are not computing Sharpe or other advanced portfolio statistics yet.
- We are not running walk-forward or out-of-sample studies yet.
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

Phase 4 establishes the first reproducible measurement layer. Interpreting those numbers as strategy quality still requires later cost realism, more data, and robustness checks.

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

Phase 4 is complete when:

- metrics are defined and documented;
- a metrics module computes the initial set from trade results;
- unit tests cover known synthetic trade outcomes;
- the baseline backtest can report trade count, P&L, win rate, expectancy, and max drawdown;
- limitations are recorded;
- no claim of trading edge is made from synthetic results alone.

The next phase is trading costs and execution realism: measure performance under more realistic fee, spread, and slippage assumptions.
