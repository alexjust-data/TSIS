from __future__ import annotations

import argparse
import json
import runpy
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd


BASE_SCRIPT = Path(__file__).resolve().parent / "57b_build_trades_file_acceptance_artifacts_lt1b.py"
MOD00_SCRIPT = Path(__file__).resolve().parent / "00_load_trades_run_artifacts.py"

_base = runpy.run_path(str(BASE_SCRIPT))
_mod00 = runpy.run_path(str(MOD00_SCRIPT))

CURRENT_PARQUET_CD = _base["CURRENT_PARQUET_CD"]
TARGET_LT1B_PATH = _base["TARGET_LT1B_PATH"]
DEFAULT_CACHE_DIR = CURRENT_PARQUET_CD.parent / "root_cause_exports" / "file_acceptance_cache_lt1b_full"

_safe_list = _base["_safe_list"]
_safe_float = _base["_safe_float"]
_count_negative_rows = _base["_count_negative_rows"]
_utcnow_iso = _base["_utcnow_iso"]
_write_df = _base["_write_df"]
load_target_lt1b_tickers = _base["load_target_lt1b_tickers"]
classify_sample_stratum = _base["classify_sample_stratum"]
_update_reservoir = _base["_update_reservoir"]
compute_raw_metrics_for_sample_row = _base["compute_raw_metrics_for_sample_row"]
classify_acceptance = _base["classify_acceptance"]

make_trades_audit_handle = _mod00["make_trades_audit_handle"]


def _flush_rows(rows: list[dict], out_dir: Path, prefix: str, shard_idx: int) -> int:
    if not rows:
        return shard_idx
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{prefix}_{shard_idx:05d}.parquet"
    pd.DataFrame(rows).to_parquet(out_path, index=False)
    rows.clear()
    return shard_idx + 1


def compute_layer1_full_artifacts(
    handle,
    target_tickers: set[str],
    batch_size: int,
    index_shard_size: int,
    index_shards_dir: Path,
    sample_per_stratum: int = 20,
    max_batches: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int]]:
    counters = Counter()
    severity_counter = Counter()
    examples: list[dict] = []
    reservoirs: dict[str, list[dict]] = defaultdict(list)
    seen_counter: dict[str, int] = defaultdict(int)
    rng = __import__("random").Random(42)
    shard_rows: list[dict] = []
    index_shard_idx = 1

    cols = ["file", "ticker", "date", "severity", "issues", "warns", "metrics_json"]
    for batch_idx, df in enumerate(handle.stream(columns=cols, batch_size=batch_size, normalize=True), start=1):
        if max_batches is not None and batch_idx > max_batches:
            break
        df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
        df = df.loc[df["ticker"].isin(target_tickers)].copy()
        if df.empty:
            continue

        counters["files_total"] += len(df)
        severity_counter.update(df["severity"].astype(str).tolist())

        for _, row in df.iterrows():
            metrics = row.get("metrics", {}) if isinstance(row.get("metrics"), dict) else {}
            missing_required = _safe_list(metrics.get("missing_required_cols"))
            dtype_mismatches = _safe_list(metrics.get("dtype_mismatches"))
            neg_price_signal = _safe_float(metrics.get("negative_or_zero_price_rows"))
            neg_size_signal = _safe_float(metrics.get("negative_or_zero_size_rows"))
            ts_out = bool(metrics.get("timestamp_out_of_partition_day", False))
            rows_after_parse = _safe_float(metrics.get("rows_after_parse"))
            n_raw = _safe_float(metrics.get("n"))
            file_path = row.get("file")

            neg_price = _count_negative_rows(file_path, "price") if pd.notna(neg_price_signal) and neg_price_signal > 0 else 0
            neg_size = _count_negative_rows(file_path, "size") if pd.notna(neg_size_signal) and neg_size_signal > 0 else 0

            if missing_required:
                counters["files_missing_required_cols"] += 1
            if dtype_mismatches:
                counters["files_dtype_mismatch"] += 1
            if neg_price > 0:
                counters["files_negative_price"] += 1
            if neg_size > 0:
                counters["files_negative_size"] += 1
            if ts_out:
                counters["files_timestamp_out_of_partition"] += 1
            if pd.notna(rows_after_parse) and rows_after_parse <= 0:
                counters["files_empty_after_parse"] += 1
            if pd.notna(n_raw) and n_raw <= 0:
                counters["files_zero_raw_rows"] += 1

            hard_integrity_fail = bool(
                missing_required
                or (neg_price > 0)
                or (neg_size > 0)
                or ts_out
                or (pd.notna(rows_after_parse) and rows_after_parse <= 0)
            )
            if hard_integrity_fail and len(examples) < 200:
                examples.append(
                    {
                        "file": row.get("file"),
                        "ticker": row.get("ticker"),
                        "date": row.get("date"),
                        "severity": row.get("severity"),
                        "missing_required_cols": str(missing_required),
                        "dtype_mismatches": str(dtype_mismatches),
                        "negative_price_rows": neg_price,
                        "negative_size_rows": neg_size,
                        "timestamp_out_of_partition_day": ts_out,
                        "rows_after_parse": rows_after_parse,
                        "issues_list": str(_safe_list(row.get("issues_list"))),
                        "warns_list": str(_safe_list(row.get("warns_list"))),
                    }
                )

            row_dict = {
                "file": row.get("file"),
                "ticker": row.get("ticker"),
                "date": row.get("date"),
                "severity": row.get("severity"),
                "issues_list": _safe_list(row.get("issues_list")),
                "warns_list": _safe_list(row.get("warns_list")),
                "m.l": metrics.get("l"),
                "m.h": metrics.get("h"),
                "m.vw": metrics.get("vw"),
                "m.price_min": metrics.get("price_min"),
                "m.price_max": metrics.get("price_max"),
                "m.trade_vwap": metrics.get("trade_vwap"),
                "m.off_session_trade_pct": metrics.get("off_session_trade_pct"),
                "m.duplicate_excess_ratio_pct": metrics.get("duplicate_excess_ratio_pct"),
                "m.max_trades_same_timestamp": metrics.get("max_trades_same_timestamp"),
                "m.missing_required_cols": missing_required,
                "m.dtype_mismatches": dtype_mismatches,
                "m.timestamp_out_of_partition_day": ts_out,
                "m.rows_after_parse": rows_after_parse,
                "m.ohlcv_1m_found": metrics.get("ohlcv_1m_found"),
                "m.ohlcv_daily_found": metrics.get("ohlcv_daily_found"),
                "m.ohlcv_1m_path": metrics.get("ohlcv_1m_path"),
                "m.ohlcv_daily_path": metrics.get("ohlcv_daily_path"),
                "sample_stratum": None,
            }
            row_dict["sample_stratum"] = classify_sample_stratum(pd.Series(row_dict))
            _update_reservoir(reservoirs, row_dict, sample_per_stratum, seen_counter, rng)
            shard_rows.append(row_dict)

            if len(shard_rows) >= index_shard_size:
                index_shard_idx = _flush_rows(shard_rows, index_shards_dir, "index", index_shard_idx)

        if batch_idx % 25 == 0:
            print(
                json.dumps(
                    {
                        "stage": "layer1_scan_full",
                        "batch_idx": batch_idx,
                        "files_total_seen_lt1b": counters["files_total"],
                        "index_shards_written": index_shard_idx - 1,
                        "strata_seen": len(reservoirs),
                    },
                    ensure_ascii=False,
                )
            )

    index_shard_idx = _flush_rows(shard_rows, index_shards_dir, "index", index_shard_idx)

    integrity_summary = pd.DataFrame(
        [
            {"metric": "files_total", "value": counters["files_total"]},
            {"metric": "pass_files", "value": severity_counter.get("PASS", 0)},
            {"metric": "soft_fail_files", "value": severity_counter.get("SOFT_FAIL", 0)},
            {"metric": "hard_fail_files", "value": severity_counter.get("HARD_FAIL", 0)},
            {"metric": "files_missing_required_cols", "value": counters["files_missing_required_cols"]},
            {"metric": "files_dtype_mismatch", "value": counters["files_dtype_mismatch"]},
            {"metric": "files_negative_price", "value": counters["files_negative_price"]},
            {"metric": "files_negative_size", "value": counters["files_negative_size"]},
            {"metric": "files_timestamp_out_of_partition", "value": counters["files_timestamp_out_of_partition"]},
            {"metric": "files_empty_after_parse", "value": counters["files_empty_after_parse"]},
            {"metric": "files_zero_raw_rows", "value": counters["files_zero_raw_rows"]},
        ]
    )
    sample_index = pd.DataFrame([row for rows in reservoirs.values() for row in rows]).drop_duplicates(subset=["file"]).reset_index(drop=True)
    integrity_examples = pd.DataFrame(examples)
    return integrity_summary, integrity_examples, sample_index, {"index_shards_written": index_shard_idx - 1}


def build_full_raw_metrics_from_index_shards(
    index_shards_dir: Path,
    raw_metrics_shards_dir: Path,
    metrics_shard_size: int,
) -> dict:
    raw_metrics_shards_dir.mkdir(parents=True, exist_ok=True)
    metrics_buffer: list[dict] = []
    shard_idx = 1
    files_done = 0
    policy_counter = Counter()
    files_with_1m_reference = 0
    files_with_daily_reference = 0

    for index_path in sorted(index_shards_dir.glob("index_*.parquet")):
        index_df = pd.read_parquet(index_path)
        for _, row in index_df.iterrows():
            metrics = compute_raw_metrics_for_sample_row(row)
            metrics["acceptance_label"] = classify_acceptance(pd.Series(metrics))
            metrics_buffer.append(metrics)
            policy_counter[metrics["acceptance_label"]] += 1
            files_with_1m_reference += int(bool(metrics.get("has_1m_reference", False)))
            files_with_daily_reference += int(bool(metrics.get("has_daily_reference", False)))
            files_done += 1

            if len(metrics_buffer) >= metrics_shard_size:
                shard_idx = _flush_rows(metrics_buffer, raw_metrics_shards_dir, "raw_metrics", shard_idx)
                print(
                    json.dumps(
                        {
                            "stage": "full_raw_recompute",
                            "files_done": files_done,
                            "raw_metric_shards_written": shard_idx - 1,
                        },
                        ensure_ascii=False,
                    )
                )

    shard_idx = _flush_rows(metrics_buffer, raw_metrics_shards_dir, "raw_metrics", shard_idx)
    if files_done:
        print(
            json.dumps(
                {
                    "stage": "full_raw_recompute",
                    "files_done": files_done,
                    "raw_metric_shards_written": shard_idx - 1,
                },
                ensure_ascii=False,
            )
        )

    policy_summary = pd.DataFrame(
        [{"acceptance_label": label, "files": count} for label, count in sorted(policy_counter.items())]
    ).sort_values(["files", "acceptance_label"], ascending=[False, True]).reset_index(drop=True)
    coverage_summary = pd.DataFrame(
        [
            {"metric": "files_total_full_raw", "value": files_done},
            {"metric": "files_with_1m_reference_pct", "value": 100 * files_with_1m_reference / files_done if files_done else 0.0},
            {"metric": "files_with_daily_reference_pct", "value": 100 * files_with_daily_reference / files_done if files_done else 0.0},
        ]
    )
    return {
        "policy_summary": policy_summary,
        "coverage_summary": coverage_summary,
        "raw_metric_shards_written": shard_idx - 1,
        "files_done": files_done,
    }


def build_file_acceptance_artifacts_lt1b_full(
    current_parquet: Path = CURRENT_PARQUET_CD,
    target_lt1b_path: Path = TARGET_LT1B_PATH,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    batch_size: int = 50_000,
    index_shard_size: int = 100_000,
    metrics_shard_size: int = 5_000,
    sample_per_stratum: int = 20,
    max_batches: int | None = None,
) -> dict:
    handle = make_trades_audit_handle(current_parquet)
    target_tickers = load_target_lt1b_tickers(target_lt1b_path)
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_shards_dir = cache_dir / "full_index_shards"
    raw_metrics_shards_dir = cache_dir / "raw_metrics_shards"

    integrity_summary, integrity_examples, sample_index, layer1_meta = compute_layer1_full_artifacts(
        handle=handle,
        target_tickers=target_tickers,
        batch_size=batch_size,
        index_shard_size=index_shard_size,
        index_shards_dir=index_shards_dir,
        sample_per_stratum=sample_per_stratum,
        max_batches=max_batches,
    )
    _write_df(integrity_summary, cache_dir / "layer1_integrity_summary.parquet")
    _write_df(integrity_examples, cache_dir / "layer1_integrity_examples.parquet")
    _write_df(sample_index, cache_dir / "sample_index.parquet")

    full_meta = build_full_raw_metrics_from_index_shards(
        index_shards_dir=index_shards_dir,
        raw_metrics_shards_dir=raw_metrics_shards_dir,
        metrics_shard_size=metrics_shard_size,
    )
    _write_df(full_meta["policy_summary"], cache_dir / "layer6_policy_summary_full.parquet")
    _write_df(full_meta["coverage_summary"], cache_dir / "layer2_coverage_summary_full.parquet")

    manifest = {
        "built_at_utc": _utcnow_iso(),
        "mode": "full_raw_lt1b",
        "current_parquet": str(current_parquet),
        "target_lt1b_path": str(target_lt1b_path),
        "target_tickers": int(len(target_tickers)),
        "cache_dir": str(cache_dir),
        "batch_size": batch_size,
        "index_shard_size": index_shard_size,
        "metrics_shard_size": metrics_shard_size,
        "sample_per_stratum": sample_per_stratum,
        "max_batches": max_batches,
        "files_total": int(integrity_summary.loc[integrity_summary["metric"] == "files_total", "value"].iloc[0]),
        "sample_files": int(len(sample_index)),
        "index_shards_written": int(layer1_meta["index_shards_written"]),
        "raw_metric_shards_written": int(full_meta["raw_metric_shards_written"]),
        "full_raw_files_done": int(full_meta["files_done"]),
        "artifacts": sorted([p.name for p in cache_dir.glob("*.parquet")]),
        "subdirs": sorted([p.name for p in cache_dir.iterdir() if p.is_dir()]),
    }
    (cache_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-parquet", type=Path, default=CURRENT_PARQUET_CD)
    parser.add_argument("--target-lt1b-path", type=Path, default=TARGET_LT1B_PATH)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--index-shard-size", type=int, default=100_000)
    parser.add_argument("--metrics-shard-size", type=int, default=5_000)
    parser.add_argument("--sample-per-stratum", type=int, default=20)
    parser.add_argument("--max-batches", type=int, default=None)
    args = parser.parse_args()

    manifest = build_file_acceptance_artifacts_lt1b_full(
        current_parquet=args.current_parquet,
        target_lt1b_path=args.target_lt1b_path,
        cache_dir=args.cache_dir,
        batch_size=args.batch_size,
        index_shard_size=args.index_shard_size,
        metrics_shard_size=args.metrics_shard_size,
        sample_per_stratum=args.sample_per_stratum,
        max_batches=args.max_batches,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
