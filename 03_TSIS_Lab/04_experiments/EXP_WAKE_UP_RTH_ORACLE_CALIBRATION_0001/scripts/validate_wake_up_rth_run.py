#!/usr/bin/env python3
"""Independent terminal validator for Wake-up RTH candidate/panel runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from wake_up_rth_core import atomic_json, sha256_file, utc_now


PUBLIC_COLUMNS = {"blind_case_id", "case_id", "chart_file", "review_order"}
REVIEW_COLUMNS = {
    "blind_case_id",
    "case_id",
    "review_order",
    "reviewer_id",
    "label_class",
    "onset_interval_start_utc",
    "onset_interval_end_utc",
    "confidence",
    "reason_codes",
    "review_status",
    "protocol_id",
    "created_at_utc",
}
REQUIRED_STRATA = {
    "rth_time_bucket",
    "price_band",
    "market_cap_proxy_band",
    "prior_activity_stratum",
    "source_quality_stratum",
}
EXPECTED_RTH_BUCKETS = {"OPEN_0_60M", "MID_60_240M", "CLOSE_240M_PLUS"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--panel-root", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def check(condition: bool, check_id: str, detail: str, rows: list[dict]) -> None:
    rows.append(
        {
            "check_id": check_id,
            "status": "PASS" if condition else "FAIL",
            "detail": detail,
        }
    )


def main() -> int:
    args = parse_args()
    output = args.output or (args.run_root / "terminal_validation_manifest.json")
    rows = []
    final_path = args.run_root / "final_manifest.json"
    final = json.loads(final_path.read_text(encoding="utf-8"))
    check(final["status"] == "COMPLETE", "RUN_COMPLETE", str(final["status"]), rows)
    expected = int(final["expected_targets"])
    completed = int(final["completed_targets"])
    check(completed == expected, "TARGET_CARDINALITY", f"{completed}/{expected}", rows)
    check(
        int(final["governed_target_count"]) == 2400,
        "FROZEN_DENOMINATOR_MEMBERSHIP",
        str(final["governed_target_count"]),
        rows,
    )
    script_path = Path(final["script_path"])
    check(
        sha256_file(script_path) == final["script_sha256"],
        "RUNNER_SHA_MATCH",
        str(script_path),
        rows,
    )
    config_path = Path(final["config_path"])
    check(
        sha256_file(config_path) == final["config_sha256"],
        "CONFIG_SHA_MATCH",
        str(config_path),
        rows,
    )

    audit = pd.read_parquet(args.run_root / "source_and_session_audit.parquet")
    check(len(audit) == expected, "AUDIT_ROW_COUNT", f"{len(audit)}/{expected}", rows)
    check(
        not audit["target_file_key"].duplicated().any(),
        "COMPOSITE_PHYSICAL_ID_UNIQUE",
        f"unique={audit['target_file_key'].nunique()}",
        rows,
    )
    metric_paths = sorted((args.run_root / "session_metrics").glob("target_*.parquet"))
    check(len(metric_paths) == expected, "METRIC_PARTITION_COUNT", str(len(metric_paths)), rows)
    metric_cardinality_ok = True
    for path in metric_paths:
        frame = pd.read_parquet(path, columns=["target_file_key", "source_state"])
        key = str(frame["target_file_key"].iloc[0])
        expected_rows = int(
            audit.loc[audit["target_file_key"] == key, "decision_seconds"].iloc[0]
        )
        metric_cardinality_ok &= len(frame) == expected_rows
    check(metric_cardinality_ok, "DECISION_GRID_CARDINALITY", "open+1 through close-1", rows)

    candidates = pd.read_parquet(args.run_root / "candidate_pool.parquet")
    if not candidates.empty:
        check(
            not candidates.duplicated(
                ["target_file_key", "candidate_timestamp_utc"]
            ).any(),
            "CANDIDATE_IDENTITY_UNIQUE",
            f"rows={len(candidates)}",
            rows,
        )
        check(
            pd.to_datetime(candidates["session_date"]).max()
            <= pd.Timestamp("2022-12-30"),
            "NO_VALIDATION_OR_OOS_ROWS",
            str(candidates["session_date"].max()),
            rows,
        )
    else:
        check(False, "CANDIDATE_POOL_NONEMPTY", "zero candidates", rows)

    panel_root = args.panel_root or (args.run_root / "blind_panel")
    panel_manifest = json.loads(
        (panel_root / "panel_manifest.json").read_text(encoding="utf-8")
    )
    check(
        sha256_file(Path(panel_manifest["script_path"]))
        == panel_manifest["script_sha256"],
        "PANEL_BUILDER_SHA_MATCH",
        panel_manifest["script_path"],
        rows,
    )
    check(
        panel_manifest.get("config_sha256") == sha256_file(config_path)
        and panel_manifest.get("candidate_final_manifest_sha256")
        == sha256_file(final_path),
        "PANEL_INPUT_LINEAGE",
        "config and candidate final manifest hash-bound",
        rows,
    )
    public = pd.read_parquet(panel_root / "panel_blind_manifest.parquet")
    internal = pd.read_parquet(panel_root / "panel_internal_manifest.parquet")
    check(set(public.columns) == PUBLIC_COLUMNS, "BLIND_PUBLIC_SCHEMA", str(list(public.columns)), rows)
    check(
        not public["case_id"].duplicated().any(),
        "BLIND_CASE_UNIQUENESS",
        f"rows={len(public)}",
        rows,
    )
    check(
        not public["blind_case_id"].duplicated().any(),
        "BLIND_ID_UNIQUENESS",
        f"unique={public['blind_case_id'].nunique()}",
        rows,
    )
    check(
        REQUIRED_STRATA.issubset(internal.columns),
        "INTERNAL_STRATA_COMPLETE",
        str(sorted(REQUIRED_STRATA)),
        rows,
    )
    observed_rth_buckets = set(internal["rth_time_bucket"].dropna().astype(str))
    full_mode = str(final.get("mode")) == "full"
    check(
        (
            observed_rth_buckets == EXPECTED_RTH_BUCKETS
            if full_mode
            else bool(observed_rth_buckets)
            and observed_rth_buckets.issubset(EXPECTED_RTH_BUCKETS)
        ),
        "RTH_TIME_BUCKET_COVERAGE",
        f"mode={final.get('mode')} buckets={sorted(observed_rth_buckets)}",
        rows,
    )
    requested_per_group = int(panel_manifest["requested_cases_per_role_per_cohort"])
    group_counts = internal.groupby(["cohort_id", "panel_role"]).size()
    expected_group_count = len(panel_manifest["cohorts"]) * len(panel_manifest["roles"])
    check(
        (
            len(group_counts) == expected_group_count
            and bool((group_counts == requested_per_group).all())
            and not panel_manifest["shortages"]
            if full_mode
            else len(internal) > 0 and len(group_counts) > 0
        ),
        "PANEL_ROLE_COHORT_CARDINALITY",
        (
            f"groups={len(group_counts)}/{expected_group_count} "
            f"rows={len(internal)} shortages={len(panel_manifest['shortages'])}"
        ),
        rows,
    )
    review = pd.read_csv(panel_root / "review_template.csv", dtype=str)
    check(set(review.columns) == REVIEW_COLUMNS, "REVIEW_TEMPLATE_SCHEMA", str(list(review.columns)), rows)
    gallery = json.loads(
        (panel_root / "gallery_manifest.json").read_text(encoding="utf-8")
    )
    check(
        sha256_file(Path(gallery["script_path"])) == gallery["script_sha256"],
        "GALLERY_RENDERER_SHA_MATCH",
        gallery["script_path"],
        rows,
    )
    check(
        gallery.get("config_sha256") == sha256_file(config_path)
        and gallery.get("panel_manifest_sha256")
        == sha256_file(panel_root / "panel_manifest.json"),
        "GALLERY_INPUT_LINEAGE",
        "config and panel manifest hash-bound",
        rows,
    )
    chart_count = len(list((panel_root / "charts").glob("WURTH-*.png")))
    check(
        (
            chart_count == int(gallery["rendered_case_count"]) == len(public)
            if full_mode
            else chart_count == int(gallery["rendered_case_count"])
            and chart_count <= len(public)
        ),
        "GALLERY_CHART_COUNT",
        f"files={chart_count} manifest={gallery['rendered_case_count']}",
        rows,
    )
    check(
        gallery["intraday_price_path_consumed"] is False
        and gallery["price_displayed"] is False,
        "NO_INTRADAY_PRICE_PATH_IN_BLIND_GALLERY",
        "price path absent; dollar notional allowed",
        rows,
    )
    check(
        final["binding_a_consumed"] is False and final["binding_b_consumed"] is False,
        "NO_BINDING_CONTAMINATION",
        "A=false B=false",
        rows,
    )
    failed = [row for row in rows if row["status"] == "FAIL"]
    payload = {
        "status": "PASS" if not failed else "FAIL",
        "created_at_utc": utc_now(),
        "validator_path": str(Path(__file__).resolve()),
        "validator_sha256": sha256_file(Path(__file__)),
        "run_root": str(args.run_root.resolve()),
        "check_count": len(rows),
        "failed_check_count": len(failed),
        "checks": rows,
    }
    atomic_json(output, payload)
    print(json.dumps(payload, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
