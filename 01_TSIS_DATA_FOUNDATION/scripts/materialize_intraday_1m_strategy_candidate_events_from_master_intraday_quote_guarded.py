from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import pandas as pd

import materialize_strategy_candidate_events_table as event_builder


SOURCE_DATASET_ID = "master_intraday_bar_table_v0_2_candidate_quote_guarded_session_threshold_adapter_v0_1"
MATERIALIZATION_SCOPE = "intraday_1m_quote_guarded_first_motion_controlled_candidate"
EVENT_DEFINITION_ID = "intraday_1m_first_session_open_move_pct_ge_50_candidate_v0_1"
EVENT_DEFINITION_VERSION = "v0_1"
EVENT_FAMILY = "intraday_first_motion_threshold_cross_candidate"
EVENT_TYPE = "first_motion_threshold_cross"
EVENT_ANCHOR_ROLE = "trigger_bar_close"
EVENT_TIMESTAMP_POLICY = "closed_1m_bar"

DEFAULT_MASTER_INTRADAY_PARQUET = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "master_intraday_bar_table_v0_2_candidate_quote_guarded/data.parquet"
)
DEFAULT_MASTER_INTRADAY_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table/"
    "_master_intraday_bar_table_v0_2_candidate_quote_guarded_manifest.json"
)
DEFAULT_QG_REPAIR_MANIFEST = Path(
    "E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet"
)
DEFAULT_OUTPUT_ROOT = Path(
    "C:/TSIS_Data/tests/test_runs/2026-07-05/"
    "intraday_1m_strategy_candidate_events_from_master_intraday_qg_controlled"
)

REQUIRED_COLUMNS = {
    "master_intraday_bar_id",
    "ticker",
    "instrument_id",
    "ts_utc",
    "session_date",
    "price_view",
    "open",
    "high",
    "close",
    "volume",
    "vwap",
    "quote_guarded_repair_applied",
    "repair_manifest_row_present",
    "repair_state",
    "repair_reason",
    "qg_ohlc_changed",
    "source_ohlcv_path",
    "source_quotes_path",
    "source_quote_guarded_run_id",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _run_id() -> str:
    return "intraday_1m_strategy_candidate_events_qg_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_id(*parts: Any, length: int = 18) -> str:
    payload = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def _iso_z(value: Any) -> str:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC").replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    return bool(value)


def _session_phase(ts_utc: Any) -> str:
    ny = pd.Timestamp(ts_utc).tz_convert(ZoneInfo("America/New_York"))
    minutes = ny.hour * 60 + ny.minute
    if 4 * 60 <= minutes < 9 * 60 + 30:
        return "premarket"
    if 9 * 60 + 30 <= minutes < 16 * 60:
        return "regular"
    return "afterhours"


def _safe_reset_output_root(output_root: Path, overwrite: bool) -> None:
    if not output_root.exists():
        output_root.mkdir(parents=True, exist_ok=True)
        return
    if any(output_root.iterdir()) and not overwrite:
        raise FileExistsError(f"Output root already exists and is not empty: {output_root}")
    if overwrite:
        resolved = output_root.resolve()
        expected = Path("C:/TSIS_Data/tests/test_runs").resolve()
        if expected not in resolved.parents and resolved != expected:
            raise RuntimeError(f"refusing to delete outside tests/test_runs: {resolved}")
        shutil.rmtree(resolved)
    output_root.mkdir(parents=True, exist_ok=True)


def _read_master_intraday(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"master intraday candidate missing columns: {missing}")
    frame = frame.copy()
    frame["ticker"] = frame["ticker"].astype(str).str.upper().str.strip()
    frame["ts_norm"] = pd.to_datetime(frame["ts_utc"], utc=True)
    return frame.sort_values(["ticker", "session_date", "ts_norm", "price_view"]).reset_index(drop=True)


def _dollar_value(frame: pd.DataFrame) -> pd.Series:
    price = frame["vwap"].fillna(frame["close"]).astype(float)
    return price * frame["volume"].astype(float)


def build_source_candidates(
    frame: pd.DataFrame,
    *,
    threshold_pct: float,
    run_id: str,
    created_at_utc: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    qg = frame[frame["price_view"].eq("1m_quote_guarded_raw")].copy()
    raw = frame[frame["price_view"].eq("1m_raw")].copy()
    if qg.empty:
        raise ValueError("No 1m_quote_guarded_raw rows found")

    raw_grouped = {(ticker, session): group.copy() for (ticker, session), group in raw.groupby(["ticker", "session_date"])}
    rows: list[dict[str, Any]] = []
    selected_count = 0
    for (ticker, session_date), group in qg.groupby(["ticker", "session_date"], sort=True):
        group = group.sort_values("ts_norm").reset_index(drop=True)
        first_open = float(group.iloc[0]["open"])
        threshold_price = first_open * (1.0 + threshold_pct / 100.0)
        hit = group[group["high"].astype(float) >= threshold_price]
        selected = not hit.empty
        event = hit.iloc[0] if selected else group.iloc[-1]
        event_ts = pd.Timestamp(event["ts_norm"])
        through_event = group[group["ts_norm"] <= event_ts]
        raw_group = raw_grouped.get((ticker, session_date), pd.DataFrame())
        raw_event_detected = False
        if not raw_group.empty:
            raw_event_detected = bool((raw_group["high"].astype(float) >= threshold_price).any())
        selected_count += int(selected)
        instrument_id = event.get("instrument_id")
        if pd.isna(instrument_id) or instrument_id in (None, ""):
            instrument_id = f"ticker:{ticker}"
        move_pct = (float(event["high"]) / first_open - 1.0) * 100.0
        dollar_to_time = float(_dollar_value(through_event).sum())
        volume_to_time = float(through_event["volume"].astype(float).sum())
        candidate_id = "intraday_qg_session_threshold_" + _stable_id(
            SOURCE_DATASET_ID, ticker, session_date, threshold_pct
        )
        rows.append(
            {
                "intraday_scanner_candidate_id": candidate_id,
                "scanner_run_id": run_id,
                "scanner_definition_id": "master_intraday_qg_session_threshold_adapter_v0_1",
                "scanner_definition_version": "adapter_v0_1",
                "build_run_id": run_id,
                "source_candidate_build_run_id": run_id,
                "source_candidate_quality_state": "usable_candidate" if selected else "not_selected",
                "instrument_id": str(instrument_id),
                "ticker": ticker,
                "session_date": str(session_date),
                "is_common_stock": True,
                "is_lt1b_operational": True,
                "instrument_identity_temporal_match": True,
                "calendar_session_valid": True,
                "selected_intraday_in_play_candidate": bool(selected),
                "motion_threshold_passed": bool(selected),
                "quote_guarded_event_confirmed": bool(selected),
                "raw_event_detected": bool(raw_event_detected),
                "raw_only_rejected_reason": None,
                "quote_guarded_repair_applied_at_event": _bool(event.get("quote_guarded_repair_applied")),
                "repair_state_at_event": event.get("repair_state"),
                "repair_reason_at_event": event.get("repair_reason"),
                "first_cross_50_ts_utc": _iso_z(event_ts) if selected else None,
                "event_bar_ts_utc": _iso_z(event_ts) if selected else None,
                "event_bar_end_utc": _iso_z(event_ts + pd.Timedelta(minutes=1)) if selected else None,
                "as_of_utc": _iso_z(event_ts + pd.Timedelta(minutes=1)) if selected else None,
                "event_availability_utc": _iso_z(event_ts + pd.Timedelta(minutes=1)) if selected else None,
                "detection_timestamp_utc": _iso_z(event_ts + pd.Timedelta(minutes=1)) if selected else None,
                "source_data_availability_cutoff_utc": _iso_z(event_ts + pd.Timedelta(minutes=1))
                if selected
                else None,
                "first_cross_50_ts_et": pd.Timestamp(event_ts)
                .tz_convert(ZoneInfo("America/New_York"))
                .isoformat()
                if selected
                else None,
                "first_cross_50_segment": _session_phase(event_ts) if selected else None,
                "event_session_phase": _session_phase(event_ts) if selected else None,
                "first_cross_price": float(event["high"]) if selected else None,
                "first_cross_move_vs_segment_open_pct": float(move_pct) if selected else None,
                "volume_to_time_at_first_cross": volume_to_time if selected else None,
                "dollar_volume_to_time_at_first_cross": dollar_to_time if selected else None,
                "bars_observed_to_first_cross": int(len(through_event)) if selected else None,
                "first_observed_bar_ts_utc": _iso_z(group.iloc[0]["ts_norm"]),
                "first_observed_open": first_open,
                "threshold_pct": float(threshold_pct),
                "threshold_price": float(threshold_price),
                "candidate_reasons": "first_session_open_move_pct_threshold_cross" if selected else "threshold_not_crossed",
                "scanner_selection_state": "selected" if selected else "not_selected",
                "trigger_source_bar_file": event.get("source_ohlcv_path") if selected else None,
                "first_cross_source_ohlcv_1m_file": event.get("source_ohlcv_path") if selected else None,
                "source_quotes_path": event.get("source_quotes_path") if selected else None,
                "source_quote_guarded_run_id": event.get("source_quote_guarded_run_id"),
                "source_master_intraday_bar_id": event.get("master_intraday_bar_id") if selected else None,
                "source_price_view": "ohlcv_1m_quote_guarded",
                "adapter_created_at_utc": created_at_utc,
            }
        )
    output = pd.DataFrame(rows)
    stats = {
        "source_quote_guarded_bar_rows": int(len(qg)),
        "source_raw_bar_rows": int(len(raw)),
        "source_session_count": int(output[["ticker", "session_date"]].drop_duplicates().shape[0]),
        "selected_source_row_count": int(selected_count),
        "threshold_pct": float(threshold_pct),
    }
    return output, stats


def build(args: argparse.Namespace) -> dict[str, Any]:
    _safe_reset_output_root(args.output_root, args.overwrite)
    run_id = args.run_id or _run_id()
    created_at_utc = args.created_at_utc or _utc_now()
    frame = _read_master_intraday(args.master_intraday_parquet)
    source_candidates, source_stats = build_source_candidates(
        frame,
        threshold_pct=args.threshold_pct,
        run_id=run_id,
        created_at_utc=created_at_utc,
    )
    source_path = args.output_root / "_intraday_1m_strategy_candidate_events_source_candidates.parquet"
    source_candidates.to_parquet(source_path, index=False)
    source_summary_path = args.output_root / "_intraday_1m_strategy_candidate_events_source_candidates_summary.json"
    source_summary_path.write_text(json.dumps(source_stats, indent=2, ensure_ascii=False), encoding="utf-8")

    qg_run_id = args.source_quote_guarded_run_id
    if qg_run_id is None:
        non_null = source_candidates["source_quote_guarded_run_id"].dropna().astype(str)
        qg_run_id = non_null.iloc[0] if not non_null.empty else run_id

    event_output_root = args.output_root / "event_candidate_table"
    event_args = event_builder.parse_args(
        [
            "--dataset-id",
            event_builder.INTRADAY_DATASET_ID,
            "--source-candidates",
            str(source_path),
            "--source-candidate-manifest",
            str(args.master_intraday_manifest),
            "--source-quote-guarded-repair-manifest",
            str(args.source_quote_guarded_repair_manifest),
            "--source-master-intraday-table-path",
            str(args.master_intraday_parquet),
            "--source-candidate-dataset-id",
            SOURCE_DATASET_ID,
            "--selection-column",
            "selected_intraday_in_play_candidate",
            "--event-definition-id",
            args.event_definition_id,
            "--event-definition-version",
            EVENT_DEFINITION_VERSION,
            "--event-family",
            EVENT_FAMILY,
            "--event-type",
            EVENT_TYPE,
            "--event-subtype",
            f"session_open_move_pct_ge_{args.threshold_pct:g}",
            "--event-anchor-role",
            EVENT_ANCHOR_ROLE,
            "--event-timestamp-policy",
            EVENT_TIMESTAMP_POLICY,
            "--source-scanner-definition-version",
            "adapter_v0_1",
            "--source-quote-guarded-run-id",
            qg_run_id,
            "--materialization-scope",
            MATERIALIZATION_SCOPE,
            "--output-root",
            str(event_output_root),
            "--run-id",
            run_id,
            "--created-at-utc",
            created_at_utc,
            "--overwrite",
        ]
    )
    event_manifest = event_builder.build(event_args)
    manifest_path = args.output_root / "_intraday_1m_strategy_candidate_events_from_master_intraday_qg_manifest.json"
    manifest = {
        "dataset_id": event_builder.INTRADAY_DATASET_ID,
        "adapter_source_dataset_id": SOURCE_DATASET_ID,
        "status": "controlled_candidate_not_promoted",
        "promotion_level": "controlled_candidate",
        "materialization_scope": MATERIALIZATION_SCOPE,
        "event_definition_id": args.event_definition_id,
        "event_definition_version": EVENT_DEFINITION_VERSION,
        "threshold_pct": float(args.threshold_pct),
        "build_run_id": run_id,
        "created_at_utc": created_at_utc,
        "source_candidates_path": source_path.as_posix(),
        "source_candidates_sha256": _sha256_file(source_path),
        "source_candidates_summary_path": source_summary_path.as_posix(),
        "source_stats": source_stats,
        "master_intraday_parquet": args.master_intraday_parquet.as_posix(),
        "master_intraday_manifest": args.master_intraday_manifest.as_posix(),
        "master_intraday_manifest_sha256": _sha256_file(args.master_intraday_manifest),
        "source_quote_guarded_repair_manifest": args.source_quote_guarded_repair_manifest.as_posix(),
        "source_quote_guarded_run_id": qg_run_id,
        "event_table_manifest": event_manifest["manifest_path"],
        "event_table_dataset": event_manifest["dataset_path"],
        "event_table_stats": event_manifest["stats"],
        "validator_summary": event_manifest["validator_summary"],
        "full_universe_claim": False,
        "ml_ready_dataset_enabled": False,
        "rl_training_dataset_enabled": False,
        "alphaevolve_evaluator_enabled": False,
        "non_goals": [
            "No materializa intraday_scanner_candidates_table_v0_2.",
            "No materializa market_state_table ni event_state_table.",
            "No contiene outcomes, labels, rewards, fills, PnL ni acciones.",
            "El umbral +50% vive como definicion candidata versionada, no como atributo base de estado.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return manifest


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build controlled intraday 1m strategy candidate events from "
            "master_intraday_bar_table_v0_2_candidate_quote_guarded."
        )
    )
    parser.add_argument("--master-intraday-parquet", type=Path, default=DEFAULT_MASTER_INTRADAY_PARQUET)
    parser.add_argument("--master-intraday-manifest", type=Path, default=DEFAULT_MASTER_INTRADAY_MANIFEST)
    parser.add_argument("--source-quote-guarded-repair-manifest", type=Path, default=DEFAULT_QG_REPAIR_MANIFEST)
    parser.add_argument("--source-quote-guarded-run-id")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--threshold-pct", type=float, default=50.0)
    parser.add_argument("--event-definition-id", default=EVENT_DEFINITION_ID)
    parser.add_argument("--run-id")
    parser.add_argument("--created-at-utc")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    for path in (args.master_intraday_parquet, args.master_intraday_manifest, args.source_quote_guarded_repair_manifest):
        if not path.exists():
            raise FileNotFoundError(path)
    return args


def main(argv: Iterable[str] | None = None) -> int:
    manifest = build(parse_args(argv))
    print(json.dumps({"source_stats": manifest["source_stats"], "event_table_stats": manifest["event_table_stats"]}, indent=2))
    print(f"Manifest: {manifest['event_table_manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
