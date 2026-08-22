#!/usr/bin/env python3
"""Validate, preserve and aggregate two independent blind Wake-up reviews."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from wake_up_rth_core import atomic_json, sha256_file, utc_now


ALLOWED_CLASSES = {
    "POSITIVE_WAKE_UP",
    "NEGATIVE_ONE_PRINT",
    "NEGATIVE_INSUFFICIENT_CORROBORATION",
    "NEGATIVE_CONTEXT_NORMAL_HIGH_ACTIVITY",
    "NEGATIVE_DATA_ARTIFACT",
    "AMBIGUOUS",
    "UNAVAILABLE",
}
REQUIRED_COLUMNS = {
    "reviewer_id",
    "case_id",
    "label_class",
    "onset_interval_start_utc",
    "onset_interval_end_utc",
    "confidence",
    "reason_codes",
    "review_status",
    "protocol_id",
    "created_at_utc",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel-root", required=True, type=Path)
    parser.add_argument("--review", required=True, action="append", type=Path)
    parser.add_argument("--adjudication", type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def read_review(path: Path, panel_ids: set[str]) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str).fillna("")
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    if frame["case_id"].duplicated().any():
        raise ValueError(f"{path} contains duplicate case_id")
    if set(frame["case_id"]) != panel_ids:
        raise ValueError(f"{path} case membership differs from frozen panel")
    invalid = sorted(set(frame["label_class"]).difference(ALLOWED_CLASSES))
    if invalid:
        raise ValueError(f"{path} has invalid label classes: {invalid}")
    if frame["reviewer_id"].nunique() != 1:
        raise ValueError(f"{path} must contain exactly one reviewer_id")
    if (frame["review_status"] != "COMPLETE").any():
        raise ValueError(f"{path} contains non-COMPLETE review rows")
    return frame


def main() -> int:
    args = parse_args()
    if len(args.review) != 2:
        raise ValueError("Exactly two independent review files are required")
    panel = pd.read_parquet(args.panel_root / "panel_internal_manifest.parquet")
    panel_ids = set(panel["case_id"].astype(str))
    left = read_review(args.review[0], panel_ids)
    right = read_review(args.review[1], panel_ids)
    if left["reviewer_id"].iloc[0] == right["reviewer_id"].iloc[0]:
        raise ValueError("The two review files must have different reviewer IDs")
    combined = pd.concat([left, right], ignore_index=True)
    paired = left.merge(right, on="case_id", suffixes=("_r1", "_r2"), validate="one_to_one")
    agreement = paired["label_class_r1"] == paired["label_class_r2"]
    paired["agreement_state"] = pd.Series(
        ["AGREEMENT" if value else "DISAGREEMENT" for value in agreement]
    )
    agreed = paired.loc[agreement].copy()
    adjudicated = pd.DataFrame(
        {
            "case_id": agreed["case_id"],
            "final_label_class": agreed["label_class_r1"],
            "finalization_mode": "DIRECT_REVIEWER_AGREEMENT",
        }
    )
    disagreements = paired.loc[~agreement].copy()
    if not disagreements.empty and args.adjudication is not None:
        decision = pd.read_csv(args.adjudication, dtype=str).fillna("")
        required = {"case_id", "final_label_class", "adjudicator_id", "reason_codes"}
        missing = required.difference(decision.columns)
        if missing:
            raise ValueError(f"Adjudication missing columns: {sorted(missing)}")
        if set(decision["case_id"]) != set(disagreements["case_id"]):
            raise ValueError("Adjudication must cover exactly all disagreements")
        invalid = sorted(set(decision["final_label_class"]).difference(ALLOWED_CLASSES))
        if invalid:
            raise ValueError(f"Invalid adjudicated classes: {invalid}")
        decision["finalization_mode"] = "SEPARATE_ADJUDICATOR"
        adjudicated = pd.concat(
            [adjudicated, decision[["case_id", "final_label_class", "finalization_mode"]]],
            ignore_index=True,
        )

    args.output_root.mkdir(parents=True, exist_ok=False)
    combined.to_parquet(args.output_root / "immutable_reviewer_rows.parquet", index=False)
    paired.to_parquet(args.output_root / "paired_review_comparison.parquet", index=False)
    disagreements.to_csv(args.output_root / "disagreements_for_adjudication.csv", index=False)
    adjudicated.to_parquet(args.output_root / "adjudicated_labels.parquet", index=False)
    status = (
        "COMPLETE"
        if len(adjudicated) == len(panel)
        else "WAITING_FOR_SEPARATE_ADJUDICATION"
    )
    atomic_json(
        args.output_root / "review_aggregation_manifest.json",
        {
            "status": status,
            "created_at_utc": utc_now(),
            "script_path": str(Path(__file__).resolve()),
            "script_sha256": sha256_file(Path(__file__)),
            "panel_case_count": len(panel),
            "reviewer_row_count": len(combined),
            "agreement_count": int(agreement.sum()),
            "disagreement_count": int((~agreement).sum()),
            "adjudicated_case_count": len(adjudicated),
            "ambiguous_and_unavailable_preserved": True,
        },
    )
    print(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
