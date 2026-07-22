from __future__ import annotations

import argparse
import json

import pandas as pd

from _ws_common import CURATED_DIR, RAW_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    parser.add_argument("--head", type=int, default=15)
    return parser.parse_args()


def print_json_block(title: str, payload: object) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:
    args = parse_args()

    raw_dir = RAW_DIR / args.label
    curated_dir = CURATED_DIR / args.label

    raw_path = raw_dir / "events.jsonl"
    meta_path = raw_dir / "capture_meta.json"
    summary_path = curated_dir / "summary.json"
    parquet_path = curated_dir / "events.parquet"

    print("Rutas de inspeccion")
    print(f"raw jsonl   : {raw_path}")
    print(f"capture meta: {meta_path}")
    print(f"summary     : {summary_path}")
    print(f"parquet     : {parquet_path}")

    if meta_path.exists():
        print_json_block("CAPTURE META", json.loads(meta_path.read_text(encoding="utf-8")))

    if summary_path.exists():
        print_json_block("SUMMARY", json.loads(summary_path.read_text(encoding="utf-8")))

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
        print(f"\n=== PARQUET INFO ===")
        print(f"rows={len(df)} cols={len(df.columns)} columns={list(df.columns)}")

        if not df.empty:
            print(f"\n=== PARQUET HEAD ({min(args.head, len(df))}) ===")
            print(df.head(args.head).to_string(index=False))

            if "ev" in df.columns:
                print("\n=== EVENT TYPES ===")
                print(df["ev"].value_counts(dropna=False).to_string())

            if "sym" in df.columns:
                print("\n=== SYMBOL COUNTS ===")
                print(df["sym"].value_counts(dropna=False).head(20).to_string())

    if raw_path.exists():
        print(f"\n=== RAW JSONL SAMPLE ({args.head}) ===")
        with raw_path.open("r", encoding="utf-8") as handle:
            for idx, line in enumerate(handle):
                if idx >= args.head:
                    break
                print(line.rstrip())


if __name__ == "__main__":
    main()
