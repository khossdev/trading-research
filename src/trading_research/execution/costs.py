from collections.abc import Sequence
from dataclasses import dataclass

from trading_research.evaluation.metrics import Trade


@dataclass(frozen=True)
class ExecutionCostConfig:
    fee_rate: float = 0.0
    spread: float = 0.0
    slippage: float = 0.0

    def __post_init__(self) -> None:
        if self.fee_rate < 0:
            raise ValueError("fee_rate must be non-negative")
        if self.spread < 0:
            raise ValueError("spread must be non-negative")
        if self.slippage < 0:
            raise ValueError("slippage must be non-negative")


@dataclass(frozen=True)
class NetEvaluationReport:
    trade_count: int
    gross_pnl: float
    net_pnl: float
    fees: float
    spread_cost: float
    slippage_cost: float
    win_count: int
    loss_count: int
    win_rate: float
    average_win: float
    average_loss: float
    expectancy: float


def calculate_fee(
    price: float,
    quantity: float,
    fee_rate: float,
) -> float:
    return price * quantity * fee_rate


def _effective_prices(
    trade: Trade,
    config: ExecutionCostConfig,
) -> tuple[float, float]:
    entry_price = trade.entry_price + config.spread / 2 + config.slippage
    exit_price = trade.exit_price - config.spread / 2 - config.slippage
    return entry_price, exit_price


def trade_fees(
    trade: Trade,
    config: ExecutionCostConfig,
) -> float:
    entry_price, exit_price = _effective_prices(trade, config)
    return (
        calculate_fee(entry_price, trade.quantity, config.fee_rate)
        + calculate_fee(exit_price, trade.quantity, config.fee_rate)
    )


def trade_spread_cost(
    trade: Trade,
    config: ExecutionCostConfig,
) -> float:
    return config.spread * trade.quantity


def trade_slippage_cost(
    trade: Trade,
    config: ExecutionCostConfig,
) -> float:
    return 2 * config.slippage * trade.quantity


def net_pnl(
    trade: Trade,
    config: ExecutionCostConfig,
) -> float:
    entry_price, exit_price = _effective_prices(trade, config)
    gross = (exit_price - entry_price) * trade.quantity
    return gross - trade_fees(trade, config)


def evaluate_net(
    trades: Sequence[Trade],
    config: ExecutionCostConfig,
) -> NetEvaluationReport:
    count = len(trades)
    gross_pnl = sum(trade.pnl for trade in trades)
    net_pnls = [net_pnl(trade, config) for trade in trades]
    net_pnl_total = sum(net_pnls)
    fees = sum(trade_fees(trade, config) for trade in trades)
    spread_cost = sum(trade_spread_cost(trade, config) for trade in trades)
    slippage_cost = sum(trade_slippage_cost(trade, config) for trade in trades)

    wins = [pnl for pnl in net_pnls if pnl > 0]
    losses = [pnl for pnl in net_pnls if pnl < 0]
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = win_count / count if count else 0.0
    average_win = sum(wins) / win_count if win_count else 0.0
    average_loss = sum(losses) / loss_count if loss_count else 0.0
    expectancy = win_rate * average_win + (1 - win_rate) * average_loss

    return NetEvaluationReport(
        trade_count=count,
        gross_pnl=gross_pnl,
        net_pnl=net_pnl_total,
        fees=fees,
        spread_cost=spread_cost,
        slippage_cost=slippage_cost,
        win_count=win_count,
        loss_count=loss_count,
        win_rate=win_rate,
        average_win=average_win,
        average_loss=average_loss,
        expectancy=expectancy,
    )
