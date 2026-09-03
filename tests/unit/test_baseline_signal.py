from unittest.mock import MagicMock

from trading_research.strategies.baseline import BaselineStrategy, BaselineStrategyConfig


def make_strategy() -> BaselineStrategy:
    strategy = BaselineStrategy(
        BaselineStrategyConfig(
            instrument_id="AAPL.XNAS",
            bar_type="AAPL.XNAS-1-MINUTE-LAST-EXTERNAL",
            short_window=3,
            long_window=5,
            trade_size=1,
        ),
    )
    strategy._submit_market_order = MagicMock()
    return strategy


def test_buy_signal_when_flat_and_bullish_crossover() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 99
    strategy._previous_long_sma = 100
    strategy._short_sma = 101
    strategy._long_sma = 100
    strategy._position = 0

    assert strategy._generate_signal() == "BUY"


def test_sell_signal_when_long_and_bearish_crossover() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100
    strategy._short_sma = 99
    strategy._long_sma = 100
    strategy._position = 1

    assert strategy._generate_signal() == "SELL"


def test_no_buy_signal_when_already_long() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 99
    strategy._previous_long_sma = 100
    strategy._short_sma = 101
    strategy._long_sma = 100
    strategy._position = 1

    assert strategy._generate_signal() is None


def test_no_sell_signal_when_flat() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100
    strategy._short_sma = 99
    strategy._long_sma = 100
    strategy._position = 0

    assert strategy._generate_signal() is None


def test_buy_signal_updates_position() -> None:
    strategy = make_strategy()

    strategy._apply_signal("BUY")

    assert strategy._position == 1
    strategy._submit_market_order.assert_called_once()


def test_sell_signal_closes_position() -> None:
    strategy = make_strategy()

    strategy._position = 1
    strategy._apply_signal("SELL")

    assert strategy._position == 0
    strategy._submit_market_order.assert_called_once()
