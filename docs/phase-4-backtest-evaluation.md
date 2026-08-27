# Phase 4 — Backtest Evaluation

## Objective

Measure what the Phase 3 baseline strategy produces in a backtest, using a small set of well-defined trading metrics.

This phase does not attempt to optimize parameters or claim a trading edge. It establishes how to evaluate a strategy correctly before searching for better ones.

## Research question

Given a completed NautilusTrader backtest of `BaselineStrategy`, can we compute reproducible trading metrics (trades, P&L, win rate, expectancy, and later drawdown) from the resulting fills?

This phase does not attempt to answer whether a profitable strategy exists. It establishes a measurement layer that can later support comparison and robustness work.

## Planned approach

The work is layered, in the same spirit as Phase 3:

```text
BaselineStrategy
      ↓
Backtest
      ↓
Trades
      ↓
Metrics
      ↓
P&L / Win Rate / Expectancy / Drawdown
      ↓
Evaluation
```

Incremental milestones:

1. Define metrics and document assumptions.
2. Implement a small metrics module.
3. Unit-test metrics on synthetic trades with known answers.
4. Connect metrics to the real baseline backtest.
5. Record and interpret results without claiming an edge.

## Metrics

### Initial set

| Metric | Meaning |
|--------|---------|
| `trade_count` | Number of completed round-trip trades |
| `total_pnl` | Sum of realized P&L across completed trades |
| `win_count` | Number of trades with positive P&L |
| `loss_count` | Number of trades with negative P&L |
| `win_rate` | `win_count / trade_count` when `trade_count > 0` |
| `average_win` | Mean P&L of winning trades (positive) |
| `average_loss` | Mean P&L of losing trades (**negative**) |
| `expectancy` | Expected P&L per trade: `win_rate * average_win + (1 - win_rate) * average_loss` |

### Later additions

| Metric | Meaning |
|--------|---------|
| `max_drawdown` | Largest peak-to-trough decline on the equity curve from realized P&L |
| `profit_factor` | Gross profits divided by gross losses (when losses are non-zero) |

### Definitions used in this phase

- A **trade** is a completed round trip: entry fill(s) closed by exit fill(s). For the long-only baseline, that means BUY then SELL.
- **P&L** for a trade is computed from fill prices and quantity, before modeling fees, spread, or slippage in detail.
- A **win** is a trade with P&L `> 0`.
- A **loss** is a trade with P&L `< 0`.
- A trade with P&L `== 0` is neither a win nor a loss; it still counts in `trade_count`.
- `average_win` is the mean of winning trade P&Ls and is positive.
- `average_loss` is the mean of losing trade P&Ls and is **negative** (not an absolute value).
- `expectancy` uses those signed values directly:
  `win_rate * average_win + (1 - win_rate) * average_loss`.
- Metrics are undefined or explicitly guarded when there are zero trades (no division by zero).

Example with two trades (`+100`, `-50`):

```text
win_rate     = 0.5
average_win  = +100
average_loss = -50
expectancy   = 0.5 × 100 + 0.5 × (-50) = +25
```

Exact formulas will be locked by unit tests on synthetic trades before any NautilusTrader wiring.

## Reference scenario

Reuse the Phase 3 synthetic integration backtest as the first real connection point:

```text
closes: 100, 100, 100, 110, 110, 90
windows: short=2, long=3
               ↑         ↑
              BUY       SELL
```

Phase 3 already proved that this scenario produces real BUY and SELL fills and ends flat. Phase 4 asks what metrics that single completed trade produces.

This remains infrastructure-plus-measurement evidence on synthetic data, not evidence of strategy quality.

## Research principles established

Measurement must be defined and tested independently of the strategy and the engine whenever possible.

A metric module that fails on known synthetic trades is not ready to interpret a backtest.

A positive P&L on synthetic data does not imply an edge. It only shows that measurement and execution are consistent for that scenario.

No parameter search belongs in this phase. Correct measurement comes before optimization.

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
- the baseline backtest can report at least trade count, P&L, win rate, and expectancy;
- limitations are recorded;
- no claim of trading edge is made from synthetic results alone.

The next phase after evaluation is trading costs and execution realism: measure performance under more realistic fee, spread, and slippage assumptions.
