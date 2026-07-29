"""Physical data inspection for the first TSIS real-data fixture."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import pyarrow.parquet as pq

from .contracts import MissingDataPolicy, ResolvedDataContext, RunDataRequest, to_jsonable


PHYSICAL_INSPECTION_PASS = "PHYSICAL_INSPECTION_PASS"
PHYSICAL_INSPECTION_FAIL = "PHYSICAL_INSPECTION_FAIL"
PASS_COMPLETE = "PASS_COMPLETE"
PASS_WITH_GAPS = "PASS_WITH_GAPS"
FAIL = "FAIL"


@dataclass(frozen=True)
class TickerDayInspection:
    ticker: str
    session_date: str
    status: str
    file: Path | None
    file_found: bool
    file_sha256: str | None
    monthly_rows: int
    session_rows: int
    session_min_utc: str | None
    session_max_utc: str | None
    has_required_open: bool
    has_required_close: bool
    missing_regular_minutes: int
    observed_minute_gaps: tuple[str, ...]
    duplicate_timestamps: int
    invalid_core_rows: int
    invalid_core_issue_counts: Mapping[str, int]
    optional_columns_present: tuple[str, ...]
    optional_columns_missing: tuple[str, ...]
    warning_codes: tuple[str, ...]
    failure_codes: tuple[str, ...]
    expected_discovery_drift: tuple[str, ...]


@dataclass(frozen=True)
class UniverseScreen:
    universe_id: str
    physical_path: Path
    sha256: str | None
    expected_sha256: str | None
    symbols_checked: tuple[str, ...]
    missing_symbols: tuple[str, ...]
    outside_pti_symbols: tuple[str, ...]
    disallowed_classification_symbols: tuple[str, ...]
    failure_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class CorporateActionScreen:
    dataset_id: str
    physical_path: Path
    table_sha256: str | None
    expected_table_sha256: str | None
    manifest_path: Path | None
    manifest_sha256: str | None
    expected_manifest_sha256: str | None
    symbols_consulted: tuple[str, ...]
    temporal_field: str
    window_start: str
    window_end: str
    session_date: str
    rows_found: int
    exact_session_rows: int
    action_types_found: tuple[str, ...]
    failure_codes: tuple[str, ...]
    warning_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


@dataclass(frozen=True)
class PhysicalDataInspection:
    inspection_status: str
    fixture_id: str
    fixture_kind: str
    files_consumed: tuple[Path, ...]
    content_hashes: Mapping[str, str]
    rows_available: int
    symbols_requested: tuple[str, ...]
    symbols_found: tuple[str, ...]
    observed_time_range: Mapping[str, str | None]
    per_ticker_day_results: tuple[TickerDayInspection, ...]
    missing_data_summary: Mapping[str, Any]
    universe_screen: UniverseScreen
    corporate_action_screen: CorporateActionScreen
    dataset_validation_manifest: Mapping[str, Any]
    failure_codes: tuple[str, ...]
    warning_codes: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return to_jsonable(self)


class RealDataInspector:
    def __init__(self, fixture_config: Mapping[str, Any], fixture_config_path: Path | None = None) -> None:
        self._config = dict(fixture_config)
        self._fixture_config_path = fixture_config_path

    @classmethod
    def from_fixture_config(cls, path: Path) -> "RealDataInspector":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload, fixture_config_path=path)

    def inspect(self, request: RunDataRequest, context: ResolvedDataContext) -> PhysicalDataInspection:
        fixture = self._config
        symbols = tuple(request.symbols_optional or context.selected_symbols)
        request_binding_failures = self._request_binding_failures(request, context, symbols)
        validation_manifest_screen, validation_manifest_failures = self._inspect_dataset_validation_manifest()
        session = fixture["session"]
        session_date = _date_from_iso(session["session_date"])
        start_utc = _parse_utc(session["regular_session_filter_utc_for_this_date"]["start_inclusive"])
        end_utc = _parse_utc(session["regular_session_filter_utc_for_this_date"]["end_exclusive"])
        open_proxy = _parse_utc(session["open_proxy_ts_utc"])
        close_proxy = _parse_utc(session["close_proxy_ts_utc"])

        universe_screen = self._inspect_universe(symbols, session_date)
        ticker_results = tuple(
            self._inspect_ticker_day(
                ticker=ticker,
                session_date=session_date,
                start_utc=start_utc,
                end_utc=end_utc,
                open_proxy=open_proxy,
                close_proxy=close_proxy,
                missing_policy=request.missing_data_policy,
            )
            for ticker in symbols
        )
        corporate_action_screen = self._inspect_corporate_actions(symbols, session_date)

        files_consumed = tuple(result.file for result in ticker_results if result.file is not None and result.file_found)
        content_hashes = {str(result.file): result.file_sha256 for result in ticker_results if result.file is not None and result.file_sha256}
        if universe_screen.sha256 is not None:
            content_hashes[str(universe_screen.physical_path)] = universe_screen.sha256
        if corporate_action_screen.table_sha256 is not None:
            content_hashes[str(corporate_action_screen.physical_path)] = corporate_action_screen.table_sha256
        if corporate_action_screen.manifest_path is not None and corporate_action_screen.manifest_sha256 is not None:
            content_hashes[str(corporate_action_screen.manifest_path)] = corporate_action_screen.manifest_sha256
        validation_manifest_path = validation_manifest_screen.get("path")
        validation_manifest_sha256 = validation_manifest_screen.get("sha256")
        if validation_manifest_path is not None and validation_manifest_sha256 is not None:
            content_hashes[str(validation_manifest_path)] = str(validation_manifest_sha256)

        rows_available = sum(result.session_rows for result in ticker_results)
        all_times = [
            value
            for result in ticker_results
            for value in (result.session_min_utc, result.session_max_utc)
            if value is not None
        ]
        missing_symbols = tuple(result.ticker for result in ticker_results if not result.file_found)
        failure_codes = []
        warning_codes = []
        failure_codes.extend(request_binding_failures)
        failure_codes.extend(validation_manifest_failures)
        for screen_code in universe_screen.failure_codes:
            failure_codes.append(screen_code)
        for result in ticker_results:
            failure_codes.extend(result.failure_codes)
            warning_codes.extend(result.warning_codes)
        failure_codes.extend(corporate_action_screen.failure_codes)
        warning_codes.extend(corporate_action_screen.warning_codes)

        inspection_status = PHYSICAL_INSPECTION_PASS if not failure_codes else PHYSICAL_INSPECTION_FAIL
        gap_tickers = tuple(result.ticker for result in ticker_results if result.missing_regular_minutes > 0 and result.status != FAIL)
        complete_tickers = tuple(result.ticker for result in ticker_results if result.status == PASS_COMPLETE)

        return PhysicalDataInspection(
            inspection_status=inspection_status,
            fixture_id=str(fixture.get("fixture_id", "UNKNOWN_FIXTURE")),
            fixture_kind=str(fixture.get("fixture_kind", request.fixture_kind)),
            files_consumed=files_consumed,
            content_hashes=content_hashes,
            rows_available=rows_available,
            symbols_requested=symbols,
            symbols_found=tuple(result.ticker for result in ticker_results if result.file_found),
            observed_time_range={
                "min_utc": min(all_times) if all_times else None,
                "max_utc": max(all_times) if all_times else None,
            },
            per_ticker_day_results=ticker_results,
            missing_data_summary={
                "inspection_status": "pass" if not missing_symbols else "fail",
                "policy_id": request.missing_data_policy.policy_id,
                "gap_policy": request.missing_data_policy.on_missing_bar,
                "complete_tickers": complete_tickers,
                "gap_tickers": gap_tickers,
                "missing_symbols": missing_symbols,
            },
            universe_screen=universe_screen,
            corporate_action_screen=corporate_action_screen,
            dataset_validation_manifest=validation_manifest_screen,
            failure_codes=tuple(dict.fromkeys(failure_codes)),
            warning_codes=tuple(dict.fromkeys(warning_codes)),
            limitations=tuple(self._config.get("limitations", ())),
        )

    def _request_binding_failures(
        self,
        request: RunDataRequest,
        context: ResolvedDataContext,
        symbols: tuple[str, ...],
    ) -> tuple[str, ...]:
        fixture = self._config
        failures: list[str] = []
        expected_fixture_id = str(fixture.get("fixture_id", ""))
        if not request.fixture_id or request.fixture_id != expected_fixture_id:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        dataset = fixture.get("dataset", {})
        if request.dataset_id != dataset.get("dataset_id") or context.dataset_id != dataset.get("dataset_id"):
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        universe = fixture.get("universe", {})
        if request.universe_id != universe.get("universe_id") or context.universe_dataset_id != universe.get("universe_id"):
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        session = fixture.get("session", {})
        fixture_date_raw = session.get("session_date")
        try:
            fixture_date = _date_from_iso(str(fixture_date_raw))
        except ValueError:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")
        else:
            if request.date_start != fixture_date or request.date_end != fixture_date:
                failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        if request.session_policy != session.get("session_policy"):
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")
        if request.calendar_id != session.get("calendar_id"):
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")
        if request.timezone != session.get("timezone"):
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        price_view_policy = fixture.get("price_view_policy", {})
        expected_signal = price_view_policy.get("signal", {}).get("price_view")
        expected_execution = price_view_policy.get("execution", {}).get("price_view")
        expected_valuation = price_view_policy.get("valuation", {}).get("price_view")
        if request.signal_price_view != expected_signal:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")
        if request.execution_price_view != expected_execution:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")
        if request.valuation_price_view != expected_valuation:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        fixture_symbols = tuple(fixture.get("symbols", ()))
        if symbols != fixture_symbols:
            failures.append("REAL_FIXTURE_REQUEST_MISMATCH")

        return tuple(dict.fromkeys(failures))

    def _inspect_dataset_validation_manifest(self) -> tuple[dict[str, Any], tuple[str, ...]]:
        dataset = self._config.get("dataset", {})
        path_raw = dataset.get("validation_manifest")
        expected_hash = dataset.get("validation_manifest_sha256")
        screen: dict[str, Any] = {
            "path": Path(path_raw) if path_raw else None,
            "sha256": None,
            "expected_sha256": expected_hash,
        }
        failures: list[str] = []
        if not path_raw:
            failures.append("VALIDATION_MANIFEST_PATH_REQUIRED")
            return screen, tuple(failures)
        path = Path(path_raw)
        if not path.exists():
            failures.append("VALIDATION_MANIFEST_NOT_FOUND")
            return screen, tuple(failures)
        actual_hash = sha256_file(path)
        screen["sha256"] = actual_hash
        if expected_hash and actual_hash != expected_hash:
            failures.append("VALIDATION_MANIFEST_HASH_MISMATCH")
        return screen, tuple(failures)

    def _inspect_ticker_day(
        self,
        ticker: str,
        session_date: date,
        start_utc: datetime,
        end_utc: datetime,
        open_proxy: datetime,
        close_proxy: datetime,
        missing_policy: MissingDataPolicy,
    ) -> TickerDayInspection:
        dataset = self._config["dataset"]
        root = Path(dataset["physical_root"])
        path = root / f"year={session_date.year}" / f"ticker={ticker}" / f"month={session_date.month:02d}" / "part-000.parquet"
        expected = self._expected_for_ticker(ticker)
        required_columns = tuple(dataset["minimum_required_columns"])
        optional_columns = tuple(dataset.get("optional_columns_observed_in_fixture", ()))
        allowed_row_dataset_ids = tuple(dataset.get("allowed_row_dataset_ids", ()))
        expected_row_build_run_ids = tuple(dataset.get("expected_row_build_run_ids", ()))

        if not path.exists():
            return self._ticker_failure(ticker, session_date, path, "FILE_NOT_FOUND")

        file_hash = sha256_file(path)
        try:
            parquet_file = pq.ParquetFile(path)
        except Exception:
            return self._ticker_failure(ticker, session_date, path, "PARQUET_READ_ERROR", file_sha256=file_hash)

        schema_names = tuple(parquet_file.schema_arrow.names)
        missing_required = tuple(column for column in required_columns if column not in schema_names)
        if missing_required:
            return self._ticker_failure(
                ticker,
                session_date,
                path,
                "SCHEMA_MISSING_REQUIRED_COLUMNS",
                file_sha256=file_hash,
                optional_columns_present=tuple(column for column in optional_columns if column in schema_names),
                optional_columns_missing=tuple(column for column in optional_columns if column not in schema_names),
            )

        table = parquet_file.read(columns=list(required_columns))
        rows = table.to_pylist()
        session_rows: list[dict[str, Any]] = []
        issue_counts: dict[str, int] = {}
        invalid_rows = 0
        timestamp_counts: dict[str, int] = {}

        for row in rows:
            ts = _safe_parse_utc(row.get("ts_utc"))
            if ts is None:
                _increment(issue_counts, "timestamp_null_or_unparseable")
                continue
            if start_utc <= ts < end_utc:
                session_rows.append(row)
                timestamp_counts[ts.isoformat().replace("+00:00", "Z")] = timestamp_counts.get(ts.isoformat().replace("+00:00", "Z"), 0) + 1
                row_issues = self._row_core_issues(
                    row=row,
                    partition_ticker=ticker,
                    session_date=session_date,
                    ts=ts,
                    allowed_row_dataset_ids=allowed_row_dataset_ids,
                    expected_row_build_run_ids=expected_row_build_run_ids,
                )
                if row_issues:
                    invalid_rows += 1
                    for issue in row_issues:
                        _increment(issue_counts, issue)

        observed_times = sorted(_safe_parse_utc(row.get("ts_utc")) for row in session_rows if _safe_parse_utc(row.get("ts_utc")) is not None)
        observed_set = set(observed_times)
        expected_minutes = tuple(_minute_range(start_utc, end_utc))
        gaps = tuple(ts.isoformat().replace("+00:00", "Z") for ts in expected_minutes if ts not in observed_set)
        has_open = open_proxy in observed_set
        has_close = close_proxy in observed_set
        duplicates = sum(count - 1 for count in timestamp_counts.values() if count > 1)

        failure_codes: list[str] = []
        warning_codes: list[str] = []
        if not has_open:
            failure_codes.append("REQUIRED_OPEN_BAR_MISSING")
        if not has_close:
            failure_codes.append("REQUIRED_CLOSE_BAR_MISSING")
        if duplicates:
            failure_codes.append("DUPLICATE_TIMESTAMPS")
        if invalid_rows:
            failure_codes.append("INVALID_CORE_ROWS")
        if gaps:
            warning_codes.append("OBSERVED_MINUTE_GAP")
            if missing_policy.on_missing_bar != "EMIT_GAP_WITHOUT_IMPUTATION":
                failure_codes.append("OBSERVED_MINUTE_GAP_NOT_ALLOWED")
        drift = self._discovery_drift(
            expected=expected,
            file_hash=file_hash,
            session_rows=len(session_rows),
            missing_regular_minutes=len(gaps),
            has_open=has_open,
            has_close=has_close,
        )
        if drift:
            failure_codes.append("EXPECTED_DISCOVERY_EVIDENCE_DRIFT")

        if failure_codes:
            status = FAIL
        elif gaps:
            status = PASS_WITH_GAPS
        else:
            status = PASS_COMPLETE

        return TickerDayInspection(
            ticker=ticker,
            session_date=session_date.isoformat(),
            status=status,
            file=path,
            file_found=True,
            file_sha256=file_hash,
            monthly_rows=len(rows),
            session_rows=len(session_rows),
            session_min_utc=observed_times[0].isoformat().replace("+00:00", "Z") if observed_times else None,
            session_max_utc=observed_times[-1].isoformat().replace("+00:00", "Z") if observed_times else None,
            has_required_open=has_open,
            has_required_close=has_close,
            missing_regular_minutes=len(gaps),
            observed_minute_gaps=gaps,
            duplicate_timestamps=duplicates,
            invalid_core_rows=invalid_rows,
            invalid_core_issue_counts=issue_counts,
            optional_columns_present=tuple(column for column in optional_columns if column in schema_names),
            optional_columns_missing=tuple(column for column in optional_columns if column not in schema_names),
            warning_codes=tuple(dict.fromkeys(warning_codes)),
            failure_codes=tuple(dict.fromkeys(failure_codes)),
            expected_discovery_drift=drift,
        )

    def _inspect_universe(self, symbols: tuple[str, ...], session_date: date) -> UniverseScreen:
        universe = self._config["universe"]
        path = Path(universe["physical_path"])
        expected_hash = universe.get("sha256")
        if not path.exists():
            return UniverseScreen(str(universe.get("universe_id", "UNKNOWN")), path, None, expected_hash, symbols, symbols, (), (), ("UNIVERSE_FILE_NOT_FOUND",))
        actual_hash = sha256_file(path)
        failures: list[str] = []
        if expected_hash and actual_hash != expected_hash:
            failures.append("UNIVERSE_HASH_MISMATCH")
        table = pq.read_table(path, columns=["ticker", "first_seen_date", "last_observed_date", "classification_1b"])
        rows = {str(row["ticker"]): row for row in table.to_pylist()}
        missing = []
        outside_pti = []
        disallowed = []
        allowed_classes = set(universe.get("classification_allowed", ("active_lt_1b_last_classifiable", "inactive_died_lt_1b")))
        for symbol in symbols:
            row = rows.get(symbol)
            if row is None:
                missing.append(symbol)
                continue
            first = _to_date(row.get("first_seen_date"))
            last = _to_date(row.get("last_observed_date"))
            if first is None or last is None or not (first <= session_date <= last):
                outside_pti.append(symbol)
            if row.get("classification_1b") not in allowed_classes:
                disallowed.append(symbol)
        if missing:
            failures.append("UNIVERSE_SYMBOL_NOT_FOUND")
        if outside_pti:
            failures.append("UNIVERSE_SYMBOL_OUTSIDE_PTI_WINDOW")
        if disallowed:
            failures.append("UNIVERSE_SYMBOL_CLASSIFICATION_NOT_ALLOWED")
        return UniverseScreen(
            universe_id=str(universe.get("universe_id", "UNKNOWN")),
            physical_path=path,
            sha256=actual_hash,
            expected_sha256=expected_hash,
            symbols_checked=symbols,
            missing_symbols=tuple(missing),
            outside_pti_symbols=tuple(outside_pti),
            disallowed_classification_symbols=tuple(disallowed),
            failure_codes=tuple(dict.fromkeys(failures)),
        )

    def _inspect_corporate_actions(self, symbols: tuple[str, ...], session_date: date) -> CorporateActionScreen:
        config = self._config["corporate_actions"]
        path = Path(config["physical_path"])
        manifest_path = Path(config["manifest_path"]) if config.get("manifest_path") else None
        expected_table_hash = config.get("table_sha256")
        expected_manifest_hash = config.get("manifest_sha256")
        window_start = session_date - timedelta(days=7)
        window_end = session_date + timedelta(days=7)
        failures: list[str] = []
        warnings: list[str] = []
        table_hash = None
        manifest_hash = None
        rows_found = 0
        exact_rows = 0
        action_types: tuple[str, ...] = ()

        if not path.exists():
            failures.append("CORPORATE_ACTION_TABLE_NOT_FOUND")
        else:
            table_hash = sha256_file(path)
            if expected_table_hash and table_hash != expected_table_hash:
                failures.append("CORPORATE_ACTION_TABLE_HASH_MISMATCH")
            table = pq.read_table(path, columns=["ticker", "action_type", "action_date"])
            found_types = []
            for row in table.to_pylist():
                if row.get("ticker") not in symbols:
                    continue
                action_date = _to_date(row.get("action_date"))
                if action_date is None:
                    continue
                if window_start <= action_date <= window_end:
                    rows_found += 1
                    found_types.append(str(row.get("action_type")))
                    if action_date == session_date:
                        exact_rows += 1
            action_types = tuple(sorted(set(found_types)))
            if exact_rows:
                failures.append("CORPORATE_ACTION_EFFECTIVE_ON_SESSION")
            elif rows_found:
                warnings.append("NEARBY_CORPORATE_ACTION_OBSERVED")

        if manifest_path is None or not manifest_path.exists():
            failures.append("CORPORATE_ACTION_MANIFEST_NOT_FOUND")
        else:
            manifest_hash = sha256_file(manifest_path)
            if expected_manifest_hash and manifest_hash != expected_manifest_hash:
                failures.append("CORPORATE_ACTION_MANIFEST_HASH_MISMATCH")

        return CorporateActionScreen(
            dataset_id=str(config.get("dataset_id", "UNKNOWN")),
            physical_path=path,
            table_sha256=table_hash,
            expected_table_sha256=expected_table_hash,
            manifest_path=manifest_path,
            manifest_sha256=manifest_hash,
            expected_manifest_sha256=expected_manifest_hash,
            symbols_consulted=symbols,
            temporal_field="action_date",
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
            session_date=session_date.isoformat(),
            rows_found=rows_found,
            exact_session_rows=exact_rows,
            action_types_found=action_types,
            failure_codes=tuple(dict.fromkeys(failures)),
            warning_codes=tuple(dict.fromkeys(warnings)),
        )

    def _row_core_issues(
        self,
        row: Mapping[str, Any],
        partition_ticker: str,
        session_date: date,
        ts: datetime,
        allowed_row_dataset_ids: tuple[str, ...],
        expected_row_build_run_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        issues: list[str] = []
        if row.get("ticker") != partition_ticker:
            issues.append("ticker_null_or_partition_mismatch")
        if not str(row.get("ts_utc", "")).endswith("Z"):
            issues.append("timestamp_not_declared_utc_z")
        epoch_ms = row.get("t")
        if not isinstance(epoch_ms, int) or epoch_ms != int(ts.timestamp() * 1000):
            issues.append("epoch_ms_mismatch")
        o = row.get("o")
        h = row.get("h")
        l = row.get("l")
        c = row.get("c")
        v = row.get("v")
        if not all(_finite_positive(value) for value in (o, h, l, c)):
            issues.append("ohlc_non_finite_or_non_positive")
        elif h < max(o, l, c):
            issues.append("high_below_open_low_or_close")
        elif l > min(o, h, c):
            issues.append("low_above_open_high_or_close")
        if not _finite_non_negative(v):
            issues.append("volume_non_finite_or_negative")
        if str(row.get("date")) != session_date.isoformat() or row.get("year") != ts.year or row.get("month") != ts.month:
            issues.append("date_year_month_incompatible_with_ts_utc")
        row_dataset_id = row.get("dataset_id")
        if not row_dataset_id or (allowed_row_dataset_ids and row_dataset_id not in allowed_row_dataset_ids):
            issues.append("dataset_id_unexpected")
        build_run_id = row.get("build_run_id")
        if expected_row_build_run_ids and build_run_id not in expected_row_build_run_ids:
            issues.append("build_run_id_unexpected")
        return tuple(issues)

    def _expected_for_ticker(self, ticker: str) -> Mapping[str, Any] | None:
        for row in self._config.get("per_ticker_day", ()): 
            if row.get("ticker") == ticker:
                return row
        return None

    @staticmethod
    def _discovery_drift(
        expected: Mapping[str, Any] | None,
        file_hash: str,
        session_rows: int,
        missing_regular_minutes: int,
        has_open: bool,
        has_close: bool,
    ) -> tuple[str, ...]:
        if expected is None:
            return ()
        drift = []
        if expected.get("sha256") != file_hash:
            drift.append("sha256")
        if expected.get("session_rows") != session_rows:
            drift.append("session_rows")
        if expected.get("missing_regular_minutes") != missing_regular_minutes:
            drift.append("missing_regular_minutes")
        if bool(expected.get("has_open_proxy_1430")) != has_open:
            drift.append("has_open_proxy_1430")
        if bool(expected.get("has_close_proxy_2059")) != has_close:
            drift.append("has_close_proxy_2059")
        return tuple(drift)

    @staticmethod
    def _ticker_failure(
        ticker: str,
        session_date: date,
        path: Path,
        code: str,
        file_sha256: str | None = None,
        optional_columns_present: tuple[str, ...] = (),
        optional_columns_missing: tuple[str, ...] = (),
    ) -> TickerDayInspection:
        return TickerDayInspection(
            ticker=ticker,
            session_date=session_date.isoformat(),
            status=FAIL,
            file=path,
            file_found=code != "FILE_NOT_FOUND",
            file_sha256=file_sha256,
            monthly_rows=0,
            session_rows=0,
            session_min_utc=None,
            session_max_utc=None,
            has_required_open=False,
            has_required_close=False,
            missing_regular_minutes=0,
            observed_minute_gaps=(),
            duplicate_timestamps=0,
            invalid_core_rows=0,
            invalid_core_issue_counts={},
            optional_columns_present=optional_columns_present,
            optional_columns_missing=optional_columns_missing,
            warning_codes=(),
            failure_codes=(code,),
            expected_discovery_drift=(),
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_utc(value: str) -> datetime:
    parsed = _safe_parse_utc(value)
    if parsed is None:
        raise ValueError(f"invalid UTC timestamp: {value}")
    return parsed


def _safe_parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _date_from_iso(value: str) -> date:
    return date.fromisoformat(value)


def _to_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
    return None


def _minute_range(start: datetime, end_exclusive: datetime) -> tuple[datetime, ...]:
    values = []
    current = start
    while current < end_exclusive:
        values.append(current)
        current += timedelta(minutes=1)
    return tuple(values)


def _finite_positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) > 0


def _finite_non_negative(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) >= 0


def _increment(counts: dict[str, int], key: str) -> None:
    counts[key] = counts.get(key, 0) + 1