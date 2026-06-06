from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]
SEVERITY_PALETTE = {
    "PASS": "#2a9d8f",
    "SOFT_FAIL": "#e9c46a",
    "HARD_FAIL": "#e76f51",
}
SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def build_time_concentration_full(full_current: pd.DataFrame):
    month_mix_full = (
        full_current.groupby(["month", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    month_pivot_full = (
        month_mix_full.pivot(index="month", columns="severity", values="files")
        .fillna(0)
        .sort_index()
    )
    month_rate_full = month_pivot_full.div(month_pivot_full.sum(axis=1), axis=0) * 100.0

    year_mix_full = (
        full_current.groupby(["year", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    year_pivot_full = (
        year_mix_full.pivot(index="year", columns="severity", values="files")
        .fillna(0)
        .sort_index()
    )
    year_rate_full = year_pivot_full.div(year_pivot_full.sum(axis=1), axis=0) * 100.0
    return month_mix_full, month_pivot_full, month_rate_full, year_mix_full, year_pivot_full, year_rate_full


def plot_time_concentration_full(month_rate_full: pd.DataFrame, year_rate_full: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.8, 6.2), sharex=False)
    month_rate_full[[c for c in SEVERITY_ORDER if c in month_rate_full.columns]].plot(
        ax=axes[0],
        color=SEVERITY_PALETTE,
    )
    axes[0].set_title("Tasa mensual por severidad (%)", fontsize=SMALL_TITLE_SIZE)
    axes[0].set_ylabel("pct", fontsize=SMALL_LABEL_SIZE)
    axes[0].set_xlabel("month", fontsize=SMALL_LABEL_SIZE)
    axes[0].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)

    sns.heatmap(
        year_rate_full[[c for c in SEVERITY_ORDER if c in year_rate_full.columns]],
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        annot_kws={"size": 7},
        ax=axes[1],
    )
    axes[1].set_title("Tasa anual por severidad (%)", fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel("severity", fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel("year", fontsize=SMALL_LABEL_SIZE)
    axes[1].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()


def build_ticker_focus_full(full_current: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    ticker_mix_full = (
        full_current.groupby(["ticker", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    ticker_pivot_full = (
        ticker_mix_full.pivot(index="ticker", columns="severity", values="files")
        .fillna(0)
    )
    ticker_pivot_full["total"] = ticker_pivot_full.sum(axis=1)
    ticker_pivot_full["hard_fail_rate_pct"] = (
        100.0 * ticker_pivot_full.get("HARD_FAIL", 0) / ticker_pivot_full["total"].clip(lower=1)
    )
    return ticker_pivot_full.sort_values(["hard_fail_rate_pct", "total"], ascending=[False, False]).head(top_n)


def plot_ticker_focus_full(ticker_focus_full: pd.DataFrame) -> None:
    plot_cols = [c for c in SEVERITY_ORDER if c in ticker_focus_full.columns]
    ticker_focus_full[plot_cols].plot(
        kind="barh",
        stacked=True,
        figsize=(8.4, 6.4),
        color=SEVERITY_PALETTE,
    )
    plt.title("Top tickers por presion de HARD_FAIL en full", fontsize=SMALL_TITLE_SIZE)
    plt.xlabel("files", fontsize=SMALL_LABEL_SIZE)
    plt.ylabel("ticker", fontsize=SMALL_LABEL_SIZE)
    plt.xticks(fontsize=SMALL_TICK_SIZE)
    plt.yticks(fontsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()
