from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover
    pq = None

from qg_full_universe_common import atomic_write_json, base_manifest, ensure_dir, human_bytes, utc_now, write_heartbeat


DEFAULT_CANDIDATE_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate"
)
DEFAULT_ORIGINAL_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1"
)
DEFAULT_DELTA_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate"
)
DEFAULT_EXPECTED_FAILURES = Path(
    r"C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/06_TABLES/013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv"
)
DEFAULT_MERGE_MANIFEST = (
    DEFAULT_CANDIDATE_ROOT
    / "_build_runs"
    / "qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z"
    / "final_manifest_merge.json"
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate OHLCV 1m quote-guarded v0_2 candidate merge tree.")
    p.add_argument("--candidate-root", type=Path, default=DEFAULT_CANDIDATE_ROOT)
    p.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    p.add_argument("--delta-root", type=Path, default=DEFAULT_DELTA_ROOT)
    p.add_argument("--expected-failures", type=Path, default=DEFAULT_EXPECTED_FAILURES)
    p.add_argument("--merge-manifest", type=Path, default=DEFAULT_MERGE_MANIFEST)
    p.add_argument("--run-id", default=None)
    p.add_argument("--schema-sample-limit", type=int, default=600)
    p.add_argument("--max-files", type=int, default=None, help="Smoke-only file limit.")
    p.add_argument("--heartbeat-every-sec", type=float, default=30.0)
    return p


def make_run_id() -> str:
    return "qg_1m_full_universe_v0_2_candidate_validation_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_expected_pairs(path: Path) -> Set[Tuple[int, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        pairs: Set[Tuple[int, str]] = set()
        for row in reader:
            clean = {(k or "").strip().strip('"').lstrip("\ufeff"): (v or "").strip().strip('"') for k, v in row.items()}
            pairs.add((int(clean["year"]), clean["ticker"].upper()))
    return pairs


def parse_partition(path: Path) -> Optional[Tuple[int, str, int]]:
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
    if year is None or ticker is None or month is None:
        return None
    return year, ticker, month


def same_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def schema_signature(path: Path) -> Optional[Tuple[str, ...]]:
    if pq is None:
        return None
    schema = pq.read_schema(path)
    return tuple(f"{field.name}:{field.type}" for field in schema)


def add_issue(
    issues: List[Dict[str, Any]],
    *,
    severity: str,
    check: str,
    message: str,
    year: Any = "",
    ticker: str = "",
    month: Any = "",
    path: Any = "",
) -> None:
    issues.append(
        {
            "severity": severity,
            "check": check,
            "year": year,
            "ticker": ticker,
            "month": month,
            "path": str(path) if path else "",
            "message": message,
        }
    )


def write_issue_csv(path: Path, issues: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    fields = ["severity", "check", "year", "ticker", "month", "path", "message"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for issue in issues:
            writer.writerow({field: issue.get(field, "") for field in fields})


def disk_free(path: Path) -> Optional[int]:
    import shutil

    try:
        probe = path if path.exists() else path.parent
        return int(shutil.disk_usage(probe).free)
    except OSError:
        return None


def append_log(path: Path, line: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line.rstrip() + "\n")


def reservoir_add(sample: List[Path], item: Path, seen: int, limit: int, rng: random.Random) -> None:
    if limit <= 0:
        return
    if len(sample) < limit:
        sample.append(item)
        return
    idx = rng.randint(1, seen)
    if idx <= limit:
        sample[idx - 1] = item


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or make_run_id()
    run_root = args.candidate_root / "_validation_runs" / run_id
    log_path = run_root / "validation.log"
    final_manifest_path = run_root / "final_manifest_validation.json"
    issues_csv = run_root / "validation_issues.csv"
    ensure_dir(run_root)

    monitor_cmd = (
        f'python "{Path(__file__).with_name("monitor_ohlcv_1m_qg_validation_v0_1.py")}" '
        f'--run-root "{run_root}" --watch --interval-sec 30 --compact'
    )

    expected_pairs = read_expected_pairs(args.expected_failures)
    merge_manifest = read_json(args.merge_manifest)
    merge_result = merge_manifest.get("result", {})
    merge_counters = merge_result.get("counters", {})

    manifest = base_manifest(
        run_id=run_id,
        script_path=Path(__file__),
        command_line=sys.argv,
        mode="validate_v0_2_candidate",
        input_roots={
            "candidate_root": str(args.candidate_root),
            "original_root": str(args.original_root),
            "delta_root": str(args.delta_root),
            "expected_failures": str(args.expected_failures),
            "merge_manifest": str(args.merge_manifest),
        },
        output_roots={"run_root": str(run_root)},
        expected_scope={
            "years": "2005-2026",
            "expected_delta_ticker_years": len(expected_pairs),
            "max_files": args.max_files,
            "schema_sample_limit": args.schema_sample_limit,
        },
        monitor_command=monitor_cmd,
        resume_policy="validation is read-only; rerun with a new run_id",
        overwrite_policy="writes only validation run artifacts",
        success_criteria=[
            "candidate merge manifest is complete",
            "candidate files point to the expected source root",
            "all 3,918 expected failed ticker-years are present from delta",
            "non-failed partitions are sourced from original v0_1",
            "sample schemas match their source partitions",
        ],
    )
    manifest.update({"status": "running"})
    atomic_write_json(run_root / "pre_manifest_validation.json", manifest)
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
    print("mode validate_v0_2_candidate")
    print("candidate_root", args.candidate_root)
    print("monitor", monitor_cmd)

    started = time.time()
    last_heartbeat = 0.0
    stage = "scan_candidate"
    latest_file = ""
    issues: List[Dict[str, Any]] = []
    rng = random.Random(20260716)
    source_sample_limit = max(1, args.schema_sample_limit // 2)
    original_schema_sample: List[Path] = []
    delta_schema_sample: List[Path] = []
    original_sample_seen = 0
    delta_sample_seen = 0

    counters: Dict[str, Any] = {
        "candidate_files_seen": 0,
        "candidate_files_from_original": 0,
        "candidate_files_from_delta": 0,
        "candidate_files_bad_source": 0,
        "source_missing": 0,
        "expected_delta_pairs_observed": 0,
        "errors": 0,
    }
    years = Counter()
    expected_delta_pairs_observed: Set[Tuple[int, str]] = set()

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
                "latest_file": latest_file,
                "log_path": str(log_path),
                "log_size": log_path.stat().st_size if log_path.exists() else 0,
                "candidate_root": str(args.candidate_root),
                "output_free_bytes": disk_free(args.candidate_root),
                "output_free_human": human_bytes(disk_free(args.candidate_root)),
                "counters": counters,
            },
        )

    try:
        heartbeat(force=True)
        append_log(log_path, f"{utc_now()} START run_id={run_id}")

        if merge_manifest.get("status") != "complete" or merge_result.get("status") != "complete":
            add_issue(
                issues,
                severity="ERROR",
                check="merge_manifest_status",
                path=args.merge_manifest,
                message=f"Merge manifest is not complete: status={merge_manifest.get('status')!r} result_status={merge_result.get('status')!r}",
            )
        if merge_result.get("promotion_authorization") is not False:
            add_issue(
                issues,
                severity="ERROR",
                check="promotion_boundary",
                path=args.merge_manifest,
                message="Merge manifest must not authorize promotion.",
            )

        for file in args.candidate_root.glob("year=*/ticker=*/month=*/part-000.parquet"):
            latest_file = str(file)
            parsed = parse_partition(file)
            counters["candidate_files_seen"] += 1
            if parsed is None:
                add_issue(issues, severity="ERROR", check="partition_parse", path=file, message="Cannot parse partition.")
                counters["candidate_files_bad_source"] += 1
                continue
            year, ticker, month = parsed
            years[year] += 1
            pair = (year, ticker)
            relative = file.relative_to(args.candidate_root)
            if pair in expected_pairs:
                expected_delta_pairs_observed.add(pair)
                source = args.delta_root / relative
                if not source.exists():
                    counters["source_missing"] += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="delta_source_missing",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=source,
                        message="Candidate partition should come from delta but source file is missing.",
                    )
                elif same_file(file, source):
                    counters["candidate_files_from_delta"] += 1
                    delta_sample_seen += 1
                    reservoir_add(delta_schema_sample, file, delta_sample_seen, source_sample_limit, rng)
                else:
                    counters["candidate_files_bad_source"] += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="delta_hardlink_mismatch",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=file,
                        message=f"Expected candidate partition to be hardlinked to delta source {source}.",
                    )
            else:
                source = args.original_root / relative
                if not source.exists():
                    counters["source_missing"] += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="original_source_missing",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=source,
                        message="Candidate partition should come from original but source file is missing.",
                    )
                elif same_file(file, source):
                    counters["candidate_files_from_original"] += 1
                    original_sample_seen += 1
                    reservoir_add(original_schema_sample, file, original_sample_seen, source_sample_limit, rng)
                else:
                    counters["candidate_files_bad_source"] += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="original_hardlink_mismatch",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=file,
                        message=f"Expected candidate partition to be hardlinked to original source {source}.",
                    )
            counters["expected_delta_pairs_observed"] = len(expected_delta_pairs_observed)
            if counters["candidate_files_seen"] % 50000 == 0:
                append_log(
                    log_path,
                    f"{utc_now()} files_seen={counters['candidate_files_seen']} original={counters['candidate_files_from_original']} delta={counters['candidate_files_from_delta']} errors={len([x for x in issues if x['severity'] == 'ERROR'])}",
                )
            heartbeat()
            if args.max_files is not None and counters["candidate_files_seen"] >= args.max_files:
                break

        if args.max_files is None:
            expected_years = set(range(2005, 2027))
            observed_years = set(years)
            if observed_years != expected_years:
                add_issue(
                    issues,
                    severity="ERROR",
                    check="years_present",
                    message=f"Expected years 2005..2026, observed {sorted(observed_years)}.",
                )
            missing_pairs = sorted(expected_pairs - expected_delta_pairs_observed)
            for year, ticker in missing_pairs:
                add_issue(
                    issues,
                    severity="ERROR",
                    check="expected_delta_pair_missing",
                    year=year,
                    ticker=ticker,
                    message="Expected delta ticker-year not observed in candidate tree.",
                )
            expected_total = int(merge_counters.get("original_files_linked_or_copied", -1)) + int(
                merge_counters.get("delta_files_linked_or_copied", -1)
            )
            if expected_total >= 0 and counters["candidate_files_seen"] != expected_total:
                add_issue(
                    issues,
                    severity="ERROR",
                    check="candidate_file_count",
                    message=f"Expected {expected_total} parquet files from merge manifest, observed {counters['candidate_files_seen']}.",
                )
            if counters["candidate_files_from_original"] != int(merge_counters.get("original_files_linked_or_copied", -1)):
                add_issue(
                    issues,
                    severity="ERROR",
                    check="original_source_count",
                    message="Candidate original-source file count does not match merge manifest.",
                )
            if counters["candidate_files_from_delta"] != int(merge_counters.get("delta_files_linked_or_copied", -1)):
                add_issue(
                    issues,
                    severity="ERROR",
                    check="delta_source_count",
                    message="Candidate delta-source file count does not match merge manifest.",
                )

        stage = "schema_sample"
        heartbeat(force=True)
        schema_checked = 0
        schema_mismatches = 0
        schema_unavailable = pq is None
        if schema_unavailable:
            add_issue(issues, severity="WARN", check="schema_sample", message="pyarrow is unavailable; schema sample skipped.")
        else:
            for file in original_schema_sample + delta_schema_sample:
                parsed = parse_partition(file)
                if parsed is None:
                    continue
                year, ticker, _month = parsed
                source_root = args.delta_root if (year, ticker) in expected_pairs else args.original_root
                source = source_root / file.relative_to(args.candidate_root)
                schema_checked += 1
                if schema_signature(file) != schema_signature(source):
                    schema_mismatches += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="schema_mismatch",
                        year=year,
                        ticker=ticker,
                        path=file,
                        message=f"Candidate schema differs from source {source}.",
                    )
        counters["schema_checked"] = schema_checked
        counters["schema_mismatches"] = schema_mismatches
        counters["schema_unavailable"] = schema_unavailable

        errors = [x for x in issues if x["severity"] == "ERROR"]
        warnings = [x for x in issues if x["severity"] == "WARN"]
        final_status = "PASS" if not errors and args.max_files is None else ("SMOKE_PASS" if not errors else "FAIL")
        result = {
            "run_id": run_id,
            "status": final_status,
            "finished_at_utc": utc_now(),
            "candidate_root": str(args.candidate_root),
            "original_root": str(args.original_root),
            "delta_root": str(args.delta_root),
            "expected_failures": str(args.expected_failures),
            "merge_manifest": str(args.merge_manifest),
            "counters": counters,
            "years": dict(sorted(years.items())),
            "error_count": len(errors),
            "warning_count": len(warnings),
            "issues_csv": str(issues_csv),
            "promotion_authorization": False,
            "promotion_note": "Validation PASS makes the candidate eligible for promotion review only; it does not promote the dataset.",
        }
        write_issue_csv(issues_csv, issues)
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
                "candidate_root": str(args.candidate_root),
                "log_path": str(log_path),
                "log_size": log_path.stat().st_size if log_path.exists() else 0,
                "final_manifest": str(final_manifest_path),
                "counters": counters,
            },
        )
        append_log(log_path, f"{utc_now()} COMPLETE status={final_status} counters={json.dumps(counters, sort_keys=True)}")
        print(f"status={final_status}")
        print(f"errors={len(errors)} warnings={len(warnings)}")
        print(f"candidate_files_seen={counters['candidate_files_seen']}")
        print(f"candidate_files_from_original={counters['candidate_files_from_original']}")
        print(f"candidate_files_from_delta={counters['candidate_files_from_delta']}")
        print(f"schema_checked={schema_checked} schema_mismatches={schema_mismatches}")
        print(f"final_manifest={final_manifest_path}")
        return 0 if not errors else 2
    except Exception as exc:
        counters["errors"] += 1
        add_issue(issues, severity="ERROR", check="exception", message=repr(exc), path=latest_file)
        write_issue_csv(issues_csv, issues)
        result = {
            "run_id": run_id,
            "status": "FAIL",
            "finished_at_utc": utc_now(),
            "error": repr(exc),
            "candidate_root": str(args.candidate_root),
            "counters": counters,
            "issues_csv": str(issues_csv),
            "promotion_authorization": False,
        }
        final_manifest = dict(manifest)
        final_manifest.update({"status": "FAIL", "finished_at_utc": result["finished_at_utc"], "result": result})
        atomic_write_json(final_manifest_path, final_manifest)
        write_heartbeat(
            run_root,
            {
                "run_id": run_id,
                "status": "FAIL",
                "stage": "failed",
                "elapsed_seconds": round(time.time() - started, 3),
                "wrapper_pid": os.getpid(),
                "wrapper_alive": False,
                "latest_file": latest_file,
                "error": repr(exc),
                "final_manifest": str(final_manifest_path),
                "counters": counters,
            },
        )
        append_log(log_path, f"{utc_now()} FAILED error={repr(exc)} counters={json.dumps(counters, sort_keys=True)}")
        print(f"status=FAIL error={repr(exc)}")
        print(f"final_manifest={final_manifest_path}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
