from __future__ import annotations

import pandas as pd


def classify_quote_case(row: pd.Series) -> str:
    crossed = float(row.get("m.crossed_ratio_pct", 0.0) or 0.0)
    ask_integer = float(row.get("m.ask_integer_pct", 0.0) or 0.0)
    ask_round = float(row.get("m.ask_eq_round_bid_pct", 0.0) or 0.0)
    ts_shift = bool(row.get("m.timestamp_out_of_partition_day", False))
    rows = float(row.get("rows", 0.0) or 0.0)
    issues = set(row.get("issues_list", []) or [])
    warns = set(row.get("warns_list", []) or [])

    if "ask_integer_with_crossed_anomaly" in issues or (ask_integer >= 95 and crossed > 20):
        return "integerized_crossed_anomaly"
    if "crossed_ratio_gt_hard_cap" in issues or crossed > 5:
        return "hard_crossed_market"
    if "crossed_ratio_gt_threshold" in issues and rows <= 100:
        return "small_file_hard_crossed"
    if "crossed_ratio_gt_threshold" in issues:
        return "moderate_crossed_market"
    if ts_shift and "crossed_rows_present_but_under_threshold" in warns:
        return "soft_crossed_plus_timestamp_shift"
    if ts_shift:
        return "timestamp_partition_shift"
    if "crossed_rows_present_but_under_threshold" in warns and crossed <= 0.1:
        return "mild_crossed_micro_noise"
    if "crossed_rows_present_but_under_threshold" in warns:
        return "persistent_soft_crossed_market"
    if ask_round >= 80:
        return "rounded_ask_pattern_without_cross_hard"
    return "clean_pass_or_other"


def run_cd_taxonomy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tax_df = df.copy()
    tax_df["taxonomy"] = tax_df.apply(classify_quote_case, axis=1)
    summary = (
        tax_df.groupby("taxonomy", dropna=False)
        .agg(
            files=("task_key", "count"),
            tickers=("ticker", "nunique"),
            dates=("date", "nunique"),
            hard_fail_files=("severity", lambda s: int(s.eq("HARD_FAIL").sum())),
            soft_fail_files=("severity", lambda s: int(s.eq("SOFT_FAIL").sum())),
            crossed_ratio_median_pct=("m.crossed_ratio_pct", "median"),
            crossed_ratio_p90_pct=("m.crossed_ratio_pct", lambda s: float(s.quantile(0.9))),
        )
        .reset_index()
        .sort_values("files", ascending=False)
        .reset_index(drop=True)
    )
    summary["pct"] = summary["files"] / max(len(tax_df), 1) * 100.0
    return tax_df, summary

