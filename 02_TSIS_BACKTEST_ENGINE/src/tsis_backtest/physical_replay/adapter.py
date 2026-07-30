"Physical 013 OHLCV row to replay-event adapter for BT-GATE-013."

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import pyarrow.parquet as pq

from tsis_backtest.preflight.contracts import MarketDataBar1m, to_jsonable
from tsis_backtest.replay.contracts import ReplayBarEvent, ReplayGapEvent, ReplayRunSummary


BT_GATE_013 = "BT-GATE-013"
PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1 = "PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1"
PHYSICAL_BAR_REPLAY_ADAPTER_V0_1 = "PhysicalBarReplayAdapterV0_1"
SOURCE_TABLE_ID = "013_ohlcv_1m_quote_guarded"
SOURCE_LOGICAL_DATASET_ID = "ohlcv_1m_quote_guarded_v0_2_candidate"
SOURCE_PHYSICAL_DATASET_ID = "ohlcv_1m_quote_guarded_full_universe_v0_2_candidate"
SOURCE_ROOT_ID = "ohlcv_1m_quote_guarded_full_universe_v0_2_candidate"
SOURCE_TIMESTAMP_FIELD = "ts_utc"
SOURCE_TIMESTAMP_SEMANTICS = "BAR_START_UTC"
SOURCE_AS_OF_NATIVE_FIELD = "NONE"
SOURCE_AS_OF_POLICY_V0_1 = "NOT_APPLICABLE_FOR_STATIC_HASH_PINNED_PHYSICAL_FILE"
GAP_CAUSE_V0_1 = "UNKNOWN_SOURCE_GAP"

REQUIRED_COLUMNS = (
    "ticker",
    "ts_utc",
    "date",
    "year",
    "month",
    "o",
    "h",
    "l",
    "c",
    "v",
    "n",
    "t",
    "quote_guarded_repair_applied",
    "quote_guarded_view",
    "repair_lookup_state",
    "repair_state",
    "repair_reason",
    "source_quote_guarded_repair_manifest",
    "dataset_id",
    "build_run_id",
    "created_utc",
    "source_raw_path",
)
NON_CONSUMABLE_VENDOR_DERIVED_COLUMNS = ("vw",)


class PhysicalReplayAdapterError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True)
class PhysicalReplaySliceRequest:
    run_id: str
    physical_root: Path
    source_root_relative: str
    validation_manifest_path: Path
    validation_manifest_relative: str
    portable_fixture_manifest_path: Path
    portable_fixture_manifest_sha256: str
    session_calendar_snapshot_path: Path
    session_calendar_snapshot_relative: str
    session_calendar_snapshot_sha256: str
    symbols: tuple[str, ...]
    session_dates: tuple[date, ...]
    price_view: str = "quote_guarded_1m"
    session_policy: str = "REGULAR_ONLY_XNYS_V0_1"
    timezone: str = "America/New_York"
    calendar_id: str = "XNYS"

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PhysicalReplayBundle:
    events: tuple[ReplayBarEvent | ReplayGapEvent, ...]
    replay_summaries: tuple[ReplayRunSummary, ...]
    input_reports: tuple[Mapping[str, Any], ...]
    source_file_inventory: tuple[Mapping[str, Any], ...]
    selected_physical_rows: tuple[Mapping[str, Any], ...]
    row_to_event_lineage: tuple[Mapping[str, Any], ...]
    source_schema_binding: Mapping[str, Any]
    adapter_manifest: Mapping[str, Any]
    physical_request: PhysicalReplaySliceRequest

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


class PhysicalBarReplayAdapterV0_1:
    """Adapts frozen physical 013 rows into replay events without computing features."""

    def build_bundle(self, request: PhysicalReplaySliceRequest) -> PhysicalReplayBundle:
        self._validate_request(request)
        calendar_payload, calendar, calendar_metadata = self._load_calendar(request)
        fixture_manifest, fixture_file_index, fixture_metadata = self._load_fixture_manifest(request)
        _, validation_metadata = self._read_stable_json(
            request.validation_manifest_path,
            mutation_code="FAIL_SOURCE_MUTATION",
        )
        validation_manifest_sha256 = validation_metadata["hash_before_read"]
        expected_validation = fixture_manifest.get("validation_manifest", {})
        if validation_manifest_sha256 != expected_validation.get("sha256"):
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", str(request.validation_manifest_path))
        if request.validation_manifest_relative != expected_validation.get("canonical_relative_path"):
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", request.validation_manifest_relative)
        validation_size = validation_metadata["size_bytes"]
        if validation_size != int(expected_validation.get("size_bytes", -1)):
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", str(request.validation_manifest_path))
        source_file_inventory: list[dict[str, Any]] = []
        selected_rows: list[dict[str, Any]] = []
        lineages: list[dict[str, Any]] = []
        events: list[ReplayBarEvent | ReplayGapEvent] = []
        input_reports: list[dict[str, Any]] = []
        events_by_session: dict[date, list[ReplayBarEvent | ReplayGapEvent]] = {session: [] for session in request.session_dates}

        seen: dict[tuple[date, str, datetime], dict[str, Any]] = {}
        file_records: dict[str, dict[str, Any]] = {}
        for symbol in request.symbols:
            path = self._source_path(request, symbol)
            before_hash = sha256_file(path)
            relative_path = self._relative_source_path(path, request)
            expected_file = fixture_file_index.get(symbol.upper())
            if expected_file is None:
                raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", symbol)
            if relative_path != expected_file.get("canonical_source_relative_path"):
                raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", relative_path)
            source_size = path.stat().st_size
            if before_hash != expected_file.get("sha256") or source_size != int(expected_file.get("size_bytes", -1)):
                raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", str(path))
            file_records[symbol] = {
                "symbol": symbol,
                "source_relative_path": relative_path,
                "portable_fixture_relative_path": expected_file.get("portable_fixture_relative_path"),
                "inspection_location": str(path),
                "source_file_sha256": before_hash,
                "source_file_size_bytes": source_size,
                "expected_source_file_sha256": expected_file.get("sha256"),
                "expected_source_file_size_bytes": expected_file.get("size_bytes"),
                "authorized_fixture_manifest_sha256": request.portable_fixture_manifest_sha256,
                "source_identity_validation": "PASS",
            }
            parquet_file = pq.ParquetFile(path)
            schema_names = tuple(parquet_file.schema_arrow.names)
            missing = tuple(column for column in REQUIRED_COLUMNS if column not in schema_names)
            if missing:
                raise PhysicalReplayAdapterError("FAIL_SOURCE_SCHEMA_MISMATCH", f"{symbol}: {','.join(missing)}")
            source_file_inventory.append(
                {
                    **file_records[symbol],
                    "row_group_count": parquet_file.num_row_groups,
                    "source_file_row_count": parquet_file.metadata.num_rows,
                    "schema": [{"name": field.name, "type": str(field.type)} for field in parquet_file.schema_arrow],
                    "hash_before_read": before_hash,
                }
            )
            for row_group_index in range(parquet_file.num_row_groups):
                table = parquet_file.read_row_group(row_group_index, columns=list(REQUIRED_COLUMNS))
                for row_index, row in enumerate(table.to_pylist()):
                    ts_start = parse_utc(row["ts_utc"])
                    session_date = self._session_for_timestamp(ts_start, calendar)
                    if session_date is None or session_date not in request.session_dates:
                        continue
                    row_symbol = str(row["ticker"]).upper()
                    if row_symbol != symbol.upper():
                        raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", f"{symbol}: row ticker {row_symbol}")
                    key = (session_date, row_symbol, ts_start)
                    row_identity = self._row_identity(row, path, before_hash, row_group_index, row_index, request)
                    if key in seen:
                        duplicate_code = self._duplicate_code(seen[key]["row_signature"], self._row_signature(row))
                        raise PhysicalReplayAdapterError(duplicate_code, f"{session_date}:{row_symbol}:{ts_start.isoformat()}")
                    self._validate_row(row, symbol, ts_start, session_date)
                    row_identity["row_signature"] = self._row_signature(row)
                    seen[key] = row_identity
                    ts_end = ts_start + timedelta(minutes=1)
                    lineage = {
                        **row_identity,
                        "source_table_id": SOURCE_TABLE_ID,
                        "source_logical_dataset_id": SOURCE_LOGICAL_DATASET_ID,
                        "source_physical_dataset_id": SOURCE_PHYSICAL_DATASET_ID,
                        "source_root_id": SOURCE_ROOT_ID,
                        "source_root_relative": request.source_root_relative,
                        "source_timestamp_raw": row["ts_utc"],
                        "canonical_symbol": row_symbol,
                        "bar_start_timestamp_utc": ts_start,
                        "bar_end_timestamp_utc": ts_end,
                        "available_at_utc": ts_end,
                        "source_as_of_native_field": SOURCE_AS_OF_NATIVE_FIELD,
                        "source_as_of_policy": SOURCE_AS_OF_POLICY_V0_1,
                        "repair_fields_consumption": "LINEAGE_AND_RESTRICTION_VALIDATION_ONLY",
                        "repair_fields_strategy_input": "PROHIBITED",
                        "repair_fields_execution_input": "PROHIBITED",
                        "repair_fields_valuation_input": "PROHIBITED",
                        "repair_fields_decision_input": "PROHIBITED",
                        "provenance": {name: row.get(name) for name in ("dataset_id", "build_run_id", "created_utc", "source_raw_path")},
                        "repair_fields": {
                            name: row.get(name)
                            for name in (
                                "quote_guarded_repair_applied",
                                "quote_guarded_view",
                                "repair_lookup_state",
                                "repair_state",
                                "repair_reason",
                                "source_quote_guarded_repair_manifest",
                            )
                        },
                    }
                    selected = {
                        "session_date": session_date.isoformat(),
                        "ticker": row_symbol,
                        "bar_start_timestamp_utc": ts_start.isoformat(),
                        "source_row_locator": row_identity["source_row_locator"],
                        "source_relative_path": row_identity["source_relative_path"],
                    }
                    selected_rows.append(selected)
                    lineages.append(lineage)
                    bar = MarketDataBar1m(
                        ticker=row_symbol,
                        ts_start=ts_start,
                        ts_end=ts_end,
                        available_at=ts_end,
                        session_label=f"{session_date.isoformat()}:REGULAR_ONLY",
                        open=float(row["o"]),
                        high=float(row["h"]),
                        low=float(row["l"]),
                        close=float(row["c"]),
                        volume=self._volume(row["v"]),
                        price_view=request.price_view,
                        quality_flags=(),
                        source_partition_id=f"{SOURCE_ROOT_ID}:{row_identity['source_relative_path']}",
                        source_file=Path(row_identity["source_relative_path"]),
                    )
                    event = ReplayBarEvent("BAR", row_symbol, ts_end, bar, physical_lineage=lineage)
                    events.append(event)
                    events_by_session[session_date].append(event)
            after_hash = sha256_file(path)
            if after_hash != before_hash:
                raise PhysicalReplayAdapterError("FAIL_SOURCE_MUTATION", str(path))
            source_file_inventory[-1]["hash_after_read"] = after_hash

        self._validate_contractual_session_coverage(request, calendar, seen)
        gap_events = self._gap_events(request, calendar, seen, file_records)
        for event in gap_events:
            events.append(event)
            events_by_session[self._event_session(event)].append(event)
            lineages.append(event.physical_lineage or {})

        events = sorted(events, key=self._event_sort_key)
        for session in request.session_dates:
            session_events = tuple(sorted(events_by_session[session], key=self._event_sort_key))
            input_reports.append(
                self._input_report(
                    request,
                    session,
                    session_events,
                    source_file_inventory,
                    validation_manifest_sha256,
                    calendar_payload,
                )
            )
        summaries = tuple(
            ReplayRunSummary(
                preflight_run_id=f"bt_gate_013_physical_adapter_{session.isoformat()}",
                event_count=len(events_by_session[session]),
                bar_count=sum(isinstance(event, ReplayBarEvent) for event in events_by_session[session]),
                gap_count=sum(isinstance(event, ReplayGapEvent) for event in events_by_session[session]),
                symbols=request.symbols,
                first_available_at=min((event.available_at for event in events_by_session[session]), default=None),
                last_available_at=max((event.available_at for event in events_by_session[session]), default=None),
                warning_codes=("UNKNOWN_SOURCE_GAP",) if any(isinstance(event, ReplayGapEvent) for event in events_by_session[session]) else (),
                replay_preflight_report_sha256=None,
                replay_event_sequence_sha256=canonical_sha256([event.to_dict() for event in sorted(events_by_session[session], key=self._event_sort_key)]),
            )
            for session in request.session_dates
        )
        adapter_manifest = {
            "adapter_id": PHYSICAL_BAR_REPLAY_ADAPTER_V0_1,
            "gate_id": BT_GATE_013,
            "source_table_id": SOURCE_TABLE_ID,
            "source_logical_dataset_id": SOURCE_LOGICAL_DATASET_ID,
            "source_physical_dataset_id": SOURCE_PHYSICAL_DATASET_ID,
            "source_root_id": SOURCE_ROOT_ID,
            "source_root_relative": request.source_root_relative,
            "validation_manifest_relative": request.validation_manifest_relative,
            "validation_manifest_sha256": validation_manifest_sha256,
            "validation_manifest_size_bytes": validation_size,
            "validation_manifest_hash_before_read": validation_metadata["hash_before_read"],
            "validation_manifest_hash_after_read": validation_metadata["hash_after_read"],
            "portable_fixture_manifest_relative": self._portable_fixture_manifest_relative(request),
            "portable_fixture_manifest_sha256": request.portable_fixture_manifest_sha256,
            "fixture_manifest_sha256": fixture_metadata["hash_after_read"],
            "fixture_manifest_size_bytes": fixture_metadata["size_bytes"],
            "fixture_manifest_hash_before_read": fixture_metadata["hash_before_read"],
            "fixture_manifest_hash_after_read": fixture_metadata["hash_after_read"],
            "fixture_manifest_validation": "PASS",
            "calendar_relative_path": request.session_calendar_snapshot_relative,
            "calendar_snapshot_sha256": calendar_metadata["hash_after_read"],
            "calendar_snapshot_size_bytes": calendar_metadata["size_bytes"],
            "calendar_hash_before_read": calendar_metadata["hash_before_read"],
            "calendar_hash_after_read": calendar_metadata["hash_after_read"],
            "symbols": request.symbols,
            "sessions": tuple(session.isoformat() for session in request.session_dates),
            "event_count": len(events),
            "bar_count": sum(isinstance(event, ReplayBarEvent) for event in events),
            "gap_count": sum(isinstance(event, ReplayGapEvent) for event in events),
            "source_file_count": len(source_file_inventory),
            "selected_physical_row_count": len(selected_rows),
            "scientific_hash_excludes": ("absolute_path", "package_timestamp", "wall_clock_duration", "host_name", "user_name", "process_id"),
        }
        self.validate_temporal_availability(events)
        return PhysicalReplayBundle(
            tuple(events),
            summaries,
            tuple(input_reports),
            tuple(source_file_inventory),
            tuple(selected_rows),
            tuple(lineages),
            self.source_schema_binding(),
            adapter_manifest,
            request,
        )

    @staticmethod
    def source_schema_binding() -> dict[str, Any]:
        return {
            "source_symbol_field": "ticker",
            "source_timestamp_field": "ts_utc",
            "source_timestamp_semantics": SOURCE_TIMESTAMP_SEMANTICS,
            "source_epoch_ms_confirmation_field": "t",
            "source_date_field": "date",
            "source_year_field": "year",
            "source_month_field": "month",
            "source_open_field": "o",
            "source_high_field": "h",
            "source_low_field": "l",
            "source_close_field": "c",
            "source_volume_field": "v",
            "source_transaction_count_field": "n",
            "non_consumable_vendor_derived_columns": NON_CONSUMABLE_VENDOR_DERIVED_COLUMNS,
            "requested_columns": REQUIRED_COLUMNS,
            "volume_policy": "REQUIRE_FINITE_NON_NEGATIVE_INTEGER_VALUED",
            "available_at_policy": "bar_start_timestamp_utc + 1 minute",
            "source_as_of_native_field": SOURCE_AS_OF_NATIVE_FIELD,
            "source_as_of_policy": SOURCE_AS_OF_POLICY_V0_1,
        }

    def _validate_request(self, request: PhysicalReplaySliceRequest) -> None:
        if tuple(request.symbols) != ("ABAT", "ABEO", "ABSI", "ABTC", "ACB"):
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", str(request.symbols))
        if tuple(session.isoformat() for session in request.session_dates) != ("2026-01-05", "2026-01-06"):
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", str(request.session_dates))
        if not request.physical_root.exists():
            raise PhysicalReplayAdapterError("FAIL_SOURCE_ROOT_NOT_FOUND", str(request.physical_root))
        if not request.validation_manifest_path.exists():
            raise PhysicalReplayAdapterError("FAIL_VALIDATION_MANIFEST_NOT_FOUND", str(request.validation_manifest_path))
        if not request.portable_fixture_manifest_path.exists():
            raise PhysicalReplayAdapterError("FAIL_FIXTURE_MANIFEST_NOT_FOUND", str(request.portable_fixture_manifest_path))

    def _load_fixture_manifest(
        self,
        request: PhysicalReplaySliceRequest,
    ) -> tuple[Mapping[str, Any], dict[str, Mapping[str, Any]], Mapping[str, Any]]:
        payload, metadata = self._read_stable_json(
            request.portable_fixture_manifest_path,
            mutation_code="FAIL_SOURCE_MUTATION",
        )
        actual_hash = metadata["hash_before_read"]
        if actual_hash != request.portable_fixture_manifest_sha256:
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", str(request.portable_fixture_manifest_path))
        if payload.get("gate_id") != BT_GATE_013 or payload.get("capability") != PHYSICAL_HISTORICAL_REPLAY_SLICE_V0_1:
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", "fixture manifest identity")
        if payload.get("canonical_source_root_relative") != request.source_root_relative:
            raise PhysicalReplayAdapterError("FAIL_SOURCE_HASH_MISMATCH", "source root relative mismatch")
        if tuple(payload.get("symbols", ())) != tuple(request.symbols):
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", "fixture symbol set mismatch")
        if tuple(payload.get("sessions", ())) != tuple(session.isoformat() for session in request.session_dates):
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", "fixture session set mismatch")
        if payload.get("selection_policy") != "OPERATIONAL_COVERAGE_ONLY":
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", "fixture selection policy mismatch")
        file_index = {str(item["symbol"]).upper(): item for item in payload.get("files", ())}
        if set(file_index) != {symbol.upper() for symbol in request.symbols}:
            raise PhysicalReplayAdapterError("FAIL_SCOPE_LEAKAGE", "fixture files mismatch")
        return payload, file_index, metadata

    def _load_calendar(
        self,
        request: PhysicalReplaySliceRequest,
    ) -> tuple[Mapping[str, Any], dict[date, tuple[datetime, datetime]], Mapping[str, Any]]:
        payload, metadata = self._read_stable_json(
            request.session_calendar_snapshot_path,
            mutation_code="FAIL_SOURCE_MUTATION",
        )
        if metadata["hash_before_read"] != request.session_calendar_snapshot_sha256:
            raise PhysicalReplayAdapterError("FAIL_CALENDAR_HASH_MISMATCH", str(request.session_calendar_snapshot_path))
        if payload.get("calendar_authority") != "TSIS_PORTABLE_SESSION_CALENDAR_SNAPSHOT_V0_1":
            raise PhysicalReplayAdapterError("FAIL_CALENDAR_AUTHORITY", str(payload.get("calendar_authority")))
        if payload.get("calendar_id") != request.calendar_id or payload.get("timezone") != request.timezone:
            raise PhysicalReplayAdapterError("FAIL_CALENDAR_TIMEZONE_CONTRACT", f"{payload.get('calendar_id')}:{payload.get('timezone')}")
        calendar: dict[date, tuple[datetime, datetime]] = {}
        for row in payload.get("sessions", ()):
            session = date.fromisoformat(str(row["session_date"]))
            if session in request.session_dates:
                calendar[session] = (parse_utc(row["regular_open_utc"]), parse_utc(row["regular_close_utc"]))
        if set(calendar) != set(request.session_dates):
            raise PhysicalReplayAdapterError("FAIL_CALENDAR_SESSION_SET", str(sorted(calendar)))
        return payload, calendar, metadata

    @staticmethod
    def _read_stable_json(path: Path, *, mutation_code: str) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
        hash_before = sha256_file(path)
        size_before = path.stat().st_size
        payload = json.loads(path.read_text(encoding="utf-8"))
        hash_after = sha256_file(path)
        size_after = path.stat().st_size
        if hash_after != hash_before or size_after != size_before:
            raise PhysicalReplayAdapterError(mutation_code, str(path))
        return payload, {
            "size_bytes": size_after,
            "hash_before_read": hash_before,
            "hash_after_read": hash_after,
        }

    def _source_path(self, request: PhysicalReplaySliceRequest, symbol: str) -> Path:
        return request.physical_root / "year=2026" / f"ticker={symbol}" / "month=01" / "part-000.parquet"

    def _relative_source_path(self, path: Path, request: PhysicalReplaySliceRequest) -> str:
        return f"{request.source_root_relative}/{path.relative_to(request.physical_root).as_posix()}"

    def _session_for_timestamp(self, ts: datetime, calendar: Mapping[date, tuple[datetime, datetime]]) -> date | None:
        for session, (open_utc, close_utc) in calendar.items():
            if open_utc <= ts < close_utc:
                return session
        return None

    def _row_identity(self, row: Mapping[str, Any], path: Path, source_hash: str, row_group: int, row_index: int, request: PhysicalReplaySliceRequest) -> dict[str, Any]:
        return {
            "source_file_sha256": source_hash,
            "source_file_size_bytes": path.stat().st_size,
            "source_relative_path": self._relative_source_path(path, request),
            "source_row_locator": {
                "source_file_sha256": source_hash,
                "parquet_row_group_index": row_group,
                "row_index_within_row_group": row_index,
                "zero_based": True,
                "computed_from_physical_parquet_order": True,
                "dataframe_order": "prohibited",
                "filesystem_enumeration_order": "prohibited",
            },
            "source_symbol": row.get("ticker"),
            "source_timestamp": row.get("ts_utc"),
        }

    @staticmethod
    def _row_signature(row: Mapping[str, Any]) -> str:
        material_fields = ("ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v", "n", "t")
        return canonical_sha256({name: row.get(name) for name in material_fields})

    @staticmethod
    def _duplicate_code(previous_signature: str, current_signature: str) -> str:
        if previous_signature == current_signature:
            return "FAIL_DUPLICATE_PHYSICAL_BAR"
        return "FAIL_CONFLICTING_PHYSICAL_BAR"

    def _validate_row(self, row: Mapping[str, Any], symbol: str, ts_start: datetime, session: date) -> None:
        if row.get("date") != session.isoformat() or int(row.get("year")) != session.year or int(row.get("month")) != session.month:
            raise PhysicalReplayAdapterError("FAIL_SOURCE_DATE_PARTITION_MISMATCH", f"{symbol}:{ts_start.isoformat()}")
        epoch_ms = int(ts_start.timestamp() * 1000)
        if int(row["t"]) != epoch_ms:
            raise PhysicalReplayAdapterError("FAIL_EPOCH_MS_MISMATCH", f"{symbol}:{ts_start.isoformat()}")
        o, h, l, c = (float(row[name]) for name in ("o", "h", "l", "c"))
        if any(not math.isfinite(value) or value <= 0 for value in (o, h, l, c)):
            raise PhysicalReplayAdapterError("FAIL_INVALID_PHYSICAL_BAR", f"{symbol}:{ts_start.isoformat()}")
        if h < max(o, l, c) or l > min(o, h, c):
            raise PhysicalReplayAdapterError("FAIL_INVALID_PHYSICAL_BAR", f"{symbol}:{ts_start.isoformat()}")
        self._volume(row["v"])

    @staticmethod
    def _volume(value: Any) -> int:
        volume = float(value)
        if not math.isfinite(volume) or volume < 0 or volume != int(volume):
            raise PhysicalReplayAdapterError("FAIL_INVALID_PHYSICAL_BAR", f"invalid volume {value}")
        return int(volume)

    def _validate_contractual_session_coverage(
        self,
        request: PhysicalReplaySliceRequest,
        calendar: Mapping[date, tuple[datetime, datetime]],
        seen: Mapping[tuple[date, str, datetime], Mapping[str, Any]],
    ) -> None:
        for session in request.session_dates:
            open_utc, close_utc = calendar[session]
            final_bar_start = close_utc - timedelta(minutes=1)
            for symbol in request.symbols:
                if (session, symbol.upper(), final_bar_start) not in seen:
                    raise PhysicalReplayAdapterError("FAIL_MISSING_CONTRACTUAL_CLOSE", f"{session.isoformat()}:{symbol}")
                if (session, symbol.upper(), open_utc) not in seen:
                    raise PhysicalReplayAdapterError("FAIL_TRUNCATED_PHYSICAL_SESSION", f"{session.isoformat()}:{symbol}")

    @staticmethod
    def validate_temporal_availability(events: tuple[ReplayBarEvent | ReplayGapEvent, ...] | list[ReplayBarEvent | ReplayGapEvent]) -> None:
        for event in events:
            if isinstance(event, ReplayBarEvent):
                if event.available_at != event.bar.ts_end or event.available_at < event.bar.ts_end:
                    raise PhysicalReplayAdapterError("FAIL_TEMPORAL_AVAILABILITY_VIOLATION", event.ticker)
            else:
                if event.available_at != event.ts_end or event.available_at < event.ts_end:
                    raise PhysicalReplayAdapterError("FAIL_TEMPORAL_AVAILABILITY_VIOLATION", event.ticker)

    def _gap_events(
        self,
        request: PhysicalReplaySliceRequest,
        calendar: Mapping[date, tuple[datetime, datetime]],
        seen: Mapping[tuple[date, str, datetime], Mapping[str, Any]],
        file_records: Mapping[str, Mapping[str, Any]],
    ) -> tuple[ReplayGapEvent, ...]:
        gaps: list[ReplayGapEvent] = []
        for session in request.session_dates:
            open_utc, close_utc = calendar[session]
            minute = open_utc
            while minute < close_utc:
                for symbol in request.symbols:
                    key = (session, symbol.upper(), minute)
                    if key not in seen:
                        lineage = {
                            "source_table_id": SOURCE_TABLE_ID,
                            "source_root_id": SOURCE_ROOT_ID,
                            "source_relative_path": file_records[symbol]["source_relative_path"],
                            "source_file_sha256": file_records[symbol]["source_file_sha256"],
                            "canonical_symbol": symbol.upper(),
                            "session_date": session.isoformat(),
                            "expected_bar_start_timestamp_utc": minute,
                            "expected_bar_end_timestamp_utc": minute + timedelta(minutes=1),
                            "available_at_utc": minute + timedelta(minutes=1),
                            "gap_detection_rule_version": "EXPECTED_REGULAR_SESSION_MINUTE_MINUS_OBSERVED_KEYS_V0_1",
                            "gap_cause": GAP_CAUSE_V0_1,
                            "halt_inference": "NOT_AUTHORIZED",
                            "source_row_locator": None,
                        }
                        gaps.append(
                            ReplayGapEvent(
                                "GAP",
                                symbol.upper(),
                                minute,
                                minute + timedelta(minutes=1),
                                minute + timedelta(minutes=1),
                                f"{session.isoformat()}:REGULAR_ONLY",
                                request.price_view,
                                GAP_CAUSE_V0_1,
                                source_file=Path(file_records[symbol]["source_relative_path"]),
                                physical_lineage=lineage,
                            )
                        )
                minute += timedelta(minutes=1)
        return tuple(gaps)

    @staticmethod
    def _event_session(event: ReplayBarEvent | ReplayGapEvent) -> date:
        label = event.bar.session_label if isinstance(event, ReplayBarEvent) else event.session_label
        return date.fromisoformat(str(label).split(":", 1)[0])

    def _input_report(
        self,
        request: PhysicalReplaySliceRequest,
        session: date,
        events: tuple[ReplayBarEvent | ReplayGapEvent, ...],
        source_file_inventory: list[Mapping[str, Any]],
        validation_manifest_sha256: str,
        calendar_payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "run_id": f"bt_gate_013_physical_adapter_{session.isoformat()}",
            "resolved": True,
            "preflight_status": "PREFLIGHT_PASS",
            "physical_inspection_status": "PHYSICAL_INSPECTION_PASS",
            "dataset_id": SOURCE_PHYSICAL_DATASET_ID,
            "fixture_kind": "TSIS_REAL_DATA_FIXTURE",
            "source_table_id": SOURCE_TABLE_ID,
            "date_range": {"date_start": session.isoformat(), "date_end": session.isoformat()},
            "session_policy": "REGULAR_ONLY",
            "timezone": request.timezone,
            "calendar_id": request.calendar_id,
            "symbols_available": request.symbols,
            "rows_available": sum(isinstance(event, ReplayBarEvent) for event in events),
            "source_partitions_or_files_consumed": tuple(item["source_relative_path"] for item in source_file_inventory),
            "snapshot_or_content_hashes": {item["source_relative_path"]: item["source_file_sha256"] for item in source_file_inventory},
            "source_validation_manifest_relative": request.validation_manifest_relative,
            "source_validation_manifest_sha256": validation_manifest_sha256,
            "portable_fixture_manifest_relative": self._portable_fixture_manifest_relative(request),
            "portable_fixture_manifest_sha256": request.portable_fixture_manifest_sha256,
            "physical_replay_adapter_id": PHYSICAL_BAR_REPLAY_ADAPTER_V0_1,
            "source_schema_binding": self.source_schema_binding(),
            "calendar_snapshot_sha256": sha256_file(request.session_calendar_snapshot_path),
            "event_count": len(events),
            "bar_count": sum(isinstance(event, ReplayBarEvent) for event in events),
            "gap_count": sum(isinstance(event, ReplayGapEvent) for event in events),
            "calendar_snapshot": calendar_payload,
        }

    @staticmethod
    def _portable_fixture_manifest_relative(request: PhysicalReplaySliceRequest) -> str:
        parts = request.portable_fixture_manifest_path.parts
        try:
            index = parts.index("tests")
        except ValueError:
            return request.portable_fixture_manifest_path.as_posix()
        return Path(*parts[index:]).as_posix()

    @staticmethod
    def _event_sort_key(event: ReplayBarEvent | ReplayGapEvent) -> tuple[datetime, date, int, str, str]:
        session = PhysicalBarReplayAdapterV0_1._event_session(event)
        priority = 0 if isinstance(event, ReplayGapEvent) else 1
        if isinstance(event, ReplayBarEvent):
            identity = f"{event.ticker}:{event.bar.ts_start.isoformat()}:{event.bar.ts_end.isoformat()}:BAR"
        else:
            identity = f"{event.ticker}:{event.ts_start.isoformat()}:{event.ts_end.isoformat()}:GAP"
        return (event.available_at, session, priority, event.ticker.upper(), identity)


def parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise PhysicalReplayAdapterError("FAIL_AMBIGUOUS_SOURCE_TIMESTAMP", str(value))
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PhysicalReplayAdapterError("FAIL_AMBIGUOUS_SOURCE_TIMESTAMP", value) from exc
    if parsed.tzinfo is None:
        raise PhysicalReplayAdapterError("FAIL_AMBIGUOUS_SOURCE_TIMESTAMP", value)
    return parsed.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

