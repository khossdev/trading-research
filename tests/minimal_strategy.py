from nautilus_trader.trading.config import StrategyConfig
from nautilus_trader.trading.strategy import Strategy

from nautilus_trader.core.nautilus_pyo3 import UUID4

from nautilus_trader.model.enums import (
    OrderSide,
    TimeInForce,
    ContingencyType,
)

from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.model.identifiers import ClientOrderId
from nautilus_trader.model.objects import Quantity


class MinimalStrategyConfig(StrategyConfig):
    pass


class MinimalStrategy(Strategy):
    def __init__(self, config: MinimalStrategyConfig) -> None:
        super().__init__(config)
        self._submitted = False

    def on_start(self) -> None:
        self.log.info("MinimalStrategy started")

    def on_bar(self, bar) -> None:
        self.log.info(f"Received bar: {bar}")

        if self._submitted:
            return

        self._submitted = True

        order = MarketOrder(
            trader_id=self.trader_id,
            strategy_id=self.strategy_id,
            instrument_id=bar.bar_type.instrument_id,
            client_order_id=ClientOrderId("BUY-001"),
            order_side=OrderSide.BUY,
            quantity=Quantity.from_int(1),
            init_id=UUID4(),
            ts_init=self.clock.timestamp_ns(),
            time_in_force=TimeInForce.GTC,
            contingency_type=ContingencyType.NO_CONTINGENCY,
        )

        self.submit_order(order)

    def on_order_filled(self, event) -> None:
        self.log.info(f"ORDER FILLED: {event}")

    def on_stop(self) -> None:
        self.log.info("MinimalStrategy stopped")