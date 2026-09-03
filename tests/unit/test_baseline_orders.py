from unittest.mock import MagicMock

from nautilus_trader.model.enums import OrderSide

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


def test_bullish_crossover_submits_buy_order() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 99
    strategy._previous_long_sma = 100
    strategy._short_sma = 101
    strategy._long_sma = 100
    strategy._position = 0

    signal = strategy._generate_signal()
    strategy._apply_signal(signal)

    strategy._submit_market_order.assert_called_once_with(OrderSide.BUY)
    assert strategy._position == 1


def test_bearish_crossover_submits_sell_order() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100
    strategy._short_sma = 99
    strategy._long_sma = 100
    strategy._position = 1

    signal = strategy._generate_signal()
    strategy._apply_signal(signal)

    strategy._submit_market_order.assert_called_once_with(OrderSide.SELL)
    assert strategy._position == 0


def test_no_crossover_submits_no_order() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100
    strategy._short_sma = 102
    strategy._long_sma = 100
    strategy._position = 0

    signal = strategy._generate_signal()
    strategy._apply_signal(signal)

    strategy._submit_market_order.assert_not_called()
    assert strategy._position == 0


def test_no_double_buy_when_already_long() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 99
    strategy._previous_long_sma = 100
    strategy._short_sma = 101
    strategy._long_sma = 100
    strategy._position = 1

    signal = strategy._generate_signal()
    strategy._apply_signal(signal)

    strategy._submit_market_order.assert_not_called()
    assert strategy._position == 1


def test_no_sell_when_flat() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100
    strategy._short_sma = 99
    strategy._long_sma = 100
    strategy._position = 0

    signal = strategy._generate_signal()
    strategy._apply_signal(signal)

    strategy._submit_market_order.assert_not_called()
    assert strategy._position == 0
