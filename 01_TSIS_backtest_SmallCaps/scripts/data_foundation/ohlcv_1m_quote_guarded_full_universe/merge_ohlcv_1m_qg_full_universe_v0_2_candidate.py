from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from qg_full_universe_common import (
    atomic_write_json,
    base_manifest,
    ensure_dir,
    human_bytes,
    utc_now,
    write_heartbeat,
)


DEFAULT_ORIGINAL_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1"
)
DEFAULT_DELTA_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate"
)
DEFAULT_OUTPUT_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate"
)
DEFAULT_EXPECTED_FAILURES = Path(
    r"C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/06_TABLES/013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv"
)
DEFAULT_RECONCILIATION_RESULT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate/_reconciliation_runs/qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z/reconciliation_result.json"
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Build OHLCV 1m quote-guarded full-universe v0_2_candidate from v0_1 plus failed-delta rerun."
    )
    p.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    p.add_argument("--delta-root", type=Path, default=DEFAULT_DELTA_ROOT)
    p.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    p.add_argument("--expected-failures", type=Path, default=DEFAULT_EXPECTED_FAILURES)
    p.add_argument("--reconciliation-result", type=Path, default=DEFAULT_RECONCILIATION_RESULT)
    p.add_argument("--run-id", default=None)
    p.add_argument("--mode", choices=["hardlink", "copy"], default="hardlink")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--heartbeat-every-sec", type=float, default=30.0)
    p.add_argument("--max-original-files", type=int, default=None, help="Smoke-only limit for original source files.")
    p.add_argument("--max-delta-files", type=int, default=None, help="Smoke-only limit for delta source files.")
    return p


def make_run_id() -> str:
    return "qg_1m_full_universe_v0_2_candidate_merge_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def clean_csv_row(row: Dict[str, str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key, value in row.items():
        clean_key = (key or "").strip().strip('"').lstrip("\ufeff")
        out[clean_key] = (value or "").strip().strip('"')
    return out


def read_expected_pairs(path: Path) -> Set[Tuple[int, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = [clean_csv_row(row) for row in csv.DictReader(fh)]
    return {(int(row["year"]), row["ticker"].upper()) for row in rows}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def parse_partition(path: Path) -> Optional[Tuple[int, str, Optional[int]]]:
    year: Optional[int] = None
    ticker: Optional[str] = None
    month: Optional[int] = None
    for part in path.parts:
        if part.startswith("year="):
            try:
                year = int(part.split("=", 1)[1])
            except ValueError:
                return None
        elif part.startswith("ticker="):
            ticker = part.split("=", 1)[1].upper()
        elif part.startswith("month="):
            try:
                month = int(part.split("=", 1)[1])
            except ValueError:
                return None
    if year is None or ticker is None:
        return None
    return year, ticker, month


def iter_partition_files(root: Path) -> Iterable[Path]:
    yield from root.glob("year=*/ticker=*/month=*/part-000.parquet")


def safe_same_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def materialize_link_or_copy(source: Path, target: Path, mode: str, resume: bool, dry_run: bool) -> str:
    if target.exists():
        if resume and safe_same_file(source, target):
            return "skipped_existing_samefile"
        if resume and target.stat().st_size == source.stat().st_size:
            return "skipped_existing_same_size"
        raise FileExistsError(f"target exists and is not reusable: {target}")
    if dry_run:
        return "planned"
    target.parent.mkdir(parents=True, exist_ok=True)
    if mode == "hardlink":
        os.link(source, target)
        return "hardlinked"
    shutil.copy2(source, target)
    return "copied"


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    tmp = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.time_ns()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def disk_free(path: Path) -> Optional[int]:
    try:
        probe = path if path.exists() else path.parent
        usage = shutil.disk_usage(probe)
        return int(usage.free)
    except OSError:
        return None


def append_log(path: Path, line: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def build_readme(result: Dict[str, Any]) -> str:
    return f"""# ohlcv_1m_quote_guarded_full_universe_v0_2_candidate

Status: `candidate_not_promoted`

Created by governed technical merge.

```text
original_root = {result["original_root"]}
delta_root = {result["delta_root"]}
merge_run_id = {result["run_id"]}
merge_status = {result["status"]}
mode = {result["mode"]}
```

Merge rule:

```text
For the 3,918 expected failed ticker-years, delta supersedes original v0_1.
For all other partitions, original v0_1 remains the source for this candidate.
```

Boundary:

```text
This tree is a technical merge candidate.
It is not an institutional promotion.
Promotion requires separate validation, manifests, status matrix and consumption-policy updates.
```
"""


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or make_run_id()
    run_root = args.output_root / "_build_runs" / run_id
    log_path = run_root / "merge.log"
    heartbeat_latest = run_root / "heartbeat_latest.json"
    final_manifest_path = run_root / "final_manifest_merge.json"

    ensure_dir(run_root)
    monitor_cmd = (
        f'python "{Path(__file__).with_name("monitor_ohlcv_1m_qg_merge_v0_1.py")}" '
        f'--run-root "{run_root}" --watch --interval-sec 30 --compact'
    )

    expected_pairs = read_expected_pairs(args.expected_failures)
    reconciliation = read_json(args.reconciliation_result)
    if reconciliation.get("status") != "PASS" or not reconciliation.get("merge_authorization"):
        raise RuntimeError(f"reconciliation result does not authorize merge: {args.reconciliation_result}")

    smoke_limited = args.max_original_files is not None or args.max_delta_files is not None
    if smoke_limited and args.output_root == DEFAULT_OUTPUT_ROOT:
        raise RuntimeError("Refusing smoke-limited run into the real v0_2_candidate output root.")
    if args.output_root.exists() and not args.resume:
        existing = [x for x in args.output_root.iterdir() if x.name != "_build_runs"]
        if existing:
            raise FileExistsError(f"output root exists and is not empty; use --resume only if intentional: {args.output_root}")

    manifest = base_manifest(
        run_id=run_id,
        script_path=Path(__file__),
        command_line=sys.argv,
        mode="merge_v0_2_candidate",
        input_roots={
            "original_root": str(args.original_root),
            "delta_root": str(args.delta_root),
            "expected_failures": str(args.expected_failures),
            "reconciliation_result": str(args.reconciliation_result),
        },
        output_roots={"output_root": str(args.output_root), "run_root": str(run_root)},
        expected_scope={
            "expected_delta_ticker_years": len(expected_pairs),
            "original_scope": "all year=*/ticker=*/month=*/part-000.parquet excluding expected failed pairs",
            "delta_scope": "expected failed pairs only",
            "smoke_limited": smoke_limited,
        },
        monitor_command=monitor_cmd,
        resume_policy="with --resume, existing same hardlinks or same-size files are skipped",
        overwrite_policy="never overwrite existing files; fail closed on incompatible target",
        success_criteria=[
            "all eligible original partitions linked/copied",
            "all expected delta partitions linked/copied",
            "final manifest exists",
            "promotion_authorization remains false",
        ],
    )
    manifest.update({"status": "running", "dry_run": args.dry_run, "merge_mode": args.mode})
    atomic_write_json(run_root / "pre_manifest_merge.json", manifest)
    atomic_write_json(
        run_root / "pid_manifest.json",
        {
            "run_id": run_id,
            "wrapper_pid": os.getpid(),
            "process_name": "python",
            "command_line": " ".join(sys.argv),
            "started_at_utc": utc_now(),
            "current_stage": "starting",
            "expected_alive": True,
        },
    )

    print("run_id", run_id)
    print("mode merge_v0_2_candidate")
    print("output_root", args.output_root)
    print("monitor", monitor_cmd)

    counters: Dict[str, Any] = {
        "original_files_seen": 0,
        "original_files_linked_or_copied": 0,
        "original_files_skipped_expected_delta_pair": 0,
        "delta_files_seen": 0,
        "delta_files_linked_or_copied": 0,
        "delta_files_skipped_unexpected_pair": 0,
        "existing_skipped": 0,
        "planned": 0,
        "errors": 0,
    }
    stage = "link_original"
    latest_source = ""
    latest_target = ""
    started = time.time()
    last_heartbeat = 0.0
    original_limit_hit = False
    delta_limit_hit = False

    def heartbeat(force: bool = False) -> None:
        nonlocal last_heartbeat
        now = time.time()
        if not force and now - last_heartbeat < args.heartbeat_every_sec:
            return
        last_heartbeat = now
        write_heartbeat(
            run_root,
            {
                "run_id": run_id,
                "status": "running",
                "stage": stage,
                "elapsed_seconds": round(now - started, 3),
                "wrapper_pid": os.getpid(),
                "wrapper_alive": True,
                "latest_source": latest_source,
                "latest_target": latest_target,
                "output_root": str(args.output_root),
                "log_path": str(log_path),
                "log_size": log_path.stat().st_size if log_path.exists() else 0,
                "output_free_bytes": disk_free(args.output_root),
                "output_free_human": human_bytes(disk_free(args.output_root)),
                "counters": counters,
            },
        )

    try:
        heartbeat(force=True)
        append_log(log_path, f"{utc_now()} START run_id={run_id} mode={args.mode} dry_run={args.dry_run}")

        for source in iter_partition_files(args.original_root):
            parsed = parse_partition(source)
            if parsed is None:
                continue
            year, ticker, _month = parsed
            counters["original_files_seen"] += 1
            if (year, ticker) in expected_pairs:
                counters["original_files_skipped_expected_delta_pair"] += 1
                continue
            relative = source.relative_to(args.original_root)
            target = args.output_root / relative
            latest_source = str(source)
            latest_target = str(target)
            action = materialize_link_or_copy(source, target, args.mode, args.resume, args.dry_run)
            if action == "planned":
                counters["planned"] += 1
            elif action.startswith("skipped_existing"):
                counters["existing_skipped"] += 1
            else:
                counters["original_files_linked_or_copied"] += 1
            if counters["original_files_seen"] % 10000 == 0:
                append_log(log_path, f"{utc_now()} original_seen={counters['original_files_seen']} linked={counters['original_files_linked_or_copied']}")
            heartbeat()
            if args.max_original_files is not None and counters["original_files_seen"] >= args.max_original_files:
                original_limit_hit = True
                break

        stage = "link_delta"
        heartbeat(force=True)
        for source in iter_partition_files(args.delta_root):
            parsed = parse_partition(source)
            if parsed is None:
                continue
            year, ticker, _month = parsed
            counters["delta_files_seen"] += 1
            if (year, ticker) not in expected_pairs:
                counters["delta_files_skipped_unexpected_pair"] += 1
                continue
            relative = source.relative_to(args.delta_root)
            target = args.output_root / relative
            latest_source = str(source)
            latest_target = str(target)
            action = materialize_link_or_copy(source, target, args.mode, args.resume, args.dry_run)
            if action == "planned":
                counters["planned"] += 1
            elif action.startswith("skipped_existing"):
                counters["existing_skipped"] += 1
            else:
                counters["delta_files_linked_or_copied"] += 1
            if counters["delta_files_seen"] % 5000 == 0:
                append_log(log_path, f"{utc_now()} delta_seen={counters['delta_files_seen']} linked={counters['delta_files_linked_or_copied']}")
            heartbeat()
            if args.max_delta_files is not None and counters["delta_files_seen"] >= args.max_delta_files:
                delta_limit_hit = True
                break

        stage = "finalizing"
        final_status = "dry_run_complete" if args.dry_run else "complete"
        if smoke_limited:
            final_status = "smoke_complete"
        result = {
            "run_id": run_id,
            "status": final_status,
            "finished_at_utc": utc_now(),
            "mode": args.mode,
            "dry_run": args.dry_run,
            "original_root": str(args.original_root),
            "delta_root": str(args.delta_root),
            "output_root": str(args.output_root),
            "expected_failures": str(args.expected_failures),
            "reconciliation_result": str(args.reconciliation_result),
            "expected_delta_ticker_years": len(expected_pairs),
            "counters": counters,
            "original_limit_hit": original_limit_hit,
            "delta_limit_hit": delta_limit_hit,
            "merge_rule": "Expected failed ticker-years use delta; all other partitions use original v0_1.",
            "promotion_authorization": False,
        }
        if not args.dry_run:
            write_text(args.output_root / "README.md", build_readme(result))
            write_text(args.output_root / "latest_run_id.txt", run_id + "\n")
        final_manifest = dict(manifest)
        final_manifest.update({"status": final_status, "finished_at_utc": result["finished_at_utc"], "result": result})
        atomic_write_json(final_manifest_path, final_manifest)
        write_heartbeat(
            run_root,
            {
                "run_id": run_id,
                "status": final_status,
                "stage": "complete",
                "elapsed_seconds": round(time.time() - started, 3),
                "wrapper_pid": os.getpid(),
                "wrapper_alive": False,
                "output_root": str(args.output_root),
                "log_path": str(log_path),
                "log_size": log_path.stat().st_size if log_path.exists() else 0,
                "output_free_bytes": disk_free(args.output_root),
                "output_free_human": human_bytes(disk_free(args.output_root)),
                "final_manifest": str(final_manifest_path),
                "counters": counters,
            },
        )
        append_log(log_path, f"{utc_now()} COMPLETE status={final_status} counters={json.dumps(counters, sort_keys=True)}")
        print(f"final_status={final_status}")
        print(f"final_manifest={final_manifest_path}")
        return 0
    except Exception as exc:
        counters["errors"] += 1
        stage = "failed"
        error_payload = {
            "run_id": run_id,
            "status": "failed",
            "finished_at_utc": utc_now(),
            "error": repr(exc),
            "mode": args.mode,
            "output_root": str(args.output_root),
            "counters": counters,
            "promotion_authorization": False,
        }
        atomic_write_json(final_manifest_path, {**manifest, "status": "failed", "result": error_payload})
        write_heartbeat(
            run_root,
            {
                "run_id": run_id,
                "status": "failed",
                "stage": "failed",
                "elapsed_seconds": round(time.time() - started, 3),
                "wrapper_pid": os.getpid(),
                "wrapper_alive": False,
                "latest_source": latest_source,
                "latest_target": latest_target,
                "error": repr(exc),
                "final_manifest": str(final_manifest_path),
                "counters": counters,
            },
        )
        append_log(log_path, f"{utc_now()} FAILED error={repr(exc)} counters={json.dumps(counters, sort_keys=True)}")
        print(f"failed error={repr(exc)}")
        print(f"final_manifest={final_manifest_path}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
