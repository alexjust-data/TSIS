from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from _helpers.data_foundation import write_json_artifact


MODULE_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = MODULE_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from build_1m_split_normalized_materialization_manifest import build_manifest


def _touch_minute_file(root: Path, ticker: str, year: int, month: int) -> Path:
    path = (
        root
        / f"ticker={ticker}"
        / f"year={year}"
        / f"month={month:02d}"
        / f"minute_aggs_{ticker}_{year}_{month:02d}.parquet"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"synthetic parquet placeholder not read by manifest builder")
    return path


def _write_splits(root: Path, ticker: str, rows: list[dict[str, object]]) -> Path:
    path = root / f"ticker={ticker}" / f"splits_{ticker}.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    return path


def test_split_affected_manifest_uses_split_ticker_direct_partitions(
    tmp_path: Path,
    monkeypatch,
    tsis_artifacts_dir: Path,
) -> None:
    minute_root = tmp_path / "ohlcv_1m"
    splits_root = tmp_path / "splits"
    output = tmp_path / "manifest_split_affected.csv"

    for month in [1, 2, 3, 4]:
        _touch_minute_file(minute_root, "ABCD", 2020, month)
    for month in [1, 2, 3]:
        _touch_minute_file(minute_root, "ZZZZ", 2020, month)

    _write_splits(
        splits_root,
        "ABCD",
        [
            {
                "execution_date": "2020-03-15",
                "split_from": 10,
                "split_to": 1,
            }
        ],
    )
    _write_splits(
        splits_root,
        "MISS",
        [
            {
                "execution_date": "2020-02-01",
                "split_from": 2,
                "split_to": 1,
            }
        ],
    )

    def fail_rglob(self: Path, pattern: str):  # noqa: ANN001
        raise AssertionError(f"Path.rglob must not be used in split-affected manifest smoke: {self} {pattern}")

    monkeypatch.setattr(Path, "rglob", fail_rglob)

    summary = build_manifest(
        minute_root=minute_root,
        splits_root=splits_root,
        output=output,
        mode="split-affected",
        min_year=None,
        max_year=None,
        limit=None,
        chunk_size=None,
        chunks_dir=None,
    )
    manifest = pd.read_csv(output)

    assert summary["scan_strategy"] == "split_tickers_then_partition_direct"
    assert summary["rows"] == 3
    assert summary["tickers"] == 1
    assert summary["files_seen"] == 4
    assert summary["files_without_split_effect"] == 1
    assert summary["split_tickers_seen"] == 2
    assert summary["split_tickers_without_minute_dir"] == 1
    assert set(manifest["ticker"]) == {"ABCD"}
    assert manifest["month"].tolist() == [1, 2, 3]
    assert set(manifest["event_type"]) == {"reverse_split"}
    assert set(manifest["role"]) == {"split_affected_ticker_month"}
    assert "ZZZZ" not in set(manifest["ticker"])

    write_json_artifact(
        tsis_artifacts_dir,
        "split_affected_manifest_direct_partition_check.json",
        {
            "summary": summary,
            "manifest_rows": int(len(manifest)),
            "months": manifest["month"].astype(int).tolist(),
        },
    )


def test_all_existing_manifest_uses_partition_direct_scan(
    tmp_path: Path,
    monkeypatch,
    tsis_artifacts_dir: Path,
) -> None:
    minute_root = tmp_path / "ohlcv_1m"
    splits_root = tmp_path / "splits"
    output = tmp_path / "manifest_all_existing.csv"
    chunks_dir = tmp_path / "chunks"

    _touch_minute_file(minute_root, "ABCD", 2021, 1)
    _touch_minute_file(minute_root, "ABCD", 2021, 2)
    _touch_minute_file(minute_root, "WXYZ", 2022, 3)
    splits_root.mkdir(parents=True, exist_ok=True)

    def fail_rglob(self: Path, pattern: str):  # noqa: ANN001
        raise AssertionError(f"Path.rglob must not be used in manifest builder: {self} {pattern}")

    monkeypatch.setattr(Path, "rglob", fail_rglob)

    summary = build_manifest(
        minute_root=minute_root,
        splits_root=splits_root,
        output=output,
        mode="all-existing",
        min_year=None,
        max_year=None,
        limit=None,
        chunk_size=2,
        chunks_dir=chunks_dir,
    )
    manifest = pd.read_csv(output)

    assert summary["scan_strategy"] == "partition_direct_all_existing"
    assert summary["rows"] == 3
    assert summary["files_seen"] == 3
    assert summary["chunk_count"] == 2
    assert len(summary["chunk_paths"]) == 2
    assert set(manifest["role"]) == {"all_existing_raw_1m_month"}
    assert set(manifest["event_type"]) == {"physical_full_universe"}

    write_json_artifact(
        tsis_artifacts_dir,
        "all_existing_manifest_direct_partition_check.json",
        {
            "summary": summary,
            "manifest_rows": int(len(manifest)),
            "chunk_paths": summary["chunk_paths"],
        },
    )
