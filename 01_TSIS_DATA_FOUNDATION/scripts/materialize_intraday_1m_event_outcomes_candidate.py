from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "outcomes_table_v0_1_candidate"
PHYSICAL_DATASET_ID = "outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_controlled"
SCHEMA_VERSION = "outcomes_table_v0_1_candidate_intraday_1m_quote_guarded"
BUILDER_VERSION = "intraday_1m_event_outcomes_builder_candidate_v0_1"
MATERIALIZATION_SCOPE = "intraday_1m_quote_guarded_post_event_outcomes_controlled_candidate"
QUALITY_POLICY_VERSION = "outcomes_intraday_1m_quote_guarded_policy_v0_1"
OUTCOME_HORIZON = "post_event_30m_intraday_1m"
PRICE_VIEW = "1m_quote_guarded_raw"

DEFAULT_EVENT_STATE = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/"
    "event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled/data.parquet"
)
DEFAULT_EVENT_STATE_MANIFEST = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/event_state_intraday_1m_quote_guarded_controlled/"
    "_event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled_manifest.json"
)
DEFAULT_EVENT_WINDOWS = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/"
    "event_windows_table_v0_1_candidate_intraday_1m_strategy_events/data.parquet"
)
DEFAULT_EVENT_WINDOWS_MANIFEST = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/intraday_1m_strategy_event_windows_from_5_events_controlled/"
    "_event_windows_table_v0_1_candidate_intraday_1m_strategy_events_manifest.json"
)
DEFAULT_MASTER_INTRADAY = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet"
)
DEFAULT_MASTER_INTRADAY_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json"
)
DEFAULT_OUTPUT_ROOT = Path("C:/TSIS_Data/tests/test_runs/2026-07-05/outcomes_intraday_1m_quote_guarded_controlled")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "intraday_1m_event_outcomes_candidate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


def _iso(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _pct(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or pd.isna(numerator) or pd.isna(denominator) or denominator <= 0:
        return None
    return ((float(numerator) / float(denominator)) - 1.0) * 100.0


def _json_bundle(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _read_event_state(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {
        "event_state_id",
        "event_id",
        "event_window_id",
        "market_state_id",
        "instrument_id",
        "ticker",
        "event_family",
        "event_timestamp_utc",
        "decision_timestamp_utc",
        "decision_date",
        "state_role",
        "state_quality_state",
        "event_window_start_utc",
        "event_window_end_utc",
        "event_source_dataset_id",
        "event_source_quality_state",
        "full_universe_claim",
        "execution_truth",
        "build_run_id",
        "intraday__last_closed_bar_close",
        "intraday__price_view",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required event_state columns: {missing}")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        raise ValueError("Refusing event_state rows with full_universe_claim=true")
    if frame["execution_truth"].fillna(False).astype(bool).any():
        raise ValueError("Refusing event_state rows with execution_truth=true")

    frame = frame.copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame["event_timestamp_utc_ts"] = pd.to_datetime(frame["event_timestamp_utc"], utc=True)
    frame["decision_timestamp_utc_ts"] = pd.to_datetime(frame["decision_timestamp_utc"], utc=True)
    frame["event_window_start_utc_ts"] = pd.to_datetime(frame["event_window_start_utc"], utc=True)
    frame["event_window_end_utc_ts"] = pd.to_datetime(frame["event_window_end_utc"], utc=True)
    return frame.sort_values(["ticker", "event_id", "state_role", "decision_timestamp_utc_ts"]).reset_index(drop=True)


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
        "window_duration_minutes",
        "contains_post_event_information",
        "valid_for_outcome_window_candidate",
        "full_universe_claim",
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
    return frame.sort_values(["ticker", "source_event_id", "window_start_utc_ts"]).reset_index(drop=True)


def _read_master_intraday(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {
        "master_intraday_bar_id",
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
        "source_quote_guarded_repair_manifest",
        "source_quote_guarded_run_id",
        "full_universe_claim",
        "execution_truth",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required master_intraday columns: {missing}")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        raise ValueError("Refusing master_intraday rows with full_universe_claim=true")
    if frame["execution_truth"].fillna(False).astype(bool).any():
        raise ValueError("Refusing master_intraday rows with execution_truth=true")

    frame = frame[frame["price_view"].eq(PRICE_VIEW)].copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame["ts_utc_ts"] = pd.to_datetime(frame["ts_utc"], utc=True)
    frame["bar_end_utc_ts"] = frame["ts_utc_ts"] + pd.Timedelta(minutes=1)
    return frame.sort_values(["ticker", "ts_utc_ts", "master_intraday_bar_id"]).reset_index(drop=True)


def _quality_state(reference_price: float | None, bars: pd.DataFrame, expected_bars: int) -> str:
    if reference_price is None or pd.isna(reference_price) or float(reference_price) <= 0:
        return "review_missing_reference_price"
    if bars.empty:
        return "review_empty_outcome_window"
    prices = bars[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    if prices.isna().any(axis=None) or (prices <= 0).any(axis=None):
        return "review_invalid_reference_or_outcome_price"
    if len(bars) < expected_bars:
        return "review_intraday_missing_bars"
    return "good_intraday_1m_outcome"


def _window_outcome_metrics(bars: pd.DataFrame, reference_price: float | None) -> dict[str, Any]:
    if bars.empty:
        return {
            "outcome_open": None,
            "outcome_high": None,
            "outcome_low": None,
            "outcome_close": None,
            "outcome_volume": 0.0,
            "outcome_dollar_volume": 0.0,
            "outcome_vwap": None,
            "outcome_transaction_count": 0,
            "first_outcome_bar_ts_utc": None,
            "last_outcome_bar_ts_utc": None,
            "reference_to_outcome_open_return_pct": None,
            "reference_to_outcome_high_return_pct": None,
            "reference_to_outcome_low_return_pct": None,
            "reference_to_outcome_close_return_pct": None,
            "mfe_pct": None,
            "mae_pct": None,
            "outcome_open_to_close_return_pct": None,
            "outcome_range_pct": None,
        }

    first = bars.iloc[0]
    last = bars.iloc[-1]
    high = float(pd.to_numeric(bars["high"], errors="coerce").max())
    low = float(pd.to_numeric(bars["low"], errors="coerce").min())
    open_ = float(first["open"]) if pd.notna(first["open"]) else None
    close = float(last["close"]) if pd.notna(last["close"]) else None
    volume = float(pd.to_numeric(bars["volume"], errors="coerce").fillna(0).sum())
    dollar_volume = float((pd.to_numeric(bars["close"], errors="coerce") * pd.to_numeric(bars["volume"], errors="coerce")).fillna(0).sum())
    transaction_count = int(pd.to_numeric(bars["transaction_count"], errors="coerce").fillna(0).sum())
    vwap_numerator = (
        pd.to_numeric(bars["vwap"], errors="coerce") * pd.to_numeric(bars["volume"], errors="coerce")
    ).sum()
    outcome_vwap = float(vwap_numerator / volume) if volume > 0 and pd.notna(vwap_numerator) else None

    return {
        "outcome_open": open_,
        "outcome_high": high,
        "outcome_low": low,
        "outcome_close": close,
        "outcome_volume": volume,
        "outcome_dollar_volume": dollar_volume,
        "outcome_vwap": outcome_vwap,
        "outcome_transaction_count": transaction_count,
        "first_outcome_bar_ts_utc": _iso(first["ts_utc_ts"]),
        "last_outcome_bar_ts_utc": _iso(last["ts_utc_ts"]),
        "reference_to_outcome_open_return_pct": _pct(open_, reference_price),
        "reference_to_outcome_high_return_pct": _pct(high, reference_price),
        "reference_to_outcome_low_return_pct": _pct(low, reference_price),
        "reference_to_outcome_close_return_pct": _pct(close, reference_price),
        "mfe_pct": _pct(high, reference_price),
        "mae_pct": _pct(low, reference_price),
        "outcome_open_to_close_return_pct": _pct(close, open_),
        "outcome_range_pct": _pct(high, low),
    }


def _validate_output(frame: pd.DataFrame) -> dict[str, Any]:
    hard_failures: list[str] = []
    if frame.empty:
        hard_failures.append("empty_output")
    if frame["outcome_id"].duplicated().any():
        hard_failures.append("duplicate_outcome_id")
    key_dupes = frame.duplicated(["event_window_id", "outcome_horizon", "price_view"])
    if key_dupes.any():
        hard_failures.append("duplicate_event_window_horizon_price_view")
    if not frame["contains_post_event_information"].fillna(False).astype(bool).all():
        hard_failures.append("missing_post_event_information_flag")
    if not frame["prohibited_as_pre_event_feature"].fillna(False).astype(bool).all():
        hard_failures.append("missing_pre_event_prohibition_flag")
    if frame["valid_for_rl_reward_candidate"].fillna(False).astype(bool).any():
        hard_failures.append("rl_reward_candidate_enabled_without_reward_contract")
    if frame["valid_for_ml_label_candidate"].fillna(False).astype(bool).any():
        hard_failures.append("ml_label_candidate_enabled_without_label_contract")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        hard_failures.append("full_universe_claim_true")
    if frame["execution_truth"].fillna(False).astype(bool).any():
        hard_failures.append("execution_truth_true")

    good = frame["outcome_quality_state"].eq("good_intraday_1m_outcome")
    if good.any():
        numeric_required = [
            "reference_price",
            "outcome_open",
            "outcome_high",
            "outcome_low",
            "outcome_close",
            "reference_to_outcome_close_return_pct",
            "mfe_pct",
            "mae_pct",
        ]
        if frame.loc[good, numeric_required].isna().any(axis=None):
            hard_failures.append("good_outcome_missing_numeric_fields")

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

    event_state = _read_event_state(args.event_state)
    event_windows = _read_event_windows(args.event_windows)
    master = _read_master_intraday(args.master_intraday)
    event_state_manifest = _read_json(args.event_state_manifest)
    event_windows_manifest = _read_json(args.event_windows_manifest)
    master_intraday_manifest = _read_json(args.master_intraday_manifest)

    post_windows = event_windows[
        event_windows["window_role"].eq("post_event_30m")
        & event_windows["valid_for_outcome_window_candidate"].fillna(False).astype(bool)
    ].copy()
    post_state = event_state[event_state["state_role"].eq("post_event_review")].copy()
    anchor_state = event_state[event_state["state_role"].eq("at_event")].copy()

    if len(post_windows) != len(post_state):
        missing = set(post_windows["event_window_id"]) - set(post_state["event_window_id"])
        if missing:
            raise ValueError(f"Missing post_event_review event_state rows for windows: {sorted(missing)}")

    anchor_by_event = {row["event_id"]: row for _, row in anchor_state.iterrows()}
    master_by_ticker = {ticker: group.reset_index(drop=True) for ticker, group in master.groupby("ticker")}
    post_state_by_window = {row["event_window_id"]: row for _, row in post_state.iterrows()}

    rows: list[dict[str, Any]] = []
    for _, window in post_windows.iterrows():
        state = post_state_by_window.get(window["event_window_id"])
        if state is None:
            continue
        anchor = anchor_by_event.get(state["event_id"])
        reference_price = None
        reference_event_state_id = None
        reference_market_state_id = None
        reference_decision_timestamp_utc = None
        if anchor is not None:
            reference_price = anchor.get("intraday__last_closed_bar_close")
            reference_event_state_id = anchor.get("event_state_id")
            reference_market_state_id = anchor.get("market_state_id")
            reference_decision_timestamp_utc = _iso(anchor.get("decision_timestamp_utc_ts"))

        ticker = str(window["ticker"])
        bars = master_by_ticker.get(ticker, pd.DataFrame())
        if not bars.empty:
            bars = bars[
                (bars["ts_utc_ts"] >= window["window_start_utc_ts"])
                & (bars["ts_utc_ts"] < window["window_end_utc_ts"])
            ].copy()
        expected_bars = int(window["window_duration_minutes"]) if pd.notna(window["window_duration_minutes"]) else 0
        quality_state = _quality_state(reference_price, bars, expected_bars)
        metrics = _window_outcome_metrics(bars, reference_price)
        good = quality_state == "good_intraday_1m_outcome"
        repair_rows = int(bars["quote_guarded_repair_applied"].fillna(False).astype(bool).sum()) if not bars.empty else 0

        row = {
            "outcome_id": "outcome_intraday_" + _stable_id(window["event_window_id"], OUTCOME_HORIZON, PRICE_VIEW),
            "event_window_id": window["event_window_id"],
            "source_event_state_id": state["event_state_id"],
            "reference_event_state_id": reference_event_state_id,
            "reference_market_state_id": reference_market_state_id,
            "event_id": state["event_id"],
            "event_source_dataset_id": window["event_source_dataset_id"],
            "event_family": window["event_family"],
            "event_type": window["event_type"],
            "event_code": window["event_code"],
            "event_source": window["event_source"],
            "ticker": ticker,
            "instrument_id": window["instrument_id"],
            "session_date": str(window["session_date"]),
            "event_time_utc": _iso(window["event_time_utc_ts"]),
            "event_window_start_utc": _iso(window["window_start_utc_ts"]),
            "event_window_end_utc": _iso(window["window_end_utc_ts"]),
            "outcome_window_start_utc": _iso(window["window_start_utc_ts"]),
            "outcome_window_end_utc": _iso(window["window_end_utc_ts"]),
            "outcome_window_duration_minutes": expected_bars,
            "outcome_horizon": OUTCOME_HORIZON,
            "price_view": PRICE_VIEW,
            "reference_price": float(reference_price) if reference_price is not None and pd.notna(reference_price) else None,
            "reference_price_source": "event_state_at_event_intraday__last_closed_bar_close",
            "reference_decision_timestamp_utc": reference_decision_timestamp_utc,
            "bars_expected": expected_bars,
            "bars_observed": int(len(bars)),
            "bars_missing": max(expected_bars - int(len(bars)), 0),
            "quote_guarded_repair_applied_rows": repair_rows,
            "quote_guarded_repair_applied_any": repair_rows > 0,
            "repair_manifest_row_present_rows": int(bars["repair_manifest_row_present"].fillna(False).astype(bool).sum())
            if not bars.empty
            else 0,
            "source_master_intraday_bar_ids": "|".join(bars["master_intraday_bar_id"].astype(str).tolist())
            if not bars.empty
            else "",
            **metrics,
            "outcome_quality_state": quality_state,
            "valid_for_outcome_research": bool(good or quality_state == "review_intraday_missing_bars"),
            "valid_for_ml_label_candidate": False,
            "valid_for_strategy_label_candidate": False,
            "valid_for_backtest_outcome_candidate": bool(good),
            "valid_for_rl_reward_candidate": False,
            "contains_post_event_information": True,
            "prohibited_as_pre_event_feature": True,
            "requires_feature_label_separation": True,
            "full_universe_claim": False,
            "execution_truth": False,
            "label_columns_materialized": False,
            "reward_columns_materialized": False,
            "materialization_scope": MATERIALIZATION_SCOPE,
            "quality_policy_version": QUALITY_POLICY_VERSION,
            "schema_version": SCHEMA_VERSION,
            "builder_version": BUILDER_VERSION,
            "build_run_id": args.run_id,
            "created_at_utc": args.created_at_utc,
            "source_event_state_build_run_id": state.get("build_run_id"),
            "source_event_windows_build_run_id": window.get("build_run_id"),
            "source_master_intraday_schema_version": master_intraday_manifest.get("schema_version"),
            "source_master_intraday_quality_policy_version": master_intraday_manifest.get("quality_policy_version"),
            "component_manifest_hash_bundle": _json_bundle(
                {
                    "event_state_manifest_sha256": _sha256_file(args.event_state_manifest),
                    "event_windows_manifest_sha256": _sha256_file(args.event_windows_manifest),
                    "master_intraday_manifest_sha256": _sha256_file(args.master_intraday_manifest),
                }
            ),
            "source_event_state_path": args.event_state.as_posix(),
            "source_event_state_sha256": _sha256_file(args.event_state),
            "source_event_windows_path": args.event_windows.as_posix(),
            "source_event_windows_sha256": _sha256_file(args.event_windows),
            "source_master_intraday_path": args.master_intraday.as_posix(),
            "source_master_intraday_sha256": _sha256_file(args.master_intraday),
            "source_master_intraday_manifest_path": args.master_intraday_manifest.as_posix()
            if args.master_intraday_manifest
            else None,
            "source_quote_guarded_repair_manifest": master_intraday_manifest.get(
                "source_quote_guarded_repair_manifest",
                "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet",
            ),
            "source_quote_guarded_run_id": master_intraday_manifest.get("source_quote_guarded_run_id"),
        }
        rows.append(row)

    output = pd.DataFrame(rows)
    validations = _validate_output(output)
    quality_counts = output["outcome_quality_state"].value_counts(dropna=False).sort_index().to_dict()
    stats = {
        "dataset_id": DATASET_ID,
        "physical_dataset_id": PHYSICAL_DATASET_ID,
        "status": "controlled_candidate_not_promoted",
        "source_event_state_rows": int(len(event_state)),
        "source_event_window_rows": int(len(event_windows)),
        "post_event_window_rows": int(len(post_windows)),
        "reference_anchor_event_state_rows": int(len(anchor_state)),
        "outcome_rows": int(len(output)),
        "event_count": int(output["event_id"].nunique()) if not output.empty else 0,
        "ticker_count": int(output["ticker"].nunique()) if not output.empty else 0,
        "outcome_horizon": OUTCOME_HORIZON,
        "price_view": PRICE_VIEW,
        "quality_counts": quality_counts,
        "good_intraday_1m_outcome_rows": int(output["outcome_quality_state"].eq("good_intraday_1m_outcome").sum())
        if not output.empty
        else 0,
        "review_intraday_missing_bars_rows": int(output["outcome_quality_state"].eq("review_intraday_missing_bars").sum())
        if not output.empty
        else 0,
        "valid_for_outcome_research_rows": int(output["valid_for_outcome_research"].sum()) if not output.empty else 0,
        "valid_for_backtest_outcome_candidate_rows": int(output["valid_for_backtest_outcome_candidate"].sum())
        if not output.empty
        else 0,
        "valid_for_ml_label_candidate_rows": int(output["valid_for_ml_label_candidate"].sum()) if not output.empty else 0,
        "valid_for_rl_reward_candidate_rows": int(output["valid_for_rl_reward_candidate"].sum()) if not output.empty else 0,
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()) if not output.empty else 0,
        "execution_truth_rows": int(output["execution_truth"].sum()) if not output.empty else 0,
        "bars_expected_total": int(output["bars_expected"].sum()) if not output.empty else 0,
        "bars_observed_total": int(output["bars_observed"].sum()) if not output.empty else 0,
        "quote_guarded_repair_applied_rows_total": int(output["quote_guarded_repair_applied_rows"].sum())
        if not output.empty
        else 0,
        **validations,
    }

    dataset_root = args.output_root / PHYSICAL_DATASET_ID
    dataset_root.mkdir(parents=True, exist_ok=True)
    output_path = dataset_root / "data.parquet"
    output.to_parquet(output_path, index=False)
    summary_path = args.output_root / "_outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_summary.csv"
    manifest_path = args.output_root / "_outcomes_table_v0_1_candidate_intraday_1m_quote_guarded_manifest.json"
    _write_summary(summary_path, stats)

    manifest = {
        **stats,
        "validations": validations | {
            "outcome_quality_state_counts": quality_counts,
            "duplicate_outcome_id_count": int(output["outcome_id"].duplicated().sum()) if not output.empty else 0,
            "duplicate_grain_count": int(output.duplicated(["event_window_id", "outcome_horizon", "price_view"]).sum())
            if not output.empty
            else 0,
        },
        "output_path": output_path.as_posix(),
        "summary_path": summary_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "source_event_state_path": args.event_state.as_posix(),
        "source_event_state_manifest_path": args.event_state_manifest.as_posix() if args.event_state_manifest else None,
        "source_event_windows_path": args.event_windows.as_posix(),
        "source_event_windows_manifest_path": args.event_windows_manifest.as_posix() if args.event_windows_manifest else None,
        "source_master_intraday_path": args.master_intraday.as_posix(),
        "source_master_intraday_manifest_path": args.master_intraday_manifest.as_posix()
        if args.master_intraday_manifest
        else None,
        "source_event_state_manifest": event_state_manifest,
        "source_event_windows_manifest": event_windows_manifest,
        "source_master_intraday_manifest": master_intraday_manifest,
        "contracts": {
            "schema": "01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md",
            "validators": "01_foundations/validators/outputs/outcomes_table_validators.md",
            "lineage": "01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1.md",
            "event_state_lineage": (
                "01_foundations/module_contracts/outputs/"
                "state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md"
            ),
            "state_builder_contract": "01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md",
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    if validations["validator_status"] != "passed":
        raise ValueError(f"Output validation failed: {validations}")
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-state", type=Path, default=DEFAULT_EVENT_STATE)
    parser.add_argument("--event-state-manifest", type=Path, default=DEFAULT_EVENT_STATE_MANIFEST)
    parser.add_argument("--event-windows", type=Path, default=DEFAULT_EVENT_WINDOWS)
    parser.add_argument("--event-windows-manifest", type=Path, default=DEFAULT_EVENT_WINDOWS_MANIFEST)
    parser.add_argument("--master-intraday", type=Path, default=DEFAULT_MASTER_INTRADAY)
    parser.add_argument("--master-intraday-manifest", type=Path, default=DEFAULT_MASTER_INTRADAY_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-id", default=_run_id())
    parser.add_argument("--created-at-utc", default=_utc_now())
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    manifest = build(args)
    print(json.dumps({"status": "ok", "manifest_path": manifest["manifest_path"], "rows": manifest["outcome_rows"]}))


if __name__ == "__main__":
    main()
