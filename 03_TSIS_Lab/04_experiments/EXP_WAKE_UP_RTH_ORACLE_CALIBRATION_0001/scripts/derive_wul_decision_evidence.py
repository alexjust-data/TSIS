#!/usr/bin/env python3
"""Derive WUL-D01..D08 evidence without choosing or freezing decisions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from wake_up_rth_core import atomic_json, load_config, sha256_file, utc_now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--candidate-run-root", required=True, type=Path)
    parser.add_argument("--panel-root", required=True, type=Path)
    parser.add_argument("--review-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def sum_window(metrics, onset, start_delta, end_delta, column):
    start = onset + pd.Timedelta(seconds=start_delta)
    end = onset + pd.Timedelta(seconds=end_delta)
    mask = (
        (metrics["decision_timestamp_utc"] >= start)
        & (metrics["decision_timestamp_utc"] < end)
    )
    return float(metrics.loc[mask, column].sum()), int(mask.sum())


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    review_manifest = json.loads(
        (args.review_root / "review_aggregation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if review_manifest["status"] != "COMPLETE":
        raise ValueError("All disagreements must be adjudicated before WUL evidence")
    panel = pd.read_parquet(args.panel_root / "panel_internal_manifest.parquet")
    labels = pd.read_parquet(args.review_root / "adjudicated_labels.parquet")
    cases = panel.merge(labels, on="case_id", how="inner", validate="one_to_one")
    if len(cases) != len(panel):
        raise ValueError("Adjudicated labels do not cover the full panel")

    rows = []
    metric_cache = {}
    for case in cases.itertuples(index=False):
        target_file_key = str(case.target_file_key)
        if target_file_key not in metric_cache:
            path = (
                args.candidate_run_root / "session_metrics"
                / f"{target_file_key}.parquet"
            )
            metrics = pd.read_parquet(path)
            metrics["decision_timestamp_utc"] = pd.to_datetime(
                metrics["decision_timestamp_utc"], utc=True
            )
            metric_cache[target_file_key] = metrics
        metrics = metric_cache[target_file_key]
        onset = pd.Timestamp(case.candidate_timestamp_utc)
        onset = onset.tz_localize("UTC") if onset.tzinfo is None else onset.tz_convert("UTC")
        for dormancy in config["discovery"]["dormancy_seconds"]:
            for confirmation in config["discovery"]["confirmation_seconds"]:
                prior_trade, prior_seconds = sum_window(
                    metrics, onset, -int(dormancy), 0, "trade_count"
                )
                prior_cluster, _ = sum_window(
                    metrics, onset, -int(dormancy), 0,
                    "distinct_timestamp_clusters",
                )
                prior_dollar, _ = sum_window(
                    metrics, onset, -int(dormancy), 0, "dollar_volume"
                )
                confirm_trade, confirm_seconds = sum_window(
                    metrics, onset, 0, int(confirmation), "trade_count"
                )
                confirm_cluster, _ = sum_window(
                    metrics, onset, 0, int(confirmation),
                    "distinct_timestamp_clusters",
                )
                confirm_dollar, _ = sum_window(
                    metrics, onset, 0, int(confirmation), "dollar_volume"
                )
                quality, _ = sum_window(
                    metrics, onset, 0, int(confirmation),
                    "duplicate_trade_count",
                )
                restricted, _ = sum_window(
                    metrics, onset, 0, int(confirmation),
                    "restricted_or_unknown_trade_count",
                )
                prior_rate = prior_trade / max(prior_seconds, 1)
                confirm_rate = confirm_trade / max(confirm_seconds, 1)
                rows.append(
                    {
                        "case_id": case.case_id,
                        "blind_case_id": case.blind_case_id,
                        "cohort_id": case.cohort_id,
                        "panel_role": case.panel_role,
                        "final_label_class": case.final_label_class,
                        "dormancy_seconds": int(dormancy),
                        "confirmation_seconds": int(confirmation),
                        "prior_observed_seconds": prior_seconds,
                        "confirmation_observed_seconds": confirm_seconds,
                        "prior_trade_count": prior_trade,
                        "prior_cluster_count": prior_cluster,
                        "prior_dollar_volume": prior_dollar,
                        "confirmation_trade_count": confirm_trade,
                        "confirmation_cluster_count": confirm_cluster,
                        "confirmation_dollar_volume": confirm_dollar,
                        "prior_trade_rate_per_second": prior_rate,
                        "confirmation_trade_rate_per_second": confirm_rate,
                        "trade_rate_ratio_laplace_one_event": (
                            (confirm_trade + 1.0) / max(confirm_seconds, 1)
                        )
                        / ((prior_trade + 1.0) / max(prior_seconds, 1)),
                        "prior_observed_silence": prior_trade == 0,
                        "quality_flag_count_confirmation": quality + restricted,
                    }
                )
    evidence = pd.DataFrame(rows)
    numeric = [
        "prior_trade_count",
        "prior_cluster_count",
        "prior_dollar_volume",
        "confirmation_trade_count",
        "confirmation_cluster_count",
        "confirmation_dollar_volume",
        "trade_rate_ratio_laplace_one_event",
        "quality_flag_count_confirmation",
    ]
    summary = (
        evidence.groupby(
            [
                "final_label_class",
                "cohort_id",
                "dormancy_seconds",
                "confirmation_seconds",
            ],
            dropna=False,
        )[numeric]
        .agg(["count", "median", lambda x: x.quantile(0.10), lambda x: x.quantile(0.90)])
    )
    summary.columns = [
        "_".join([str(part) for part in column]).replace("<lambda_0>", "p10").replace(
            "<lambda_1>", "p90"
        )
        for column in summary.columns
    ]
    summary = summary.reset_index()
    args.output_root.mkdir(parents=True, exist_ok=False)
    evidence.to_parquet(args.output_root / "wul_case_parameter_evidence.parquet", index=False)
    summary.to_parquet(args.output_root / "wul_stratified_parameter_summary.parquet", index=False)
    atomic_json(
        args.output_root / "wul_decision_evidence_manifest.json",
        {
            "status": "EVIDENCE_READY_FOR_HUMAN_WUL_D01_D08_DECISIONS",
            "created_at_utc": utc_now(),
            "script_path": str(Path(__file__).resolve()),
            "script_sha256": sha256_file(Path(__file__)),
            "case_count": len(cases),
            "evidence_row_count": len(evidence),
            "dormancy_grid": config["discovery"]["dormancy_seconds"],
            "confirmation_grid": config["discovery"]["confirmation_seconds"],
            "binding_a_consumed": False,
            "binding_b_consumed": False,
            "intraday_price_path_consumed": False,
            "trade_price_used_only_via_dollar_notional": True,
            "automatic_wul_selection_performed": False,
            "freeze_performed": False,
        },
    )
    print(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
