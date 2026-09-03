# Phase 5 — Trading Costs and Execution Realism

## Objective

Adjust Phase 4 evaluation so that reported P&L reflects basic execution costs: fees, spread, and slippage.

This phase does not attempt to optimize parameters or claim a trading edge. It makes measurement closer to market reality before later robustness work.

## Research question

If a strategy appears profitable on gross P&L, does it remain acceptable after fees, spread, and slippage?

This phase does not attempt to answer whether a profitable strategy exists. It extends the Phase 4 measurement layer with a simple cost model that can later be compared against gross results.

## What we learned

### Layered construction

Execution costs were built in the same incremental style as Phases 3 and 4:

```text
Trade (from Phase 4 bridge)
  ↓
ExecutionCostConfig
  ↓
Fees / spread / slippage (unit-tested on synthetic trades)
  ↓
net_pnl(trade, config)
  ↓
evaluate_trades(trades, config) → EvaluationReport
  ↓
Real baseline backtest (gross vs net)
```

Each cost component was validated independently before combination and NautilusTrader integration. `BaselineStrategy` was not modified.

### Execution costs module

`tests/execution_costs.py` defines:

- `ExecutionCostConfig` with `fee_rate`, `spread`, and `slippage` (all non-negative)
- `calculate_fee(price, quantity, fee_rate)`
- `net_pnl(trade, config)` using effective entry/exit prices
- `EvaluationReport` with gross/net P&L and cost decomposition
- `evaluate_trades(trades, config)` for aggregate net metrics

Effective prices:

```text
entry_effective = entry_price + spread/2 + slippage
exit_effective  = exit_price  - spread/2 - slippage
```

Cost decomposition per trade (monetary impact, reported as positive costs):

```text
spread_cost   = spread × quantity
slippage_cost = 2 × slippage × quantity
fees          = entry fee + exit fee (on effective prices)
net_pnl       = gross_pnl - fees - spread_cost - slippage_cost
```

Win/loss metrics in the net report (`win_count`, `average_win`, `average_loss`, `expectancy`) are computed from **net P&L per trade**, not gross.

Gross evaluation (`backtest_metrics.evaluate_trades`) and net evaluation (`execution_costs.evaluate_trades`) remain separate layers.

### Cost model

#### Fees

Commission applied on entry and exit:

```text
fee = price × quantity × fee_rate
```

Example with `fee_rate = 0.001`:

```text
BUY  100 × 10 → fee 1.0
SELL 110 × 10 → fee 1.1
gross P&L = +100
net P&L   = +97.9
```

#### Spread

Execution price differs from the mid price:

```text
BUY at ask, SELL at bid
```

Even without price movement, a round trip can lose the spread.

Example with `spread = 2.0`, `100 → 110 × 10`:

```text
gross P&L = +100
net P&L   = +80.0
spread_cost = 20.0
```

#### Slippage

Actual fill price differs from the expected signal price by a fixed amount per side.

Example with `slippage = 1.0`, `100 → 110 × 10`:

```text
gross P&L = +100
net P&L   = +80.0
slippage_cost = 20.0
```

#### Combined

Example with all three costs on `100 → 110 × 10`:

```text
fee_rate = 0.001, spread = 2.0, slippage = 1.0

gross P&L     = +100.0
fees          =   2.1
spread_cost   =  20.0
slippage_cost =  20.0
net P&L       = +57.9
```

### Integration backtest

`tests/test_baseline_backtest.py` reuses the Phase 4 pipeline and adds gross vs net assertions:

1. Run the baseline backtest on synthetic catalog data.
2. Convert closed positions to `Trade` objects.
3. Report gross metrics via `backtest_metrics.evaluate_trades()`.
4. Apply `execution_costs.evaluate_trades()` with a cost configuration.
5. Assert gross and net outcomes match expected values.

Reference scenario (same synthetic bars as Phase 4):

```text
100, 100, 100, 110, 110, 90
                 ↑         ↑
                BUY       SELL
```

With `fee_rate = 0.001`, `spread = 2.0`, `slippage = 1.0`:

| Metric | Gross | Net |
|--------|------:|----:|
| P&L | -20.0 | -24.2 |
| Fees | — | 0.2 |
| Spread cost | — | 2.0 |
| Slippage cost | — | 2.0 |
| Total execution impact | — | 4.2 |

Trade detail: entry `110` → exit `90` × `1`.

Recorded results: [Phase 5 Results](phase-5-results.md).

The backtest confirms:

- Phase 4 gross evaluation still passes;
- net P&L with zero costs equals gross P&L;
- net P&L with costs applied matches the synthetic cost model on a real Nautilus closed position;
- the full evaluation report (fees, spread, slippage, net metrics) is reproducible.

### Validation

Command:

```bash
uv run pytest -v
```

Result on 2026-09-02:

| Area | Tests | Status |
|------|-------|--------|
| Prior phases (Phases 0–4) | 52 | passed |
| Execution costs unit tests | 13 | passed |

All **65** tests passed.

A worse net P&L than gross on this scenario validates the execution-cost measurement pipeline, not strategy quality.

Current limitations:

- cost parameters are fixed constants, not calibrated from real market data;
- no order book, market impact, or venue-specific fee schedules;
- tests use synthetic bars and a single forced BUY/SELL cycle;
- only one completed trade is measured in the reference scenario;
- `max_drawdown` and other gross-only metrics are not yet reported in the net evaluation report;
- no parameter search or out-of-sample validation has been performed;
- a profitable or unprofitable result on synthetic data must not be interpreted as strategy evidence.

## Research principles established

Cost modeling must be testable independently of the strategy and the engine whenever possible.

Gross and net results must both be reported so cost impact stays visible.

A strategy that looks acceptable before costs may fail after costs. That is a measurement outcome, not proof of edge or failure on its own.

No parameter search belongs in this phase.

Reporting must stay separate from interpretation: cost metrics describe execution drag; conclusions about edge require later phases.

## What we are not doing

- We are not claiming profitability.
- We are not optimizing `short_window` / `long_window`.
- We are not using real historical market data yet.
- We are not modeling every venue-specific fee schedule in detail.
- We are not modeling order books, market impact, or dynamic spread.
- We are not implementing risk management, take-profit, or stop-loss.
- We are not running walk-forward or out-of-sample studies yet.
- We are not connecting to a live exchange.

## Evaluation philosophy

Future experiments should compare gross and net performance using appropriate measures such as:

- total return;
- gross vs net P&L;
- maximum drawdown;
- win rate;
- average win and average loss;
- expectancy;
- profit factor;
- number of trades;
- fees, spread, and slippage;
- performance across different market regimes;
- out-of-sample performance;
- robustness to reasonable parameter changes.

No single metric, including raw profit, is sufficient on its own.

Phase 5 establishes a reproducible gross vs net measurement layer. Interpreting those numbers as strategy quality still requires more data, risk constraints, and robustness checks.

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

Phase 5 is complete when:

- a simple execution cost model is defined and documented;
- the fee model is unit-tested on synthetic trades;
- the spread model is unit-tested on synthetic trades;
- the slippage model is unit-tested on synthetic trades;
- gross and net metrics can be compared from the baseline backtest;
- limitations are recorded;
- no claim of trading edge is made from synthetic results alone.

All criteria are met. Recorded in [Phase 5 Results](phase-5-results.md).

The next phase is risk management: position sizing and loss constraints applied after realistic cost measurement.
