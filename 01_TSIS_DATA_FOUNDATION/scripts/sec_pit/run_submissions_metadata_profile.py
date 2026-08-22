#!/usr/bin/env python
# ruff: noqa: E402
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import socket
import subprocess
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
from sec_pit.storage import (
    ContentAddressedStore,
    append_jsonl,
    atomic_write_json,
    read_jsonl,
)
from sec_pit.telemetry import LiveResourceTelemetry, summarize_document_performance

CANONICAL_OBJECT_ROOT = Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1\objects")
LEGACY_PILOT_ROOT = Path(r"D:\sec_float_pit_v0_1")

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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=Path(__file__).resolve().parents[3], text=True
        ).strip()
    except Exception:
        return None


def require_canonical_object_root(
    object_root: Path, canonical_root: Path = CANONICAL_OBJECT_ROOT
) -> Path:
    resolved = object_root.resolve()
    canonical = canonical_root.resolve()
    if os.path.normcase(str(resolved)) != os.path.normcase(str(canonical)):
        raise ValueError(
            "object-root is not the governed active SEC PIT content store: "
            f"expected {canonical}, got {resolved}"
        )
    return resolved


def profile_inventory(ticker: str, cik: str, inventory: pd.DataFrame) -> dict[str, Any]:
    forms = inventory["form"].fillna("").astype(str).str.upper()
    dates = pd.to_datetime(inventory["filing_date"], errors="coerce")
    items = inventory["items"].fillna("").astype(str)
    history_years = 0.0
    if dates.notna().any():
        history_years = float((dates.max() - dates.min()).days / 365.25)
    counts = forms.value_counts()
    def count(names: set[str]) -> int:
        return int(forms.isin(names).sum())

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
    started_monotonic = time.monotonic()
    pool_path = args.candidate_pool.resolve()
    output = args.output.resolve()
    object_root = require_canonical_object_root(args.object_root)
    if not args.user_agent or "@" not in args.user_agent:
        raise ValueError(
            "--user-agent or SEC_USER_AGENT must identify the organization and contain a contact email"
        )
    pool_hash = file_sha256(pool_path)
    if output.exists() and not args.resume:
        raise FileExistsError(output)
    existing_pid_path = output / "pid_manifest.json"
    if args.resume and existing_pid_path.exists():
        existing_pid = json.loads(existing_pid_path.read_text(encoding="utf-8"))
        wrapper_pid = int(existing_pid.get("wrapper_pid") or 0)
        if wrapper_pid and wrapper_pid != os.getpid() and psutil.pid_exists(wrapper_pid):
            raise RuntimeError(f"refusing duplicate writer; wrapper PID {wrapper_pid} is alive")
    output.mkdir(parents=True, exist_ok=True)
    ticker_root = output / "tickers"
    ticker_root.mkdir(exist_ok=True)
    pre_path = output / "pre_manifest.json"
    if pre_path.exists():
        pre = json.loads(pre_path.read_text(encoding="utf-8"))
        if pre["candidate_pool_sha256"] != pool_hash:
            raise ValueError("resume input hash mismatch")
        if Path(pre["object_root"]).resolve() != object_root:
            raise ValueError("resume object-root mismatch")
    else:
        monitor_command = (
            "powershell -NoProfile -ExecutionPolicy Bypass -File "
            "C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/monitor_sec_pit_run.ps1 "
            f'-RunRoot "{output.as_posix()}" -Compact -IntervalSeconds 10'
        )
        pre = {
            "run_id": output.name,
            "status": "RUNNING",
            "created_at_utc": utc_now(),
            "script_path": Path(__file__).resolve().as_posix(),
            "script_sha256": file_sha256(Path(__file__).resolve()),
            "command_line": subprocess.list2cmdline(sys.argv),
            "cwd": Path.cwd().as_posix(),
            "host": socket.gethostname(),
            "user": getpass.getuser(),
            "parent_pid": os.getppid(),
            "wrapper_pid": os.getpid(),
            "git_branch": git_value("branch", "--show-current"),
            "git_commit": git_value("rev-parse", "HEAD"),
            "git_dirty_state": bool(git_value("status", "--porcelain")),
            "mode": "SEC_SUBMISSIONS_METADATA_ONLY",
            "candidate_pool_path": pool_path.as_posix(),
            "candidate_pool_sha256": pool_hash,
            "object_root": object_root.as_posix(),
            "canonical_sec_root": object_root.parent.as_posix(),
            "legacy_pilot_root": LEGACY_PILOT_ROOT.as_posix(),
            "legacy_pilot_root_state": "IMMUTABLE_READ_ONLY_PROVENANCE_NO_NEW_WRITES",
            "output_root": output.as_posix(),
            "log_path": (output / "run.log").as_posix(),
            "pid_manifest_path": (output / "pid_manifest.json").as_posix(),
            "heartbeat_latest_path": (output / "heartbeat_latest.json").as_posix(),
            "heartbeat_history_path": (output / "heartbeat.jsonl").as_posix(),
            "scope": "SEC_SUBMISSIONS_METADATA_ONLY",
            "companyfacts": "NOT_REQUESTED",
            "primary_documents": "NOT_REQUESTED",
            "complete_submissions": "NOT_REQUESTED",
            "requests_per_second": args.requests_per_second,
            "minimum_available_memory_gib": args.minimum_available_memory_gib,
            "expected_scope": "one frozen acquisition cohort",
            "resume_policy": "--resume skips tickers with complete inventory and profile; content store deduplicates by SHA-256",
            "overwrite_policy": "never overwrite content-addressed objects; output root requires --resume",
            "success_criteria": "all frozen cohort tickers have filing_inventory.parquet and profile.json",
            "monitor_command": monitor_command,
        }
        atomic_write_json(pre_path, pre)
    atomic_write_json(output / "pid_manifest.json", {
        "wrapper_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "process_name": Path(sys.executable).name,
        "command_line": subprocess.list2cmdline(sys.argv),
        "started_at_utc": utc_now(),
        "stage": "SEC_SUBMISSIONS_METADATA",
        "expected_alive": True,
        "resume": args.resume,
    })
    for key in (
        "run_id", "mode", "candidate_pool_path", "output_root", "object_root",
        "pid_manifest_path", "heartbeat_latest_path", "log_path", "monitor_command",
        "success_criteria", "resume_policy",
    ):
        print(f"{key}={pre[key]}", flush=True)
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
        store=ContentAddressedStore(object_root),
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
        request_performance_path = output / "request_performance.jsonl"
        request_performance = summarize_document_performance(
            read_jsonl([request_performance_path])
            if request_performance_path.is_file()
            else []
        )
        request_summary = {
            "request_count": int(request_performance["document_count"]),
            "fetched": int(request_performance["fetched"]),
            "failed": int(request_performance["failed"]),
            "retry_count": int(request_performance["retry_count"]),
            "http_429_count": int(request_performance["http_429_count"]),
            "bytes": int(request_performance["bytes"]),
            "request_latency_seconds": request_performance[
                "http_attempt_latency_seconds"
            ],
        }
        identity_summary = {
            "instrument_identity_reused_rows": int(
                pool["instrument_identity_reused_in_parent_universe"].fillna(False).sum()
            ),
            "instrument_identity_cik_conflict_rows": int(
                pool["instrument_identity_cik_conflict"].fillna(False).sum()
            ),
            "unique_instrument_ids": int(pool["instrument_id"].nunique()),
            "unique_ciks": int(pool["cik"].nunique()),
        }
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
            "duration_seconds": time.monotonic() - started_monotonic,
            "exit_code": 0,
            "success_rule": "all frozen cohort tickers have filing_inventory.parquet and profile.json",
            "candidate_count": len(profiles),
            "filing_count": int(profiles["filing_count"].sum()),
            "completed_tickers": int(profiles["filing_count"].notna().sum()),
            "metadata_completeness": (
                f"{int(profiles['filing_count'].notna().sum())}/{len(pool)}"
            ),
            "request_summary": request_summary,
            "identity_summary": identity_summary,
            "telemetry_peaks": merged_peaks,
            "next_gate": args.next_gate,
            "primary_documents": "NOT_REQUESTED",
            "resume_instructions": "rerun the exact command with --resume if interrupted",
            "promotion_status": "RUNTIME_METADATA_EVIDENCE_NOT_INSTITUTIONAL",
            "output_artifacts": {
                name: file_sha256(output / name)
                for name in (
                    "candidate_metadata_profiles.parquet",
                    "candidate_metadata_profiles.csv",
                )
            },
            "warnings": [],
        }
        atomic_write_json(output / "final_manifest.json", final)
        atomic_write_json(
            output / "pid_manifest.json",
            {
                "wrapper_pid": os.getpid(),
                "process_name": Path(sys.executable).name,
                "stage": "COMPLETE",
                "expected_alive": False,
                "ended_at_utc": utc_now(),
                "exit_code": 0,
            },
        )
    except BaseException as exc:
        interrupted = isinstance(exc, KeyboardInterrupt)
        terminal_status = "INTERRUPTED" if interrupted else "FAILED"
        exit_code = 130 if interrupted else 1
        state.update(
            {
                "status": terminal_status,
                "stage": terminal_status,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        failure = {
            **pre,
            **state,
            "failed_at_utc": utc_now(),
            "duration_seconds": time.monotonic() - started_monotonic,
            "exit_code": exit_code,
            "failure_reason": f"{type(exc).__name__}: {exc}",
            "resume_instructions": "fix the reported cause, then rerun the exact command with --resume",
            "promotion_status": f"{terminal_status}_RUNTIME_NOT_PROMOTED",
        }
        atomic_write_json(output / "failed_manifest.json", failure)
        atomic_write_json(output / "final_manifest.json", failure)
        atomic_write_json(
            output / "pid_manifest.json",
            {
                "wrapper_pid": os.getpid(),
                "process_name": Path(sys.executable).name,
                "stage": terminal_status,
                "expected_alive": False,
                "ended_at_utc": utc_now(),
                "exit_code": exit_code,
            },
        )
        raise
    finally:
        telemetry.stop()
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-pool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--object-root", type=Path, required=True)
    parser.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT"))
    parser.add_argument("--requests-per-second", type=float, default=5.0)
    parser.add_argument("--telemetry-interval-seconds", type=float, default=10.0)
    parser.add_argument("--minimum-available-memory-gib", type=float, default=8.0)
    parser.add_argument("--next-gate", default="BUILD_AND_REVIEW_PREDOWNLOAD_CONTROL")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    print(execute(parse_args()))
