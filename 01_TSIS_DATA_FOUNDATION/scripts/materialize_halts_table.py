from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "halts_table_v0_1"
SCHEMA_VERSION = "halts_table_v0_1"
SOURCE_DATASET_ID = "halts_v0_1"
MAX_EXPECTED_EVENT_DATE = pd.Timestamp("2026-12-31")

DEFAULT_SOURCE_MASTER = Path(r"E:\TSIS\data\Halts\processed\halts_master_multisource.parquet")
DEFAULT_SOURCE_SUMMARY = Path(r"E:\TSIS\data\Halts\processed\halts_master_multisource_summary.csv")
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\halts_table")

CONTRACTS = {
    "schema": "01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md",
    "dataset_contract": "01_foundations/contract_registry/dataset_contracts/halts_table_dataset_contract_v0_1.md",
    "source_dataset_contract": "01_foundations/contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md",
    "consumption_policy": "01_foundations/data_consumption_policies/halts_table_consumption_policy.md",
    "source_consumption_policy": "01_foundations/data_consumption_policies/halts_consumption_policy.md",
    "registry_entry": "01_foundations/dataset_registry/outputs/halts_table_registry_entry.yaml",
    "validator": "01_foundations/validators/outputs/halts_table_validators.md",
    "source_validator": "01_foundations/validators/halts/halts_validators.md",
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


def _norm(value: Any) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return str(value).strip()


def _hash_parts(parts: list[Any]) -> str:
    payload = "\x1f".join(_norm(part) for part in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _non_empty_string(series: pd.Series) -> pd.Series:
    return series.notna() & series.astype("string").str.strip().ne("")


def _build_event_states(df: pd.DataFrame) -> pd.DataFrame:
    source_allowed = df["source"].isin(["nasdaq", "nyse", "sec"])
    has_ticker = _non_empty_string(df["ticker"])
    has_halt_date = df["halt_date"].notna()
    has_halt_start = df["halt_start_et"].notna()
    has_resume_quote = df["resume_quote_et"].notna()
    has_resume_trade = df["resume_trade_et"].notna()
    is_sec = df["source"].eq("sec")

    future_date = df["halt_date"].notna() & (df["halt_date"] > MAX_EXPECTED_EVENT_DATE)
    resume_quote_before_start = has_halt_start & has_resume_quote & (df["resume_quote_et"] < df["halt_start_et"])
    resume_trade_before_start = has_halt_start & has_resume_trade & (df["resume_trade_et"] < df["halt_start_et"])
    timestamp_order_review = resume_quote_before_start | resume_trade_before_start
    parse_suspect = future_date | timestamp_order_review
    missing_core_event = (~source_allowed) | (~has_halt_date) | ((~is_sec) & (~has_ticker))

    event_state = pd.Series("good_date_level_event", index=df.index, dtype="string")
    event_state.loc[has_halt_start] = "good_full_intraday_event"
    event_state.loc[is_sec] = "regulatory_context_only"
    event_state.loc[parse_suspect | ((~is_sec) & (~has_ticker))] = "review_partial_identity"
    event_state.loc[missing_core_event] = "bad_unusable_event"

    event_granularity = pd.Series("date_level", index=df.index, dtype="string")
    event_granularity.loc[has_halt_start] = "intraday_window"
    event_granularity.loc[is_sec] = "regulatory_context"
    event_granularity.loc[parse_suspect] = "review_intraday_parse_suspect"
    event_granularity.loc[missing_core_event] = "invalid"

    quality_state = pd.Series("good", index=df.index, dtype="string")
    quality_state.loc[event_state.eq("review_partial_identity")] = "review"
    quality_state.loc[event_state.eq("bad_unusable_event")] = "bad"

    intraday_consumption_state = pd.Series("date_level_only", index=df.index, dtype="string")
    intraday_consumption_state.loc[event_state.eq("good_full_intraday_event")] = "intraday_mask_allowed"
    intraday_consumption_state.loc[event_state.eq("regulatory_context_only")] = "regulatory_context_only"
    intraday_consumption_state.loc[event_state.eq("review_partial_identity")] = "review_only"
    intraday_consumption_state.loc[event_state.eq("bad_unusable_event")] = "forensic_only"

    out = df.copy()
    out["source_allowed"] = source_allowed
    out["has_ticker"] = has_ticker
    out["has_halt_date"] = has_halt_date
    out["has_halt_start_et"] = has_halt_start
    out["has_resume_quote_et"] = has_resume_quote
    out["has_resume_trade_et"] = has_resume_trade
    out["future_date_flag"] = future_date
    out["timestamp_order_review_flag"] = timestamp_order_review
    out["parse_suspect_flag"] = parse_suspect
    out["missing_core_event_flag"] = missing_core_event
    out["halt_event_state"] = event_state
    out["event_granularity"] = event_granularity
    out["quality_state"] = quality_state
    out["intraday_consumption_state"] = intraday_consumption_state
    out["valid_for_event_engine"] = event_state.isin(
        ["good_full_intraday_event", "good_date_level_event", "regulatory_context_only"]
    )
    out["valid_for_intraday_mask"] = event_state.eq("good_full_intraday_event")
    out["valid_for_date_context"] = event_state.isin(
        ["good_full_intraday_event", "good_date_level_event", "regulatory_context_only"]
    )
    out["valid_for_backtest_event_mask_candidate"] = event_state.eq("good_full_intraday_event")
    out["valid_for_ml_flagged_candidate"] = event_state.isin(
        ["good_full_intraday_event", "good_date_level_event", "regulatory_context_only"]
    )
    out["valid_for_execution_context_candidate"] = event_state.eq("good_full_intraday_event")
    out["prohibited_as_alpha"] = True
    out["requires_decision_time_availability_contract"] = True
    out["visual_case_bucket"] = "not_materialized_in_halts_table_v0_1"
    out["market_overlay_state"] = "not_materialized_in_halts_table_v0_1"
    return out


def materialize_halts_table(
    source_master: Path,
    source_summary: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(source_master, "halts master multisource parquet")
    _require(source_summary, "halts master multisource summary")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "halts_table_v0_1.parquet"
    summary_path = output_root / "_halts_table_summary_v0_1.csv"
    manifest_path = output_root / "_halts_table_manifest_v0_1.json"

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")

    build_run_id = datetime.now(timezone.utc).strftime("halts_table_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()
    source_master_sha256 = _sha256(source_master)
    source_summary_sha256 = _sha256(source_summary)

    source_df = pd.read_parquet(source_master).reset_index(drop=True)
    source_df.insert(0, "source_row_number", source_df.index.astype("int64"))

    source_event_keys = []
    event_ids = []
    for row in source_df.itertuples(index=False):
        source_key = _hash_parts(
            [
                getattr(row, "source"),
                getattr(row, "ticker"),
                getattr(row, "issuer_name"),
                getattr(row, "halt_date"),
                getattr(row, "halt_start_et"),
                getattr(row, "halt_code"),
                getattr(row, "release_no"),
                getattr(row, "item_link"),
            ]
        )
        source_event_keys.append(source_key)
        event_ids.append(_hash_parts([DATASET_ID, source_key, getattr(row, "source_row_number")]))

    source_df.insert(0, "source_event_key", source_event_keys)
    source_df.insert(0, "halt_event_id", event_ids)
    source_df["duplicate_source_event_key"] = source_df.duplicated("source_event_key", keep=False)

    output_df = _build_event_states(source_df)
    output_df["source_dataset_id"] = SOURCE_DATASET_ID
    output_df["source_master_path"] = source_master.as_posix()
    output_df["source_master_sha256"] = source_master_sha256
    output_df["schema_version"] = SCHEMA_VERSION
    output_df["build_run_id"] = build_run_id
    output_df["created_at_utc"] = created_at_utc

    ordered_columns = [
        "halt_event_id",
        "source_event_key",
        "source_row_number",
        "duplicate_source_event_key",
        "source_dataset_id",
        "source",
        "source_priority",
        "ticker",
        "issuer_name",
        "listing_exchange",
        "halt_date",
        "halt_start_et",
        "resume_quote_et",
        "resume_trade_et",
        "halt_code",
        "halt_type",
        "raw_reason",
        "release_no",
        "item_link",
        "url_source",
        "is_sec_suspension",
        "halt_event_state",
        "event_granularity",
        "quality_state",
        "intraday_consumption_state",
        "source_allowed",
        "has_ticker",
        "has_halt_date",
        "has_halt_start_et",
        "has_resume_quote_et",
        "has_resume_trade_et",
        "future_date_flag",
        "timestamp_order_review_flag",
        "parse_suspect_flag",
        "missing_core_event_flag",
        "valid_for_event_engine",
        "valid_for_intraday_mask",
        "valid_for_date_context",
        "valid_for_backtest_event_mask_candidate",
        "valid_for_ml_flagged_candidate",
        "valid_for_execution_context_candidate",
        "prohibited_as_alpha",
        "requires_decision_time_availability_contract",
        "visual_case_bucket",
        "market_overlay_state",
        "source_master_path",
        "source_master_sha256",
        "schema_version",
        "build_run_id",
        "created_at_utc",
    ]
    output_df = output_df[ordered_columns]

    output_df.to_parquet(output_path, index=False)
    output_sha256 = _sha256(output_path)

    validations = {
        "row_count": int(len(output_df)),
        "unique_halt_event_id_count": int(output_df["halt_event_id"].nunique()),
        "duplicate_halt_event_id_count": int(output_df["halt_event_id"].duplicated().sum()),
        "duplicate_source_event_key_row_count": int(output_df["duplicate_source_event_key"].sum()),
        "source_counts": {str(k): int(v) for k, v in output_df["source"].value_counts(dropna=False).items()},
        "event_state_counts": {
            str(k): int(v) for k, v in output_df["halt_event_state"].value_counts(dropna=False).items()
        },
        "quality_state_counts": {
            str(k): int(v) for k, v in output_df["quality_state"].value_counts(dropna=False).items()
        },
        "missing_halt_date_count": int(output_df["has_halt_date"].eq(False).sum()),
        "future_date_flag_count": int(output_df["future_date_flag"].sum()),
        "timestamp_order_review_flag_count": int(output_df["timestamp_order_review_flag"].sum()),
        "parse_suspect_flag_count": int(output_df["parse_suspect_flag"].sum()),
        "hard_fail_count": int(output_df["quality_state"].eq("bad").sum()),
        "review_count": int(output_df["quality_state"].eq("review").sum()),
        "valid_for_intraday_mask_count": int(output_df["valid_for_intraday_mask"].sum()),
        "valid_for_date_context_count": int(output_df["valid_for_date_context"].sum()),
        "valid_for_backtest_event_mask_candidate_count": int(
            output_df["valid_for_backtest_event_mask_candidate"].sum()
        ),
    }

    summary = pd.DataFrame(
        [
            {"metric": "rows", "value": validations["row_count"]},
            {"metric": "sources", "value": len(validations["source_counts"])},
            {"metric": "good_rows", "value": validations["quality_state_counts"].get("good", 0)},
            {"metric": "review_rows", "value": validations["quality_state_counts"].get("review", 0)},
            {"metric": "bad_rows", "value": validations["quality_state_counts"].get("bad", 0)},
            {"metric": "valid_for_intraday_mask_rows", "value": validations["valid_for_intraday_mask_count"]},
            {"metric": "future_date_flag_rows", "value": validations["future_date_flag_count"]},
            {"metric": "missing_halt_date_rows", "value": validations["missing_halt_date_count"]},
            {"metric": "duplicate_source_event_key_rows", "value": validations["duplicate_source_event_key_row_count"]},
        ]
    )
    summary.to_csv(summary_path, index=False)

    manifest = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "source_dataset_id": SOURCE_DATASET_ID,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "output_path": output_path.as_posix(),
        "output_sha256": output_sha256,
        "summary_path": summary_path.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "source_master": source_master.as_posix(),
        "source_master_sha256": source_master_sha256,
        "source_summary": source_summary.as_posix(),
        "source_summary_sha256": source_summary_sha256,
        "max_expected_event_date": MAX_EXPECTED_EVENT_DATE.date().isoformat(),
        "contracts": CONTRACTS,
        "validations": validations,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-master", type=Path, default=DEFAULT_SOURCE_MASTER)
    parser.add_argument("--source-summary", type=Path, default=DEFAULT_SOURCE_SUMMARY)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = materialize_halts_table(
        source_master=args.source_master,
        source_summary=args.source_summary,
        output_root=args.output_root,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
