# Phase 2 — NautilusTrader Architecture

## Objective

Understand the core architecture of NautilusTrader before implementing a trading strategy.

The goal is to understand how market data, strategies, risk management, orders, and execution interact.

## Research question

How does NautilusTrader move from market data to strategy decisions and execution?

This phase does not attempt to answer whether a profitable strategy exists. It establishes the technical foundations required to implement and test one responsibly.

## What we learned

### Event-driven architecture

NautilusTrader is built around an event-driven architecture.

Its components communicate through events and messages rather than relying only on continuous polling.

The main components include:

- `NautilusKernel`
- `MessageBus`
- `Cache`
- `DataEngine`
- `RiskEngine`
- `ExecutionEngine`
- `Portfolio`
- Strategies

A simplified conceptual flow is:

```text
Market Data
     ↓
DataEngine
     ↓
Strategy
     ↓
RiskEngine
     ↓
ExecutionEngine
     ↓
Venue
```

This diagram is intentionally simplified. It does not represent every internal component or communication path.

### Market data and the DataEngine

Market data is the information consumed by a strategy.

Examples include:

- quotes;
- trades;
- order book data;
- bars;
- instrument information.

The `DataEngine` processes and distributes market data to the appropriate components.

A strategy must only make decisions using information that was available at that point in time.

### Strategy, risk, and execution

A strategy contains the trading logic and can decide to submit an order, but the decision to submit an order is separate from the final execution of that order.

Conceptually:

```text
Market Data
     ↓
Strategy
     ↓
Decision
     ↓
Risk
     ↓
Execution
```

Risk management is separated from strategy logic so that risk controls can be applied independently of the trading strategy.

The `ExecutionEngine` handles order execution and communicates with the relevant venue or simulated venue. For our research project, execution is initially simulated.

### Backtest and environments

A backtest evaluates a strategy using historical market data and simulated execution.

Conceptually:

```text
Historical Data
      ↓
Backtest
      ↓
Strategy
      ↓
Simulated Execution
      ↓
Results
```

A backtest is an experiment on historical data. A profitable backtest is not proof that a strategy will be profitable in the future.

NautilusTrader can be used in different environments:

- **Backtest** — historical data with simulated execution. This is our initial environment.
- **Sandbox** — a testing environment provided by a venue when available. Not required at this stage.
- **Live** — real market connectivity and real execution. Not part of our current research.

### Local research environment

The project currently has:

- Python 3.14;
- `uv` dependency management;
- NautilusTrader 1.231.0;
- pytest;
- a basic NautilusTrader environment test (`tests/integration/test_nautilus_environment.py`);
- a Parquet data catalog for bar storage (`tests/integration/test_catalog.py`);
- a minimal backtest pipeline with assertions (`tests/integration/test_minimal_backtest.py`);
- a smoke-test strategy that validates the pipeline end to end (`tests/fixtures/minimal_strategy.py`).

Through the smallest useful experiments, we confirmed that:

- NautilusTrader imports and runs in this project environment;
- bar data can be written to and read from a local Parquet catalog;
- an instrument definition must be stored in the catalog before backtesting bars;
- a strategy must subscribe to market data in `on_start` before it can react to events;
- import paths for strategies and data classes must use the `module:Class` format expected by NautilusTrader;
- a `BacktestNode` run can load catalog data, deliver bars to a strategy, route an order through risk and execution, and produce portfolio results.

Validation command:

```bash
uv run pytest -v
```

Result on 2026-08-25:

| Test | Purpose | Status |
|------|---------|--------|
| `test_nautilus_trader_is_available` | Verify NautilusTrader is installed | passed |
| `test_write_and_read_bars` | Verify Parquet catalog read/write | passed |
| `test_minimal_backtest` | Verify end-to-end backtest pipeline | passed |

All 3 tests passed.

The smoke-test strategy submits a single market order on the first bar. It is not a baseline trading strategy. No trading hypothesis has been evaluated yet.

During validation, we also found that the earlier backtest test only called `node.run()` without checking the result. The pipeline was failing silently because of incorrect import paths and missing instrument/subscription setup. The test now asserts that bars are processed, an order is submitted and closed, and a position is opened.

Phase 2 infrastructure and minimal backtest plumbing are validated. No trading hypothesis has been evaluated yet, and Phase 3 has not started.

Current limitations:

- tests use synthetic bars and a smoke-test strategy, not real market data or a research hypothesis;
- transaction costs, spread, slippage, and realistic execution are not yet modeled in detail;
- no out-of-sample evaluation has been performed;
- a profitable or unprofitable smoke-test result must not be interpreted as strategy evidence.

## Research principles established

No future information must leak into a strategy.

Development and evaluation data must be separated.

Transaction costs and execution assumptions must be considered.

Backtest results must not be treated as proof of future profitability.

Strategies must be evaluated on data that was not used to develop them.

Risk management must be considered during research.

## What we are not doing

- We are not connecting to a real exchange.
- We are not placing real orders.
- We are not using API keys.
- We are not deploying a trading bot.
- We are not optimizing a live strategy.
- We are not claiming profitability.
- We are not risking real capital.
- We are not defining a baseline trading strategy in this phase.

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

The smoke-test backtest in this phase validates infrastructure only. It is not evidence of strategy quality.

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

Phase 2 is complete when we can explain:

- how market data enters the system;
- the role of the `DataEngine`;
- the role of a strategy;
- why risk is separated from strategy logic;
- the role of the `ExecutionEngine`;
- the difference between backtest, sandbox, and live environments;
- why a backtest does not guarantee future profitability.

Phase 2 is also complete when the environment tests above pass, execution flow is validated, and the results are recorded.

Infrastructure validation confirms that bars reach a strategy, an order can be submitted, and simulated execution can fill that order. This does not mean trading research has started.

The next phase is to implement and document a first baseline strategy with a clear, testable trading hypothesis.
