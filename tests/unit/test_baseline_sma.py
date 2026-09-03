from trading_research.strategies.baseline import BaselineStrategy, BaselineStrategyConfig


def test_baseline_sma_values() -> None:
    config = BaselineStrategyConfig(
        instrument_id="AAPL.XNAS",
        bar_type="AAPL.XNAS-1-MINUTE-LAST-EXTERNAL",
        short_window=3,
        long_window=5,
    )

    strategy = BaselineStrategy(config)

    for price in [100, 101, 102]:
        strategy._close_prices.append(price)
        strategy._update_sma()

    assert strategy._short_sma == 101
    assert strategy._long_sma is None

    strategy._close_prices.append(103)
    strategy._update_sma()

    assert strategy._short_sma == 102
    assert strategy._long_sma is None

    strategy._close_prices.append(104)
    strategy._update_sma()

    assert strategy._short_sma == 103
    assert strategy._long_sma == 102
