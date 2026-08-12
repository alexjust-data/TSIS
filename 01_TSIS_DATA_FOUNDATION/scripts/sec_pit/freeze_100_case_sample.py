#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp


LOCAL_TAGS = {
    "LONGITUDINAL_2005_TO_2025": "tag_longitudinal_2005_to_2025",
    "MULTIPLE_TICKER_CHANGES": "tag_multiple_ticker_changes",
    "HEAVY_REVERSE_SPLIT_HISTORY": "tag_heavy_reverse_split_history",
    "SPAC_NAME_CANDIDATE": "tag_spac_name_candidate",
    "INACTIVE_OR_DELISTED_CANDIDATE": "tag_inactive_or_delisted_candidate",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def span_bucket(days: int) -> str:
    years = days / 365.25
    if years < 2:
        return "LT_2Y"
    if years < 5:
        return "Y2_TO_5"
    if years < 10:
        return "Y5_TO_10"
    if years < 15:
        return "Y10_TO_15"
    return "GE_15Y"


def solve_sample(frame: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    frame = frame.copy().reset_index(drop=True)
    frame["document_tags"] = frame["document_strata_json"].map(json.loads)
    frame["span_bucket"] = frame["observed_span_days"].map(lambda value: span_bucket(int(value)))
    tag_membership: dict[str, np.ndarray] = {}
    for tag, column in LOCAL_TAGS.items():
        tag_membership[tag] = frame[column].fillna(False).astype(bool).to_numpy(dtype=float)
    for tag in config["minimum_tag_counts"]:
        if tag not in tag_membership:
            tag_membership[tag] = frame["document_tags"].map(
                lambda tags, required_tag=tag: required_tag in tags
            ).to_numpy(dtype=float)

    rows: list[np.ndarray] = []
    lower: list[float] = []
    upper: list[float] = []
    audit_specs: list[dict[str, Any]] = []

    def constraint(name: str, mask: np.ndarray, low: float, high: float) -> None:
        rows.append(mask.astype(float))
        lower.append(low)
        upper.append(high)
        audit_specs.append({"constraint": name, "required_min": low, "required_max": high})

    ones = np.ones(len(frame))
    total = int(config["final_case_count"])
    constraint("FINAL_CASE_COUNT", ones, total, total)
    for cohort, quota in config["final_temporal_cohort_quotas"].items():
        constraint(f"COHORT_{cohort}", frame["temporal_cohort"].eq(cohort).to_numpy(), quota, quota)
    for shard, quota in config["exact_shard_quotas"].items():
        constraint(f"SHARD_{shard}", frame["shard"].eq(int(shard)).to_numpy(), quota, quota)
    for ticker in config["required_anchors"]:
        constraint(f"ANCHOR_{ticker}", frame["ticker"].eq(ticker).to_numpy(), 1, 1)
    for tag, minimum in config["minimum_tag_counts"].items():
        constraint(f"TAG_{tag}", tag_membership[tag], minimum, np.inf)
    for bucket, minimum in config["minimum_span_bucket_counts"].items():
        constraint(f"SPAN_{bucket}", frame["span_bucket"].eq(bucket).to_numpy(), minimum, np.inf)
    years = config["required_calendar_years"]
    for year in range(int(years["first"]), int(years["last"]) + 1):
        mask = frame["first_seen_year"].le(year) & frame["last_observed_year"].ge(year)
        constraint(f"CALENDAR_YEAR_{year}", mask.to_numpy(), int(years["minimum_cases"]), np.inf)

    rarity = np.zeros(len(frame))
    for membership in tag_membership.values():
        rarity += membership / max(1.0, membership.sum())
    tie = frame["stable_rank"].map(lambda value: int(str(value)[:16], 16) / (2**64)).to_numpy()
    objective = -(rarity + (1.0 - tie) * 1e-6)
    result = milp(
        c=objective,
        integrality=np.ones(len(frame)),
        bounds=Bounds(np.zeros(len(frame)), np.ones(len(frame))),
        constraints=LinearConstraint(np.vstack(rows), np.array(lower), np.array(upper)),
        options={"presolve": True},
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"sample MILP failed: {result.message}")
    chosen_mask = result.x > 0.5
    selected = frame.loc[chosen_mask].copy()
    for spec, mask in zip(audit_specs, rows, strict=True):
        spec["observed"] = int(mask[chosen_mask].sum())
        spec["pass"] = bool(spec["observed"] >= spec["required_min"] and spec["observed"] <= spec["required_max"])
    selected["all_strata_json"] = selected.apply(
        lambda row: json.dumps(sorted(set(row["document_tags"] + [
            tag for tag, column in LOCAL_TAGS.items() if bool(row[column])
        ])), separators=(",", ":")), axis=1,
    )
    selected = selected.sort_values(["temporal_cohort", "shard", "stable_rank"]).reset_index(drop=True)
    selected["final_sample_order"] = range(1, len(selected) + 1)
    return selected, audit_specs


def execute(config_path: Path, output: Path) -> Path:
    config_path = config_path.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    profiles_path = Path(config["candidate_profiles_path"]).resolve()
    output.mkdir(parents=True)
    pre = {
        "run_id": output.name,
        "status": "RUNNING",
        "created_at_utc": datetime.now(UTC).isoformat(),
        "config_path": config_path.as_posix(),
        "config_sha256": sha256_file(config_path),
        "candidate_profiles_path": profiles_path.as_posix(),
        "candidate_profiles_sha256": sha256_file(profiles_path),
        "network_access": "PROHIBITED_AND_NOT_USED",
        "primary_document_download": "NOT_AUTHORIZED",
    }
    (output / "pre_manifest.json").write_text(json.dumps(pre, indent=2) + "\n", encoding="utf-8")
    frame = pd.read_parquet(profiles_path)
    selected, audit = solve_sample(frame, config)
    if len(selected) != int(config["final_case_count"]) or not all(row["pass"] for row in audit):
        raise RuntimeError("selected sample failed governed constraint audit")
    selected.to_parquet(output / "final_100_cases.parquet", index=False)
    selected.to_csv(output / "final_100_cases.csv", index=False)
    pd.DataFrame(audit).to_csv(output / "constraint_audit.csv", index=False)
    cases = [
        {
            "ticker": row["ticker"], "cik": row["cik"],
            "instrument_id": row["instrument_id"],
            "security_class_id": row.get("share_class_figi"),
            "issuer_name": row["name"],
            "temporal_cohort": row["temporal_cohort"], "shard": int(row["shard"]),
            "first_seen_date": str(row["first_seen_date"]),
            "last_observed_date": str(row["last_observed_date"]),
            "strata": json.loads(row["all_strata_json"]),
            "security_class_gate": "PENDING_PREDOWNLOAD_CONTROL",
        }
        for row in selected.to_dict("records")
    ]
    (output / "final_100_cases.json").write_text(json.dumps(cases, indent=2, default=str) + "\n", encoding="utf-8")
    final = {
        **pre,
        "status": "COMPLETE",
        "completed_at_utc": datetime.now(UTC).isoformat(),
        "selected_case_count": len(selected),
        "constraint_count": len(audit),
        "constraint_pass_count": sum(row["pass"] for row in audit),
        "cohort_counts": selected["temporal_cohort"].value_counts().sort_index().to_dict(),
        "shard_counts": {str(k): int(v) for k, v in selected["shard"].value_counts().sort_index().items()},
        "span_counts": selected["span_bucket"].value_counts().to_dict(),
        "next_gate": "PREDOWNLOAD_IDENTITY_LIFECYCLE_AND_DOCUMENT_SELECTION_PROBES_PER_SHARD",
        "primary_document_download": "NOT_AUTHORIZED",
        "outputs": {
            name: sha256_file(output / name)
            for name in ("final_100_cases.parquet", "final_100_cases.csv", "final_100_cases.json", "constraint_audit.csv")
        },
    }
    (output / "final_manifest.json").write_text(json.dumps(final, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(execute(args.config, args.output))
