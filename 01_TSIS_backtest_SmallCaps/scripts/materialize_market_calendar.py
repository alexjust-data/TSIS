from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_ID = "market_calendar_v0_1"
SCHEMA_VERSION = "market_calendar_v0_1"

DEFAULT_SOURCE_PARQUET = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\data\reference"
    r"\market_calendar_official_XNYS_20050101_20251231.parquet"
)
DEFAULT_SOURCE_META = Path(
    r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps\data\reference"
    r"\market_calendar_official_XNYS_20050101_20251231.meta.json"
)
DEFAULT_OUTPUT_ROOT = Path(r"E:\TSIS\data\data_foundation_outputs\market_calendar")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _require(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def _load_source(source_parquet: Path) -> pd.DataFrame:
    required = {
        "session_date",
        "open_utc",
        "close_utc",
        "open_et",
        "close_et",
        "is_early_close",
        "year",
        "month",
        "dow",
        "calendar",
        "timezone",
    }
    raw = pd.read_parquet(source_parquet)
    missing = sorted(required - set(raw.columns))
    if missing:
        raise KeyError(f"Missing source columns: {missing}")

    out = raw.copy()
    out["session_date"] = pd.to_datetime(out["session_date"], errors="coerce").dt.date
    out["open_utc"] = pd.to_datetime(out["open_utc"], errors="coerce", utc=True)
    out["close_utc"] = pd.to_datetime(out["close_utc"], errors="coerce", utc=True)
    out["open_et"] = out["open_utc"].dt.tz_convert("America/New_York")
    out["close_et"] = out["close_utc"].dt.tz_convert("America/New_York")
    out["session_minutes"] = (out["close_utc"] - out["open_utc"]).dt.total_seconds() / 60.0
    out["is_early_close"] = out["is_early_close"].astype(bool)
    out["year"] = pd.to_numeric(out["year"], errors="coerce").astype("Int16")
    out["month"] = pd.to_numeric(out["month"], errors="coerce").astype("Int8")
    for col in ("dow", "calendar", "timezone"):
        out[col] = out[col].astype("string")
    return out[
        [
            "session_date",
            "open_utc",
            "close_utc",
            "open_et",
            "close_et",
            "session_minutes",
            "is_early_close",
            "year",
            "month",
            "dow",
            "calendar",
            "timezone",
        ]
    ].sort_values(["calendar", "session_date"]).reset_index(drop=True)


def materialize_market_calendar(
    source_parquet: Path,
    source_meta: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    _require(source_parquet, "source parquet")
    _require(source_meta, "source meta")

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "market_calendar_v0_1.parquet"
    summary_path = output_root / "_market_calendar_summary_v0_1.csv"
    manifest_path = output_root / "_market_calendar_manifest_v0_1.json"

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output exists. Pass --overwrite to replace: {output_path}")

    build_run_id = datetime.now(timezone.utc).strftime("market_calendar_v0_1_%Y%m%dT%H%M%SZ")
    created_at_utc = datetime.now(timezone.utc).isoformat()
    source_sha256 = _sha256(source_parquet)
    source_meta_sha256 = _sha256(source_meta)
    source_meta_payload = json.loads(source_meta.read_text(encoding="utf-8"))

    df = _load_source(source_parquet)
    df["source_calendar_artifact"] = str(source_parquet)
    df["build_run_id"] = build_run_id
    df["schema_version"] = SCHEMA_VERSION
    df["created_at_utc"] = created_at_utc

    duplicate_session_count = int(df.duplicated(["calendar", "session_date"]).sum())
    invalid_window_count = int((df["open_utc"] >= df["close_utc"]).sum())
    nonpositive_minutes_count = int((df["session_minutes"] <= 0).sum())
    unparseable_core_count = int(
        df[["session_date", "open_utc", "close_utc", "open_et", "close_et"]].isna().any(axis=1).sum()
    )
    unexpected_calendar_count = int((df["calendar"] != "XNYS").sum())
    unexpected_timezone_count = int((df["timezone"] != "America/New_York").sum())

    validations: dict[str, Any] = {
        "row_count": int(len(df)),
        "calendar_count": int(df["calendar"].nunique(dropna=True)),
        "calendar_values": sorted(df["calendar"].dropna().astype(str).unique().tolist()),
        "timezone_values": sorted(df["timezone"].dropna().astype(str).unique().tolist()),
        "first_session": str(df["session_date"].min()),
        "last_session": str(df["session_date"].max()),
        "early_close_sessions": int(df["is_early_close"].sum()),
        "duplicate_session_count": duplicate_session_count,
        "invalid_window_count": invalid_window_count,
        "nonpositive_minutes_count": nonpositive_minutes_count,
        "unparseable_core_count": unparseable_core_count,
        "unexpected_calendar_count": unexpected_calendar_count,
        "unexpected_timezone_count": unexpected_timezone_count,
        "source_sha256": source_sha256,
        "source_meta_sha256": source_meta_sha256,
    }
    validations["hard_fail_count"] = int(
        duplicate_session_count
        + invalid_window_count
        + nonpositive_minutes_count
        + unparseable_core_count
        + unexpected_calendar_count
        + unexpected_timezone_count
        + (1 if len(df) == 0 else 0)
    )

    expected_rows = int(source_meta_payload.get("sessions", 0))
    expected_early = int(source_meta_payload.get("early_close_sessions", -1))
    expected_first = str(source_meta_payload.get("first_session", ""))
    expected_last = str(source_meta_payload.get("last_session", ""))
    validations["source_meta_row_match"] = bool(len(df) == expected_rows)
    validations["source_meta_early_close_match"] = bool(validations["early_close_sessions"] == expected_early)
    validations["source_meta_first_last_match"] = bool(
        validations["first_session"] == expected_first and validations["last_session"] == expected_last
    )

    if validations["hard_fail_count"] > 0:
        raise RuntimeError(f"Hard validation failed: {validations}")
    if not (
        validations["source_meta_row_match"]
        and validations["source_meta_early_close_match"]
        and validations["source_meta_first_last_match"]
    ):
        raise RuntimeError(f"Source meta reconciliation failed: {validations}")

    df.to_parquet(output_path, index=False)

    summary_rows = [
        {"metric": "rows", "value": validations["row_count"]},
        {"metric": "calendar", "value": ",".join(validations["calendar_values"])},
        {"metric": "timezone", "value": ",".join(validations["timezone_values"])},
        {"metric": "first_session", "value": validations["first_session"]},
        {"metric": "last_session", "value": validations["last_session"]},
        {"metric": "early_close_sessions", "value": validations["early_close_sessions"]},
        {"metric": "duplicate_session_count", "value": validations["duplicate_session_count"]},
        {"metric": "invalid_window_count", "value": validations["invalid_window_count"]},
        {"metric": "hard_fail_count", "value": validations["hard_fail_count"]},
    ]
    pd.DataFrame(summary_rows).to_csv(summary_path, index=False)

    manifest: dict[str, Any] = {
        "dataset_id": DATASET_ID,
        "schema_version": SCHEMA_VERSION,
        "build_run_id": build_run_id,
        "created_at_utc": created_at_utc,
        "source_parquet": str(source_parquet),
        "source_parquet_sha256": source_sha256,
        "source_meta": str(source_meta),
        "source_meta_sha256": source_meta_sha256,
        "source_builder": "scripts/agent05_build_market_calendar_official.py",
        "output_path": str(output_path),
        "summary_path": str(summary_path),
        "validations": validations,
        "contracts": {
            "dataset_contract": "01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md",
            "schema_contract": "01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md",
            "consumption_policy": "01_foundations/data_consumption_policies/market_calendar_consumption_policy.md",
            "registry_entry": "01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml",
            "validators": "01_foundations/validators/outputs/market_calendar_validators.md",
        },
    }
    manifest["output_sha256"] = _sha256(output_path)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Materializa market_calendar_v0_1 desde el calendario oficial local.")
    ap.add_argument("--source-parquet", default=str(DEFAULT_SOURCE_PARQUET))
    ap.add_argument("--source-meta", default=str(DEFAULT_SOURCE_META))
    ap.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    ap.add_argument("--overwrite", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    materialize_market_calendar(
        source_parquet=Path(args.source_parquet),
        source_meta=Path(args.source_meta),
        output_root=Path(args.output_root),
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
