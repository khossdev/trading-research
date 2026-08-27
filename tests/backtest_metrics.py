from dataclasses import dataclass
from collections.abc import Sequence
from typing import Any


@dataclass(frozen=True)
class Trade:
    entry_price: float
    exit_price: float
    quantity: float

    @property
    def pnl(self) -> float:
        return (self.exit_price - self.entry_price) * self.quantity


def position_to_trade(position: Any) -> Trade:
    return Trade(
        entry_price=float(position.avg_px_open),
        exit_price=float(position.avg_px_close),
        quantity=float(position.peak_qty),
    )


def trade_count(trades: Sequence[Trade]) -> int:
    return len(trades)


def total_pnl(trades: Sequence[Trade]) -> float:
    return sum(trade.pnl for trade in trades)


def win_count(trades: Sequence[Trade]) -> int:
    return sum(1 for trade in trades if trade.pnl > 0)


def loss_count(trades: Sequence[Trade]) -> int:
    return sum(1 for trade in trades if trade.pnl < 0)


def win_rate(trades: Sequence[Trade]) -> float:
    count = trade_count(trades)
    if count == 0:
        return 0.0
    return win_count(trades) / count


def average_win(trades: Sequence[Trade]) -> float:
    count = win_count(trades)
    if count == 0:
        return 0.0
    return sum(trade.pnl for trade in trades if trade.pnl > 0) / count


def average_loss(trades: Sequence[Trade]) -> float:
    count = loss_count(trades)
    if count == 0:
        return 0.0
    return sum(trade.pnl for trade in trades if trade.pnl < 0) / count


def expectancy(trades: Sequence[Trade]) -> float:
    rate = win_rate(trades)
    return rate * average_win(trades) + (1 - rate) * average_loss(trades)
