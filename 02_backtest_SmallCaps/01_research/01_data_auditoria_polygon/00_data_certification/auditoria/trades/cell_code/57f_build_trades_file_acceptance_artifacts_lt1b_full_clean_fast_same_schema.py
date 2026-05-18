from __future__ import annotations

import argparse
import json
import runpy
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_57B = BASE_DIR / "57f_build_trades_file_acceptance_artifacts_lt1b_fast_same_schema.py"
SCRIPT_57C = BASE_DIR / "57c_build_trades_file_acceptance_artifacts_lt1b_full.py"
SCRIPT_00 = BASE_DIR / "00_load_trades_run_artifacts.py"

_mod57b = runpy.run_path(str(SCRIPT_57B))
_mod57c = runpy.run_path(str(SCRIPT_57C))
_mod00 = runpy.run_path(str(SCRIPT_00))

CURRENT_PARQUET_CD = _mod57b["CURRENT_PARQUET_CD"]
TARGET_LT1B_PATH = _mod57b["TARGET_LT1B_PATH"]
DEFAULT_CACHE_DIR = CURRENT_PARQUET_CD.parent / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean_fast_same_schema"

_utcnow_iso = _mod57b["_utcnow_iso"]
_write_df = _mod57b["_write_df"]
compute_raw_metrics_for_sample_row = _mod57b["compute_raw_metrics_for_sample_row"]
classify_acceptance = _mod57b["classify_acceptance"]
load_target_lt1b_tickers = _mod57b["load_target_lt1b_tickers"]
compute_layer1_full_artifacts = _mod57c["compute_layer1_full_artifacts"]
make_trades_audit_handle = _mod00["make_trades_audit_handle"]
_safe_list = _mod57b["_safe_list"]
_safe_float = _mod57b["_safe_float"]
_count_negative_rows = _mod57b["_count_negative_rows"]
classify_sample_stratum = _mod57b["classify_sample_stratum"]
_update_reservoir = _mod57b["_update_reservoir"]


def _progress_path(cache_dir: Path) -> Path:
    return cache_dir / "progress.json"


def _manifest_path(cache_dir: Path) -> Path:
    return cache_dir / "manifest.json"


def _index_dir(cache_dir: Path) -> Path:
    return cache_dir / "full_index_shards"


def _raw_dir(cache_dir: Path) -> Path:
    return cache_dir / "raw_metrics_shards"


def _read_progress(cache_dir: Path) -> dict:
    p = _progress_path(cache_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _write_progress(cache_dir: Path, payload: dict) -> None:
    payload = {**payload, "updated_at_utc": _utcnow_iso()}
    _progress_path(cache_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _raw_metrics_path_for_index(index_path: Path, raw_metrics_dir: Path) -> Path:
    return raw_metrics_dir / index_path.name.replace("index_", "raw_metrics_")


def _process_index_shard(index_path: str, raw_metrics_path: str) -> dict:
    index_p = Path(index_path)
    out_p = Path(raw_metrics_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if out_p.exists():
        df = pd.read_parquet(out_p, columns=["acceptance_label"])
        return {
            "index_shard": index_p.name,
            "status": "skipped_existing",
            "files_done": int(len(df)),
        }

    index_df = pd.read_parquet(index_p)
    index_columns = list(index_df.columns)
    rows: list[dict] = []
    for values in index_df.itertuples(index=False, name=None):
        row = dict(zip(index_columns, values))
        metrics = compute_raw_metrics_for_sample_row(row)
        metrics["acceptance_label"] = classify_acceptance(metrics)
        rows.append(metrics)

    out_df = pd.DataFrame(rows)
    out_df.to_parquet(out_p, index=False)
    return {
        "index_shard": index_p.name,
        "status": "completed",
        "files_done": int(len(out_df)),
    }


def _aggregate_existing_raw_metrics(raw_metrics_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts: dict[str, int] = {}
    files_done = 0
    files_with_1m_reference = 0
    files_with_daily_reference = 0

    for shard in sorted(raw_metrics_dir.glob("raw_metrics_*.parquet")):
        df = pd.read_parquet(shard, columns=["acceptance_label", "has_1m_reference", "has_daily_reference"])
        files_done += int(len(df))
        vc = df["acceptance_label"].value_counts().to_dict()
        for label, count in vc.items():
            counts[label] = counts.get(label, 0) + int(count)
        files_with_1m_reference += int(df["has_1m_reference"].fillna(False).astype(bool).sum())
        files_with_daily_reference += int(df["has_daily_reference"].fillna(False).astype(bool).sum())

    policy_summary = pd.DataFrame([{"acceptance_label": k, "files": v} for k, v in counts.items()])
    if not policy_summary.empty:
        policy_summary = policy_summary.sort_values(["files", "acceptance_label"], ascending=[False, True]).reset_index(drop=True)
    coverage_summary = pd.DataFrame(
        [
            {"metric": "files_total_full_raw", "value": files_done},
            {"metric": "files_with_1m_reference_pct", "value": 100 * files_with_1m_reference / files_done if files_done else 0.0},
            {"metric": "files_with_daily_reference_pct", "value": 100 * files_with_daily_reference / files_done if files_done else 0.0},
        ]
    )
    return policy_summary, coverage_summary


def _flush_index_rows(rows: list[dict], out_dir: Path, shard_idx: int) -> int:
    if not rows:
        return shard_idx
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"index_{shard_idx:05d}.parquet"
    pd.DataFrame(rows).to_parquet(out_path, index=False)
    rows.clear()
    return shard_idx + 1


def compute_layer1_full_artifacts_with_progress(
    handle,
    target_tickers: set[str],
    batch_size: int,
    index_shard_size: int,
    index_shards_dir: Path,
    cache_dir: Path,
    sample_per_stratum: int = 20,
    max_batches: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, int]]:
    counters = __import__("collections").Counter()
    severity_counter = __import__("collections").Counter()
    examples: list[dict] = []
    reservoirs: dict[str, list[dict]] = __import__("collections").defaultdict(list)
    seen_counter: dict[str, int] = __import__("collections").defaultdict(int)
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
                index_shard_idx = _flush_index_rows(shard_rows, index_shards_dir, index_shard_idx)

        if batch_idx % 5 == 0:
            sample_rows = sum(len(v) for v in reservoirs.values())
            progress_payload = {
                **_read_progress(cache_dir),
                "phase": "index_running",
                "batch_idx": batch_idx,
                "files_total_seen_lt1b": int(counters["files_total"]),
                "index_shards_written": int(index_shard_idx - 1),
                "sample_rows_current": int(sample_rows),
                "strata_seen": int(len(reservoirs)),
            }
            _write_progress(cache_dir, progress_payload)
            print(
                json.dumps(
                    {
                        "stage": "full_clean_index",
                        "batch_idx": batch_idx,
                        "files_total_seen_lt1b": counters["files_total"],
                        "index_shards_written": index_shard_idx - 1,
                        "sample_rows_current": sample_rows,
                        "strata_seen": len(reservoirs),
                    },
                    ensure_ascii=False,
                )
            )

    index_shard_idx = _flush_index_rows(shard_rows, index_shards_dir, index_shard_idx)

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


def run_index_phase(
    cache_dir: Path,
    current_parquet: Path,
    target_lt1b_path: Path,
    batch_size: int,
    index_shard_size: int,
    sample_per_stratum: int,
    max_batches: int | None,
    force_rebuild_index: bool,
) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    index_dir = _index_dir(cache_dir)
    raw_dir = _raw_dir(cache_dir)

    if force_rebuild_index:
        for p in sorted(index_dir.glob("*.parquet")):
            p.unlink()
        for p in sorted(raw_dir.glob("*.parquet")):
            p.unlink()

    existing_index_shards = sorted(index_dir.glob("index_*.parquet"))
    existing_summary = cache_dir / "layer1_integrity_summary.parquet"
    existing_examples = cache_dir / "layer1_integrity_examples.parquet"
    existing_sample = cache_dir / "sample_index.parquet"
    if existing_index_shards and existing_summary.exists() and existing_examples.exists() and existing_sample.exists():
        integrity_summary = pd.read_parquet(existing_summary)
        files_total = int(integrity_summary.loc[integrity_summary["metric"].eq("files_total"), "value"].iloc[0])
        sample_files = int(len(pd.read_parquet(existing_sample)))
        meta = {
            "phase": "index_ready",
            "files_total": files_total,
            "index_shards_written": len(existing_index_shards),
            "sample_files": sample_files,
            "resumed": True,
        }
        _write_progress(cache_dir, {**_read_progress(cache_dir), **meta})
        return meta

    handle = make_trades_audit_handle(current_parquet)
    target_tickers = load_target_lt1b_tickers(target_lt1b_path)
    integrity_summary, integrity_examples, sample_index, layer1_meta = compute_layer1_full_artifacts_with_progress(
        handle=handle,
        target_tickers=target_tickers,
        batch_size=batch_size,
        index_shard_size=index_shard_size,
        index_shards_dir=index_dir,
        cache_dir=cache_dir,
        sample_per_stratum=sample_per_stratum,
        max_batches=max_batches,
    )
    _write_df(integrity_summary, cache_dir / "layer1_integrity_summary.parquet")
    _write_df(integrity_examples, cache_dir / "layer1_integrity_examples.parquet")
    _write_df(sample_index, cache_dir / "sample_index.parquet")
    files_total = int(integrity_summary.loc[integrity_summary["metric"].eq("files_total"), "value"].iloc[0])
    meta = {
        "phase": "index_ready",
        "files_total": files_total,
        "index_shards_written": int(layer1_meta["index_shards_written"]),
        "sample_files": int(len(sample_index)),
        "resumed": False,
    }
    _write_progress(cache_dir, {**_read_progress(cache_dir), **meta})
    return meta


def run_recompute_phase(cache_dir: Path, workers: int, limit_shards: int | None) -> dict:
    index_dir = _index_dir(cache_dir)
    raw_dir = _raw_dir(cache_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    index_shards = sorted(index_dir.glob("index_*.parquet"))
    if not index_shards:
        raise FileNotFoundError(f"No se encontraron index shards en {index_dir}")

    pending: list[tuple[Path, Path]] = []
    skipped_existing = 0
    for index_path in index_shards:
        out_path = _raw_metrics_path_for_index(index_path, raw_dir)
        if out_path.exists():
            skipped_existing += 1
            continue
        pending.append((index_path, out_path))

    if limit_shards is not None:
        pending = pending[:limit_shards]

    completed_now = 0
    files_done_now = 0
    total_index_shards = len(index_shards)
    _write_progress(
        cache_dir,
        {
            **_read_progress(cache_dir),
            "phase": "recompute_running",
            "workers": workers,
            "total_index_shards": total_index_shards,
            "done_index_shards": skipped_existing,
            "pending_shards": len(pending),
            "skipped_existing_shards": skipped_existing,
            "completed_now_shards": 0,
            "files_done_now": 0,
        },
    )

    if pending:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            inflight = {
                ex.submit(_process_index_shard, str(index_path), str(out_path)): (index_path, out_path)
                for index_path, out_path in pending[:workers]
            }
            next_idx = workers
            while inflight:
                done, _ = wait(list(inflight.keys()), return_when=FIRST_COMPLETED)
                for fut in done:
                    result = fut.result()
                    inflight.pop(fut)
                    completed_now += int(result["status"] == "completed")
                    skipped_existing += int(result["status"] == "skipped_existing")
                    files_done_now += int(result["files_done"])
                    done_count = skipped_existing + completed_now
                    pending_count = total_index_shards - done_count
                    print(
                        json.dumps(
                            {
                                "stage": "full_clean_recompute",
                                "index_shard": result["index_shard"],
                                "status": result["status"],
                                "files_done_in_shard": result["files_done"],
                                "done_index_shards": done_count,
                                "total_index_shards": total_index_shards,
                                "pending_shards": pending_count,
                            },
                            ensure_ascii=False,
                        )
                    )
                    _write_progress(
                        cache_dir,
                        {
                            **_read_progress(cache_dir),
                            "phase": "recompute_running",
                            "workers": workers,
                            "total_index_shards": total_index_shards,
                            "done_index_shards": done_count,
                            "pending_shards": pending_count,
                            "skipped_existing_shards": skipped_existing,
                            "completed_now_shards": completed_now,
                            "files_done_now": files_done_now,
                        },
                    )
                    if next_idx < len(pending):
                        next_index, next_out = pending[next_idx]
                        inflight[ex.submit(_process_index_shard, str(next_index), str(next_out))] = (next_index, next_out)
                        next_idx += 1

    meta = {
        "phase": "recompute_done",
        "workers": workers,
        "total_index_shards": total_index_shards,
        "done_index_shards": len(list(raw_dir.glob("raw_metrics_*.parquet"))),
        "pending_shards": max(total_index_shards - len(list(raw_dir.glob("raw_metrics_*.parquet"))), 0),
        "skipped_existing_shards": skipped_existing,
        "completed_now_shards": completed_now,
        "files_done_now": files_done_now,
    }
    _write_progress(cache_dir, {**_read_progress(cache_dir), **meta})
    return meta


def run_finalize_phase(cache_dir: Path, workers: int) -> dict:
    raw_dir = _raw_dir(cache_dir)
    policy_summary, coverage_summary = _aggregate_existing_raw_metrics(raw_dir)
    _write_df(policy_summary, cache_dir / "layer6_policy_summary_full.parquet")
    _write_df(coverage_summary, cache_dir / "layer2_coverage_summary_full.parquet")

    integrity_summary_path = cache_dir / "layer1_integrity_summary.parquet"
    files_total = None
    if integrity_summary_path.exists():
        integrity_summary = pd.read_parquet(integrity_summary_path)
        files_total = int(integrity_summary.loc[integrity_summary["metric"].eq("files_total"), "value"].iloc[0])

    manifest = {
        "built_at_utc": _utcnow_iso(),
        "mode": "full_clean_lt1b",
        "current_parquet": str(CURRENT_PARQUET_CD),
        "target_lt1b_path": str(TARGET_LT1B_PATH),
        "cache_dir": str(cache_dir),
        "workers": workers,
        "files_total": files_total,
        "total_index_shards": len(list(_index_dir(cache_dir).glob("index_*.parquet"))),
        "raw_metric_shards_written": len(list(raw_dir.glob("raw_metrics_*.parquet"))),
        "artifacts": sorted([p.name for p in cache_dir.glob("*.parquet")]),
        "subdirs": sorted([p.name for p in cache_dir.iterdir() if p.is_dir()]),
    }
    _manifest_path(cache_dir).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_progress(cache_dir, {**_read_progress(cache_dir), "phase": "done", "workers": workers, "manifest_written": True})
    return manifest


def build_full_clean_lt1b(
    current_parquet: Path = CURRENT_PARQUET_CD,
    target_lt1b_path: Path = TARGET_LT1B_PATH,
    cache_dir: Path = DEFAULT_CACHE_DIR,
    batch_size: int = 50_000,
    index_shard_size: int = 100_000,
    sample_per_stratum: int = 20,
    max_batches: int | None = None,
    workers: int = 4,
    limit_shards: int | None = None,
    force_rebuild_index: bool = False,
) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    _write_progress(
        cache_dir,
        {
            **_read_progress(cache_dir),
            "phase": "starting",
            "workers": workers,
            "batch_size": batch_size,
            "index_shard_size": index_shard_size,
            "sample_per_stratum": sample_per_stratum,
            "max_batches": max_batches,
            "limit_shards": limit_shards,
            "force_rebuild_index": force_rebuild_index,
        },
    )
    run_index_phase(
        cache_dir=cache_dir,
        current_parquet=current_parquet,
        target_lt1b_path=target_lt1b_path,
        batch_size=batch_size,
        index_shard_size=index_shard_size,
        sample_per_stratum=sample_per_stratum,
        max_batches=max_batches,
        force_rebuild_index=force_rebuild_index,
    )
    run_recompute_phase(cache_dir=cache_dir, workers=workers, limit_shards=limit_shards)
    return run_finalize_phase(cache_dir=cache_dir, workers=workers)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-parquet", type=Path, default=CURRENT_PARQUET_CD)
    parser.add_argument("--target-lt1b-path", type=Path, default=TARGET_LT1B_PATH)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--batch-size", type=int, default=50_000)
    parser.add_argument("--index-shard-size", type=int, default=100_000)
    parser.add_argument("--sample-per-stratum", type=int, default=20)
    parser.add_argument("--max-batches", type=int, default=None)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit-shards", type=int, default=None)
    parser.add_argument("--force-rebuild-index", action="store_true")
    args = parser.parse_args()

    manifest = build_full_clean_lt1b(
        current_parquet=args.current_parquet,
        target_lt1b_path=args.target_lt1b_path,
        cache_dir=args.cache_dir,
        batch_size=args.batch_size,
        index_shard_size=args.index_shard_size,
        sample_per_stratum=args.sample_per_stratum,
        max_batches=args.max_batches,
        workers=args.workers,
        limit_shards=args.limit_shards,
        force_rebuild_index=args.force_rebuild_index,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
