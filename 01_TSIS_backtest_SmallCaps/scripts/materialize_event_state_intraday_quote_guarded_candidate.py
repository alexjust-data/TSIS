from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


DATASET_ID = "event_state_table_v0_1_candidate"
PHYSICAL_DATASET_ID = "event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled"
SCHEMA_VERSION = "event_state_table_v0_1"
BUILDER_VERSION = "event_state_intraday_1m_quote_guarded_builder_candidate_v0_1"
MATERIALIZATION_SCOPE = "intraday_1m_quote_guarded_event_state_controlled_candidate"
SOURCE_CUTOFF_POLICY_VERSION = "event_state_intraday_1m_quote_guarded_cutoff_policy_v0_1"
LEAKAGE_POLICY_VERSION = "event_state_intraday_1m_quote_guarded_leakage_policy_v0_1"
FEATURE_NAMESPACE_VERSION = "event_state_feature_namespaces_intraday_1m_quote_guarded_v0_1"

DEFAULT_MARKET_STATE_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/"
    "market_state_table_v0_1_candidate_intraday_quote_guarded_controlled"
)
DEFAULT_MARKET_STATE_MANIFEST = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/market_state_intraday_quote_guarded_candidate_v0_1/"
    "_market_state_table_manifest_v0_1_candidate_intraday_quote_guarded_controlled.json"
)
DEFAULT_EVENT_WINDOWS = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/"
    "event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet"
)
DEFAULT_EVENT_WINDOWS_MANIFEST = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/"
    "_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled"
)

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

PASSTHROUGH_PREFIXES = (
    "identity__",
    "calendar__",
    "scanner__",
    "daily__",
    "intraday__",
    "microstructure__",
    "halt__",
    "fundamentals__",
    "news__",
    "short_context__",
    "short_constraints__",
    "regime__",
    "quality__",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "event_state_intraday_1m_quote_guarded_candidate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_file(path: Path | None, chunk_size: int = 1024 * 1024) -> str | None:
    if path is None or not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(*parts: Any, length: int = 24) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _json_bundle(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_market_state(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {
        "market_state_id",
        "instrument_id",
        "ticker",
        "decision_timestamp_utc",
        "state_quality_state",
        "state_schema_version",
        "state_builder_version",
        "build_run_id",
        "created_at_utc",
        "full_universe_claim",
        "execution_truth",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required market_state columns: {missing}")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        raise ValueError("Refusing market_state rows with full_universe_claim=true")
    if frame["execution_truth"].fillna(False).astype(bool).any():
        raise ValueError("Refusing market_state rows with execution_truth=true")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame["decision_timestamp_utc_ts"] = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    return frame.sort_values(["ticker", "decision_timestamp_utc_ts", "market_state_id"]).reset_index(drop=True)


def _read_event_windows(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {
        "event_window_id",
        "source_event_id",
        "event_source_dataset_id",
        "event_family",
        "event_type",
        "event_code",
        "event_source",
        "ticker",
        "instrument_id",
        "session_date",
        "event_time_utc",
        "window_role",
        "window_start_utc",
        "window_end_utc",
        "contains_post_event_information",
        "leakage_safe_as_pre_event_feature",
        "source_event_quality_state",
        "event_window_quality_state",
        "event_window_consumption_state",
        "valid_for_backtest_event_window_candidate",
        "full_universe_claim",
        "event_anchor_decision_timestamp_utc",
        "schema_version",
        "quality_policy_version",
        "build_run_id",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required event_window columns: {missing}")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        raise ValueError("Refusing event_window rows with full_universe_claim=true")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame["window_start_utc_ts"] = pd.to_datetime(frame["window_start_utc"], utc=True)
    frame["window_end_utc_ts"] = pd.to_datetime(frame["window_end_utc"], utc=True)
    frame["event_time_utc_ts"] = pd.to_datetime(frame["event_time_utc"], utc=True)
    frame["event_anchor_decision_timestamp_utc_ts"] = pd.to_datetime(
        frame["event_anchor_decision_timestamp_utc"], utc=True
    )
    return frame.sort_values(["ticker", "window_end_utc_ts", "event_window_id"]).reset_index(drop=True)


def _target_decision_ts(window: pd.Series) -> pd.Timestamp:
    role = str(window["window_role"])
    if role == "event_anchor_1m":
        return pd.Timestamp(window["event_anchor_decision_timestamp_utc_ts"])
    return pd.Timestamp(window["window_end_utc_ts"])


def _state_role(window: pd.Series) -> str:
    role = str(window["window_role"])
    if role == "pre_event_30m":
        return "pre_event"
    if role == "event_anchor_1m":
        return "at_event"
    if role == "post_event_30m":
        return "post_event_review"
    return "research_replay"


def _state_quality(role: str, market_state_quality: str) -> str:
    if market_state_quality.startswith("state_blocked") or market_state_quality.startswith("state_bad"):
        return "event_state_blocked_invalid_component_quality"
    if role == "post_event_review":
        return "event_state_review_scoped_intraday_component"
    return "event_state_review_scoped_intraday_component"


def _select_market_state(market_by_ticker: dict[str, pd.DataFrame], ticker: str, target: pd.Timestamp) -> pd.Series | None:
    frame = market_by_ticker.get(ticker)
    if frame is None or frame.empty:
        return None
    eligible = frame[frame["decision_timestamp_utc_ts"] <= target]
    if eligible.empty:
        return None
    return eligible.iloc[-1]


def _validate_output(frame: pd.DataFrame) -> dict[str, Any]:
    hard_failures: list[str] = []
    if frame.empty:
        hard_failures.append("empty_output")
    if frame["event_state_id"].duplicated().any():
        hard_failures.append("duplicate_event_state_id")
    if frame["event_window_id"].isna().any():
        hard_failures.append("missing_event_window_id")
    if frame["market_state_id"].isna().any():
        hard_failures.append("missing_market_state_id")
    cutoff = pd.to_datetime(frame["state_cutoff_utc"], utc=True)
    decision = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    if (cutoff > decision).any():
        hard_failures.append("state_cutoff_after_decision")
    if any(column.startswith(PROHIBITED_PREFIXES) for column in frame.columns):
        hard_failures.append("prohibited_column_prefix")
    if frame["outcome_values_inline_allowed"].fillna(False).astype(bool).any():
        hard_failures.append("outcome_inline_allowed")
    if frame["label_columns_inline_allowed"].fillna(False).astype(bool).any():
        hard_failures.append("label_inline_allowed")
    if frame["reward_columns_inline_allowed"].fillna(False).astype(bool).any():
        hard_failures.append("reward_inline_allowed")
    post_ml = frame["state_role"].eq("post_event_review") & frame["valid_for_ml_feature_candidate"].fillna(False)
    if post_ml.any():
        hard_failures.append("post_event_review_marked_ml_feature")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        hard_failures.append("full_universe_claim_true")
    if frame["execution_truth"].fillna(False).astype(bool).any():
        hard_failures.append("execution_truth_true")
    return {
        "validator_status": "passed" if not hard_failures else "failed",
        "validator_hard_fail_count": len(hard_failures),
        "validator_hard_failures": hard_failures,
    }


def _write_summary(path: Path, stats: dict[str, Any]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.output_root.exists() and any(args.output_root.iterdir()) and not args.overwrite:
        raise FileExistsError(f"Output root already exists: {args.output_root}")
    if args.output_root.exists() and args.overwrite:
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    market = _read_market_state(args.market_state_root)
    windows = _read_event_windows(args.event_windows)
    market_by_ticker = {ticker: group.reset_index(drop=True) for ticker, group in market.groupby("ticker")}
    market_manifest = _read_json(args.market_state_manifest)
    event_windows_manifest = _read_json(args.event_windows_manifest)
    market_manifest_sha = _sha256_file(args.market_state_manifest)
    event_windows_manifest_sha = _sha256_file(args.event_windows_manifest)
    event_windows_sha = _sha256_file(args.event_windows)

    rows: list[dict[str, Any]] = []
    missing_windows: list[str] = []
    for _, window in windows.iterrows():
        target_decision = _target_decision_ts(window)
        market_row = _select_market_state(market_by_ticker, str(window["ticker"]), target_decision)
        if market_row is None:
            missing_windows.append(str(window["event_window_id"]))
            continue
        role = _state_role(window)
        decision_ts = pd.Timestamp(market_row["decision_timestamp_utc_ts"])
        event_ts = pd.Timestamp(window["event_time_utc_ts"])
        state_cutoff = decision_ts
        contains_post = bool(window["contains_post_event_information"])
        event_state_id = "event_state_intraday_" + _stable_id(
            window["event_window_id"], market_row["market_state_id"], role, _iso(decision_ts), SCHEMA_VERSION
        )
        output: dict[str, Any] = {
            "event_state_id": event_state_id,
            "event_id": window["source_event_id"],
            "event_window_id": window["event_window_id"],
            "market_state_id": market_row["market_state_id"],
            "instrument_id": market_row["instrument_id"],
            "ticker": market_row["ticker"],
            "event_family": window["event_family"],
            "event_timestamp_utc": _iso(event_ts),
            "decision_timestamp_utc": _iso(decision_ts),
            "decision_date": decision_ts.date().isoformat(),
            "state_role": role,
            "state_schema_version": SCHEMA_VERSION,
            "state_builder_version": BUILDER_VERSION,
            "state_quality_state": _state_quality(role, str(market_row["state_quality_state"])),
            "event_window_start_utc": _iso(window["window_start_utc_ts"]),
            "event_window_end_utc": _iso(window["window_end_utc_ts"]),
            "pre_event_window_start_utc": _iso(window["window_start_utc_ts"]) if role == "pre_event" else None,
            "pre_event_window_end_utc": _iso(window["window_end_utc_ts"]) if role == "pre_event" else None,
            "state_cutoff_utc": _iso(state_cutoff),
            "state_cutoff_reason": {
                "pre_event": "latest_closed_1m_bar_at_or_before_event_timestamp",
                "at_event": "trigger_bar_closed_quote_guarded",
                "post_event_review": "latest_closed_1m_bar_at_or_before_post_event_window_end",
                "research_replay": "research_replay_cutoff",
            }[role],
            "event_source_dataset_id": window["event_source_dataset_id"],
            "event_source_quality_state": window["source_event_quality_state"],
            "outcome_join_key": window["event_window_id"],
            "label_join_key": window["event_window_id"],
            "outcome_values_inline_allowed": False,
            "label_columns_inline_allowed": False,
            "reward_columns_inline_allowed": False,
            "valid_for_pattern_discovery": True,
            "valid_for_ml_feature_candidate": False,
            "valid_for_backtest_context_candidate": False,
            "valid_for_rl_state_candidate": False,
            "valid_for_rl_training_direct": False,
            "valid_for_execution_context_candidate": False,
            "valid_for_execution_simulator_direct": False,
            "contains_future_information_without_event_filter": contains_post,
            "requires_asof_filter": True,
            "full_universe_claim": False,
            "execution_truth": False,
            "build_run_id": args.run_id,
            "created_at_utc": args.created_at_utc,
            "market_state_build_run_id": market_row["build_run_id"],
            "event_windows_build_run_id": window["build_run_id"],
            "component_manifest_hash_bundle": _json_bundle(
                {
                    "market_state_manifest_sha256": market_manifest_sha,
                    "event_windows_manifest_sha256": event_windows_manifest_sha,
                    "event_windows_table_sha256": event_windows_sha,
                }
            ),
            "source_cutoff_policy_version": SOURCE_CUTOFF_POLICY_VERSION,
            "leakage_policy_version": LEAKAGE_POLICY_VERSION,
            "feature_namespace_version": FEATURE_NAMESPACE_VERSION,
            "event__window_role": window["window_role"],
            "event__event_type": window["event_type"],
            "event__event_code": window["event_code"],
            "event__event_source": window["event_source"],
            "event__window_consumption_state": window["event_window_consumption_state"],
            "event__event_window_quality_state": window["event_window_quality_state"],
            "event__leakage_safe_as_pre_event_feature": bool(window["leakage_safe_as_pre_event_feature"]),
            "quality__source_market_state_dataset_id": market_manifest.get("dataset_id"),
            "quality__source_event_windows_dataset_id": event_windows_manifest.get("dataset_id"),
            "quality__candidate_dataset_id": DATASET_ID,
            "quality__candidate_materialization_scope": MATERIALIZATION_SCOPE,
        }
        for key, value in market_row.items():
            if key.startswith(PASSTHROUGH_PREFIXES) and key not in output:
                output[key] = value
        rows.append(output)

    frame = pd.DataFrame(rows)
    validation = _validate_output(frame)
    if missing_windows:
        validation["validator_status"] = "failed"
        validation["validator_hard_fail_count"] += 1
        validation["validator_hard_failures"].append("missing_market_state_for_event_window")
    if validation["validator_hard_fail_count"]:
        raise ValueError(f"Event state validation failed: {validation}")

    dataset_dir = args.output_root / PHYSICAL_DATASET_ID
    dataset_dir.mkdir(parents=True, exist_ok=True)
    output_path = dataset_dir / "data.parquet"
    manifest_path = args.output_root / f"_{PHYSICAL_DATASET_ID}_manifest.json"
    summary_path = args.output_root / f"_{PHYSICAL_DATASET_ID}_summary.csv"
    frame.to_parquet(output_path, index=False)
    output_sha = _sha256_file(output_path)

    validations = {
        "source_event_window_rows": int(len(windows)),
        "joined_event_state_rows": int(len(frame)),
        "missing_market_state_window_rows": int(len(missing_windows)),
        "event_count": int(frame["event_id"].nunique()),
        "event_window_count": int(frame["event_window_id"].nunique()),
        "market_state_count": int(frame["market_state_id"].nunique()),
        "ticker_count": int(frame["ticker"].nunique()),
        "state_role_counts": {str(k): int(v) for k, v in frame["state_role"].value_counts().sort_index().items()},
        "state_quality_counts": {
            str(k): int(v) for k, v in frame["state_quality_state"].value_counts().sort_index().items()
        },
        "valid_for_pattern_discovery_rows": int(frame["valid_for_pattern_discovery"].sum()),
        "valid_for_ml_feature_candidate_rows": int(frame["valid_for_ml_feature_candidate"].sum()),
        "valid_for_rl_state_candidate_rows": int(frame["valid_for_rl_state_candidate"].sum()),
        "valid_for_rl_training_direct_rows": int(frame["valid_for_rl_training_direct"].sum()),
        "execution_truth_rows": int(frame["execution_truth"].sum()),
        "full_universe_claim_rows": int(frame["full_universe_claim"].sum()),
        "contains_future_information_without_event_filter_rows": int(
            frame["contains_future_information_without_event_filter"].sum()
        ),
        **validation,
    }
    _write_summary(summary_path, validations)

    manifest = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": PHYSICAL_DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "status": "controlled_candidate_not_promoted",
        "promotion_level": "controlled_candidate",
        "materialization_scope": MATERIALIZATION_SCOPE,
        "full_universe_claim": False,
        "build_run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "output_path": output_path.as_posix(),
        "output_sha256": output_sha,
        "manifest_path": manifest_path.as_posix(),
        "summary_path": summary_path.as_posix(),
        "source_inputs": {
            "market_state_root": args.market_state_root.as_posix(),
            "market_state_manifest": args.market_state_manifest.as_posix() if args.market_state_manifest else None,
            "event_windows_table": args.event_windows.as_posix(),
            "event_windows_manifest": args.event_windows_manifest.as_posix()
            if args.event_windows_manifest
            else None,
        },
        "source_hashes": {
            "market_state_manifest_sha256": market_manifest_sha,
            "event_windows_manifest_sha256": event_windows_manifest_sha,
            "event_windows_table_sha256": event_windows_sha,
        },
        "source_manifests": {
            "market_state_manifest": market_manifest,
            "event_windows_manifest": event_windows_manifest,
        },
        "validations": validations,
        "limitations": [
            "Controlled candidate only; not institutional event_state_table_v0_1.",
            "Built from scoped intraday quote-guarded market_state and controlled intraday event windows.",
            "No labels, rewards, strategy signals, actions, fills, PnL or outcome values are embedded.",
            "ML/RL/backtest/execution direct-use gates remain false.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize controlled intraday quote-guarded event_state candidate.")
    parser.add_argument("--market-state-root", type=Path, default=DEFAULT_MARKET_STATE_ROOT)
    parser.add_argument("--market-state-manifest", type=Path, default=DEFAULT_MARKET_STATE_MANIFEST)
    parser.add_argument("--event-windows", type=Path, default=DEFAULT_EVENT_WINDOWS)
    parser.add_argument("--event-windows-manifest", type=Path, default=DEFAULT_EVENT_WINDOWS_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--created-at-utc", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.run_id = args.run_id or _run_id()
    args.created_at_utc = args.created_at_utc or _utc_now()
    for path in (args.market_state_root, args.event_windows):
        if not path.exists():
            raise FileNotFoundError(path)
    return args


def main(argv: Iterable[str] | None = None) -> int:
    manifest = build(parse_args(argv))
    print("Intraday quote-guarded event_state candidate materialization completed.")
    print(f"Dataset: {manifest['output_path']}")
    print(f"Manifest: {manifest['manifest_path']}")
    print(f"Rows: {manifest['validations']['joined_event_state_rows']}")
    print(f"Validator: {manifest['validations']['validator_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
