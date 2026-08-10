"""Acquire only lifecycle primary documents admitted by the metadata lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = SCRIPT_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sec_pit.client import SecClient  # noqa: E402
from sec_pit.storage import ContentAddressedStore, append_jsonl, atomic_write_json  # noqa: E402

DEFAULT_SOURCE_RUN = Path(
    r"D:\TSIS\fundamental_context\sec_pit_v0_1\replays\sec_pit_7t_lifecycle_v0_1"
)
DEFAULT_OUTPUT_ROOT = Path(r"D:\TSIS\fundamental_context\sec_pit_v0_1")


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(arguments: list[str]) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *arguments],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def build_plan(ledger: pd.DataFrame, gates: pd.DataFrame) -> pd.DataFrame:
    required_gate_columns = {"ticker", "security_class_gate"}
    required_ledger_columns = {
        "ticker",
        "accession_number",
        "primary_document_url",
        "candidate_type",
        "filing_size_bytes",
    }
    if missing := required_gate_columns - set(gates.columns):
        raise ValueError(f"Missing gate columns: {sorted(missing)}")
    if missing := required_ledger_columns - set(ledger.columns):
        raise ValueError(f"Missing ledger columns: {sorted(missing)}")

    plan = ledger.merge(
        gates[["ticker", "security_class_gate", "deep_acquisition_state"]],
        on="ticker",
        how="left",
        validate="many_to_one",
    )
    plan = plan.loc[
        plan["security_class_gate"].eq("PASS")
        & plan["primary_document_url"].notna()
        & plan["primary_document_url"].astype(str).ne("")
    ].copy()
    if plan.duplicated(["ticker", "accession_number"]).any():
        raise ValueError("Duplicate ticker/accession rows in lifecycle acquisition plan")
    return plan.sort_values(
        ["ticker", "filing_date", "accession_number"], na_position="last"
    ).reset_index(drop=True)


def load_completed_urls(acquisition_log: Path) -> set[str]:
    if not acquisition_log.is_file():
        return set()
    completed: set[str] = set()
    with acquisition_log.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("status") == "FETCHED" and row.get("url"):
                completed.add(str(row["url"]))
    return completed


def write_heartbeat(
    run_root: Path,
    *,
    run_id: str,
    stage: str,
    status: str,
    completed: int,
    total: int,
    current_ticker: str | None = None,
    current_accession: str | None = None,
    failed: int = 0,
) -> None:
    payload = {
        "run_id": run_id,
        "observed_at_utc": utc_now(),
        "status": status,
        "stage": stage,
        "wrapper_pid": os.getpid(),
        "completed": completed,
        "total": total,
        "current_ticker": current_ticker,
        "current_accession": current_accession,
        "failed": failed,
    }
    atomic_write_json(run_root / "heartbeat_latest.json", payload)
    append_jsonl(run_root / "heartbeat.jsonl", payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, default=DEFAULT_SOURCE_RUN)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--user-agent", default=os.environ.get("SEC_USER_AGENT"))
    parser.add_argument("--requests-per-second", type=float, default=5.0)
    parser.add_argument("--minimum-free-space-gib", type=float, default=100.0)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.execute and (not args.user_agent or "@" not in args.user_agent):
        raise ValueError("A SEC-compliant --user-agent containing a contact email is required")

    source_run = args.source_run.resolve()
    output_root = args.output_root.resolve()
    run_root = output_root / "replays" / args.run_id
    if run_root.exists() and not args.resume:
        raise FileExistsError(f"Run exists; use --resume: {run_root}")
    run_root.mkdir(parents=True, exist_ok=True)

    ledger_path = source_run / "lifecycle_source_candidate_ledger.parquet"
    gates_path = source_run / "lifecycle_gate_matrix.parquet"
    ledger = pd.read_parquet(ledger_path)
    gates = pd.read_parquet(gates_path)
    plan = build_plan(ledger, gates)
    plan_path = run_root / "lifecycle_primary_acquisition_plan.parquet"
    plan.to_parquet(plan_path, index=False)

    free_gib = shutil.disk_usage(output_root).free / (1024**3)
    if free_gib < args.minimum_free_space_gib:
        raise RuntimeError(
            f"Free-space gate failed: {free_gib:.3f} GiB < "
            f"{args.minimum_free_space_gib:.3f} GiB"
        )

    script_path = Path(__file__).resolve()
    mode = "execute" if args.execute else "plan"
    manifest: dict[str, Any] = {
        "run_id": args.run_id,
        "status": "RUNNING",
        "created_at_utc": utc_now(),
        "mode": mode,
        "script_path": script_path.as_posix(),
        "script_sha256": sha256_file(script_path),
        "command_line": sys.argv,
        "cwd": Path.cwd().as_posix(),
        "host": socket.gethostname(),
        "wrapper_pid": os.getpid(),
        "git_branch": git_value(["branch", "--show-current"]),
        "git_commit": git_value(["rev-parse", "HEAD"]),
        "git_dirty_state": bool(git_value(["status", "--porcelain"])),
        "source_run": source_run.as_posix(),
        "source_ledger_sha256": sha256_file(ledger_path),
        "source_gates_sha256": sha256_file(gates_path),
        "output_root": output_root.as_posix(),
        "run_root": run_root.as_posix(),
        "object_store": (output_root / "objects").as_posix(),
        "planned_documents": len(plan),
        "planned_filing_size_bytes_ceiling": int(
            plan["filing_size_bytes"].fillna(0).sum()
        ),
        "requests_per_second": args.requests_per_second,
        "minimum_free_space_gib": args.minimum_free_space_gib,
        "free_space_gib_at_start": round(free_gib, 3),
        "scope": "LIFECYCLE_PRIMARY_DOCUMENTS_ONLY",
        "complete_submissions": "PROHIBITED",
        "exhibits": "PROHIBITED",
        "security_class_failures": sorted(
            gates.loc[gates["security_class_gate"].ne("PASS"), "ticker"].astype(str)
        ),
        "resume_policy": "reuse fetched URLs from acquisition.jsonl",
        "overwrite_policy": "forbidden_without_resume",
        "success_criteria": "all planned lifecycle primary documents fetched",
        "promotion_status": "NOT_AUTHORIZED",
        "monitor_command": (
            f'powershell -NoProfile -File "{(SCRIPT_DIR / "monitor_sec_pit_run.ps1")}" '
            f'-RunRoot "{run_root}" -Compact -IntervalSeconds 5'
        ),
    }
    atomic_write_json(run_root / "pre_manifest.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": args.run_id,
            "wrapper_pid": os.getpid(),
            "started_at_utc": utc_now(),
            "expected_alive": True,
        },
    )
    write_heartbeat(
        run_root,
        run_id=args.run_id,
        stage="PLAN_READY",
        status="RUNNING",
        completed=0,
        total=len(plan),
    )
    print(json.dumps({
        "run_id": args.run_id,
        "mode": mode,
        "run_root": run_root.as_posix(),
        "planned_documents": len(plan),
        "monitor_command": manifest["monitor_command"],
    }, indent=2), flush=True)

    if not args.execute:
        final = {
            **manifest,
            "status": "COMPLETE",
            "completed_at_utc": utc_now(),
            "result": "PLAN_ONLY",
        }
        atomic_write_json(run_root / "final_manifest.json", final)
        write_heartbeat(
            run_root,
            run_id=args.run_id,
            stage="PLAN_COMPLETE",
            status="COMPLETE",
            completed=0,
            total=len(plan),
        )
        return 0

    acquisition_log = run_root / "acquisition.jsonl"
    completed_urls = load_completed_urls(acquisition_log) if args.resume else set()
    client = SecClient(
        user_agent=args.user_agent,
        store=ContentAddressedStore(output_root / "objects"),
        acquisition_log=acquisition_log,
        requests_per_second=args.requests_per_second,
    )

    results: list[dict[str, Any]] = []
    failed = 0
    for index, row in enumerate(plan.to_dict("records"), start=1):
        url = str(row["primary_document_url"])
        if url in completed_urls:
            results.append({
                "ticker": row["ticker"],
                "accession_number": row["accession_number"],
                "url": url,
                "status": "SKIPPED_ALREADY_FETCHED",
            })
        else:
            document_name = Path(urlparse(url).path).name or "primary_document"
            logical_path = (
                f"lifecycle/{row['ticker']}/{row['accession_number']}/"
                f"primary/{document_name}"
            )
            result = client.fetch(url, logical_path)
            result_row = {
                "ticker": row["ticker"],
                "accession_number": row["accession_number"],
                "candidate_type": row["candidate_type"],
                **result.to_dict(),
            }
            results.append(result_row)
            if result.status != "FETCHED":
                failed += 1
        write_heartbeat(
            run_root,
            run_id=args.run_id,
            stage="ACQUIRE_LIFECYCLE_PRIMARY",
            status="RUNNING",
            completed=index,
            total=len(plan),
            current_ticker=str(row["ticker"]),
            current_accession=str(row["accession_number"]),
            failed=failed,
        )

    result_frame = pd.DataFrame(results)
    result_frame.to_parquet(run_root / "lifecycle_primary_acquisition_results.parquet", index=False)
    fetched_or_reused = int(
        result_frame["status"].isin(["FETCHED", "SKIPPED_ALREADY_FETCHED"]).sum()
    )
    final_status = "COMPLETE" if failed == 0 and fetched_or_reused == len(plan) else "FAILED"
    final = {
        **manifest,
        "status": final_status,
        "completed_at_utc": utc_now(),
        "planned_documents": len(plan),
        "fetched_or_reused_documents": fetched_or_reused,
        "failed_documents": failed,
        "acquired_response_bytes": int(
            pd.to_numeric(result_frame.get("bytes"), errors="coerce").fillna(0).sum()
        ),
        "primary_document_extraction": "NOT_EXECUTED",
        "lifecycle_event_resolution": "NOT_EXECUTED",
        "promotion_status": "NOT_AUTHORIZED",
    }
    atomic_write_json(run_root / "final_manifest.json", final)
    write_heartbeat(
        run_root,
        run_id=args.run_id,
        stage="ACQUISITION_COMPLETE" if final_status == "COMPLETE" else "ACQUISITION_FAILED",
        status=final_status,
        completed=fetched_or_reused,
        total=len(plan),
        failed=failed,
    )
    print(json.dumps(final, indent=2), flush=True)
    return 0 if final_status == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())