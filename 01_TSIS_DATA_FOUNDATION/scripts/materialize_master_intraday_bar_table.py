from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


DATASET_ID = "master_intraday_bar_table_v0_1"
SCHEMA_VERSION = "master_intraday_bar_table_v0_1"
QUALITY_POLICY_VERSION = "master_intraday_bar_table_policy_v0_1"
MATERIALIZATION_SCOPE = "scoped_split_normalized_event_cases"
PRICE_VIEWS = ("1m_raw", "1m_split_normalized")

DEFAULT_SPLIT_NORMALIZED_ROOT = Path(r"E:\TSIS\data\ohlcv_1m_split_normalized")
DEFAULT_RAW_1M_ROOT = Path(r"E:\TSIS\data\ohlcv_1m")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_CORPORATE_ACTIONS = Path(
    r"E:\TSIS\data\data_foundation_outputs\corporate_actions_table\corporate_actions_table_v0_1.parquet"
)
DEFAULT_CORPORATE_ACTIONS_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\corporate_actions_table\_corporate_actions_table_manifest_v0_1.json"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet"
)
DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\_dataset_certification_matrix_manifest_v0_1.json"
)
DEFAULT_RAW_1M_QUALITY_MANIFEST = Path(
    r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\inspection_dossiers\minute\evidence_assets\core_quality\minute_core_quality_manifest_v0_1.parquet"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\master_intraday_bar_table")


def _path_for_json(path: Path) -> str:
    return str(path).replace("\\", "/")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_parquet_tree(root: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    total_bytes = 0
    for path in files:
        rel = path.relative_to(root).as_posix()
        size = path.stat().st_size
        file_hash = _sha256(path)
        total_bytes += size
        h.update(rel.encode("utf-8"))
        h.update(str(size).encode("ascii"))
        h.update(file_hash.encode("ascii"))
    return {
        "parquet_file_count": len(files),
        "total_bytes": total_bytes,
        "tree_sha256": h.hexdigest(),
    }


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset == resolved_root:
        raise RuntimeError(f"Refusing to delete output root: {dataset_dir}")
    if "master_intraday_bar_table" not in str(resolved_dataset):
        raise RuntimeError(f"Refusing to delete suspicious dataset dir: {dataset_dir}")
    shutil.rmtree(dataset_dir)


def _session_segment(ts_utc: pd.Series) -> pd.Series:
    local = ts_utc.dt.tz_convert("America/New_York")
    minute_of_day = local.dt.hour * 60 + local.dt.minute
    return pd.Series(
        np.select(
            [
                (minute_of_day >= 4 * 60) & (minute_of_day < 9 * 60 + 30),
                (minute_of_day >= 9 * 60 + 30) & (minute_of_day < 16 * 60),
                (minute_of_day >= 16 * 60) & (minute_of_day < 20 * 60),
            ],
            ["premarket", "regular", "afterhours"],
            default="overnight_or_closed",
        ),
        index=ts_utc.index,
    )


def _price_integrity_state(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    eps = 1e-9
    values = frame[["open", "high", "low", "close"]]
    hard_invalid = (
        values.isna().any(axis=1)
        | (values <= 0).any(axis=1)
        | frame["high"].isna()
        | frame["low"].isna()
        | (frame["high"] + eps < frame["low"])
        | (frame["open"] + eps < frame["low"])
        | (frame["open"] - eps > frame["high"])
        | (frame["close"] + eps < frame["low"])
        | (frame["close"] - eps > frame["high"])
    )
    state = pd.Series(np.where(hard_invalid, "hard_invalid", "pass"), index=frame.index)
    return state, hard_invalid


def _build_ids(frame: pd.DataFrame) -> list[str]:
    return [
        hashlib.sha256(f"{ticker}|{ts}|{bar_size}|{price_view}".encode("utf-8")).hexdigest()
        for ticker, ts, bar_size, price_view in zip(
            frame["ticker"].astype(str),
            frame["ts_utc"].astype(str),
            frame["bar_size"].astype(str),
            frame["price_view"].astype(str),
            strict=True,
        )
    ]


def _read_quality_manifest(path: Path) -> pd.DataFrame:
    columns = [
        "ticker",
        "year",
        "month",
        "rows",
        "core_quality_state",
        "core_issue_family",
        "combined_quality_state",
        "allowed_consumption",
        "vw_quality_state",
        "vw_issue_family",
        "final_policy_bucket_lt1b",
        "m.negative_or_zero_ohlc_rows",
        "m.negative_volume_rows",
        "m.high_low_inversion_rows",
        "m.duplicate_ts_utc_rows",
        "m.vw_outside_range_rows",
    ]
    manifest = pd.read_parquet(path, columns=columns)
    return manifest.rename(
        columns={
            "rows": "raw_quality_manifest_rows",
            "core_quality_state": "raw_core_quality_state",
            "core_issue_family": "raw_core_issue_family",
            "combined_quality_state": "raw_combined_quality_state",
            "allowed_consumption": "raw_allowed_consumption",
            "vw_quality_state": "raw_vw_quality_state",
            "vw_issue_family": "raw_vw_issue_family",
            "final_policy_bucket_lt1b": "raw_final_policy_bucket_lt1b",
            "m.negative_or_zero_ohlc_rows": "raw_manifest_negative_or_zero_ohlc_rows",
            "m.negative_volume_rows": "raw_manifest_negative_volume_rows",
            "m.high_low_inversion_rows": "raw_manifest_high_low_inversion_rows",
            "m.duplicate_ts_utc_rows": "raw_manifest_duplicate_ts_utc_rows",
            "m.vw_outside_range_rows": "raw_manifest_vw_outside_range_rows",
        }
    )


def _read_dataset_gates(path: Path) -> pd.DataFrame:
    columns = [
        "dataset_family",
        "data_quality_verdict",
        "foundations_completion_status",
        "visual_inspection_status",
        "production_use_gate",
        "event_consumption_gate",
        "quality_policy_version",
        "build_run_id",
    ]
    gates = pd.read_parquet(path, columns=columns)
    gates = gates[gates["dataset_family"].isin(["ohlcv_1m_raw", "ohlcv_1m_split_normalized"])].copy()
    return gates.rename(
        columns={
            "data_quality_verdict": "family_data_quality_verdict",
            "foundations_completion_status": "family_foundations_completion_status",
            "visual_inspection_status": "family_visual_inspection_status",
            "production_use_gate": "family_production_use_gate",
            "event_consumption_gate": "family_event_consumption_gate",
            "quality_policy_version": "gate_quality_policy_version",
            "build_run_id": "dataset_certification_matrix_build_run_id",
        }
    )


def _read_instrument_master(path: Path, tickers: set[str]) -> pd.DataFrame:
    columns = [
        "instrument_id",
        "ticker",
        "valid_from",
        "valid_to",
        "identity_resolution_level",
        "ticker_identity_scope",
        "is_common_stock",
        "is_lt1b_operational",
        "lt1b_first_seen_date",
        "lt1b_last_observed_date",
        "lt1b_classification_1b",
        "build_run_id",
        "schema_version",
    ]
    instruments = pd.read_parquet(path, columns=columns)
    instruments = instruments[instruments["ticker"].isin(tickers)].copy()
    return instruments.rename(
        columns={
            "build_run_id": "instrument_master_build_run_id",
            "schema_version": "instrument_master_schema_version",
        }
    )


def _read_corporate_actions(path: Path, tickers: set[str]) -> pd.DataFrame:
    columns = ["ticker", "action_type", "action_date"]
    actions = pd.read_parquet(path, columns=columns)
    actions = actions[actions["ticker"].isin(tickers)].copy()
    actions["session_date"] = pd.to_datetime(actions["action_date"], errors="coerce").dt.date
    grouped = (
        actions.groupby(["ticker", "session_date"], dropna=False)
        .agg(
            corporate_action_count=("action_type", "size"),
            split_action_count=("action_type", lambda x: int((x == "split").sum())),
            dividend_action_count=("action_type", lambda x: int((x == "dividend").sum())),
            ticker_change_action_count=("action_type", lambda x: int((x == "ticker_change").sum())),
        )
        .reset_index()
    )
    return grouped


def _source_files(split_normalized_root: Path) -> list[Path]:
    files = sorted(split_normalized_root.rglob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No split-normalized parquet files found under {split_normalized_root}")
    return files


def _base_frame(
    split_files: list[Path],
    instrument_master: pd.DataFrame,
    quality_manifest: pd.DataFrame,
    corporate_actions: pd.DataFrame,
) -> pd.DataFrame:
    frames = []
    for path in split_files:
        frame = pd.read_parquet(path)
        frame["source_split_normalized_file"] = _path_for_json(path)
        frames.append(frame)

    base = pd.concat(frames, ignore_index=True)
    base["ticker"] = base["ticker"].astype(str).str.upper()
    base["year"] = base["year"].astype("int32")
    base["month"] = base["month"].astype("int8")
    base["ts_utc"] = pd.to_datetime(base["ts_utc"], utc=True, errors="raise")
    base["session_date"] = pd.to_datetime(base["date"], errors="raise").dt.date
    base["session_segment"] = _session_segment(base["ts_utc"])
    base["pilot_event_date"] = pd.to_datetime(base["pilot_event_date"], errors="coerce").dt.date

    base = base.merge(instrument_master, on="ticker", how="left", validate="many_to_one")
    base = base.merge(quality_manifest, on=["ticker", "year", "month"], how="left", validate="many_to_one")
    base["raw_quality_manifest_present"] = base["raw_allowed_consumption"].notna()
    base = base.merge(corporate_actions, on=["ticker", "session_date"], how="left", validate="many_to_one")

    count_cols = [
        "corporate_action_count",
        "split_action_count",
        "dividend_action_count",
        "ticker_change_action_count",
    ]
    base[count_cols] = base[count_cols].fillna(0).astype("int32")
    base["has_split_action"] = base["split_action_count"] > 0
    base["has_dividend_action"] = base["dividend_action_count"] > 0
    base["has_ticker_change_action"] = base["ticker_change_action_count"] > 0
    base["has_any_corporate_action"] = base["corporate_action_count"] > 0

    return base


def _price_view_frame(
    base: pd.DataFrame,
    price_view: str,
    split_normalized_root: Path,
    raw_1m_root: Path,
    gates: pd.DataFrame,
    build_run_id: str,
    created_at_utc: str,
) -> pd.DataFrame:
    if price_view == "1m_raw":
        selected = pd.DataFrame(
            {
                "open": base["o"],
                "high": base["h"],
                "low": base["l"],
                "close": base["c"],
                "vwap": base["vw"],
                "source_dataset": "ohlcv_1m_raw_v0_1",
                "quality_gate_family": "ohlcv_1m_raw",
                "source_root": _path_for_json(raw_1m_root),
                "source_file": base["source_1m_file"],
            }
        )
    elif price_view == "1m_split_normalized":
        selected = pd.DataFrame(
            {
                "open": base["o_split_normalized"],
                "high": base["h_split_normalized"],
                "low": base["l_split_normalized"],
                "close": base["c_split_normalized"],
                "vwap": base["vw_split_normalized"],
                "source_dataset": "ohlcv_1m_split_normalized_v0_1",
                "quality_gate_family": "ohlcv_1m_split_normalized",
                "source_root": _path_for_json(split_normalized_root),
                "source_file": base["source_split_normalized_file"],
            }
        )
    else:
        raise ValueError(f"Unsupported price view: {price_view}")

    frame = pd.concat([base.reset_index(drop=True), selected.reset_index(drop=True)], axis=1)
    frame["price_view"] = price_view
    frame["bar_size"] = "1m"
    frame["volume"] = frame["v"].astype("float64")
    frame["transaction_count"] = frame["n"].astype("Int64")
    frame["source_t_epoch_ms"] = frame["t"].astype("Int64")
    frame["source_raw_open"] = frame["o"]
    frame["source_raw_high"] = frame["h"]
    frame["source_raw_low"] = frame["l"]
    frame["source_raw_close"] = frame["c"]
    frame["source_raw_vwap"] = frame["vw"]
    frame["source_raw_volume"] = frame["v"]
    frame["source_raw_transaction_count"] = frame["n"].astype("Int64")
    frame["materialized_source_price_view"] = frame["materialized_price_view"]
    frame["source_1m_file_reported"] = frame["source_1m_file"]

    gate = gates.set_index("dataset_family").loc[frame["quality_gate_family"].iloc[0]]
    for column, value in gate.items():
        if column != "dataset_family":
            frame[column] = value

    row_state, hard_invalid = _price_integrity_state(frame)
    frame["row_level_price_integrity_state"] = row_state
    frame["selected_price_hard_invalid"] = hard_invalid
    frame["negative_volume"] = frame["volume"].fillna(0) < 0
    frame["core_ohlcv_consumption_allowed"] = (
        frame["raw_allowed_consumption"].isin(["controlled_ohlcv_research", "ohlcv_without_vw_only"])
        & ~frame["selected_price_hard_invalid"]
        & ~frame["negative_volume"]
        & frame["raw_quality_manifest_present"]
    )
    frame["vwap_consumption_allowed"] = (
        frame["raw_allowed_consumption"].eq("controlled_ohlcv_research")
        & frame["raw_vw_quality_state"].isin(["good", "review"])
        & frame["vwap"].notna()
    )
    frame["vwap_consumption_state"] = np.select(
        [
            frame["vwap"].isna(),
            frame["vwap_consumption_allowed"],
            frame["raw_vw_quality_state"].eq("bad"),
            ~frame["raw_quality_manifest_present"],
        ],
        ["missing", "allowed_with_declared_vw_policy", "blocked_by_raw_vw_quality", "raw_quality_unknown"],
        default="restricted_by_policy",
    )
    frame["event_research_bar_candidate"] = (
        frame["core_ohlcv_consumption_allowed"]
        & frame["family_event_consumption_gate"].eq("allowed_with_scope_flags")
    )
    frame["backtest_core_bar_candidate"] = False
    frame["full_universe_claim"] = False
    frame["materialization_scope"] = MATERIALIZATION_SCOPE
    frame["quality_policy_version"] = QUALITY_POLICY_VERSION
    frame["schema_version"] = SCHEMA_VERSION
    frame["build_run_id"] = build_run_id
    frame["created_at_utc"] = created_at_utc

    output_columns = [
        "ticker",
        "instrument_id",
        "ts_utc",
        "session_date",
        "year",
        "month",
        "bar_size",
        "price_view",
        "quality_gate_family",
        "source_dataset",
        "source_root",
        "source_file",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "transaction_count",
        "source_t_epoch_ms",
        "source_raw_open",
        "source_raw_high",
        "source_raw_low",
        "source_raw_close",
        "source_raw_vwap",
        "source_raw_volume",
        "source_raw_transaction_count",
        "future_split_factor",
        "o_split_normalized",
        "h_split_normalized",
        "l_split_normalized",
        "c_split_normalized",
        "vw_split_normalized",
        "materialized_source_price_view",
        "source_1m_file_reported",
        "source_splits_file",
        "source_split_normalized_file",
        "pilot_role",
        "pilot_event_type",
        "pilot_event_date",
        "session_segment",
        "raw_quality_manifest_present",
        "raw_quality_manifest_rows",
        "raw_core_quality_state",
        "raw_core_issue_family",
        "raw_combined_quality_state",
        "raw_allowed_consumption",
        "raw_vw_quality_state",
        "raw_vw_issue_family",
        "raw_final_policy_bucket_lt1b",
        "raw_manifest_negative_or_zero_ohlc_rows",
        "raw_manifest_negative_volume_rows",
        "raw_manifest_high_low_inversion_rows",
        "raw_manifest_duplicate_ts_utc_rows",
        "raw_manifest_vw_outside_range_rows",
        "corporate_action_count",
        "split_action_count",
        "dividend_action_count",
        "ticker_change_action_count",
        "has_split_action",
        "has_dividend_action",
        "has_ticker_change_action",
        "has_any_corporate_action",
        "row_level_price_integrity_state",
        "selected_price_hard_invalid",
        "negative_volume",
        "core_ohlcv_consumption_allowed",
        "vwap_consumption_allowed",
        "vwap_consumption_state",
        "event_research_bar_candidate",
        "backtest_core_bar_candidate",
        "full_universe_claim",
        "materialization_scope",
        "family_data_quality_verdict",
        "family_foundations_completion_status",
        "family_visual_inspection_status",
        "family_production_use_gate",
        "family_event_consumption_gate",
        "gate_quality_policy_version",
        "dataset_certification_matrix_build_run_id",
        "instrument_master_build_run_id",
        "instrument_master_schema_version",
        "quality_policy_version",
        "schema_version",
        "build_run_id",
        "created_at_utc",
    ]
    frame = frame[output_columns].copy()
    frame.insert(0, "master_intraday_bar_id", _build_ids(frame))
    return frame


def materialize_master_intraday_bar_table(
    split_normalized_root: Path,
    raw_1m_root: Path,
    instrument_master: Path,
    corporate_actions: Path,
    corporate_actions_manifest: Path,
    dataset_certification_matrix: Path,
    dataset_certification_matrix_manifest: Path,
    raw_1m_quality_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(split_normalized_root, "split-normalized 1m root")
    _require(raw_1m_root, "raw 1m root")
    _require(instrument_master, "instrument master")
    _require(corporate_actions, "corporate actions table")
    corporate_manifest = _load_manifest(corporate_actions_manifest)
    _require(dataset_certification_matrix, "dataset certification matrix")
    dcm_manifest = _load_manifest(dataset_certification_matrix_manifest)
    _require(raw_1m_quality_manifest, "raw 1m quality manifest")

    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / DATASET_ID
    summary_path = output_root / f"_{DATASET_ID.replace('_v0_1', '')}_summary_v0_1.csv"
    manifest_path = output_root / f"_{DATASET_ID.replace('_v0_1', '')}_manifest_v0_1.json"

    if dataset_dir.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {dataset_dir}")
        _safe_remove_dataset_dir(dataset_dir, output_root)

    split_files = _source_files(split_normalized_root)
    tickers = {path.parts[[part.startswith("ticker=") for part in path.parts].index(True)].split("=", 1)[1] for path in split_files}

    build_run_id = datetime.now(timezone.utc).strftime("master_intraday_bar_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    instruments = _read_instrument_master(instrument_master, tickers)
    quality = _read_quality_manifest(raw_1m_quality_manifest)
    actions = _read_corporate_actions(corporate_actions, tickers)
    gates = _read_dataset_gates(dataset_certification_matrix)
    base = _base_frame(split_files, instruments, quality, actions)

    frames = [
        _price_view_frame(
            base=base,
            price_view=price_view,
            split_normalized_root=split_normalized_root,
            raw_1m_root=raw_1m_root,
            gates=gates,
            build_run_id=build_run_id,
            created_at_utc=created_at_utc,
        )
        for price_view in PRICE_VIEWS
    ]
    output = pd.concat(frames, ignore_index=True)
    output["month"] = output["month"].astype("int8")
    output["year"] = output["year"].astype("int32")

    table = pa.Table.from_pandas(output, preserve_index=False)
    pq.write_to_dataset(
        table,
        root_path=dataset_dir,
        partition_cols=["year", "month", "price_view"],
        compression="zstd",
        use_dictionary=True,
    )

    summary = (
        output.groupby("price_view", dropna=False)
        .agg(
            rows=("master_intraday_bar_id", "size"),
            tickers=("ticker", "nunique"),
            first_ts_utc=("ts_utc", "min"),
            last_ts_utc=("ts_utc", "max"),
            hard_invalid_rows=("selected_price_hard_invalid", "sum"),
            negative_volume_rows=("negative_volume", "sum"),
            event_research_bar_candidate_rows=("event_research_bar_candidate", "sum"),
            backtest_core_bar_candidate_rows=("backtest_core_bar_candidate", "sum"),
            raw_quality_manifest_missing_rows=("raw_quality_manifest_present", lambda x: int((~x).sum())),
            vwap_blocked_rows=("vwap_consumption_state", lambda x: int((x == "blocked_by_raw_vw_quality").sum())),
            rows_with_corporate_action=("has_any_corporate_action", "sum"),
        )
        .reset_index()
    )
    summary.to_csv(summary_path, index=False)

    duplicate_key_groups = int(
        output.groupby(["ticker", "ts_utc", "bar_size", "price_view"], dropna=False)
        .size()
        .gt(1)
        .sum()
    )
    source_rows = int(len(base))
    rows_by_view = {
        row["price_view"]: {
            "rows": int(row["rows"]),
            "hard_invalid_rows": int(row["hard_invalid_rows"]),
            "negative_volume_rows": int(row["negative_volume_rows"]),
            "event_research_bar_candidate_rows": int(row["event_research_bar_candidate_rows"]),
            "backtest_core_bar_candidate_rows": int(row["backtest_core_bar_candidate_rows"]),
            "raw_quality_manifest_missing_rows": int(row["raw_quality_manifest_missing_rows"]),
            "vwap_blocked_rows": int(row["vwap_blocked_rows"]),
            "rows_with_corporate_action": int(row["rows_with_corporate_action"]),
        }
        for _, row in summary.iterrows()
    }
    output_tree = _sha256_parquet_tree(dataset_dir)
    split_tree = _sha256_parquet_tree(split_normalized_root)
    hard_fail_count = int(
        duplicate_key_groups > 0
        or source_rows == 0
        or len(output) != source_rows * len(PRICE_VIEWS)
        or output["selected_price_hard_invalid"].sum() > 0
        or output["negative_volume"].sum() > 0
        or output["full_universe_claim"].any()
    )

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "full_universe_claim": False,
        "output_path": _path_for_json(dataset_dir),
        "summary_path": _path_for_json(summary_path),
        "manifest_path": _path_for_json(manifest_path),
        "output_tree": output_tree,
        "source_split_normalized_root": _path_for_json(split_normalized_root),
        "source_split_normalized_tree": split_tree,
        "source_raw_1m_root": _path_for_json(raw_1m_root),
        "source_instrument_master": _path_for_json(instrument_master),
        "source_instrument_master_sha256": _sha256(instrument_master),
        "source_corporate_actions": _path_for_json(corporate_actions),
        "source_corporate_actions_sha256": _sha256(corporate_actions),
        "source_corporate_actions_build_run_id": corporate_manifest.get("build_run_id"),
        "source_dataset_certification_matrix": _path_for_json(dataset_certification_matrix),
        "source_dataset_certification_matrix_sha256": _sha256(dataset_certification_matrix),
        "source_dataset_certification_matrix_build_run_id": dcm_manifest.get("build_run_id"),
        "source_raw_1m_quality_manifest": _path_for_json(raw_1m_quality_manifest),
        "source_raw_1m_quality_manifest_sha256": _sha256(raw_1m_quality_manifest),
        "source_price_views": list(PRICE_VIEWS),
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "validations": {
            "row_count": int(len(output)),
            "source_split_normalized_bar_rows": source_rows,
            "expected_rows_from_source_price_views": source_rows * len(PRICE_VIEWS),
            "ticker_count": int(output["ticker"].nunique()),
            "ticker_month_count": int(base[["ticker", "year", "month"]].drop_duplicates().shape[0]),
            "price_view_count": int(output["price_view"].nunique()),
            "first_ts_utc": str(output["ts_utc"].min()),
            "last_ts_utc": str(output["ts_utc"].max()),
            "duplicate_key_groups": duplicate_key_groups,
            "selected_price_hard_invalid_rows": int(output["selected_price_hard_invalid"].sum()),
            "negative_volume_rows": int(output["negative_volume"].sum()),
            "event_research_bar_candidate_rows": int(output["event_research_bar_candidate"].sum()),
            "backtest_core_bar_candidate_rows": int(output["backtest_core_bar_candidate"].sum()),
            "raw_quality_manifest_missing_rows": int((~output["raw_quality_manifest_present"]).sum()),
            "raw_quality_manifest_missing_ticker_months": int(
                base.loc[~base["raw_quality_manifest_present"], ["ticker", "year", "month"]]
                .drop_duplicates()
                .shape[0]
            ),
            "rows_by_price_view": rows_by_view,
            "hard_fail_count": hard_fail_count,
        },
        "contracts": {
            "canonical_schema": "01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md",
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md",
            "consumption_policy": "01_foundations/data_consumption_policies/master_intraday_bar_table_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/master_intraday_bar_table_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/master_intraday_bar_table_validators.md",
            "output_target_contract": "01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize master_intraday_bar_table_v0_1.")
    parser.add_argument("--split-normalized-root", type=Path, default=DEFAULT_SPLIT_NORMALIZED_ROOT)
    parser.add_argument("--raw-1m-root", type=Path, default=DEFAULT_RAW_1M_ROOT)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--corporate-actions", type=Path, default=DEFAULT_CORPORATE_ACTIONS)
    parser.add_argument("--corporate-actions-manifest", type=Path, default=DEFAULT_CORPORATE_ACTIONS_MANIFEST)
    parser.add_argument("--dataset-certification-matrix", type=Path, default=DEFAULT_DATASET_CERTIFICATION_MATRIX)
    parser.add_argument(
        "--dataset-certification-matrix-manifest",
        type=Path,
        default=DEFAULT_DATASET_CERTIFICATION_MATRIX_MANIFEST,
    )
    parser.add_argument("--raw-1m-quality-manifest", type=Path, default=DEFAULT_RAW_1M_QUALITY_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = materialize_master_intraday_bar_table(
        split_normalized_root=args.split_normalized_root,
        raw_1m_root=args.raw_1m_root,
        instrument_master=args.instrument_master,
        corporate_actions=args.corporate_actions,
        corporate_actions_manifest=args.corporate_actions_manifest,
        dataset_certification_matrix=args.dataset_certification_matrix,
        dataset_certification_matrix_manifest=args.dataset_certification_matrix_manifest,
        raw_1m_quality_manifest=args.raw_1m_quality_manifest,
        output_root=args.output_root,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest["validations"], indent=2))
    print(f"Wrote {manifest['output_path']}")


if __name__ == "__main__":
    main()
