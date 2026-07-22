from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import pyarrow.parquet as pq
except Exception:  # pragma: no cover - handled at runtime
    pq = None

from qg_full_universe_common import atomic_write_json, base_manifest, ensure_dir, utc_now


DEFAULT_ORIGINAL_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1"
)
DEFAULT_DELTA_ROOT = Path(
    r"C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate"
)
DEFAULT_EXPECTED_FAILURES = Path(
    r"C:/TSIS_Data/00_CTO_APPLIED_ARCHITECTURE/06_TABLES/013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv"
)
DEFAULT_DELTA_LAUNCH_RUN_ROOT = (
    DEFAULT_DELTA_ROOT
    / "_build_runs"
    / "qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z"
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Reconcile original OHLCV 1m quote-guarded v0_1 with failed-ticker delta output."
    )
    p.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    p.add_argument("--delta-root", type=Path, default=DEFAULT_DELTA_ROOT)
    p.add_argument("--expected-failures", type=Path, default=DEFAULT_EXPECTED_FAILURES)
    p.add_argument("--delta-launch-run-root", type=Path, default=DEFAULT_DELTA_LAUNCH_RUN_ROOT)
    p.add_argument("--run-id", default=None)
    p.add_argument("--schema-mode", choices=["none", "sample", "all"], default="all")
    p.add_argument("--sample-limit", type=int, default=25)
    return p


def now_run_id() -> str:
    return "qg_1m_failed_2015_2020_reconciliation_v0_1_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows: List[Dict[str, str]] = []
        for row in reader:
            clean: Dict[str, str] = {}
            for key, value in row.items():
                clean_key = (key or "").strip().strip('"').lstrip("\ufeff")
                clean[clean_key] = (value or "").strip().strip('"')
            rows.append(clean)
        return rows


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_issue_csv(path: Path, issues: Sequence[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    fields = ["severity", "check", "year", "ticker", "month", "path", "message"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for issue in issues:
            writer.writerow({field: issue.get(field, "") for field in fields})


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


def parse_partition_file(path: Path) -> Optional[Tuple[int, str, int]]:
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
            ticker = part.split("=", 1)[1]
        elif part.startswith("month="):
            try:
                month = int(part.split("=", 1)[1])
            except ValueError:
                return None
    if year is None or ticker is None or month is None:
        return None
    return year, ticker, month


def list_partition_files(root: Path) -> List[Path]:
    return sorted(root.glob("year=*/ticker=*/month=*/part-000.parquet"))


def schema_signature(path: Path) -> Optional[Tuple[str, ...]]:
    if pq is None:
        return None
    schema = pq.read_schema(path)
    return tuple(f"{field.name}:{field.type}" for field in schema)


def choose_original_baseline(original_root: Path, issues: List[Dict[str, Any]]) -> Optional[Path]:
    preferred_years = [2021, 2022, 2023, 2024, 2025, 2026, 2014, 2013]
    for year in preferred_years:
        matches = list((original_root / f"year={year}").glob("ticker=*/month=*/part-000.parquet"))
        if matches:
            return sorted(matches)[0]
    add_issue(
        issues,
        severity="ERROR",
        check="schema_baseline",
        message="No original baseline parquet found.",
        path=original_root,
    )
    return None


def expected_pairs(rows: Iterable[Dict[str, str]]) -> List[Tuple[int, str]]:
    pairs: List[Tuple[int, str]] = []
    for row in rows:
        pairs.append((int(row["year"]), row["ticker"].strip().upper()))
    return pairs


def load_year_summary_by_ticker(run_root: Path, year: int, issues: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    path = run_root / f"qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z_year_{year}" / f"year_{year}_materialization_summary.json"
    if not path.exists():
        add_issue(
            issues,
            severity="ERROR",
            check="delta_year_summary",
            year=year,
            path=path,
            message="Missing delta year materialization summary.",
        )
        return {}
    data = read_json(path)
    if data.get("final_status") != "complete":
        add_issue(
            issues,
            severity="ERROR",
            check="delta_year_summary",
            year=year,
            path=path,
            message=f"Expected final_status=complete, observed {data.get('final_status')!r}.",
        )
    if int(data.get("failed_tickers", -1)) != 0:
        add_issue(
            issues,
            severity="ERROR",
            check="delta_year_summary",
            year=year,
            path=path,
            message=f"Expected failed_tickers=0, observed {data.get('failed_tickers')!r}.",
        )
    summaries = data.get("summaries", [])
    by_ticker: Dict[str, Dict[str, Any]] = {}
    for item in summaries:
        ticker = str(item.get("ticker", "")).upper()
        if ticker in by_ticker:
            add_issue(
                issues,
                severity="ERROR",
                check="delta_summary_duplicate",
                year=year,
                ticker=ticker,
                path=path,
                message="Duplicate ticker summary in year materialization summary.",
            )
        by_ticker[ticker] = item
    return by_ticker


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    run_id = args.run_id or now_run_id()
    run_root = args.delta_root / "_reconciliation_runs" / run_id
    ensure_dir(run_root)

    monitor_cmd = "not_applicable: reconciliation is a bounded metadata validation."
    manifest = base_manifest(
        run_id=run_id,
        script_path=Path(__file__),
        command_line=sys.argv,
        mode="reconcile_failed_delta",
        input_roots={
            "original_root": str(args.original_root),
            "delta_root": str(args.delta_root),
            "expected_failures": str(args.expected_failures),
            "delta_launch_run_root": str(args.delta_launch_run_root),
        },
        output_roots={"run_root": str(run_root)},
        expected_scope={"years": "2015-2020", "expected_failed_ticker_years": "from expected_failures csv"},
        monitor_command=monitor_cmd,
        resume_policy="safe to rerun with a new run_id; no data mutation",
        overwrite_policy="writes only into a new _reconciliation_runs/run_id directory",
        success_criteria=[
            "expected failed ticker-years are unique",
            "delta launcher final manifest is complete",
            "every expected ticker-year has a complete delta commit",
            "delta physical output files exist",
            "delta schema is compatible with original baseline",
            "no unexpected delta ticker-years exist",
        ],
    )
    atomic_write_json(run_root / "pre_manifest_reconciliation.json", manifest)

    issues: List[Dict[str, Any]] = []
    counters: Dict[str, Any] = {}

    for required in [args.original_root, args.delta_root, args.expected_failures, args.delta_launch_run_root]:
        if not required.exists():
            add_issue(
                issues,
                severity="ERROR",
                check="required_path",
                path=required,
                message="Required path does not exist.",
            )

    rows = read_csv_rows(args.expected_failures)
    pairs = expected_pairs(rows)
    pair_counts = Counter(pairs)
    duplicate_pairs = [pair for pair, count in pair_counts.items() if count > 1]
    expected_set = set(pairs)
    expected_by_year = Counter(year for year, _ in pairs)
    counters["expected_rows"] = len(rows)
    counters["expected_unique_pairs"] = len(expected_set)
    counters["expected_by_year"] = dict(sorted(expected_by_year.items()))
    if duplicate_pairs:
        for year, ticker in duplicate_pairs:
            add_issue(
                issues,
                severity="ERROR",
                check="expected_duplicates",
                year=year,
                ticker=ticker,
                message="Duplicate expected failed ticker-year in source csv.",
            )

    launch_manifest_path = args.delta_launch_run_root / "launcher_final_manifest.json"
    if launch_manifest_path.exists():
        launch_manifest = read_json(launch_manifest_path)
        counters["launcher_final_status"] = launch_manifest.get("final_status")
        counters["launcher_exit_code"] = launch_manifest.get("exit_code")
        counters["launcher_completed_years"] = launch_manifest.get("completed_years")
        if launch_manifest.get("final_status") != "complete" or int(launch_manifest.get("exit_code", -1)) != 0:
            add_issue(
                issues,
                severity="ERROR",
                check="launcher_final_manifest",
                path=launch_manifest_path,
                message=f"Expected complete/0, observed {launch_manifest.get('final_status')!r}/{launch_manifest.get('exit_code')!r}.",
            )
    else:
        add_issue(
            issues,
            severity="ERROR",
            check="launcher_final_manifest",
            path=launch_manifest_path,
            message="Missing launcher final manifest.",
        )

    year_summaries: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for year in sorted(expected_by_year):
        by_ticker = load_year_summary_by_ticker(args.delta_launch_run_root.parent, year, issues)
        year_summaries[year] = by_ticker
        observed = len(by_ticker)
        expected = expected_by_year[year]
        if observed != expected:
            add_issue(
                issues,
                severity="ERROR",
                check="delta_year_summary_count",
                year=year,
                message=f"Expected {expected} ticker summaries, observed {observed}.",
            )

    actual_files = list_partition_files(args.delta_root)
    actual_pairs = {(year, ticker) for file in actual_files for year, ticker, month in [parse_partition_file(file)] if year is not None}
    counters["delta_partition_files"] = len(actual_files)
    counters["delta_actual_pairs"] = len(actual_pairs)

    unexpected_pairs = sorted(actual_pairs - expected_set)
    missing_pairs = sorted(expected_set - actual_pairs)
    for year, ticker in unexpected_pairs[:1000]:
        add_issue(
            issues,
            severity="ERROR",
            check="unexpected_delta_pair",
            year=year,
            ticker=ticker,
            message="Delta contains a ticker-year not listed in expected failed cases.",
        )
    for year, ticker in missing_pairs:
        add_issue(
            issues,
            severity="ERROR",
            check="missing_delta_pair",
            year=year,
            ticker=ticker,
            message="Expected failed ticker-year has no physical delta parquet files.",
        )

    duplicate_files = []
    month_counter: Counter[Tuple[int, str, int]] = Counter()
    for file in actual_files:
        parsed = parse_partition_file(file)
        if parsed:
            month_counter[parsed] += 1
    for key, count in month_counter.items():
        if count > 1:
            duplicate_files.append((key, count))
    for (year, ticker, month), count in duplicate_files:
        add_issue(
            issues,
            severity="ERROR",
            check="duplicate_delta_month_file",
            year=year,
            ticker=ticker,
            month=month,
            message=f"Expected one part-000.parquet for partition, observed {count}.",
        )

    committed_pairs = 0
    summary_missing = 0
    commit_missing = 0
    output_file_missing = 0
    zero_output_rows = 0
    for year, ticker in sorted(expected_set):
        summary = year_summaries.get(year, {}).get(ticker)
        if summary is None:
            summary_missing += 1
            add_issue(
                issues,
                severity="ERROR",
                check="missing_ticker_summary",
                year=year,
                ticker=ticker,
                message="Expected ticker missing from delta year summary.",
            )
            continue
        if summary.get("status") != "complete":
            add_issue(
                issues,
                severity="ERROR",
                check="ticker_summary_status",
                year=year,
                ticker=ticker,
                message=f"Expected status=complete, observed {summary.get('status')!r}.",
            )
        if summary.get("issues"):
            add_issue(
                issues,
                severity="ERROR",
                check="ticker_summary_issues",
                year=year,
                ticker=ticker,
                message=f"Ticker summary contains issues: {summary.get('issues')!r}.",
            )
        commit = args.delta_launch_run_root.parent / f"qg_1m_failed_2015_2020_delta_v0_1_20260716T000000Z_year_{year}" / "commits" / f"year={year}" / f"{ticker}.json"
        if not commit.exists():
            commit_missing += 1
            add_issue(
                issues,
                severity="ERROR",
                check="missing_delta_commit",
                year=year,
                ticker=ticker,
                path=commit,
                message="Missing delta commit marker for expected ticker-year.",
            )
        else:
            committed_pairs += 1
        for output in summary.get("output_files", []):
            if not Path(output).exists():
                output_file_missing += 1
                add_issue(
                    issues,
                    severity="ERROR",
                    check="missing_output_file",
                    year=year,
                    ticker=ticker,
                    path=output,
                    message="Output file listed in ticker summary does not exist.",
                )
        if int(summary.get("output_rows", 0)) == 0:
            zero_output_rows += 1
            add_issue(
                issues,
                severity="WARN",
                check="zero_output_rows",
                year=year,
                ticker=ticker,
                message="Ticker summary completed with zero output rows.",
            )

    counters["committed_pairs"] = committed_pairs
    counters["summary_missing"] = summary_missing
    counters["commit_missing"] = commit_missing
    counters["output_file_missing"] = output_file_missing
    counters["zero_output_rows"] = zero_output_rows

    schema_checked_files = 0
    schema_mismatches = 0
    schema_missing_original_counterpart = 0
    schema_unavailable = pq is None
    if args.schema_mode != "none":
        if pq is None:
            add_issue(
                issues,
                severity="WARN",
                check="schema_scan",
                message="pyarrow is not available; schema scan skipped.",
            )
        else:
            files_to_check = actual_files
            if args.schema_mode == "sample" and args.sample_limit < len(actual_files):
                if args.sample_limit <= 1:
                    files_to_check = actual_files[:1]
                else:
                    step = (len(actual_files) - 1) / float(args.sample_limit - 1)
                    indexes = sorted({round(i * step) for i in range(args.sample_limit)})
                    files_to_check = [actual_files[i] for i in indexes]
            for file in files_to_check:
                parsed = parse_partition_file(file)
                year, ticker, month = parsed if parsed else ("", "", "")
                try:
                    relative = file.relative_to(args.delta_root)
                except ValueError:
                    relative = None
                original_file = args.original_root / relative if relative is not None else None
                if original_file is None or not original_file.exists():
                    schema_missing_original_counterpart += 1
                    add_issue(
                        issues,
                        severity="WARN",
                        check="schema_original_counterpart_missing",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=file,
                        message="Cannot compare delta schema to equivalent original partition because original file is missing.",
                    )
                    continue
                delta_sig = schema_signature(file)
                original_sig = schema_signature(original_file)
                schema_checked_files += 1
                if delta_sig != original_sig:
                    schema_mismatches += 1
                    add_issue(
                        issues,
                        severity="ERROR",
                        check="schema_mismatch_equivalent_partition",
                        year=year,
                        ticker=ticker,
                        month=month,
                        path=file,
                        message=f"Delta schema differs from equivalent original partition {original_file}.",
                    )
    counters["schema_mode"] = args.schema_mode
    counters["schema_unavailable"] = schema_unavailable
    counters["schema_checked_files"] = schema_checked_files
    counters["schema_mismatches"] = schema_mismatches
    counters["schema_missing_original_counterpart"] = schema_missing_original_counterpart

    errors = [x for x in issues if x.get("severity") == "ERROR"]
    warnings = [x for x in issues if x.get("severity") == "WARN"]
    final_status = "PASS" if not errors else "FAIL"

    result = {
        "run_id": run_id,
        "status": final_status,
        "created_at_utc": manifest["created_at_utc"],
        "finished_at_utc": utc_now(),
        "original_root": str(args.original_root),
        "delta_root": str(args.delta_root),
        "expected_failures": str(args.expected_failures),
        "delta_launch_run_root": str(args.delta_launch_run_root),
        "counters": counters,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issue_csv": str(run_root / "reconciliation_issues.csv"),
        "merge_authorization": final_status == "PASS",
        "merge_rule": "For expected failed ticker-years, delta supersedes original v0_1. All other original v0_1 partitions remain source for candidate merge.",
        "promotion_authorization": False,
        "promotion_note": "Reconciliation PASS authorizes preparing a technical merge candidate only; it does not promote the dataset.",
    }

    atomic_write_json(run_root / "reconciliation_result.json", result)
    write_issue_csv(run_root / "reconciliation_issues.csv", issues)
    final_manifest = dict(manifest)
    final_manifest.update({"status": final_status, "finished_at_utc": result["finished_at_utc"], "result": result})
    atomic_write_json(run_root / "final_manifest_reconciliation.json", final_manifest)

    print(f"run_id={run_id}")
    print(f"status={final_status}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    print(f"expected_unique_pairs={counters['expected_unique_pairs']}")
    print(f"committed_pairs={committed_pairs}")
    print(f"schema_checked_files={schema_checked_files} schema_mismatches={schema_mismatches}")
    print(f"result={run_root / 'reconciliation_result.json'}")
    print(f"issues={run_root / 'reconciliation_issues.csv'}")
    return 0 if final_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())




