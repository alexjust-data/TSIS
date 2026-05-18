from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_explain_df(band_df: pd.DataFrame) -> pd.DataFrame:
    explain_df = band_df.copy()
    explain_df["has_1m_break_warn"] = explain_df["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs))
    explain_df["has_scale_warn"] = explain_df["warns_list"].map(
        lambda xs: bool({
            "possible_corporate_action_scale_mismatch",
            "possible_corporate_action_scale_mismatch_vs_daily",
            "possible_corporate_action_scale_mismatch_vs_1m",
        } & set(xs))
    )
    explain_df["has_off_session_warn"] = explain_df["warns_list"].map(lambda xs: "off_session_trades_present" in set(xs))
    explain_df["has_dup_warn"] = explain_df["warns_list"].map(
        lambda xs: bool({
            "duplicate_exact_trade_rows_present",
            "duplicate_excess_ratio_gt_threshold",
        } & set(xs))
    )
    return explain_df


def build_abs_pct_signal_tables(explain_df: pd.DataFrame):
    abs_signal = explain_df.groupby("abs_break_bucket", observed=False).agg(
        files=("file", "size"),
        pct_1m_break=("has_1m_break_warn", lambda s: 100 * s.mean()),
        pct_scale_warn=("has_scale_warn", lambda s: 100 * s.mean()),
        pct_off_session=("has_off_session_warn", lambda s: 100 * s.mean()),
        pct_dup_warn=("has_dup_warn", lambda s: 100 * s.mean()),
    ).reset_index()
    pct_signal = explain_df.groupby("pct_break_bucket", observed=False).agg(
        files=("file", "size"),
        pct_1m_break=("has_1m_break_warn", lambda s: 100 * s.mean()),
        pct_scale_warn=("has_scale_warn", lambda s: 100 * s.mean()),
        pct_off_session=("has_off_session_warn", lambda s: 100 * s.mean()),
        pct_dup_warn=("has_dup_warn", lambda s: 100 * s.mean()),
    ).reset_index()
    return abs_signal, pct_signal


def plot_abs_signal(abs_signal: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.4))
    sns.barplot(data=abs_signal, x="abs_break_bucket", y="pct_1m_break", color="#2a9d8f", ax=axes[0, 0])
    axes[0, 0].set_title("% con confirmacion 1m por banda absoluta")
    axes[0, 0].set_xlabel("abs_break_bucket")
    axes[0, 0].set_ylabel("pct")
    axes[0, 0].tick_params(axis="x", rotation=45)

    sns.barplot(data=abs_signal, x="abs_break_bucket", y="pct_scale_warn", color="#f4a261", ax=axes[0, 1])
    axes[0, 1].set_title("% con scale mismatch por banda absoluta")
    axes[0, 1].set_xlabel("abs_break_bucket")
    axes[0, 1].set_ylabel("pct")
    axes[0, 1].tick_params(axis="x", rotation=45)

    sns.barplot(data=abs_signal, x="abs_break_bucket", y="pct_off_session", color="#6a4c93", ax=axes[1, 0])
    axes[1, 0].set_title("% con off-session por banda absoluta")
    axes[1, 0].set_xlabel("abs_break_bucket")
    axes[1, 0].set_ylabel("pct")
    axes[1, 0].tick_params(axis="x", rotation=45)

    sns.barplot(data=abs_signal, x="abs_break_bucket", y="pct_dup_warn", color="#d62828", ax=axes[1, 1])
    axes[1, 1].set_title("% con duplicados por banda absoluta")
    axes[1, 1].set_xlabel("abs_break_bucket")
    axes[1, 1].set_ylabel("pct")
    axes[1, 1].tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()


def build_side_signal(explain_df: pd.DataFrame) -> pd.DataFrame:
    return explain_df.groupby("break_side", observed=False).agg(
        files=("file", "size"),
        pct_1m_break=("has_1m_break_warn", lambda s: 100 * s.mean()),
        pct_scale_warn=("has_scale_warn", lambda s: 100 * s.mean()),
        pct_off_session=("has_off_session_warn", lambda s: 100 * s.mean()),
        pct_dup_warn=("has_dup_warn", lambda s: 100 * s.mean()),
        median_abs_break=("break_abs_max", "median"),
        p95_abs_break=("break_abs_max", lambda s: s.quantile(0.95)),
        median_pct_break=("break_pct_span_max", "median"),
        p95_pct_break=("break_pct_span_max", lambda s: s.quantile(0.95)),
    ).reset_index()


def plot_side_signal(side_signal: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.4))
    sns.barplot(data=side_signal, x="break_side", y="pct_1m_break", color="#2a9d8f", ax=axes[0, 0])
    axes[0, 0].set_title("% con confirmacion 1m por lado")
    axes[0, 0].set_xlabel("break_side")
    axes[0, 0].set_ylabel("pct")

    sns.barplot(data=side_signal, x="break_side", y="pct_scale_warn", color="#f4a261", ax=axes[0, 1])
    axes[0, 1].set_title("% con scale mismatch por lado")
    axes[0, 1].set_xlabel("break_side")
    axes[0, 1].set_ylabel("pct")

    sns.barplot(data=side_signal, x="break_side", y="pct_off_session", color="#6a4c93", ax=axes[1, 0])
    axes[1, 0].set_title("% con off-session por lado")
    axes[1, 0].set_xlabel("break_side")
    axes[1, 0].set_ylabel("pct")

    sns.barplot(data=side_signal, x="break_side", y="pct_dup_warn", color="#d62828", ax=axes[1, 1])
    axes[1, 1].set_title("% con duplicados por lado")
    axes[1, 1].set_xlabel("break_side")
    axes[1, 1].set_ylabel("pct")
    plt.tight_layout()
    plt.show()


def build_side_signal_view(side_signal: pd.DataFrame) -> pd.DataFrame:
    side_signal_view = side_signal[
        [
            "break_side", "files", "pct_1m_break", "pct_scale_warn", "pct_off_session",
            "pct_dup_warn", "median_abs_break", "p95_abs_break", "median_pct_break", "p95_pct_break",
        ]
    ].sort_values("files", ascending=False).copy()
    for col in [
        "pct_1m_break", "pct_scale_warn", "pct_off_session", "pct_dup_warn",
        "median_abs_break", "p95_abs_break", "median_pct_break", "p95_pct_break",
    ]:
        side_signal_view[col] = pd.to_numeric(side_signal_view[col], errors="coerce").round(3)
    return side_signal_view
