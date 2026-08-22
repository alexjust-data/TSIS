#!/usr/bin/env python3
"""Create a deterministic, stratified and blinded Wake-up review panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from wake_up_rth_core import atomic_json, load_config, sha256_file, stable_case_id, utc_now


ROLES = (
    "CANDIDATE_ACTIVITY_TRANSITION",
    "CONTROL_DORMANT",
    "CONTROL_ONE_CLUSTER",
    "CONTROL_CONTEXT_NORMAL_ACTIVITY",
    "CONTROL_QUALITY_OR_ARTIFACT",
    "CONTROL_RANDOM_ELIGIBLE",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--candidate-run-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    return parser.parse_args()


def _future_sum(series: pd.Series, seconds: int) -> pd.Series:
    return series.iloc[::-1].rolling(seconds, min_periods=1).sum().iloc[::-1]


def _case_rows(metrics: pd.DataFrame, role: str) -> pd.DataFrame:
    trades = metrics["trade_count"].astype(float)
    clusters = metrics["distinct_timestamp_clusters"].astype(float)
    dollars = metrics["dollar_volume"].astype(float)
    prior_trades = trades.shift(1).rolling(900, min_periods=60).sum()
    future_trades = _future_sum(trades, 60)
    future_clusters = _future_sum(clusters, 60)
    future_dollars = _future_sum(dollars, 60)
    quality = (
        metrics["duplicate_trade_count"].astype(float)
        + metrics["restricted_or_unknown_trade_count"].astype(float)
    )
    positions = np.arange(len(metrics))

    if role == "CONTROL_DORMANT":
        mask = (prior_trades == 0) & (future_trades == 0)
    elif role == "CONTROL_ONE_CLUSTER":
        mask = (future_clusters == 1) & (future_trades >= 1)
    elif role == "CONTROL_CONTEXT_NORMAL_ACTIVITY":
        prior_rate = prior_trades / 900.0
        future_rate = future_trades / 60.0
        ratio = (future_rate + 1e-9) / (prior_rate + 1e-9)
        mask = (prior_trades >= 10) & (future_trades >= 2) & ratio.between(0.5, 2.0)
    elif role == "CONTROL_QUALITY_OR_ARTIFACT":
        mask = quality > 0
    elif role == "CONTROL_RANDOM_ELIGIBLE":
        mask = (
            (metrics["source_state"] == "OBSERVED")
            & (positions >= 900)
            & (positions < len(metrics) - 300)
        )
    else:
        raise ValueError(role)

    selected = metrics.loc[
        mask,
        [
            "target_ordinal",
            "target_file_key",
            "block_id",
            "cohort_id",
            "instrument_id",
            "ticker",
            "session_date",
            "session_open_utc",
            "presession_reference_price",
            "presession_reference_market_cap_proxy",
            "decision_timestamp_utc",
            "source_state",
        ],
    ].copy()
    selected = selected.rename(
        columns={"decision_timestamp_utc": "candidate_timestamp_utc"}
    )
    selected["panel_role"] = role
    selected["prior_trade_count_900s"] = prior_trades.loc[mask].to_numpy()
    selected["confirmation_trade_count_60s"] = future_trades.loc[mask].to_numpy()
    selected["confirmation_cluster_count_60s"] = future_clusters.loc[mask].to_numpy()
    selected["confirmation_dollar_volume_60s"] = future_dollars.loc[mask].to_numpy()
    selected["quality_flag_count"] = quality.loc[mask].to_numpy()
    return selected


def _add_strata(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    timestamp = pd.to_datetime(frame["candidate_timestamp_utc"], utc=True)
    session_open = pd.to_datetime(frame["session_open_utc"], utc=True)
    minutes = (timestamp - session_open).dt.total_seconds() / 60.0
    frame["rth_time_bucket"] = pd.cut(
        minutes,
        bins=[-1, 60, 240, float("inf")],
        labels=["OPEN_0_60M", "MID_60_240M", "CLOSE_240M_PLUS"],
    ).astype(str)
    frame["price_band"] = pd.cut(
        frame["presession_reference_price"].astype(float),
        bins=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0000001],
        right=False,
        labels=["P_0_5_1", "P_1_2", "P_2_5", "P_5_10", "P_10_20"],
    ).astype(str)
    frame["market_cap_proxy_band"] = pd.cut(
        frame["presession_reference_market_cap_proxy"].astype(float),
        bins=[0, 10e6, 25e6, 50e6, 100e6],
        right=False,
        labels=["MCAP_LT10M", "MCAP_10_25M", "MCAP_25_50M", "MCAP_50_100M"],
    ).astype(str)
    prior = frame.get(
        "prior_trade_count",
        frame.get("prior_trade_count_900s", pd.Series(0, index=frame.index)),
    ).fillna(0)
    frame["prior_activity_stratum"] = pd.cut(
        prior.astype(float),
        bins=[-1, 0, 10, float("inf")],
        labels=["PRIOR_ZERO", "PRIOR_LOW", "PRIOR_ACTIVE"],
    ).astype(str)
    quality = frame.get("quality_flag_count", pd.Series(0, index=frame.index)).fillna(0)
    frame["source_quality_stratum"] = np.where(
        quality.astype(float) > 0, "QUALITY_FLAGGED", "QUALITY_CLEAR"
    )
    frame["sampling_stratum"] = (
        frame["rth_time_bucket"] + "|" + frame["price_band"] + "|"
        + frame["market_cap_proxy_band"] + "|" + frame["prior_activity_stratum"]
        + "|" + frame["source_quality_stratum"]
    )
    return frame


def _deterministic_sample(
    frame: pd.DataFrame, count: int, seed: int, key: str
) -> pd.DataFrame:
    if frame.empty:
        return frame
    key_seed = int.from_bytes(key.encode("utf-8"), "little", signed=False) % (2**32)
    rng = np.random.default_rng((seed + key_seed) % (2**32))
    work = frame.reset_index(drop=True).copy()
    work["_source_row_id"] = np.arange(len(work))
    work["_random_order"] = rng.random(len(work))

    def sample_composite(source: pd.DataFrame, requested: int) -> pd.DataFrame:
        if source.empty or requested <= 0:
            return source.head(0)
        if "sampling_stratum" not in source.columns:
            return source.sort_values("_random_order").head(requested)
        strata = sorted(source["sampling_stratum"].astype(str).unique())
        rng.shuffle(strata)
        stratum_order = {value: ordinal for ordinal, value in enumerate(strata)}
        ordered = source.copy()
        ordered["_stratum_order"] = (
            ordered["sampling_stratum"].astype(str).map(stratum_order)
        )
        ordered = ordered.sort_values(["_stratum_order", "_random_order"])
        selected_layers = []
        for round_number in range(1, len(ordered) + 1):
            layer = ordered.groupby(
                "sampling_stratum", sort=False, as_index=False
            ).nth(round_number - 1)
            if layer.empty:
                break
            selected_layers.append(layer.sort_values("_stratum_order"))
            if sum(len(part) for part in selected_layers) >= requested:
                break
        return pd.concat(selected_layers, ignore_index=True).head(requested)

    selected_parts = []
    if "rth_time_bucket" in work.columns:
        time_buckets = sorted(work["rth_time_bucket"].astype(str).unique())
        rng.shuffle(time_buckets)
        base, remainder = divmod(min(count, len(work)), len(time_buckets))
        for ordinal, bucket in enumerate(time_buckets):
            quota = base + (1 if ordinal < remainder else 0)
            bucket_source = work.loc[
                work["rth_time_bucket"].astype(str) == bucket
            ]
            selected_parts.append(sample_composite(bucket_source, quota))
    else:
        selected_parts.append(sample_composite(work, count))

    selected = (
        pd.concat(selected_parts, ignore_index=True)
        if selected_parts
        else work.head(0)
    )
    selected_ids = set(selected["_source_row_id"].astype(int))
    shortfall = min(count, len(work)) - len(selected)
    if shortfall > 0:
        remaining = work.loc[~work["_source_row_id"].isin(selected_ids)]
        selected = pd.concat(
            [selected, sample_composite(remaining, shortfall)], ignore_index=True
        )
    selected["_final_order"] = rng.random(len(selected))
    return (
        selected.sort_values("_final_order")
        .head(count)
        .drop(
            columns=[
                "_source_row_id",
                "_random_order",
                "_stratum_order",
                "_final_order",
            ],
            errors="ignore",
        )
        .reset_index(drop=True)
    )


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    final_manifest = json.loads(
        (args.candidate_run_root / "final_manifest.json").read_text(encoding="utf-8")
    )
    if final_manifest["status"] != "COMPLETE":
        raise ValueError("Candidate run must be COMPLETE")
    candidates = pd.read_parquet(args.candidate_run_root / "candidate_pool.parquet")
    if candidates.empty:
        raise ValueError("Candidate pool is empty")
    candidates["panel_role"] = "CANDIDATE_ACTIVITY_TRANSITION"
    candidates = _add_strata(candidates)
    metrics_paths = sorted(
        (args.candidate_run_root / "session_metrics").glob("target_*.parquet")
    )
    controls: list[pd.DataFrame] = []
    for metrics_path in metrics_paths:
        metrics = pd.read_parquet(metrics_path)
        if metrics.empty or metrics["source_state"].iloc[0] != "OBSERVED":
            continue
        for role in ROLES[1:]:
            controls.append(_case_rows(metrics, role))
    control_pool = pd.concat(controls, ignore_index=True) if controls else pd.DataFrame()
    if not control_pool.empty:
        control_pool = _add_strata(control_pool)

    panel_config = config["panel"]
    count = int(panel_config["cases_per_role_per_cohort"])
    seed = int(panel_config["blind_seed"])
    cohorts = sorted(candidates["cohort_id"].dropna().astype(str).unique())
    selected_parts: list[pd.DataFrame] = []
    shortages: list[dict] = []
    for cohort in cohorts:
        for role in ROLES:
            source = (
                candidates.loc[candidates["cohort_id"].astype(str) == cohort].copy()
                if role == ROLES[0]
                else control_pool.loc[
                    (control_pool["cohort_id"].astype(str) == cohort)
                    & (control_pool["panel_role"] == role)
                ].copy()
            )
            sample = _deterministic_sample(source, count, seed, f"{cohort}|{role}")
            if len(sample) < count:
                shortages.append(
                    {
                        "cohort_id": cohort,
                        "panel_role": role,
                        "requested": count,
                        "available": len(source),
                        "selected": len(sample),
                    }
                )
            selected_parts.append(sample)
    panel = pd.concat(selected_parts, ignore_index=True)
    panel["candidate_timestamp_utc"] = pd.to_datetime(
        panel["candidate_timestamp_utc"], utc=True
    )
    panel["case_id"] = panel.apply(stable_case_id, axis=1)
    if panel["case_id"].duplicated().any():
        raise ValueError("Panel contains duplicate case IDs")
    blind_order = _deterministic_sample(panel, len(panel), seed, "BLIND_ORDER").reset_index(
        drop=True
    )
    blind_order["blind_case_id"] = [
        f"WURTH-{ordinal:04d}" for ordinal in range(1, len(blind_order) + 1)
    ]

    args.output_root.mkdir(parents=True, exist_ok=False)
    internal_columns = [
        "blind_case_id",
        "case_id",
        "panel_role",
        "target_ordinal",
        "target_file_key",
        "block_id",
        "cohort_id",
        "instrument_id",
        "ticker",
        "session_date",
        "session_open_utc",
        "presession_reference_price",
        "presession_reference_market_cap_proxy",
        "candidate_timestamp_utc",
        "source_state",
        "rth_time_bucket",
        "price_band",
        "market_cap_proxy_band",
        "prior_activity_stratum",
        "source_quality_stratum",
        "sampling_stratum",
    ]
    for optional in (
        "dormancy_window_seconds",
        "confirmation_window_seconds",
        "candidate_reduction_score",
        "prior_trade_count",
        "confirmation_trade_count",
        "confirmation_cluster_count",
        "confirmation_dollar_volume",
        "prior_trade_count_900s",
        "confirmation_trade_count_60s",
        "confirmation_cluster_count_60s",
        "confirmation_dollar_volume_60s",
        "quality_flag_count",
    ):
        if optional in blind_order.columns:
            internal_columns.append(optional)
    internal = blind_order[internal_columns].copy()
    public = internal[["blind_case_id", "case_id"]].copy()
    public["chart_file"] = public["blind_case_id"].map(lambda x: f"charts/{x}.png")
    public["review_order"] = np.arange(1, len(public) + 1)
    internal.to_parquet(args.output_root / "panel_internal_manifest.parquet", index=False)
    public.to_parquet(args.output_root / "panel_blind_manifest.parquet", index=False)

    review_template = public[["blind_case_id", "case_id", "review_order"]].copy()
    review_template["reviewer_id"] = ""
    review_template["label_class"] = ""
    review_template["onset_interval_start_utc"] = ""
    review_template["onset_interval_end_utc"] = ""
    review_template["confidence"] = ""
    review_template["reason_codes"] = ""
    review_template["review_status"] = ""
    review_template["protocol_id"] = "wake_up_blind_review_protocol_v0_1"
    review_template["created_at_utc"] = ""
    review_template.to_csv(args.output_root / "review_template.csv", index=False)
    manifest = {
        "status": "COMPLETE" if not shortages else "COMPLETE_WITH_PANEL_SHORTAGES",
        "created_at_utc": utc_now(),
        "candidate_run_root": str(args.candidate_run_root.resolve()),
        "candidate_final_manifest_sha256": sha256_file(
            args.candidate_run_root / "final_manifest.json"
        ),
        "config_path": str(args.config.resolve()),
        "config_sha256": sha256_file(args.config),
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": sha256_file(Path(__file__)),
        "panel_case_count": len(internal),
        "cohorts": cohorts,
        "roles": list(ROLES),
        "requested_cases_per_role_per_cohort": count,
        "shortages": shortages,
        "blind_manifest_exposes_identity": False,
        "blind_manifest_exposes_panel_role": False,
        "intraday_price_path_consumed": False,
        "presession_reference_price_used_for_stratification": True,
        "trade_price_used_only_via_dollar_notional": True,
        "binding_a_consumed": False,
        "binding_b_consumed": False,
    }
    atomic_json(args.output_root / "panel_manifest.json", manifest)
    print(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
