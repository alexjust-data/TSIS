from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import pandas as pd


OK_STATUSES = {"DOWNLOADED_OK", "DOWNLOADED_EMPTY"}


def utc_stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--missing-csv", required=True)
    ap.add_argument("--events-history-csv", required=True)
    ap.add_argument("--outdir", default="")
    args = ap.parse_args()

    missing_csv = Path(args.missing_csv)
    events_history_csv = Path(args.events_history_csv)

    if not missing_csv.exists():
        raise SystemExit(f"missing csv not found: {missing_csv}")
    if not events_history_csv.exists():
        raise SystemExit(f"events history csv not found: {events_history_csv}")

    outdir = Path(args.outdir) if args.outdir else Path(
        rf"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\quotes_lt_1b_remaining_only\{utc_stamp()}_build_quotes_lt_1b_remaining_only_from_run_state"
    )
    outdir.mkdir(parents=True, exist_ok=True)

    missing = pd.read_csv(missing_csv, usecols=["ticker", "date"])
    missing["ticker"] = missing["ticker"].astype(str).str.upper().str.strip()
    missing["date"] = missing["date"].astype(str).str.strip()
    missing = missing.drop_duplicates().reset_index(drop=True)
    missing["task_key"] = missing["ticker"] + "|" + missing["date"]

    history = pd.read_csv(events_history_csv)
    if "ticker" not in history.columns or "date" not in history.columns or "status" not in history.columns:
        raise SystemExit("events history csv must contain ticker,date,status")

    history["ticker"] = history["ticker"].astype(str).str.upper().str.strip()
    history["date"] = history["date"].astype(str).str.strip()
    history["status"] = history["status"].astype(str).str.strip()
    history["task_key"] = history["ticker"] + "|" + history["date"]

    history_latest = history.drop_duplicates(subset=["task_key"], keep="last").copy()
    history_latest["is_ok_terminal"] = history_latest["status"].isin(OK_STATUSES)

    ok_keys = set(history_latest.loc[history_latest["is_ok_terminal"], "task_key"].astype(str))
    non_ok = history_latest.loc[~history_latest["is_ok_terminal"], ["task_key", "ticker", "date", "status"]].copy()
    non_ok = non_ok.rename(columns={"status": "current_status"})

    remaining = missing.loc[~missing["task_key"].isin(ok_keys), ["ticker", "date", "task_key"]].copy()
    remaining = remaining.merge(
        non_ok[["task_key", "current_status"]],
        on="task_key",
        how="left",
    )
    remaining["remaining_reason"] = remaining["current_status"].fillna("NOT_PROCESSED_YET")

    audit = missing.merge(
        history_latest[["task_key", "status"]].rename(columns={"status": "current_status"}),
        on="task_key",
        how="left",
    )
    audit["selection"] = "REMAINING_ONLY"
    audit.loc[audit["current_status"].isin(list(OK_STATUSES)), "selection"] = "ALREADY_RESOLVED_OK"

    remaining_csv = outdir / "tasks_quotes_lt_1b_remaining_only.csv"
    remaining_parquet = outdir / "tasks_quotes_lt_1b_remaining_only.parquet"
    audit_csv = outdir / "tasks_quotes_lt_1b_remaining_audit.csv"
    resolved_ok_csv = outdir / "tasks_quotes_lt_1b_already_resolved_ok.csv"
    manifest_json = outdir / "tasks_quotes_lt_1b_remaining_manifest.json"

    remaining[["ticker", "date", "current_status", "remaining_reason"]].to_csv(remaining_csv, index=False)
    remaining[["ticker", "date", "current_status", "remaining_reason"]].to_parquet(remaining_parquet, index=False)
    audit.to_csv(audit_csv, index=False)
    audit.loc[audit["selection"] == "ALREADY_RESOLVED_OK", ["ticker", "date", "current_status"]].to_csv(
        resolved_ok_csv, index=False
    )

    status_counts = history_latest["status"].value_counts(dropna=False).to_dict()
    manifest = {
        "missing_csv": str(missing_csv),
        "events_history_csv": str(events_history_csv),
        "outdir": str(outdir),
        "missing_total": int(len(missing)),
        "events_history_total": int(len(history)),
        "history_unique_task_keys": int(history_latest["task_key"].nunique()),
        "resolved_ok_terminal": int(len(ok_keys)),
        "remaining_total": int(len(remaining)),
        "remaining_not_processed_yet": int(remaining["remaining_reason"].eq("NOT_PROCESSED_YET").sum()),
        "remaining_fail_or_partial": int(remaining["remaining_reason"].ne("NOT_PROCESSED_YET").sum()),
        "status_counts_history_latest": status_counts,
    }
    manifest_json.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("=== SUMMARY ===")
    print(json.dumps(manifest, indent=2))
    print(f"saved: {remaining_csv}")


if __name__ == "__main__":
    main()
