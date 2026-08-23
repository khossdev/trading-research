from nautilus_trader.trading.config import StrategyConfig
from nautilus_trader.trading.strategy import Strategy


class MinimalStrategyConfig(StrategyConfig):
    pass


class MinimalStrategy(Strategy):
    def __init__(self, config: MinimalStrategyConfig) -> None:
        super().__init__(config)

    def on_start(self) -> None:
        self.log.info("MinimalStrategy started")

    def on_bar(self, bar) -> None:
        self.log.info(f"Received bar: {bar}")

    def on_stop(self) -> None:
        self.log.info("MinimalStrategy stopped")