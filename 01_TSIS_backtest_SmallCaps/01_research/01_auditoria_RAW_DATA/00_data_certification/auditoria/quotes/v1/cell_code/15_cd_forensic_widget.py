from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import Markdown, display


def _load_quote_file(file_path: str, max_rows: int = 200_000) -> pd.DataFrame:
    df = pd.read_parquet(file_path).copy()
    if len(df) > max_rows:
        df = df.iloc[:max_rows].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ns", utc=True, errors="coerce")
    return df


def _plot_quote_case(raw: pd.DataFrame, title: str) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(18, 10), sharex=True)
    axes[0].plot(raw["timestamp"], raw["bid_price"], label="bid", color="#264653", linewidth=0.8)
    axes[0].plot(raw["timestamp"], raw["ask_price"], label="ask", color="#e76f51", linewidth=0.8)
    axes[0].legend()
    axes[0].set_title(title)

    spread = raw["ask_price"] - raw["bid_price"]
    axes[1].plot(raw["timestamp"], spread, color="#2a9d8f", linewidth=0.8)
    axes[1].axhline(0, color="black", linewidth=0.8, linestyle="--")
    axes[1].set_title("spread = ask - bid")

    crossed = (raw["bid_price"] > raw["ask_price"]).astype(int)
    axes[2].plot(raw["timestamp"], crossed, color="#f4a261", linewidth=0.8)
    axes[2].set_title("crossed rows flag")
    axes[2].set_ylim(-0.05, 1.05)
    fig.tight_layout()


def run_cd_forensic_widget(df: pd.DataFrame, initial_focus: str = "HARD_FAIL", top_n: int = 20) -> pd.DataFrame:
    if initial_focus == "HARD_FAIL":
        base = df.loc[df["severity"].eq("HARD_FAIL")].copy()
    elif initial_focus == "TIMESTAMP":
        base = df.loc[df["m.timestamp_out_of_partition_day"].fillna(False)].copy()
    else:
        base = df.copy()

    cols = [
        "ticker",
        "date",
        "root",
        "severity",
        "rows",
        "m.crossed_ratio_pct",
        "m.crossed_rows",
        "m.ask_integer_pct",
        "m.ask_eq_round_bid_pct",
        "file",
    ]
    ranked = base.loc[:, cols].sort_values(["m.crossed_ratio_pct", "rows"], ascending=False).head(top_n).reset_index(drop=True)
    display(ranked)
    if ranked.empty:
        display(Markdown("No hay casos para inspeccionar."))
        return ranked

    top = ranked.iloc[0]
    raw = _load_quote_file(top["file"])
    display(
        Markdown(
            f"**Caso inicial:** `{top['ticker']}` `{top['date'].date()}` root `{top['root']}` "
            f"severity `{top['severity']}` crossed_ratio_pct `{top['m.crossed_ratio_pct']:.4f}`"
        )
    )
    _plot_quote_case(raw, f"{top['ticker']} {top['date'].date()} {Path(top['file']).drive}")
    return ranked

