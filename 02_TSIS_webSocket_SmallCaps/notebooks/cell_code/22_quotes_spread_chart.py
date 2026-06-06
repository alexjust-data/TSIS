from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import pandas as pd

from _ws_common import CURATED_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run_phase3")
    parser.add_argument("--max-symbols", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    quotes_path = CURATED_DIR / args.label / "normalized" / "quotes.parquet"
    if not quotes_path.exists():
        raise FileNotFoundError(f"No existe quotes.parquet: {quotes_path}")

    df = pd.read_parquet(quotes_path).copy()
    if df.empty:
        raise ValueError("El dataset de quotes está vacío para este run")

    df["event_dt_utc"] = pd.to_datetime(df["event_time"], unit="ms", utc=True, errors="coerce")
    df["spread"] = df["ask_price"] - df["bid_price"]
    df = df.sort_values(["sym", "event_dt_utc", "sequence"]).reset_index(drop=True)

    symbols = df["sym"].value_counts().head(args.max_symbols).index.tolist()
    fig, axes = plt.subplots(len(symbols), 1, figsize=(13, max(4, 4 * len(symbols))), sharex=False)
    if len(symbols) == 1:
        axes = [axes]

    for ax, sym in zip(axes, symbols):
        data = df[df["sym"] == sym].copy()
        ax.plot(data["event_dt_utc"], data["bid_price"], label="bid", color="#0b5d7a", linewidth=1.1)
        ax.plot(data["event_dt_utc"], data["ask_price"], label="ask", color="#d04a02", linewidth=1.1)
        ax.fill_between(data["event_dt_utc"], data["bid_price"], data["ask_price"], color="#f1c27d", alpha=0.25)
        ax.set_title(
            f"{sym} | quotes={len(data)} | spread_min={data['spread'].min():.4f} | spread_max={data['spread'].max():.4f}"
        )
        ax.set_ylabel("Price")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="upper right")

    axes[-1].set_xlabel("Event time (UTC)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
