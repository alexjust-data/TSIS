from __future__ import annotations

import argparse

import pandas as pd

from _ws_common import CURATED_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    parser.add_argument("--head", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    quotes_path = CURATED_DIR / args.label / "normalized" / "quotes.parquet"
    if not quotes_path.exists():
        print(f"No existe quotes.parquet para este run: {quotes_path}")
        return

    df = pd.read_parquet(quotes_path)
    print(f"rows={len(df)} cols={len(df.columns)}")
    print(f"columns={list(df.columns)}")
    if df.empty:
        print("El dataset de quotes existe pero está vacío.")
        return

    display_cols = [
        col
        for col in [
            "captured_at_utc",
            "sym",
            "event_time",
            "bid_price",
            "bid_size",
            "ask_price",
            "ask_size",
            "sequence",
        ]
        if col in df.columns
    ]
    print("\nHead")
    print(df[display_cols].head(args.head).to_string(index=False))

    print("\nQuotes por símbolo")
    print(df["sym"].value_counts().to_string())


if __name__ == "__main__":
    main()
