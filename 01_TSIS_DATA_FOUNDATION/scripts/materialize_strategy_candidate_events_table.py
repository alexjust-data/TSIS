from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

import validate_event_candidate_tables as event_validator


MODULE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MODULE_ROOT.parent

DAILY_DATASET_ID = "daily_strategy_candidate_events_table_v0_1"
INTRADAY_DATASET_ID = "intraday_1m_strategy_candidate_events_table_v0_1"
DATASET_DIR_NAMES = {
    DAILY_DATASET_ID: "daily_strategy_candidate_events_table_v0_1_candidate",
    INTRADAY_DATASET_ID: "intraday_1m_strategy_candidate_events_table_v0_1_candidate",
}
QUALITY_POLICY_VERSION = "event_candidate_table_quality_policy_v0_1"
DECISION_TIMESTAMP_POLICY_ID = "state_decision_timestamp_policy_v0_1"
DEFINITION_CUTOFF_POLICY_VERSION = "event_definition_cutoff_policy_v0_1"
FORMULA_CONTRACT_ID = "state_derived_observables_formula_contract_v0_1"

DEFAULT_INSTRUMENT_MASTER = Path(
    "E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet"
)
DEFAULT_MASTER_DAILY = Path(
    "E:/TSIS/data/data_foundation_outputs/master_daily_table/master_daily_table_v0_1"
)

DAILY_DEFAULTS = {
    "source_candidate_dataset_id": "daily_scanner_candidates_table_v0_3",
    "selection_column": "selected_any_profile",
    "event_definition_id": "daily_in_play_momentum_candidate_event_v0_1",
    "event_definition_version": "v0_1",
    "event_family": "daily_in_play_momentum_candidate",
    "event_type": "in_play_momentum",
    "event_anchor_role": "daily_session_anchor",
    "event_timestamp_policy": "session_close_available",
    "source_scanner_definition_version": "v0_3",
}
INTRADAY_DEFAULTS = {
    "source_candidate_dataset_id": "intraday_scanner_candidates_table_v0_2_quote_guarded_candidate",
    "selection_column": "selected_intraday_in_play_candidate",
    "event_definition_id": "intraday_1m_first_motion_candidate_event_v0_1",
    "event_definition_version": "v0_1",
    "event_family": "intraday_first_motion_threshold_cross_candidate",
    "event_type": "first_motion_threshold_cross",
    "event_anchor_role": "trigger_bar_close",
    "event_timestamp_policy": "closed_1m_bar",
    "source_scanner_definition_version": "v0_2",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id(dataset_id: str) -> str:
    prefix = "daily_strategy_candidate_events" if dataset_id == DAILY_DATASET_ID else "intraday_1m_strategy_candidate_events"
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def _default_output_root(run_id: str) -> Path:
    date_key = datetime.now().strftime("%Y-%m-%d")
    return REPO_ROOT / "tests" / "test_runs" / date_key / run_id


def _as_posix(path: Path | None) -> str | None:
    return None if path is None else path.as_posix()


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_suffix(*parts: Any, length: int = 16) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _read_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows") if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ValueError("JSON source must be a list or an object with rows")
        return pd.DataFrame(rows)
    if suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return pd.DataFrame(rows)
    raise ValueError(f"Unsupported source suffix: {path.suffix}")


def _missing(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    return isinstance(value, str) and value.strip() == ""


def _value(row: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row and not _missing(row[name]):
            return row[name]
    return default


def _bool_value(row: dict[str, Any], *names: str, default: bool = False) -> bool:
    value = _value(row, *names, default=default)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.fillna(False).map(
        lambda value: str(value).strip().lower() in {"true", "1", "yes", "y"}
        if isinstance(value, str)
        else bool(value)
    )


def _date_str(value: Any) -> str:
    return pd.Timestamp(value).date().isoformat()


def _iso_z(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _add_minutes(value: Any, minutes: int) -> str:
    ts = pd.Timestamp(_iso_z(value))
    return (ts + timedelta(minutes=minutes)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_bundle(payload: dict[str, Any]) -> str:
    cleaned = {key: value for key, value in payload.items() if not _missing(value)}
    return json.dumps(cleaned, sort_keys=True, ensure_ascii=False, default=str)


def _observables(row: dict[str, Any], names: list[str]) -> dict[str, Any]:
    return {name: row[name] for name in names if name in row and not _missing(row[name])}


def _source_candidate_id(row: dict[str, Any], dataset_id: str) -> str:
    names = (
        ["scanner_candidate_id", "daily_scanner_candidate_id", "source_candidate_id"]
        if dataset_id == DAILY_DATASET_ID
        else ["intraday_scanner_candidate_id", "scanner_candidate_id", "source_candidate_id"]
    )
    value = _value(row, *names)
    if value is not None:
        return str(value)
    return _stable_suffix(dataset_id, _value(row, "instrument_id"), _value(row, "ticker"), _value(row, "session_date"))


def _common_row(row: dict[str, Any], args: argparse.Namespace, *, dataset_id: str) -> dict[str, Any]:
    source_manifest = args.source_candidate_manifest or args.source_candidates
    source_manifest_sha = _sha256_file(source_manifest) if source_manifest else None
    session_date = _date_str(_value(row, "session_date", "event_date"))
    event_date = _date_str(_value(row, "event_date", "session_date", default=session_date))
    is_common_stock = _bool_value(row, "is_common_stock", default=True)
    is_lt1b = _bool_value(row, "is_lt1b_operational", default=True)

    return {
        "event_definition_id": args.event_definition_id,
        "event_definition_version": args.event_definition_version,
        "event_family": args.event_family,
        "event_type": args.event_type,
        "event_subtype": args.event_subtype,
        "event_anchor_role": args.event_anchor_role,
        "instrument_id": str(_value(row, "instrument_id")),
        "ticker": str(_value(row, "ticker")).upper(),
        "session_date": session_date,
        "event_date": event_date,
        "market_timezone": args.market_timezone,
        "listing_exchange": _value(row, "listing_exchange", "primary_exchange", "exchange_acronym"),
        "is_common_stock": is_common_stock,
        "is_lt1b_operational": is_lt1b,
        "instrument_identity_temporal_match": bool(_value(row, "instrument_identity_temporal_match", default=True)),
        "calendar_session_valid": bool(_value(row, "calendar_session_valid", "expected_session", default=True)),
        "event_timestamp_policy": args.event_timestamp_policy,
        "decision_timestamp_policy_id": DECISION_TIMESTAMP_POLICY_ID,
        "source_candidate_id": _source_candidate_id(row, dataset_id),
        "source_candidate_dataset_id": args.source_candidate_dataset_id,
        "source_candidate_build_run_id": _value(row, "build_run_id", "source_candidate_build_run_id", "scanner_run_id"),
        "source_candidate_quality_state": _value(row, "source_candidate_quality_state", "event_quality_state", default="usable_candidate"),
        "source_scanner_definition_id": _value(row, "scanner_definition_id", "source_scanner_definition_id"),
        "source_scanner_definition_version": args.source_scanner_definition_version,
        "source_scanner_run_id": _value(row, "scanner_run_id", "source_scanner_run_id"),
        "source_manifest_path": _as_posix(source_manifest),
        "source_manifest_sha256": source_manifest_sha,
        "event_definition_params_bundle": _json_bundle(
            {
                "event_definition_id": args.event_definition_id,
                "event_definition_version": args.event_definition_version,
                "source_selection_column": args.selection_column,
                "source_candidate_dataset_id": args.source_candidate_dataset_id,
            }
        ),
        "thresholds_bundle": _json_bundle({"source_threshold_policy": "source_definition_bundle"}),
        "definition_cutoff_policy_version": DEFINITION_CUTOFF_POLICY_VERSION,
        "definition_formula_contract_id": FORMULA_CONTRACT_ID,
        "definition_is_parametric": True,
        "definition_is_alphaevolve_candidate": bool(args.definition_is_alphaevolve_candidate),
        "event_quality_state": "usable_candidate",
        "event_selection_state": "candidate",
        "event_anchor_quality_state": "usable_candidate",
        "valid_for_event_windows_candidate": True,
        "valid_for_event_state_candidate": False,
        "valid_for_pattern_discovery_candidate": True,
        "valid_for_backtest_event_candidate": True,
        "valid_for_ml_feature_candidate": False,
        "valid_for_rl_state_candidate": False,
        "valid_for_alphaevolve_candidate": bool(args.definition_is_alphaevolve_candidate),
        "alphaevolve_evaluator_production_enabled": False,
        "full_universe_claim": False,
        "contains_outcome_information": False,
        "contains_label_information": False,
        "contains_reward_information": False,
        "execution_truth": False,
        "requires_asof_filter": True,
        "materialization_scope": args.materialization_scope,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "schema_version": dataset_id,
        "build_run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "source_instrument_master_path": _as_posix(args.source_instrument_master_path),
        "source_instrument_master_sha256": _sha256_file(args.source_instrument_master_path),
        "source_market_calendar_path": _as_posix(args.source_market_calendar_path),
        "source_market_calendar_sha256": _sha256_file(args.source_market_calendar_path),
        "source_master_daily_table_path": _as_posix(args.source_master_daily_table_path),
        "source_master_daily_table_sha256": None,
    }


def _daily_event_row(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    out = _common_row(row, args, dataset_id=DAILY_DATASET_ID)
    session_date = out["session_date"]
    as_of = _iso_z(_value(row, "as_of_utc", "event_availability_utc", default=f"{session_date}T21:05:00Z"))
    source_candidate_id = out["source_candidate_id"]
    event_suffix = _stable_suffix(args.event_definition_id, out["instrument_id"], session_date, args.event_anchor_role)
    out.update(
        {
            "daily_event_id": f"daily_event_{event_suffix}",
            "event_id": f"event_daily_{event_suffix}",
            "event_table_id": DAILY_DATASET_ID,
            "event_schema_version": DAILY_DATASET_ID,
            "as_of_utc": as_of,
            "event_availability_utc": _iso_z(_value(row, "event_availability_utc", "as_of_utc", default=as_of)),
            "detection_timestamp_utc": _iso_z(_value(row, "detection_timestamp_utc", "as_of_utc", default=as_of)),
            "source_data_availability_cutoff_utc": _iso_z(
                _value(row, "source_data_availability_cutoff_utc", "as_of_utc", default=as_of)
            ),
            "source_price_view": _value(row, "price_view", "source_price_view", default="daily_raw"),
            "contains_intraday_timestamp_claim": False,
            "event_timestamp_utc": None,
            "trigger_observables_bundle": _json_bundle(
                _observables(
                    row,
                    [
                        "daily_high_vs_prev_close_pct",
                        "in_play_motion_pct",
                        "daily_return_pct",
                        "gap_pct",
                        "volume_today",
                        "dollar_volume_today",
                        "volume",
                        "dollar_volume",
                        "rvol_20d",
                        "rank",
                        "rank_metric_value",
                        "candidate_reasons",
                        "scanner_selection_state",
                    ],
                )
                | {"source_candidate_id": source_candidate_id}
            ),
        }
    )
    return out


def _intraday_event_row(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    confirmed = _bool_value(row, args.quote_guarded_confirmed_column, default=False)
    if not confirmed and args.allow_controlled_quote_guarded_assumption:
        confirmed = True
    if not confirmed:
        raise ValueError(
            "Selected intraday rows must contain quote-guarded confirmation or use "
            "--allow-controlled-quote-guarded-assumption for controlled fixtures."
        )

    out = _common_row(row, args, dataset_id=INTRADAY_DATASET_ID)
    event_ts = _iso_z(
        _value(row, "event_timestamp_utc", "first_cross_50_ts_utc", "event_bar_ts_utc", "as_of_utc")
    )
    event_bar_ts = _iso_z(_value(row, "event_bar_ts_utc", "first_cross_50_ts_utc", default=event_ts))
    event_bar_end = _iso_z(_value(row, "event_bar_end_utc", default=_add_minutes(event_bar_ts, 1)))
    as_of = _iso_z(_value(row, "as_of_utc", default=event_bar_end))
    if pd.Timestamp(as_of) < pd.Timestamp(event_bar_end):
        as_of = event_bar_end
    event_suffix = _stable_suffix(args.event_definition_id, out["instrument_id"], event_ts, args.event_anchor_role)
    out.update(
        {
            "intraday_event_id": f"intraday_event_{event_suffix}",
            "event_id": f"event_intraday_{event_suffix}",
            "event_table_id": INTRADAY_DATASET_ID,
            "event_schema_version": INTRADAY_DATASET_ID,
            "event_timestamp_utc": event_ts,
            "event_timestamp_et": _value(row, "event_timestamp_et", "first_cross_50_ts_et"),
            "event_bar_ts_utc": event_bar_ts,
            "event_bar_end_utc": event_bar_end,
            "event_bar_size": "1m",
            "as_of_utc": as_of,
            "event_availability_utc": _iso_z(_value(row, "event_availability_utc", default=event_bar_end)),
            "detection_timestamp_utc": _iso_z(_value(row, "detection_timestamp_utc", default=event_bar_end)),
            "source_data_availability_cutoff_utc": _iso_z(
                _value(row, "source_data_availability_cutoff_utc", default=event_bar_end)
            ),
            "uses_incomplete_bar": False,
            "event_session_phase": _value(row, "event_session_phase", "first_cross_50_segment", "session_segment", default="unknown_review"),
            "source_price_view": args.source_price_view,
            "source_ohlcv_1m_root": _as_posix(args.source_ohlcv_1m_root),
            "source_master_intraday_table_path": _as_posix(args.source_master_intraday_table_path),
            "source_quote_guarded_repair_manifest": _as_posix(args.source_quote_guarded_repair_manifest),
            "source_quote_guarded_run_id": args.source_quote_guarded_run_id,
            "quote_guarded_view": args.source_price_view == "ohlcv_1m_quote_guarded",
            "quote_guarded_repair_applied_at_event": _bool_value(row, "quote_guarded_repair_applied_at_event", default=False),
            "repair_state_at_event": _value(row, "repair_state_at_event", default="not_repaired"),
            "repair_reason_at_event": _value(row, "repair_reason_at_event"),
            "raw_event_detected": _bool_value(row, "raw_event_detected", "motion_threshold_passed", args.selection_column, default=True),
            "quote_guarded_event_confirmed": confirmed,
            "raw_only_rejected_reason": None,
            "trigger_price": _value(row, "trigger_price", "first_cross_price"),
            "trigger_move_vs_prior_close_pct": _value(
                row, "trigger_move_vs_prior_close_pct", "first_cross_move_vs_prev_close_pct"
            ),
            "trigger_move_vs_segment_open_pct": _value(
                row, "trigger_move_vs_segment_open_pct", "first_cross_move_vs_segment_open_pct"
            ),
            "trigger_volume_to_time": _value(row, "trigger_volume_to_time", "volume_to_time_at_first_cross"),
            "trigger_dollar_volume_to_time": _value(
                row, "trigger_dollar_volume_to_time", "dollar_volume_to_time_at_first_cross"
            ),
            "bars_observed_to_event": _value(row, "bars_observed_to_event", "bars_observed_to_first_cross"),
            "trigger_source_bar_file": _value(row, "trigger_source_bar_file", "first_cross_source_ohlcv_1m_file"),
            "trigger_observables_bundle": _json_bundle(
                _observables(
                    row,
                    [
                        "first_cross_price",
                        "first_cross_move_vs_prev_close_pct",
                        "first_cross_move_vs_segment_open_pct",
                        "volume_to_time_at_first_cross",
                        "dollar_volume_to_time_at_first_cross",
                        "bars_observed_to_first_cross",
                        "candidate_reasons",
                        "scanner_selection_state",
                    ],
                )
            ),
        }
    )
    return out


def _selected_rows(df: pd.DataFrame, args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.selection_column not in df.columns:
        raise ValueError(f"Selection column not found in source candidates: {args.selection_column}")
    selected = df[_bool_series(df[args.selection_column])].copy()
    if selected.empty:
        raise ValueError(f"No selected rows found using selection column: {args.selection_column}")
    return selected.to_dict(orient="records")


def _write_summary_csv(path: Path, stats: dict[str, Any]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.output_root.exists() and any(args.output_root.iterdir()) and not args.overwrite:
        raise FileExistsError(f"Output root already exists and is not empty: {args.output_root}")
    if args.output_root.exists() and args.overwrite:
        shutil.rmtree(args.output_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    source = _read_source(args.source_candidates)
    selected_rows = _selected_rows(source, args)
    rows = (
        [_daily_event_row(row, args) for row in selected_rows]
        if args.dataset_id == DAILY_DATASET_ID
        else [_intraday_event_row(row, args) for row in selected_rows]
    )
    output_dir = args.output_root / DATASET_DIR_NAMES[args.dataset_id]
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = output_dir / "data.parquet"
    pd.DataFrame(rows).to_parquet(dataset_path, index=False)

    validator_summary = event_validator.validate_rows(rows, args.dataset_id, dataset_path)
    stats = {
        "dataset_id": args.dataset_id,
        "row_count": len(rows),
        "source_row_count": len(source),
        "selected_source_row_count": len(selected_rows),
        "validator_status": validator_summary["status"],
        "validator_hard_fail_count": validator_summary["hard_fail_count"],
        "validator_review_fail_count": validator_summary["review_fail_count"],
        "full_universe_claim_true_rows": int(sum(bool(row["full_universe_claim"]) for row in rows)),
        "ml_feature_candidate_rows": int(sum(bool(row["valid_for_ml_feature_candidate"]) for row in rows)),
        "rl_state_candidate_rows": int(sum(bool(row["valid_for_rl_state_candidate"]) for row in rows)),
        "alphaevolve_production_enabled_rows": int(
            sum(bool(row.get("alphaevolve_evaluator_production_enabled")) for row in rows)
        ),
    }
    summary_path = args.output_root / f"_{args.dataset_id}_summary_candidate.csv"
    manifest_path = args.output_root / f"_{args.dataset_id}_manifest_candidate.json"
    validator_summary_path = args.output_root / f"_{args.dataset_id}_validator_summary_candidate.json"
    validator_failures_path = args.output_root / f"_{args.dataset_id}_validator_failures_candidate.json"
    _write_summary_csv(summary_path, stats)
    validator_summary_path.write_text(
        json.dumps({key: value for key, value in validator_summary.items() if key != "failures"}, indent=2, default=str),
        encoding="utf-8",
    )
    validator_failures_path.write_text(
        json.dumps({"failures": validator_summary["failures"]}, indent=2, default=str),
        encoding="utf-8",
    )

    manifest = {
        "dataset_id": args.dataset_id,
        "schema_version": args.dataset_id,
        "promotion_level": "candidate_not_promoted",
        "materialization_scope": args.materialization_scope,
        "build_run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "output_root": _as_posix(args.output_root),
        "dataset_path": _as_posix(dataset_path),
        "dataset_sha256": _sha256_file(dataset_path),
        "manifest_path": _as_posix(manifest_path),
        "summary_path": _as_posix(summary_path),
        "source_candidate_dataset_id": args.source_candidate_dataset_id,
        "source_candidates_path": _as_posix(args.source_candidates),
        "source_candidates_sha256": _sha256_file(args.source_candidates),
        "source_candidate_manifest": _as_posix(args.source_candidate_manifest),
        "source_candidate_manifest_sha256": _sha256_file(args.source_candidate_manifest)
        if args.source_candidate_manifest
        else None,
        "selection_column": args.selection_column,
        "event_definition_id": args.event_definition_id,
        "event_definition_version": args.event_definition_version,
        "validator_summary_path": _as_posix(validator_summary_path),
        "validator_failures_path": _as_posix(validator_failures_path),
        "validator_summary": {key: value for key, value in validator_summary.items() if key != "failures"},
        "stats": stats,
        "non_goals": [
            "No contiene outcomes, labels, rewards, acciones, fills ni PnL.",
            "No materializa market_state_table ni event_state_table.",
            "No habilita ML/RL/AlphaEvolve production.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    if validator_summary["hard_fail_count"]:
        raise ValueError(f"Event candidate validator failed: {validator_summary['hard_fail_count']} hard failures")
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize TSIS strategy candidate event tables.")
    parser.add_argument("--dataset-id", choices=[DAILY_DATASET_ID, INTRADAY_DATASET_ID], required=True)
    parser.add_argument("--source-candidates", type=Path, required=True)
    parser.add_argument("--source-candidate-manifest", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--created-at-utc")
    parser.add_argument("--selection-column")
    parser.add_argument("--source-candidate-dataset-id")
    parser.add_argument("--event-definition-id")
    parser.add_argument("--event-definition-version")
    parser.add_argument("--event-family")
    parser.add_argument("--event-type")
    parser.add_argument("--event-subtype")
    parser.add_argument("--event-anchor-role")
    parser.add_argument("--event-timestamp-policy")
    parser.add_argument("--source-scanner-definition-version")
    parser.add_argument("--materialization-scope", default="controlled_candidate_not_promoted")
    parser.add_argument("--market-timezone", default="America/New_York")
    parser.add_argument("--definition-is-alphaevolve-candidate", action="store_true")
    parser.add_argument("--source-instrument-master-path", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--source-market-calendar-path", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument("--source-master-daily-table-path", type=Path, default=DEFAULT_MASTER_DAILY)
    parser.add_argument("--source-price-view", default="ohlcv_1m_quote_guarded")
    parser.add_argument("--source-ohlcv-1m-root", type=Path, default=Path("E:/TSIS/data/ohlcv_1m"))
    parser.add_argument("--source-master-intraday-table-path", type=Path)
    parser.add_argument("--source-quote-guarded-repair-manifest", type=Path)
    parser.add_argument("--source-quote-guarded-run-id", default="quote_guarded_run_id_required_for_real_materialization")
    parser.add_argument("--quote-guarded-confirmed-column", default="quote_guarded_event_confirmed")
    parser.add_argument("--allow-controlled-quote-guarded-assumption", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    defaults = DAILY_DEFAULTS if args.dataset_id == DAILY_DATASET_ID else INTRADAY_DEFAULTS
    for key, value in defaults.items():
        if getattr(args, key) is None:
            setattr(args, key, value)
    args.run_id = args.run_id or _run_id(args.dataset_id)
    args.created_at_utc = args.created_at_utc or _utc_now()
    args.output_root = args.output_root or _default_output_root(args.run_id)

    if not args.source_candidates.exists():
        raise FileNotFoundError(args.source_candidates)
    if args.dataset_id == INTRADAY_DATASET_ID:
        if args.source_price_view == "ohlcv_1m_quote_guarded" and args.source_quote_guarded_repair_manifest is None:
            raise ValueError("--source-quote-guarded-repair-manifest is required for quote-guarded intraday events")
    return args


def main(argv: Iterable[str] | None = None) -> int:
    manifest = build(parse_args(argv))
    print("Strategy candidate events materialization completed.")
    print(f"Dataset ID: {manifest['dataset_id']}")
    print(f"Run ID: {manifest['build_run_id']}")
    print(f"Dataset: {manifest['dataset_path']}")
    print(f"Manifest: {manifest['manifest_path']}")
    print(f"Validator: {manifest['validator_summary']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
