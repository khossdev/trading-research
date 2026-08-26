import pytest

from tests.baseline_strategy import BaselineStrategyConfig


def test_baseline_strategy_config_defaults() -> None:
    config = BaselineStrategyConfig(
        instrument_id="AAPL.XNAS",
        bar_type="AAPL.XNAS-1-MINUTE-LAST-EXTERNAL",
    )

    assert config.instrument_id == "AAPL.XNAS"
    assert config.bar_type == "AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"
    assert config.short_window == 5
    assert config.long_window == 20
    assert config.trade_size == 1


@pytest.mark.parametrize(
    "kwargs",
    [
        {"short_window": 0},
        {"short_window": -1},
        {"long_window": 5},
        {"long_window": 4},
        {"trade_size": 0},
        {"trade_size": -1},
    ],
)
def test_baseline_strategy_config_rejects_invalid_parameters(
    kwargs: dict,
) -> None:
    with pytest.raises(ValueError):
        BaselineStrategyConfig(
            instrument_id="AAPL.XNAS",
            bar_type="AAPL.XNAS-1-MINUTE-LAST-EXTERNAL",
            **kwargs,
        )
