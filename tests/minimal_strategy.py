"""Infrastructure smoke-test strategy for Phase 2 pipeline validation.

This module is not a baseline trading strategy and must not be reused as one.
"""

from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.config import StrategyConfig
from nautilus_trader.trading.strategy import Strategy


class MinimalStrategyConfig(StrategyConfig):
    bar_type: str


class MinimalStrategy(Strategy):
    def __init__(self, config: MinimalStrategyConfig) -> None:
        super().__init__(config)
        self._submitted = False

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self.config.bar_type))
        self.log.info("MinimalStrategy started")

    def on_bar(self, bar) -> None:
        self.log.info(f"Received bar: {bar}")

        if self._submitted:
            return

        self._submitted = True

        order = self.order_factory.market(
            instrument_id=bar.bar_type.instrument_id,
            order_side=OrderSide.BUY,
            quantity=Quantity.from_int(1),
        )

        self.submit_order(order)

    def on_order_filled(self, event) -> None:
        self.log.info(f"ORDER FILLED: {event}")

    def on_stop(self) -> None:
        self.log.info("MinimalStrategy stopped")
