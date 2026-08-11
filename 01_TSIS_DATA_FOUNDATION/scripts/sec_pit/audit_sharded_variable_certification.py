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


def shard_for(instrument_id: str, count: int) -> int:
    return int(hashlib.sha256(instrument_id.encode()).hexdigest(), 16) % count


def audit_daily_frames(
    daily_os: pd.DataFrame,
    daily_float: pd.DataFrame,
) -> dict[str, Any]:
    os_unique = not daily_os.duplicated(["instrument_id", "session_date"]).any()
    float_unique = not daily_float.duplicated(
        ["instrument_id", "session_date"]
    ).any()
    os_causal = (
        daily_os["anchor_eligible_from_session"].isna()
        | (
            daily_os["anchor_eligible_from_session"].astype(str)
            <= daily_os["session_date"].astype(str)
        )
    ).all()
    baseline_causal = (
        daily_float["ownership_baseline_eligible_from_session"].isna()
        | (
            daily_float["ownership_baseline_eligible_from_session"].astype(str)
            <= daily_float["session_date"].astype(str)
        )
    ).all()
    calculated = daily_float[
        daily_float["float_owner_exclusion_estimate_as_known"].notna()
    ]
    formula = (
        (
            calculated["shares_outstanding_estimate_as_known"]
            - calculated["unique_supported_excluded_shares"]
            - calculated["float_owner_exclusion_estimate_as_known"]
        ).abs()
        <= 1e-8
    ).all()
    fraction = (
        (
            calculated["float_fraction_estimate_as_known"]
            - calculated["float_owner_exclusion_estimate_as_known"]
            / calculated["shares_outstanding_estimate_as_known"]
        ).abs()
        <= 1e-10
    ).all()
    percent = (
        (
            calculated["float_percent_estimate_as_known"]
            - 100.0 * calculated["float_fraction_estimate_as_known"]
        ).abs()
        <= 1e-8
    ).all()
    blocked = daily_float[
        daily_float["float_owner_exclusion_estimate_as_known"].isna()
    ]
    nulls_explicit = (
        blocked["estimation_state"].notna()
        & blocked["blocker_codes_json"].notna()
    ).all()
    return {
        "os_grain_unique": bool(os_unique),
        "float_grain_unique": bool(float_unique),
        "os_anchor_causality_pass": bool(os_causal),
        "ownership_baseline_causality_pass": bool(baseline_causal),
        "float_formula_pass": bool(formula),
        "float_fraction_unit_pass": bool(fraction),
        "float_percent_unit_pass": bool(percent),
        "null_state_explicit_pass": bool(nulls_explicit),
        "all_checks_pass": bool(
            os_unique
            and float_unique
            and os_causal
            and baseline_causal
            and formula
            and fraction
            and percent
            and nulls_explicit
        ),
    }


def execute(args: argparse.Namespace) -> Path:
    case_matrix_path = args.case_matrix.resolve()
    cases = json.loads(case_matrix_path.read_text(encoding="utf-8"))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    rows: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    os_schemas: set[tuple[str, ...]] = set()
    float_schemas: set[tuple[str, ...]] = set()
    component_hashes: set[str] = set()
    for case in cases:
        instrument_id = str(case["instrument_id"])
        shard = shard_for(instrument_id, args.shard_count)
        ticker = str(case["ticker"])
        if case["probe_gate"] != "ELIGIBLE":
            rows.append(
                {
                    "ticker": ticker,
                    "shard": shard,
                    "probe_gate": case["probe_gate"],
                    "certification_state": "PASS_EXPECTED_FAIL_CLOSED_CONTROL",
                    "all_checks_pass": True,
                }
            )
            continue
        os_root = args.run_root / "runs" / args.os_run_template.format(
            ticker_lower=ticker.lower(), ticker=ticker
        )
        owner_root = args.run_root / "runs" / args.owner_run_template.format(
            ticker_lower=ticker.lower(), ticker=ticker
        )
        daily_os = pd.read_parquet(os_root / "daily_os_state.parquet")
        daily_float = pd.read_parquet(owner_root / "daily_float_state.parquet")
        os_schemas.add(tuple(daily_os.columns))
        float_schemas.add(tuple(daily_float.columns))
        manifest = json.loads(
            (owner_root / "final_manifest.json").read_text(encoding="utf-8")
        )
        component_hashes.add(
            json.dumps(manifest["component_hashes"], sort_keys=True)
        )
        audit = audit_daily_frames(daily_os, daily_float)
        rows.append(
            {
                "ticker": ticker,
                "shard": shard,
                "probe_gate": case["probe_gate"],
                "sessions": len(daily_float),
                "os_nonnull": int(
                    daily_os["shares_outstanding_estimate_as_known"].notna().sum()
                ),
                "float_nonnull": int(
                    daily_float[
                        "float_owner_exclusion_estimate_as_known"
                    ].notna().sum()
                ),
                "certification_state": (
                    "SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING"
                    if audit["all_checks_pass"]
                    else "FAIL"
                ),
                **audit,
            }
        )
        readable = daily_float[
            daily_float["float_owner_exclusion_estimate_as_known"].notna()
        ]
        sample = readable.iloc[0] if len(readable) else daily_float.iloc[0]
        samples.append(
            {
                "ticker": ticker,
                "shard": shard,
                **{
                    key: sample.get(key)
                    for key in (
                        "session_date",
                        "shares_outstanding_estimate_as_known",
                        "unique_supported_excluded_shares",
                        "float_owner_exclusion_estimate_as_known",
                        "float_fraction_estimate_as_known",
                        "float_percent_estimate_as_known",
                        "estimation_state",
                        "blocker_codes_json",
                    )
                },
            }
        )
    frame = pd.DataFrame(rows)
    shard_summary = []
    for shard in range(args.shard_count):
        scoped = frame[frame["shard"].eq(shard)]
        shard_summary.append(
            {
                "shard": shard,
                "case_count": len(scoped),
                "eligible_case_count": int(
                    scoped["probe_gate"].eq("ELIGIBLE").sum()
                ),
                "all_cases_pass": bool(scoped["all_checks_pass"].all()),
                "tickers": scoped["ticker"].tolist(),
            }
        )
    frame.to_parquet(output / "case_variable_certification.parquet", index=False)
    pd.DataFrame(samples).to_parquet(
        output / "readable_value_samples.parquet", index=False
    )
    result = {
        "status": (
            "SYSTEM_PASS_HUMAN_SCALE_AUTHORIZATION_PENDING"
            if frame["all_checks_pass"].all()
            and len(os_schemas) == 1
            and len(float_schemas) == 1
            and len(component_hashes) == 1
            and all(row["eligible_case_count"] >= 1 for row in shard_summary)
            else "FAIL"
        ),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "policy_id": "sec_pit_variable_by_shard_certification_v0_1",
        "shard_function": "sha256(instrument_id)_mod_4",
        "shard_count": args.shard_count,
        "shards": shard_summary,
        "os_schema_equivalent_across_cases": len(os_schemas) == 1,
        "float_schema_equivalent_across_cases": len(float_schemas) == 1,
        "component_hashes_equivalent_across_cases": len(component_hashes) == 1,
        "case_matrix_path": case_matrix_path.as_posix(),
        "case_matrix_sha256": sha256_file(case_matrix_path),
        "scale_authorization": "NOT_GRANTED_REQUIRES_HUMAN_OR_GOVERNED_GATE",
    }
    (output / "certification.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    result["outputs"] = {
        path.name: sha256_file(path)
        for path in (
            output / "case_variable_certification.parquet",
            output / "readable_value_samples.parquet",
            output / "certification.json",
        )
    }
    (output / "final_manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-matrix", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--os-run-template", required=True)
    parser.add_argument("--owner-run-template", required=True)
    parser.add_argument("--shard-count", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args))
