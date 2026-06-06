from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Shard manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    return pd.read_parquet(path)


def concat_parquets(paths: list[Path]) -> pd.DataFrame:
    frames = [pd.read_parquet(p) for p in paths]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def maybe_concat(paths: list[Path]) -> pd.DataFrame:
    existing = [p for p in paths if p.exists()]
    return concat_parquets(existing) if existing else pd.DataFrame()


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge sharded quotes_current outputs and verify integrity")
    ap.add_argument("--shards-manifest", required=True)
    ap.add_argument("--inventory-parquet", required=True)
    ap.add_argument("--validation-root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--run-id-prefix", default="quotes_validate_2005_2026_d_full_shard_")
    ap.add_argument("--num-shards", type=int, default=8)
    args = ap.parse_args()

    manifest = load_manifest(Path(args.shards_manifest))
    inventory = load_inventory(Path(args.inventory_parquet))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    validation_root = Path(args.validation_root)

    current_paths: list[Path] = []
    retry_paths: list[Path] = []
    shard_rows: list[dict[str, Any]] = []

    for shard_id in range(1, int(args.num_shards) + 1):
        run_id = f"{args.run_id_prefix}{shard_id:02d}_of_{int(args.num_shards):02d}"
        shard_dir = validation_root / run_id
        current_path = shard_dir / "quotes_current.parquet"
        retry_path = shard_dir / "retry_current.parquet"
        summary_path = shard_dir / "materialization_summary.json"

        if not current_path.exists():
            raise FileNotFoundError(f"Missing shard current parquet: {current_path}")

        current_paths.append(current_path)
        if retry_path.exists():
            retry_paths.append(retry_path)

        summary = {}
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        shard_rows.append(
            {
                "shard_id": shard_id,
                "run_id": run_id,
                "shard_dir": str(shard_dir),
                "quotes_current_parquet": str(current_path),
                "retry_current_parquet": str(retry_path) if retry_path.exists() else None,
                "current_rows": summary.get("current_rows"),
                "retry_current_rows": summary.get("retry_current_rows"),
            }
        )

    current_df = concat_parquets(current_paths)
    retry_df = maybe_concat(retry_paths)

    expected_inventory = inventory.copy()
    expected_inventory["task_key"] = expected_inventory["task_key"].astype(str)
    expected_filtered = expected_inventory["task_key"].nunique()

    merged_task_keys = current_df["task_key"].astype(str).nunique() if "task_key" in current_df.columns else None
    merged_files = current_df["file"].astype(str).nunique() if "file" in current_df.columns else None

    if "task_key" not in current_df.columns:
        raise ValueError("Merged quotes_current is missing task_key")
    if "file" not in current_df.columns:
        raise ValueError("Merged quotes_current is missing file")

    dup_task_key_rows = current_df["task_key"].astype(str).duplicated().sum()
    dup_file_rows = current_df["file"].astype(str).duplicated().sum()

    verification = {
        "merged_at_utc": utc_now(),
        "shards_manifest": str(Path(args.shards_manifest)),
        "inventory_parquet": str(Path(args.inventory_parquet)),
        "validation_root": str(validation_root),
        "outdir": str(outdir),
        "num_shards": int(args.num_shards),
        "expected_inventory_task_keys": int(expected_filtered),
        "merged_current_rows": int(len(current_df)),
        "merged_current_task_keys": int(merged_task_keys),
        "merged_current_files": int(merged_files),
        "duplicate_task_key_rows": int(dup_task_key_rows),
        "duplicate_file_rows": int(dup_file_rows),
        "retry_rows": int(len(retry_df)),
        "verification_passed": bool(
            len(current_df) == expected_filtered
            and merged_task_keys == expected_filtered
            and merged_files == expected_filtered
            and dup_task_key_rows == 0
            and dup_file_rows == 0
        ),
    }

    if not verification["verification_passed"]:
        missing_task_keys = sorted(
            set(expected_inventory["task_key"].astype(str))
            - set(current_df["task_key"].astype(str))
        )
        extra_task_keys = sorted(
            set(current_df["task_key"].astype(str))
            - set(expected_inventory["task_key"].astype(str))
        )
        pd.DataFrame({"task_key": missing_task_keys}).to_csv(outdir / "missing_task_keys.csv", index=False)
        pd.DataFrame({"task_key": extra_task_keys}).to_csv(outdir / "extra_task_keys.csv", index=False)
        raise ValueError(json.dumps(verification, indent=2))

    write_json(outdir / "merge_verification_summary.json", verification)
    current_df.to_parquet(outdir / "quotes_current.parquet", index=False)
    retry_df.to_parquet(outdir / "retry_current.parquet", index=False)
    pd.DataFrame(shard_rows).to_csv(outdir / "merged_shards_summary.csv", index=False)
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
