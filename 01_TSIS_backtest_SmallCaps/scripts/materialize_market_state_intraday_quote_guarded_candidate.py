from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "market_state_table_v0_1_candidate"
PHYSICAL_DATASET_ID = "market_state_table_v0_1_candidate_intraday_quote_guarded_controlled"
STATE_SCHEMA_VERSION = "market_state_table_v0_1"
BUILDER_VERSION = "market_state_intraday_quote_guarded_builder_candidate_v0_1"
SOURCE_CUTOFF_POLICY_VERSION = "state_decision_timestamp_policy_v0_1"
LEAKAGE_POLICY_VERSION = "market_state_leakage_policy_v0_1_candidate"
FEATURE_NAMESPACE_VERSION = "market_state_feature_namespaces_v0_1_candidate"
CANDIDATE_SCOPE = "intraday_quote_guarded_scoped_candidate"
CANDIDATE_STATUS = "controlled_candidate_not_promoted"

DEFAULT_INTRADAY_PARQUET = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet"
)
DEFAULT_INTRADAY_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1"
)
MANIFEST_NAME = "_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json"
SUMMARY_NAME = "_market_state_table_summary_v0_1_candidate_intraday_quote_guarded_controlled.csv"

REQUIRED_INTRADAY_COLUMNS = {
    "master_intraday_bar_id",
    "dataset_id",
    "physical_dataset_id",
    "ticker",
    "instrument_id",
    "ts_utc",
    "session_date",
    "bar_size",
    "price_view",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "transaction_count",
    "quote_guarded_view",
    "quote_guarded_repair_applied",
    "repair_manifest_row_present",
    "repair_state",
    "repair_reason",
    "vw_quote_guarded_status",
    "quote_count",
    "source_quote_guarded_repair_manifest",
    "source_repair_shard_path",
    "source_quote_guarded_run_id",
    "source_quotes_root_state",
    "source_ohlcv_path",
    "source_quotes_path",
    "raw_ohlc_matches_manifest",
    "qg_ohlc_changed",
    "manifest_qg_ohlc_differs_from_raw",
    "manifest_qg_diff_not_applied",
    "vwap_consumption_state",
    "full_universe_claim",
    "execution_truth",
    "valid_for_ml_feature_candidate",
    "valid_for_rl_state_component_candidate",
    "schema_version",
    "quality_policy_version",
}

PROHIBITED_PREFIXES = (
    "outcome__",
    "label__",
    "reward__",
    "action__",
    "policy__",
    "fill__",
    "pnl__",
    "future__",
    "strategy__",
    "signal__",
)

COMPONENT_STATES = {
    "identity": "missing_optional",
    "calendar": "included_good",
    "scanner": "not_requested",
    "daily": "not_requested",
    "intraday": "included_good",
    "microstructure": "not_requested",
    "halt": "not_requested",
    "fundamentals": "not_requested",
    "news": "not_requested",
    "short_context": "not_requested",
    "short_constraints": "not_requested",
    "regime": "not_requested",
    "quality": "included_good",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "market_state_intraday_quote_guarded_candidate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_parquet_tree(root: Path) -> dict[str, Any]:
    files = sorted(path for path in root.rglob("*.parquet") if path.is_file())
    file_hashes: list[dict[str, Any]] = []
    tree = hashlib.sha256()
    for path in files:
        rel = path.relative_to(root).as_posix()
        digest = _sha256_file(path)
        tree.update(rel.encode("utf-8"))
        tree.update(digest.encode("utf-8"))
        file_hashes.append({"relative_path": rel, "sha256": digest, "bytes": path.stat().st_size})
    return {"file_count": len(file_hashes), "tree_sha256": tree.hexdigest(), "files": file_hashes}


def _stable_id(*parts: Any, length: int = 24) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _json_bundle(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)


def _to_utc_timestamp(value: Any) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _iso_z(value: Any) -> str:
    return _to_utc_timestamp(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _nullable_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def _nullable_int(value: Any) -> int | None:
    if pd.isna(value):
        return None
    return int(value)


def _nullable_string(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value)
    return text if text else None


def _safe_remove_dataset_dir(dataset_dir: Path, output_root: Path) -> None:
    resolved_dataset = dataset_dir.resolve()
    resolved_root = output_root.resolve()
    if resolved_dataset != resolved_root and resolved_root not in resolved_dataset.parents:
        raise RuntimeError(f"refusing to delete outside output root: {resolved_dataset}")
    shutil.rmtree(resolved_dataset)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_intraday_frame(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    missing = sorted(REQUIRED_INTRADAY_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"intraday candidate missing required columns: {missing}")
    frame = frame[frame["price_view"].astype(str) == "1m_quote_guarded_raw"].copy()
    if frame.empty:
        raise ValueError("intraday candidate has no 1m_quote_guarded_raw rows")
    frame["_bar_start_utc"] = pd.to_datetime(frame["ts_utc"], utc=True)
    frame["_bar_end_utc"] = frame["_bar_start_utc"] + pd.Timedelta(minutes=1)
    return frame.sort_values(["ticker", "_bar_start_utc", "master_intraday_bar_id"]).reset_index(drop=True)


def _state_quality(row: pd.Series) -> str:
    if pd.isna(row.get("_bar_end_utc")):
        return "state_bad_missing_decision_timestamp"
    if bool(row.get("full_universe_claim", False)):
        return "state_blocked_invalid_component_quality"
    return "state_review_scoped_intraday_component"


def _build_state_rows(
    intraday: pd.DataFrame,
    *,
    intraday_manifest: dict[str, Any],
    intraday_manifest_path: Path,
    intraday_manifest_sha256: str,
    intraday_parquet_path: Path,
    intraday_parquet_sha256: str,
    build_run_id: str,
    created_at_utc: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    component_quality = {
        "source_intraday_dataset_id": intraday_manifest.get("dataset_id"),
        "source_intraday_physical_dataset_id": intraday_manifest.get("physical_dataset_id"),
        "source_intraday_status": intraday_manifest.get("status"),
        "source_intraday_materialization_scope": intraday_manifest.get("materialization_scope"),
        "source_intraday_full_universe_claim": intraday_manifest.get("full_universe_claim"),
        "source_intraday_validator_status": intraday_manifest.get("validations", {}).get("validator_status"),
    }
    component_hashes = {
        "intraday_parquet_sha256": intraday_parquet_sha256,
        "intraday_manifest_sha256": intraday_manifest_sha256,
    }
    component_build_runs = {"intraday_build_run_id": intraday_manifest.get("build_run_id")}
    for item in intraday.to_dict(orient="records"):
        bar_start = _to_utc_timestamp(item["_bar_start_utc"])
        decision_ts = _to_utc_timestamp(item["_bar_end_utc"])
        decision_iso = _iso_z(decision_ts)
        bar_start_iso = _iso_z(bar_start)
        ticker = str(item["ticker"]).upper().strip()
        source_instrument_id = _nullable_string(item.get("instrument_id"))
        instrument_id = source_instrument_id or f"ticker:{ticker}"
        market_state_id = "market_state_" + _stable_id(
            DATASET_ID,
            item["master_intraday_bar_id"],
            ticker,
            decision_iso,
            "closed_1m_bar",
            STATE_SCHEMA_VERSION,
        )
        output: dict[str, Any] = {
            "market_state_id": market_state_id,
            "source_master_intraday_bar_id": item["master_intraday_bar_id"],
            "instrument_id": instrument_id,
            "ticker": ticker,
            "decision_timestamp_utc": decision_iso,
            "decision_date": decision_ts.date().isoformat(),
            "decision_session_date": str(item["session_date"]),
            "state_horizon": "closed_1m_bar",
            "state_scope": CANDIDATE_SCOPE,
            "state_schema_version": STATE_SCHEMA_VERSION,
            "state_builder_version": BUILDER_VERSION,
            "state_quality_state": _state_quality(pd.Series(item)),
            "build_run_id": build_run_id,
            "created_at_utc": created_at_utc,
            "source_cutoff_policy_version": SOURCE_CUTOFF_POLICY_VERSION,
            "leakage_policy_version": LEAKAGE_POLICY_VERSION,
            "feature_namespace_version": FEATURE_NAMESPACE_VERSION,
            "component_manifest_hash_bundle": _json_bundle(component_hashes),
            "component_build_run_id_bundle": _json_bundle(component_build_runs),
            "component_quality_bundle": _json_bundle(component_quality),
            "component_availability_bundle": _json_bundle(COMPONENT_STATES),
            "valid_for_event_context_candidate": False,
            "valid_for_ml_feature_candidate": False,
            "valid_for_backtest_context_candidate": False,
            "valid_for_rl_state_candidate": False,
            "valid_for_rl_training_direct": False,
            "valid_for_execution_simulator_direct": False,
            "contains_future_information_without_event_filter": False,
            "requires_asof_filter": True,
            "full_universe_claim": False,
            "execution_truth": False,
            "identity_component_state": COMPONENT_STATES["identity"],
            "calendar_component_state": COMPONENT_STATES["calendar"],
            "scanner_component_state": COMPONENT_STATES["scanner"],
            "daily_component_state": COMPONENT_STATES["daily"],
            "intraday_component_state": COMPONENT_STATES["intraday"],
            "microstructure_component_state": COMPONENT_STATES["microstructure"],
            "halt_component_state": COMPONENT_STATES["halt"],
            "fundamentals_component_state": COMPONENT_STATES["fundamentals"],
            "news_component_state": COMPONENT_STATES["news"],
            "short_context_component_state": COMPONENT_STATES["short_context"],
            "short_constraints_component_state": COMPONENT_STATES["short_constraints"],
            "regime_component_state": COMPONENT_STATES["regime"],
            "quality_component_state": COMPONENT_STATES["quality"],
            "identity_as_of_utc": None,
            "calendar_as_of_utc": decision_iso,
            "scanner_as_of_utc": None,
            "daily_as_of_utc": None,
            "intraday_as_of_utc": decision_iso,
            "microstructure_as_of_utc": None,
            "halt_as_of_utc": None,
            "fundamentals_as_of_utc": None,
            "news_as_of_utc": None,
            "short_context_as_of_utc": None,
            "short_constraints_as_of_utc": None,
            "regime_as_of_utc": None,
            "identity__instrument_id_source": (
                "source_intraday_instrument_id" if source_instrument_id else "ticker_fallback_from_intraday_candidate"
            ),
            "calendar__session_date": str(item["session_date"]),
            "calendar__bar_start_utc": bar_start_iso,
            "calendar__bar_end_utc": decision_iso,
            "intraday__source_master_intraday_bar_id": item["master_intraday_bar_id"],
            "intraday__source_intraday_dataset_id": item.get("dataset_id"),
            "intraday__source_physical_dataset_id": item.get("physical_dataset_id"),
            "intraday__bar_start_utc": bar_start_iso,
            "intraday__bar_end_utc": decision_iso,
            "intraday__bar_size": item.get("bar_size"),
            "intraday__price_view": item.get("price_view"),
            "intraday__last_closed_bar_open": float(item["open"]),
            "intraday__last_closed_bar_high": float(item["high"]),
            "intraday__last_closed_bar_low": float(item["low"]),
            "intraday__last_closed_bar_close": float(item["close"]),
            "intraday__last_closed_bar_volume": float(item["volume"]),
            "intraday__last_closed_bar_vwap": _nullable_float(item.get("vwap")),
            "intraday__last_closed_bar_transaction_count": _nullable_int(item.get("transaction_count")),
            "intraday__quote_guarded_view": item.get("quote_guarded_view"),
            "intraday__quote_guarded_repair_applied": _bool(item.get("quote_guarded_repair_applied")),
            "intraday__repair_manifest_row_present": _bool(item.get("repair_manifest_row_present")),
            "intraday__repair_state": item.get("repair_state"),
            "intraday__repair_reason": item.get("repair_reason"),
            "intraday__vw_quote_guarded_status": item.get("vw_quote_guarded_status"),
            "intraday__quote_count": _nullable_int(item.get("quote_count")),
            "intraday__raw_ohlc_matches_manifest": _bool(item.get("raw_ohlc_matches_manifest")),
            "intraday__qg_ohlc_changed": _bool(item.get("qg_ohlc_changed")),
            "intraday__manifest_qg_ohlc_differs_from_raw": _bool(
                item.get("manifest_qg_ohlc_differs_from_raw")
            ),
            "intraday__manifest_qg_diff_not_applied": _bool(item.get("manifest_qg_diff_not_applied")),
            "intraday__vwap_consumption_state": item.get("vwap_consumption_state"),
            "quality__candidate_dataset_id": DATASET_ID,
            "quality__candidate_materialization_scope": CANDIDATE_SCOPE,
            "quality__state_output_promoted": False,
            "quality__source_intraday_manifest": intraday_manifest_path.as_posix(),
            "quality__source_intraday_manifest_sha256": intraday_manifest_sha256,
            "quality__source_intraday_parquet": intraday_parquet_path.as_posix(),
            "quality__source_intraday_parquet_sha256": intraday_parquet_sha256,
            "quality__source_ohlcv_path": item.get("source_ohlcv_path"),
            "quality__source_quotes_path": _nullable_string(item.get("source_quotes_path")),
            "quality__source_repair_shard_path": _nullable_string(item.get("source_repair_shard_path")),
            "quality__source_quote_guarded_repair_manifest": item.get(
                "source_quote_guarded_repair_manifest"
            ),
            "quality__source_quote_guarded_run_id": _nullable_string(item.get("source_quote_guarded_run_id")),
            "quality__source_quotes_root_state": item.get("source_quotes_root_state"),
            "quality__intraday_quality_policy_version": item.get("quality_policy_version"),
            "quality__full_universe_claim": False,
        }
        rows.append(output)
    return pd.DataFrame(rows)


def _write_partitioned(frame: pd.DataFrame, dataset_dir: Path) -> None:
    frame = frame.copy()
    decision_ts = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    frame["decision_year"] = decision_ts.dt.year
    frame["decision_month"] = decision_ts.dt.month
    frame.to_parquet(dataset_dir, index=False, partition_cols=["decision_year", "decision_month"])


def _validate_frame(frame: pd.DataFrame, source_intraday: pd.DataFrame) -> dict[str, Any]:
    hard_failures: list[str] = []
    prohibited_columns = [
        column for column in frame.columns for prefix in PROHIBITED_PREFIXES if column.startswith(prefix)
    ]
    duplicate_state_ids = int(frame["market_state_id"].duplicated().sum())
    if prohibited_columns:
        hard_failures.append("prohibited_column_prefix_present")
    if duplicate_state_ids:
        hard_failures.append("duplicate_market_state_id")
    if bool(frame["full_universe_claim"].any()):
        hard_failures.append("full_universe_claim_rows_present")
    if bool(frame["valid_for_ml_feature_candidate"].any()) or bool(frame["valid_for_rl_state_candidate"].any()):
        hard_failures.append("ml_or_rl_candidate_rows_present")
    if bool(frame["execution_truth"].any()):
        hard_failures.append("execution_truth_rows_present")

    decision_ts = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    intraday_as_of = pd.to_datetime(frame["intraday_as_of_utc"], utc=True)
    bar_end = pd.to_datetime(frame["intraday__bar_end_utc"], utc=True)
    as_of_violation_rows = int((intraday_as_of > decision_ts).sum())
    bar_end_mismatch_rows = int((bar_end != decision_ts).sum())
    expected_rows = int(len(source_intraday))

    if as_of_violation_rows:
        hard_failures.append("intraday_as_of_after_decision_timestamp")
    if bar_end_mismatch_rows:
        hard_failures.append("bar_end_not_equal_decision_timestamp")
    if int(len(frame)) != expected_rows:
        hard_failures.append("state_rows_not_equal_quote_guarded_intraday_rows")
    if set(frame["intraday__price_view"].astype(str).unique()) != {"1m_quote_guarded_raw"}:
        hard_failures.append("unexpected_intraday_price_view")
    if not bool((frame["intraday_component_state"] == "included_good").all()):
        hard_failures.append("intraday_component_state_not_included_good")

    return {
        "source_quote_guarded_intraday_rows": expected_rows,
        "state_rows": int(len(frame)),
        "ticker_count": int(frame["ticker"].nunique()),
        "duplicate_state_id_rows": duplicate_state_ids,
        "prohibited_column_count": len(prohibited_columns),
        "prohibited_columns": prohibited_columns,
        "full_universe_claim_rows": int(frame["full_universe_claim"].sum()),
        "ml_candidate_rows": int(frame["valid_for_ml_feature_candidate"].sum()),
        "rl_candidate_rows": int(frame["valid_for_rl_state_candidate"].sum()),
        "execution_truth_rows": int(frame["execution_truth"].sum()),
        "intraday_as_of_after_decision_rows": as_of_violation_rows,
        "bar_end_decision_timestamp_mismatch_rows": bar_end_mismatch_rows,
        "quote_guarded_repair_applied_rows": int(frame["intraday__quote_guarded_repair_applied"].sum()),
        "qg_ohlc_changed_rows": int(frame["intraday__qg_ohlc_changed"].sum()),
        "manifest_qg_diff_not_applied_rows": int(frame["intraday__manifest_qg_diff_not_applied"].sum()),
        "state_quality_counts": {
            str(key): int(value) for key, value in frame["state_quality_state"].value_counts().sort_index().items()
        },
        "validator_status": "passed" if not hard_failures else "failed",
        "validator_hard_fail_count": len(hard_failures),
        "validator_hard_failures": hard_failures,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    for label, path in {"intraday parquet": args.intraday_parquet, "intraday manifest": args.intraday_manifest}.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing {label}: {path}")

    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dir = output_root / args.physical_dataset_id
    manifest_path = output_root / MANIFEST_NAME
    summary_path = output_root / SUMMARY_NAME
    if dataset_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"output exists; pass --overwrite: {dataset_dir}")
        _safe_remove_dataset_dir(dataset_dir, output_root)

    created_at_utc = args.created_at_utc or _utc_now()
    build_run_id = args.run_id or _run_id()
    intraday_manifest = _read_json(args.intraday_manifest)
    intraday_manifest_sha = _sha256_file(args.intraday_manifest)
    intraday_parquet_sha = _sha256_file(args.intraday_parquet)
    intraday = _load_intraday_frame(args.intraday_parquet)
    state_frame = _build_state_rows(
        intraday,
        intraday_manifest=intraday_manifest,
        intraday_manifest_path=args.intraday_manifest,
        intraday_manifest_sha256=intraday_manifest_sha,
        intraday_parquet_path=args.intraday_parquet,
        intraday_parquet_sha256=intraday_parquet_sha,
        build_run_id=build_run_id,
        created_at_utc=created_at_utc,
    )
    validations = _validate_frame(state_frame, intraday)
    _write_partitioned(state_frame, dataset_dir)
    output_tree = _sha256_parquet_tree(dataset_dir)
    validations["output_tree_sha256"] = output_tree["tree_sha256"]

    summary = pd.DataFrame(
        [
            {
                "dataset_id": DATASET_ID,
                "physical_dataset_id": args.physical_dataset_id,
                "build_run_id": build_run_id,
                "status": CANDIDATE_STATUS,
                "materialization_scope": CANDIDATE_SCOPE,
                "row_count": validations["state_rows"],
                "ticker_count": validations["ticker_count"],
                "quote_guarded_repair_applied_rows": validations["quote_guarded_repair_applied_rows"],
                "qg_ohlc_changed_rows": validations["qg_ohlc_changed_rows"],
                "manifest_qg_diff_not_applied_rows": validations["manifest_qg_diff_not_applied_rows"],
                "full_universe_claim_rows": validations["full_universe_claim_rows"],
                "ml_candidate_rows": validations["ml_candidate_rows"],
                "rl_candidate_rows": validations["rl_candidate_rows"],
                "validator_status": validations["validator_status"],
                "validator_hard_fail_count": validations["validator_hard_fail_count"],
                "output_tree_sha256": validations["output_tree_sha256"],
            }
        ]
    )
    summary.to_csv(summary_path, index=False)
    manifest = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": args.physical_dataset_id,
        "schema_version": STATE_SCHEMA_VERSION,
        "status": CANDIDATE_STATUS,
        "promotion_level": "controlled_candidate",
        "materialization_scope": CANDIDATE_SCOPE,
        "full_universe_claim": False,
        "official_dataset_created": False,
        "valid_for_event_context_candidate": False,
        "valid_for_ml_feature_candidate": False,
        "valid_for_backtest_context_candidate": False,
        "valid_for_rl_state_candidate": False,
        "valid_for_rl_training_direct": False,
        "valid_for_execution_simulator_direct": False,
        "execution_truth": False,
        "contains_future_information_without_event_filter": False,
        "requires_asof_filter": True,
        "decision_timestamp_rule": (
            "decision_timestamp_utc = intraday bar ts_utc + 1 minute; "
            "bar must be closed before consumption"
        ),
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": dataset_dir.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "summary_path": summary_path.as_posix(),
        "output_tree": output_tree,
        "source_inputs": {
            "intraday_parquet": args.intraday_parquet.as_posix(),
            "intraday_manifest": args.intraday_manifest.as_posix(),
        },
        "source_hashes": {
            "intraday_parquet_sha256": intraday_parquet_sha,
            "intraday_manifest_sha256": intraday_manifest_sha,
        },
        "upstream_intraday_manifest": {
            "dataset_id": intraday_manifest.get("dataset_id"),
            "physical_dataset_id": intraday_manifest.get("physical_dataset_id"),
            "status": intraday_manifest.get("status"),
            "build_run_id": intraday_manifest.get("build_run_id"),
            "materialization_scope": intraday_manifest.get("materialization_scope"),
            "full_universe_claim": intraday_manifest.get("full_universe_claim"),
            "validations": intraday_manifest.get("validations"),
        },
        "validations": validations,
        "limitations": [
            "Controlled candidate only; not institutional market_state_table_v0_1.",
            "Built only from master_intraday_bar_table_v0_2_candidate_quote_guarded scoped E-root rows.",
            "One state row per closed 1m quote-guarded bar; no event anchoring, no outcomes and no scanner threshold.",
            "Identity component is not joined to instrument_master in this scope; ticker fallback is explicit and candidate-only.",
            "full_universe_claim=false and all ML/RL/backtest/execution direct-use gates remain false.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    if validations["validator_status"] != "passed":
        raise RuntimeError(f"market_state intraday quote-guarded candidate validation failed: {validations}")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize a controlled market_state_table_v0_1 candidate from "
            "master_intraday_bar_table_v0_2_candidate_quote_guarded."
        )
    )
    parser.add_argument("--intraday-parquet", type=Path, default=DEFAULT_INTRADAY_PARQUET)
    parser.add_argument("--intraday-manifest", type=Path, default=DEFAULT_INTRADAY_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--physical-dataset-id", default=PHYSICAL_DATASET_ID)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--created-at-utc", default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    manifest = build(args)
    print(json.dumps(manifest["validations"], indent=2, ensure_ascii=False))
    print(f"Wrote {manifest['output_path']}")


if __name__ == "__main__":
    main()
