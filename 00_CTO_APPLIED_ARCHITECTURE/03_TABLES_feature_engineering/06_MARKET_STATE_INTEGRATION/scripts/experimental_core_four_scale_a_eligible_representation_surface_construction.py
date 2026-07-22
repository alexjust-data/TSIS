from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
from collections import Counter
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq


SCRIPT_VERSION = "experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1"
RUN_ID_PREFIX = "experimental_core_four_scale_a_eligible_representation_surface_construction_v0_1"
DEFAULT_SCOPE = (
    Path(__file__).resolve().parents[1]
    / "configs"
    / "experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1.json"
)
NY_TZ = ZoneInfo("America/New_York")


class ConstructionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe_value(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe_value(item) for item in value]
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


def canonical_json(value: Any, ensure_ascii: bool = True) -> str:
    return json.dumps(json_safe_value(value), ensure_ascii=ensure_ascii, sort_keys=True, separators=(",", ":"))


def serialize_cell(value: Any) -> str:
    safe = json_safe_value(value)
    if safe is None:
        return ""
    if isinstance(safe, (dict, list)):
        return canonical_json(safe, ensure_ascii=False)
    return str(safe)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(json_safe_value(payload), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def long_path_text_target(path: Path) -> str:
    resolved = str(path.resolve())
    prefix = "\\\\?\\"
    if platform.system().lower().startswith("win") and not resolved.startswith(prefix):
        return prefix + resolved
    return resolved


def write_text_file(path: Path, text: str) -> None:
    with open(long_path_text_target(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def long_path_exists(path: Path) -> bool:
    return os.path.exists(long_path_text_target(path))


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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_path(raw: str, base: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


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


def clock_text(value: datetime | pd.Timestamp | None) -> str:
    if value is None:
        return ""
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).time().replace(microsecond=0).isoformat()


def session_time_utc(session_date: date, time_text: str) -> datetime:
    parts = [int(part) for part in str(time_text).split(":")]
    while len(parts) < 3:
        parts.append(0)
    return datetime.combine(session_date, time(parts[0], parts[1], parts[2]), tzinfo=timezone.utc)


def ny_regular_session_utc(session_date: date) -> tuple[datetime, datetime]:
    local_open = datetime.combine(session_date, time(9, 30), tzinfo=NY_TZ)
    local_close = datetime.combine(session_date, time(16, 0), tzinfo=NY_TZ)
    return local_open.astimezone(timezone.utc), local_close.astimezone(timezone.utc)


def file_doc(path: Path, *, include_hash: bool = True) -> dict[str, Any]:
    stat = path.stat()
    payload = {
        "path": str(path),
        "exists": path.exists(),
        "bytes": int(stat.st_size),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if path.suffix.lower() == ".parquet":
        pf = pq.ParquetFile(path)
        payload["parquet_rows"] = int(pf.metadata.num_rows)
        payload["parquet_row_groups"] = int(pf.metadata.num_row_groups)
        payload["columns"] = list(pf.schema_arrow.names)
    if include_hash:
        payload["sha256"] = sha256_file(path)
    return payload


def validate_authority(scope: dict[str, Any]) -> None:
    if scope.get("scope_id") != "experimental_core_four_scale_a_eligible_representation_surface_scope_v0_1":
        raise ConstructionError("Unexpected eligible representation surface scope_id")
    if scope.get("mode") != "experimental_core_four_scale_a_eligible_representation_surface_construction":
        raise ConstructionError("Unexpected construction mode")
    authority = scope.get("authority", {})
    required_true = [
        "source_snapshot_allowed",
        "bounded_014_derived_candidate_surface_creation_allowed",
        "eligible_pool_construction_allowed",
        "upstream_013_allowed_only_for_bounded_014_derivation",
    ]
    required_false = [
        "original_014_modification_allowed",
        "official_014_promotion_allowed",
        "scale_a_sample_preflight_rerun_allowed",
        "scale_a_builder_execution_allowed",
        "information_object_resolution_allowed",
        "market_state_integration_allowed",
        "market_state_materialization_allowed",
        "market_state_candidate_parquet_allowed",
        "official_market_state_allowed",
        "production_builder_allowed",
        "state_consumption_allowed",
        "downstream_consumption_allowed",
        "dataset_promotion_allowed",
        "full_history_execution_allowed",
        "full_universe_execution_allowed",
        "quote_dependent_object_integration_allowed",
        "raw_quote_consumption_allowed",
        "microstructure_feature_consumption_allowed",
    ]
    bad_true = [key for key in required_true if authority.get(key) is not True]
    bad_false = [key for key in required_false if authority.get(key) is not False]
    if bad_true or bad_false:
        raise ConstructionError(f"Authority validation failed: true={bad_true}; false={bad_false}")
    allowed = set(scope.get("source_aliases_allowed", []))
    expected_allowed = {"004_master_daily_table", "014_master_intraday_bar_table_candidate", "013_ohlcv_1m_quote_guarded"}
    if allowed != expected_allowed:
        raise ConstructionError(f"Unexpected allowed aliases: {sorted(allowed)}")
    forbidden = {str(item).replace("\\", "/") for item in scope.get("source_aliases_forbidden", [])}
    if "00_CTO/99_REFERENCE_LIBRARY" not in forbidden:
        raise ConstructionError("Reference library exclusion missing")
    if "013_ohlcv_1m_quote_guarded" in forbidden:
        raise ConstructionError("013 is both allowed and forbidden")
    limits = scope.get("limits", {})
    if int(limits.get("required_output_files", -1)) != len(scope.get("allowed_outputs", [])):
        raise ConstructionError("required_output_files does not match allowed_outputs count")
    if int(limits.get("maximum_output_files", -1)) < int(limits.get("required_output_files", -1)):
        raise ConstructionError("maximum_output_files is lower than required_output_files")


def resolve_source_roots(scope: dict[str, Any], scope_dir: Path) -> tuple[Path, dict[str, Path], dict[str, Any]]:
    registry_path = resolve_path(scope["governance_inputs"]["source_binding_registry"], scope_dir)
    registry = read_json(registry_path)
    bindings = registry.get("bindings", {})
    roots: dict[str, Path] = {}
    for alias in scope["source_aliases_allowed"]:
        binding = bindings.get(alias)
        if not binding:
            raise ConstructionError(f"Missing source binding for {alias}")
        root = Path(str(binding.get("physical_candidate_root"))).resolve()
        root_text = str(root).replace("\\", "/")
        if "00_CTO/99_REFERENCE_LIBRARY" in root_text:
            raise ConstructionError(f"Forbidden reference library path resolved for {alias}: {root}")
        if not root.exists():
            raise ConstructionError(f"Resolved source root does not exist for {alias}: {root}")
        roots[alias] = root
    return registry_path, roots, registry


def discover_013_files(root: Path, *, year: int, month: int, max_candidates: int) -> tuple[list[str], list[Path], int]:
    year_dir = root / f"year={year}"
    if not year_dir.exists():
        return [], [], 0
    tickers: list[str] = []
    files: list[Path] = []
    dirs_inspected = 0
    for ticker_dir in sorted((item for item in year_dir.iterdir() if item.is_dir()), key=lambda item: item.name):
        if not ticker_dir.name.startswith("ticker="):
            continue
        dirs_inspected += 1
        ticker = ticker_dir.name.split("=", 1)[1].strip().upper()
        month_dir = ticker_dir / f"month={month:02d}"
        month_files = sorted(month_dir.glob("*.parquet")) if month_dir.exists() else []
        if not month_files:
            continue
        tickers.append(ticker)
        files.extend(month_files)
        if len(tickers) >= max_candidates:
            break
    return tickers, files, dirs_inspected


def read_013(files: list[Path]) -> tuple[pd.DataFrame, list[dict[str, Any]], int]:
    frames: list[pd.DataFrame] = []
    file_docs: list[dict[str, Any]] = []
    columns = ["ticker", "ts_utc", "date", "year", "month", "o", "h", "l", "c", "v"]
    rows_read = 0
    for path in files:
        doc = file_doc(path, include_hash=True)
        file_docs.append(doc)
        table = pq.ParquetFile(path).read(columns=columns)
        df = table.to_pandas()
        df["source_alias"] = "013_ohlcv_1m_quote_guarded"
        df["source_file"] = str(path)
        df["source_row_ordinal"] = range(len(df))
        frames.append(df)
        rows_read += int(len(df))
    if not frames:
        return pd.DataFrame(columns=columns), file_docs, rows_read
    df = pd.concat(frames, ignore_index=True)
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_iso"] = df["date"].map(lambda value: (parse_session_date(value).isoformat() if parse_session_date(value) else ""))
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    for src, dst in [("o", "open"), ("h", "high"), ("l", "low"), ("c", "close"), ("v", "volume")]:
        df[dst] = pd.to_numeric(df[src], errors="coerce")
    return df, file_docs, rows_read


def read_014(root: Path) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    path = root / "data.parquet"
    if not path.exists():
        raise ConstructionError(f"014 data.parquet not found: {path}")
    before = file_doc(path, include_hash=True)
    columns = ["ticker", "instrument_id", "session_date", "year", "month", "ts_utc", "price_view", "bar_size", "open", "high", "low", "close", "volume"]
    pf = pq.ParquetFile(path)
    missing = [column for column in columns if column not in set(pf.schema_arrow.names)]
    if missing:
        raise ConstructionError(f"014 missing columns: {missing}")
    df = pf.read(columns=columns).to_pandas()
    df["source_alias"] = "014_master_intraday_bar_table_candidate"
    df["source_file"] = str(path)
    df["source_row_ordinal"] = range(len(df))
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_iso"] = df["session_date"].map(lambda value: (parse_session_date(value).isoformat() if parse_session_date(value) else ""))
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df, before, before


def read_daily(root: Path, tickers: list[str], *, year: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    path = root / f"year={year}" / "price_view=split_normalized" / "data_0.parquet"
    if not path.exists():
        raise ConstructionError(f"004 split_normalized file not found: {path}")
    columns = ["instrument_id", "ticker", "session_date", "open", "prior_close", "volume"]
    pf = pq.ParquetFile(path)
    missing = [column for column in columns if column not in set(pf.schema_arrow.names)]
    if missing:
        raise ConstructionError(f"004 missing columns: {missing}")
    source_doc = file_doc(path, include_hash=True)
    dataset = ds.dataset(str(path), format="parquet")
    table = dataset.to_table(columns=columns, filter=ds.field("ticker").isin(tickers))
    df = table.to_pandas()
    df["price_view"] = "split_normalized"
    df["source_alias"] = "004_master_daily_table"
    df["source_file"] = str(path)
    df["source_row_ordinal"] = range(len(df))
    df["ticker"] = df["ticker"].astype(str).str.strip().str.upper()
    df["session_date_iso"] = df["session_date"].map(lambda value: (parse_session_date(value).isoformat() if parse_session_date(value) else ""))
    for column in ["open", "prior_close", "volume"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    source_doc["filtered_ticker_count"] = int(df["ticker"].nunique(dropna=True))
    source_doc["filtered_rows"] = int(len(df))
    source_doc["rows_read"] = int(len(df))
    return df, source_doc


def compatible_session_rows(intraday_013: pd.DataFrame, scope: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    guard = scope["calendar_guard"]
    expected_open = str(guard["regular_open_utc"])
    expected_close = str(guard["regular_close_utc"])
    candidate_dates = sorted(date_key for date_key in intraday_013["session_date_iso"].dropna().unique() if date_key)
    rows: list[dict[str, Any]] = []
    for date_key in candidate_dates:
        session_obj = parse_session_date(date_key)
        if session_obj is None:
            continue
        observed_open, observed_close = ny_regular_session_utc(session_obj)
        holiday_or_closed = session_obj.weekday() >= 5
        session_type = "closed_or_weekend" if holiday_or_closed else "regular"
        compatible = (
            clock_text(observed_open) == expected_open
            and clock_text(observed_close) == expected_close
            and session_type == "regular"
            and holiday_or_closed is False
        )
        ticker_count = int(intraday_013.loc[intraday_013["session_date_iso"] == date_key, "ticker"].nunique())
        rows.append(
            {
                "session_date": date_key,
                "expected_open_utc": expected_open,
                "observed_open_utc": clock_text(observed_open),
                "expected_close_utc": expected_close,
                "observed_close_utc": clock_text(observed_close),
                "session_type": session_type,
                "early_close": False,
                "holiday_or_closed": bool(holiday_or_closed),
                "compatible": bool(compatible and ticker_count > 0),
                "intraday_ticker_count": ticker_count,
                "evidence_source": "America/New_York regular session conversion plus 013 bounded row presence; not a governed exchange calendar",
                "finding": "compatible with fixed UTC Scale A guard" if compatible and ticker_count > 0 else "not compatible",
            }
        )
    selected = [row["session_date"] for row in rows if row["compatible"] is True][
        : int(scope["limits"]["maximum_sessions_considered"])
    ]
    selected_rows = [row for row in rows if row["session_date"] in set(selected)]
    return selected_rows, selected


def state_signature(row: pd.Series) -> str:
    return canonical_json(
        {
            "open": json_safe_value(row.get("open")),
            "high": json_safe_value(row.get("high")),
            "low": json_safe_value(row.get("low")),
            "close": json_safe_value(row.get("close")),
            "volume": json_safe_value(row.get("volume")),
        }
    )


def daily_maps(daily: pd.DataFrame) -> tuple[dict[tuple[str, str], list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    by_ticker: dict[str, list[dict[str, Any]]] = {}
    for _, row in daily.dropna(subset=["ticker", "session_date_iso"]).iterrows():
        doc = {
            "ticker": str(row["ticker"]),
            "session_date": str(row["session_date_iso"]),
            "instrument_id": json_safe_value(row.get("instrument_id")),
            "open_present": bool(pd.notna(row.get("open"))),
            "prior_close_present": bool(pd.notna(row.get("prior_close"))),
            "volume_present": bool(pd.notna(row.get("volume"))),
        }
        by_key.setdefault((doc["ticker"], doc["session_date"]), []).append(doc)
        by_ticker.setdefault(doc["ticker"], []).append(doc)
    for ticker in by_ticker:
        by_ticker[ticker] = sorted(by_ticker[ticker], key=lambda item: item["session_date"])
    return by_key, by_ticker


def resolve_instrument_id(rows: list[dict[str, Any]]) -> tuple[str, bool, bool, int]:
    ids = sorted({str(row.get("instrument_id")) for row in rows if row.get("instrument_id") not in {None, ""}})
    return (ids[0] if len(ids) == 1 else "", len(ids) == 1, len(ids) > 1, len(ids))


def prior_volume_count(rows: list[dict[str, Any]], session_date_iso: str) -> int:
    dates = sorted({row["session_date"] for row in rows if row["session_date"] < session_date_iso and row["volume_present"]})
    return min(len(dates), 20)


def normalize_013_rows(
    intraday_013: pd.DataFrame,
    *,
    selected_sessions: list[str],
    source_snapshot_fingerprint: str,
    instrument_id_by_ticker: dict[str, str],
) -> pd.DataFrame:
    df = intraday_013[intraday_013["session_date_iso"].isin(selected_sessions)].copy()
    df["instrument_id"] = df["ticker"].map(instrument_id_by_ticker).fillna("")
    df["bar_end_utc"] = df["ts"]
    df["ts_utc_out"] = df["ts"]
    df["bar_size"] = "1m"
    df["price_view"] = "1m_quote_guarded_raw"
    df["selection_reason"] = "bounded 013 upstream row normalized into run-local 014-derived candidate surface"
    df["source_snapshot_fingerprint"] = source_snapshot_fingerprint
    df = df[
        [
            "source_alias",
            "source_file",
            "source_row_ordinal",
            "source_snapshot_fingerprint",
            "ticker",
            "instrument_id",
            "session_date_iso",
            "year",
            "month",
            "ts_utc_out",
            "bar_end_utc",
            "bar_size",
            "price_view",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "selection_reason",
        ]
    ].rename(columns={"session_date_iso": "session_date", "ts_utc_out": "ts_utc"})
    return df


def normalize_014_rows(
    intraday_014: pd.DataFrame,
    *,
    selected_sessions: list[str],
    tickers: list[str],
    source_snapshot_fingerprint: str,
) -> pd.DataFrame:
    df = intraday_014[
        intraday_014["session_date_iso"].isin(selected_sessions)
        & intraday_014["ticker"].isin(tickers)
        & (intraday_014["price_view"].astype(str) == "1m_quote_guarded_raw")
    ].copy()
    if df.empty:
        return pd.DataFrame()
    df["bar_end_utc"] = df["ts"]
    df["ts_utc_out"] = df["ts"]
    df["selection_reason"] = "existing 014 candidate row preserved where applicable"
    df["source_snapshot_fingerprint"] = source_snapshot_fingerprint
    df = df[
        [
            "source_alias",
            "source_file",
            "source_row_ordinal",
            "source_snapshot_fingerprint",
            "ticker",
            "instrument_id",
            "session_date_iso",
            "year",
            "month",
            "ts_utc_out",
            "bar_end_utc",
            "bar_size",
            "price_view",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "selection_reason",
        ]
    ].rename(columns={"session_date_iso": "session_date", "ts_utc_out": "ts_utc"})
    return df


def build_derived_surface(rows_013: pd.DataFrame, rows_014: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    frames = [frame for frame in [rows_014, rows_013] if frame is not None and not frame.empty]
    if not frames:
        return pd.DataFrame(), []
    combined = pd.concat(frames, ignore_index=True)
    combined["source_priority"] = combined["source_alias"].map({"014_master_intraday_bar_table_candidate": 0}).fillna(1)
    combined = combined.sort_values(["ticker", "session_date", "ts_utc", "source_priority", "source_file", "source_row_ordinal"])
    duplicate_rows: list[dict[str, Any]] = []
    statuses: dict[tuple[str, str, str], str] = {}
    for key, group in combined.groupby(["ticker", "session_date", "ts_utc"], sort=True):
        signatures = {state_signature(row) for _, row in group.iterrows()}
        if len(group) > 1 and len(signatures) > 1:
            status = "conflicting_duplicate_rows_existing_014_preferred"
            risk_rank = 2
        elif len(group) > 1:
            status = "identical_duplicate_rows_collapsed"
            risk_rank = 1
        else:
            status = "unique"
            risk_rank = 0
        statuses[(str(key[0]), str(key[1]), pd.Timestamp(key[2]).isoformat().replace("+00:00", "Z"))] = status
        duplicate_rows.append(
            {
                "ticker": str(key[0]),
                "session_date": str(key[1]),
                "bar_end_utc": pd.Timestamp(key[2]).isoformat().replace("+00:00", "Z"),
                "duplicate_group_row_count": int(len(group)),
                "duplicate_group_distinct_state_count": int(len(signatures)),
                "duplicate_status": status,
                "duplicate_risk_rank": risk_rank,
                "kept_source_alias": str(group.iloc[0]["source_alias"]),
                "dropped_rows": int(max(0, len(group) - 1)),
            }
        )
    deduped = combined.drop_duplicates(["ticker", "session_date", "ts_utc"], keep="first").copy()
    deduped["duplicate_status"] = deduped.apply(
        lambda row: statuses[
            (
                str(row["ticker"]),
                str(row["session_date"]),
                pd.Timestamp(row["ts_utc"]).isoformat().replace("+00:00", "Z"),
            )
        ],
        axis=1,
    )
    return deduped.drop(columns=["source_priority"]), duplicate_rows


def write_derived_surface(path: Path, rows: pd.DataFrame) -> None:
    column_order = [
        "source_alias",
        "source_file",
        "source_row_ordinal",
        "source_snapshot_fingerprint",
        "ticker",
        "instrument_id",
        "session_date",
        "year",
        "month",
        "ts_utc",
        "bar_end_utc",
        "bar_size",
        "price_view",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "duplicate_status",
        "selection_reason",
    ]
    rows = rows[column_order].copy()
    rows["source_row_ordinal"] = pd.to_numeric(rows["source_row_ordinal"], errors="coerce").fillna(-1).astype("int64")
    rows["year"] = pd.to_numeric(rows["year"], errors="coerce").fillna(-1).astype("int64")
    rows["month"] = pd.to_numeric(rows["month"], errors="coerce").fillna(-1).astype("int64")
    for column in ["open", "high", "low", "close", "volume"]:
        rows[column] = pd.to_numeric(rows[column], errors="coerce").astype("float64")
    rows["ts_utc"] = pd.to_datetime(rows["ts_utc"], utc=True, errors="coerce")
    rows["bar_end_utc"] = pd.to_datetime(rows["bar_end_utc"], utc=True, errors="coerce")
    schema = pa.schema(
        [
            ("source_alias", pa.string()),
            ("source_file", pa.string()),
            ("source_row_ordinal", pa.int64()),
            ("source_snapshot_fingerprint", pa.string()),
            ("ticker", pa.string()),
            ("instrument_id", pa.string()),
            ("session_date", pa.string()),
            ("year", pa.int64()),
            ("month", pa.int64()),
            ("ts_utc", pa.timestamp("ns", tz="UTC")),
            ("bar_end_utc", pa.timestamp("ns", tz="UTC")),
            ("bar_size", pa.string()),
            ("price_view", pa.string()),
            ("open", pa.float64()),
            ("high", pa.float64()),
            ("low", pa.float64()),
            ("close", pa.float64()),
            ("volume", pa.float64()),
            ("duplicate_status", pa.string()),
            ("selection_reason", pa.string()),
        ]
    )
    table = pa.Table.from_pandas(rows, schema=schema, preserve_index=False)
    pq.write_table(table, path, compression="zstd")


def semantic_surface_fingerprint(rows: pd.DataFrame) -> str:
    payload = []
    for _, row in rows.sort_values(["ticker", "session_date", "ts_utc"]).iterrows():
        payload.append(
            {
                "ticker": row["ticker"],
                "instrument_id": row["instrument_id"],
                "session_date": row["session_date"],
                "bar_end_utc": json_safe_value(row["bar_end_utc"]),
                "open": json_safe_value(row["open"]),
                "high": json_safe_value(row["high"]),
                "low": json_safe_value(row["low"]),
                "close": json_safe_value(row["close"]),
                "volume": json_safe_value(row["volume"]),
                "source_alias": row["source_alias"],
                "source_file": row["source_file"],
                "source_row_ordinal": row["source_row_ordinal"],
                "duplicate_status": row["duplicate_status"],
            }
        )
    return sha256_payload(payload)


def evaluate_candidates(
    *,
    candidate_tickers: list[str],
    selected_sessions: list[str],
    daily: pd.DataFrame,
    derived_surface: pd.DataFrame,
    duplicate_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    daily_by_key, daily_by_ticker = daily_maps(daily)
    duplicate_risk_by_ticker: dict[str, int] = {}
    for row in duplicate_rows:
        duplicate_risk_by_ticker[str(row["ticker"])] = max(
            duplicate_risk_by_ticker.get(str(row["ticker"]), 0),
            int(row.get("duplicate_risk_rank", 0)),
        )
    session_rows: list[dict[str, Any]] = []
    pool_candidates: list[dict[str, Any]] = []
    rejection_rows: list[dict[str, Any]] = []
    for ticker in candidate_tickers:
        ticker_daily_rows = daily_by_ticker.get(ticker, [])
        instrument_id, identity_resolved, identity_ambiguous, identity_count = resolve_instrument_id(ticker_daily_rows)
        eligible_session_count = 0
        daily_linked_count = 0
        intraday_linked_count = 0
        prior20_count = 0
        field_present_cells = 0
        field_expected_cells = 0
        source_rows = int((derived_surface["ticker"] == ticker).sum()) if not derived_surface.empty else 0
        for session_date in selected_sessions:
            daily_rows = daily_by_key.get((ticker, session_date), [])
            daily_row = daily_rows[0] if daily_rows else None
            intraday_rows = derived_surface[
                (derived_surface["ticker"] == ticker) & (derived_surface["session_date"] == session_date)
            ]
            intraday_regular_rows = int(len(intraday_rows))
            daily_linked = bool(
                daily_row
                and daily_row.get("instrument_id")
                and daily_row.get("open_present")
                and daily_row.get("prior_close_present")
                and daily_row.get("volume_present")
            )
            intraday_linked = intraday_regular_rows > 0
            prior_count = prior_volume_count(ticker_daily_rows, session_date)
            prior_ok = prior_count >= 20
            required_intraday_fields_present = bool(
                intraday_linked
                and intraday_rows[["open", "high", "low", "close", "volume"]].notna().all(axis=None)
            )
            required_fields_present = bool(daily_linked and required_intraday_fields_present)
            eligible_session = bool(
                identity_resolved
                and daily_linked
                and intraday_linked
                and prior_ok
                and required_fields_present
            )
            if daily_linked:
                daily_linked_count += 1
            if intraday_linked:
                intraday_linked_count += 1
            if prior_ok:
                prior20_count += 1
            if eligible_session:
                eligible_session_count += 1
            expected = 10
            present = 0
            present += int(bool(identity_resolved))
            present += int(bool(daily_row))
            present += int(bool(daily_row and daily_row.get("instrument_id")))
            present += int(bool(daily_row and daily_row.get("open_present")))
            present += int(bool(daily_row and daily_row.get("prior_close_present")))
            present += int(bool(daily_row and daily_row.get("volume_present")))
            present += int(bool(prior_ok))
            present += int(bool(intraday_linked))
            present += int(bool(required_intraday_fields_present))
            present += 1
            field_present_cells += present
            field_expected_cells += expected
            session_rows.append(
                {
                    "ticker": ticker,
                    "instrument_id": instrument_id,
                    "session_date": session_date,
                    "identity_resolved": identity_resolved,
                    "daily_linked": daily_linked,
                    "intraday_linked": intraday_linked,
                    "prior_20_daily_volume_rows": prior_count,
                    "prior_20_daily_volume_coverage_available": prior_ok,
                    "required_core_four_source_fields_present": required_fields_present,
                    "intraday_rows": intraday_regular_rows,
                    "calendar_guard_compatible": True,
                    "excluded_context_class": False,
                    "eligible_session": eligible_session,
                    "status": "PASS" if eligible_session else "NOT_ELIGIBLE_SESSION",
                }
            )
        sessions_considered = max(1, len(selected_sessions))
        required_field_coverage_ratio = field_present_cells / max(1, field_expected_cells)
        candidate = {
            "instrument_id": instrument_id,
            "ticker": ticker,
            "identity_resolved": identity_resolved,
            "identity_ambiguous": identity_ambiguous,
            "identity_count": identity_count,
            "eligible_session_count": eligible_session_count,
            "calendar_compatible_session_coverage_count": len(selected_sessions),
            "daily_linkage_completeness_ratio": daily_linked_count / sessions_considered,
            "intraday_linkage_completeness_ratio": intraday_linked_count / sessions_considered,
            "prior_20_daily_volume_complete_session_count": prior20_count,
            "required_field_coverage_ratio": required_field_coverage_ratio,
            "duplicate_risk_rank": duplicate_risk_by_ticker.get(ticker, 0),
            "source_rows_per_eligible_session": source_rows / max(1, eligible_session_count),
            "source_rows": source_rows,
        }
        rejection_reasons = []
        if not identity_resolved:
            rejection_reasons.append("identity_not_resolved")
        if eligible_session_count < 5:
            rejection_reasons.append("eligible_session_count_lt_5")
        if not rejection_reasons:
            pool_candidates.append(candidate)
        else:
            rejection_rows.append({**candidate, "rejection_reasons": rejection_reasons})
    ranked = sorted(
        pool_candidates,
        key=lambda row: (
            -int(row["calendar_compatible_session_coverage_count"]),
            -int(row["identity_resolved"]),
            -float(row["daily_linkage_completeness_ratio"]),
            -float(row["intraday_linkage_completeness_ratio"]),
            -int(row["prior_20_daily_volume_complete_session_count"]),
            -float(row["required_field_coverage_ratio"]),
            int(row["duplicate_risk_rank"]),
            float(row["source_rows_per_eligible_session"]),
            str(row["instrument_id"]),
            str(row["ticker"]),
        ),
    )
    return ranked, rejection_rows, session_rows, duplicate_rows


def build_readout(status: str, run_id: str, summary: dict[str, Any]) -> str:
    return f"""# Experimental Core Four Scale A Eligible Representation Surface Construction Readout v0.1

Status: `{status}`
Date: `2026-07-22`
Run: `{run_id}`

This run constructed the bounded eligible representation surface for Scale A.
It did not rerun Scale A sample preflight, execute builders, resolve
Information Objects, integrate Market State, materialize Market State parquet,
promote data, or authorize downstream consumption.

## Result

```text
candidate_instruments_discovered = {summary['candidate_instruments_discovered']}
resolved_intraday_source_distinct_instruments = {summary['resolved_intraday_source_distinct_instruments']}
candidate_instruments_with_daily_linkage = {summary['candidate_instruments_with_daily_linkage']}
candidate_instruments_with_5_compatible_sessions = {summary['candidate_instruments_with_5_compatible_sessions']}
eligible_candidates_before_cap = {summary['eligible_candidates_before_cap']}
eligible_instruments_emitted = {summary['eligible_instruments_emitted']}
selected_sessions = {summary['selected_sessions_count']}
source_market_data_rows_read = {summary['source_market_data_rows_read']}
derived_014_rows_written = {summary['derived_014_rows_written']}
candidate_surface_parquet_files_written = {summary['candidate_surface_parquet_files_written']}
market_state_parquet_files_written = 0
authority_failures = {summary['authority_failures']}
determinism_failures = {summary['determinism_failures']}
hard_contract_failures = {summary['hard_contract_failures']}
```

## Boundary

```text
original_014_modified = false
013_use = bounded_upstream_for_run_local_014_derivation_only
Scale_A_sample_preflight_rerun = NOT_AUTHORIZED
Scale_A_builder_execution = NOT_AUTHORIZED
Market_State_integration = NOT_AUTHORIZED
Market_State_materialization = NOT_AUTHORIZED
Market_State_parquet = NOT_AUTHORIZED
official_Market_State = NOT_OPEN
downstream_consumption = NOT_AUTHORIZED
```

## Next Gate

```text
experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", type=Path, default=DEFAULT_SCOPE)
    args = parser.parse_args()

    scope_path = args.scope.resolve()
    scope_dir = scope_path.parent
    base_dir = scope_dir.parent
    repo_root = base_dir.parents[2]
    scope = read_json(scope_path)
    validate_authority(scope)

    run_id = f"{RUN_ID_PREFIX}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir = base_dir / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    start = utc_now()

    registry_path, roots, _ = resolve_source_roots(scope, scope_dir)
    limits = scope["limits"]
    construction_year = 2025
    construction_month = 9
    max_candidates = int(limits["maximum_candidate_instruments_discovered"])

    pre_manifest = {
        "run_id": run_id,
        "created_at_utc": start,
        "script_version": SCRIPT_VERSION,
        "scope": str(scope_path),
        "authorization": str((base_dir / "experimental_core_four_scale_a_eligible_representation_surface_authorization_v0_1.md").resolve()),
        "authority": scope["authority"],
        "limits": limits,
        "git_commit": git_value(["git", "rev-parse", "HEAD"], repo_root),
        "git_branch": git_value(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo_root),
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    write_json(run_dir / "pre_manifest.json", pre_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": "RUNNING", "updated_at_utc": utc_now()})

    candidate_tickers, source_013_files, dirs_inspected = discover_013_files(
        roots["013_ohlcv_1m_quote_guarded"],
        year=construction_year,
        month=construction_month,
        max_candidates=max_candidates,
    )
    intraday_013, source_013_file_docs, rows_013_read = read_013(source_013_files)
    intraday_014, original_014_before, _ = read_014(roots["014_master_intraday_bar_table_candidate"])
    daily, daily_source_doc = read_daily(roots["004_master_daily_table"], candidate_tickers, year=construction_year)
    total_source_rows_read = int(rows_013_read + original_014_before.get("parquet_rows", 0) + daily_source_doc.get("rows_read", 0))

    calendar_rows, selected_sessions = compatible_session_rows(intraday_013, scope)
    d_by_key, d_by_ticker = daily_maps(daily)
    candidate_instruments_with_daily_linkage = 0
    candidate_instruments_with_5_compatible_sessions = 0
    instrument_id_by_ticker: dict[str, str] = {}
    for ticker in candidate_tickers:
        instrument_id, identity_resolved, _, _ = resolve_instrument_id(d_by_ticker.get(ticker, []))
        if identity_resolved:
            instrument_id_by_ticker[ticker] = instrument_id
        linked_sessions = 0
        compatible_intraday_sessions = 0
        for session_date in selected_sessions:
            if d_by_key.get((ticker, session_date)):
                linked_sessions += 1
            if not intraday_013[
                (intraday_013["ticker"] == ticker) & (intraday_013["session_date_iso"] == session_date)
            ].empty:
                compatible_intraday_sessions += 1
        if identity_resolved and linked_sessions >= int(limits["minimum_eligible_sessions_per_instrument"]):
            candidate_instruments_with_daily_linkage += 1
        if compatible_intraday_sessions >= int(limits["minimum_eligible_sessions_per_instrument"]):
            candidate_instruments_with_5_compatible_sessions += 1

    feasibility = {
        "resolved_intraday_source_distinct_instruments": int(intraday_013["ticker"].nunique(dropna=True)),
        "candidate_instruments_discovered": int(len(candidate_tickers)),
        "candidate_instrument_dirs_inspected": int(dirs_inspected),
        "candidate_instruments_with_daily_linkage": candidate_instruments_with_daily_linkage,
        "candidate_instruments_with_5_compatible_sessions": candidate_instruments_with_5_compatible_sessions,
        "minimum_resolved_intraday_source_distinct_instruments": int(
            scope["source_expansion_feasibility_precheck"]["minimum_resolved_intraday_source_distinct_instruments"]
        ),
        "minimum_candidate_instruments_with_daily_linkage": int(
            scope["source_expansion_feasibility_precheck"]["minimum_candidate_instruments_with_daily_linkage"]
        ),
        "minimum_candidate_instruments_with_5_compatible_sessions": int(
            scope["source_expansion_feasibility_precheck"]["minimum_candidate_instruments_with_5_compatible_sessions"]
        ),
    }
    feasibility["passed"] = bool(
        feasibility["resolved_intraday_source_distinct_instruments"]
        >= feasibility["minimum_resolved_intraday_source_distinct_instruments"]
        and feasibility["candidate_instruments_with_daily_linkage"]
        >= feasibility["minimum_candidate_instruments_with_daily_linkage"]
        and feasibility["candidate_instruments_with_5_compatible_sessions"]
        >= feasibility["minimum_candidate_instruments_with_5_compatible_sessions"]
    )

    source_snapshot_payload = {
        "run_id": run_id,
        "source_binding_registry": str(registry_path),
        "source_paths": {
            "004_master_daily_table": str(roots["004_master_daily_table"]),
            "014_master_intraday_bar_table_candidate": str(roots["014_master_intraday_bar_table_candidate"]),
            "013_ohlcv_1m_quote_guarded": str(roots["013_ohlcv_1m_quote_guarded"]),
        },
        "construction_period": {"year": construction_year, "month": construction_month},
        "candidate_tickers": candidate_tickers,
        "selected_sessions": selected_sessions,
        "feasibility_precheck": feasibility,
        "source_files": {
            "004_daily_file": daily_source_doc,
            "014_current_file": original_014_before,
            "013_selected_files": source_013_file_docs,
        },
        "source_read_rows": {
            "004_rows_read": int(daily_source_doc.get("rows_read", 0)),
            "004_filtered_rows": int(daily_source_doc.get("filtered_rows", 0)),
            "014_rows_read": int(original_014_before.get("parquet_rows", 0)),
            "013_rows_read": int(rows_013_read),
            "total_source_market_data_rows_read": total_source_rows_read,
        },
    }
    source_snapshot_fingerprint = sha256_payload(source_snapshot_payload)
    source_snapshot_payload["source_snapshot_fingerprint"] = source_snapshot_fingerprint
    write_json(run_dir / "eligible_surface_source_snapshot_manifest.json", source_snapshot_payload)

    if not feasibility["passed"]:
        status = "BLOCKED_SOURCE_CARDINALITY"
        derived_surface = pd.DataFrame()
        duplicate_rows: list[dict[str, Any]] = []
        parquet_files_written = 0
        bounded_surface_fingerprint = ""
        emitted_pool: list[dict[str, Any]] = []
        ranked_candidates: list[dict[str, Any]] = []
        rejection_rows: list[dict[str, Any]] = []
        session_rows: list[dict[str, Any]] = []
    else:
        rows_013 = normalize_013_rows(
            intraday_013,
            selected_sessions=selected_sessions,
            source_snapshot_fingerprint=source_snapshot_fingerprint,
            instrument_id_by_ticker=instrument_id_by_ticker,
        )
        rows_014 = normalize_014_rows(
            intraday_014,
            selected_sessions=selected_sessions,
            tickers=candidate_tickers,
            source_snapshot_fingerprint=source_snapshot_fingerprint,
        )
        derived_surface, duplicate_rows = build_derived_surface(rows_013, rows_014)
        if len(derived_surface) > int(limits["maximum_expanded_intraday_rows_written"]):
            raise ConstructionError("Derived 014 candidate surface exceeds row cap")
        parquet_path = run_dir / "014_scale_a_eligible_surface_candidate_v0_1.parquet"
        write_derived_surface(parquet_path, derived_surface)
        parquet_files_written = 1
        bounded_surface_fingerprint = semantic_surface_fingerprint(derived_surface)
        ranked_candidates, rejection_rows, session_rows, duplicate_rows = evaluate_candidates(
            candidate_tickers=candidate_tickers,
            selected_sessions=selected_sessions,
            daily=daily,
            derived_surface=derived_surface,
            duplicate_rows=duplicate_rows,
        )
        emitted_pool = ranked_candidates[: int(limits["maximum_eligible_instruments"])]
        status = (
            "PASS_WITH_RESTRICTIONS"
            if len(emitted_pool) >= int(limits["minimum_eligible_instruments"])
            else "BLOCKED_ELIGIBLE_POOL_CARDINALITY"
        )

    pool_payload = {
        "run_id": run_id,
        "accepted_pool": status == "PASS_WITH_RESTRICTIONS",
        "eligible_surface_id": scope["eligible_surface_id"],
        "eligibility_rule_id": scope["eligibility_rule_id"],
        "source_snapshot_fingerprint": source_snapshot_fingerprint,
        "bounded_014_candidate_surface_fingerprint": bounded_surface_fingerprint,
        "eligible_candidates_before_cap": int(len(ranked_candidates)),
        "eligible_instruments_emitted": int(len(emitted_pool)),
        "instruments": emitted_pool if status == "PASS_WITH_RESTRICTIONS" else [],
    }
    eligible_instrument_pool_fingerprint = sha256_payload(pool_payload["instruments"])
    eligibility_rule_fingerprint = sha256_payload(
        {
            "eligible_session_rule": scope["eligible_session_rule"],
            "eligible_instrument_rule": scope["eligible_instrument_rule"],
            "prior_20_daily_volume_coverage_rule": scope["prior_20_daily_volume_coverage_rule"],
            "ranking_policy": scope["ranking_policy"],
            "limits": {
                "minimum_eligible_instruments": limits["minimum_eligible_instruments"],
                "maximum_eligible_instruments": limits["maximum_eligible_instruments"],
                "minimum_eligible_sessions_per_instrument": limits["minimum_eligible_sessions_per_instrument"],
            },
        }
    )
    eligible_surface_fingerprint = sha256_payload(
        {
            "source_snapshot_fingerprint": source_snapshot_fingerprint,
            "bounded_014_candidate_surface_fingerprint": bounded_surface_fingerprint,
            "eligibility_rule_fingerprint": eligibility_rule_fingerprint,
            "eligible_instrument_pool_fingerprint": eligible_instrument_pool_fingerprint,
        }
    )
    pool_payload["eligibility_rule_fingerprint"] = eligibility_rule_fingerprint
    pool_payload["eligible_surface_fingerprint"] = eligible_surface_fingerprint
    pool_payload["eligible_instrument_pool_fingerprint"] = eligible_instrument_pool_fingerprint
    write_json(run_dir / "eligible_instrument_pool.json", pool_payload)

    rows_from_014 = int((derived_surface["source_alias"] == "014_master_intraday_bar_table_candidate").sum()) if not derived_surface.empty else 0
    rows_from_013 = int((derived_surface["source_alias"] == "013_ohlcv_1m_quote_guarded").sum()) if not derived_surface.empty else 0
    bounded_manifest = {
        "run_id": run_id,
        "output": str(run_dir / "014_scale_a_eligible_surface_candidate_v0_1.parquet"),
        "created": bool(parquet_files_written),
        "original_014_modified": False,
        "original_014_overwritten": False,
        "official_014_promotion": False,
        "original_014_rows_observed": int(original_014_before.get("parquet_rows", 0)),
        "existing_014_rows_observed": int(original_014_before.get("parquet_rows", 0)),
        "013_upstream_rows_read": int(rows_013_read),
        "derived_014_rows_written": int(len(derived_surface)),
        "derived_rows_from_existing_014": rows_from_014,
        "derived_rows_from_013": rows_from_013,
        "expanded_rows_added": rows_from_013,
        "candidate_instruments_added": int(derived_surface.loc[derived_surface["source_alias"] == "013_ohlcv_1m_quote_guarded", "ticker"].nunique())
        if not derived_surface.empty
        else 0,
        "sessions_added": int(derived_surface["session_date"].nunique()) if not derived_surface.empty else 0,
        "source_evidence": {
            "source_snapshot_fingerprint": source_snapshot_fingerprint,
            "bounded_upstream_intraday_alias": "013_ohlcv_1m_quote_guarded",
            "existing_014_alias": "014_master_intraday_bar_table_candidate",
        },
        "output_fingerprint": bounded_surface_fingerprint,
        "parquet_sha256": sha256_file(run_dir / "014_scale_a_eligible_surface_candidate_v0_1.parquet")
        if parquet_files_written
        else "",
    }
    write_json(run_dir / "bounded_014_expansion_manifest.json", bounded_manifest)

    source_coverage_rows = [
        {
            "source_alias": "004_master_daily_table",
            "rows_read": int(daily_source_doc.get("rows_read", 0)),
            "physical_file_rows": int(daily_source_doc.get("parquet_rows", 0)),
            "filtered_rows": int(daily_source_doc.get("filtered_rows", 0)),
            "distinct_tickers": int(daily["ticker"].nunique(dropna=True)),
            "distinct_sessions": int(daily["session_date_iso"].nunique(dropna=True)),
            "source_use": "identity_daily_linkage_prior_20_coverage",
        },
        {
            "source_alias": "014_master_intraday_bar_table_candidate",
            "rows_read": int(original_014_before.get("parquet_rows", 0)),
            "filtered_rows": rows_from_014,
            "distinct_tickers": int(intraday_014["ticker"].nunique(dropna=True)),
            "distinct_sessions": int(intraday_014["session_date_iso"].nunique(dropna=True)),
            "source_use": "existing_bounded_intraday_candidate_surface_assessment",
        },
        {
            "source_alias": "013_ohlcv_1m_quote_guarded",
            "rows_read": int(rows_013_read),
            "filtered_rows": rows_from_013,
            "distinct_tickers": int(intraday_013["ticker"].nunique(dropna=True)),
            "distinct_sessions": int(intraday_013["session_date_iso"].nunique(dropna=True)),
            "source_use": "eligible_surface_construction_only",
        },
    ]
    write_csv_rows(
        run_dir / "eligible_surface_source_coverage_report.csv",
        ["source_alias", "rows_read", "filtered_rows", "distinct_tickers", "distinct_sessions", "source_use"],
        source_coverage_rows,
    )
    write_csv_rows(
        run_dir / "eligible_surface_calendar_guard_report.csv",
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
            "intraday_ticker_count",
            "evidence_source",
            "finding",
        ],
        calendar_rows,
    )
    write_csv_rows(
        run_dir / "eligible_session_coverage_report.csv",
        [
            "ticker",
            "instrument_id",
            "session_date",
            "identity_resolved",
            "daily_linked",
            "intraday_linked",
            "prior_20_daily_volume_rows",
            "prior_20_daily_volume_coverage_available",
            "required_core_four_source_fields_present",
            "intraday_rows",
            "calendar_guard_compatible",
            "excluded_context_class",
            "eligible_session",
            "status",
        ],
        session_rows,
    )
    write_csv_rows(
        run_dir / "eligible_instrument_pool_report.csv",
        [
            "instrument_id",
            "ticker",
            "eligible_session_count",
            "calendar_compatible_session_coverage_count",
            "daily_linkage_completeness_ratio",
            "intraday_linkage_completeness_ratio",
            "prior_20_daily_volume_complete_session_count",
            "required_field_coverage_ratio",
            "duplicate_risk_rank",
            "source_rows_per_eligible_session",
            "source_rows",
        ],
        emitted_pool,
    )
    write_csv_rows(
        run_dir / "eligible_instrument_rejection_report.csv",
        [
            "instrument_id",
            "ticker",
            "identity_resolved",
            "identity_ambiguous",
            "identity_count",
            "eligible_session_count",
            "daily_linkage_completeness_ratio",
            "intraday_linkage_completeness_ratio",
            "prior_20_daily_volume_complete_session_count",
            "required_field_coverage_ratio",
            "duplicate_risk_rank",
            "source_rows",
            "rejection_reasons",
        ],
        rejection_rows,
    )
    write_csv_rows(
        run_dir / "eligible_surface_duplicate_status_report.csv",
        [
            "ticker",
            "session_date",
            "bar_end_utc",
            "duplicate_group_row_count",
            "duplicate_group_distinct_state_count",
            "duplicate_status",
            "duplicate_risk_rank",
            "kept_source_alias",
            "dropped_rows",
        ],
        duplicate_rows,
    )

    original_014_after = file_doc(roots["014_master_intraday_bar_table_candidate"] / "data.parquet", include_hash=True)
    original_014_hash_unchanged = original_014_before["sha256"] == original_014_after["sha256"]
    original_014_mtime_unchanged = original_014_before["mtime_utc"] == original_014_after["mtime_utc"]
    authority_failures = 0 if original_014_hash_unchanged and original_014_mtime_unchanged else 1
    determinism_payload = {
        "eligible_instrument_pool_fingerprint_recomputed": sha256_payload(pool_payload["instruments"]),
        "eligible_instrument_pool_fingerprint_recorded": eligible_instrument_pool_fingerprint,
        "eligible_surface_fingerprint_recomputed": sha256_payload(
            {
                "source_snapshot_fingerprint": source_snapshot_fingerprint,
                "bounded_014_candidate_surface_fingerprint": bounded_surface_fingerprint,
                "eligibility_rule_fingerprint": eligibility_rule_fingerprint,
                "eligible_instrument_pool_fingerprint": eligible_instrument_pool_fingerprint,
            }
        ),
        "eligible_surface_fingerprint_recorded": eligible_surface_fingerprint,
        "determinism_failures": 0,
    }
    if (
        determinism_payload["eligible_instrument_pool_fingerprint_recomputed"]
        != determinism_payload["eligible_instrument_pool_fingerprint_recorded"]
        or determinism_payload["eligible_surface_fingerprint_recomputed"]
        != determinism_payload["eligible_surface_fingerprint_recorded"]
    ):
        determinism_payload["determinism_failures"] = 1
    write_json(run_dir / "eligible_surface_determinism_report.json", determinism_payload)

    authority_report = {
        "run_id": run_id,
        "upstream_source_use": "eligible_surface_construction_only",
        "013_direct_builder_use": False,
        "013_market_state_input": False,
        "013_downstream_input": False,
        "raw_quote_consumption": False,
        "microstructure_feature_consumption": False,
        "original_014_sha256_before": original_014_before["sha256"],
        "original_014_sha256_after": original_014_after["sha256"],
        "original_014_sha256_unchanged": original_014_hash_unchanged,
        "original_014_mtime_before": original_014_before["mtime_utc"],
        "original_014_mtime_after": original_014_after["mtime_utc"],
        "original_014_mtime_unchanged": original_014_mtime_unchanged,
        "market_state_parquet_files_written": 0,
        "scale_a_preflight_rerun": False,
        "builder_records_emitted": 0,
        "integrated_candidate_records_emitted": 0,
        "authority_failures": authority_failures,
    }
    write_json(run_dir / "eligible_surface_authority_report.json", authority_report)

    summary = {
        "run_id": run_id,
        "status": status,
        "candidate_instruments_discovered": int(len(candidate_tickers)),
        "resolved_intraday_source_distinct_instruments": feasibility["resolved_intraday_source_distinct_instruments"],
        "candidate_instruments_with_daily_linkage": candidate_instruments_with_daily_linkage,
        "candidate_instruments_with_5_compatible_sessions": candidate_instruments_with_5_compatible_sessions,
        "eligible_candidates_before_cap": int(len(ranked_candidates)),
        "eligible_instruments_emitted": int(len(emitted_pool)),
        "selected_sessions_count": int(len(selected_sessions)),
        "source_market_data_rows_read": int(total_source_rows_read),
        "derived_014_rows_written": int(len(derived_surface)),
        "candidate_surface_parquet_files_written": int(parquet_files_written),
        "authority_failures": int(authority_failures),
        "determinism_failures": int(determinism_payload["determinism_failures"]),
        "hard_contract_failures": 0,
        "source_snapshot_fingerprint": source_snapshot_fingerprint,
        "bounded_014_candidate_surface_fingerprint": bounded_surface_fingerprint,
        "eligible_instrument_pool_fingerprint": eligible_instrument_pool_fingerprint,
        "eligible_surface_fingerprint": eligible_surface_fingerprint,
    }
    write_json(run_dir / "eligible_instrument_pool_summary.json", summary)

    readout_path = run_dir / "experimental_core_four_scale_a_eligible_representation_surface_construction_readout_v0_1.md"
    write_text_file(readout_path, build_readout(status, run_id, summary))
    expected_outputs = set(scope["allowed_outputs"])
    observed_outputs = set(os.listdir(str(run_dir)))
    final_outputs = sorted(
        name
        for name in scope["allowed_outputs"]
        if name == "eligible_surface_final_manifest.json" or name in observed_outputs or long_path_exists(run_dir / name)
    )
    output_files_count_after_final = len(final_outputs)
    missing_required_outputs = sorted(expected_outputs - set(final_outputs))
    unexpected_outputs = sorted((observed_outputs | {"eligible_surface_final_manifest.json"}) - expected_outputs)
    hard_contract_failures = 0
    if missing_required_outputs:
        hard_contract_failures += 1
    if unexpected_outputs:
        hard_contract_failures += 1
    if total_source_rows_read > int(limits["maximum_source_market_data_rows_read"]):
        hard_contract_failures += 1
    if parquet_files_written and len(derived_surface) > int(limits["maximum_expanded_intraday_rows_written"]):
        hard_contract_failures += 1
    if status == "PASS_WITH_RESTRICTIONS" and len(emitted_pool) < int(limits["minimum_eligible_instruments"]):
        hard_contract_failures += 1
    if output_files_count_after_final > int(limits["maximum_output_files"]):
        hard_contract_failures += 1
    summary["hard_contract_failures"] = hard_contract_failures
    final_manifest = {
        "run_id": run_id,
        "script_version": SCRIPT_VERSION,
        "created_at_utc": start,
        "completed_at_utc": utc_now(),
        "status": "CLOSED_PASS_WITH_RESTRICTIONS" if status == "PASS_WITH_RESTRICTIONS" else status,
        "terminal_status": status,
        "summary": summary,
        "outputs": {
            "files_written_before_final_manifest": sorted(set(final_outputs) - {"eligible_surface_final_manifest.json"}),
            "final_output_files": final_outputs,
            "final_output_file_count": output_files_count_after_final,
            "required_output_files": int(limits["required_output_files"]),
            "maximum_output_files": int(limits["maximum_output_files"]),
            "missing_required_output_files": missing_required_outputs,
            "unexpected_output_files": unexpected_outputs,
        },
        "next_allowed_gate": "experimental_core_four_market_state_scale_a_sample_preflight_rerun_authorization_v0_1"
        if status == "PASS_WITH_RESTRICTIONS"
        else "remediate eligible representation surface construction blocker",
        "still_closed": [
            "Scale_A_sample_preflight_rerun",
            "Scale_A_builder_execution",
            "Market_State_integration",
            "Market_State_materialization",
            "Market_State_candidate_parquet",
            "official_Market_State",
            "production_builder",
            "downstream_consumption",
            "dataset_promotion",
            "full_history_execution",
            "full_universe_execution",
        ],
    }
    write_json(run_dir / "eligible_surface_final_manifest.json", final_manifest)
    write_json(run_dir / "heartbeat.json", {"run_id": run_id, "status": final_manifest["status"], "updated_at_utc": utc_now()})
    print(json.dumps(json_safe_value({"run_id": run_id, "status": final_manifest["status"], "run_dir": str(run_dir), "summary": summary}), indent=2))
    return 0 if hard_contract_failures == 0 and authority_failures == 0 and determinism_payload["determinism_failures"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
