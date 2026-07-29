"""Deterministic historical replay feed for preflight-approved 1m bars."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

import pyarrow.parquet as pq

from tsis_backtest.preflight.contracts import MarketDataBar1m, to_jsonable
from tsis_backtest.preflight.real_data_inspector import sha256_file

from .contracts import ReplayBarEvent, ReplayContractError, ReplayEvent, ReplayGapEvent, ReplayRunSummary


REPLAY_REQUIRED_COLUMNS = ("ticker", "ts_utc", "o", "h", "l", "c", "v")
REPLAY_OPTIONAL_LINEAGE_COLUMNS = (
    "t",
    "date",
    "year",
    "month",
    "dataset_id",
    "build_run_id",
    "quote_guarded_repair_applied",
    "quote_guarded_view",
    "repair_lookup_state",
    "source_quote_guarded_repair_manifest",
    "source_raw_path",
)
NON_CONSUMABLE_VENDOR_DERIVED_COLUMNS = ("vw",)


class HistoricalReplayFeed:
    """Loads only data already approved by RunPreflight and emits legal replay events."""

    def __init__(
        self,
        preflight_report: Mapping[str, Any],
        verify_hashes: bool = True,
        preflight_report_sha256: str | None = None,
    ) -> None:
        if verify_hashes is not True:
            raise ReplayContractError("REPLAY_HASH_VERIFICATION_REQUIRED", "HistoricalReplayFeed requires source hash verification")
        self._report = dict(preflight_report)
        self._verify_hashes = verify_hashes
        self._preflight_report_sha256 = preflight_report_sha256 or _canonical_sha256(self._report)

    @classmethod
    def from_preflight_report(cls, path: Path, verify_hashes: bool = True) -> "HistoricalReplayFeed":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload, verify_hashes=verify_hashes, preflight_report_sha256=sha256_file(path))

    def stream_events(self) -> tuple[ReplayEvent, ...]:
        self._validate_preflight_report()
        if self._verify_hashes:
            self._verify_consumed_file_hashes()
        events = list(self._load_bar_events()) + list(self._load_gap_events())
        events.sort(key=self._event_sort_key)
        return tuple(events)

    def stream_bars(self) -> tuple[MarketDataBar1m, ...]:
        return tuple(event.bar for event in self.stream_events() if isinstance(event, ReplayBarEvent))

    def summarize(self) -> ReplayRunSummary:
        events = self.stream_events()
        bars = tuple(event for event in events if isinstance(event, ReplayBarEvent))
        gaps = tuple(event for event in events if isinstance(event, ReplayGapEvent))
        times = tuple(event.available_at for event in events)
        return ReplayRunSummary(
            preflight_run_id=str(self._report.get("run_id", "UNKNOWN_PREFLIGHT_RUN")),
            event_count=len(events),
            bar_count=len(bars),
            gap_count=len(gaps),
            symbols=tuple(self._report.get("symbols_available", ())),
            first_available_at=min(times) if times else None,
            last_available_at=max(times) if times else None,
            warning_codes=tuple(self._report.get("physical_inspection", {}).get("warning_codes", ())),
            replay_preflight_report_sha256=self._preflight_report_sha256,
            replay_event_sequence_sha256=_event_sequence_sha256(events),
        )

    def _validate_preflight_report(self) -> None:
        if not self._report.get("resolved") or self._report.get("preflight_status") != "PREFLIGHT_PASS":
            raise ReplayContractError("REPLAY_PREFLIGHT_NOT_PASS", "replay requires a resolved PREFLIGHT_PASS report")
        if self._report.get("physical_inspection_status") != "PHYSICAL_INSPECTION_PASS":
            raise ReplayContractError("REPLAY_PHYSICAL_INSPECTION_NOT_PASS", "replay requires PHYSICAL_INSPECTION_PASS")
        if not self._report.get("source_partitions_or_files_consumed"):
            raise ReplayContractError("REPLAY_NO_SOURCE_FILES", "preflight report has no consumed source files")
        if not self._report.get("snapshot_or_content_hashes"):
            raise ReplayContractError("REPLAY_NO_SOURCE_HASHES", "preflight report has no source hashes")

    def _verify_consumed_file_hashes(self) -> None:
        expected_hashes = self._report.get("snapshot_or_content_hashes", {})
        for file_name in self._report.get("source_partitions_or_files_consumed", ()): 
            path = Path(file_name)
            if not path.exists():
                raise ReplayContractError("REPLAY_SOURCE_FILE_NOT_FOUND", f"source file not found: {path}")
            expected = _lookup_hash(expected_hashes, path)
            if expected is None:
                raise ReplayContractError("REPLAY_SOURCE_HASH_MISSING", f"source file hash missing from preflight report: {path}")
            actual = sha256_file(path)
            if actual != expected:
                raise ReplayContractError("REPLAY_SOURCE_HASH_MISMATCH", f"source file hash drift: {path}")

    def _load_bar_events(self) -> Iterable[ReplayBarEvent]:
        session_start, session_end = self._session_bounds_utc()
        price_view = self._price_view()
        for file_name in self._report.get("source_partitions_or_files_consumed", ()): 
            path = Path(file_name)
            parquet_file = pq.ParquetFile(path)
            schema_names = tuple(parquet_file.schema_arrow.names)
            missing = tuple(column for column in REPLAY_REQUIRED_COLUMNS if column not in schema_names)
            if missing:
                raise ReplayContractError("REPLAY_SCHEMA_MISSING_REQUIRED_COLUMNS", ",".join(missing))
            columns = list(REPLAY_REQUIRED_COLUMNS) + [
                column for column in REPLAY_OPTIONAL_LINEAGE_COLUMNS if column in schema_names and column not in REPLAY_REQUIRED_COLUMNS
            ]
            table = parquet_file.read(columns=columns)
            for row in table.to_pylist():
                ts_start = _parse_utc(row.get("ts_utc"))
                if not (session_start <= ts_start < session_end):
                    continue
                ticker = str(row["ticker"])
                ts_end = ts_start + timedelta(minutes=1)
                bar = MarketDataBar1m(
                    ticker=ticker,
                    ts_start=ts_start,
                    ts_end=ts_end,
                    available_at=ts_end,
                    session_label=self._session_label(),
                    open=float(row["o"]),
                    high=float(row["h"]),
                    low=float(row["l"]),
                    close=float(row["c"]),
                    volume=int(row["v"]),
                    price_view=price_view,
                    quality_flags=self._quality_flags(row),
                    source_partition_id=self._source_partition_id(row, path),
                    source_file=path,
                )
                yield ReplayBarEvent(event_type="BAR", ticker=ticker, available_at=bar.available_at, bar=bar)

    def _load_gap_events(self) -> Iterable[ReplayGapEvent]:
        price_view = self._price_view()
        for result in self._report.get("physical_inspection", {}).get("per_ticker_day_results", ()): 
            ticker = str(result.get("ticker"))
            source_file = Path(result["file"]) if result.get("file") else None
            for gap_ts in result.get("observed_minute_gaps", ()): 
                ts_start = _parse_utc(gap_ts)
                ts_end = ts_start + timedelta(minutes=1)
                yield ReplayGapEvent(
                    event_type="GAP",
                    ticker=ticker,
                    ts_start=ts_start,
                    ts_end=ts_end,
                    available_at=ts_end,
                    session_label=self._session_label(),
                    price_view=price_view,
                    reason="OBSERVED_MINUTE_GAP",
                    source_file=source_file,
                )

    def _session_bounds_utc(self) -> tuple[datetime, datetime]:
        date_range = self._report.get("date_range", {})
        if date_range.get("date_start") != date_range.get("date_end"):
            raise ReplayContractError("REPLAY_MULTI_DAY_NOT_SUPPORTED", "minimum replay supports one session only")
        session_date = datetime.fromisoformat(date_range["date_start"]).date()
        timezone_name = str(self._report.get("timezone", "America/New_York"))
        tz = ZoneInfo(timezone_name)
        if self._report.get("session_policy") != "REGULAR_ONLY":
            raise ReplayContractError("REPLAY_SESSION_POLICY_NOT_SUPPORTED", "minimum replay supports REGULAR_ONLY only")
        start_local = datetime.combine(session_date, time(9, 30), tzinfo=tz)
        end_local = datetime.combine(session_date, time(16, 0), tzinfo=tz)
        return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)

    def _session_label(self) -> str:
        return f"{self._report.get('date_range', {}).get('date_start')}:{self._report.get('session_policy')}"

    def _price_view(self) -> str:
        return str(self._report.get("price_view_policy", {}).get("signal", {}).get("price_view", "UNKNOWN_PRICE_VIEW"))

    @staticmethod
    def _quality_flags(row: Mapping[str, Any]) -> tuple[str, ...]:
        flags: list[str] = []
        if row.get("quote_guarded_repair_applied") is True:
            flags.append("QUOTE_GUARDED_REPAIR_APPLIED")
        repair_state = row.get("repair_lookup_state")
        if repair_state:
            flags.append(f"REPAIR_LOOKUP_STATE:{repair_state}")
        return tuple(flags)

    @staticmethod
    def _source_partition_id(row: Mapping[str, Any], path: Path) -> str:
        dataset_id = row.get("dataset_id")
        build_run_id = row.get("build_run_id")
        if dataset_id and build_run_id:
            return f"{dataset_id}:{build_run_id}:{path.as_posix()}"
        return path.as_posix()

    @staticmethod
    def _event_sort_key(event: ReplayEvent) -> tuple[datetime, int, str]:
        priority = 0 if isinstance(event, ReplayGapEvent) else 1
        return (event.available_at, priority, event.ticker)


def _lookup_hash(expected_hashes: Mapping[str, str], path: Path) -> str | None:
    candidates = {str(path), path.as_posix()}
    try:
        candidates.add(str(path.resolve(strict=False)))
        candidates.add(path.resolve(strict=False).as_posix())
    except OSError:
        pass
    lowered = {candidate.lower(): value for candidate, value in expected_hashes.items()}
    for candidate in candidates:
        value = expected_hashes.get(candidate)
        if value is not None:
            return value
        value = lowered.get(candidate.lower())
        if value is not None:
            return value
    return None


def _parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ReplayContractError("REPLAY_TIMESTAMP_INVALID", "timestamp must be an ISO string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReplayContractError("REPLAY_TIMESTAMP_INVALID", value) from exc
    if parsed.tzinfo is None:
        raise ReplayContractError("REPLAY_TIMESTAMP_NOT_UTC", value)
    return parsed.astimezone(timezone.utc)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _event_sequence_sha256(events: tuple[ReplayEvent, ...]) -> str:
    return _canonical_sha256([event.to_dict() for event in events])
