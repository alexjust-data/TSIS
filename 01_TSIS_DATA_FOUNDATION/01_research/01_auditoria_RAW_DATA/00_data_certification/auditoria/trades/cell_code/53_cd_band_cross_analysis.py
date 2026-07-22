from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def build_cross_band_tables(band_df: pd.DataFrame):
    cross_abs = band_df.groupby(["abs_break_bucket", "break_side"], dropna=False).size().rename("files").reset_index()
    cross_pct = band_df.groupby(["pct_break_bucket", "break_side"], dropna=False).size().rename("files").reset_index()
    return cross_abs, cross_pct


def plot_cross_band_tables(cross_abs: pd.DataFrame, cross_pct: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))
    sns.barplot(data=cross_abs, x="abs_break_bucket", y="files", hue="break_side", ax=axes[0])
    axes[0].set_title("Ruptura absoluta por bandas y lado")
    axes[0].set_xlabel("break_abs_max")
    axes[0].set_ylabel("files")
    axes[0].tick_params(axis="x", rotation=45)

    sns.barplot(data=cross_pct, x="pct_break_bucket", y="files", hue="break_side", ax=axes[1])
    axes[1].set_title("Ruptura relativa por bandas y lado")
    axes[1].set_xlabel("break_pct_span_max")
    axes[1].set_ylabel("files")
    axes[1].tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()


def build_cross_band_pct_tables(cross_abs: pd.DataFrame, cross_pct: pd.DataFrame):
    cross_abs_pct = cross_abs.copy()
    cross_abs_pct["pct_in_bucket"] = 100 * cross_abs_pct["files"] / cross_abs_pct.groupby("abs_break_bucket")["files"].transform("sum").clip(lower=1)
    cross_pct_pct = cross_pct.copy()
    cross_pct_pct["pct_in_bucket"] = 100 * cross_pct_pct["files"] / cross_pct_pct.groupby("pct_break_bucket")["files"].transform("sum").clip(lower=1)
    return cross_abs_pct, cross_pct_pct


def plot_cross_band_pct_tables(cross_abs_pct: pd.DataFrame, cross_pct_pct: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.8))
    sns.barplot(data=cross_abs_pct, x="abs_break_bucket", y="pct_in_bucket", hue="break_side", ax=axes[0])
    axes[0].set_title("% dentro de cada banda absoluta")
    axes[0].set_xlabel("break_abs_max")
    axes[0].set_ylabel("pct_in_bucket")
    axes[0].tick_params(axis="x", rotation=45)

    sns.barplot(data=cross_pct_pct, x="pct_break_bucket", y="pct_in_bucket", hue="break_side", ax=axes[1])
    axes[1].set_title("% dentro de cada banda relativa")
    axes[1].set_xlabel("break_pct_span_max")
    axes[1].set_ylabel("pct_in_bucket")
    axes[1].tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.show()
