from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


MODULE_ROOT = Path(__file__).resolve().parents[1]

DATASET_ID = "microstructure_features_table_v0_2_candidate"
MANIFEST_ID = "microstructure_features_table_v0_2_candidate_window_manifest"
MANIFEST_VERSION = "v0_1"
MATERIALIZATION_SCOPE = "halt_event_windows_microstructure_candidate"
SOURCE_WINDOW_DATASET_ID = "event_windows_table_v0_1"
SOURCE_EVENT_DATASET_ID = "halts_table_v0_1"
DEFAULT_EVENT_WINDOWS = Path(
    r"E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet"
)
DEFAULT_OUTPUT_DIR = MODULE_ROOT / "runs" / "data_foundation" / MANIFEST_ID
DEFAULT_ROLES = ("pre_event_30m", "same_session_regular")

REQUIRED_COLUMNS = {
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
    "resume_trade_utc",
    "event_session_phase",
    "window_role",
    "window_start_utc",
    "window_end_utc",
    "contains_post_event_information",
    "leakage_safe_as_pre_event_feature",
    "event_window_quality_state",
    "event_window_consumption_state",
    "valid_for_microstructure_feature_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_outcome_window_candidate",
    "valid_for_backtest_event_window_candidate",
    "valid_for_rl_state_component_candidate",
    "requires_decision_time_availability_contract",
    "full_universe_claim",
    "materialization_scope",
    "schema_version",
    "quality_policy_version",
    "build_run_id",
}

OUTPUT_COLUMNS = [
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
    "resume_trade_utc",
    "event_session_phase",
    "window_role",
    "window_start_utc",
    "window_end_utc",
    "window_label",
    "source_scope_note",
    "contains_post_event_information",
    "leakage_safe_as_pre_event_feature",
    "event_window_quality_state",
    "event_window_consumption_state",
    "valid_for_microstructure_feature_candidate",
    "valid_for_ml_feature_candidate",
    "valid_for_outcome_window_candidate",
    "valid_for_backtest_event_window_candidate",
    "valid_for_rl_state_component_candidate",
    "requires_decision_time_availability_contract",
    "source_event_window_materialization_scope",
    "source_event_window_schema_version",
    "source_event_window_quality_policy_version",
    "source_event_window_build_run_id",
    "candidate_dataset_id",
    "candidate_manifest_id",
    "candidate_manifest_version",
    "candidate_materialization_scope",
    "candidate_full_universe_claim",
    "source_window_dataset_id",
    "quotes_root_state_required",
    "trades_root_state_required",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return str(value)


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_event_windows(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing event windows table: {path}")
    frame = pd.read_parquet(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing event windows columns: {sorted(missing)}")
    return frame


def _normalize_bool(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for column in columns:
        out[column] = out[column].fillna(False).astype(bool)
    return out


def _validate_event_window_semantics(frame: pd.DataFrame) -> None:
    if frame["event_window_id"].duplicated().any():
        raise ValueError("event_window_id must be unique in event_windows_table input")
    if frame["full_universe_claim"].fillna(False).astype(bool).any():
        raise ValueError("event_windows_table input must not carry full_universe_claim=true")
    if frame["valid_for_rl_state_component_candidate"].fillna(False).astype(bool).any():
        raise ValueError("event_windows_table v0.1 must not carry RL candidate windows")

    ml = frame["valid_for_ml_feature_candidate"].fillna(False).astype(bool)
    leak_safe = frame["leakage_safe_as_pre_event_feature"].fillna(False).astype(bool)
    post_info = frame["contains_post_event_information"].fillna(False).astype(bool)
    if (ml & (~leak_safe | post_info)).any():
        bad = frame.loc[ml & (~leak_safe | post_info), ["event_window_id", "window_role"]].head(10)
        raise ValueError(
            "ML feature candidates must be leakage-safe and pre-event only. "
            f"Examples: {bad.to_dict(orient='records')}"
        )


def _format_for_csv(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in [
        "session_date",
        "event_time_utc",
        "resume_trade_utc",
        "window_start_utc",
        "window_end_utc",
    ]:
        if column in out.columns:
            out[column] = pd.to_datetime(out[column], utc=True, errors="coerce").map(
                lambda value: "" if pd.isna(value) else value.isoformat()
            )
    return out


def build_candidate_manifest(
    *,
    event_windows_path: Path,
    output_dir: Path,
    max_per_role: int,
    roles: tuple[str, ...],
    quotes_root_state_required: str,
    trades_root_state_required: str,
    overwrite: bool,
) -> dict[str, Any]:
    if max_per_role <= 0:
        raise ValueError("max_per_role must be positive")
    if not roles:
        raise ValueError("At least one role must be requested")

    created_at = _utc_now()
    run_id = created_at.strftime(f"{MANIFEST_ID}_%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{MANIFEST_ID}_{MANIFEST_VERSION}.csv"
    json_path = output_dir / f"{MANIFEST_ID}_{MANIFEST_VERSION}.json"

    if not overwrite and (csv_path.exists() or json_path.exists()):
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_dir}")

    source = _read_event_windows(event_windows_path)
    _validate_event_window_semantics(source)
    source = _normalize_bool(
        source,
        [
            "valid_for_microstructure_feature_candidate",
            "valid_for_ml_feature_candidate",
            "valid_for_outcome_window_candidate",
            "valid_for_backtest_event_window_candidate",
            "valid_for_rl_state_component_candidate",
            "requires_decision_time_availability_contract",
            "contains_post_event_information",
            "leakage_safe_as_pre_event_feature",
            "full_universe_claim",
        ],
    )

    eligible = source.loc[
        source["event_source_dataset_id"].eq(SOURCE_EVENT_DATASET_ID)
        & source["event_family"].eq("halt")
        & source["valid_for_microstructure_feature_candidate"]
        & source["window_role"].isin(roles)
    ].copy()
    if eligible.empty:
        raise ValueError("No eligible microstructure candidate windows found")

    role_counts = eligible["window_role"].value_counts().sort_index().to_dict()
    selected = (
        eligible.sort_values(
            ["window_role", "session_date", "ticker", "source_event_id", "event_window_id"],
            ascending=[True, False, True, True, True],
        )
        .groupby("window_role", group_keys=False)
        .head(max_per_role)
        .copy()
    )
    selected = selected.sort_values(["session_date", "ticker", "window_role", "event_window_id"]).reset_index(
        drop=True
    )

    selected["window_label"] = selected["window_role"]
    selected["source_scope_note"] = (
        "Derived from event_windows_table_v0_1 for microstructure_features_table_v0_2_candidate; "
        "candidate manifest only, not feature materialization."
    )
    selected["source_event_window_materialization_scope"] = selected["materialization_scope"]
    selected["source_event_window_schema_version"] = selected["schema_version"]
    selected["source_event_window_quality_policy_version"] = selected["quality_policy_version"]
    selected["source_event_window_build_run_id"] = selected["build_run_id"]
    selected["candidate_dataset_id"] = DATASET_ID
    selected["candidate_manifest_id"] = MANIFEST_ID
    selected["candidate_manifest_version"] = MANIFEST_VERSION
    selected["candidate_materialization_scope"] = MATERIALIZATION_SCOPE
    selected["candidate_full_universe_claim"] = False
    selected["source_window_dataset_id"] = SOURCE_WINDOW_DATASET_ID
    selected["quotes_root_state_required"] = quotes_root_state_required
    selected["trades_root_state_required"] = trades_root_state_required

    output = _format_for_csv(selected[OUTPUT_COLUMNS])
    output.to_csv(csv_path, index=False)

    manifest = {
        "manifest_id": MANIFEST_ID,
        "manifest_version": MANIFEST_VERSION,
        "candidate_dataset_id": DATASET_ID,
        "candidate_materialization_scope": MATERIALIZATION_SCOPE,
        "candidate_full_universe_claim": False,
        "created_at_utc": created_at.isoformat(),
        "build_run_id": run_id,
        "source_event_windows_table": str(event_windows_path),
        "source_event_windows_table_sha256": _sha256_file(event_windows_path),
        "source_window_dataset_id": SOURCE_WINDOW_DATASET_ID,
        "source_event_dataset_id": SOURCE_EVENT_DATASET_ID,
        "source_event_family": "halt",
        "requested_roles": list(roles),
        "max_per_role": max_per_role,
        "output_csv": str(csv_path),
        "output_json": str(json_path),
        "output_csv_sha256": _sha256_file(csv_path),
        "source_counts": {
            "source_event_windows_rows": int(len(source)),
            "eligible_microstructure_rows": int(len(eligible)),
            "eligible_role_counts": {str(k): int(v) for k, v in role_counts.items()},
            "selected_rows": int(len(selected)),
            "selected_role_counts": {
                str(k): int(v) for k, v in selected["window_role"].value_counts().sort_index().to_dict().items()
            },
            "selected_source_event_count": int(selected["source_event_id"].nunique()),
            "selected_ticker_count": int(selected["ticker"].nunique()),
        },
        "root_policy": {
            "quotes_root_state_required": quotes_root_state_required,
            "trades_root_state_required": trades_root_state_required,
            "feature_materialization_started": False,
            "official_dataset_created": False,
        },
        "contracts": {
            "microstructure_plan": (
                "01_foundations/module_contracts/outputs/"
                "microstructure_features_table_multi_window_materialization_plan_v0_1.md"
            ),
            "event_windows_dataset_contract": (
                "01_foundations/contract_registry/dataset_contracts/"
                "event_windows_table_dataset_contract_v0_1.md"
            ),
            "microstructure_dataset_contract": (
                "01_foundations/contract_registry/dataset_contracts/"
                "microstructure_features_table_dataset_contract_v0_1.md"
            ),
            "builder": "scripts/build_microstructure_candidate_window_manifest.py",
        },
    }
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    manifest["output_json_sha256"] = _sha256_file(json_path)
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, default=_json_default), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a governed candidate window manifest for microstructure_features_table v0.2."
    )
    parser.add_argument("--event-windows", type=Path, default=DEFAULT_EVENT_WINDOWS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-per-role", type=int, default=25)
    parser.add_argument("--roles", nargs="+", default=list(DEFAULT_ROLES))
    parser.add_argument(
        "--quotes-root-state-required",
        default="provisional_d_legacy_recovery_root_pending_e_parity",
    )
    parser.add_argument("--trades-root-state-required", default="official_e_raw_root")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    manifest = build_candidate_manifest(
        event_windows_path=args.event_windows,
        output_dir=args.output_dir,
        max_per_role=args.max_per_role,
        roles=tuple(args.roles),
        quotes_root_state_required=args.quotes_root_state_required,
        trades_root_state_required=args.trades_root_state_required,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "manifest": manifest["output_json"],
                "csv": manifest["output_csv"],
                "source_counts": manifest["source_counts"],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
