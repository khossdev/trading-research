# Phase 2 — NautilusTrader Architecture

## Objective

Understand the core architecture of NautilusTrader before implementing a trading strategy.

The goal is to understand how market data, strategies, risk management, orders, and execution interact.

---

## Research question

How does NautilusTrader move from market data to strategy decisions and execution?

---

## Event-driven architecture

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

---

## Market data

Market data is the information consumed by a strategy.

Examples include:

- quotes
- trades
- order book data
- bars
- instrument information

The `DataEngine` processes and distributes market data to the appropriate components.

A strategy must only make decisions using information that was available at that point in time.

---

## Strategy

A strategy contains the trading logic.

Conceptually:

```text
Market Data
     ↓
Strategy
     ↓
Decision
```

A strategy can decide to submit an order, but the decision to submit an order is separate from the final execution of that order.

---

## Risk

Risk management is separated from strategy logic.

Conceptually:

```text
Strategy
     ↓
Order
     ↓
Risk
     ↓
Execution
```

This separation allows risk controls to be applied independently of the trading strategy.

---

## Execution

The `ExecutionEngine` is responsible for handling order execution and communicating with the relevant venue or simulated venue.

Execution depends on the environment being used.

For our research project, execution will initially be simulated.

---

## Backtest

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

A backtest is an experiment on historical data.

A profitable backtest is not proof that a strategy will be profitable in the future.

---

## Environments

NautilusTrader can be used in different environments.

### Backtest

Historical data with simulated execution.

**This is our initial environment.**

### Sandbox

A testing environment provided by a venue when available.

**Not required at this stage.**

### Live

Real market connectivity and real execution.

**Not part of our current research.**

---

## Research principles

Our research environment follows these principles:

1. No future information must leak into a strategy.
2. Development and evaluation data must be separated.
3. Transaction costs and execution assumptions must be considered.
4. Backtest results must not be treated as proof of future profitability.
5. Strategies must be evaluated on data that was not used to develop them.
6. Risk management must be considered during research.

---

## What we are not doing

At this stage we are not:

- connecting to a real exchange
- placing real orders
- using API keys
- deploying a trading bot
- optimizing a live strategy
- claiming profitability
- risking real capital

---

## Current state

The project currently has:

- Python 3.14
- `uv` dependency management
- NautilusTrader 1.231.0
- pytest
- a basic NautilusTrader environment test

No trading strategy has been implemented yet.

---

## Exit criteria

This phase is complete when we can explain:

- how market data enters the system
- the role of the `DataEngine`
- the role of a strategy
- why risk is separated from strategy logic
- the role of the `ExecutionEngine`
- the difference between backtest, sandbox, and live environments
- why a backtest does not guarantee future profitability

The next step is to build a minimal local backtest environment.
