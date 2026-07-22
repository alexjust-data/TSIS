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


DATASET_ID = "event_windows_table_v0_1_candidate_daily_strategy_events"
SCHEMA_VERSION = "event_windows_table_v0_1_candidate_daily_strategy_events"
QUALITY_POLICY_VERSION = "event_windows_table_policy_v0_1_candidate_daily_strategy_events"
MATERIALIZATION_SCOPE = "daily_strategy_event_windows_controlled_candidate"
SOURCE_EVENT_DATASET_ID = "daily_strategy_candidate_events_table_v0_1"

DEFAULT_MARKET_CALENDAR = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/market_calendar_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/market_calendar/_market_calendar_manifest_v0_1.json"
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "daily_strategy_event_windows_candidate_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(*parts: Any, length: int = 16) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _as_posix(path: Path | None) -> str | None:
    return None if path is None else path.as_posix()


def _iso(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _date(value: Any) -> str:
    return pd.Timestamp(value).date().isoformat()


def _read_events(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    required = {
        "event_id",
        "event_family",
        "event_type",
        "event_definition_id",
        "ticker",
        "instrument_id",
        "session_date",
        "as_of_utc",
        "event_quality_state",
        "event_selection_state",
        "valid_for_event_windows_candidate",
        "contains_outcome_information",
        "contains_label_information",
        "contains_reward_information",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required event columns: {missing}")
    selected = df[
        df["valid_for_event_windows_candidate"].fillna(False).astype(bool)
        & df["event_selection_state"].eq("candidate")
        & ~df["contains_outcome_information"].fillna(False).astype(bool)
        & ~df["contains_label_information"].fillna(False).astype(bool)
        & ~df["contains_reward_information"].fillna(False).astype(bool)
    ].copy()
    if selected.empty:
        raise ValueError("No valid daily strategy event candidates found for event windows")
    selected["session_date"] = pd.to_datetime(selected["session_date"]).dt.normalize()
    selected["ticker"] = selected["ticker"].astype(str).str.upper().str.strip()
    return selected


def _read_calendar(path: Path) -> pd.DataFrame:
    calendar = pd.read_parquet(path)
    required = {
        "session_date",
        "open_utc",
        "close_utc",
        "session_minutes",
        "is_early_close",
        "calendar",
        "timezone",
    }
    missing = sorted(required - set(calendar.columns))
    if missing:
        raise ValueError(f"Missing required market calendar columns: {missing}")
    calendar = calendar.sort_values("session_date").copy()
    calendar["session_date"] = pd.to_datetime(calendar["session_date"]).dt.normalize()
    calendar["previous_session_date"] = calendar["session_date"].shift(1)
    calendar["next_session_date"] = calendar["session_date"].shift(-1)
    calendar["previous_open_utc"] = calendar["open_utc"].shift(1)
    calendar["previous_close_utc"] = calendar["close_utc"].shift(1)
    calendar["next_open_utc"] = calendar["open_utc"].shift(-1)
    calendar["next_close_utc"] = calendar["close_utc"].shift(-1)
    return calendar


def _window_row(event: Any, role: str, start: Any, end: Any, start_source: str, end_source: str) -> dict[str, Any] | None:
    if pd.isna(start) or pd.isna(end):
        return None
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    if end_ts <= start_ts:
        return None

    event_time = pd.Timestamp(event.as_of_utc)
    source_event_id = str(event.event_id)
    contains_event_time = role == "event_session_regular"
    contains_post_event = role == "next_session_regular"
    leakage_safe = role == "prior_session_regular"
    valid_for_ml = role == "prior_session_regular"
    valid_for_outcome = role == "next_session_regular"
    consumption = {
        "prior_session_regular": "pre_event_context_window",
        "event_session_regular": "daily_event_definition_window",
        "next_session_regular": "outcome_candidate_window",
    }[role]

    return {
        "event_window_id": "daily_strategy_event_window_" + _stable_id(DATASET_ID, source_event_id, role),
        "source_event_id": source_event_id,
        "event_source_dataset_id": SOURCE_EVENT_DATASET_ID,
        "event_family": event.event_family,
        "event_type": event.event_type,
        "event_code": event.event_definition_id,
        "event_source": getattr(event, "source_candidate_dataset_id", SOURCE_EVENT_DATASET_ID),
        "ticker": event.ticker,
        "instrument_id": event.instrument_id,
        "issuer_name": None,
        "listing_exchange": getattr(event, "listing_exchange", None),
        "session_date": _date(event.session_date),
        "year": int(pd.Timestamp(event.session_date).year),
        "month": int(pd.Timestamp(event.session_date).month),
        "event_time_utc": _iso(event_time),
        "resume_trade_utc": None,
        "event_session_phase": "daily_session_close_available",
        "window_role": role,
        "window_start_utc": _iso(start_ts),
        "window_end_utc": _iso(end_ts),
        "window_duration_minutes": float((end_ts - start_ts).total_seconds() / 60.0),
        "window_start_source": start_source,
        "window_end_source": end_source,
        "contains_event_time": contains_event_time,
        "contains_post_event_information": contains_post_event,
        "leakage_safe_as_pre_event_feature": leakage_safe,
        "source_event_quality_state": event.event_quality_state,
        "source_halt_event_state": "not_applicable_daily_strategy_event",
        "source_resume_trade_observed": False,
        "event_response_end_observed": False,
        "event_window_quality_state": "good",
        "event_window_consumption_state": consumption,
        "session_open_utc": _iso(event.open_utc),
        "session_close_utc": _iso(event.close_utc),
        "session_minutes": int(event.session_minutes),
        "is_early_close": bool(event.is_early_close),
        "calendar": event.calendar,
        "timezone": event.timezone,
        "previous_session_date": None
        if pd.isna(event.previous_session_date)
        else _date(event.previous_session_date),
        "next_session_date": None if pd.isna(event.next_session_date) else _date(event.next_session_date),
        "instrument_identity_temporal_match": bool(event.instrument_identity_temporal_match),
        "is_common_stock": bool(event.is_common_stock),
        "is_lt1b_operational": bool(event.is_lt1b_operational),
        "lt1b_classification_1b": "lt1b_operational_true" if bool(event.is_lt1b_operational) else "not_lt1b",
        "valid_for_event_engine": True,
        "valid_for_microstructure_feature_candidate": False,
        "valid_for_ml_feature_candidate": valid_for_ml,
        "valid_for_outcome_window_candidate": valid_for_outcome,
        "valid_for_backtest_event_window_candidate": True,
        "valid_for_rl_state_component_candidate": False,
        "requires_decision_time_availability_contract": True,
        "full_universe_claim": False,
    }


def _build_windows(events: pd.DataFrame, calendar: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    base = events.merge(calendar, on="session_date", how="left")
    source_event_count = int(events["event_id"].nunique())
    calendar_covered = base[base["open_utc"].notna() & base["close_utc"].notna()].copy()
    rows: list[dict[str, Any]] = []

    for event in calendar_covered.itertuples(index=False):
        candidates = [
            _window_row(
                event,
                "prior_session_regular",
                event.previous_open_utc,
                event.previous_close_utc,
                "previous_session_open_utc",
                "previous_session_close_utc",
            ),
            _window_row(
                event,
                "event_session_regular",
                event.open_utc,
                event.close_utc,
                "event_session_open_utc",
                "event_session_close_utc",
            ),
            _window_row(
                event,
                "next_session_regular",
                event.next_open_utc,
                event.next_close_utc,
                "next_session_open_utc",
                "next_session_close_utc",
            ),
        ]
        rows.extend(row for row in candidates if row is not None)

    output = pd.DataFrame(rows)
    validations = {
        "source_event_count": source_event_count,
        "calendar_covered_event_count": int(calendar_covered["event_id"].nunique()),
        "excluded_no_market_calendar_session_event_count": source_event_count
        - int(calendar_covered["event_id"].nunique()),
        "source_valid_intraday_event_count": 0,
        "identity_temporal_match_event_count": int(calendar_covered["event_id"].nunique()),
        "excluded_no_temporal_identity_event_count": 0,
        "duplicate_identity_candidate_rows": 0,
    }
    return output, validations


def _validate_output(output: pd.DataFrame) -> dict[str, Any]:
    hard_failures: list[str] = []
    if output.empty:
        hard_failures.append("empty_output")
    if output["event_window_id"].duplicated().any():
        hard_failures.append("duplicate_event_window_id")
    if output["full_universe_claim"].any():
        hard_failures.append("full_universe_claim_true")
    if output["valid_for_rl_state_component_candidate"].any():
        hard_failures.append("rl_state_component_candidate_true")
    bad_ml = output["valid_for_ml_feature_candidate"] & ~output["leakage_safe_as_pre_event_feature"]
    if bad_ml.any():
        hard_failures.append("ml_feature_not_leakage_safe")
    bad_post_ml = output["valid_for_ml_feature_candidate"] & output["contains_post_event_information"]
    if bad_post_ml.any():
        hard_failures.append("ml_feature_contains_post_event_information")
    return {
        "hard_failures": hard_failures,
        "hard_fail_count": len(hard_failures),
        "status": "passed" if not hard_failures else "failed",
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

    events = _read_events(args.source_events)
    calendar = _read_calendar(args.market_calendar)
    output, source_validations = _build_windows(events, calendar)
    validation = _validate_output(output)
    if validation["hard_fail_count"]:
        raise ValueError(f"Event windows candidate validation failed: {validation['hard_failures']}")

    output["materialization_scope"] = MATERIALIZATION_SCOPE
    output["quality_policy_version"] = QUALITY_POLICY_VERSION
    output["schema_version"] = SCHEMA_VERSION
    output["build_run_id"] = args.run_id
    output["created_at_utc"] = args.created_at_utc
    source_events_sha = _sha256_file(args.source_events)
    market_calendar_sha = _sha256_file(args.market_calendar)
    output["source_halts_table_path"] = args.source_events.as_posix()
    output["source_halts_table_sha256"] = source_events_sha
    output["source_instrument_master_path"] = "not_applicable_source_event_identity_already_resolved"
    output["source_instrument_master_sha256"] = None
    output["source_market_calendar_path"] = args.market_calendar.as_posix()
    output["source_market_calendar_sha256"] = market_calendar_sha
    output["source_event_table_path"] = args.source_events.as_posix()
    output["source_event_table_sha256"] = source_events_sha

    dataset_dir = args.output_root / "event_windows_table_v0_1_candidate_daily_strategy_events"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    output_path = dataset_dir / "data.parquet"
    manifest_path = args.output_root / "_event_windows_table_v0_1_candidate_daily_strategy_events_manifest.json"
    summary_path = args.output_root / "_event_windows_table_v0_1_candidate_daily_strategy_events_summary.csv"
    output.to_parquet(output_path, index=False)
    output_sha = _sha256_file(output_path)

    validations = {
        **source_validations,
        "row_count": int(len(output)),
        "unique_event_window_id_count": int(output["event_window_id"].nunique()),
        "duplicate_event_window_id_count": int(output["event_window_id"].duplicated().sum()),
        "ticker_count": int(output["ticker"].nunique()),
        "instrument_count": int(output["instrument_id"].nunique()),
        "window_role_counts": {str(k): int(v) for k, v in output["window_role"].value_counts().items()},
        "event_window_quality_state_counts": {
            str(k): int(v) for k, v in output["event_window_quality_state"].value_counts().items()
        },
        "ml_feature_candidate_rows": int(output["valid_for_ml_feature_candidate"].sum()),
        "outcome_window_candidate_rows": int(output["valid_for_outcome_window_candidate"].sum()),
        "microstructure_feature_candidate_rows": int(output["valid_for_microstructure_feature_candidate"].sum()),
        "backtest_event_window_candidate_rows": int(output["valid_for_backtest_event_window_candidate"].sum()),
        "rl_state_component_candidate_rows": int(output["valid_for_rl_state_component_candidate"].sum()),
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()),
        "validator_status": validation["status"],
        "validator_hard_fail_count": validation["hard_fail_count"],
    }
    _write_summary(summary_path, validations)

    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "promotion_level": "controlled_candidate_not_promoted",
        "materialization_scope": MATERIALIZATION_SCOPE,
        "source_event_dataset_id": SOURCE_EVENT_DATASET_ID,
        "full_universe_claim": False,
        "build_run_id": args.run_id,
        "created_at_utc": args.created_at_utc,
        "output_path": output_path.as_posix(),
        "output_sha256": output_sha,
        "summary_path": summary_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "source_event_table": args.source_events.as_posix(),
        "source_event_table_sha256": source_events_sha,
        "source_event_manifest": args.source_events_manifest.as_posix() if args.source_events_manifest else None,
        "source_event_manifest_sha256": _sha256_file(args.source_events_manifest)
        if args.source_events_manifest
        else None,
        "source_market_calendar": args.market_calendar.as_posix(),
        "source_market_calendar_sha256": market_calendar_sha,
        "source_market_calendar_manifest": args.market_calendar_manifest.as_posix()
        if args.market_calendar_manifest
        else None,
        "source_market_calendar_manifest_sha256": _sha256_file(args.market_calendar_manifest)
        if args.market_calendar_manifest
        else None,
        "window_roles": ["prior_session_regular", "event_session_regular", "next_session_regular"],
        "contract_caveat": (
            "Candidate extension for daily strategy events. It reuses the event_windows "
            "schema surface but is not the official halts-only event_windows_table_v0_1."
        ),
        "validations": validations,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize controlled daily strategy event windows.")
    parser.add_argument("--source-events", type=Path, required=True)
    parser.add_argument("--source-events-manifest", type=Path)
    parser.add_argument("--market-calendar", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument("--market-calendar-manifest", type=Path, default=DEFAULT_MARKET_CALENDAR_MANIFEST)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--created-at-utc", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    args.run_id = args.run_id or _run_id()
    args.created_at_utc = args.created_at_utc or _utc_now()
    for path in (args.source_events, args.market_calendar):
        if not path.exists():
            raise FileNotFoundError(path)
    return args


def main(argv: Iterable[str] | None = None) -> int:
    manifest = build(parse_args(argv))
    print("Daily strategy event windows candidate materialization completed.")
    print(f"Dataset: {manifest['output_path']}")
    print(f"Manifest: {manifest['manifest_path']}")
    print(f"Rows: {manifest['validations']['row_count']}")
    print(f"Validator: {manifest['validations']['validator_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
