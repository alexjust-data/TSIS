#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def blocker_codes(values: pd.Series) -> list[str]:
    result: set[str] = set()
    for value in values.dropna():
        parsed = json.loads(str(value))
        result.update(str(item) for item in parsed)
    return sorted(result)


def outcome(float_nonnull: int, sessions: int) -> str:
    if float_nonnull == sessions:
        return "CALCULATED_ALL_SESSIONS"
    if float_nonnull > 0:
        return "CALCULATED_PARTIAL_SESSIONS"
    return "BLOCKED_ALL_SESSIONS"


def aggregate(frame: pd.DataFrame, key: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value, scoped in frame.groupby(key, dropna=False):
        eligible = scoped[scoped["probe_gate"].eq("ELIGIBLE")]
        rows.append({
            key: None if pd.isna(value) else value,
            "case_count": len(scoped),
            "eligible_case_count": len(eligible),
            "halt_case_count": int(scoped["probe_gate"].ne("ELIGIBLE").sum()),
            "os_full_case_count": int(eligible["os_nonnull_rows"].eq(eligible["session_rows"]).sum()),
            "float_full_case_count": int(eligible["float_nonnull_rows"].eq(eligible["session_rows"]).sum()),
            "float_partial_case_count": int(((eligible["float_nonnull_rows"] > 0) & (eligible["float_nonnull_rows"] < eligible["session_rows"])).sum()),
            "float_any_case_count": int(eligible["float_nonnull_rows"].gt(0).sum()),
            "float_full_case_rate": (float(eligible["float_nonnull_rows"].eq(eligible["session_rows"]).mean()) if len(eligible) else None),
            "float_any_case_rate": (float(eligible["float_nonnull_rows"].gt(0).mean()) if len(eligible) else None),
        })
    return rows


def execute(
    *,
    case_matrix_path: Path,
    run_root: Path,
    os_run_template: str,
    owner_run_template: str,
    certification_path: Path,
    result_audit_path: Path,
    output: Path,
) -> Path:
    cases = json.loads(case_matrix_path.read_text(encoding="utf-8"))
    certification = json.loads(certification_path.read_text(encoding="utf-8"))
    result_audit = json.loads(result_audit_path.read_text(encoding="utf-8"))
    if certification.get("status") != "SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING":
        raise ValueError("shard certification is not PASS")
    if result_audit.get("status") != "PASS" or result_audit.get("case_count") != 99:
        raise ValueError("owner result audit is not 99-case PASS")

    rows: list[dict[str, Any]] = []
    blocker_case_counter: Counter[str] = Counter()
    blocker_session_counter: Counter[str] = Counter()
    for case in cases:
        ticker = str(case["ticker"])
        base = {
            "ticker": ticker,
            "instrument_id": case["instrument_id"],
            "temporal_cohort": case.get("temporal_cohort"),
            "stratum": case.get("stratum"),
            "strata_json": json.dumps(case.get("strata") or [], sort_keys=True),
            "shard": int(case["shard"]),
            "probe_gate": case["probe_gate"],
        }
        if case["probe_gate"] != "ELIGIBLE":
            rows.append({
                **base,
                "session_rows": 0,
                "os_nonnull_rows": 0,
                "float_nonnull_rows": 0,
                "outcome": case["probe_gate"],
                "blocker_codes_json": json.dumps([case["probe_gate"]]),
            })
            blocker_case_counter[case["probe_gate"]] += 1
            continue
        os_root = run_root / "runs" / os_run_template.format(ticker_lower=ticker.lower(), ticker=ticker)
        owner_root = run_root / "runs" / owner_run_template.format(ticker_lower=ticker.lower(), ticker=ticker)
        daily_os = pd.read_parquet(os_root / "daily_os_state.parquet")
        daily_float = pd.read_parquet(owner_root / "daily_float_state.parquet")
        codes = blocker_codes(daily_float["blocker_codes_json"])
        for code in codes:
            blocker_case_counter[code] += 1
        for value in daily_float["blocker_codes_json"].dropna():
            for code in set(json.loads(str(value))):
                blocker_session_counter[str(code)] += 1
        float_nonnull = int(daily_float["float_owner_exclusion_estimate_as_known"].notna().sum())
        rows.append({
            **base,
            "session_rows": len(daily_float),
            "os_nonnull_rows": int(daily_os["shares_outstanding_estimate_as_known"].notna().sum()),
            "float_nonnull_rows": float_nonnull,
            "outcome": outcome(float_nonnull, len(daily_float)),
            "blocker_codes_json": json.dumps(codes),
        })

    frame = pd.DataFrame(rows).sort_values("ticker").reset_index(drop=True)
    eligible = frame[frame["probe_gate"].eq("ELIGIBLE")]
    strata_rows: list[dict[str, Any]] = []
    strata_names = sorted({name for raw in frame["strata_json"] for name in json.loads(raw)})
    for name in strata_names:
        scoped = frame[frame["strata_json"].map(lambda raw: name in json.loads(raw))]
        eligible_scoped = scoped[scoped["probe_gate"].eq("ELIGIBLE")]
        strata_rows.append({
            "stratum": name,
            "case_count": len(scoped),
            "eligible_case_count": len(eligible_scoped),
            "float_full_case_count": int(eligible_scoped["float_nonnull_rows"].eq(eligible_scoped["session_rows"]).sum()),
            "float_any_case_count": int(eligible_scoped["float_nonnull_rows"].gt(0).sum()),
            "float_any_case_rate": float(eligible_scoped["float_nonnull_rows"].gt(0).mean()) if len(eligible_scoped) else None,
        })

    output.mkdir(parents=True, exist_ok=False)
    frame.to_parquet(output / "case_coverage.parquet", index=False)
    pd.DataFrame(aggregate(frame, "temporal_cohort")).to_parquet(output / "coverage_by_temporal_cohort.parquet", index=False)
    pd.DataFrame(aggregate(frame, "shard")).to_parquet(output / "coverage_by_shard.parquet", index=False)
    pd.DataFrame(strata_rows).to_parquet(output / "coverage_by_strata_membership.parquet", index=False)
    blocker_rows = [
        {"blocker_code": code, "case_count": count, "blocked_session_count": blocker_session_counter.get(code, 0)}
        for code, count in blocker_case_counter.most_common()
    ]
    pd.DataFrame(blocker_rows).to_parquet(output / "blocker_distribution.parquet", index=False)
    summary = {
        "status": "COMPLETE_SYSTEM_AUDIT_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "total_sample_cases": len(frame),
        "eligible_cases": len(eligible),
        "security_class_halts": int(frame["probe_gate"].ne("ELIGIBLE").sum()),
        "os_full_cases": int(eligible["os_nonnull_rows"].eq(eligible["session_rows"]).sum()),
        "os_any_cases": int(eligible["os_nonnull_rows"].gt(0).sum()),
        "float_full_cases": int(eligible["float_nonnull_rows"].eq(eligible["session_rows"]).sum()),
        "float_partial_cases": int(((eligible["float_nonnull_rows"] > 0) & (eligible["float_nonnull_rows"] < eligible["session_rows"])).sum()),
        "float_any_cases": int(eligible["float_nonnull_rows"].gt(0).sum()),
        "float_full_case_rate": float(eligible["float_nonnull_rows"].eq(eligible["session_rows"]).mean()),
        "float_any_case_rate": float(eligible["float_nonnull_rows"].gt(0).mean()),
        "eligible_session_rows": int(eligible["session_rows"].sum()),
        "os_nonnull_session_rows": int(eligible["os_nonnull_rows"].sum()),
        "float_nonnull_session_rows": int(eligible["float_nonnull_rows"].sum()),
        "top_blockers": blocker_rows,
        "certification_status": certification["status"],
        "owner_result_audit_status": result_audit["status"],
        "scale_authorization": "NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-matrix", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--os-run-template", required=True)
    parser.add_argument("--owner-run-template", required=True)
    parser.add_argument("--certification", type=Path, required=True)
    parser.add_argument("--result-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(
        case_matrix_path=args.case_matrix,
        run_root=args.run_root,
        os_run_template=args.os_run_template,
        owner_run_template=args.owner_run_template,
        certification_path=args.certification,
        result_audit_path=args.result_audit,
        output=args.output,
    ))
