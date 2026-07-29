"""Replay/event-loop primitives for TSIS backtest vertical slice."""

from .contracts import ReplayBarEvent, ReplayContractError, ReplayGapEvent, ReplayRunSummary

__all__ = [
    "HistoricalReplayFeed",
    "ReplayBarEvent",
    "ReplayContractError",
    "ReplayGapEvent",
    "ReplayRunSummary",
]


def __getattr__(name: str):
    if name == "HistoricalReplayFeed":
        from .historical_feed import HistoricalReplayFeed

        return HistoricalReplayFeed
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
