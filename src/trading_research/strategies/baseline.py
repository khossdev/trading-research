from collections import deque
from statistics import fmean

from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.config import StrategyConfig
from nautilus_trader.trading.strategy import Strategy


class BaselineStrategyConfig(StrategyConfig):
    instrument_id: str
    bar_type: str
    short_window: int = 5
    long_window: int = 20
    trade_size: int = 1

    def __post_init__(self) -> None:
        if self.short_window <= 0:
            raise ValueError("short_window must be positive")

        if self.long_window <= self.short_window:
            raise ValueError("long_window must be greater than short_window")

        if self.trade_size <= 0:
            raise ValueError("trade_size must be positive")


class BaselineStrategy(Strategy):
    def __init__(self, config: BaselineStrategyConfig) -> None:
        super().__init__(config)

        self._close_prices: deque[float] = deque(
            maxlen=config.long_window,
        )
        self._short_sma: float | None = None
        self._long_sma: float | None = None
        self._previous_short_sma: float | None = None
        self._previous_long_sma: float | None = None
        self._position = 0

    def _update_sma(self) -> None:
        if len(self._close_prices) >= self.config.short_window:
            self._short_sma = fmean(
                list(self._close_prices)[-self.config.short_window :],
            )

        if len(self._close_prices) >= self.config.long_window:
            self._long_sma = fmean(self._close_prices)

    def _detect_crossover(self) -> str | None:
        if (
            self._previous_short_sma is None
            or self._previous_long_sma is None
            or self._short_sma is None
            or self._long_sma is None
        ):
            return None

        crossed_up = (
            self._previous_short_sma <= self._previous_long_sma
            and self._short_sma > self._long_sma
        )

        crossed_down = (
            self._previous_short_sma >= self._previous_long_sma
            and self._short_sma < self._long_sma
        )

        if crossed_up:
            return "BUY"

        if crossed_down:
            return "SELL"

        return None

    def _generate_signal(self) -> str | None:
        crossover = self._detect_crossover()

        if crossover == "BUY" and self._position == 0:
            return "BUY"

        if crossover == "SELL" and self._position > 0:
            return "SELL"

        return None

    def _submit_market_order(self, side: OrderSide) -> None:
        order = self.order_factory.market(
            instrument_id=InstrumentId.from_str(self.config.instrument_id),
            order_side=side,
            quantity=Quantity.from_int(self.config.trade_size),
        )
        self.submit_order(order)

    def _apply_signal(self, signal: str | None) -> None:
        if signal == "BUY":
            self._submit_market_order(OrderSide.BUY)
            self._position = self.config.trade_size
        elif signal == "SELL":
            self._submit_market_order(OrderSide.SELL)
            self._position = 0

    def on_start(self) -> None:
        self.subscribe_bars(BarType.from_str(self.config.bar_type))

    def on_bar(self, bar) -> None:
        self._previous_short_sma = self._short_sma
        self._previous_long_sma = self._long_sma

        self._close_prices.append(float(bar.close))
        self._update_sma()

        signal = self._generate_signal()
        self._apply_signal(signal)

    def on_stop(self) -> None:
        pass
