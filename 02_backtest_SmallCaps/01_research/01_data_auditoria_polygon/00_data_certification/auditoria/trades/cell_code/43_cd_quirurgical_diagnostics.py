from __future__ import annotations

import random

import matplotlib.pyplot as plt
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns


SEVERITY_PALETTE = {
    "PASS": "#2a9d8f",
    "SOFT_FAIL": "#e9c46a",
    "HARD_FAIL": "#e76f51",
}
SMALL_TITLE_SIZE = 11
SMALL_LABEL_SIZE = 9
SMALL_TICK_SIZE = 8


def build_sample_plot_full(full_current: pd.DataFrame, max_n: int = 100_000, random_state: int = 7):
    sample_plot_full = full_current.sample(n=min(max_n, len(full_current)), random_state=random_state).copy()
    scale_mask_full = sample_plot_full["warns_list"].map(
        lambda xs: bool(
            {
                "possible_corporate_action_scale_mismatch",
                "possible_corporate_action_scale_mismatch_vs_1m",
                "possible_corporate_action_scale_mismatch_vs_daily",
            } & set(xs)
        )
    )
    scale_df_full = sample_plot_full.loc[scale_mask_full].copy()
    dup_df_full = sample_plot_full.copy()
    return sample_plot_full, scale_df_full, dup_df_full


def plot_scale_and_dup_diagnostics(scale_df_full: pd.DataFrame, dup_df_full: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))

    plot_df = scale_df_full.dropna(
        subset=[
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
        ]
    ).copy()
    sns.scatterplot(
        data=plot_df,
        x="m.possible_price_scale_factor_vs_daily",
        y="m.possible_price_scale_factor_vs_1m",
        hue="severity",
        alpha=0.5,
        palette=SEVERITY_PALETTE,
        ax=axes[0],
    )
    axes[0].axvline(0.1, ls="--", color="black", lw=1)
    axes[0].axvline(10.0, ls="--", color="black", lw=1)
    axes[0].axhline(0.1, ls="--", color="black", lw=1)
    axes[0].axhline(10.0, ls="--", color="black", lw=1)
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_title("Factor de escala precio: daily vs 1m", fontsize=SMALL_TITLE_SIZE)
    axes[0].set_xlabel("m.possible_price_scale_factor_vs_daily", fontsize=SMALL_LABEL_SIZE)
    axes[0].set_ylabel("m.possible_price_scale_factor_vs_1m", fontsize=SMALL_LABEL_SIZE)
    axes[0].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)

    sns.boxplot(
        data=dup_df_full,
        x="severity",
        y="m.duplicate_excess_ratio_pct",
        hue="severity",
        palette=SEVERITY_PALETTE,
        dodge=False,
        ax=axes[1],
    )
    if axes[1].legend_ is not None:
        axes[1].legend_.remove()
    axes[1].set_title("Distribucion de duplicate_excess_ratio_pct", fontsize=SMALL_TITLE_SIZE)
    axes[1].set_xlabel("", fontsize=SMALL_LABEL_SIZE)
    axes[1].set_ylabel("pct", fontsize=SMALL_LABEL_SIZE)
    axes[1].tick_params(axis="both", labelsize=SMALL_TICK_SIZE)
    plt.tight_layout()
    plt.show()


def build_dup_outlier_view(dup_df_full: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    cols = [
        "ticker",
        "date",
        "severity",
        "m.duplicate_excess_ratio_pct",
        "m.max_trades_same_timestamp",
        "file",
    ]
    return (
        dup_df_full[cols]
        .sort_values(
            ["m.duplicate_excess_ratio_pct", "m.max_trades_same_timestamp"],
            ascending=[False, False],
        )
        .head(top_n)
    )


def build_sample_plot_full_chunked(current_parquet: str, mod00: dict, max_n: int = 100_000, random_state: int = 7):
    pf = pq.ParquetFile(current_parquet)
    rng = random.Random(random_state)
    sample_rows: list[dict] = []
    seen = 0

    for row_group_idx in range(pf.num_row_groups):
        chunk = pf.read_row_group(
            row_group_idx,
            columns=["severity", "warns", "metrics_json", "ticker", "date", "file"],
        ).to_pandas()
        if chunk.empty:
            continue

        for row in chunk.to_dict("records"):
            seen += 1
            if len(sample_rows) < max_n:
                sample_rows.append(row)
                continue
            replace_idx = rng.randint(0, seen - 1)
            if replace_idx < max_n:
                sample_rows[replace_idx] = row

    sample_plot_full = mod00["normalize_event_like_df"](pd.DataFrame(sample_rows))
    for col in [
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.duplicate_excess_ratio_pct",
        "m.max_trades_same_timestamp",
    ]:
        if col in sample_plot_full.columns:
            sample_plot_full[col] = pd.to_numeric(sample_plot_full[col], errors="coerce")

    return build_sample_plot_full(sample_plot_full, max_n=max_n, random_state=random_state)
