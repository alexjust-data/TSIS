from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def build_break_side_scatter_view(daily_break_full: pd.DataFrame) -> pd.DataFrame:
    return (
        daily_break_full[
            [
                "ticker", "date", "break_side", "break_below_abs", "break_above_abs",
                "break_below_pct_span", "break_above_pct_span", "break_pct_span_max",
            ]
        ]
        .replace([np.inf, -np.inf], np.nan)
        .dropna(subset=["break_below_abs", "break_above_abs"])
        .copy()
    )


def plot_break_side_scatter(plot_df: pd.DataFrame) -> None:
    plot_sample = plot_df.sample(min(50_000, len(plot_df)), random_state=7).copy()
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    sns.scatterplot(
        data=plot_sample,
        x="break_below_abs",
        y="break_above_abs",
        hue="break_side",
        alpha=0.35,
        palette={"below_only": "#457b9d", "above_only": "#d62828", "both": "#6a4c93"},
        ax=axes[0],
    )
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_title("Corte por abajo vs corte por arriba")
    axes[0].set_xlabel("break_below_abs")
    axes[0].set_ylabel("break_above_abs")

    hb = axes[1].hexbin(
        plot_df["break_below_abs"].clip(lower=1e-9),
        plot_df["break_above_abs"].clip(lower=1e-9),
        gridsize=60,
        bins="log",
        cmap="YlOrRd",
        mincnt=1,
    )
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Densidad de ruptura abajo/arriba")
    axes[1].set_xlabel("break_below_abs")
    axes[1].set_ylabel("break_above_abs")
    fig.colorbar(hb, ax=axes[1], label="log10(count)")
    plt.tight_layout()
    plt.show()


def build_break_extreme_view(plot_df: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    return plot_df.sort_values(
        ["break_pct_span_max", "break_below_abs", "break_above_abs"],
        ascending=[False, False, False],
    ).head(top_n)


def build_break_visual_summary(daily_break_full: pd.DataFrame):
    viz_df = daily_break_full.copy()
    for c in [
        "break_below_abs", "break_above_abs", "break_below_pct_span",
        "break_above_pct_span", "break_pct_span_max",
    ]:
        viz_df[c] = pd.to_numeric(viz_df[c], errors="coerce")

    cap_below = viz_df["break_below_abs"].quantile(0.99)
    cap_above = viz_df["break_above_abs"].quantile(0.99)
    cap_pct = viz_df["break_pct_span_max"].quantile(0.99)

    viz_df["break_below_abs_cap"] = viz_df["break_below_abs"].clip(upper=cap_below)
    viz_df["break_above_abs_cap"] = viz_df["break_above_abs"].clip(upper=cap_above)
    viz_df["break_pct_span_max_cap"] = viz_df["break_pct_span_max"].clip(upper=cap_pct)

    summary_breaks = pd.DataFrame([{
        "files": len(viz_df),
        "p50_below_abs": viz_df["break_below_abs"].median(),
        "p90_below_abs": viz_df["break_below_abs"].quantile(0.90),
        "p95_below_abs": viz_df["break_below_abs"].quantile(0.95),
        "p99_below_abs": viz_df["break_below_abs"].quantile(0.99),
        "p50_above_abs": viz_df["break_above_abs"].median(),
        "p90_above_abs": viz_df["break_above_abs"].quantile(0.90),
        "p95_above_abs": viz_df["break_above_abs"].quantile(0.95),
        "p99_above_abs": viz_df["break_above_abs"].quantile(0.99),
        "p50_pct_span": viz_df["break_pct_span_max"].median(),
        "p90_pct_span": viz_df["break_pct_span_max"].quantile(0.90),
        "p95_pct_span": viz_df["break_pct_span_max"].quantile(0.95),
        "p99_pct_span": viz_df["break_pct_span_max"].quantile(0.99),
    }])
    return viz_df, summary_breaks


def plot_break_visual_summary(viz_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(8.8, 6.4))
    sns.histplot(viz_df["break_below_abs_cap"], bins=80, color="#457b9d", ax=axes[0, 0])
    axes[0, 0].set_title("Corte por abajo capado al p99")
    axes[0, 0].set_xlabel("break_below_abs (cap p99)")
    axes[0, 0].set_ylabel("files")

    sns.histplot(viz_df["break_above_abs_cap"], bins=80, color="#d62828", ax=axes[0, 1])
    axes[0, 1].set_title("Corte por arriba capado al p99")
    axes[0, 1].set_xlabel("break_above_abs (cap p99)")
    axes[0, 1].set_ylabel("files")

    sns.histplot(viz_df["break_pct_span_max_cap"], bins=80, color="#2a9d8f", ax=axes[1, 0])
    axes[1, 0].set_title("Ruptura relativa al rango daily capada al p99")
    axes[1, 0].set_xlabel("break_pct_span_max (cap p99)")
    axes[1, 0].set_ylabel("files")

    sns.boxplot(data=viz_df[["break_below_abs_cap", "break_above_abs_cap", "break_pct_span_max_cap"]], orient="h", ax=axes[1, 1])
    axes[1, 1].set_title("Distribuciones resumidas")
    axes[1, 1].set_xlabel("valor")
    plt.tight_layout()
    plt.show()


def build_year_break_views(daily_break_full: pd.DataFrame):
    tmp = daily_break_full.copy()
    tmp["year"] = pd.to_datetime(tmp["date"]).dt.year
    year_side = tmp.groupby(["year", "break_side"]).size().rename("files").reset_index()
    year_mag = tmp.groupby("year", as_index=False).agg(
        files=("file", "size"),
        median_break_pct_span_max=("break_pct_span_max", "median"),
        p95_break_pct_span_max=("break_pct_span_max", lambda s: s.quantile(0.95)),
    )
    return tmp, year_side, year_mag


def plot_year_break_views(year_side: pd.DataFrame, year_mag: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.4, 6.4), sharex=True)
    sns.barplot(data=year_side, x="year", y="files", hue="break_side", ax=axes[0])
    axes[0].set_title("Ruptura por a?o y lado")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("files")

    axes[1].plot(year_mag["year"], year_mag["median_break_pct_span_max"], marker="o", label="median")
    axes[1].plot(year_mag["year"], year_mag["p95_break_pct_span_max"], marker="o", label="p95")
    axes[1].set_title("Severidad anual de la ruptura")
    axes[1].set_xlabel("year")
    axes[1].set_ylabel("pct of daily span")
    axes[1].legend()
    plt.tight_layout()
    plt.show()
