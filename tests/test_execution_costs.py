import pytest

from tests.backtest_metrics import Trade
from tests.execution_costs import (
    EvaluationReport,
    ExecutionCostConfig,
    calculate_fee,
    evaluate_trades,
    net_pnl,
)


def test_calculate_fee() -> None:
    assert calculate_fee(price=100, quantity=10, fee_rate=0.001) == 1.0


def test_net_pnl_without_costs() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(fee_rate=0.0)

    assert net_pnl(trade, config) == 100.0


def test_net_pnl_with_fees_on_winning_trade() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(fee_rate=0.001)

    assert net_pnl(trade, config) == 97.9


def test_net_pnl_with_fees_on_losing_trade() -> None:
    trade = Trade(entry_price=110, exit_price=105, quantity=10)
    config = ExecutionCostConfig(fee_rate=0.001)

    assert net_pnl(trade, config) == -52.15


def test_net_pnl_without_spread() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=0.0,
    )

    assert net_pnl(trade, config) == 100.0


def test_net_pnl_with_spread_on_winning_trade() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=2.0,
    )

    assert net_pnl(trade, config) == 80.0


def test_net_pnl_with_spread_without_price_movement() -> None:
    trade = Trade(entry_price=100, exit_price=100, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=2.0,
    )

    assert net_pnl(trade, config) == -20.0


def test_net_pnl_without_slippage() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=0.0,
        slippage=0.0,
    )

    assert net_pnl(trade, config) == 100.0


def test_net_pnl_with_slippage_on_winning_trade() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=0.0,
        slippage=1.0,
    )

    assert net_pnl(trade, config) == 80.0


def test_net_pnl_with_slippage_without_price_movement() -> None:
    trade = Trade(entry_price=100, exit_price=100, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=0.0,
        slippage=1.0,
    )

    assert net_pnl(trade, config) == -20.0


def test_net_pnl_with_fees_spread_and_slippage() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)
    config = ExecutionCostConfig(
        fee_rate=0.001,
        spread=2.0,
        slippage=1.0,
    )

    assert net_pnl(trade, config) == pytest.approx(57.9)


def test_evaluate_trades_without_costs() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]
    config = ExecutionCostConfig(
        fee_rate=0.0,
        spread=0.0,
        slippage=0.0,
    )

    report = evaluate_trades(trades, config)

    assert report == EvaluationReport(
        trade_count=1,
        gross_pnl=100.0,
        net_pnl=100.0,
        fees=0.0,
        spread_cost=0.0,
        slippage_cost=0.0,
        win_count=1,
        loss_count=0,
        win_rate=1.0,
        average_win=100.0,
        average_loss=0.0,
        expectancy=100.0,
    )


def test_evaluate_trades_with_fees_spread_and_slippage() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]
    config = ExecutionCostConfig(
        fee_rate=0.001,
        spread=2.0,
        slippage=1.0,
    )

    report = evaluate_trades(trades, config)

    assert report.trade_count == 1
    assert report.gross_pnl == pytest.approx(100.0)
    assert report.net_pnl == pytest.approx(57.9)
    assert report.fees == pytest.approx(2.1)
    assert report.spread_cost == pytest.approx(20.0)
    assert report.slippage_cost == pytest.approx(20.0)
    assert report.net_pnl == pytest.approx(
        report.gross_pnl - report.fees - report.spread_cost - report.slippage_cost
    )
    assert report.win_count == 1
    assert report.loss_count == 0
    assert report.win_rate == 1.0
    assert report.average_win == pytest.approx(57.9)
    assert report.average_loss == 0.0
    assert report.expectancy == pytest.approx(57.9)
