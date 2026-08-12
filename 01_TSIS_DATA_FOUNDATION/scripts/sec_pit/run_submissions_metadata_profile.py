#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import psutil

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.client import SecClient
from sec_pit.metadata import (
    SUBMISSIONS_URL,
    filing_roles,
    parse_submissions_root,
    parse_submissions_supplement,
    primary_document_url,
)
from sec_pit.storage import ContentAddressedStore, append_jsonl, atomic_write_json
from sec_pit.telemetry import LiveResourceTelemetry


OFFERING_FORMS = {
    "S-1", "S-1/A", "S-3", "S-3/A", "F-1", "F-1/A", "F-3", "F-3/A",
    "424B1", "424B2", "424B3", "424B4", "424B5", "POS AM",
}
FORM_13DG = {
    "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A",
    "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G", "SCHEDULE 13G/A",
}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def profile_inventory(ticker: str, cik: str, inventory: pd.DataFrame) -> dict[str, Any]:
    forms = inventory["form"].fillna("").astype(str).str.upper()
    dates = pd.to_datetime(inventory["filing_date"], errors="coerce")
    items = inventory["items"].fillna("").astype(str)
    history_years = 0.0
    if dates.notna().any():
        history_years = float((dates.max() - dates.min()).days / 365.25)
    counts = forms.value_counts()
    count = lambda names: int(forms.isin(names).sum())
    def14a = int(counts.get("DEF 14A", 0))
    merger_proxy = count({"PREM14A", "DEFM14A", "PREM14C", "DEFM14C"})
    form4 = count({"4", "4/A"})
    thirteen = count(FORM_13DG)
    offerings = count(OFFERING_FORMS)
    twenty_f = count({"20-F", "20-F/A"})
    twenty_f_amend = int(counts.get("20-F/A", 0))
    tags = []
    if def14a:
        tags.append("DOMESTIC_ANNUAL_PROXY_CANDIDATE")
    if merger_proxy or def14a >= 3:
        tags.append("PROXY_VARIETY_OR_SPECIAL_MEETING_CANDIDATE")
    if twenty_f:
        tags.append("FOREIGN_20F_HISTORY")
    if twenty_f_amend >= 2:
        tags.append("FOREIGN_20F_MULTIPLE_AMENDMENTS")
    if form4 >= 50:
        tags.append("MANY_FORM4")
    if thirteen >= 20:
        tags.append("HEAVY_13DG_HISTORY")
    if history_years >= 5 and def14a <= 1 and not twenty_f:
        tags.append("SPARSE_PROXY_HISTORY")
    if dates.lt(pd.Timestamp("2009-01-01")).any():
        tags.append("PRE_XBRL_HISTORY")
    if offerings >= 20:
        tags.append("FREQUENT_OFFERINGS")
    if items.str.split(",").map(lambda values: any(value.strip() == "1.03" for value in values)).any():
        tags.append("BANKRUPTCY_OR_RECEIVERSHIP_ITEM_1_03")
    if count({"25", "25-NSE", "15-12G", "15-12G/A", "15-15D", "15-15D/A"}):
        tags.append("DELISTING_OR_DEREGISTRATION_HISTORY")
    return {
        "ticker": ticker,
        "cik": cik,
        "filing_count": len(inventory),
        "first_filing_date": dates.min(),
        "last_filing_date": dates.max(),
        "filing_history_years": history_years,
        "def14a_count": def14a,
        "merger_proxy_count": merger_proxy,
        "twenty_f_count": twenty_f,
        "twenty_f_amendment_count": twenty_f_amend,
        "form4_count": form4,
        "thirteen_dg_count": thirteen,
        "offering_form_count": offerings,
        "document_strata_json": json.dumps(tags, separators=(",", ":")),
    }


def execute(args: argparse.Namespace) -> Path:
    pool_path = args.candidate_pool.resolve()
    output = args.output.resolve()
    pool_hash = __import__("hashlib").sha256(pool_path.read_bytes()).hexdigest()
    if output.exists() and not args.resume:
        raise FileExistsError(output)
    output.mkdir(parents=True, exist_ok=True)
    ticker_root = output / "tickers"
    ticker_root.mkdir(exist_ok=True)
    pre_path = output / "pre_manifest.json"
    if pre_path.exists():
        pre = json.loads(pre_path.read_text(encoding="utf-8"))
        if pre["candidate_pool_sha256"] != pool_hash:
            raise ValueError("resume input hash mismatch")
    else:
        pre = {
            "run_id": output.name,
            "status": "RUNNING",
            "created_at_utc": utc_now(),
            "candidate_pool_path": pool_path.as_posix(),
            "candidate_pool_sha256": pool_hash,
            "scope": "SEC_SUBMISSIONS_METADATA_ONLY",
            "companyfacts": "NOT_REQUESTED",
            "primary_documents": "NOT_REQUESTED",
            "complete_submissions": "NOT_REQUESTED",
            "requests_per_second": args.requests_per_second,
            "minimum_available_memory_gib": args.minimum_available_memory_gib,
            "monitor_command": (
                "powershell -NoProfile -ExecutionPolicy Bypass -File "
                "C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/monitor_sec_pit_run.ps1 "
                f"-RunRoot {output.as_posix()} -Compact -IntervalSeconds 30"
            ),
        }
        atomic_write_json(pre_path, pre)
    atomic_write_json(output / "pid_manifest.json", {
        "wrapper_pid": os.getpid(), "started_at_utc": utc_now(), "resume": args.resume,
    })
    pool = pd.read_parquet(pool_path).sort_values("selection_order")
    state: dict[str, Any] = {
        "status": "RUNNING", "stage": "SEC_SUBMISSIONS_METADATA",
        "completed": 0, "total": len(pool), "filing_count": 0,
    }
    telemetry = LiveResourceTelemetry(
        run_root=output,
        output_root=output,
        run_id=output.name,
        interval_seconds=args.telemetry_interval_seconds,
        state_snapshot=lambda: state,
    )
    client = SecClient(
        user_agent=args.user_agent,
        store=ContentAddressedStore(args.object_root.resolve()),
        acquisition_log=output / "acquisition.jsonl",
        requests_per_second=args.requests_per_second,
        telemetry_log=output / "request_performance.jsonl",
    )
    telemetry.start()
    try:
        for index, row in enumerate(pool.to_dict("records"), start=1):
            ticker = str(row["ticker"])
            cik = "".join(character for character in str(row["cik"]) if character.isdigit()).zfill(10)
            case_root = ticker_root / ticker.lower()
            inventory_path = case_root / "filing_inventory.parquet"
            profile_path = case_root / "profile.json"
            state.update({"current_index": index, "current_item": ticker})
            if inventory_path.exists() and profile_path.exists():
                state["completed"] = int(state["completed"]) + 1
                state["filing_count"] = int(state["filing_count"]) + len(pd.read_parquet(inventory_path))
                continue
            while psutil.virtual_memory().available / (1024**3) < args.minimum_available_memory_gib:
                state["stage"] = "PAUSED_LOW_MEMORY"
                time.sleep(10)
            state["stage"] = "SEC_SUBMISSIONS_METADATA"
            result, payload = client.fetch_json(
                SUBMISSIONS_URL.format(cik=cik), f"submissions/{cik}.json",
            )
            if payload is None:
                raise RuntimeError(f"submissions root failed for {ticker} {cik}")
            records, supplements = parse_submissions_root(payload, result.object_path or "")
            for supplement_name in supplements:
                supplement_result, supplement = client.fetch_json(
                    f"https://data.sec.gov/submissions/{supplement_name}",
                    f"submissions/{cik}/{supplement_name}",
                )
                if supplement is not None:
                    records.extend(parse_submissions_supplement(cik, supplement, supplement_result.object_path or ""))
            rows = []
            for record in records:
                value = asdict(record)
                value.update({
                    "ticker": ticker,
                    "roles": filing_roles(record),
                    "primary_document_url": primary_document_url(record),
                })
                rows.append(value)
            inventory = pd.DataFrame(rows).sort_values(["filing_date", "accession_number"])
            case_root.mkdir(exist_ok=True)
            temporary = inventory_path.with_suffix(".parquet.tmp")
            inventory.to_parquet(temporary, index=False)
            os.replace(temporary, inventory_path)
            profile = profile_inventory(ticker, cik, inventory)
            atomic_write_json(profile_path, profile)
            state["completed"] = int(state["completed"]) + 1
            state["filing_count"] = int(state["filing_count"]) + len(inventory)
        profiles = pd.DataFrame([
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(ticker_root.glob("*/profile.json"))
        ])
        profiles = pool.merge(profiles, on=["ticker", "cik"], how="left", validate="one_to_one")
        profiles.to_parquet(output / "candidate_metadata_profiles.parquet", index=False)
        profiles.to_csv(output / "candidate_metadata_profiles.csv", index=False)
        state.update({"status": "COMPLETE", "stage": "COMPLETE"})
        previous_final_path = output / "final_manifest.json"
        previous_final = (
            json.loads(previous_final_path.read_text(encoding="utf-8"))
            if previous_final_path.exists()
            else {}
        )
        merged_peaks = dict(previous_final.get("telemetry_peaks", {}))
        for key, value in telemetry.peaks.items():
            merged_peaks[key] = max(float(merged_peaks.get(key, 0.0)), float(value))
        failed_path = output / "failed_manifest.json"
        if failed_path.exists():
            append_jsonl(output / "recovered_attempts.jsonl", {
                "recovered_at_utc": utc_now(),
                "failure": json.loads(failed_path.read_text(encoding="utf-8")),
            })
            failed_path.unlink()
        final = {
            **pre,
            "status": "COMPLETE",
            "completed_at_utc": utc_now(),
            "candidate_count": len(profiles),
            "filing_count": int(profiles["filing_count"].sum()),
            "completed_tickers": int(profiles["filing_count"].notna().sum()),
            "telemetry_peaks": merged_peaks,
            "next_gate": "FREEZE_EXACT_100_CASE_SAMPLE",
            "primary_documents": "NOT_REQUESTED",
        }
        atomic_write_json(output / "final_manifest.json", final)
    except Exception as exc:
        state.update({"status": "FAILED", "stage": "FAILED", "error": f"{type(exc).__name__}: {exc}"})
        atomic_write_json(output / "failed_manifest.json", {**pre, **state, "failed_at_utc": utc_now()})
        raise
    finally:
        telemetry.stop()
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-pool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--object-root", type=Path, required=True)
    parser.add_argument("--user-agent", required=True)
    parser.add_argument("--requests-per-second", type=float, default=5.0)
    parser.add_argument("--telemetry-interval-seconds", type=float, default=10.0)
    parser.add_argument("--minimum-available-memory-gib", type=float, default=8.0)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    print(execute(parse_args()))
