from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]


def build_time_concentration_cd(df: pd.DataFrame):
    month_mix = (
        df.groupby(["month", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    month_pivot = month_mix.pivot(index="month", columns="severity", values="files").fillna(0).reindex(columns=SEVERITY_ORDER, fill_value=0)
    month_pivot["total"] = month_pivot.sum(axis=1)
    month_rate = month_pivot.assign(
        hard_fail_rate_pct=month_pivot["HARD_FAIL"] / month_pivot["total"].replace(0, pd.NA) * 100.0,
        soft_fail_rate_pct=month_pivot["SOFT_FAIL"] / month_pivot["total"].replace(0, pd.NA) * 100.0,
    ).reset_index()

    year_mix = (
        df.groupby(["year", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    year_pivot = year_mix.pivot(index="year", columns="severity", values="files").fillna(0).reindex(columns=SEVERITY_ORDER, fill_value=0)
    year_pivot["total"] = year_pivot.sum(axis=1)
    year_rate = year_pivot.assign(
        hard_fail_rate_pct=year_pivot["HARD_FAIL"] / year_pivot["total"].replace(0, pd.NA) * 100.0,
        soft_fail_rate_pct=year_pivot["SOFT_FAIL"] / year_pivot["total"].replace(0, pd.NA) * 100.0,
    ).reset_index()
    return month_mix, month_pivot.reset_index(), month_rate, year_mix, year_pivot.reset_index(), year_rate


def build_ticker_concentration_cd(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    pivot = (
        df.groupby(["ticker", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
        .pivot(index="ticker", columns="severity", values="files")
        .fillna(0)
        .reindex(columns=SEVERITY_ORDER, fill_value=0)
    )
    pivot["total"] = pivot.sum(axis=1)
    pivot["hard_fail_rate_pct"] = pivot["HARD_FAIL"] / pivot["total"].replace(0, pd.NA) * 100.0
    pivot["soft_fail_rate_pct"] = pivot["SOFT_FAIL"] / pivot["total"].replace(0, pd.NA) * 100.0
    return pivot.sort_values(["HARD_FAIL", "SOFT_FAIL", "total"], ascending=False).head(top_n).reset_index()


def plot_time_concentration_cd(month_rate: pd.DataFrame, year_rate: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(18, 9), sharex=False)
    axes[0].plot(month_rate["month"], month_rate["hard_fail_rate_pct"], label="hard_fail_rate_pct", color="#e76f51")
    axes[0].plot(month_rate["month"], month_rate["soft_fail_rate_pct"], label="soft_fail_rate_pct", color="#e9c46a")
    axes[0].set_title("Concentracion mensual")
    axes[0].tick_params(axis="x", rotation=90)
    axes[0].legend()

    axes[1].plot(year_rate["year"], year_rate["hard_fail_rate_pct"], label="hard_fail_rate_pct", color="#e76f51")
    axes[1].plot(year_rate["year"], year_rate["soft_fail_rate_pct"], label="soft_fail_rate_pct", color="#e9c46a")
    axes[1].set_title("Concentracion anual")
    axes[1].legend()
    fig.tight_layout()

