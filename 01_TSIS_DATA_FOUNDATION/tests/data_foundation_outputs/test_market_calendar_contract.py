from __future__ import annotations

from pathlib import Path

import pandas as pd

from _helpers.data_foundation import (
    assert_relative_contract_paths_exist,
    load_json,
    non_empty_string_mask,
    sha256_file,
    write_json_artifact,
)


OUTPUT_ROOT = Path("E:/TSIS/data/data_foundation_outputs/market_calendar")
MANIFEST_PATH = OUTPUT_ROOT / "_market_calendar_manifest_v0_1.json"
SUMMARY_PATH = OUTPUT_ROOT / "_market_calendar_summary_v0_1.csv"

REQUIRED_COLUMNS = {
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
    "source_calendar_artifact",
    "build_run_id",
    "schema_version",
    "created_at_utc",
}


def _manifest() -> dict:
    return load_json(MANIFEST_PATH)


def _frame() -> pd.DataFrame:
    return pd.read_parquet(_manifest()["output_path"])


def test_market_calendar_manifest_paths_hashes_and_contract_links(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    output_path = Path(manifest["output_path"])
    summary_path = Path(manifest["summary_path"])
    source_parquet = Path(manifest["source_parquet"])
    source_meta = Path(manifest["source_meta"])

    assert manifest["dataset_id"] == "market_calendar_v0_1"
    assert manifest["schema_version"] == "market_calendar_v0_1"
    assert output_path.exists()
    assert summary_path.exists()
    assert summary_path == SUMMARY_PATH
    assert source_parquet.exists()
    assert source_meta.exists()
    assert sha256_file(output_path) == manifest["output_sha256"]
    assert sha256_file(source_parquet) == manifest["source_parquet_sha256"]
    assert sha256_file(source_meta) == manifest["source_meta_sha256"]
    assert_relative_contract_paths_exist(manifest)

    write_json_artifact(
        tsis_artifacts_dir,
        "market_calendar_manifest_check.json",
        {
            "dataset_id": manifest["dataset_id"],
            "output_path": str(output_path),
            "output_sha256": manifest["output_sha256"],
            "source_parquet": str(source_parquet),
            "source_parquet_sha256": manifest["source_parquet_sha256"],
            "validations": manifest["validations"],
        },
    )


def test_market_calendar_schema_lineage_and_manifest_counts() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert REQUIRED_COLUMNS <= set(df.columns)
    assert len(df) == validations["row_count"] == 5328
    assert set(df["schema_version"]) == {"market_calendar_v0_1"}
    assert set(df["build_run_id"]) == {manifest["build_run_id"]}
    assert non_empty_string_mask(df["created_at_utc"]).all()
    assert non_empty_string_mask(df["source_calendar_artifact"]).all()
    assert df["session_date"].astype(str).min() == validations["first_session"] == "2005-01-03"
    assert df["session_date"].astype(str).max() == validations["last_session"] == "2026-03-09"


def test_market_calendar_session_contract_rules() -> None:
    manifest = _manifest()
    df = _frame()
    validations = manifest["validations"]

    assert df.duplicated(["calendar", "session_date"]).sum() == validations["duplicate_session_count"] == 0
    assert (df["open_utc"] < df["close_utc"]).all()
    assert df["session_minutes"].gt(0).all()
    assert set(df["calendar"]) == {"XNYS"}
    assert set(df["timezone"]) == {"America/New_York"}
    assert validations["hard_fail_count"] == 0
    assert validations["invalid_window_count"] == 0
    assert validations["nonpositive_minutes_count"] == 0
    assert int(df["is_early_close"].sum()) == validations["early_close_sessions"] == 45
    assert df["month"].between(1, 12).all()


def test_market_calendar_source_and_known_session_edges(tsis_artifacts_dir: Path) -> None:
    manifest = _manifest()
    df = _frame().copy()
    source = pd.read_parquet(manifest["source_parquet"])
    sessions = set(df["session_date"].astype(str))

    assert len(source) == len(df)
    assert "2012-10-29" not in sessions
    assert "2012-10-30" not in sessions
    assert "2018-12-05" not in sessions

    black_friday = df.loc[df["session_date"].astype(str).eq("2024-11-29")]
    assert len(black_friday) == 1
    assert bool(black_friday.iloc[0]["is_early_close"]) is True
    assert float(black_friday.iloc[0]["session_minutes"]) == 210.0

    write_json_artifact(
        tsis_artifacts_dir,
        "market_calendar_source_reconciliation.json",
        {
            "source_parquet": manifest["source_parquet"],
            "source_row_count": len(source),
            "output_row_count": len(df),
            "known_closed_sessions_absent": ["2012-10-29", "2012-10-30", "2018-12-05"],
            "early_close_case": {
                "session_date": "2024-11-29",
                "session_minutes": 210.0,
            },
        },
    )
