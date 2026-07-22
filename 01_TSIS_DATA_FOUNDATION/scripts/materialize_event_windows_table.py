from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "event_windows_table_v0_1"
SCHEMA_VERSION = "event_windows_table_v0_1"
QUALITY_POLICY_VERSION = "event_windows_table_policy_v0_1"
MATERIALIZATION_SCOPE = "halts_intraday_lt1b_calendar_covered"
SOURCE_EVENT_DATASET_ID = "halts_table_v0_1"

DEFAULT_HALTS_TABLE = Path(r"E:\TSIS\data\data_foundation_outputs\halts_table\halts_table_v0_1.parquet")
DEFAULT_HALTS_MANIFEST = Path(r"E:\TSIS\data\data_foundation_outputs\halts_table\_halts_table_manifest_v0_1.json")
DEFAULT_INSTRUMENT_MASTER = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet"
)
DEFAULT_INSTRUMENT_MASTER_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\instrument_master\_instrument_master_manifest_v0_1.json"
)
DEFAULT_MARKET_CALENDAR = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\market_calendar_v0_1.parquet"
)
DEFAULT_MARKET_CALENDAR_MANIFEST = Path(
    r"E:\TSIS\data\data_foundation_outputs\market_calendar\_market_calendar_manifest_v0_1.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\event_windows_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/event_windows_table_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/event_windows_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/event_windows_table_validators.md",
    "source_event_dataset_contract": "01_foundations/contract_registry/dataset_contracts/halts_table_dataset_contract_v0_1.md",
    "instrument_master_contract": "01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md",
    "market_calendar_contract": "01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md",
}


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_manifest(path: Path) -> dict[str, Any]:
    _require(path, "manifest")
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return str(value).strip()


def _hash_parts(parts: list[Any]) -> str:
    payload = "\x1f".join(_norm(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _iso_or_none(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).isoformat()


def _date_or_none(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).date().isoformat()


def _localize_et_to_utc(series: pd.Series) -> pd.Series:
    localized = pd.to_datetime(series, errors="coerce").dt.tz_localize(
        "America/New_York",
        ambiguous="NaT",
        nonexistent="shift_forward",
    )
    return localized.dt.tz_convert("UTC")


def _prepare_base_events(
    halts_table: Path,
    instrument_master: Path,
    market_calendar: Path,
) -> tuple[pd.DataFrame, dict[str, int]]:
    halts = pd.read_parquet(
        halts_table,
        columns=[
            "halt_event_id",
            "source",
            "ticker",
            "issuer_name",
            "listing_exchange",
            "halt_date",
            "halt_start_et",
            "resume_trade_et",
            "halt_code",
            "halt_type",
            "quality_state",
            "halt_event_state",
            "valid_for_intraday_mask",
        ],
    )
    source_valid_intraday = halts[halts["valid_for_intraday_mask"].eq(True)].copy()
    source_valid_intraday["ticker"] = source_valid_intraday["ticker"].astype(str).str.upper().str.strip()
    source_valid_intraday["halt_date"] = pd.to_datetime(source_valid_intraday["halt_date"]).dt.normalize()
    source_valid_intraday["event_time_utc"] = _localize_et_to_utc(source_valid_intraday["halt_start_et"])
    source_valid_intraday["resume_trade_utc"] = _localize_et_to_utc(source_valid_intraday["resume_trade_et"])

    instruments = pd.read_parquet(
        instrument_master,
        columns=[
            "instrument_id",
            "ticker",
            "valid_from",
            "valid_to",
            "is_common_stock",
            "is_lt1b_operational",
            "lt1b_classification_1b",
            "build_run_id",
            "schema_version",
        ],
    )
    instruments["ticker"] = instruments["ticker"].astype(str).str.upper().str.strip()
    instruments["valid_from"] = pd.to_datetime(instruments["valid_from"], errors="coerce").dt.normalize()
    instruments["valid_to"] = pd.to_datetime(instruments["valid_to"], errors="coerce").dt.normalize()

    identity_candidates = source_valid_intraday.merge(instruments, on="ticker", how="left")
    identity_matches = identity_candidates[
        identity_candidates["instrument_id"].notna()
        & (
            identity_candidates["valid_from"].isna()
            | (identity_candidates["valid_from"] <= identity_candidates["halt_date"])
        )
        & (
            identity_candidates["valid_to"].isna()
            | (identity_candidates["valid_to"] >= identity_candidates["halt_date"])
        )
    ].copy()
    duplicate_identity_candidate_rows = int(identity_matches["halt_event_id"].duplicated(keep=False).sum())
    identity_matches = (
        identity_matches.sort_values(
            ["halt_event_id", "valid_from", "valid_to", "instrument_id"],
            ascending=[True, False, False, True],
        )
        .drop_duplicates("halt_event_id")
        .reset_index(drop=True)
    )

    calendar = pd.read_parquet(
        market_calendar,
        columns=[
            "session_date",
            "open_utc",
            "close_utc",
            "open_et",
            "close_et",
            "session_minutes",
            "is_early_close",
            "calendar",
            "timezone",
            "build_run_id",
            "schema_version",
        ],
    )
    calendar["session_date"] = pd.to_datetime(calendar["session_date"]).dt.normalize()
    calendar = calendar.sort_values("session_date").reset_index(drop=True)
    calendar["prev_session_date"] = calendar["session_date"].shift(1)
    calendar["next_session_date"] = calendar["session_date"].shift(-1)
    calendar["prev_open_utc"] = calendar["open_utc"].shift(1)
    calendar["prev_close_utc"] = calendar["close_utc"].shift(1)
    calendar["next_open_utc"] = calendar["open_utc"].shift(-1)
    calendar["next_close_utc"] = calendar["close_utc"].shift(-1)

    base = identity_matches.merge(calendar, left_on="halt_date", right_on="session_date", how="inner")
    event_phase = pd.Series("regular", index=base.index, dtype="string")
    event_phase.loc[base["event_time_utc"] < base["open_utc"]] = "premarket"
    event_phase.loc[base["event_time_utc"] > base["close_utc"]] = "afterhours"
    base["event_session_phase"] = event_phase

    source_event_count = int(source_valid_intraday["halt_event_id"].nunique())
    identity_event_count = int(identity_matches["halt_event_id"].nunique())
    calendar_event_count = int(base["halt_event_id"].nunique())
    validations = {
        "source_valid_intraday_event_count": source_event_count,
        "identity_temporal_match_event_count": identity_event_count,
        "calendar_covered_event_count": calendar_event_count,
        "excluded_no_temporal_identity_event_count": source_event_count - identity_event_count,
        "excluded_no_market_calendar_session_event_count": identity_event_count - calendar_event_count,
        "duplicate_identity_candidate_rows": duplicate_identity_candidate_rows,
    }
    return base, validations


def _build_windows(base: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add_window(row: Any, role: str, start: Any, end: Any, start_source: str, end_source: str) -> None:
        if pd.isna(start) or pd.isna(end):
            return
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        if end_ts <= start_ts:
            return

        event_ts = pd.Timestamp(row.event_time_utc)
        contains_event = bool(start_ts <= event_ts < end_ts)
        contains_post_event = bool(end_ts > event_ts)
        leakage_safe_pre_event = bool(end_ts <= event_ts)
        event_response_end_observed = bool(role == "event_to_resume_or_30m" and end_source == "resume_trade_utc")
        quality_state = "good"
        if role == "event_to_resume_or_30m" and not event_response_end_observed:
            quality_state = "review_resume_fallback"

        consumption_state = {
            "prior_session_regular": "pre_event_context_window",
            "pre_event_30m": "pre_event_feature_candidate",
            "event_to_resume_or_30m": "event_response_window",
            "same_session_regular": "session_context_window",
            "next_session_regular": "outcome_candidate_window",
        }[role]

        event_window_id = _hash_parts([DATASET_ID, row.halt_event_id, role])
        rows.append(
            {
                "event_window_id": event_window_id,
                "source_event_id": row.halt_event_id,
                "event_source_dataset_id": SOURCE_EVENT_DATASET_ID,
                "event_family": "halt",
                "event_type": row.halt_type,
                "event_code": row.halt_code,
                "event_source": row.source,
                "ticker": row.ticker,
                "instrument_id": row.instrument_id,
                "issuer_name": row.issuer_name,
                "listing_exchange": row.listing_exchange,
                "session_date": row.session_date,
                "year": int(pd.Timestamp(row.session_date).year),
                "month": int(pd.Timestamp(row.session_date).month),
                "event_time_utc": row.event_time_utc,
                "resume_trade_utc": row.resume_trade_utc,
                "event_session_phase": row.event_session_phase,
                "window_role": role,
                "window_start_utc": start_ts,
                "window_end_utc": end_ts,
                "window_duration_minutes": float((end_ts - start_ts).total_seconds() / 60.0),
                "window_start_source": start_source,
                "window_end_source": end_source,
                "contains_event_time": contains_event,
                "contains_post_event_information": contains_post_event,
                "leakage_safe_as_pre_event_feature": leakage_safe_pre_event,
                "source_event_quality_state": row.quality_state,
                "source_halt_event_state": row.halt_event_state,
                "source_resume_trade_observed": bool(pd.notna(row.resume_trade_utc)),
                "event_response_end_observed": event_response_end_observed,
                "event_window_quality_state": quality_state,
                "event_window_consumption_state": consumption_state,
                "session_open_utc": row.open_utc,
                "session_close_utc": row.close_utc,
                "session_minutes": float(row.session_minutes),
                "is_early_close": bool(row.is_early_close),
                "calendar": row.calendar,
                "timezone": row.timezone,
                "previous_session_date": row.prev_session_date,
                "next_session_date": row.next_session_date,
                "instrument_identity_temporal_match": True,
                "is_common_stock": bool(row.is_common_stock),
                "is_lt1b_operational": bool(row.is_lt1b_operational),
                "lt1b_classification_1b": row.lt1b_classification_1b,
                "valid_for_event_engine": True,
                "valid_for_microstructure_feature_candidate": role in {"pre_event_30m", "same_session_regular"},
                "valid_for_ml_feature_candidate": role in {"prior_session_regular", "pre_event_30m"},
                "valid_for_outcome_window_candidate": role in {"event_to_resume_or_30m", "next_session_regular"},
                "valid_for_backtest_event_window_candidate": row.event_session_phase == "regular",
                "valid_for_rl_state_component_candidate": False,
                "requires_decision_time_availability_contract": True,
                "full_universe_claim": False,
            }
        )

    for row in base.itertuples(index=False):
        event_ts = pd.Timestamp(row.event_time_utc)
        resume_ts = pd.Timestamp(row.resume_trade_utc) if pd.notna(row.resume_trade_utc) else pd.NaT
        event_response_end = resume_ts if pd.notna(resume_ts) and resume_ts > event_ts else event_ts + pd.Timedelta(minutes=30)
        event_response_end_source = "resume_trade_utc" if pd.notna(resume_ts) and resume_ts > event_ts else "fixed_30m_fallback"

        add_window(row, "prior_session_regular", row.prev_open_utc, row.prev_close_utc, "previous_session_open_utc", "previous_session_close_utc")
        add_window(row, "pre_event_30m", event_ts - pd.Timedelta(minutes=30), event_ts, "event_time_utc_minus_30m", "event_time_utc")
        add_window(row, "event_to_resume_or_30m", event_ts, event_response_end, "event_time_utc", event_response_end_source)
        add_window(row, "same_session_regular", row.open_utc, row.close_utc, "session_open_utc", "session_close_utc")
        add_window(row, "next_session_regular", row.next_open_utc, row.next_close_utc, "next_session_open_utc", "next_session_close_utc")

    return pd.DataFrame(rows)


def materialize_event_windows_table(
    halts_table: Path,
    halts_manifest: Path,
    instrument_master: Path,
    instrument_master_manifest: Path,
    market_calendar: Path,
    market_calendar_manifest: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(halts_table, "halts table")
    _require(halts_manifest, "halts table manifest")
    _require(instrument_master, "instrument master")
    _require(instrument_master_manifest, "instrument master manifest")
    _require(market_calendar, "market calendar")
    _require(market_calendar_manifest, "market calendar manifest")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "event_windows_table_v0_1.parquet"
    summary_path = output_root / "_event_windows_table_summary_v0_1.csv"
    manifest_path = output_root / "_event_windows_table_manifest_v0_1.json"

    if output_path.exists():
        if not overwrite:
            raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")
        output_path.unlink()

    build_run_id = datetime.now(timezone.utc).strftime("event_windows_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()

    halts_table_sha256 = _sha256(halts_table)
    halts_manifest_sha256 = _sha256(halts_manifest)
    instrument_master_sha256 = _sha256(instrument_master)
    instrument_master_manifest_sha256 = _sha256(instrument_master_manifest)
    market_calendar_sha256 = _sha256(market_calendar)
    market_calendar_manifest_sha256 = _sha256(market_calendar_manifest)

    _load_manifest(halts_manifest)
    _load_manifest(instrument_master_manifest)
    _load_manifest(market_calendar_manifest)

    base, source_validations = _prepare_base_events(
        halts_table=halts_table,
        instrument_master=instrument_master,
        market_calendar=market_calendar,
    )
    output = _build_windows(base)
    output["materialization_scope"] = MATERIALIZATION_SCOPE
    output["quality_policy_version"] = QUALITY_POLICY_VERSION
    output["schema_version"] = SCHEMA_VERSION
    output["build_run_id"] = build_run_id
    output["created_at_utc"] = created_at_utc
    output["source_halts_table_path"] = halts_table.as_posix()
    output["source_halts_table_sha256"] = halts_table_sha256
    output["source_instrument_master_path"] = instrument_master.as_posix()
    output["source_instrument_master_sha256"] = instrument_master_sha256
    output["source_market_calendar_path"] = market_calendar.as_posix()
    output["source_market_calendar_sha256"] = market_calendar_sha256

    ordered_columns = [
        "event_window_id",
        "source_event_id",
        "event_source_dataset_id",
        "event_family",
        "event_type",
        "event_code",
        "event_source",
        "ticker",
        "instrument_id",
        "issuer_name",
        "listing_exchange",
        "session_date",
        "year",
        "month",
        "event_time_utc",
        "resume_trade_utc",
        "event_session_phase",
        "window_role",
        "window_start_utc",
        "window_end_utc",
        "window_duration_minutes",
        "window_start_source",
        "window_end_source",
        "contains_event_time",
        "contains_post_event_information",
        "leakage_safe_as_pre_event_feature",
        "source_event_quality_state",
        "source_halt_event_state",
        "source_resume_trade_observed",
        "event_response_end_observed",
        "event_window_quality_state",
        "event_window_consumption_state",
        "session_open_utc",
        "session_close_utc",
        "session_minutes",
        "is_early_close",
        "calendar",
        "timezone",
        "previous_session_date",
        "next_session_date",
        "instrument_identity_temporal_match",
        "is_common_stock",
        "is_lt1b_operational",
        "lt1b_classification_1b",
        "valid_for_event_engine",
        "valid_for_microstructure_feature_candidate",
        "valid_for_ml_feature_candidate",
        "valid_for_outcome_window_candidate",
        "valid_for_backtest_event_window_candidate",
        "valid_for_rl_state_component_candidate",
        "requires_decision_time_availability_contract",
        "full_universe_claim",
        "materialization_scope",
        "quality_policy_version",
        "schema_version",
        "build_run_id",
        "created_at_utc",
        "source_halts_table_path",
        "source_halts_table_sha256",
        "source_instrument_master_path",
        "source_instrument_master_sha256",
        "source_market_calendar_path",
        "source_market_calendar_sha256",
    ]
    output = output[ordered_columns]

    output.to_parquet(output_path, index=False)
    output_sha256 = _sha256(output_path)

    validations = {
        **source_validations,
        "row_count": int(len(output)),
        "unique_event_window_id_count": int(output["event_window_id"].nunique()),
        "duplicate_event_window_id_count": int(output["event_window_id"].duplicated().sum()),
        "source_event_count": int(output["source_event_id"].nunique()),
        "ticker_count": int(output["ticker"].nunique()),
        "instrument_count": int(output["instrument_id"].nunique()),
        "window_role_counts": {str(k): int(v) for k, v in output["window_role"].value_counts().items()},
        "event_session_phase_counts": {
            str(k): int(v) for k, v in base["event_session_phase"].value_counts().items()
        },
        "event_window_quality_state_counts": {
            str(k): int(v) for k, v in output["event_window_quality_state"].value_counts().items()
        },
        "resume_fallback_window_count": int(output["window_end_source"].eq("fixed_30m_fallback").sum()),
        "ml_feature_candidate_rows": int(output["valid_for_ml_feature_candidate"].sum()),
        "outcome_window_candidate_rows": int(output["valid_for_outcome_window_candidate"].sum()),
        "microstructure_feature_candidate_rows": int(output["valid_for_microstructure_feature_candidate"].sum()),
        "backtest_event_window_candidate_rows": int(output["valid_for_backtest_event_window_candidate"].sum()),
        "rl_state_component_candidate_rows": int(output["valid_for_rl_state_component_candidate"].sum()),
        "full_universe_claim_rows": int(output["full_universe_claim"].sum()),
    }

    summary = pd.DataFrame(
        [
            {"metric": "rows", "value": validations["row_count"]},
            {"metric": "source_events", "value": validations["source_event_count"]},
            {"metric": "tickers", "value": validations["ticker_count"]},
            {"metric": "instruments", "value": validations["instrument_count"]},
            {"metric": "source_valid_intraday_events", "value": validations["source_valid_intraday_event_count"]},
            {"metric": "identity_temporal_match_events", "value": validations["identity_temporal_match_event_count"]},
            {"metric": "calendar_covered_events", "value": validations["calendar_covered_event_count"]},
            {"metric": "excluded_no_temporal_identity_events", "value": validations["excluded_no_temporal_identity_event_count"]},
            {"metric": "excluded_no_market_calendar_session_events", "value": validations["excluded_no_market_calendar_session_event_count"]},
            {"metric": "resume_fallback_windows", "value": validations["resume_fallback_window_count"]},
            {"metric": "ml_feature_candidate_rows", "value": validations["ml_feature_candidate_rows"]},
            {"metric": "outcome_window_candidate_rows", "value": validations["outcome_window_candidate_rows"]},
        ]
    )
    summary.to_csv(summary_path, index=False)

    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "quality_policy_version": QUALITY_POLICY_VERSION,
        "materialization_scope": MATERIALIZATION_SCOPE,
        "source_event_dataset_id": SOURCE_EVENT_DATASET_ID,
        "full_universe_claim": False,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": output_path.as_posix(),
        "output_sha256": output_sha256,
        "summary_path": summary_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "source_halts_table": halts_table.as_posix(),
        "source_halts_table_sha256": halts_table_sha256,
        "source_halts_manifest": halts_manifest.as_posix(),
        "source_halts_manifest_sha256": halts_manifest_sha256,
        "source_instrument_master": instrument_master.as_posix(),
        "source_instrument_master_sha256": instrument_master_sha256,
        "source_instrument_master_manifest": instrument_master_manifest.as_posix(),
        "source_instrument_master_manifest_sha256": instrument_master_manifest_sha256,
        "source_market_calendar": market_calendar.as_posix(),
        "source_market_calendar_sha256": market_calendar_sha256,
        "source_market_calendar_manifest": market_calendar_manifest.as_posix(),
        "source_market_calendar_manifest_sha256": market_calendar_manifest_sha256,
        "contracts": CONTRACTS,
        "validations": validations,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--halts-table", type=Path, default=DEFAULT_HALTS_TABLE)
    parser.add_argument("--halts-manifest", type=Path, default=DEFAULT_HALTS_MANIFEST)
    parser.add_argument("--instrument-master", type=Path, default=DEFAULT_INSTRUMENT_MASTER)
    parser.add_argument("--instrument-master-manifest", type=Path, default=DEFAULT_INSTRUMENT_MASTER_MANIFEST)
    parser.add_argument("--market-calendar", type=Path, default=DEFAULT_MARKET_CALENDAR)
    parser.add_argument("--market-calendar-manifest", type=Path, default=DEFAULT_MARKET_CALENDAR_MANIFEST)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = materialize_event_windows_table(
        halts_table=args.halts_table,
        halts_manifest=args.halts_manifest,
        instrument_master=args.instrument_master,
        instrument_master_manifest=args.instrument_master_manifest,
        market_calendar=args.market_calendar,
        market_calendar_manifest=args.market_calendar_manifest,
        output_root=args.output_root,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
