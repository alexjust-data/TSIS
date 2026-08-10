"""Benchmark reference and vectorized Trading Activity Stage-8 kernels."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
from pathlib import Path

import pandas as pd
import psutil
from trading_activity_binding_a_baseline_cpp import materialize_baseline_and_surprise_cpp
from trading_activity_binding_a_baseline_native import build_baseline_cache_native
from trading_activity_binding_a_baseline_vectorized import (
    materialize_baseline_and_surprise_vectorized,
)
from trading_activity_binding_a_multisession_engine import materialize_baseline_and_surprise

BASELINE_COLUMNS = [
    "session_date", "decision_timestamp", "window_seconds", "calculation_state",
    "eligible_trade_count", "eligible_share_volume", "eligible_dollar_volume",
    "trade_arrival_rate", "median_intertrade_duration_us", "feature_input_max_available_at",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("reference", "vectorized", "native", "cpp"), required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--session-date", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    paths = sorted((args.run_root / "current_state").rglob("part-*.parquet"))
    target_paths = [path for path in paths if f"session_date={args.session_date}" in str(path)]
    if len(target_paths) != 1:
        raise ValueError(f"expected one target partition, found {len(target_paths)}")
    load_started = time.perf_counter()
    prior = pd.concat([pd.read_parquet(path, columns=BASELINE_COLUMNS) for path in paths], ignore_index=True)
    current = pd.read_parquet(target_paths[0])
    load_seconds = time.perf_counter() - load_started

    process = psutil.Process(os.getpid())
    peak_rss = process.memory_info().rss
    stop = threading.Event()

    def sample() -> None:
        nonlocal peak_rss
        while not stop.wait(0.05):
            peak_rss = max(peak_rss, process.memory_info().rss)

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    if args.mode == "reference":
        kernel = materialize_baseline_and_surprise
    elif args.mode == "cpp":
        kernel = materialize_baseline_and_surprise_cpp
    else:
        kernel = materialize_baseline_and_surprise_vectorized
    kernel_started = time.perf_counter()
    kwargs = {
        "prior_current": prior,
        "config": config,
        "evaluation_session_date": pd.Timestamp(args.session_date).date(),
    }
    if args.mode == "native":
        kwargs["cache_builder"] = build_baseline_cache_native
    result = kernel(current, **kwargs)
    kernel_seconds = time.perf_counter() - kernel_started
    stop.set()
    sampler.join(timeout=1)
    peak_rss = max(peak_rss, process.memory_info().rss)

    args.output_root.mkdir(parents=True, exist_ok=True)
    output = args.output_root / f"{args.mode}.parquet"
    result.to_parquet(output, index=False, compression="zstd")
    manifest = {
        "mode": args.mode,
        "session_date": args.session_date,
        "input_partition_count": len(paths),
        "prior_rows": len(prior),
        "current_rows": len(current),
        "output_rows": len(result),
        "load_seconds": load_seconds,
        "kernel_seconds": kernel_seconds,
        "total_seconds": time.perf_counter() - started,
        "peak_rss_bytes": peak_rss,
        "output_sha256": _sha256(output),
        "columns": list(result.columns),
        "dtypes": {column: str(dtype) for column, dtype in result.dtypes.items()},
    }
    (args.output_root / f"{args.mode}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
