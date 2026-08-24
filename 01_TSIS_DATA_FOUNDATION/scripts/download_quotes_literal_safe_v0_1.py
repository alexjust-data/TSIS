#!/usr/bin/env python3
"""Literal-safe governed entrypoint for the historical Quotes downloader.

This wrapper deliberately preserves the proven download/pagination/write logic in
``download_quotes.py`` while replacing only its CSV readers.  Pandas' default NA
tokens include the valid market symbol ``NA``; therefore task and resume ledgers
must be read with ``keep_default_na=False`` and explicit string identity columns.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


LEGACY_DOWNLOADER = Path(__file__).with_name("download_quotes.py")


def _load_legacy_module():
    spec = importlib.util.spec_from_file_location("tsis_download_quotes_legacy", LEGACY_DOWNLOADER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load legacy downloader: {LEGACY_DOWNLOADER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_csv_tasks_literal_safe(csv_path: Path, legacy) -> pd.DataFrame:
    df = pd.read_csv(
        csv_path,
        keep_default_na=False,
        dtype={"ticker": "string", "date": "string"},
    )
    if "ticker" not in df.columns or "date" not in df.columns:
        raise ValueError("CSV debe contener columnas: ticker,date")

    out = df[["ticker", "date"]].copy()
    out["ticker"] = out["ticker"].str.strip()
    out["date"] = out["date"].str.strip()

    invalid = out["ticker"].isna() | out["ticker"].eq("") | out["date"].isna() | out["date"].eq("")
    if bool(invalid.any()):
        sample = out.loc[invalid].head(10).to_dict(orient="records")
        raise ValueError(f"Task identity contains null/blank ticker or date: {sample}")

    out = out.drop_duplicates(subset=["ticker", "date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    out["task_key"] = [legacy.task_key(ticker, date) for ticker, date in out[["ticker", "date"]].itertuples(index=False, name=None)]
    return out


def load_current_literal_safe(events_current_csv: Path, legacy) -> pd.DataFrame:
    if not events_current_csv.exists():
        return pd.DataFrame(columns=legacy.EVENT_COLUMNS)
    try:
        df = pd.read_csv(
            events_current_csv,
            keep_default_na=False,
            dtype={
                "task_key": "string",
                "ticker": "string",
                "date": "string",
                "status": "string",
            },
        )
    except Exception as exc:
        raise RuntimeError(f"Cannot read resume ledger {events_current_csv}: {exc}") from exc

    for column in legacy.EVENT_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

    if len(df):
        invalid = df["ticker"].isna() | df["ticker"].str.strip().eq("")
        if bool(invalid.any()):
            raise ValueError("Resume ledger contains null/blank ticker identity")
    return df[legacy.EVENT_COLUMNS].copy()


def _cli_value(flag: str) -> str | None:
    try:
        index = sys.argv.index(flag)
    except ValueError:
        return None
    if index + 1 >= len(sys.argv):
        raise ValueError(f"Missing value after {flag}")
    return sys.argv[index + 1]


def install_literal_safe_overrides(legacy) -> None:
    legacy.read_csv_tasks = lambda path: read_csv_tasks_literal_safe(path, legacy)
    legacy.load_current = lambda path: load_current_literal_safe(path, legacy)
    # One empty response remains resumable until a second request records
    # EMPTY_CONFIRMED.
    legacy.RESUME_SKIP_STATUSES = {"DOWNLOADED_OK", "EMPTY_CONFIRMED"}


def main() -> int:
    legacy = _load_legacy_module()
    install_literal_safe_overrides(legacy)

    max_empty_rechecks = int(_cli_value("--max-empty-rechecks") or "2")
    passes = max(1, max_empty_rechecks)
    for pass_number in range(1, passes + 1):
        result = int(legacy.main())
        if result != 0:
            return result
        if pass_number < passes and "--resume" not in sys.argv:
            sys.argv.append("--resume")

    run_dir_value = _cli_value("--run-dir")
    csv_value = _cli_value("--csv")
    if csv_value is None:
        raise ValueError("Missing required --csv")
    run_dir = Path(run_dir_value) if run_dir_value else Path(csv_value).resolve().parent
    current = load_current_literal_safe(run_dir / "download_events_current.csv", legacy)
    unresolved = current[current["status"].isin(["DOWNLOAD_FAIL", "DOWNLOAD_PARTIAL", "DOWNLOADED_EMPTY"])]
    if len(unresolved):
        print(f"ERROR: unresolved terminal/recheck states={len(unresolved)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
