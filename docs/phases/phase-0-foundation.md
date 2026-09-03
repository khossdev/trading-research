# Phase 0 — Foundation

## Objective

Establish the scope, principles, and safety boundaries of the project before writing trading code.

## Research question

Can a systematic trading strategy demonstrate a statistically meaningful edge after realistic transaction costs and under controlled risk?

This is an open research question. The project does not assume that the answer is yes.

## What we are not doing

- We are not building a guaranteed-profit bot.
- We are not targeting a fixed daily income as a design requirement.
- We are not starting with leverage or derivatives.
- We are not deploying real capital during the initial research phases.
- We are not using machine learning before establishing a simple baseline.

## Evaluation philosophy

A strategy will not be considered promising based on raw profit alone. Evaluation should include, where applicable:

- total return;
- volatility;
- maximum drawdown;
- win rate;
- average win and average loss;
- profit factor;
- number of trades;
- exposure and turnover;
- fees, spread, and slippage;
- performance across different market regimes;
- out-of-sample performance;
- robustness to reasonable parameter changes.

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

Phase 0 is complete when the repository has a clear research scope, safety boundaries, roadmap, and reproducible development principles. The next phase is learning the trading and market concepts required to make informed implementation decisions.
