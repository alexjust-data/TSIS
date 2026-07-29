"""Contracts for deterministic historical replay."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from tsis_backtest.preflight.contracts import MarketDataBar1m, to_jsonable


class ReplayContractError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ReplayBarEvent:
    event_type: str
    ticker: str
    available_at: datetime
    bar: MarketDataBar1m

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class ReplayGapEvent:
    event_type: str
    ticker: str
    ts_start: datetime
    ts_end: datetime
    available_at: datetime
    session_label: str
    price_view: str
    reason: str
    source_file: Path | None = None

    def is_observable_at(self, decision_timestamp: datetime) -> bool:
        return decision_timestamp >= self.available_at

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


ReplayEvent = ReplayBarEvent | ReplayGapEvent


@dataclass(frozen=True)
class ReplayRunSummary:
    preflight_run_id: str
    event_count: int
    bar_count: int
    gap_count: int
    symbols: tuple[str, ...]
    first_available_at: datetime | None
    last_available_at: datetime | None
    warning_codes: tuple[str, ...] = ()
    replay_preflight_report_sha256: str | None = None
    replay_event_sequence_sha256: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)
