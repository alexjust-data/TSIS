"""End-to-end backtest orchestration for TSIS."""

from .contracts import (
    BacktestRunError,
    BacktestRunRequest,
    EndToEndBacktestResult,
    StrategySpec,
)
from .runner import SingleStrategyEndToEndBacktestRunner
from .strategy import OpenShortCloseCoverStrategy, default_open_short_close_strategy

__all__ = [
    "BacktestRunError",
    "BacktestRunRequest",
    "EndToEndBacktestResult",
    "OpenShortCloseCoverStrategy",
    "SingleStrategyEndToEndBacktestRunner",
    "StrategySpec",
    "default_open_short_close_strategy",
]
