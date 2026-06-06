from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]
SEVERITY_PALETTE = {"PASS": "#2a9d8f", "SOFT_FAIL": "#e9c46a", "HARD_FAIL": "#e76f51"}


def build_microstructure_sample_cd(df: pd.DataFrame, max_n: int = 250_000, random_state: int = 7) -> pd.DataFrame:
    if len(df) <= max_n:
        return df.copy()
    return df.sample(max_n, random_state=random_state).copy()


def build_crossed_band_view_cd(df: pd.DataFrame) -> pd.DataFrame:
    out = (
        df.groupby(["severity", "crossed_bucket"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    return out


def build_integer_anomaly_view_cd(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    cols = [
        "ticker",
        "date",
        "root",
        "severity",
        "rows",
        "m.crossed_ratio_pct",
        "m.crossed_rows",
        "m.ask_integer_pct",
        "m.bid_integer_pct",
        "m.ask_eq_round_bid_pct",
        "issues_list",
        "warns_list",
    ]
    use = df.loc[df["m.ask_integer_pct"].fillna(0).ge(80) | df["m.ask_eq_round_bid_pct"].fillna(0).ge(80), cols].copy()
    return use.sort_values(["m.ask_integer_pct", "m.ask_eq_round_bid_pct", "m.crossed_ratio_pct"], ascending=False).head(top_n)


def build_timestamp_view_cd(df: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    cols = ["ticker", "date", "root", "severity", "rows", "m.ts_min_utc", "m.ts_max_utc", "m.actual_timestamp_dates_utc", "warns_list"]
    use = df.loc[df["m.timestamp_out_of_partition_day"].fillna(False), cols].copy()
    return use.sort_values(["rows", "ticker", "date"], ascending=[False, True, True]).head(top_n)


def plot_microstructure_diagnostics_cd(sample_df: pd.DataFrame, crossed_band: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(20, 5))

    for severity in SEVERITY_ORDER:
        sub = sample_df.loc[sample_df["severity"].eq(severity), "m.crossed_ratio_pct"].dropna()
        if not sub.empty:
            axes[0].hist(np.clip(sub, 0, 20), bins=60, alpha=0.45, label=severity, color=SEVERITY_PALETTE[severity])
    axes[0].set_title("Distribucion crossed_ratio_pct (clip 20)")
    axes[0].legend()

    integer_df = sample_df.groupby("severity")[["m.ask_integer_pct", "m.bid_integer_pct", "m.ask_eq_round_bid_pct"]].median().reindex(SEVERITY_ORDER)
    integer_df.plot(kind="bar", ax=axes[1], color=["#264653", "#2a9d8f", "#f4a261"])
    axes[1].set_title("Medianas de senales de enterizacion")
    axes[1].set_ylabel("pct")
    axes[1].tick_params(axis="x", rotation=0)

    pivot = crossed_band.pivot(index="crossed_bucket", columns="severity", values="files").fillna(0).reindex(columns=SEVERITY_ORDER, fill_value=0)
    pivot.plot(kind="bar", stacked=True, ax=axes[2], color=[SEVERITY_PALETTE[x] for x in SEVERITY_ORDER])
    axes[2].set_title("Bandas de crossed_ratio_pct")
    axes[2].set_ylabel("files")
    axes[2].tick_params(axis="x", rotation=45)

    fig.tight_layout()

