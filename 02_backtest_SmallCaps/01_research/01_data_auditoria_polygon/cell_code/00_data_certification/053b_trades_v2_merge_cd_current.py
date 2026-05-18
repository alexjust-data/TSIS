from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(message: str) -> None:
    print(f"[{utc_now()}] {message}", flush=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    return pd.read_parquet(path)


def concat_parquets(paths: list[Path], label: str = "parquets") -> pd.DataFrame:
    frames = []
    total = len(paths)
    for idx, p in enumerate(paths, start=1):
        log(f"Reading {label} [{idx}/{total}]: {p}")
        frames.append(pd.read_parquet(p))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def maybe_concat(paths: list[Path], label: str = "parquets") -> pd.DataFrame:
    existing = [p for p in paths if p.exists()]
    return concat_parquets(existing, label=label) if existing else pd.DataFrame()


def ensure_unique(df: pd.DataFrame, col: str, label: str) -> int:
    if col not in df.columns:
        raise ValueError(f"{label} is missing required column: {col}")
    return int(df[col].astype(str).duplicated().sum())


def build_presence_flags(inventory_df: pd.DataFrame) -> pd.DataFrame:
    inv = inventory_df.copy()
    inv["root_upper"] = inv["root"].astype(str).str.upper()
    grouped = inv.groupby("task_key", dropna=False)
    rows: list[dict[str, Any]] = []
    for task_key, grp in grouped:
        roots = set(grp["root_upper"].tolist())
        rows.append(
            {
                "task_key": task_key,
                "present_in_c": "C" in roots,
                "present_in_d": "D" in roots,
                "present_in_both": ("C" in roots and "D" in roots),
            }
        )
    return pd.DataFrame(rows)


def enrich_with_inventory(current_df: pd.DataFrame, inventory_df: pd.DataFrame, source_population: str) -> pd.DataFrame:
    if current_df.empty:
        out = current_df.copy()
        out["source_population"] = pd.Series(dtype="object")
        return out
    inv_cols = ["file", "root", "root_path", "relpath", "ticker", "date", "task_key", "size_bytes", "mtime_utc"]
    inv_file = inventory_df[inv_cols].drop_duplicates(subset=["file"])
    task_presence = build_presence_flags(inventory_df)
    out = current_df.copy()

    # 053 materialization already writes most inventory fields into current/retry exports.
    # Only inject inventory columns that are actually missing to avoid duplicate column names.
    merge_cols = ["file"]
    rename_map: dict[str, str] = {}
    for col in inv_cols:
        if col == "file":
            continue
        if col in out.columns:
            continue
        target_col = f"{col}_inventory" if f"{col}_inventory" not in out.columns else None
        if target_col is None:
            continue
        merge_cols.append(col)
        rename_map[col] = target_col if col in {"ticker", "date"} else col

    if len(merge_cols) > 1:
        inv_merge = inv_file[merge_cols].rename(columns=rename_map)
        out = out.merge(inv_merge, on="file", how="left")

    if "task_key" in out.columns:
        out = out.drop(columns=[c for c in ["present_in_c", "present_in_d", "present_in_both"] if c in out.columns])
        out = out.merge(task_presence, on="task_key", how="left")
    out["source_population"] = source_population
    return out


def prepare_for_write(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    for col in ["issues", "warns", "metrics_json"]:
        if col in out.columns:
            out[col] = out[col].map(
                lambda value: value
                if isinstance(value, str)
                else ("" if value is None or (isinstance(value, float) and pd.isna(value)) else json.dumps(value, ensure_ascii=False, sort_keys=True, default=str))
            )
    return out


def write_outputs(
    outdir: Path,
    current_df: pd.DataFrame,
    retry_current_df: pd.DataFrame,
    retry_frozen_df: pd.DataFrame,
    live_status: dict[str, Any],
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    current_write = prepare_for_write(current_df)
    retry_current_write = prepare_for_write(retry_current_df)
    retry_frozen_write = prepare_for_write(retry_frozen_df)

    current_write.to_parquet(outdir / "trades_current.parquet", index=False)
    current_write.to_csv(outdir / "trades_current.csv", index=False)
    retry_current_write.to_parquet(outdir / "retry_current.parquet", index=False)
    retry_current_write.to_csv(outdir / "retry_current.csv", index=False)
    retry_frozen_write.to_parquet(outdir / "retry_frozen.parquet", index=False)
    retry_frozen_write.to_csv(outdir / "retry_frozen.csv", index=False)

    current_write.to_csv(outdir / "trades_agent_strict_events_current.csv", index=False)
    retry_current_write.to_csv(outdir / "retry_queue_trades_strict_current.csv", index=False)
    retry_frozen_write.to_csv(outdir / "retry_frozen_trades_strict.csv", index=False)

    write_json(outdir / "live_status_trades_strict.json", live_status)


def main() -> None:
    ap = argparse.ArgumentParser(description="Merge trades D monolithic current with C sharded current and verify integrity")
    ap.add_argument("--d-validation-outdir", required=True)
    ap.add_argument("--d-inventory-parquet", required=True)
    ap.add_argument("--c-shards-manifest", required=True)
    ap.add_argument("--c-validation-root", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--c-run-id-prefix", default="trades_validate_2005_2026_c_full_shard_")
    ap.add_argument("--num-c-shards", type=int, default=20)
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    log(f"Starting trades CD merge into: {outdir}")

    d_validation_outdir = Path(args.d_validation_outdir)
    d_current_path = d_validation_outdir / "trades_current.parquet"
    d_retry_current_path = d_validation_outdir / "retry_current.parquet"
    d_retry_frozen_path = d_validation_outdir / "retry_frozen.parquet"
    if not d_current_path.exists():
        raise FileNotFoundError(f"Missing D current parquet: {d_current_path}")
    log(f"D current source: {d_current_path}")

    c_manifest = load_json(Path(args.c_shards_manifest))
    c_inventory_paths = [Path(str(entry["shard_path"])) for entry in c_manifest.get("shards", [])]
    if len(c_inventory_paths) != int(args.num_c_shards):
        raise ValueError(f"Expected {args.num_c_shards} C shard inventory paths, found {len(c_inventory_paths)}")
    log(f"Loaded C shards manifest with {len(c_inventory_paths)} inventory shards")

    c_validation_root = Path(args.c_validation_root)
    c_current_paths: list[Path] = []
    c_retry_current_paths: list[Path] = []
    c_retry_frozen_paths: list[Path] = []
    c_rows: list[dict[str, Any]] = []

    for shard_id in range(1, int(args.num_c_shards) + 1):
        run_id = f"{args.c_run_id_prefix}{shard_id:02d}_of_{int(args.num_c_shards):02d}"
        shard_dir = c_validation_root / run_id
        current_path = shard_dir / "trades_current.parquet"
        retry_current_path = shard_dir / "retry_current.parquet"
        retry_frozen_path = shard_dir / "retry_frozen.parquet"
        summary_path = shard_dir / "materialization_summary.json"

        if not current_path.exists():
            raise FileNotFoundError(f"Missing C shard current parquet: {current_path}")

        log(f"Discovered C shard [{shard_id}/{int(args.num_c_shards)}]: {shard_dir}")

        c_current_paths.append(current_path)
        if retry_current_path.exists():
            c_retry_current_paths.append(retry_current_path)
        if retry_frozen_path.exists():
            c_retry_frozen_paths.append(retry_frozen_path)

        summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
        c_rows.append(
            {
                "source_population": "C_full_sharded",
                "shard_id": shard_id,
                "run_id": run_id,
                "shard_dir": str(shard_dir),
                "current_rows": summary.get("current_rows"),
                "retry_current_rows": summary.get("retry_current_rows"),
                "retry_frozen_rows": summary.get("retry_frozen_rows"),
            }
        )

    log("Loading exact D inventory")
    d_inventory_df = load_inventory(Path(args.d_inventory_parquet))
    log(f"D inventory rows loaded: {len(d_inventory_df)}")
    log("Loading exact C inventory shards")
    c_inventory_df = concat_parquets(c_inventory_paths, label="C inventory shards")
    log(f"C inventory rows loaded: {len(c_inventory_df)}")

    log("Loading and enriching D current")
    d_current_df = enrich_with_inventory(pd.read_parquet(d_current_path), d_inventory_df, "D_full_monolithic")
    log(f"D current rows loaded: {len(d_current_df)}")
    d_retry_current_df = enrich_with_inventory(pd.read_parquet(d_retry_current_path), d_inventory_df, "D_full_monolithic") if d_retry_current_path.exists() else pd.DataFrame()
    d_retry_frozen_df = enrich_with_inventory(pd.read_parquet(d_retry_frozen_path), d_inventory_df, "D_full_monolithic") if d_retry_frozen_path.exists() else pd.DataFrame()

    log("Loading and enriching C current shards")
    c_current_df = enrich_with_inventory(concat_parquets(c_current_paths, label="C current shards"), c_inventory_df, "C_full_sharded")
    log(f"C current rows loaded: {len(c_current_df)}")
    c_retry_current_df = enrich_with_inventory(maybe_concat(c_retry_current_paths, label="C retry_current shards"), c_inventory_df, "C_full_sharded")
    c_retry_frozen_df = enrich_with_inventory(maybe_concat(c_retry_frozen_paths, label="C retry_frozen shards"), c_inventory_df, "C_full_sharded")

    d_expected = int(d_inventory_df["task_key"].astype(str).nunique())
    c_expected = int(c_inventory_df["task_key"].astype(str).nunique())
    log(f"Expected task_keys: D={d_expected}, C={c_expected}")

    verification: dict[str, Any] = {
        "merged_at_utc": utc_now(),
        "d_validation_outdir": str(d_validation_outdir),
        "d_inventory_parquet": str(Path(args.d_inventory_parquet)),
        "c_shards_manifest": str(Path(args.c_shards_manifest)),
        "c_validation_root": str(c_validation_root),
        "outdir": str(outdir),
        "num_c_shards": int(args.num_c_shards),
        "d_expected_task_keys": d_expected,
        "c_expected_task_keys": c_expected,
        "d_current_rows": int(len(d_current_df)),
        "c_current_rows": int(len(c_current_df)),
        "d_duplicate_task_key_rows": ensure_unique(d_current_df, "task_key", "D current"),
        "d_duplicate_file_rows": ensure_unique(d_current_df, "file", "D current"),
        "c_duplicate_task_key_rows": ensure_unique(c_current_df, "task_key", "C current"),
        "c_duplicate_file_rows": ensure_unique(c_current_df, "file", "C current"),
    }

    d_task_keys = set(d_current_df["task_key"].astype(str))
    c_task_keys = set(c_current_df["task_key"].astype(str))
    d_files = set(d_current_df["file"].astype(str))
    c_files = set(c_current_df["file"].astype(str))

    overlap_task_keys = sorted(d_task_keys & c_task_keys)
    overlap_files = sorted(d_files & c_files)
    log(f"Overlap counts: task_keys={len(overlap_task_keys)}, files={len(overlap_files)}")

    log("Concatenating merged current/retry outputs")
    merged_current = pd.concat([d_current_df, c_current_df], ignore_index=True)
    merged_retry_current = pd.concat([df for df in [d_retry_current_df, c_retry_current_df] if not df.empty], ignore_index=True) if (not d_retry_current_df.empty or not c_retry_current_df.empty) else pd.DataFrame()
    merged_retry_frozen = pd.concat([df for df in [d_retry_frozen_df, c_retry_frozen_df] if not df.empty], ignore_index=True) if (not d_retry_frozen_df.empty or not c_retry_frozen_df.empty) else pd.DataFrame()
    log(f"Merged rows: current={len(merged_current)}, retry_current={len(merged_retry_current)}, retry_frozen={len(merged_retry_frozen)}")

    verification.update(
        {
            "d_task_keys_current": int(len(d_task_keys)),
            "c_task_keys_current": int(len(c_task_keys)),
            "overlap_task_keys_cd": int(len(overlap_task_keys)),
            "overlap_files_cd": int(len(overlap_files)),
            "merged_current_rows": int(len(merged_current)),
            "merged_current_task_keys": int(merged_current["task_key"].astype(str).nunique()),
            "merged_current_files": int(merged_current["file"].astype(str).nunique()),
            "merged_retry_current_rows": int(len(merged_retry_current)),
            "merged_retry_frozen_rows": int(len(merged_retry_frozen)),
            "merged_duplicate_task_key_rows": int(merged_current["task_key"].astype(str).duplicated().sum()),
            "merged_duplicate_file_rows": int(merged_current["file"].astype(str).duplicated().sum()),
        }
    )

    verification["verification_passed"] = bool(
        verification["d_current_rows"] == d_expected
        and verification["c_current_rows"] == c_expected
        and verification["d_duplicate_task_key_rows"] == 0
        and verification["d_duplicate_file_rows"] == 0
        and verification["c_duplicate_task_key_rows"] == 0
        and verification["c_duplicate_file_rows"] == 0
        and verification["overlap_task_keys_cd"] == 0
        and verification["overlap_files_cd"] == 0
        and verification["merged_duplicate_task_key_rows"] == 0
        and verification["merged_duplicate_file_rows"] == 0
        and verification["merged_current_rows"] == (d_expected + c_expected)
        and verification["merged_current_task_keys"] == (d_expected + c_expected)
        and verification["merged_current_files"] == (d_expected + c_expected)
    )

    pd.DataFrame(c_rows).to_csv(outdir / "merged_sources_summary.csv", index=False)

    if overlap_task_keys:
        pd.DataFrame({"task_key": overlap_task_keys}).to_csv(outdir / "overlap_task_keys_cd.csv", index=False)
    if overlap_files:
        pd.DataFrame({"file": overlap_files}).to_csv(outdir / "overlap_files_cd.csv", index=False)
    dup_task_keys = merged_current.loc[merged_current["task_key"].astype(str).duplicated(keep=False), ["task_key", "file", "source_population"]].copy()
    dup_files = merged_current.loc[merged_current["file"].astype(str).duplicated(keep=False), ["file", "task_key", "source_population"]].copy()
    if not dup_task_keys.empty:
        dup_task_keys.to_csv(outdir / "duplicate_task_keys.csv", index=False)
    if not dup_files.empty:
        dup_files.to_csv(outdir / "duplicate_files.csv", index=False)

    if not verification["verification_passed"]:
        log("Verification failed; writing diagnostic summary")
        write_json(outdir / "merge_verification_summary.json", verification)
        raise ValueError(json.dumps(verification, indent=2))

    sev_counts = {str(k): int(v) for k, v in merged_current["severity"].value_counts(dropna=False).to_dict().items()} if "severity" in merged_current.columns else {}
    live_status = {
        "run_id": "trades_current_cd_merged",
        "updated_utc": utc_now(),
        "materialization_utc": utc_now(),
        "backend_mode": "duckdb_parquet_contract_v2_materialized_exports",
        "current_materialized_from": str(outdir / "trades_current.parquet"),
        "retry_materialized_from": str(outdir / "retry_current.parquet"),
        "validation_completion_status": "completed",
        "materialization_scope": "final_cd_merge",
        "files_current_snapshot": int(len(merged_current)),
        "severity_counts_current": sev_counts,
        "retry_pending_files_current": int(len(merged_retry_current)),
        "source_populations": {
            "d_validation_outdir": str(d_validation_outdir),
            "c_validation_root": str(c_validation_root),
            "d_expected_task_keys": d_expected,
            "c_expected_task_keys": c_expected,
        },
    }

    log("Writing merged outputs to disk")
    write_outputs(outdir, merged_current, merged_retry_current, merged_retry_frozen, live_status)
    write_json(outdir / "merge_verification_summary.json", verification)
    log("Merge completed successfully")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
