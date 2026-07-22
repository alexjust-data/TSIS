from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


SCRIPT_VERSION = "experimental_core_four_market_state_scale_a_sample_preflight_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_market_state_scale_a_scope_v0_1.json"
)
RUN_ID_PREFIX = "experimental_core_four_market_state_scale_a_sample_preflight_v0_1"
NY_TZ = ZoneInfo("America/New_York")
EXPECTED_OBJECTS_PER_CONTEXT = 4


class PreflightError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any, ensure_ascii: bool = True) -> str:
    return json.dumps(json_safe_value(value), ensure_ascii=ensure_ascii, sort_keys=True, separators=(",", ":"))


def json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe_value(v) for v in value]
    if isinstance(value, tuple):
        return [json_safe_value(v) for v in value]
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if hasattr(value, "item"):
        try:
            return json_safe_value(value.item())
        except Exception:
            pass
    return value


def serialize_cell(value: Any) -> str:
    safe = json_safe_value(value)
    if safe is None:
        return ""
    if isinstance(safe, (dict, list)):
        return canonical_json(safe, ensure_ascii=False)
    return str(safe)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_safe_value(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row, ensure_ascii=False))
            handle.write("\n")


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: serialize_cell(row.get(field)) for field in fieldnames})


def sha256_payload(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload, ensure_ascii=True).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def is_within_or_equal(candidate: Path, allowed: Path) -> bool:
    candidate = candidate.resolve()
    allowed = allowed.resolve()
    if candidate == allowed:
        return True
    try:
        candidate.relative_to(allowed)
        return True
    except ValueError:
        return False


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(args, cwd=str(cwd), text=True, capture_output=True, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def parse_session_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raw = str(value).strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        parsed = pd.to_datetime(raw, utc=True, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()


def parse_utc_timestamp(value: Any) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def clock_text(value: datetime | pd.Timestamp | None) -> str:
    if value is None:
        return ""
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    return value.time().replace(microsecond=0).isoformat()


def session_time_utc(session_date: date, time_text: str) -> datetime:
    parts = [int(part) for part in str(time_text).split(":")]
    while len(parts) < 3:
        parts.append(0)
    return datetime.combine(session_date, time(parts[0], parts[1], parts[2]), tzinfo=timezone.utc)


def ny_regular_session_utc(session_date: date) -> tuple[datetime, datetime]:
    local_open = datetime.combine(session_date, time(9, 30), tzinfo=NY_TZ)
    local_close = datetime.combine(session_date, time(16, 0), tzinfo=NY_TZ)
    return local_open.astimezone(timezone.utc), local_close.astimezone(timezone.utc)


def validate_authority(scope: dict[str, Any]) -> None:
    scope_id = scope.get("scope_id")
    allowed_scope_ids = {
        "experimental_core_four_market_state_scale_a_scope_v0_1",
        "experimental_core_four_market_state_scale_a_sample_preflight_rerun_scope_v0_1",
    }
    if scope_id not in allowed_scope_ids:
        raise PreflightError(f"Unexpected Scale A scope_id: {scope_id}")
    allowed_scope_statuses = {
        "authorized_bounded_non_production_scale_a",
        "authorized_with_restrictions",
        "authorized_with_restrictions_preflight_rerun",
    }
    if scope.get("scope_status") not in allowed_scope_statuses:
        raise PreflightError(f"Scale A scope status is not authorized: {scope.get('scope_status')}")
    authority = scope.get("authority", {})
    required_false = [
        "official_market_state_allowed",
        "official_state_table_write_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "quote_dependent_object_integration_allowed",
        "scale_b_calendar_aware_execution_allowed",
        "scale_c_historical_bounded_execution_allowed",
    ]
    offenders = [key for key in required_false if authority.get(key) is not False]
    if offenders:
        raise PreflightError(f"Forbidden authority flags are not false: {offenders}")
    allowed_aliases = set(scope.get("source_aliases_allowed", []))
    if allowed_aliases != {"004_master_daily_table", "014_master_intraday_bar_table_candidate"}:
        raise PreflightError(f"Unexpected source aliases allowed: {sorted(allowed_aliases)}")
    forbidden = {str(item).replace("\\", "/") for item in scope.get("source_aliases_forbidden", [])}
    if "00_CTO/99_REFERENCE_LIBRARY" not in forbidden:
        raise PreflightError("Reference library exclusion is missing from Scale A scope")
    limits = scope.get("limits", {})
    target_contexts = int(limits.get("target_requested_contexts", -1))
    if target_contexts * EXPECTED_OBJECTS_PER_CONTEXT != int(limits.get("target_resolution_records", -1)):
        raise PreflightError("target_resolution_records does not equal target_requested_contexts * 4")
    if int(limits.get("target_expected_blocked_contexts", -1)) + int(
        limits.get("target_integrated_candidate_records", -1)
    ) != target_contexts:
        raise PreflightError("blocked + integrated target contexts does not equal target_requested_contexts")
    if scope_id == "experimental_core_four_market_state_scale_a_sample_preflight_rerun_scope_v0_1":
        if authority.get("scale_a_sample_preflight_rerun_allowed") is not True:
            raise PreflightError("Preflight rerun scope must explicitly allow scale_a_sample_preflight_rerun_allowed")
        preflight_false = [
            "builder_execution_allowed_for_scale_a",
            "integration_execution_allowed_for_scale_a",
            "candidate_materialization_allowed_for_scale_a",
            "candidate_parquet_output_allowed_for_scale_a",
        ]
        rerun_offenders = [key for key in preflight_false if authority.get(key) is not False]
        if rerun_offenders:
            raise PreflightError(f"Preflight rerun scope has execution authority flags not false: {rerun_offenders}")


def load_source_roots(scope: dict[str, Any], scope_dir: Path) -> tuple[Path, Path, Path, dict[str, Any]]:
    registry_path = resolve_path(scope["governance_inputs"]["source_binding_registry"], scope_dir)
    registry = read_json(registry_path)
    bindings = registry.get("bindings", {})
    roots: dict[str, Path] = {}
    source_overrides = scope.get("source_overrides", {})
    for alias in ("004_master_daily_table", "014_master_intraday_bar_table_candidate"):
        override = source_overrides.get(alias, {})
        if alias == "014_master_intraday_bar_table_candidate" and override.get("parquet_path"):
            root = resolve_path(str(override["parquet_path"]), scope_dir)
        else:
            binding = bindings.get(alias)
            if not binding:
                raise PreflightError(f"Missing source binding for {alias}")
            root = Path(str(binding.get("physical_candidate_root"))).resolve()
        root_text = str(root).replace("\\", "/")
        if "00_CTO/99_REFERENCE_LIBRARY" in root_text:
            raise PreflightError(f"Forbidden reference library path resolved for {alias}: {root}")
        if not root.exists():
            raise PreflightError(f"Physical source path does not exist for {alias}: {root}")
        roots[alias] = root
    return registry_path, roots["004_master_daily_table"], roots["014_master_intraday_bar_table_candidate"], registry


def read_intraday_source(root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    data_path = root if root.is_file() else root / "data.parquet"
    if not data_path.exists():
        raise PreflightError(f"014 data.parquet not found: {data_path}")
    columns = [
        "ticker",
        "instrument_id",
        "session_date",
        "ts_utc",
        "price_view",
        "bar_size",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    optional_columns = ["duplicate_status"]
    pf = pq.ParquetFile(str(data_path))
    available = set(pf.schema_arrow.names)
    missing = [column for column in columns if column not in available]
    if missing:
        raise PreflightError(f"014 missing required preflight columns: {missing}")
    read_columns = columns + [column for column in optional_columns if column in available]
    df = pd.read_parquet(data_path, columns=read_columns)
    df = df.reset_index(drop=True)
    if "duplicate_status" not in df.columns:
        df["duplicate_status"] = "unique"
    else:
        df["duplicate_status"] = df["duplicate_status"].fillna("unique").astype(str)
    df["source_row_ordinal_in_file"] = df.index
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_obj"] = df["session_date"].map(parse_session_date)
    df["session_date_iso"] = df["session_date_obj"].map(lambda value: value.isoformat() if value else None)
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    report = {
        "source_alias": "014_master_intraday_bar_table_candidate",
        "file_path": str(data_path),
        "physical_candidate_root": str(root if root.is_dir() else root.parent),
        "rows_read": int(len(df)),
        "columns_read": read_columns,
        "duplicate_status_counts": {str(k): int(v) for k, v in df["duplicate_status"].value_counts(dropna=False).items()},
        "invalid_timestamp_rows": int(df["ts"].isna().sum()),
        "invalid_session_date_rows": int(df["session_date_obj"].isna().sum()),
        "unique_tickers": int(df["ticker"].nunique(dropna=True)),
        "unique_sessions": int(df["session_date_iso"].nunique(dropna=True)),
        "price_view_counts": {str(k): int(v) for k, v in df["price_view"].value_counts(dropna=False).items()},
        "bar_size_counts": {str(k): int(v) for k, v in df["bar_size"].value_counts(dropna=False).items()},
        "sha256": sha256_file(data_path),
    }
    return df, report


def load_authorized_eligible_pool(scope: dict[str, Any], scope_dir: Path) -> tuple[list[str], dict[str, Any]]:
    pool_cfg = (
        scope.get("input_artifacts", {})
        .get("accepted_eligible_surface", {})
        .get("eligible_instrument_pool", {})
    )
    if not pool_cfg:
        return [], {"pool_required": False}
    pool_path = resolve_path(str(pool_cfg["path"]), scope_dir)
    pool = read_json(pool_path)
    if pool.get("accepted_pool") is not True:
        raise PreflightError(f"Eligible instrument pool is not accepted: {pool_path}")
    expected_fingerprint = pool_cfg.get("expected_fingerprint")
    observed_fingerprint = pool.get("eligible_instrument_pool_fingerprint")
    if expected_fingerprint and observed_fingerprint != expected_fingerprint:
        raise PreflightError(
            "Eligible instrument pool fingerprint mismatch: "
            f"expected {expected_fingerprint}, observed {observed_fingerprint}"
        )
    instruments = pool.get("instruments", [])
    tickers = [str(item.get("ticker", "")).strip().upper() for item in instruments if item.get("ticker")]
    tickers = [ticker for ticker in tickers if ticker]
    if len(tickers) != len(set(tickers)):
        raise PreflightError("Eligible instrument pool contains duplicate tickers")
    minimum_pool_size = int(pool_cfg.get("minimum_eligible_instruments", 0))
    if len(tickers) < minimum_pool_size:
        raise PreflightError(f"Eligible instrument pool below required minimum: {len(tickers)} < {minimum_pool_size}")
    return tickers, {
        "pool_required": True,
        "pool_path": str(pool_path),
        "accepted_pool": True,
        "eligible_surface_run_id": pool.get("run_id"),
        "eligible_surface_fingerprint": pool.get("eligible_surface_fingerprint"),
        "eligible_instrument_pool_fingerprint": observed_fingerprint,
        "eligible_instruments_in_pool": len(tickers),
        "eligible_pool_tickers": tickers,
    }


def validate_rerun_input_artifacts(scope: dict[str, Any], scope_dir: Path, intraday_report: dict[str, Any]) -> dict[str, Any]:
    surface_cfg = (
        scope.get("input_artifacts", {})
        .get("accepted_eligible_surface", {})
        .get("bounded_014_candidate_surface", {})
    )
    if not surface_cfg:
        return {"bounded_surface_required": False}
    surface_path = resolve_path(str(surface_cfg["path"]), scope_dir)
    expected_sha = surface_cfg.get("expected_parquet_sha256")
    observed_sha = intraday_report.get("sha256")
    if expected_sha and observed_sha != expected_sha:
        raise PreflightError(
            "Bounded 014 candidate surface SHA-256 mismatch: "
            f"expected {expected_sha}, observed {observed_sha}"
        )
    return {
        "bounded_surface_required": True,
        "bounded_surface_path": str(surface_path),
        "expected_parquet_sha256": expected_sha,
        "observed_parquet_sha256": observed_sha,
        "expected_surface_fingerprint": surface_cfg.get("expected_surface_fingerprint"),
    }


def read_daily_source(root: Path, tickers: list[str], years: list[int]) -> tuple[pd.DataFrame, dict[str, Any]]:
    columns = [
        "instrument_id",
        "ticker",
        "session_date",
        "open",
        "prior_close",
        "volume",
        "year",
        "price_view",
    ]
    if not tickers or not years:
        empty = pd.DataFrame(columns=columns)
        return empty, {
            "source_alias": "004_master_daily_table",
            "physical_candidate_root": str(root),
            "rows_read": 0,
            "columns_read": columns,
            "years_filter": years,
            "ticker_filter": tickers,
            "selected_price_view": "split_normalized",
        }
    dataset = ds.dataset(str(root), format="parquet", partitioning="hive")
    available = set(dataset.schema.names)
    missing = [column for column in columns if column not in available]
    if missing:
        raise PreflightError(f"004 missing required preflight columns: {missing}")
    filt = (
        ds.field("year").isin([int(year) for year in years])
        & (ds.field("price_view") == "split_normalized")
        & ds.field("ticker").isin([str(ticker) for ticker in tickers])
    )
    table = dataset.to_table(columns=columns, filter=filt)
    df = table.to_pandas()
    df = df.reset_index(drop=True)
    df["source_row_ordinal_in_returned_filter"] = df.index
    if not df.empty:
        df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_obj"] = df["session_date"].map(parse_session_date) if "session_date" in df else None
    df["session_date_iso"] = df["session_date_obj"].map(lambda value: value.isoformat() if value else None)
    report = {
        "source_alias": "004_master_daily_table",
        "physical_candidate_root": str(root),
        "rows_read": int(len(df)),
        "columns_read": columns,
        "years_filter": years,
        "ticker_filter": tickers,
        "selected_price_view": "split_normalized",
        "unique_tickers": int(df["ticker"].nunique(dropna=True)) if not df.empty else 0,
        "unique_sessions": int(df["session_date_iso"].nunique(dropna=True)) if not df.empty else 0,
    }
    return df, report


def state_signature(row: pd.Series) -> str:
    return canonical_json(
        {
            "open": json_safe_value(row.get("open")),
            "high": json_safe_value(row.get("high")),
            "low": json_safe_value(row.get("low")),
            "close": json_safe_value(row.get("close")),
            "volume": json_safe_value(row.get("volume")),
        },
        ensure_ascii=True,
    )


def build_intraday_summaries(intraday: pd.DataFrame, expected_open: str, expected_close: str) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str, str], dict[str, Any]],
]:
    valid = intraday.dropna(subset=["ticker", "session_date_iso", "ts"]).copy()
    duplicate_map: dict[tuple[str, str, str], dict[str, Any]] = {}
    for (ticker, session_date_iso, ts), group in valid.groupby(["ticker", "session_date_iso", "ts"], sort=True):
        signatures = {state_signature(row) for _, row in group.iterrows()}
        preserved_statuses = sorted(
            {
                str(value)
                for value in group.get("duplicate_status", pd.Series(dtype=str)).fillna("unique")
                if str(value) not in {"", "unique", "nan", "None"}
            }
        )
        if len(group) > 1 and len(signatures) > 1:
            status = "conflicting_duplicate_rows"
        elif len(group) > 1:
            status = "identical_duplicate_rows"
        elif preserved_statuses:
            status = preserved_statuses[0]
        else:
            status = "unique"
        duplicate_map[(str(ticker), str(session_date_iso), pd.Timestamp(ts).isoformat().replace("+00:00", "Z"))] = {
            "duplicate_status": status,
            "duplicate_group_row_count": int(len(group)),
            "duplicate_group_distinct_state_count": int(len(signatures)),
            "source_duplicate_evidence": bool(status != "unique"),
        }
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for (ticker, session_date_iso), group in valid.groupby(["ticker", "session_date_iso"], sort=True):
        session_obj = parse_session_date(session_date_iso)
        if session_obj is None:
            continue
        open_dt = pd.Timestamp(session_time_utc(session_obj, expected_open))
        close_dt = pd.Timestamp(session_time_utc(session_obj, expected_close))
        unique_times = sorted(pd.Timestamp(ts) for ts in group["ts"].dropna().unique())
        regular_times = [ts for ts in unique_times if open_dt <= ts <= close_dt]
        all_duplicate_groups = [
            duplicate_map[(str(ticker), str(session_date_iso), ts.isoformat().replace("+00:00", "Z"))]
            for ts in unique_times
        ]
        regular_duplicate_groups = [
            duplicate_map[(str(ticker), str(session_date_iso), ts.isoformat().replace("+00:00", "Z"))]
            for ts in regular_times
        ]
        summaries[(str(ticker), str(session_date_iso))] = {
            "ticker": str(ticker),
            "session_date": str(session_date_iso),
            "rows": int(len(group)),
            "unique_bar_timestamps": int(len(unique_times)),
            "first_ts_utc": unique_times[0] if unique_times else None,
            "last_ts_utc": unique_times[-1] if unique_times else None,
            "regular_unique_bar_timestamps": int(len(regular_times)),
            "first_regular_ts_utc": regular_times[0] if regular_times else None,
            "last_regular_ts_utc": regular_times[-1] if regular_times else None,
            "duplicate_group_count": int(sum(1 for item in all_duplicate_groups if item["duplicate_group_row_count"] > 1)),
            "regular_duplicate_group_count": int(
                sum(1 for item in regular_duplicate_groups if item["duplicate_group_row_count"] > 1)
            ),
            "source_duplicate_evidence_count": int(
                sum(1 for item in all_duplicate_groups if item.get("source_duplicate_evidence") is True)
            ),
            "regular_source_duplicate_evidence_count": int(
                sum(1 for item in regular_duplicate_groups if item.get("source_duplicate_evidence") is True)
            ),
            "conflicting_duplicate_group_count": int(
                sum(1 for item in all_duplicate_groups if item["duplicate_status"] == "conflicting_duplicate_rows")
            ),
        }
    return summaries, duplicate_map


def build_daily_maps(daily: pd.DataFrame) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    daily_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    daily_by_ticker: dict[str, list[dict[str, Any]]] = {}
    if daily.empty:
        return daily_by_key, daily_by_ticker
    for _, row in daily.dropna(subset=["ticker", "session_date_iso"]).iterrows():
        ticker = str(row["ticker"]).strip().upper()
        session_date_iso = str(row["session_date_iso"])
        doc = {
            "ticker": ticker,
            "session_date": session_date_iso,
            "instrument_id": json_safe_value(row.get("instrument_id")),
            "open_present": row.get("open") is not None and not pd.isna(row.get("open")),
            "prior_close_present": row.get("prior_close") is not None and not pd.isna(row.get("prior_close")),
            "volume_present": row.get("volume") is not None and not pd.isna(row.get("volume")),
        }
        key = (ticker, session_date_iso)
        if key not in daily_by_key:
            daily_by_key[key] = doc
        daily_by_ticker.setdefault(ticker, []).append(doc)
    for ticker, rows in daily_by_ticker.items():
        daily_by_ticker[ticker] = sorted(rows, key=lambda row: row["session_date"])
    return daily_by_key, daily_by_ticker


def prior_daily_volume_count(daily_by_ticker: dict[str, list[dict[str, Any]]], ticker: str, session_date_iso: str) -> int:
    rows = [
        row
        for row in daily_by_ticker.get(ticker, [])
        if row["session_date"] < session_date_iso and row.get("volume_present") is True
    ]
    return len(rows[-20:])


def build_calendar_report(
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
    scope: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    required = scope["calendar_policy"]["required_selected_session_properties"]
    expected_open = str(required["regular_open_utc"])
    expected_close = str(required["regular_close_utc"])
    session_dates = sorted({session_date for _, session_date in intraday_summaries})
    candidate_rows: list[dict[str, Any]] = []
    for session_date_iso in session_dates:
        session_obj = parse_session_date(session_date_iso)
        if session_obj is None:
            continue
        expected_open_dt = session_time_utc(session_obj, expected_open)
        expected_close_dt = session_time_utc(session_obj, expected_close)
        observed_open_dt, observed_close_dt = ny_regular_session_utc(session_obj)
        weekday_closed = session_obj.weekday() >= 5
        holiday_or_closed = bool(weekday_closed)
        early_close = False
        session_type = "closed_or_weekend" if holiday_or_closed else "regular"
        calendar_time_compatible = (
            clock_text(observed_open_dt) == expected_open
            and clock_text(observed_close_dt) == expected_close
            and session_type == "regular"
            and early_close is False
            and holiday_or_closed is False
        )
        regular_rows = [
            summary
            for (ticker, date_key), summary in intraday_summaries.items()
            if date_key == session_date_iso and int(summary["regular_unique_bar_timestamps"]) > 0
        ]
        compatible = bool(calendar_time_compatible and regular_rows)
        candidate_rows.append(
            {
                "session_date": session_date_iso,
                "expected_open_utc": expected_open,
                "observed_open_utc": clock_text(observed_open_dt),
                "expected_close_utc": expected_close,
                "observed_close_utc": clock_text(observed_close_dt),
                "session_type": session_type,
                "early_close": early_close,
                "holiday_or_closed": holiday_or_closed,
                "compatible": compatible,
                "evidence_source": "America/New_York regular session conversion plus 014 regular-window row presence; not a governed exchange calendar",
                "regular_window_ticker_count": len(regular_rows),
                "regular_window_min_first_ts_utc": min(
                    (row["first_regular_ts_utc"] for row in regular_rows if row["first_regular_ts_utc"] is not None),
                    default=None,
                ),
                "regular_window_max_last_ts_utc": max(
                    (row["last_regular_ts_utc"] for row in regular_rows if row["last_regular_ts_utc"] is not None),
                    default=None,
                ),
                "finding": "compatible with fixed UTC Scale A guard"
                if compatible
                else "not compatible with fixed UTC Scale A guard or no regular-window 014 rows",
            }
        )
    compatible_sessions = [row["session_date"] for row in candidate_rows if row["compatible"] is True]
    selected_sessions = compatible_sessions[: int(scope["limits"]["session_count"])]
    selected_rows = [row for row in candidate_rows if row["session_date"] in set(selected_sessions)]
    if len(selected_rows) < int(scope["limits"]["session_count"]):
        selected_rows = candidate_rows[: int(scope["limits"]["session_count"])]
    return selected_rows, selected_sessions


def build_identity_and_coverage_reports(
    *,
    intraday: pd.DataFrame,
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
    daily_by_key: dict[tuple[str, str], dict[str, Any]],
    daily_by_ticker: dict[str, list[dict[str, Any]]],
    selected_sessions: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    tickers = sorted(str(ticker) for ticker in intraday["ticker"].dropna().unique())
    identity_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    eligible_tickers: list[str] = []
    for ticker in tickers:
        daily_ids = sorted(
            {
                str(row.get("instrument_id"))
                for row in daily_by_ticker.get(ticker, [])
                if row.get("instrument_id") not in {None, ""}
            }
        )
        calendar_compatible_session_count = sum(1 for session_date in selected_sessions if (ticker, session_date) in intraday_summaries)
        eligible_session_count = 0
        for session_date in selected_sessions:
            daily_row = daily_by_key.get((ticker, session_date))
            intraday_summary = intraday_summaries.get((ticker, session_date))
            prior_count = prior_daily_volume_count(daily_by_ticker, ticker, session_date)
            daily_required_present = bool(
                daily_row
                and daily_row.get("instrument_id")
                and daily_row.get("open_present")
                and daily_row.get("prior_close_present")
                and daily_row.get("volume_present")
            )
            intraday_required_present = bool(intraday_summary and intraday_summary["regular_unique_bar_timestamps"] > 0)
            coverage_pass = bool(daily_required_present and prior_count >= 20 and intraday_required_present)
            if coverage_pass:
                eligible_session_count += 1
            coverage_rows.append(
                {
                    "ticker": ticker,
                    "session_date": session_date,
                    "daily_row_present": bool(daily_row),
                    "daily_instrument_id_present": bool(daily_row and daily_row.get("instrument_id")),
                    "daily_open_present": bool(daily_row and daily_row.get("open_present")),
                    "daily_prior_close_present": bool(daily_row and daily_row.get("prior_close_present")),
                    "daily_volume_present": bool(daily_row and daily_row.get("volume_present")),
                    "prior_20_daily_volume_rows": prior_count,
                    "intraday_session_present": bool(intraday_summary),
                    "intraday_regular_unique_bar_timestamps": int(intraday_summary["regular_unique_bar_timestamps"])
                    if intraday_summary
                    else 0,
                    "intraday_regular_duplicate_groups": int(intraday_summary["regular_duplicate_group_count"])
                    if intraday_summary
                    else 0,
                    "source_coverage_status": "PASS" if coverage_pass else "BLOCKED_SOURCE_COVERAGE",
                    "finding": "required daily, prior-history and intraday regular-window coverage present"
                    if coverage_pass
                    else "missing required daily, prior-history or intraday regular-window coverage",
                }
            )
        identity_resolved = len(daily_ids) == 1
        if identity_resolved and eligible_session_count > 0:
            eligible_tickers.append(ticker)
        identity_rows.append(
            {
                "ticker": ticker,
                "daily_instrument_id": daily_ids[0] if len(daily_ids) == 1 else "",
                "daily_identity_resolved": identity_resolved,
                "daily_identity_ambiguous": len(daily_ids) > 1,
                "daily_identity_count": len(daily_ids),
                "intraday_instrument_id_present": bool(intraday.loc[intraday["ticker"] == ticker, "instrument_id"].notna().any()),
                "intraday_rows": int((intraday["ticker"] == ticker).sum()),
                "calendar_compatible_session_count": calendar_compatible_session_count,
                "coverage_eligible_session_count": eligible_session_count,
                "instrument_selection_status": "ELIGIBLE_FOR_SCALE_A"
                if identity_resolved and eligible_session_count > 0
                else "NOT_ELIGIBLE_FOR_SCALE_A_SAMPLE",
                "finding": "identity resolved from 004 and at least one selected compatible session has coverage"
                if identity_resolved and eligible_session_count > 0
                else "instrument lacks resolved 004 identity or selected compatible session coverage",
            }
        )
    return identity_rows, coverage_rows, sorted(eligible_tickers)


def context_timestamp_for_family(
    *,
    family: str,
    ticker: str,
    session_date: str,
    intraday_summary: dict[str, Any],
) -> tuple[str, datetime]:
    first_all = pd.Timestamp(intraday_summary["first_ts_utc"]).to_pydatetime()
    first_regular = pd.Timestamp(intraday_summary["first_regular_ts_utc"]).to_pydatetime()
    last_regular = pd.Timestamp(intraday_summary["last_regular_ts_utc"]).to_pydatetime()
    if family == "pre_first_observable_bar_expected_blocked":
        return "before_first_observable_bar", first_all - timedelta(seconds=1)
    if family == "first_closed_bar_or_early_regular_intraday":
        return "first_regular_intraday_bar", first_regular
    if family == "mid_session_regular_intraday":
        open_dt = session_time_utc(parse_session_date(session_date) or first_regular.date(), "13:30:00")
        close_dt = session_time_utc(parse_session_date(session_date) or first_regular.date(), "20:00:00")
        midpoint = open_dt + (close_dt - open_dt) / 2
        return "mid_session_regular_intraday", midpoint
    if family == "after_last_sampled_bar_not_session_close":
        return "after_last_sampled_bar_not_session_close", last_regular + timedelta(seconds=1)
    raise PreflightError(f"Unsupported decision_case_family: {family}")


def build_sample_manifest(
    *,
    scope: dict[str, Any],
    eligible_tickers: list[str],
    selected_sessions: list[str],
    identity_rows: list[dict[str, Any]],
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    limits = scope["limits"]
    target_contexts = int(limits["target_requested_contexts"])
    target_instruments = int(limits["instrument_count"])
    target_sessions = int(limits["session_count"])
    if len(eligible_tickers) < target_instruments or len(selected_sessions) < target_sessions:
        return []
    selected_sessions = selected_sessions[:target_sessions]
    selected_tickers = eligible_tickers[:target_instruments]
    duplicate_min = int(
        scope.get("sample_plan", {})
        .get("duplicate_status_targets", {})
        .get("contexts_with_known_duplicate_physical_group_evidence_minimum", 0)
    )
    duplicate_evidence_tickers = [
        ticker
        for ticker in eligible_tickers
        if any(
            (ticker, session_date) in intraday_summaries
            and int(intraday_summaries[(ticker, session_date)].get("regular_source_duplicate_evidence_count", 0)) > 0
            for session_date in selected_sessions
        )
    ]
    if duplicate_min > 0 and duplicate_evidence_tickers:
        selected_set = set(selected_tickers)
        if not any(ticker in selected_set for ticker in duplicate_evidence_tickers):
            selected_tickers = selected_tickers[:-1] + [duplicate_evidence_tickers[0]]
    instrument_id_by_ticker = {
        str(row["ticker"]): str(row["daily_instrument_id"])
        for row in identity_rows
        if row.get("daily_identity_resolved") is True and row.get("daily_instrument_id")
    }
    eligible_pairs = [
        (ticker, session_date)
        for ticker in selected_tickers
        for session_date in selected_sessions
        if (ticker, session_date) in intraday_summaries
        and int(intraday_summaries[(ticker, session_date)]["regular_unique_bar_timestamps"]) > 0
    ]
    if not eligible_pairs:
        return []
    rows: list[dict[str, Any]] = []
    context_index = 0
    pair_index = 0
    required_props = scope["calendar_policy"]["required_selected_session_properties"]
    for family_doc in scope["sample_plan"]["decision_case_families"]:
        family = str(family_doc["decision_case_family"])
        target = int(family_doc["target_contexts"])
        for _ in range(target):
            attempts = 0
            selected_pair: tuple[str, str] | None = None
            while attempts < len(eligible_pairs):
                pair = eligible_pairs[pair_index % len(eligible_pairs)]
                pair_index += 1
                attempts += 1
                if pair in intraday_summaries:
                    selected_pair = pair
                    break
            if selected_pair is None:
                return []
            ticker, session_date = selected_pair
            intraday_summary = intraday_summaries[selected_pair]
            decision_case, decision_timestamp = context_timestamp_for_family(
                family=family,
                ticker=ticker,
                session_date=session_date,
                intraday_summary=intraday_summary,
            )
            context_index += 1
            expected_outcome = str(family_doc["expected_integration_status"])
            rows.append(
                {
                    "sample_context_id": f"scale_a_context_{context_index:04d}",
                    "instrument_id": instrument_id_by_ticker.get(ticker, ""),
                    "ticker": ticker,
                    "session_date": session_date,
                    "decision_timestamp_utc": decision_timestamp.astimezone(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "decision_case": decision_case,
                    "decision_case_family": family,
                    "exchange": "XNYS_or_XNAS_regular_equity_proxy_not_governed_calendar",
                    "regular_open_utc": required_props["regular_open_utc"],
                    "regular_close_utc": required_props["regular_close_utc"],
                    "session_type": required_props["session_type"],
                    "early_close": required_props["early_close_indicator"],
                    "holiday_or_closed": required_props["holiday_or_closed_indicator"],
                    "calendar_compatibility_status": "PASS_WITH_RESTRICTIONS",
                    "selection_stratum": family,
                    "selection_reason": "deterministic Scale A stratified preflight selection from compatible 004/014 coverage",
                    "expected_context_outcome": expected_outcome,
                    "expected_materialized_as_row": bool(family_doc["materialized_as_rows"]),
                    "source_coverage_status": "PASS",
                    "known_duplicate_physical_group_evidence": bool(
                        int(intraday_summary.get("regular_source_duplicate_evidence_count", 0)) > 0
                    ),
                    "duplicate_evidence_status": "PRESERVED_SOURCE_DUPLICATE_EVIDENCE"
                    if int(intraday_summary.get("regular_source_duplicate_evidence_count", 0)) > 0
                    else "NO_DUPLICATE_EVIDENCE",
                    "after_last_sampled_bar_semantics": "not_session_close"
                    if family == "after_last_sampled_bar_not_session_close"
                    else "",
                }
            )
            if len(rows) >= target_contexts:
                return rows
    return rows


def build_stratification_report(
    *,
    scope: dict[str, Any],
    sample_rows: list[dict[str, Any]],
    eligible_tickers: list[str],
    selected_sessions: list[str],
    intraday_summaries: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    frozen_tickers = sorted({row["ticker"] for row in sample_rows})
    frozen_sessions = sorted({row["session_date"] for row in sample_rows})
    rows.append(
        {
            "stratum": "instrument_diversity",
            "required_count": int(scope["limits"]["instrument_count"]),
            "available_count": len(eligible_tickers),
            "frozen_sample_count": len(frozen_tickers),
            "status": "PASS" if len(frozen_tickers) >= int(scope["limits"]["instrument_count"]) else "BLOCKED_SAMPLE_CARDINALITY",
            "finding": "all required instruments represented"
            if len(frozen_tickers) >= int(scope["limits"]["instrument_count"])
            else "not enough eligible instruments to freeze Scale A sample",
        }
    )
    required_sessions = int(scope["limits"]["session_count"])
    session_status = "PASS" if len(frozen_sessions) >= required_sessions else "BLOCKED_SAMPLE_CARDINALITY"
    if len(frozen_sessions) >= required_sessions:
        session_finding = "all required sessions represented"
    elif len(selected_sessions) >= required_sessions:
        session_finding = "compatible sessions are available, but sample was not frozen because another cardinality constraint blocked preflight"
    else:
        session_finding = "not enough compatible sessions to freeze Scale A sample"
    rows.append(
        {
            "stratum": "session_diversity",
            "required_count": required_sessions,
            "available_count": len(selected_sessions),
            "frozen_sample_count": len(frozen_sessions),
            "status": session_status,
            "finding": session_finding,
        }
    )
    family_counts = Counter(row.get("decision_case_family") for row in sample_rows)
    for family_doc in scope["sample_plan"]["decision_case_families"]:
        family = str(family_doc["decision_case_family"])
        target = int(family_doc["target_contexts"])
        count = int(family_counts.get(family, 0))
        rows.append(
            {
                "stratum": family,
                "required_count": target,
                "available_count": "",
                "frozen_sample_count": count,
                "status": "PASS" if count == target else "BLOCKED_SAMPLE_CARDINALITY",
                "finding": "target decision-case family count represented"
                if count == target
                else "decision-case family target not frozen",
            }
        )
    duplicate_group_available = sum(
        1
        for summary in intraday_summaries.values()
        if int(summary.get("regular_duplicate_group_count", 0)) > 0
        or int(summary.get("regular_source_duplicate_evidence_count", 0)) > 0
    )
    duplicate_min = int(
        scope["sample_plan"]["duplicate_status_targets"][
            "contexts_with_known_duplicate_physical_group_evidence_minimum"
        ]
    )
    frozen_duplicate_contexts = sum(
        1 for row in sample_rows if row.get("known_duplicate_physical_group_evidence") is True
    )
    rows.append(
        {
            "stratum": "duplicate_status_diversity",
            "required_count": duplicate_min,
            "available_count": duplicate_group_available,
            "frozen_sample_count": frozen_duplicate_contexts,
            "status": "PASS"
            if sample_rows and duplicate_group_available >= duplicate_min and frozen_duplicate_contexts >= duplicate_min
            else "BLOCKED_SAMPLE_CARDINALITY",
            "finding": "duplicate physical-group evidence represented in frozen contexts"
            if duplicate_group_available >= duplicate_min and frozen_duplicate_contexts >= duplicate_min
            else "not enough duplicate physical group evidence represented in frozen contexts",
        }
    )
    return rows


def build_duplicate_context_report(sample_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int, int]:
    context_counts = Counter(row["sample_context_id"] for row in sample_rows)
    semantic_counts = Counter(
        (
            row["instrument_id"],
            row["ticker"],
            row["session_date"],
            row["decision_timestamp_utc"],
            row["decision_case"],
        )
        for row in sample_rows
    )
    duplicate_context_ids = sum(count - 1 for count in context_counts.values() if count > 1)
    duplicate_semantic_contexts = sum(count - 1 for count in semantic_counts.values() if count > 1)
    rows: list[dict[str, Any]] = []
    if not sample_rows:
        rows.append(
            {
                "check_name": "scale_a_sample_duplicate_contexts",
                "sample_context_id": "",
                "semantic_context_key": "",
                "duplicate_count": 0,
                "status": "NOT_APPLICABLE_SAMPLE_NOT_FROZEN",
                "finding": "no frozen sample rows were emitted because preflight blocked before sample freeze",
            }
        )
        return rows, duplicate_context_ids, duplicate_semantic_contexts
    for key, count in sorted(context_counts.items()):
        if count > 1:
            rows.append(
                {
                    "check_name": "sample_context_id",
                    "sample_context_id": key,
                    "semantic_context_key": "",
                    "duplicate_count": count - 1,
                    "status": "FAILED_DUPLICATE_CONTEXT_ID",
                    "finding": "duplicate sample_context_id detected",
                }
            )
    for key, count in sorted(semantic_counts.items()):
        if count > 1:
            rows.append(
                {
                    "check_name": "semantic_context",
                    "sample_context_id": "",
                    "semantic_context_key": canonical_json(key, ensure_ascii=False),
                    "duplicate_count": count - 1,
                    "status": "FAILED_DUPLICATE_SEMANTIC_CONTEXT",
                    "finding": "duplicate semantic context detected",
                }
            )
    if not rows:
        rows.append(
            {
                "check_name": "scale_a_sample_duplicate_contexts",
                "sample_context_id": "",
                "semantic_context_key": "",
                "duplicate_count": 0,
                "status": "PASS",
                "finding": "no duplicate context ids or duplicate semantic contexts detected",
            }
        )
    return rows, duplicate_context_ids, duplicate_semantic_contexts


def decide_status(summary: dict[str, Any]) -> str:
    if summary["contract_failures"] > 0:
        return "FAILED_CONTRACT"
    if summary["calendar_compatibility_failures"] > 0 or summary["calendar_sessions_checked"] < summary["required_sessions"]:
        return "BLOCKED_CALENDAR_COMPATIBILITY"
    if summary["identity_failures"] > 0:
        return "BLOCKED_IDENTITY"
    if summary["eligible_instruments"] < summary["required_instruments"]:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["selected_sessions"] < summary["required_sessions"]:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["sample_manifest_rows"] != summary["requested_contexts"]:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["source_coverage_failures_in_frozen_sample"] > 0:
        return "BLOCKED_SOURCE_COVERAGE"
    if summary["duplicate_context_ids"] > 0 or summary["duplicate_semantic_contexts"] > 0:
        return "FAILED_CONTRACT"
    if summary.get("stratification_failures", 0) > 0:
        return "BLOCKED_SAMPLE_CARDINALITY"
    if summary["estimated_total_source_rows"] > summary["maximum_source_market_data_rows_read"]:
        return "BLOCKED_SOURCE_COVERAGE"
    return "PASS_WITH_RESTRICTIONS"


def write_readout(path: Path, *, run_id: str, summary: dict[str, Any], run_dir: Path) -> None:
    status = summary["preflight_status"]
    lines = [
        "# Experimental Core Four Market State Scale A Sample Preflight Readout v0.1",
        "",
        f"run_id = `{run_id}`",
        f"script_version = `{SCRIPT_VERSION}`",
        "",
        "## Decision",
        "",
        "```text",
        f"experimental_core_four_market_state_scale_a_sample_preflight = {status}",
        f"experimental_core_four_market_state_scale_a_execution = {summary['scale_a_execution_status']}",
        "official_market_state = NOT_OPEN",
        "production_builder = NOT_AUTHORIZED",
        "downstream_consumption = NOT_AUTHORIZED",
        "dataset_promotion = NOT_AUTHORIZED",
        "full_history_execution = NOT_AUTHORIZED",
        "full_universe_execution = NOT_AUTHORIZED",
        "```",
        "",
        "## Counts",
        "",
        "```text",
        f"requested_contexts = {summary['requested_contexts']}",
        f"sample_manifest_rows = {summary['sample_manifest_rows']}",
        f"required_instruments = {summary['required_instruments']}",
        f"available_intraday_tickers = {summary['available_intraday_tickers']}",
        f"eligible_instruments = {summary['eligible_instruments']}",
        f"required_sessions = {summary['required_sessions']}",
        f"calendar_sessions_checked = {summary['calendar_sessions_checked']}",
        f"calendar_compatible_sessions = {summary['calendar_compatible_sessions']}",
        f"calendar_compatibility_failures = {summary['calendar_compatibility_failures']}",
        f"expected_resolution_records = {summary['expected_resolution_records']}",
        f"expected_blocked_contexts = {summary['expected_blocked_contexts']}",
        f"expected_integrable_contexts = {summary['expected_integrable_contexts']}",
        f"estimated_daily_rows = {summary['estimated_daily_rows']}",
        f"estimated_intraday_rows = {summary['estimated_intraday_rows']}",
        f"estimated_total_source_rows = {summary['estimated_total_source_rows']}",
        f"maximum_source_market_data_rows_read = {summary['maximum_source_market_data_rows_read']}",
        f"duplicate_context_ids = {summary['duplicate_context_ids']}",
        f"duplicate_semantic_contexts = {summary['duplicate_semantic_contexts']}",
        f"identity_failures = {summary['identity_failures']}",
        f"source_coverage_failures = {summary['source_coverage_failures']}",
        f"hard_preflight_failures = {summary['hard_preflight_failures']}",
        "```",
        "",
        "## Interpretation",
        "",
    ]
    if status == "PASS_WITH_RESTRICTIONS":
        lines.append("The Scale A sample is frozen as bounded non-production evidence. Builders may consume the emitted sample manifest in the next gate only.")
    elif status == "BLOCKED_SAMPLE_CARDINALITY":
        lines.append("The preflight did not freeze the 60-context sample because the authorized 014 source surface does not contain enough eligible instruments under the Scale A calendar guard.")
    elif status == "BLOCKED_CALENDAR_COMPATIBILITY":
        lines.append("The preflight did not freeze the sample because five compatible sessions could not be demonstrated under the fixed UTC Scale A guard.")
    else:
        lines.append("The preflight did not freeze the sample. Resolve the blocking report before starting any Scale A builder, integration or materialization run.")
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "```text",
            str(run_dir),
            "```",
            "",
            "The preflight did not execute builders, did not emit Information Object resolution records, did not integrate Market State and did not write parquet.",
            "",
            "## Next Gate",
            "",
        ]
    )
    if status == "PASS_WITH_RESTRICTIONS":
        lines.append("Open `experimental_core_four_market_state_scale_a_execution` as a separate run that consumes this exact sample fingerprint.")
    else:
        lines.append("Do not open `experimental_core_four_market_state_scale_a_execution`. Adjust the authorized source surface or Scale A scope, then rerun this preflight.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default=str(DEFAULT_SCOPE))
    args = parser.parse_args(argv)

    scope_path = Path(args.scope).resolve()
    scope_dir = scope_path.parent
    integration_root = scope_dir.parent
    workspace_root = Path("C:/TSIS_Data").resolve()
    scope = read_json(scope_path)
    validate_authority(scope)

    run_root = resolve_path(scope["output_policy"]["output_root"], scope_dir)
    if not is_within_or_equal(run_root, integration_root):
        raise PreflightError(f"Output root must stay inside integration root: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id_prefix = scope.get("output_policy", {}).get("run_id_prefix", RUN_ID_PREFIX)
    run_id = f"{run_id_prefix}_{timestamp}"
    run_dir = run_root / run_id
    if run_dir.exists():
        raise PreflightError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    if not is_within_or_equal(run_dir, workspace_root):
        raise PreflightError(f"Refusing to write outside workspace: {run_dir}")

    command_line = " ".join([str(Path(__file__).resolve()), "--scope", str(scope_path)])
    git_branch = git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], workspace_root)
    git_commit = git_value(["git", "rev-parse", "HEAD"], workspace_root)
    git_dirty_state = bool(git_value(["git", "status", "--porcelain"], workspace_root))

    pre_manifest = {
        "run_id": run_id,
        "status": "starting",
        "created_at_utc": utc_now(),
        "script_path": str(Path(__file__).resolve()),
        "script_version": SCRIPT_VERSION,
        "command_line": command_line,
        "cwd": str(Path.cwd()),
        "host": platform.node(),
        "user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "parent_pid": os.getppid(),
        "pid": os.getpid(),
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_dirty_state": git_dirty_state,
        "mode": scope["mode"],
        "execution_class": "experimental_scale_a_sample_preflight",
        "input_scope_path": str(scope_path),
        "output_root": str(run_root),
        "run_dir": str(run_dir),
        "expected_scope": "freeze exactly 60 Scale A contexts only if instrument, session, calendar and source coverage constraints pass",
        "overwrite_policy": "refuse_existing_run_dir",
        "success_criteria": "60 contexts, 8 instruments, 5 compatible sessions, 240 expected resolution records, 0 hard preflight failures",
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "load_scope_and_sources",
            "pid": os.getpid(),
            "run_dir": str(run_dir),
        },
    )

    registry_path, daily_root, intraday_root, registry = load_source_roots(scope, scope_dir)
    intraday, intraday_read_report = read_intraday_source(intraday_root)
    artifact_validation_report = validate_rerun_input_artifacts(scope, scope_dir, intraday_read_report)
    authorized_pool_tickers, eligible_pool_report = load_authorized_eligible_pool(scope, scope_dir)
    if authorized_pool_tickers:
        before_pool_filter_rows = int(len(intraday))
        authorized_pool_set = set(authorized_pool_tickers)
        intraday = intraday[intraday["ticker"].isin(authorized_pool_set)].copy().reset_index(drop=True)
        intraday_read_report["rows_after_authorized_pool_filter"] = int(len(intraday))
        intraday_read_report["authorized_pool_filter_removed_rows"] = before_pool_filter_rows - int(len(intraday))
        intraday_read_report["authorized_pool_tickers"] = authorized_pool_tickers
    intraday_years = sorted({int(value) for value in intraday["ts"].dropna().dt.year.unique()})
    intraday_tickers = sorted(str(ticker) for ticker in intraday["ticker"].dropna().unique())
    daily, daily_read_report = read_daily_source(daily_root, intraday_tickers, intraday_years)
    total_rows_read = int(intraday_read_report["rows_read"]) + int(daily_read_report["rows_read"])

    expected_open = scope["calendar_policy"]["required_selected_session_properties"]["regular_open_utc"]
    expected_close = scope["calendar_policy"]["required_selected_session_properties"]["regular_close_utc"]
    intraday_summaries, duplicate_map = build_intraday_summaries(intraday, expected_open, expected_close)
    daily_by_key, daily_by_ticker = build_daily_maps(daily)

    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "running",
            "stage": "build_reports",
            "pid": os.getpid(),
            "intraday_rows_read": intraday_read_report["rows_read"],
            "daily_rows_read": daily_read_report["rows_read"],
        },
    )

    calendar_rows, selected_sessions = build_calendar_report(intraday_summaries, scope)
    identity_rows, coverage_rows, eligible_tickers = build_identity_and_coverage_reports(
        intraday=intraday,
        intraday_summaries=intraday_summaries,
        daily_by_key=daily_by_key,
        daily_by_ticker=daily_by_ticker,
        selected_sessions=selected_sessions,
    )
    if authorized_pool_tickers:
        eligible_set = set(eligible_tickers)
        eligible_tickers = [ticker for ticker in authorized_pool_tickers if ticker in eligible_set]
    sample_rows = build_sample_manifest(
        scope=scope,
        eligible_tickers=eligible_tickers,
        selected_sessions=selected_sessions,
        identity_rows=identity_rows,
        intraday_summaries=intraday_summaries,
    )
    if len(sample_rows) != int(scope["limits"]["target_requested_contexts"]):
        sample_rows = []

    duplicate_rows, duplicate_context_ids, duplicate_semantic_contexts = build_duplicate_context_report(sample_rows)
    stratification_rows = build_stratification_report(
        scope=scope,
        sample_rows=sample_rows,
        eligible_tickers=eligible_tickers,
        selected_sessions=selected_sessions,
        intraday_summaries=intraday_summaries,
    )
    stratification_failures = sum(1 for row in stratification_rows if row.get("status") != "PASS")

    source_coverage_failures = sum(1 for row in coverage_rows if row["source_coverage_status"] != "PASS")
    source_coverage_failures_in_frozen_sample = 0
    if sample_rows:
        coverage_by_key = {(row["ticker"], row["session_date"]): row for row in coverage_rows}
        source_coverage_failures_in_frozen_sample = sum(
            1
            for row in sample_rows
            if coverage_by_key.get((row["ticker"], row["session_date"]), {}).get("source_coverage_status") != "PASS"
        )

    calendar_failures = sum(1 for row in calendar_rows if str(row.get("compatible")) != "True" and row.get("compatible") is not True)
    identity_failures = sum(
        1
        for row in identity_rows
        if row["daily_identity_resolved"] is not True and int(row.get("calendar_compatible_session_count") or 0) > 0
    )

    instrument_selection_fingerprint = sha256_payload(
        {
            "eligible_tickers": eligible_tickers,
            "required_instruments": scope["limits"]["instrument_count"],
            "sample_frozen": bool(sample_rows),
        }
    )
    session_selection_fingerprint = sha256_payload(
        {
            "selected_sessions": selected_sessions,
            "required_sessions": scope["limits"]["session_count"],
            "calendar_rows": calendar_rows,
            "sample_frozen": bool(sample_rows),
        }
    )
    scale_a_sample_fingerprint = sha256_payload(sample_rows) if sample_rows else ""

    summary: dict[str, Any] = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "scope_id": scope["scope_id"],
        "source_binding_registry": str(registry_path),
        "source_binding_registry_id": registry.get("registry_id"),
        "accepted_eligible_pool_required": bool(eligible_pool_report.get("pool_required")),
        "accepted_eligible_pool_instruments": int(eligible_pool_report.get("eligible_instruments_in_pool", 0)),
        "accepted_eligible_pool_fingerprint": eligible_pool_report.get("eligible_instrument_pool_fingerprint", ""),
        "accepted_bounded_014_surface_sha256": artifact_validation_report.get("observed_parquet_sha256", ""),
        "requested_contexts": int(scope["limits"]["target_requested_contexts"]),
        "maximum_requested_contexts_respected": bool(
            len(sample_rows) <= int(scope["limits"]["maximum_requested_contexts"])
        ),
        "sample_manifest_rows": len(sample_rows),
        "sample_freeze_status": "FROZEN" if sample_rows else "NOT_FROZEN_BLOCKED",
        "required_instruments": int(scope["limits"]["instrument_count"]),
        "available_intraday_tickers": len(intraday_tickers),
        "eligible_instruments": len(eligible_tickers),
        "selected_instruments": len({row["ticker"] for row in sample_rows}),
        "required_sessions": int(scope["limits"]["session_count"]),
        "selected_sessions": len(selected_sessions),
        "calendar_sessions_checked": len(calendar_rows),
        "calendar_compatible_sessions": sum(1 for row in calendar_rows if row.get("compatible") is True),
        "calendar_compatibility_failures": calendar_failures,
        "required_objects_per_context": int(scope["limits"]["required_objects_per_context"]),
        "expected_resolution_records": int(scope["limits"]["target_resolution_records"])
        if sample_rows
        else int(scope["limits"]["target_requested_contexts"]) * int(scope["limits"]["required_objects_per_context"]),
        "expected_blocked_contexts": int(scope["limits"]["target_expected_blocked_contexts"]),
        "expected_integrable_contexts": int(scope["limits"]["target_integrated_candidate_records"]),
        "estimated_daily_rows": int(daily_read_report["rows_read"]),
        "estimated_intraday_rows": int(intraday_read_report["rows_read"]),
        "estimated_total_source_rows": total_rows_read,
        "maximum_source_market_data_rows_read": int(scope["limits"]["maximum_source_market_data_rows_read"]),
        "source_market_data_rows_read_mode": "bounded_returned_rows_not_filesystem_access_audit",
        "duplicate_context_ids": duplicate_context_ids,
        "duplicate_semantic_contexts": duplicate_semantic_contexts,
        "identity_failures": identity_failures,
        "source_coverage_failures": source_coverage_failures,
        "source_coverage_failures_in_frozen_sample": source_coverage_failures_in_frozen_sample,
        "stratification_failures": stratification_failures,
        "duplicate_status_diversity_frozen_contexts": sum(
            1 for row in sample_rows if row.get("known_duplicate_physical_group_evidence") is True
        ),
        "contract_failures": 0,
        "instrument_selection_fingerprint": instrument_selection_fingerprint,
        "session_selection_fingerprint": session_selection_fingerprint,
        "scale_a_sample_fingerprint": scale_a_sample_fingerprint,
        "source_market_data_reread_beyond_authorized_aliases": False,
        "builders_executed": False,
        "resolution_records_emitted": 0,
        "integration_executed": False,
        "materialization_executed": False,
        "candidate_parquet_files_written": 0,
        "official_market_state_allowed": False,
        "production_builder_allowed": False,
        "downstream_consumption_allowed": False,
        "dataset_promotion_allowed": False,
        "full_history_execution_allowed": False,
        "full_universe_execution_allowed": False,
    }
    summary["preflight_status"] = decide_status(summary)
    blocking_statuses = {
        "BLOCKED_CALENDAR_COMPATIBILITY",
        "BLOCKED_SAMPLE_CARDINALITY",
        "BLOCKED_SOURCE_COVERAGE",
        "BLOCKED_IDENTITY",
        "FAILED_CONTRACT",
    }
    summary["hard_preflight_failures"] = 1 if summary["preflight_status"] in blocking_statuses else 0
    summary["scale_a_execution_status"] = (
        "NOT_EXECUTED_READY_FOR_SEPARATE_GATE"
        if summary["preflight_status"] == "PASS_WITH_RESTRICTIONS"
        else "BLOCKED_NOT_STARTED"
    )

    write_jsonl(run_dir / "scale_a_sample_manifest.jsonl", sample_rows)
    write_json(run_dir / "scale_a_sample_summary.json", summary)
    write_csv_rows(
        run_dir / "scale_a_calendar_compatibility_report.csv",
        [
            "session_date",
            "expected_open_utc",
            "observed_open_utc",
            "expected_close_utc",
            "observed_close_utc",
            "session_type",
            "early_close",
            "holiday_or_closed",
            "compatible",
            "evidence_source",
            "regular_window_ticker_count",
            "regular_window_min_first_ts_utc",
            "regular_window_max_last_ts_utc",
            "finding",
        ],
        calendar_rows,
    )
    write_csv_rows(
        run_dir / "scale_a_identity_report.csv",
        [
            "ticker",
            "daily_instrument_id",
            "daily_identity_resolved",
            "daily_identity_ambiguous",
            "daily_identity_count",
            "intraday_instrument_id_present",
            "intraday_rows",
            "calendar_compatible_session_count",
            "coverage_eligible_session_count",
            "instrument_selection_status",
            "finding",
        ],
        identity_rows,
    )
    write_csv_rows(
        run_dir / "scale_a_source_coverage_report.csv",
        [
            "ticker",
            "session_date",
            "daily_row_present",
            "daily_instrument_id_present",
            "daily_open_present",
            "daily_prior_close_present",
            "daily_volume_present",
            "prior_20_daily_volume_rows",
            "intraday_session_present",
            "intraday_regular_unique_bar_timestamps",
            "intraday_regular_duplicate_groups",
            "source_coverage_status",
            "finding",
        ],
        coverage_rows,
    )
    write_csv_rows(
        run_dir / "scale_a_stratification_report.csv",
        ["stratum", "required_count", "available_count", "frozen_sample_count", "status", "finding"],
        stratification_rows,
    )
    write_csv_rows(
        run_dir / "scale_a_duplicate_context_report.csv",
        ["check_name", "sample_context_id", "semantic_context_key", "duplicate_count", "status", "finding"],
        duplicate_rows,
    )
    sample_preflight_manifest = {
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "script_version": SCRIPT_VERSION,
        "input_scope": str(scope_path),
        "source_artifacts": {
            "004_master_daily_table_root": str(daily_root),
            "014_master_intraday_bar_table_candidate_root": str(intraday_root),
            "source_binding_registry": str(registry_path),
            "accepted_eligible_pool": eligible_pool_report,
            "accepted_bounded_014_surface": artifact_validation_report,
        },
        "source_read_reports": {
            "004_master_daily_table": daily_read_report,
            "014_master_intraday_bar_table_candidate": intraday_read_report,
            "estimated_total_source_rows": total_rows_read,
        },
        "outputs": {
            "scale_a_sample_manifest": str(run_dir / "scale_a_sample_manifest.jsonl"),
            "scale_a_sample_summary": str(run_dir / "scale_a_sample_summary.json"),
            "scale_a_calendar_compatibility_report": str(run_dir / "scale_a_calendar_compatibility_report.csv"),
            "scale_a_identity_report": str(run_dir / "scale_a_identity_report.csv"),
            "scale_a_source_coverage_report": str(run_dir / "scale_a_source_coverage_report.csv"),
            "scale_a_stratification_report": str(run_dir / "scale_a_stratification_report.csv"),
            "scale_a_duplicate_context_report": str(run_dir / "scale_a_duplicate_context_report.csv"),
        },
        "fingerprints": {
            "instrument_selection_fingerprint": instrument_selection_fingerprint,
            "session_selection_fingerprint": session_selection_fingerprint,
            "scale_a_sample_fingerprint": scale_a_sample_fingerprint,
        },
        "status": summary["preflight_status"],
    }
    write_json(run_dir / "sample_preflight_manifest.json", sample_preflight_manifest)
    final_manifest = {
        "run_id": run_id,
        "completed_at_utc": utc_now(),
        "script_version": SCRIPT_VERSION,
        "status": summary["preflight_status"],
        "summary": summary,
        "authority_boundary": {
            "builders_executed": False,
            "resolution_records_emitted": 0,
            "integration_executed": False,
            "materialization_executed": False,
            "candidate_parquet_files_written": 0,
            "official_market_state": "NOT_OPEN",
            "production_builder": "NOT_AUTHORIZED",
            "downstream_consumption": "NOT_AUTHORIZED",
            "dataset_promotion": "NOT_AUTHORIZED",
            "full_history_execution": "NOT_AUTHORIZED",
            "full_universe_execution": "NOT_AUTHORIZED",
        },
        "outputs": sample_preflight_manifest["outputs"],
    }
    write_json(run_dir / "final_manifest.json", final_manifest)
    write_json(
        run_dir / "heartbeat.json",
        {
            "run_id": run_id,
            "observed_at_utc": utc_now(),
            "status": "complete" if summary["preflight_status"] == "PASS_WITH_RESTRICTIONS" else "blocked",
            "stage": "final",
            "pid": os.getpid(),
            "preflight_status": summary["preflight_status"],
        },
    )
    readout_filename = scope.get("output_policy", {}).get(
        "readout_filename",
        "experimental_core_four_market_state_scale_a_sample_preflight_readout_v0_1.md",
    )
    readout_path = integration_root / str(readout_filename)
    write_readout(readout_path, run_id=run_id, summary=summary, run_dir=run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
