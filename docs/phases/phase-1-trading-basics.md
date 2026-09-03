# Phase 1 — Trading & Market Basics

## Objective

Establish the minimum trading and market knowledge required to make informed research and implementation decisions without assuming that a strategy will be profitable.

## Research question

What concepts and constraints are necessary to evaluate a systematic trading idea responsibly before implementing or evaluating a strategy?

This phase does not attempt to answer whether a profitable strategy exists. It establishes the vocabulary, mechanics, risk concepts, and research discipline needed for later phases.

## What we learned

### Market structure

- order book;
- bid and ask;
- spread;
- market and limit orders;
- liquidity and execution basics.

### Price and positions

- candlesticks and basic price representation;
- long and short positions;
- position sizing and maximum exposure;
- profit and loss (P&L).

### Trading costs and risk

- fees;
- spread and slippage;
- win rate;
- average win and average loss;
- expectancy;
- loss limits;
- maximum drawdown.

### Research and backtesting

- chronological historical simulation;
- train, validation, and test separation;
- out-of-sample evaluation;
- overfitting;
- data leakage;
- multiple testing;
- robustness and reproducibility.

## Research principles established

A historical simulation must respect the information available at the time of each decision. Future information must not influence past decisions.

The final test set must remain independent from the decisions used to develop the strategy. Repeatedly modifying a strategy based on test results turns the test into another optimization target.

A strong historical result is not sufficient evidence of future profitability. Performance must be considered together with risk, costs, execution assumptions, sample size, and out-of-sample behavior.

Simple and explainable hypotheses should be preferred before adding unnecessary complexity.

## What we are not doing

- We are not building a guaranteed-profit bot.
- We are not targeting a fixed daily income as a design requirement.
- We are not deploying real capital during the initial research phases.
- We are not assuming that a strong backtest predicts future returns.
- We are not using machine learning before establishing a simple baseline.
- We are not defining a trading strategy in this phase.

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

Phase 1 is complete when the project has established the trading and market vocabulary, basic risk concepts, backtesting principles, and research rules required for the next implementation phase.

The next phase will establish the NautilusTrader research environment and its technical foundations before any strategy is evaluated.
