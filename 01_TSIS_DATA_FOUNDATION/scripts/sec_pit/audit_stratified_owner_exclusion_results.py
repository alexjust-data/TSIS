#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_run(run_root: Path) -> dict[str, Any]:
    manifest = json.loads((run_root / "final_manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((run_root / "variable_audit.json").read_text(encoding="utf-8"))
    daily = pd.read_parquet(run_root / "daily_float_state.parquet")
    output_hashes_valid = all(
        sha256_file(run_root / name) == expected["sha256"]
        for name, expected in manifest["output_files"].items()
    )
    sessions = daily["session_date"].astype(str)
    unique_grain = not daily.duplicated(["instrument_id", "session_date"]).any()
    ordered_sessions = sessions.tolist() == sorted(sessions.tolist())
    baseline_pit = all(
        not eligible or str(eligible) <= str(session)
        for eligible, session in zip(
            daily["ownership_baseline_eligible_from_session"], sessions, strict=True
        )
    )
    calculated = daily["estimation_state"].astype(str).str.startswith("CALCULATED")
    blocked = ~calculated
    calculated_values_valid = bool(
        (
            daily.loc[calculated, "float_owner_exclusion_estimate_as_known"].notna()
            & daily.loc[calculated, "unique_supported_excluded_shares"].notna()
            & daily.loc[calculated, "float_percent_estimate_as_known"].between(0, 100)
            & (
                daily.loc[calculated, "float_owner_exclusion_estimate_as_known"]
                == daily.loc[calculated, "shares_outstanding_estimate_as_known"]
                - daily.loc[calculated, "unique_supported_excluded_shares"]
            )
        ).all()
    )
    blocked_values_valid = bool(
        (
            daily.loc[blocked, "float_owner_exclusion_estimate_as_known"].isna()
            & daily.loc[blocked, "blocker_codes_json"].ne("[]")
        ).all()
    )
    checks = {
        "network_requests_zero": manifest["network_requests"] == 0,
        "output_hashes_valid": output_hashes_valid,
        "daily_rows_five": len(daily) == 5,
        "unique_instrument_session_grain": unique_grain,
        "sessions_ordered": ordered_sessions,
        "baseline_eligible_no_later_than_session": baseline_pit,
        "calculated_values_valid": calculated_values_valid,
        "blocked_rows_null_with_explicit_blocker": blocked_values_valid,
    }
    return {
        "ticker": manifest["ticker"],
        "run_id": manifest["run_id"],
        "schema_columns": daily.columns.tolist(),
        "schema_version_values": sorted(daily["schema_version"].dropna().unique().tolist()),
        "component_hashes": manifest["component_hashes"],
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "gates": {
            key: audit[key]
            for key in (
                "S5_OS_MANUAL_GATE",
                "S6_NEUTRAL_OWNERSHIP_EXTRACTION",
                "S7_HOLDER_AND_CLASS_RECONCILIATION",
                "S8_OWNER_EXCLUSION_FLOAT",
                "S9_FLOAT_CHANGE_AUDIT",
            )
        },
        "daily_nonnull_float_rows": int(
            daily["float_owner_exclusion_estimate_as_known"].notna().sum()
        ),
    }


def audit_matrix(run_roots: list[Path]) -> dict[str, Any]:
    cases = [audit_run(path) for path in run_roots]
    schema_equivalent = len({tuple(case["schema_columns"]) for case in cases}) == 1
    schema_version_equivalent = (
        len({tuple(case["schema_version_values"]) for case in cases}) == 1
    )
    component_hashes_equivalent = (
        len({json.dumps(case["component_hashes"], sort_keys=True) for case in cases}) == 1
    )
    matrix_checks = {
        "all_case_audits_pass": all(case["status"] == "PASS" for case in cases),
        "schema_columns_equivalent": schema_equivalent,
        "schema_versions_equivalent": schema_version_equivalent,
        "component_hashes_equivalent": component_hashes_equivalent,
    }
    return {
        "policy_id": "sec_pit_stratified_owner_exclusion_certification_v0_1",
        "case_count": len(cases),
        "matrix_checks": matrix_checks,
        "status": "PASS" if all(matrix_checks.values()) else "FAIL",
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = audit_matrix([Path(value) for value in args.run_root])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
