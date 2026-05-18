from __future__ import annotations

from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display


def build_final_df(tax_df):
    final_df = tax_df.copy()
    final_df["has_1m_break_warn"] = final_df["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs))
    final_df["has_scale_warn"] = final_df["warns_list"].map(lambda xs: bool({"possible_corporate_action_scale_mismatch", "possible_corporate_action_scale_mismatch_vs_daily", "possible_corporate_action_scale_mismatch_vs_1m"} & set(xs)))
    final_df["has_dup_warn"] = final_df["warns_list"].map(lambda xs: bool({"duplicate_exact_trade_rows_present", "duplicate_excess_ratio_gt_threshold"} & set(xs)))
    dup_series = final_df["m.duplicate_excess_ratio_pct"] if "m.duplicate_excess_ratio_pct" in final_df.columns else pd.Series(0.0, index=final_df.index)
    off_session_series = final_df["m.off_session_trade_pct"] if "m.off_session_trade_pct" in final_df.columns else pd.Series(0.0, index=final_df.index)
    final_df["dup_excess_ratio_pct_num"] = pd.to_numeric(dup_series, errors="coerce").fillna(0)
    final_df["off_session_trade_pct_num"] = pd.to_numeric(off_session_series, errors="coerce").fillna(0)
    final_df["final_bucket"] = "manual_review"
    final_df.loc[final_df["has_1m_break_warn"] & (~final_df["has_scale_warn"]) & (final_df["dup_excess_ratio_pct_num"] < 1.0), "final_bucket"] = "likely_real_break_confirmed_by_1m"
    final_df.loc[final_df["has_1m_break_warn"] & (final_df["dup_excess_ratio_pct_num"] >= 1.0), "final_bucket"] = "likely_dup_heavy_break"
    final_df.loc[(~final_df["has_1m_break_warn"]) & (final_df["break_pct_span_max"] < 100), "final_bucket"] = "likely_minor_unconfirmed_break"
    final_df.loc[final_df["has_scale_warn"], "final_bucket"] = "scale_suspect"
    return final_df


def build_final_summary(final_df):
    return final_df.groupby("final_bucket", observed=False).agg(files=("file", "size"), tickers=("ticker", "nunique"), dates=("date", "nunique"), median_abs_break=("break_abs_max", "median"), median_pct_break=("break_pct_span_max", "median"), pct_dup_warn=("has_dup_warn", lambda s: 100 * s.mean()), pct_off_session=("off_session_trade_pct_num", lambda s: 100 * (s > 0).mean())).reset_index().sort_values("files", ascending=False)


def export_final_outputs(final_df, final_summary, export_dir):
    export_dir = Path(export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    final_df.to_parquet(export_dir / "trades_cd_root_cause_final_bucket.parquet", index=False)
    final_df.to_csv(export_dir / "trades_cd_root_cause_final_bucket.csv", index=False)
    final_summary.to_parquet(export_dir / "trades_cd_root_cause_final_bucket_summary.parquet", index=False)
    final_summary.to_csv(export_dir / "trades_cd_root_cause_final_bucket_summary.csv", index=False)
    return export_dir


def run_cd_final_bucket(tax_df, export_dir, write_exports: bool = True):
    final_df = build_final_df(tax_df)
    final_summary = build_final_summary(final_df)
    display(final_summary)
    final_export_dir = None
    if write_exports:
        final_export_dir = export_final_outputs(final_df, final_summary, export_dir)
        display(Markdown(f"Exportado en: `{final_export_dir}`"))
    return final_df, final_summary, final_export_dir
