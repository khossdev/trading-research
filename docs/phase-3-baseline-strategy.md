# Phase 3 — First Baseline Strategy

## Objective

Implement the first deterministic trading strategy on top of the NautilusTrader backtest infrastructure validated in Phase 2.

The purpose of this phase is **not** to find a profitable strategy. The purpose is to establish a simple, reproducible baseline that gives the research project a reference point for later experiments.

Phase 2 established that market data can reach a strategy and that a strategy can submit an order which is simulated through the backtest execution flow. Phase 3 adds an explicit, testable trading hypothesis on top of that infrastructure.

## Research question

Can a simple, rule-based trend-following strategy produce a measurable result on the selected historical data after the basic trading assumptions are applied?

A positive result is not considered evidence of future profitability. A negative result is also useful because it provides a baseline against which later ideas can be compared.

## Baseline hypothesis

The baseline hypothesis is that a short-term trend can be represented by the relationship between a short moving average and a longer moving average.

The strategy will use a simple moving-average crossover:

- when the short moving average crosses above the long moving average, the strategy generates a BUY signal;
- when the short moving average crosses below the long moving average, the strategy generates a SELL signal;
- the strategy holds at most one position at a time;
- the strategy uses a fixed quantity;
- the strategy does not use leverage;
- the strategy does not optimize its parameters during this phase.

The exact periods will be explicit configuration parameters rather than hidden constants.

## Why this baseline

The baseline should be simple enough that its behavior can be explained without ambiguity.

A moving-average crossover is suitable for this role because:

- it is deterministic;
- it uses only information available up to the current bar;
- it has a small number of understandable parameters;
- it naturally produces both entry and exit conditions;
- it can be tested with synthetic data;
- it provides a useful reference for later strategy research.

This choice is a research baseline, not a claim that moving-average crossovers are profitable.

## Data

The initial implementation will continue to use the local Parquet catalog and synthetic bar data established during Phase 2.

Initial assumptions:

- instrument: `AAPL.XNAS`;
- bar type: `AAPL.XNAS-1-MINUTE-LAST-EXTERNAL`;
- data source: local Parquet catalog;
- execution environment: NautilusTrader backtest;
- initial position size: fixed quantity of `1`.

Real market data is outside the initial implementation of this phase. Introducing real data should be a separate, explicit change so that data-source changes are not confused with strategy changes.

## Signal definition

Let:

- `S_t` be the short moving average at bar `t`;
- `L_t` be the long moving average at bar `t`.

A BUY crossover occurs when:

```text
S_(t-1) <= L_(t-1)
AND
S_t > L_t
```

A SELL crossover occurs when:

```text
S_(t-1) >= L_(t-1)
AND
S_t < L_t
```

The strategy must not generate a signal until enough bars exist to calculate both moving averages.

Only completed bars available to the strategy at decision time may be used. Future bars must never influence the current signal.

## Position rules

The baseline will use a single-position model.

### Entry

- BUY signal with no open position → submit one BUY market order for the configured quantity.
- BUY signal while already long → do nothing.

### Exit / reversal

- SELL signal while long → submit one SELL market order for the configured quantity to close the position.
- SELL signal while flat → do nothing.

Short positions are **out of scope for the first implementation**. This keeps the first baseline focused on one direction of exposure and makes the initial accounting and tests easier to reason about.

## Execution assumptions

Phase 2 already validated market-order submission and simulated execution.

Phase 3 will initially preserve that execution model rather than introducing several new execution variables at once.

The strategy will use market orders for the baseline. Detailed transaction-cost and execution-realism modeling is not the primary objective of this phase and will be addressed explicitly in the later execution/cost research work.

Any result from this baseline must therefore be interpreted together with its execution assumptions.

## Configuration

The baseline strategy should expose its research parameters explicitly through its configuration.

Initial parameters:

| Parameter | Meaning |
|---|---|
| `instrument_id` | Instrument traded by the strategy |
| `bar_type` | Bar stream used by the strategy |
| `short_window` | Number of bars in the short moving average |
| `long_window` | Number of bars in the long moving average |
| `trade_size` | Fixed position quantity |

Validation rules should reject invalid configurations, including:

- `short_window <= 0`;
- `long_window <= 0`;
- `short_window >= long_window`;
- `trade_size <= 0`.

The initial parameter values will be deliberately simple and should be recorded in the test/backtest configuration rather than hidden inside the strategy implementation.

## Testing strategy

Testing comes before interpreting backtest results.

The tests should verify the smallest useful behaviors independently and then verify the end-to-end backtest.

### Unit-level behavior

Synthetic bars should be constructed so that the expected moving-average relationship is known.

Tests should verify:

1. no signal is generated before enough bars are available;
2. a bullish crossover generates exactly one BUY signal;
3. repeated bullish bars do not generate repeated BUY orders while already long;
4. a bearish crossover generates a SELL signal while long;
5. no SELL order is submitted while already flat;
6. invalid strategy configuration is rejected;
7. the strategy does not use future bars when calculating a signal.

### End-to-end backtest

The integration test should reuse the Phase 2 pipeline:

```text
Parquet catalog
      ↓
BacktestDataConfig
      ↓
BacktestNode
      ↓
BaselineStrategy
      ↓
Market order
      ↓
Simulated execution
      ↓
Position
      ↓
Backtest result
```

The test should assert observable outcomes rather than only checking that `node.run()` completes.

At minimum, it should verify that:

- the backtest processes the expected bars;
- the strategy generates an expected trade;
- an order is submitted and executed;
- a position is opened and subsequently closed;
- the resulting order/position state is available from the backtest cache.

## Metrics

The first baseline report should record at least:

- initial capital;
- final capital;
- total P&L;
- number of trades;
- winning trades;
- losing trades;
- win rate;
- average win;
- average loss;
- maximum drawdown when available from the backtest result;
- exposure/holding information when available.

No single metric should be used to declare a strategy successful.

## Experimental discipline

The baseline is intended to establish a reference point.

Therefore:

- parameters must be declared explicitly;
- the data used for development must be identifiable;
- the experiment must be reproducible;
- results must be recorded with the assumptions used to obtain them;
- parameters must not be optimized against an evaluation dataset;
- changes to data, execution assumptions, or strategy rules must be distinguishable in version control.

Development and out-of-sample evaluation are not combined in this phase. A later validation phase will define the separation more formally.

## What this phase does not do

Phase 3 does **not** attempt to:

- prove profitability;
- trade real money;
- connect to a real exchange;
- use API keys or live credentials;
- use machine learning;
- optimize parameters automatically;
- test many instruments simultaneously;
- introduce complex portfolio construction;
- model every aspect of real execution;
- perform a final out-of-sample robustness study.

Those concerns belong to later research phases.

## Relationship with previous phases

### Phase 0 — Foundation

Phase 0 established the research scope and the requirement for reproducible, risk-aware experiments.

### Phase 1 — Trading and market basics

Phase 1 established the basic concepts and assumptions needed to reason about orders, positions, returns, and risk.

### Phase 2 — NautilusTrader infrastructure

Phase 2 validated the technical pipeline:

```text
catalog → market data → strategy → order → risk → execution → position/result
```

The Phase 2 smoke-test strategy is infrastructure validation only. It must not be treated as the Phase 3 trading baseline.

### Phase 3 — Baseline strategy

Phase 3 introduces the first explicit trading hypothesis and turns the validated infrastructure into a reproducible strategy experiment.

## Development workflow

The phase follows the project's research loop:

1. Define the hypothesis and rules.
2. Document assumptions.
3. Write tests for expected behavior.
4. Implement the smallest useful strategy.
5. Run the backtest.
6. Record metrics and assumptions.
7. Review limitations and failure modes.
8. Commit the work.
9. Only then move to the next phase.

## Exit criteria

Phase 3 is complete when:

- the baseline hypothesis is documented;
- strategy parameters are explicit and validated;
- signal generation is covered by tests;
- entry and exit behavior are covered by tests;
- the end-to-end backtest executes successfully;
- the test verifies actual order and position outcomes;
- baseline metrics are recorded;
- the result is clearly separated from any claim of future profitability;
- the implementation and assumptions are reproducible from the repository.

## Current status

**Status: Design documented — implementation not started.**

The next step is to implement the tests from the behavior defined in this document before implementing the strategy itself.
