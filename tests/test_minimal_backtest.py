from pathlib import Path

from nautilus_trader.backtest.config import (
    BacktestDataConfig,
    BacktestEngineConfig,
    BacktestRunConfig,
    BacktestVenueConfig,
)
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.config import ImportableStrategyConfig


def test_minimal_backtest(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog"

    catalog = ParquetDataCatalog.from_uri(str(catalog_path))

    # TODO: réutiliser ici les bars créés dans test_catalog.py
    # pour alimenter le catalog

    strategy = ImportableStrategyConfig(
        strategy_path="tests.minimal_strategy.MinimalStrategy",
        config_path="tests.minimal_strategy.MinimalStrategyConfig",
        config={},
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
                data_cls="Bar",
            )
        ],
        engine=engine,
    )

    node = BacktestNode([run_config])

    node.run()