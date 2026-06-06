from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


EXTREME_VOLUME_THRESHOLD = 10.0
MODERATE_VOLUME_LOW = 2.0
MODERATE_VOLUME_HIGH = 10.0
OFF_SESSION_HEAVY_PCT = 40.0
DUP_HEAVY_PCT = 3.0
OUTSIDE_SMALL_PCT = 5.0
OUTSIDE_LARGE_PCT = 25.0


def classify_other_subtype(row: pd.Series) -> str:
    pf_daily = row.get("m.possible_price_scale_factor_vs_daily", np.nan)
    pf_1m = row.get("m.possible_price_scale_factor_vs_1m", np.nan)
    vol_daily = row.get("m.trade_volume_vs_daily_ratio", np.nan)
    vol_1m = row.get("m.trade_volume_vs_1m_ratio", np.nan)
    off_pct = row.get("m.off_session_trade_pct", np.nan)
    dup_pct = row.get("m.duplicate_excess_ratio_pct", np.nan)
    outside_pct = row.get("outside_pct_of_daily_span", np.nan)

    near_one_price = (
        pd.notna(pf_daily)
        and pd.notna(pf_1m)
        and (0.8 <= float(pf_daily) <= 1.2)
        and (0.8 <= float(pf_1m) <= 1.2)
    )
    extreme_volume = (
        (pd.notna(vol_daily) and float(vol_daily) > EXTREME_VOLUME_THRESHOLD)
        or (pd.notna(vol_1m) and float(vol_1m) > EXTREME_VOLUME_THRESHOLD)
    )
    moderate_volume = (
        (pd.notna(vol_daily) and MODERATE_VOLUME_LOW <= float(vol_daily) <= MODERATE_VOLUME_HIGH)
        or (pd.notna(vol_1m) and MODERATE_VOLUME_LOW <= float(vol_1m) <= MODERATE_VOLUME_HIGH)
    )
    off_session_heavy = pd.notna(off_pct) and float(off_pct) >= OFF_SESSION_HEAVY_PCT
    dup_heavy = pd.notna(dup_pct) and float(dup_pct) >= DUP_HEAVY_PCT
    outside_small = pd.notna(outside_pct) and float(outside_pct) <= OUTSIDE_SMALL_PCT
    outside_large = pd.notna(outside_pct) and float(outside_pct) > OUTSIDE_LARGE_PCT

    if near_one_price and extreme_volume:
        return "same_scale_extreme_volume_break"
    if near_one_price and moderate_volume:
        return "same_scale_moderate_volume_break"
    if near_one_price and outside_small:
        return "same_scale_small_range_break"
    if near_one_price and outside_large:
        return "same_scale_large_range_break"
    if off_session_heavy and not extreme_volume:
        return "session_structure_break"
    if dup_heavy:
        return "duplicate_pressure_break"
    return "mixed_other_break"


def build_other_reference_break_subtypes(focus_df: pd.DataFrame) -> pd.DataFrame:
    other = focus_df.loc[focus_df["root_cause_bucket"] == "other_reference_break"].copy()

    for c in [
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.trade_vwap_vs_daily_vw_diff_pct",
        "m.off_session_trade_pct",
        "m.duplicate_excess_ratio_pct",
        "m.price_min",
        "m.price_max",
        "m.l",
        "m.h",
    ]:
        if c in other.columns:
            other[c] = pd.to_numeric(other[c], errors="coerce")

    other["outside_below_abs"] = (
        pd.to_numeric(other["m.l"], errors="coerce")
        - pd.to_numeric(other["m.price_min"], errors="coerce")
    ).clip(lower=0)

    other["outside_above_abs"] = (
        pd.to_numeric(other["m.price_max"], errors="coerce")
        - pd.to_numeric(other["m.h"], errors="coerce")
    ).clip(lower=0)

    other["daily_span"] = (
        pd.to_numeric(other["m.h"], errors="coerce")
        - pd.to_numeric(other["m.l"], errors="coerce")
    )

    other["outside_abs_max"] = other[["outside_below_abs", "outside_above_abs"]].max(axis=1)
    other["outside_pct_of_daily_span"] = (
        100 * other["outside_abs_max"] / other["daily_span"].replace(0, np.nan)
    )

    other["other_subtype"] = other.apply(classify_other_subtype, axis=1)
    return other


def build_other_subtype_counts(other_df: pd.DataFrame, focus_df: pd.DataFrame | None = None) -> pd.DataFrame:
    sub_counts = (
        other_df["other_subtype"]
        .value_counts(dropna=False)
        .rename_axis("other_subtype")
        .reset_index(name="files")
    )
    sub_counts["pct_within_other"] = 100.0 * sub_counts["files"] / max(len(other_df), 1)
    if focus_df is not None:
        sub_counts["pct_within_all_daily_range_hard"] = 100.0 * sub_counts["files"] / max(len(focus_df), 1)
    return sub_counts


def plot_other_subtype_breakdown(other_df: pd.DataFrame, sub_counts: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    sns.barplot(data=sub_counts, y="other_subtype", x="files", color="#6d597a", ax=axes[0])
    axes[0].set_title("Subtipos dentro de other_reference_break")
    axes[0].set_xlabel("files")
    axes[0].set_ylabel("")

    sns.barplot(data=sub_counts, y="other_subtype", x="pct_within_other", color="#457b9d", ax=axes[1])
    axes[1].set_title("Peso dentro de other_reference_break (%)")
    axes[1].set_xlabel("pct")
    axes[1].set_ylabel("")
    plt.tight_layout()
    plt.show()

    fig, axes = plt.subplots(2, 2, figsize=(18, 14))

    price_df = other_df.dropna(subset=["m.possible_price_scale_factor_vs_daily", "m.possible_price_scale_factor_vs_1m"]).copy()
    price_df = price_df[
        (price_df["m.possible_price_scale_factor_vs_daily"] > 0)
        & (price_df["m.possible_price_scale_factor_vs_1m"] > 0)
    ]
    sns.scatterplot(
        data=price_df,
        x="m.possible_price_scale_factor_vs_daily",
        y="m.possible_price_scale_factor_vs_1m",
        hue="other_subtype",
        alpha=0.5,
        ax=axes[0, 0],
    )
    axes[0, 0].axvline(1.0, ls="--", color="black", lw=1)
    axes[0, 0].axhline(1.0, ls="--", color="black", lw=1)
    axes[0, 0].set_xscale("log")
    axes[0, 0].set_yscale("log")
    axes[0, 0].set_title("Price scale factor dentro de other_reference_break")

    vol_df = other_df.dropna(subset=["m.trade_volume_vs_daily_ratio", "m.trade_volume_vs_1m_ratio"]).copy()
    vol_df = vol_df[
        (vol_df["m.trade_volume_vs_daily_ratio"] > 0)
        & (vol_df["m.trade_volume_vs_1m_ratio"] > 0)
    ]
    sns.scatterplot(
        data=vol_df,
        x="m.trade_volume_vs_daily_ratio",
        y="m.trade_volume_vs_1m_ratio",
        hue="other_subtype",
        alpha=0.5,
        ax=axes[0, 1],
    )
    axes[0, 1].axvline(1.0, ls="--", color="black", lw=1)
    axes[0, 1].axhline(1.0, ls="--", color="black", lw=1)
    axes[0, 1].set_xscale("log")
    axes[0, 1].set_yscale("log")
    axes[0, 1].set_title("Volume ratio dentro de other_reference_break")

    sns.boxplot(
        data=other_df,
        x="other_subtype",
        y="outside_pct_of_daily_span",
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("outside_pct_of_daily_span por subtipo")
    axes[1, 0].tick_params(axis="x", rotation=45)

    sns.boxplot(
        data=other_df,
        x="other_subtype",
        y="m.off_session_trade_pct",
        ax=axes[1, 1],
    )
    axes[1, 1].set_title("off_session_trade_pct por subtipo")
    axes[1, 1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.show()


def build_other_subtype_summary(other_df: pd.DataFrame) -> pd.DataFrame:
    return (
        other_df.groupby("other_subtype")
        .agg(
            files=("file", "count"),
            tickers=("ticker", "nunique"),
            median_pf_daily=("m.possible_price_scale_factor_vs_daily", "median"),
            median_pf_1m=("m.possible_price_scale_factor_vs_1m", "median"),
            median_vol_daily=("m.trade_volume_vs_daily_ratio", "median"),
            median_vol_1m=("m.trade_volume_vs_1m_ratio", "median"),
            median_outside_pct=("outside_pct_of_daily_span", "median"),
            median_off_session_pct=("m.off_session_trade_pct", "median"),
            median_dup_pct=("m.duplicate_excess_ratio_pct", "median"),
        )
        .reset_index()
        .sort_values("files", ascending=False)
    )


def display_other_examples_by_subtype(other_df: pd.DataFrame, sub_counts: pd.DataFrame, top_n: int = 20) -> None:
    example_cols = [
        "other_subtype",
        "ticker",
        "date",
        "batch_id",
        "severity",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "outside_pct_of_daily_span",
        "m.off_session_trade_pct",
        "m.duplicate_excess_ratio_pct",
        "file",
    ]

    for subtype in sub_counts["other_subtype"].tolist():
        display(Markdown(f"### {subtype}"))
        display(
            other_df.loc[other_df["other_subtype"] == subtype, example_cols]
            .sort_values(["ticker", "date"])
            .head(top_n)
        )


def display_other_interpretation() -> None:
    display(Markdown(
        """
## Cómo leer esta celda

- Si domina `same_scale_extreme_volume_break`:
  el precio no parece escalado, pero el volumen frente a referencias está totalmente roto.

- Si dominan `same_scale_small_range_break` o `same_scale_large_range_break`:
  el problema parece realmente de rango y no de escala.

- Si aparece mucho `session_structure_break`:
  `daily` y `1m` pueden no estar capturando la misma sesión que `trades`.

- Si domina `mixed_other_break`:
  hace falta un clasificador más fino o revisar referencias concretas.
"""
    ))
