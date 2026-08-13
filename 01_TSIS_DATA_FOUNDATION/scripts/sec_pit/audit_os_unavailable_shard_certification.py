#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shard_for(instrument_id: str, count: int = 4) -> int:
    return int(hashlib.sha256(instrument_id.encode()).hexdigest(), 16) % count


def audit_case(run_root: Path, case: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = json.loads((run_root / "final_manifest.json").read_text(encoding="utf-8"))
    daily = pd.read_parquet(run_root / "daily_os_state.parquet")
    observations = pd.read_parquet(run_root / "os_source_observations.parquet")
    admissions = pd.read_parquet(run_root / "accession_instrument_admission.parquet")
    unique = not daily.duplicated(["instrument_id", "session_date"]).any()
    causal = (
        daily["anchor_eligible_from_session"].notna()
        & (daily["anchor_eligible_from_session"].astype(str) <= daily["session_date"].astype(str))
    ).all()
    nonnull = daily["shares_outstanding_estimate_as_known"].notna().all()
    positive = (daily["shares_outstanding_estimate_as_known"] > 0).all()
    no_blockers = daily["blocker_codes_json"].eq("[]").all()
    source_readable = bool(
        len(observations)
        and observations["value"].notna().all()
        and (observations["value"] > 0).all()
        and observations["measurement_at"].notna().all()
        and observations["eligible_from_session"].notna().all()
        and observations["source_excerpt"].fillna("").str.len().gt(0).all()
    )
    class_stable = bool(
        len(admissions)
        and admissions["admission_decision"].eq(
            "ADMITTED_TARGET_INSTRUMENT_CLASS"
        ).all()
        and admissions["resolved_target_class_label"].notna().all()
    )
    manifest_pass = bool(
        manifest["status"] == "COMPLETE"
        and manifest["network_requests"] == 0
        and manifest["counts"]["daily_nonnull_rows"] == manifest["counts"]["daily_rows"]
        and not manifest["counts"]["blocker_codes"]
    )
    checks = {
        "ticker": case["ticker"],
        "shard": shard_for(str(case["instrument_id"])),
        "daily_rows": len(daily),
        "source_observations": len(observations),
        "grain_unique_pass": bool(unique),
        "causality_pass": bool(causal),
        "nonnull_pass": bool(nonnull),
        "positive_value_pass": bool(positive),
        "explicit_no_blockers_pass": bool(no_blockers),
        "source_readable_pass": source_readable,
        "class_admission_stable_pass": class_stable,
        "manifest_pass": manifest_pass,
    }
    checks["all_checks_pass"] = all(
        value for key, value in checks.items() if key.endswith("_pass")
    )
    sample = daily.iloc[0]
    readable = {
        "ticker": case["ticker"],
        "shard": checks["shard"],
        "session_date": sample["session_date"],
        "shares_outstanding_estimate_as_known": sample[
            "shares_outstanding_estimate_as_known"
        ],
        "anchor_measurement_at": sample["anchor_measurement_at"],
        "anchor_eligible_from_session": sample["anchor_eligible_from_session"],
        "os_state": sample["os_state"],
    }
    checks["daily_schema"] = tuple(daily.columns)
    checks["component_hashes"] = json.dumps(
        manifest["component_hashes"], sort_keys=True
    )
    return checks, readable


def execute(args: argparse.Namespace) -> Path:
    cases = json.loads(args.case_matrix.read_text(encoding="utf-8"))
    selected = {ticker.upper() for ticker in args.ticker}
    cases = [case for case in cases if str(case["ticker"]).upper() in selected]
    if {str(case["ticker"]).upper() for case in cases} != selected:
        raise ValueError("selected ticker absent from case matrix")
    args.output.mkdir(parents=True, exist_ok=False)
    rows, samples = [], []
    for case in cases:
        ticker = str(case["ticker"])
        run_root = args.run_root / "runs" / args.run_template.format(
            ticker=ticker, ticker_lower=ticker.lower()
        )
        checks, sample = audit_case(run_root, case)
        rows.append(checks)
        samples.append(sample)
    schemas = {row.pop("daily_schema") for row in rows}
    hashes = {row.pop("component_hashes") for row in rows}
    shards = {int(row["shard"]) for row in rows if row["all_checks_pass"]}
    frame = pd.DataFrame(rows).sort_values("shard")
    frame.to_parquet(args.output / "case_os_certification.parquet", index=False)
    pd.DataFrame(samples).sort_values("shard").to_parquet(
        args.output / "readable_value_samples.parquet", index=False
    )
    status = "SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING" if (
        frame["all_checks_pass"].all()
        and shards == {0, 1, 2, 3}
        and len(schemas) == 1
        and len(hashes) == 1
    ) else "FAIL"
    result = {
        "status": status,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": "sec_pit_os_unavailable_variable_by_shard_certification_v0_1",
        "selected_tickers": frame["ticker"].tolist(),
        "covered_shards": sorted(shards),
        "daily_schema_equivalent_across_cases": len(schemas) == 1,
        "component_hashes_equivalent_across_cases": len(hashes) == 1,
        "network_requests": 0,
        "case_matrix_path": args.case_matrix.as_posix(),
        "case_matrix_sha256": sha256_file(args.case_matrix),
        "scale_authorization": "NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE",
    }
    (args.output / "certification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result["outputs"] = {
        path.name: sha256_file(path) for path in (
            args.output / "case_os_certification.parquet",
            args.output / "readable_value_samples.parquet",
            args.output / "certification.json",
        )
    }
    (args.output / "final_manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return args.output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-matrix", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-template", required=True)
    parser.add_argument("--ticker", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    print(execute(parse_args()))
