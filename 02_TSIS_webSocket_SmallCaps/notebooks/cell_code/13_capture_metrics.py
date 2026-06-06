from __future__ import annotations

import argparse
import json

import pandas as pd

from _ws_common import CURATED_DIR, RAW_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw_path = RAW_DIR / args.label / "events.jsonl"
    meta_path = RAW_DIR / args.label / "capture_meta.json"
    normalized_dir = CURATED_DIR / args.label / "normalized"
    out_path = CURATED_DIR / args.label / "metrics.json"

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    raw_size_bytes = raw_path.stat().st_size if raw_path.exists() else 0

    metrics: dict[str, object] = {
        "capture_duration_sec": meta.get("duration_sec"),
        "total_messages": meta.get("total_messages"),
        "total_events": meta.get("total_events"),
        "events_per_message": round(meta.get("total_events", 0) / max(meta.get("total_messages", 1), 1), 4),
        "raw_size_bytes": raw_size_bytes,
        "datasets": {},
    }

    for dataset in ["trades", "quotes", "minute_aggs", "second_aggs"]:
        parquet_path = normalized_dir / f"{dataset}.parquet"
        if not parquet_path.exists():
            metrics["datasets"][dataset] = {"rows": 0, "exists": False}
            continue

        df = pd.read_parquet(parquet_path)
        dataset_metrics = {
            "rows": int(len(df)),
            "exists": True,
            "columns": list(df.columns),
            "symbols": df["sym"].value_counts().to_dict() if "sym" in df.columns and not df.empty else {},
        }

        if dataset == "trades" and not df.empty:
            event_ts = pd.to_datetime(df["event_time"], unit="ms", utc=True, errors="coerce")
            capture_ts = pd.to_datetime(df["captured_at_utc"], utc=True, errors="coerce")
            capture_minus_event_ms = (capture_ts - event_ts).dt.total_seconds() * 1000
            dataset_metrics["timing_observation_ms"] = {
                "definition": "captured_at_utc minus event_time",
                "note": "Esto no debe interpretarse como latencia operativa fiable sin modelar mejor la semantica del timestamp del feed y el reloj local.",
                "min": round(float(capture_minus_event_ms.min()), 3),
                "max": round(float(capture_minus_event_ms.max()), 3),
                "median": round(float(capture_minus_event_ms.median()), 3),
                "mean": round(float(capture_minus_event_ms.mean()), 3),
            }

        metrics["datasets"][dataset] = dataset_metrics

    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"\nMetrics: {out_path}")


if __name__ == "__main__":
    main()
