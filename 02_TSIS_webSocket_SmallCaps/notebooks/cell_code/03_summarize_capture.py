from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from _ws_common import CURATED_DIR, RAW_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = RAW_DIR / args.label / "events.jsonl"
    curated_dir = CURATED_DIR / args.label
    curated_dir.mkdir(parents=True, exist_ok=True)

    if not raw_path.exists():
        raise FileNotFoundError(f"No existe captura previa: {raw_path}")

    rows: list[dict[str, object]] = []
    with raw_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            event = payload["event"]
            rows.append(
                {
                    "captured_at_utc": payload["captured_at_utc"],
                    "ev": event.get("ev"),
                    "sym": event.get("sym"),
                    "t": event.get("t"),
                    "price": event.get("p", event.get("c")),
                    "size": event.get("s", event.get("v")),
                    "raw_event": json.dumps(event, separators=(",", ":")),
                }
            )

    df = pd.DataFrame(rows)
    summary = {
        "rows": int(len(df)),
        "event_types": df["ev"].value_counts(dropna=False).to_dict() if not df.empty else {},
        "symbols": df["sym"].value_counts(dropna=False).to_dict() if not df.empty else {},
    }

    parquet_path = curated_dir / "events.parquet"
    csv_path = curated_dir / "events_preview.csv"
    summary_path = curated_dir / "summary.json"

    if not df.empty:
        df.to_parquet(parquet_path, index=False)
        df.head(200).to_csv(csv_path, index=False)

    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if not df.empty:
        print("\nPreview:")
        print(df.head(10).to_string(index=False))
    print(f"\nSummary: {summary_path}")
    if not df.empty:
        print(f"Parquet: {parquet_path}")
        print(f"CSV preview: {csv_path}")


if __name__ == "__main__":
    main()
