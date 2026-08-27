from pathlib import Path

from nautilus_trader.backtest.config import (
    BacktestDataConfig,
    BacktestEngineConfig,
    BacktestRunConfig,
    BacktestVenueConfig,
)
from nautilus_trader.backtest.node import BacktestNode
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType, OrderSide
from nautilus_trader.model.identifiers import InstrumentId, Symbol
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.objects import Currency, Price, Quantity
from nautilus_trader.persistence.catalog import ParquetDataCatalog
from nautilus_trader.trading.config import ImportableStrategyConfig

from tests.backtest_metrics import (
    average_loss,
    average_win,
    expectancy,
    loss_count,
    position_to_trade,
    total_pnl,
    trade_count,
    win_count,
    win_rate,
)

BAR_TYPE = "AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"
MINUTE_NS = 60_000_000_000


def _create_test_instrument() -> Equity:
    return Equity(
        instrument_id=InstrumentId.from_str("AAPL.XNAS"),
        raw_symbol=Symbol("AAPL"),
        currency=Currency.from_str("USD"),
        price_precision=2,
        price_increment=Price.from_str("0.01"),
        lot_size=Quantity.from_int(1),
        ts_event=0,
        ts_init=0,
    )


def _create_crossover_bars() -> list[Bar]:
    """Synthetic closes that force BUY then SELL with short=2, long=3.

    Closes: 100, 100, 100, 110, 110, 90
    - after bar 4: bullish crossover → BUY
    - after bar 6: bearish crossover → SELL
    """
    bar_type = BarType.from_str(BAR_TYPE)
    closes = [100.00, 100.00, 100.00, 110.00, 110.00, 90.00]
    bars: list[Bar] = []

    for i, close in enumerate(closes):
        ts = (i + 1) * MINUTE_NS
        price = Price(close, 2)
        bars.append(
            Bar(
                bar_type,
                price,
                price,
                price,
                price,
                Quantity(10, 0),
                ts,
                ts,
            )
        )

    return bars


def test_baseline_backtest_buy_then_sell(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog"

    catalog = ParquetDataCatalog.from_uri(str(catalog_path))
    catalog.write_data([_create_test_instrument()])
    catalog.write_data(_create_crossover_bars())

    instrument_id = InstrumentId.from_str("AAPL.XNAS")

    strategy = ImportableStrategyConfig(
        strategy_path="tests.baseline_strategy:BaselineStrategy",
        config_path="tests.baseline_strategy:BaselineStrategyConfig",
        config={
            "instrument_id": "AAPL.XNAS",
            "bar_type": BAR_TYPE,
            "short_window": 2,
            "long_window": 3,
            "trade_size": 1,
        },
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
                bar_types=[BAR_TYPE],
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
        assert result.iterations >= 6
        assert result.total_orders >= 2
        assert int(result.summary["orders.closed"]) >= 2

        engine = node.get_engine(run_config.id)
        orders = engine.cache.orders()
        positions = engine.cache.positions()

        buy_orders = [o for o in orders if o.side == OrderSide.BUY]
        sell_orders = [o for o in orders if o.side == OrderSide.SELL]

        assert len(buy_orders) >= 1
        assert all(order.is_closed for order in buy_orders)
        assert len(sell_orders) >= 1
        assert all(order.is_closed for order in sell_orders)

        assert len(positions) >= 1
        assert all(position.is_closed for position in positions)
        assert engine.cache.positions_open() == []

        closed_positions = [position for position in positions if position.is_closed]
        trades = [position_to_trade(position) for position in closed_positions]

        assert trade_count(trades) == 1
        assert total_pnl(trades) == -20
        assert win_count(trades) == 0
        assert loss_count(trades) == 1
        assert win_rate(trades) == 0.0
        assert average_win(trades) == 0.0
        assert average_loss(trades) == -20.0
        assert expectancy(trades) == -20.0
    finally:
        node.dispose()
