import pytest
from unittest.mock import MagicMock

from tests.backtest_metrics import (
    Trade,
    EvaluationReport,
    average_loss,
    average_win,
    evaluate_trades,
    expectancy,
    loss_count,
    max_drawdown,
    position_to_trade,
    total_pnl,
    trade_count,
    win_count,
    win_rate,
)


def test_trade_winning_pnl() -> None:
    trade = Trade(entry_price=100, exit_price=110, quantity=10)

    assert trade.pnl == 100


def test_trade_losing_pnl() -> None:
    trade = Trade(entry_price=110, exit_price=105, quantity=10)

    assert trade.pnl == -50


def test_trade_flat_pnl() -> None:
    trade = Trade(entry_price=100, exit_price=100, quantity=10)

    assert trade.pnl == 0


def test_trade_count_and_total_pnl_empty() -> None:
    trades: list[Trade] = []

    assert trade_count(trades) == 0
    assert total_pnl(trades) == 0


def test_trade_count_and_total_pnl_single_winner() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]

    assert trade_count(trades) == 1
    assert total_pnl(trades) == 100


def test_trade_count_and_total_pnl_mixed() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=110, exit_price=105, quantity=10),  # -50
        Trade(entry_price=100, exit_price=100, quantity=10),  # 0
    ]

    assert trade_count(trades) == 3
    assert total_pnl(trades) == 50


def test_win_loss_rate_empty() -> None:
    trades: list[Trade] = []

    assert win_count(trades) == 0
    assert loss_count(trades) == 0
    assert win_rate(trades) == 0.0


def test_win_loss_rate_single_winner() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]

    assert win_count(trades) == 1
    assert loss_count(trades) == 0
    assert win_rate(trades) == 1.0


def test_win_loss_rate_single_loser() -> None:
    trades = [Trade(entry_price=110, exit_price=105, quantity=10)]

    assert win_count(trades) == 0
    assert loss_count(trades) == 1
    assert win_rate(trades) == 0.0


def test_win_loss_rate_mixed() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=110, exit_price=105, quantity=10),  # -50
        Trade(entry_price=100, exit_price=100, quantity=10),  # 0
    ]

    assert win_count(trades) == 1
    assert loss_count(trades) == 1
    assert win_rate(trades) == 1 / 3


def test_average_win_loss_empty() -> None:
    trades: list[Trade] = []

    assert average_win(trades) == 0.0
    assert average_loss(trades) == 0.0


def test_average_win_loss_single_winner() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]

    assert average_win(trades) == 100.0
    assert average_loss(trades) == 0.0


def test_average_win_loss_single_loser() -> None:
    trades = [Trade(entry_price=110, exit_price=105, quantity=10)]

    assert average_win(trades) == 0.0
    assert average_loss(trades) == -50.0


def test_average_win_loss_mixed() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=110, exit_price=105, quantity=10),  # -50
        Trade(entry_price=100, exit_price=100, quantity=10),  # 0
    ]

    assert average_win(trades) == 100.0
    assert average_loss(trades) == -50.0


def test_expectancy_empty() -> None:
    trades: list[Trade] = []

    assert expectancy(trades) == 0.0


def test_expectancy_single_winner() -> None:
    trades = [Trade(entry_price=100, exit_price=110, quantity=10)]

    assert expectancy(trades) == 100.0


def test_expectancy_single_loser() -> None:
    trades = [Trade(entry_price=110, exit_price=105, quantity=10)]

    assert expectancy(trades) == -50.0


def test_expectancy_mixed_with_flat() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=110, exit_price=105, quantity=10),  # -50
        Trade(entry_price=100, exit_price=100, quantity=10),  # 0
    ]

    assert expectancy(trades) == pytest.approx(0.0)


def test_expectancy_mixed_without_flat() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=100, exit_price=105, quantity=10),  # +50
        Trade(entry_price=100, exit_price=96, quantity=10),  # -40
        Trade(entry_price=100, exit_price=98, quantity=10),  # -20
    ]

    assert expectancy(trades) == 22.5


def test_position_to_trade_winning() -> None:
    position = MagicMock()
    position.avg_px_open = 100
    position.avg_px_close = 110
    position.peak_qty = 2

    trade = position_to_trade(position)

    assert trade.entry_price == 100.0
    assert trade.exit_price == 110.0
    assert trade.quantity == 2.0
    assert trade.pnl == 20.0


def test_position_to_trade_losing() -> None:
    position = MagicMock()
    position.avg_px_open = 110
    position.avg_px_close = 105
    position.peak_qty = 2

    trade = position_to_trade(position)

    assert trade.entry_price == 110.0
    assert trade.exit_price == 105.0
    assert trade.quantity == 2.0
    assert trade.pnl == -10.0


def test_max_drawdown_empty() -> None:
    assert max_drawdown([]) == 0.0


def test_max_drawdown_single_loss() -> None:
    trades = [Trade(entry_price=110, exit_price=90, quantity=1)]

    assert max_drawdown(trades) == 20.0


def test_max_drawdown_mixed() -> None:
    trades = [
        Trade(entry_price=100, exit_price=110, quantity=10),  # +100
        Trade(entry_price=110, exit_price=105, quantity=10),  # -50
    ]

    assert max_drawdown(trades) == 50.0


def test_evaluate_trades_reference_scenario() -> None:
    trades = [Trade(entry_price=110, exit_price=90, quantity=1)]

    report = evaluate_trades(trades)

    assert report == EvaluationReport(
        trade_count=1,
        total_pnl=-20.0,
        win_count=0,
        loss_count=1,
        win_rate=0.0,
        average_win=0.0,
        average_loss=-20.0,
        expectancy=-20.0,
        max_drawdown=20.0,
    )
