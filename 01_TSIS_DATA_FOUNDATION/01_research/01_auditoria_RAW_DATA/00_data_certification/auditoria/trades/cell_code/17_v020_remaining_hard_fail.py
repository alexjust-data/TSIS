from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def flatten_token_series(series) -> list[str]:
    out: list[str] = []
    for value in series:
        if value is None:
            continue
        if isinstance(value, list):
            out.extend(str(x) for x in value if pd.notna(x))
        else:
            out.append(str(value))
    return out


def token_counts(series: pd.Series, col_name: str) -> pd.DataFrame:
    vals = pd.Series(flatten_token_series(series), dtype="object")
    if vals.empty:
        return pd.DataFrame(columns=[col_name, "files"])
    return vals.value_counts().rename_axis(col_name).reset_index(name="files")


def build_remaining_hard_fail_view(cur_df: pd.DataFrame) -> pd.DataFrame:
    hard_df = cur_df[cur_df["severity"] == "HARD_FAIL"].copy()

    numeric_cols = [
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
    ]
    for c in numeric_cols:
        if c in hard_df.columns:
            hard_df[c] = pd.to_numeric(hard_df[c], errors="coerce")

    return hard_df


def build_hard_issue_counts(hard_df: pd.DataFrame) -> pd.DataFrame:
    return token_counts(hard_df["issues_list"], "issue")


def build_hard_warn_counts(hard_df: pd.DataFrame) -> pd.DataFrame:
    return token_counts(hard_df["warns_list"], "warn")


def build_top_tickers_hard(hard_df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    return (
        hard_df.groupby("ticker")
        .size()
        .sort_values(ascending=False)
        .head(top_n)
        .rename_axis("ticker")
        .reset_index(name="hard_files")
    )


def plot_remaining_hard_fail_overview(
    hard_df: pd.DataFrame,
    hard_issue_counts: pd.DataFrame,
    hard_warn_counts: pd.DataFrame,
    top_tickers_hard: pd.DataFrame,
    top_n_issues: int = 15,
    top_n_warns: int = 15,
) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    sns.barplot(
        data=hard_issue_counts.head(top_n_issues),
        y="issue",
        x="files",
        color="#d62828",
        ax=ax,
    )
    ax.set_title("Top causas de HARD_FAIL en v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    sns.barplot(
        data=hard_warn_counts.head(top_n_warns),
        y="warn",
        x="files",
        color="#e9c46a",
        ax=ax,
    )
    ax.set_title("Warnings más frecuentes dentro de HARD_FAIL v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    sns.barplot(
        data=top_tickers_hard,
        y="ticker",
        x="hard_files",
        color="#264653",
        ax=ax,
    )
    ax.set_title("Top tickers por HARD_FAIL en v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()

    if all(
        c in hard_df.columns
        for c in [
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
        ]
    ):
        plot_scale = hard_df.dropna(
            subset=[
                "m.possible_price_scale_factor_vs_daily",
                "m.possible_price_scale_factor_vs_1m",
            ]
        ).copy()
        plot_scale = plot_scale[
            (plot_scale["m.possible_price_scale_factor_vs_daily"] > 0)
            & (plot_scale["m.possible_price_scale_factor_vs_1m"] > 0)
        ]

        fig, ax = plt.subplots(figsize=(6.2, 4.6))
        sns.scatterplot(
            data=plot_scale,
            x="m.possible_price_scale_factor_vs_daily",
            y="m.possible_price_scale_factor_vs_1m",
            alpha=0.7,
            s=22,
            ax=ax,
        )
        ax.axvline(1.0, ls="--", color="black", lw=1)
        ax.axhline(1.0, ls="--", color="black", lw=1)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title("Price scale factor dentro de HARD_FAIL v020", fontsize=SMALL_TITLE_SIZE)
        ax.set_xlabel("possible_price_scale_factor_vs_daily", fontsize=SMALL_LABEL_SIZE)
        ax.set_ylabel("possible_price_scale_factor_vs_1m", fontsize=SMALL_LABEL_SIZE)
        ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
        fig.tight_layout()
        plt.show()


def plot_hard_issue_ticker_heatmap(
    hard_df: pd.DataFrame,
    hard_issue_counts: pd.DataFrame,
    top_tickers_hard: pd.DataFrame,
    top_n_issues: int = 8,
    top_n_tickers: int = 12,
) -> None:
    hard_issue_ticker = hard_df[["ticker", "issues_list"]].copy()
    hard_issue_ticker["issue"] = hard_issue_ticker["issues_list"]
    hard_issue_ticker = hard_issue_ticker[["ticker", "issue"]].explode("issue").dropna()

    top_issue_names = hard_issue_counts["issue"].head(top_n_issues).tolist()
    top_ticker_names = top_tickers_hard["ticker"].head(top_n_tickers).tolist()

    heat = (
        hard_issue_ticker[
            hard_issue_ticker["issue"].isin(top_issue_names)
            & hard_issue_ticker["ticker"].isin(top_ticker_names)
        ]
        .groupby(["issue", "ticker"])
        .size()
        .unstack(fill_value=0)
    )

    if heat.empty:
        return

    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    sns.heatmap(heat, annot=True, fmt=".0f", cmap="Reds", annot_kws={"size": 7}, ax=ax)
    ax.set_title("Mapa de calor: top issue x top ticker dentro de HARD_FAIL v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("ticker", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("issue", fontsize=SMALL_LABEL_SIZE)
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def classify_hard_subtype(row: pd.Series) -> str:
    issues = set(str(x) for x in row.get("issues_list", []) if pd.notna(x))
    pf_daily = row.get("m.possible_price_scale_factor_vs_daily", np.nan)
    pf_1m = row.get("m.possible_price_scale_factor_vs_1m", np.nan)
    vol_daily = row.get("m.trade_volume_vs_daily_ratio", np.nan)
    vol_1m = row.get("m.trade_volume_vs_1m_ratio", np.nan)
    off_pct = row.get("m.off_session_trade_pct", np.nan)
    dup_pct = row.get("m.duplicate_excess_ratio_pct", np.nan)

    if {
        "missing_required_columns",
        "parquet_unreadable",
        "all_rows_invalid_after_parse",
    } & issues:
        return "structural_corruption"
    if {
        "timestamp_out_of_partition_day",
        "partition_vs_column_date_mismatch",
    } & issues:
        return "partition_time_break"
    if {
        "negative_or_zero_price_rows",
        "negative_or_zero_size_rows",
    } & issues:
        return "impossible_trade_values"
    if "duplicate_excess_ratio_gt_hard_cap" in issues:
        return "duplicate_hard_cap"
    if "trade_price_outside_daily_range" in issues:
        near_one_price = (
            pd.notna(pf_daily)
            and pd.notna(pf_1m)
            and 0.8 <= float(pf_daily) <= 1.2
            and 0.8 <= float(pf_1m) <= 1.2
        )
        extreme_volume = (
            (pd.notna(vol_daily) and float(vol_daily) > 10)
            or (pd.notna(vol_1m) and float(vol_1m) > 10)
        )
        session_heavy = pd.notna(off_pct) and float(off_pct) >= 40
        dup_heavy = pd.notna(dup_pct) and float(dup_pct) >= 3

        if near_one_price and extreme_volume:
            return "same_scale_extreme_volume_break"
        if near_one_price and session_heavy:
            return "same_scale_session_break"
        if near_one_price:
            return "same_scale_true_range_break"
        if dup_heavy:
            return "range_break_with_duplicate_pressure"
        return "unresolved_reference_break"
    return "other_hard_fail"


def build_hard_subtypes(hard_df: pd.DataFrame) -> pd.DataFrame:
    out = hard_df.copy()
    out["hard_subtype"] = out.apply(classify_hard_subtype, axis=1)
    return out


def build_hard_subtype_counts(hard_df: pd.DataFrame) -> pd.DataFrame:
    subtype_counts = (
        hard_df["hard_subtype"]
        .value_counts()
        .rename_axis("hard_subtype")
        .reset_index(name="files")
    )
    subtype_counts["pct"] = 100.0 * subtype_counts["files"] / max(len(hard_df), 1)
    return subtype_counts


def plot_hard_subtypes(subtype_counts: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    sns.barplot(data=subtype_counts, y="hard_subtype", x="files", color="#6d597a", ax=ax)
    ax.set_title("Subtipos operativos dentro de HARD_FAIL v020", fontsize=SMALL_TITLE_SIZE)
    ax.set_xlabel("files", fontsize=SMALL_LABEL_SIZE)
    ax.set_ylabel("")
    ax.tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    fig.tight_layout()
    plt.show()


def display_hard_subtype_examples(hard_df: pd.DataFrame, subtype_counts: pd.DataFrame, top_n: int = 20) -> None:
    summary_cols = [
        "ticker",
        "date",
        "hard_subtype",
        "issues_list",
        "warns_list",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.off_session_trade_pct",
        "m.duplicate_excess_ratio_pct",
        "file",
    ]
    summary_cols = [c for c in summary_cols if c in hard_df.columns]

    for subtype in subtype_counts["hard_subtype"].tolist():
        display(Markdown(f"### {subtype}"))
        display(
            hard_df[summary_cols][hard_df["hard_subtype"] == subtype]
            .sort_values(["ticker", "date"])
            .head(top_n)
        )


def display_hard_fail_interpretation() -> None:
    display(Markdown(
        """
## Cómo usar esta salida

- Si domina `same_scale_true_range_break`:
  la siguiente iteración debe estudiar mejor el rango real frente a `daily/1m`, no la escala.

- Si domina `same_scale_extreme_volume_break`:
  el siguiente refinado debe separar problema de precio y problema de volumen.

- Si domina `same_scale_session_break`:
  conviene introducir reglas por sesión o distinguir `RTH` vs `extended hours`.

- Si domina `unresolved_reference_break`:
  todavía queda una zona gris importante en referencias y hay que afinar el clasificador.

- Si dominan `structural_corruption`, `partition_time_break` o `impossible_trade_values`:
  esos deben seguir duros.
"""
    ))
