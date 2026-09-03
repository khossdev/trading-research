# Phase 4 Results

## Baseline strategy evaluation

This report records the first reproducible evaluation of `BaselineStrategy` using the Phase 4 metrics layer.

It does not claim strategy success or failure. The objective was to validate measurement, not profitability.

## Scenario

- Synthetic bars from `tests/test_baseline_backtest.py`
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

## Result

| Metric | Value |
|--------|------:|
| Trades | 1 |
| Total P&L | -20 |
| Win count | 0 |
| Loss count | 1 |
| Win rate | 0.0 |
| Average win | 0.0 |
| Average loss | -20.0 |
| Expectancy | -20.0 |
| Max drawdown | 20.0 |

Reproduce with:

```bash
uv run pytest tests/test_baseline_backtest.py -v
```

Full suite:

```bash
uv run pytest -v
```

On 2026-08-27: **52 passed**.

## Interpretation

This result does not demonstrate strategy failure or success.

Reasons:

- the dataset is synthetic and designed to force one BUY/SELL cycle;
- there is only one completed trade;
- fees, spread, and slippage are not modeled in detail;
- no parameter search or out-of-sample validation was performed.

The negative P&L confirms that the evaluation pipeline can report what the backtest produced. It is measurement evidence, not evidence of a trading edge.

## Limitations

- closed Nautilus positions use `peak_qty`, not `quantity`, after flattening;
- P&L is computed from average entry/exit prices before detailed cost modeling;
- `profit_factor` and other advanced metrics are deferred to later work.

## Next step

Phase 5 will measure the same pipeline under more realistic trading costs: fees, spread, and slippage.
