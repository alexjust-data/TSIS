from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


MODULE_ROOT = Path(__file__).resolve().parents[1]
BUILDER = MODULE_ROOT / "scripts/build_trading_activity_rth_coverage_sidecar.py"


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _write_trade_parquet(path: Path, ticker: str, date: str, rows: int = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.table(
        {
            "ticker": [ticker] * rows,
            "date": [date] * rows,
            "timestamp": pa.array(["2024-01-02T14:30:01", "2024-01-02T14:30:02"][:rows], type=pa.string()),
            "price": [1.0, 1.01][:rows],
            "size": [100, 200][:rows],
            "exchange": [11, 11][:rows],
            "conditions": pa.array([[0], [0]][:rows], type=pa.list_(pa.int64())),
            "year": [2024] * rows,
            "month": [1] * rows,
            "day": [date] * rows,
        }
    )
    pq.write_table(table, path)


def _build_fixture(tmp_path: Path) -> tuple[Path, Path]:
    run_root = tmp_path / "runs"
    run_dir = run_root / "fixture_shard_01"
    source_root = tmp_path / "active_trades"
    historical_root = Path("C:/historical/trades")
    tasks = [
        ("OKAY", "2024-01-02", "DOWNLOADED_OK", 2),
        ("EMPT", "2024-01-03", "DOWNLOADED_EMPTY", 0),
        ("FAIL", "2024-01-04", "DOWNLOAD_FAIL", 0),
        ("MISS", "2024-01-05", None, None),
    ]
    expected_rows = []
    event_rows = []
    for ticker, date, status, rows in tasks:
        key = f"{ticker}|{date}|market"
        historical = historical_root / ticker / f"day={date}" / "market.parquet"
        expected_rows.append(
            {
                "task_key": key,
                "ticker": ticker,
                "date": date,
                "session": "market",
                "expected_file": str(historical),
            }
        )
        if status is not None:
            event_rows.append(
                {
                    "task_key": key,
                    "ticker": ticker,
                    "date": date,
                    "session": "market",
                    "status": status,
                    "rows": rows,
                    "file": str(historical),
                    "elapsed_sec": 0.1,
                    "processed_at_utc": "2026-03-25T00:00:00+00:00",
                    "error": "fixture failure" if status == "DOWNLOAD_FAIL" else "",
                }
            )

    _write_csv(
        run_dir / "expected_manifest_trades_ticks.csv",
        ["task_key", "ticker", "date", "session", "expected_file"],
        expected_rows,
    )
    _write_csv(
        run_dir / "download_events_trades_ticks_current.csv",
        [
            "task_key",
            "ticker",
            "date",
            "session",
            "status",
            "rows",
            "file",
            "elapsed_sec",
            "processed_at_utc",
            "error",
        ],
        event_rows,
    )
    _write_trade_parquet(
        source_root / "OKAY/year=2024/month=01/day=2024-01-02/market.parquet",
        "OKAY",
        "2024-01-02",
    )
    return run_root, source_root


def _run_builder(
    tmp_path: Path,
    *,
    downloader_hash: str | None = None,
    output_name: str = "output",
) -> tuple[dict[str, object], list[dict[str, str]]]:
    run_root, source_root = _build_fixture(tmp_path)
    output_dir = tmp_path / output_name
    command = [
        sys.executable,
        str(BUILDER),
        "--run-root",
        str(run_root),
        "--source-root",
        str(source_root),
        "--output-dir",
        str(output_dir),
        "--run-id",
        "fixture_run_v0_1",
        "--hash-inputs",
    ]
    if downloader_hash is not None:
        command.extend(["--downloader-content-hash", downloader_hash])
    result = subprocess.run(
        command,
        cwd=MODULE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    manifest = json.loads(Path(payload["manifest"]).read_text(encoding="utf-8"))
    with Path(payload["csv"]).open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return manifest, rows


def test_coverage_sidecar_classifies_terminal_states(tmp_path: Path) -> None:
    manifest, rows = _run_builder(tmp_path)
    by_ticker = {row["ticker"]: row for row in rows}

    assert manifest["row_count"] == 4
    assert manifest["full_universe_claim"] is False
    assert manifest["canonical_promotion"] == "NOT_AUTHORIZED"
    assert by_ticker["OKAY"]["coverage_gate_state"] == "PASS_WITH_RESTRICTIONS"
    assert by_ticker["OKAY"]["row_count_match"] == "True"
    assert by_ticker["EMPT"]["coverage_gate_state"] == "PASS_WITH_RESTRICTIONS"
    assert by_ticker["EMPT"]["physical_file_exists"] == "False"
    assert by_ticker["FAIL"]["coverage_gate_state"] == "FAIL_UNAVAILABLE"
    assert "DOWNLOAD_FAILED" in by_ticker["FAIL"]["coverage_restriction_reason_codes"]
    assert by_ticker["MISS"]["coverage_gate_state"] == "FAIL_UNAVAILABLE"
    assert "MISSING_TERMINAL_EVENT" in by_ticker["MISS"]["coverage_restriction_reason_codes"]


def test_coverage_sidecar_uses_active_root_not_historical_path(tmp_path: Path) -> None:
    _, rows = _run_builder(tmp_path)
    okay = next(row for row in rows if row["ticker"] == "OKAY")
    assert str(tmp_path / "active_trades") in okay["active_physical_file"]
    assert "C:\\historical\\trades" in okay["historical_expected_file"] or "C:/historical/trades" in okay[
        "historical_expected_file"
    ]
    assert okay["active_physical_file"] != okay["historical_expected_file"]


def test_coverage_sidecar_fails_closed_on_downloader_identity_mismatch(tmp_path: Path) -> None:
    manifest, rows = _run_builder(tmp_path, downloader_hash="not-the-audited-hash")
    assert manifest["downloader_identity_matches"] is False
    assert all(row["coverage_gate_state"] == "FAIL_UNAVAILABLE" for row in rows)
    assert all("DOWNLOADER_IDENTITY_MISMATCH" in row["coverage_restriction_reason_codes"] for row in rows)


def test_coverage_sidecar_csv_is_deterministically_ordered(tmp_path: Path) -> None:
    _, rows = _run_builder(tmp_path)
    keys = [row["task_key"] for row in rows]
    assert keys == sorted(keys)

