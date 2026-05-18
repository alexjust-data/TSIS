from __future__ import annotations

import argparse
import json
import random
import runpy
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
SCRIPT_57F = BASE_DIR / "57f_build_trades_file_acceptance_artifacts_lt1b_fast_same_schema.py"
_mod57f = runpy.run_path(str(SCRIPT_57F))

compute_raw_metrics_for_sample_row = _mod57f["compute_raw_metrics_for_sample_row"]
classify_acceptance = _mod57f["classify_acceptance"]


DEFAULT_CACHE_DIR = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean"
)


def _index_path(cache_dir: Path, shard_id: int) -> Path:
    return cache_dir / "full_index_shards" / f"index_{shard_id:05d}.parquet"


def _raw_path(cache_dir: Path, shard_id: int) -> Path:
    return cache_dir / "raw_metrics_shards" / f"raw_metrics_{shard_id:05d}.parquet"


def _values_equal(a, b) -> bool:
    if pd.isna(a) and pd.isna(b):
        return True
    return a == b


def validate_shard(cache_dir: Path, shard_id: int, sample_size: int, seed: int) -> dict:
    index_df = pd.read_parquet(_index_path(cache_dir, shard_id))
    raw_df = pd.read_parquet(_raw_path(cache_dir, shard_id))
    if len(index_df) != len(raw_df):
        return {
            "shard_id": shard_id,
            "status": "length_mismatch",
            "index_rows": int(len(index_df)),
            "raw_rows": int(len(raw_df)),
        }

    rng = random.Random(seed + shard_id)
    positions = list(range(len(index_df)))
    rng.shuffle(positions)
    positions = sorted(positions[: min(sample_size, len(index_df))])

    mismatches: list[dict] = []
    sample_rows: list[dict] = []
    raw_columns = list(raw_df.columns)
    generated_columns = None

    for pos in positions:
        index_row = index_df.iloc[pos]
        expected = raw_df.iloc[pos].to_dict()
        got = compute_raw_metrics_for_sample_row(index_row)
        got["acceptance_label"] = classify_acceptance(got)
        sample_rows.append(got)
        if generated_columns is None:
            generated_columns = list(got.keys())

        bad = [k for k in expected.keys() if not _values_equal(expected.get(k), got.get(k))]
        if bad:
            mismatches.append(
                {
                    "position": int(pos),
                    "file": str(index_row["file"]),
                    "mismatch_columns": bad[:20],
                }
            )
            if len(mismatches) >= 10:
                break

    generated_df = pd.DataFrame(sample_rows)
    return {
        "shard_id": shard_id,
        "status": "ok" if not mismatches else "value_mismatch",
        "sample_size": int(len(positions)),
        "raw_column_order_matches_generated": raw_columns == list(generated_df.columns),
        "raw_columns_count": int(len(raw_columns)),
        "generated_columns_count": int(len(generated_df.columns)),
        "mismatch_count": int(len(mismatches)),
        "mismatches": mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--shards", type=int, nargs="+", required=True)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    reports = [validate_shard(args.cache_dir, shard_id, args.sample_size, args.seed) for shard_id in args.shards]
    summary = {
        "cache_dir": str(args.cache_dir),
        "shards": args.shards,
        "sample_size": args.sample_size,
        "all_ok": all(r["status"] == "ok" and r["raw_column_order_matches_generated"] for r in reports),
        "reports": reports,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
