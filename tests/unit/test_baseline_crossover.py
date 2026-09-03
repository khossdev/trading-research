from trading_research.strategies.baseline import BaselineStrategy, BaselineStrategyConfig


def make_strategy() -> BaselineStrategy:
    return BaselineStrategy(
        BaselineStrategyConfig(
            instrument_id="AAPL.XNAS",
            bar_type="AAPL.XNAS-1-MINUTE-LAST-EXTERNAL",
            short_window=3,
            long_window=5,
        ),
    )


def test_no_crossover_without_previous_sma() -> None:
    strategy = make_strategy()

    strategy._short_sma = 101
    strategy._long_sma = 100

    assert strategy._detect_crossover() is None


def test_detects_bullish_crossover() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 99
    strategy._previous_long_sma = 100

    strategy._short_sma = 101
    strategy._long_sma = 100

    assert strategy._detect_crossover() == "BUY"


def test_detects_bearish_crossover() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100

    strategy._short_sma = 99
    strategy._long_sma = 100

    assert strategy._detect_crossover() == "SELL"


def test_no_signal_when_trend_does_not_cross() -> None:
    strategy = make_strategy()

    strategy._previous_short_sma = 101
    strategy._previous_long_sma = 100

    strategy._short_sma = 102
    strategy._long_sma = 100

    assert strategy._detect_crossover() is None
