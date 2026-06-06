from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


def build_reclassified_metric_view(
    cmp_df: pd.DataFrame,
    cur_right: pd.DataFrame,
    left_label: str,
    right_label: str,
    from_severity: str = "HARD_FAIL",
    to_severity: str = "SOFT_FAIL",
) -> pd.DataFrame:
    transition = f"{from_severity} -> {to_severity}"
    metric_cols = [c for c in cur_right.columns if c.startswith("m.")]

    reclassified = (
        cmp_df[cmp_df["transition"] == transition]
        .copy()
        .merge(
            cur_right[["file_key", "ticker", "date"] + metric_cols],
            on=["file_key", "ticker", "date"],
            how="left",
            suffixes=("", "_dup"),
        )
    )

    reclassified = reclassified.loc[:, ~reclassified.columns.duplicated()].copy()

    numeric_cols = [
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
    ]
    for c in numeric_cols:
        if c in reclassified.columns:
            reclassified[c] = pd.to_numeric(reclassified[c], errors="coerce")

    reclassified.attrs["left_label"] = left_label
    reclassified.attrs["right_label"] = right_label
    reclassified.attrs["transition"] = transition
    return reclassified


def plot_reclassified_scale_granularity(
    reclassified_df: pd.DataFrame,
    top_n_tickers: int = 20,
    top_n_heatmap_tickers: int = 12,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))

    if all(
        c in reclassified_df.columns
        for c in [
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
        ]
    ):
        plot1 = reclassified_df.dropna(
            subset=[
                "m.possible_price_scale_factor_vs_daily",
                "m.possible_price_scale_factor_vs_1m",
            ]
        ).copy()
        plot1 = plot1[
            (plot1["m.possible_price_scale_factor_vs_daily"] > 0)
            & (plot1["m.possible_price_scale_factor_vs_1m"] > 0)
        ]

        sns.scatterplot(
            data=plot1,
            x="m.possible_price_scale_factor_vs_daily",
            y="m.possible_price_scale_factor_vs_1m",
            hue="m.scale_mismatch_confidence" if "m.scale_mismatch_confidence" in plot1.columns else None,
            ax=axes[0, 0],
        )
        axes[0, 0].axvline(1.0, ls="--", color="black", lw=1)
        axes[0, 0].axhline(1.0, ls="--", color="black", lw=1)
        axes[0, 0].set_xscale("log")
        axes[0, 0].set_yscale("log")
        axes[0, 0].set_title("Reclasificados: factor de escala price daily vs 1m")
        axes[0, 0].set_xlabel("possible_price_scale_factor_vs_daily")
        axes[0, 0].set_ylabel("possible_price_scale_factor_vs_1m")
    else:
        axes[0, 0].axis("off")
        axes[0, 0].set_title("Métricas de escala no disponibles")

    if all(
        c in reclassified_df.columns
        for c in [
            "m.trade_volume_vs_daily_ratio",
            "m.trade_volume_vs_1m_ratio",
        ]
    ):
        plot2 = reclassified_df.dropna(
            subset=[
                "m.trade_volume_vs_daily_ratio",
                "m.trade_volume_vs_1m_ratio",
            ]
        ).copy()
        plot2 = plot2[
            (plot2["m.trade_volume_vs_daily_ratio"] > 0)
            & (plot2["m.trade_volume_vs_1m_ratio"] > 0)
        ]

        sns.scatterplot(
            data=plot2,
            x="m.trade_volume_vs_daily_ratio",
            y="m.trade_volume_vs_1m_ratio",
            hue="m.scale_mismatch_confidence" if "m.scale_mismatch_confidence" in plot2.columns else None,
            ax=axes[0, 1],
        )
        axes[0, 1].axvline(1.0, ls="--", color="black", lw=1)
        axes[0, 1].axhline(1.0, ls="--", color="black", lw=1)
        axes[0, 1].set_xscale("log")
        axes[0, 1].set_yscale("log")
        axes[0, 1].set_title("Reclasificados: ratio de volumen vs referencias")
        axes[0, 1].set_xlabel("trade_volume_vs_daily_ratio")
        axes[0, 1].set_ylabel("trade_volume_vs_1m_ratio")
    else:
        axes[0, 1].axis("off")
        axes[0, 1].set_title("Métricas de volumen no disponibles")

    top_tickers = (
        reclassified_df.groupby("ticker")
        .size()
        .sort_values(ascending=False)
        .head(top_n_tickers)
        .rename_axis("ticker")
        .reset_index(name="files_reclassified")
    )

    sns.barplot(data=top_tickers, y="ticker", x="files_reclassified", color="#2a9d8f", ax=axes[1, 0])
    axes[1, 0].set_title("Top tickers con mayor reclasificación HARD -> SOFT")
    axes[1, 0].set_xlabel("files")
    axes[1, 0].set_ylabel("")

    if "m.scale_mismatch_confidence" in reclassified_df.columns and not top_tickers.empty:
        conf_by_ticker = (
            reclassified_df.groupby(["ticker", "m.scale_mismatch_confidence"])
            .size()
            .reset_index(name="files")
        )
        top_ticker_names = top_tickers["ticker"].tolist()[:top_n_heatmap_tickers]
        conf_by_ticker = conf_by_ticker[conf_by_ticker["ticker"].isin(top_ticker_names)]
        pivot = conf_by_ticker.pivot(
            index="ticker",
            columns="m.scale_mismatch_confidence",
            values="files",
        ).fillna(0)
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=axes[1, 1])
        axes[1, 1].set_title("Granularidad por ticker y scale_mismatch_confidence")
    else:
        axes[1, 1].axis("off")

    plt.tight_layout()
    plt.show()


def display_reclassified_granularity_table(
    reclassified_df: pd.DataFrame,
    top_n: int = 15,
) -> None:
    display(Markdown("### Casos reclasificados ordenados por granularidad de escala"))

    cols_gran = [
        "ticker",
        "date",
        "severity_v010",
        "severity_v020",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.scale_mismatch_confidence",
        "m.scale_mismatch_detected",
        "file_key",
    ]
    cols_gran = [c for c in cols_gran if c in reclassified_df.columns]

    sort_cols = [
        c
        for c in [
            "m.scale_mismatch_confidence",
            "m.possible_price_scale_factor_vs_daily",
            "ticker",
            "date",
        ]
        if c in reclassified_df.columns
    ]

    display(reclassified_df[cols_gran].sort_values(sort_cols).head(top_n))
