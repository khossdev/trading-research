from pathlib import Path

from nautilus_trader.backtest.config import (
    BacktestDataConfig,
    BacktestEngineConfig,
    BacktestRunConfig,
    BacktestVenueConfig,
)
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import InstrumentId, Symbol
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.objects import Currency, Price, Quantity
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.config import ImportableStrategyConfig


def _create_test_instrument() -> Equity:
    instrument_id = InstrumentId.from_str("AAPL.XNAS")

    return Equity(
        instrument_id=instrument_id,
        raw_symbol=Symbol("AAPL"),
        currency=Currency.from_str("USD"),
        price_precision=2,
        price_increment=Price.from_str("0.01"),
        lot_size=Quantity.from_int(1),
        ts_event=0,
        ts_init=0,
    )


def _create_test_bars() -> list[Bar]:
    bar_type = BarType.from_str("AAPL.XNAS-1-MINUTE-LAST-EXTERNAL")

    return [
        Bar(
            bar_type,
            Price(100.00, 2),
            Price(101.00, 2),
            Price(99.00, 2),
            Price(100.50, 2),
            Quantity(10, 0),
            1_000_000_000,
            1_000_000_000,
        ),
        Bar(
            bar_type,
            Price(100.50, 2),
            Price(102.00, 2),
            Price(100.00, 2),
            Price(101.50, 2),
            Quantity(12, 0),
            61_000_000_000,
            61_000_000_000,
        ),
    ]


def test_minimal_backtest(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog"

    catalog = ParquetDataCatalog.from_uri(str(catalog_path))
    catalog.write_data([_create_test_instrument()])
    catalog.write_data(_create_test_bars())

    instrument_id = InstrumentId.from_str("AAPL.XNAS")

    strategy = ImportableStrategyConfig(
        strategy_path="tests.fixtures.minimal_strategy:MinimalStrategy",
        config_path="tests.fixtures.minimal_strategy:MinimalStrategyConfig",
        config={"bar_type": "AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"},
    )

    venue = BacktestVenueConfig(
        name="XNAS",
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        starting_balances=["100000 USD"],
    )

    engine = BacktestEngineConfig(
        strategies=[strategy],
    )

    run_config = BacktestRunConfig(
        venues=[venue],
        data=[
            BacktestDataConfig(
                catalog_path=str(catalog_path),
                data_cls="nautilus_trader.model.data:Bar",
                instrument_id=instrument_id,
                bar_types=["AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"],
            )
        ],
        engine=engine,
        raise_exception=True,
        dispose_on_completion=False,
    )

    node = BacktestNode([run_config])
    try:
        results = node.run()

        assert len(results) == 1
        result = results[0]
        assert result.iterations >= 2
        assert result.total_events >= 2
        assert result.total_orders >= 1
        assert result.total_positions >= 1
        assert int(result.summary["orders.closed"]) >= 1

        engine = node.get_engine(run_config.id)
        orders = engine.cache.orders()
        positions = engine.cache.positions()

        assert len(orders) >= 1
        assert any(order.is_closed for order in orders)
        assert len(positions) >= 1
    finally:
        node.dispose()
