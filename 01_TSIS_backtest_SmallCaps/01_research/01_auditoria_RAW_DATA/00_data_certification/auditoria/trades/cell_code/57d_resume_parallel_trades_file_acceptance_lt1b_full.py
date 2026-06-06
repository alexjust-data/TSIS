from __future__ import annotations

import argparse
import json
import runpy
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_57B = BASE_DIR / "57b_build_trades_file_acceptance_artifacts_lt1b.py"
SCRIPT_57C = BASE_DIR / "57c_build_trades_file_acceptance_artifacts_lt1b_full.py"

_mod57b = runpy.run_path(str(SCRIPT_57B))
_mod57c = runpy.run_path(str(SCRIPT_57C))

CURRENT_PARQUET_CD = _mod57b["CURRENT_PARQUET_CD"]
TARGET_LT1B_PATH = _mod57b["TARGET_LT1B_PATH"]
DEFAULT_CACHE_DIR = _mod57c["DEFAULT_CACHE_DIR"]

compute_raw_metrics_for_sample_row = _mod57b["compute_raw_metrics_for_sample_row"]
classify_acceptance = _mod57b["classify_acceptance"]
_utcnow_iso = _mod57b["_utcnow_iso"]
_write_df = _mod57b["_write_df"]


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
            "raw_metrics_shard": out_p.name,
            "status": "skipped_existing",
            "files_done": int(len(df)),
            "label_counts": df["acceptance_label"].value_counts().to_dict(),
        }

    index_df = pd.read_parquet(index_p)
    rows: list[dict] = []
    for _, row in index_df.iterrows():
        metrics = compute_raw_metrics_for_sample_row(row)
        metrics["acceptance_label"] = classify_acceptance(pd.Series(metrics))
        rows.append(metrics)

    out_df = pd.DataFrame(rows)
    out_df.to_parquet(out_p, index=False)
    return {
        "index_shard": index_p.name,
        "raw_metrics_shard": out_p.name,
        "status": "completed",
        "files_done": int(len(out_df)),
        "label_counts": out_df["acceptance_label"].value_counts().to_dict(),
    }


def _aggregate_existing_raw_metrics(raw_metrics_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts: dict[str, int] = {}
    files_done = 0
    files_with_1m_reference = 0
    files_with_daily_reference = 0

    for shard in sorted(raw_metrics_dir.glob("raw_metrics_*.parquet")):
        cols = ["acceptance_label", "has_1m_reference", "has_daily_reference"]
        df = pd.read_parquet(shard, columns=cols)
        files_done += int(len(df))
        for label, count in df["acceptance_label"].value_counts().to_dict().items():
            counts[label] = counts.get(label, 0) + int(count)
        files_with_1m_reference += int(df["has_1m_reference"].fillna(False).astype(bool).sum())
        files_with_daily_reference += int(df["has_daily_reference"].fillna(False).astype(bool).sum())

    policy_summary = pd.DataFrame(
        [{"acceptance_label": label, "files": count} for label, count in counts.items()]
    )
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


def _write_progress(
    cache_dir: Path,
    total_index_shards: int,
    done_index_shards: int,
    skipped_existing_shards: int,
    completed_now_shards: int,
    files_done_now: int,
    pending_shards: int,
    workers: int,
) -> None:
    progress = {
        "updated_at_utc": _utcnow_iso(),
        "mode": "resume_parallel_full_raw_lt1b",
        "total_index_shards": total_index_shards,
        "done_index_shards": done_index_shards,
        "pending_shards": pending_shards,
        "skipped_existing_shards": skipped_existing_shards,
        "completed_now_shards": completed_now_shards,
        "files_done_now": files_done_now,
        "workers": workers,
    }
    (cache_dir / "progress.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


def resume_parallel_full_raw_lt1b(
    cache_dir: Path = DEFAULT_CACHE_DIR,
    workers: int = 4,
    limit_shards: int | None = None,
) -> dict:
    index_dir = cache_dir / "full_index_shards"
    raw_metrics_dir = cache_dir / "raw_metrics_shards"
    raw_metrics_dir.mkdir(parents=True, exist_ok=True)

    index_shards = sorted(index_dir.glob("index_*.parquet"))
    if not index_shards:
        raise FileNotFoundError(f"No se encontraron index shards en {index_dir}")

    pending: list[tuple[Path, Path]] = []
    skipped_existing_shards = 0
    for index_path in index_shards:
        out_path = _raw_metrics_path_for_index(index_path, raw_metrics_dir)
        if out_path.exists():
            skipped_existing_shards += 1
            continue
        pending.append((index_path, out_path))

    if limit_shards is not None:
        pending = pending[:limit_shards]

    total_index_shards = len(index_shards)
    completed_now_shards = 0
    files_done_now = 0

    _write_progress(
        cache_dir=cache_dir,
        total_index_shards=total_index_shards,
        done_index_shards=skipped_existing_shards,
        skipped_existing_shards=skipped_existing_shards,
        completed_now_shards=0,
        files_done_now=0,
        pending_shards=len(pending),
        workers=workers,
    )

    if pending:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            future_map = {
                ex.submit(_process_index_shard, str(index_path), str(out_path)): (index_path, out_path)
                for index_path, out_path in pending[:workers]
            }
            next_idx = workers

            while future_map:
                done, _ = wait(list(future_map.keys()), return_when=FIRST_COMPLETED)
                for fut in done:
                    index_path, _ = future_map.pop(fut)
                    result = fut.result()
                    completed_now_shards += int(result["status"] == "completed")
                    skipped_existing_shards += int(result["status"] == "skipped_existing")
                    files_done_now += int(result["files_done"])

                    done_index_shards = skipped_existing_shards + completed_now_shards
                    pending_count = len(pending) - done_index_shards + skipped_existing_shards
                    print(
                        json.dumps(
                            {
                                "stage": "resume_parallel_full_raw",
                                "index_shard": result["index_shard"],
                                "status": result["status"],
                                "files_done_in_shard": result["files_done"],
                                "done_index_shards": done_index_shards,
                                "total_index_shards": total_index_shards,
                                "pending_shards": max(pending_count, 0),
                            },
                            ensure_ascii=False,
                        )
                    )
                    _write_progress(
                        cache_dir=cache_dir,
                        total_index_shards=total_index_shards,
                        done_index_shards=done_index_shards,
                        skipped_existing_shards=skipped_existing_shards,
                        completed_now_shards=completed_now_shards,
                        files_done_now=files_done_now,
                        pending_shards=max(pending_count, 0),
                        workers=workers,
                    )

                    if next_idx < len(pending):
                        next_index_path, next_out_path = pending[next_idx]
                        future_map[ex.submit(_process_index_shard, str(next_index_path), str(next_out_path))] = (next_index_path, next_out_path)
                        next_idx += 1

    policy_summary, coverage_summary = _aggregate_existing_raw_metrics(raw_metrics_dir)
    _write_df(policy_summary, cache_dir / "layer6_policy_summary_full.parquet")
    _write_df(coverage_summary, cache_dir / "layer2_coverage_summary_full.parquet")

    manifest = {
        "built_at_utc": _utcnow_iso(),
        "mode": "resume_parallel_full_raw_lt1b",
        "current_parquet": str(CURRENT_PARQUET_CD),
        "target_lt1b_path": str(TARGET_LT1B_PATH),
        "cache_dir": str(cache_dir),
        "workers": workers,
        "total_index_shards": total_index_shards,
        "raw_metric_shards_written": len(list(raw_metrics_dir.glob("raw_metrics_*.parquet"))),
        "artifacts": sorted([p.name for p in cache_dir.glob("*.parquet")]),
        "subdirs": sorted([p.name for p in cache_dir.iterdir() if p.is_dir()]),
    }
    (cache_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_progress(
        cache_dir=cache_dir,
        total_index_shards=total_index_shards,
        done_index_shards=len(list(raw_metrics_dir.glob("raw_metrics_*.parquet"))),
        skipped_existing_shards=skipped_existing_shards,
        completed_now_shards=completed_now_shards,
        files_done_now=files_done_now,
        pending_shards=max(total_index_shards - len(list(raw_metrics_dir.glob("raw_metrics_*.parquet"))), 0),
        workers=workers,
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit-shards", type=int, default=None)
    args = parser.parse_args()

    manifest = resume_parallel_full_raw_lt1b(
        cache_dir=args.cache_dir,
        workers=args.workers,
        limit_shards=args.limit_shards,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
