# Phase 5 Results

## Baseline strategy: gross vs net evaluation

This report records the first reproducible comparison of gross and net P&L for `BaselineStrategy`, using the Phase 5 execution cost layer on top of the Phase 4 evaluation pipeline.

It does not claim strategy success or failure. The objective was to validate the execution-cost measurement pipeline, not the profitability of the strategy.

## Scenario

Same synthetic backtest as Phase 4, validated end-to-end through NautilusTrader:

- Synthetic bars from `tests/integration/test_baseline_backtest.py`
- Instrument: `AAPL.XNAS`
- Bar type: `AAPL.XNAS-1-MINUTE-LAST-EXTERNAL`
- `short_window`: 2
- `long_window`: 3
- `trade_size`: 1

Closes:

```text
100, 100, 100, 110, 110, 90
                 ↑         ↑
                BUY       SELL
```

Execution detail:

- BUY fill at `110`
- SELL fill at `90`
- Completed round-trip quantity: `1`

Execution cost configuration:

| Parameter | Value |
|-----------|------:|
| `fee_rate` | 0.001 |
| `spread` | 2.0 |
| `slippage` | 1.0 |

Pipeline:

```text
Nautilus Position
      ↓
position_to_trade()
      ↓
Trade (110 → 90 × 1)
      ↓
evaluate_net(config)
      ↓
NetEvaluationReport
```

## Result

### Gross vs net

```text
Nautilus round-trip
110 → 90 × 1

Gross P&L       -20.0
Fees             -0.2
Spread           -2.0
Slippage         -2.0
----------------------
Net P&L         -24.2
```

Total execution impact: **4.2** (21% worse than gross on this single trade).

### Evaluation report

| Metric | Gross (Phase 4) | Net (Phase 5) |
|--------|----------------:|--------------:|
| Trades | 1 | 1 |
| P&L | -20.0 | -24.2 |
| Win count | 0 | 0 |
| Loss count | 1 | 1 |
| Win rate | 0.0 | 0.0 |
| Average win | 0.0 | 0.0 |
| Average loss | -20.0 | -24.2 |
| Expectancy | -20.0 | -24.2 |

Cost breakdown (net report):

| Component | Impact |
|-----------|-------:|
| Fees | 0.2 |
| Spread cost | 2.0 |
| Slippage cost | 2.0 |
| **Total cost** | **4.2** |

Effective prices for this trade:

```text
BUY  = 110 + spread/2 + slippage = 112
SELL = 90  - spread/2 - slippage = 88
```

Reproduce with:

```bash
uv run pytest tests/integration/test_baseline_backtest.py -v
```

Full suite:

```bash
uv run pytest -v
```

On 2026-09-02: **65 passed**.

## Interpretation

This result does not demonstrate strategy failure or success.

What it does show:

- gross P&L and net P&L can be reported side by side from the same Nautilus round-trip;
- execution costs degrade the measured outcome on a losing trade (-20.0 → -24.2);
- fees, spread, and slippage are decomposed explicitly in the evaluation report;
- win rate, average loss, and expectancy are computed from **net P&L per trade**, not gross.

The synthetic winning scenario (`100 → 110 × 10`) was used only to unit-test the cost model with known answers. It is not evidence of profitability.

> Phase 5 validates the execution-cost measurement pipeline, not the profitability of the strategy.

## Limitations

The cost model is intentionally simplified:

- proportional fees (`fee_rate × price × quantity`);
- fixed spread per unit;
- fixed slippage per side;
- no order book or liquidity model;
- no market impact;
- no venue-specific fee schedules;
- cost parameters are not calibrated from real historical market data.

Additional scope limits:

- one synthetic scenario with a single completed trade;
- `BaselineStrategy` was not modified; costs are applied after the backtest;
- gross evaluation (`evaluate_gross`) and net evaluation (`evaluate_net`) remain separate layers;
- no parameter search or out-of-sample validation was performed.

## What Phase 5 allows us to conclude

- A layered pipeline exists: backtest → raw trades → execution costs → gross/net evaluation report.
- Each cost component (fees, spread, slippage) is unit-tested independently and in combination.
- The same mechanics work on synthetic trades and on a real Nautilus closed position.
- Reported net metrics reflect execution drag, not just mid-price P&L.

## What Phase 5 does not allow us to conclude

- That the strategy is profitable or unprofitable in real markets.
- That the chosen fee, spread, and slippage values are realistic for any specific venue.
- That a strategy acceptable on gross P&L would fail or survive after costs in general.
- That synthetic test scenarios represent tradable edge.

## Phase 5 conclusion

Phase 5 is complete. The project can now measure and report execution costs on top of backtest results before applying risk constraints.

The next phase is risk management: position sizing and loss limits applied after realistic cost measurement.
