from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from _ws_common import CURATED_DIR


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="prototype_run")
    return parser.parse_args()


def add_partition_columns(df: pd.DataFrame, time_col: str) -> pd.DataFrame:
    if df.empty:
        return df
    ts = pd.to_datetime(df[time_col], unit="ms", utc=True, errors="coerce")
    df = df.copy()
    df["event_dt_utc"] = ts
    df["event_date"] = ts.dt.strftime("%Y-%m-%d")
    return df


def main() -> None:
    args = parse_args()
    normalized_dir = CURATED_DIR / args.label / "normalized"
    partitioned_root = CURATED_DIR / args.label / "partitioned"
    partitioned_root.mkdir(parents=True, exist_ok=True)

    specs = {
        "trades": "event_time",
        "quotes": "event_time",
        "minute_aggs": "window_start",
        "second_aggs": "window_start",
    }

    report: dict[str, dict[str, object]] = {}
    for dataset, time_col in specs.items():
        src = normalized_dir / f"{dataset}.parquet"
        dst = partitioned_root / dataset
        if not src.exists():
            report[dataset] = {"written": False, "reason": "missing_source"}
            continue

        df = pd.read_parquet(src)
        if df.empty:
            report[dataset] = {"written": False, "reason": "empty_dataset"}
            continue

        df = add_partition_columns(df, time_col)
        df.to_parquet(dst, index=False, partition_cols=["event_date", "sym"])
        report[dataset] = {
            "written": True,
            "rows": int(len(df)),
            "path": str(dst),
            "partitions": int(df[["event_date", "sym"]].drop_duplicates().shape[0]),
        }

    report_path = partitioned_root / "partition_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nPartition report: {report_path}")


if __name__ == "__main__":
    main()
