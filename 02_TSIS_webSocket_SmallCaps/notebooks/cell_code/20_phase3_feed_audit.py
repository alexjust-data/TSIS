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
    meta_path = RAW_DIR / args.label / "capture_meta.json"
    manifest_path = CURATED_DIR / args.label / "normalized" / "manifest.json"
    metrics_path = CURATED_DIR / args.label / "metrics.json"

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))

    report = {
        "label": args.label,
        "subscription": meta.get("subscription"),
        "event_counts": meta.get("event_counts"),
        "normalized_rows": {k: v.get("rows", 0) for k, v in manifest.items()},
        "datasets_present": {
            k: bool(v.get("exists", v.get("written", False))) for k, v in metrics.get("datasets", {}).items()
        },
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    frame = pd.DataFrame(
        [
            {
                "dataset": dataset,
                "rows": details.get("rows", 0),
                "exists": details.get("exists", details.get("written", False)),
            }
            for dataset, details in metrics.get("datasets", {}).items()
        ]
    )
    if not frame.empty:
        print("\nDatasets")
        print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
