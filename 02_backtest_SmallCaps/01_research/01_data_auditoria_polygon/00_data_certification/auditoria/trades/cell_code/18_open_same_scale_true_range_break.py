from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def classify_session(off_pct: float) -> str:
    if pd.isna(off_pct):
        return "unknown_session"
    if float(off_pct) < 5:
        return "mostly_RTH"
    if float(off_pct) < 25:
        return "RTH_with_some_extended"
    if float(off_pct) < 50:
        return "mixed_session"
    return "extended_hours_heavy"


def classify_gap_size(pct: float) -> str:
    if pd.isna(pct):
        return "unknown_gap"
    if float(pct) <= 1:
        return "tiny_gap_<=1pct"
    if float(pct) <= 5:
        return "small_gap_1_5pct"
    if float(pct) <= 20:
        return "medium_gap_5_20pct"
    return "large_gap_gt20pct"


def build_same_scale_true_range_break_view(hard_df: pd.DataFrame) -> pd.DataFrame:
    focus = hard_df[hard_df["hard_subtype"] == "same_scale_true_range_break"].copy()

    numeric_cols = [
        "m.off_session_trade_pct",
        "m.price_min",
        "m.price_max",
        "m.l",
        "m.h",
        "m.ohlcv_1m_low_min",
        "m.ohlcv_1m_high_max",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
    ]
    for c in numeric_cols:
        if c in focus.columns:
            focus[c] = pd.to_numeric(focus[c], errors="coerce")

    focus["session_bucket"] = focus["m.off_session_trade_pct"].map(classify_session)
    focus["breaks_1m"] = focus["warns_list"].map(lambda xs: "trade_price_outside_1m_range" in set(xs))
    focus["range_break_mode"] = np.where(
        focus["breaks_1m"],
        "breaks_daily_and_1m",
        "breaks_daily_only",
    )

    focus["outside_below_abs"] = (
        pd.to_numeric(focus["m.l"], errors="coerce")
        - pd.to_numeric(focus["m.price_min"], errors="coerce")
    ).clip(lower=0)

    focus["outside_above_abs"] = (
        pd.to_numeric(focus["m.price_max"], errors="coerce")
        - pd.to_numeric(focus["m.h"], errors="coerce")
    ).clip(lower=0)

    focus["daily_span"] = (
        pd.to_numeric(focus["m.h"], errors="coerce")
        - pd.to_numeric(focus["m.l"], errors="coerce")
    )

    focus["outside_abs_max"] = focus[["outside_below_abs", "outside_above_abs"]].max(axis=1)
    focus["outside_pct_of_daily_span"] = (
        100.0 * focus["outside_abs_max"] / focus["daily_span"].replace(0, np.nan)
    )
    focus["gap_bucket"] = focus["outside_pct_of_daily_span"].map(classify_gap_size)
    return focus


def _build_count_table(df: pd.DataFrame, col_name: str, out_name: str) -> pd.DataFrame:
    out = (
        df[col_name]
        .value_counts(dropna=False)
        .rename_axis(col_name)
        .reset_index(name="files")
    )
    out["pct"] = 100.0 * out["files"] / max(len(df), 1)
    return out.rename(columns={col_name: out_name})


def build_session_counts(focus_df: pd.DataFrame) -> pd.DataFrame:
    return _build_count_table(focus_df, "session_bucket", "session_bucket")


def build_break_mode_counts(focus_df: pd.DataFrame) -> pd.DataFrame:
    return _build_count_table(focus_df, "range_break_mode", "range_break_mode")


def build_gap_counts(focus_df: pd.DataFrame) -> pd.DataFrame:
    return _build_count_table(focus_df, "gap_bucket", "gap_bucket")


def plot_same_scale_true_range_break_overview(
    focus_df: pd.DataFrame,
    session_counts: pd.DataFrame,
    break_mode_counts: pd.DataFrame,
    gap_counts: pd.DataFrame,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    sns.barplot(data=session_counts, y="session_bucket", x="files", color="#457b9d", ax=ax)
    ax.set_title("same_scale_true_range_break por sesión", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 2.8))
    sns.barplot(data=break_mode_counts, y="range_break_mode", x="files", color="#e76f51", ax=ax)
    ax.set_title("same_scale_true_range_break: rompe solo daily vs daily+1m", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    sns.barplot(data=gap_counts, y="gap_bucket", x="files", color="#2a9d8f", ax=ax)
    ax.set_title("same_scale_true_range_break por magnitud de gap", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    sns.boxplot(data=focus_df, x="range_break_mode", y="outside_pct_of_daily_span", ax=ax)
    ax.set_yscale("log")
    ax.set_title("Magnitud del gap por tipo de rotura", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("")
    ax.set_ylabel("outside_pct_of_daily_span (log)", fontsize=SMALL_LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    sns.boxplot(data=focus_df, x="session_bucket", y="outside_pct_of_daily_span", ax=ax)
    ax.set_yscale("log")
    ax.set_title("Magnitud del gap por sesión", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("")
    ax.set_ylabel("outside_pct_of_daily_span (log)", fontsize=SMALL_LABEL_SIZE)
    ax.tick_params(axis="x", labelrotation=20, labelsize=SMALL_TICK_SIZE)
    ax.tick_params(axis="y", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def plot_session_gap_heatmap(focus_df: pd.DataFrame) -> None:
    heat = (
        focus_df.groupby(["session_bucket", "gap_bucket"])
        .size()
        .unstack(fill_value=0)
    )
    if heat.empty:
        return

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="YlGnBu", annot_kws={"size": 7}, ax=ax)
    ax.set_title("Heatmap sesión x magnitud de gap", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("gap_bucket", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("session_bucket", fontsize=SMALL_LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def display_same_scale_true_range_examples(focus_df: pd.DataFrame, top_n: int = 10) -> None:
    show_cols = [
        "ticker",
        "date",
        "session_bucket",
        "range_break_mode",
        "gap_bucket",
        "m.off_session_trade_pct",
        "outside_abs_max",
        "outside_pct_of_daily_span",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "issues_list",
        "warns_list",
        "file",
    ]
    show_cols = [c for c in show_cols if c in focus_df.columns]

    display(Markdown("### Ejemplos de `breaks_daily_only`"))
    display(
        focus_df[show_cols][focus_df["range_break_mode"] == "breaks_daily_only"]
        .sort_values(["outside_pct_of_daily_span", "ticker", "date"], ascending=[False, True, True])
        .head(top_n)
    )

    display(Markdown("### Ejemplos de `breaks_daily_and_1m`"))
    display(
        focus_df[show_cols][focus_df["range_break_mode"] == "breaks_daily_and_1m"]
        .sort_values(["outside_pct_of_daily_span", "ticker", "date"], ascending=[False, True, True])
        .head(top_n)
    )


def display_same_scale_true_range_interpretation() -> None:
    display(Markdown(
        """
## Cómo leer esta celda

- Si domina `breaks_daily_only`:
  `daily` está pesando demasiado y conviene rebajar su dureza cuando `1m` no acompaña.

- Si domina `breaks_daily_and_1m`:
  la rotura es más sólida y tiene sentido mantenerla dura.

- Si dominan `tiny_gap_<=1pct` o `small_gap_1_5pct`:
  conviene subir tolerancias o introducir una zona gris `SOFT_FAIL`.

- Si domina `extended_hours_heavy` o `mixed_session`:
  conviene separar reglas por sesión antes de seguir afinando.

- Si los gaps grandes concentran `breaks_daily_and_1m`:
  esos son los mejores candidatos para seguir como `HARD_FAIL`.
"""
    ))
