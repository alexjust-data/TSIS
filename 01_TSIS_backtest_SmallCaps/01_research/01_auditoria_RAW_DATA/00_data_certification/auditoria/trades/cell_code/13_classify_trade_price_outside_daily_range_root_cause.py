from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


FACTOR_TOL_PCT = 5.0
INVERSE_VOLUME_TOL = 0.25

SMALL_SCALE_FACTORS = [0.5, 0.25, 0.2, 0.1, 0.05, 0.01, 1 / 200]
LARGE_SCALE_FACTORS = [2.0, 4.0, 5.0, 10.0, 20.0, 100.0, 200.0]


def near_factor(x: Any, target: float, tol_pct: float = FACTOR_TOL_PCT) -> bool:
    if x is None or pd.isna(x) or target == 0:
        return False
    return abs(float(x) - float(target)) / abs(float(target)) * 100.0 <= tol_pct


def classify_scale_case(row: pd.Series) -> str:
    pf_daily = row.get("m.possible_price_scale_factor_vs_daily", np.nan)
    pf_1m = row.get("m.possible_price_scale_factor_vs_1m", np.nan)
    vol_daily = row.get("m.trade_volume_vs_daily_ratio", np.nan)

    price_scale_match_daily = any(near_factor(pf_daily, x) for x in SMALL_SCALE_FACTORS + LARGE_SCALE_FACTORS)
    price_scale_match_1m = any(near_factor(pf_1m, x) for x in SMALL_SCALE_FACTORS + LARGE_SCALE_FACTORS)
    price_scale_match = price_scale_match_daily and price_scale_match_1m

    inverse_volume_match = False
    if pd.notna(pf_daily) and pd.notna(vol_daily) and float(pf_daily) != 0:
        expected_inverse = 1.0 / float(pf_daily)
        inverse_volume_match = abs(float(vol_daily) - expected_inverse) / abs(expected_inverse) <= INVERSE_VOLUME_TOL

    if price_scale_match and inverse_volume_match:
        return "scale_mismatch_strong"

    if price_scale_match:
        return "scale_mismatch_probable"

    if pd.notna(pf_daily) and pd.notna(pf_1m):
        if 0.8 <= float(pf_daily) <= 1.2 and 0.8 <= float(pf_1m) <= 1.2:
            return "outside_range_without_detected_scale_shift"

    return "other_reference_break"


def classify_trade_price_outside_daily_range(events_df: pd.DataFrame) -> pd.DataFrame:
    focus = events_df.loc[
        events_df["issues_list"].map(lambda xs: "trade_price_outside_daily_range" in set(xs))
    ].copy()

    numeric_cols = [
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.possible_volume_scale_factor_vs_daily",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.trade_vwap_vs_daily_vw_diff_pct",
        "m.price_min",
        "m.price_max",
        "m.l",
        "m.h",
    ]
    for c in numeric_cols:
        if c in focus.columns:
            focus[c] = pd.to_numeric(focus[c], errors="coerce")

    focus["root_cause_bucket"] = focus.apply(classify_scale_case, axis=1)
    return focus


def build_bucket_counts(focus_df: pd.DataFrame) -> pd.DataFrame:
    bucket_counts = (
        focus_df["root_cause_bucket"]
        .value_counts(dropna=False)
        .rename_axis("bucket")
        .reset_index(name="files")
    )
    bucket_counts["pct"] = 100.0 * bucket_counts["files"] / max(len(focus_df), 1)
    return bucket_counts


def build_support_table(focus_df: pd.DataFrame) -> pd.DataFrame:
    support = (
        focus_df.groupby("root_cause_bucket")
        .agg(
            files=("file", "count"),
            tickers=("ticker", "nunique"),
            date_min=("date", "min"),
            date_max=("date", "max"),
            median_pf_daily=("m.possible_price_scale_factor_vs_daily", "median"),
            median_pf_1m=("m.possible_price_scale_factor_vs_1m", "median"),
            median_vol_daily=("m.trade_volume_vs_daily_ratio", "median"),
            median_vol_1m=("m.trade_volume_vs_1m_ratio", "median"),
        )
        .reset_index()
        .sort_values("files", ascending=False)
    )
    return support


def plot_bucket_counts(bucket_counts: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    sns.barplot(data=bucket_counts, y="bucket", x="files", color="#457b9d", ax=axes[0])
    axes[0].set_title("Clasificación de root cause para trade_price_outside_daily_range")
    axes[0].set_xlabel("files")
    axes[0].set_ylabel("")

    sns.barplot(data=bucket_counts, y="bucket", x="pct", color="#1d3557", ax=axes[1])
    axes[1].set_title("Peso relativo por bucket (%)")
    axes[1].set_xlabel("pct")
    axes[1].set_ylabel("")

    plt.tight_layout()
    plt.show()


def plot_scale_and_volume_scatter(focus_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    plot_df = focus_df.dropna(
        subset=["m.possible_price_scale_factor_vs_daily", "m.possible_price_scale_factor_vs_1m"]
    ).copy()
    plot_df = plot_df[
        (plot_df["m.possible_price_scale_factor_vs_daily"] > 0)
        & (plot_df["m.possible_price_scale_factor_vs_1m"] > 0)
    ]

    sns.scatterplot(
        data=plot_df,
        x="m.possible_price_scale_factor_vs_daily",
        y="m.possible_price_scale_factor_vs_1m",
        hue="root_cause_bucket",
        alpha=0.5,
        ax=axes[0],
    )
    axes[0].axvline(1.0, ls="--", color="black", lw=1)
    axes[0].axhline(1.0, ls="--", color="black", lw=1)
    for v in SMALL_SCALE_FACTORS + LARGE_SCALE_FACTORS:
        axes[0].axvline(v, ls=":", color="grey", lw=0.6, alpha=0.35)
        axes[0].axhline(v, ls=":", color="grey", lw=0.6, alpha=0.35)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_title("Price scale factor: daily vs 1m")
    axes[0].set_xlabel("possible_price_scale_factor_vs_daily")
    axes[0].set_ylabel("possible_price_scale_factor_vs_1m")

    vol_df = focus_df.dropna(subset=["m.trade_volume_vs_daily_ratio", "m.trade_volume_vs_1m_ratio"]).copy()
    vol_df = vol_df[
        (vol_df["m.trade_volume_vs_daily_ratio"] > 0)
        & (vol_df["m.trade_volume_vs_1m_ratio"] > 0)
    ]

    sns.scatterplot(
        data=vol_df,
        x="m.trade_volume_vs_daily_ratio",
        y="m.trade_volume_vs_1m_ratio",
        hue="root_cause_bucket",
        alpha=0.5,
        ax=axes[1],
    )
    axes[1].axvline(1.0, ls="--", color="black", lw=1)
    axes[1].axhline(1.0, ls="--", color="black", lw=1)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Volume ratio: trades vs references")
    axes[1].set_xlabel("trade_volume_vs_daily_ratio")
    axes[1].set_ylabel("trade_volume_vs_1m_ratio")

    plt.tight_layout()
    plt.show()


def display_examples_by_bucket(focus_df: pd.DataFrame, bucket_counts: pd.DataFrame, top_n: int = 15) -> None:
    examples = focus_df[
        [
            "root_cause_bucket",
            "ticker",
            "date",
            "severity",
            "batch_id",
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
            "m.trade_volume_vs_daily_ratio",
            "m.trade_volume_vs_1m_ratio",
            "m.price_min",
            "m.price_max",
            "m.l",
            "m.h",
            "file",
        ]
    ].sort_values(["root_cause_bucket", "ticker", "date"])

    for bucket in bucket_counts["bucket"].tolist():
        display(Markdown(f"### {bucket}"))
        display(examples[examples["root_cause_bucket"] == bucket].head(top_n))


def display_interpretation() -> None:
    display(Markdown(
        """
## Interpretación

- `scale_mismatch_strong`:
  `daily` y `1m` apuntan al mismo factor de escala y el volumen acompaña el inverso esperado.
  Estos casos son candidatos claros a relajación de severidad.

- `scale_mismatch_probable`:
  el precio ya sugiere desalineación fuerte, aunque el volumen no acompaña perfecto.
  También son candidatos plausibles a relajación.

- `outside_range_without_detected_scale_shift`:
  `trades` y referencias viven aproximadamente en la misma escala.
  Estos son los casos más defendibles como ruptura real frente al rango.

- `other_reference_break`:
  necesitan inspección adicional; aquí puede haber mezcla de causas.
"""
    ))
