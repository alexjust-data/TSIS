from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return {} if default is None else dict(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {} if default is None else dict(default)


def load_events(events_dir: Path, manifest: dict[str, Any], checkpoint: dict[str, Any]) -> tuple[pd.DataFrame, list[str], list[str]]:
    confirmed_files: list[Path] = []
    confirmed_names: list[str] = []
    batch_entries = manifest.get("batch_files", []) if isinstance(manifest, dict) else []

    for entry in batch_entries:
        path = Path(str(entry.get("path", "")).strip())
        if path.exists() and path.parent == events_dir:
            confirmed_files.append(path)
            confirmed_names.append(path.name)

    if not confirmed_files:
        confirmed_files = sorted(events_dir.glob("batch_*.parquet"))
        confirmed_names = [path.name for path in confirmed_files]

    seen_set = set(confirmed_names)
    all_files = sorted(events_dir.glob("batch_*.parquet"))
    skipped_names = [path.name for path in all_files if path.name not in seen_set]

    if not confirmed_files:
        return pd.DataFrame(), [], skipped_names

    frames = [pd.read_parquet(path) for path in confirmed_files]
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return df, confirmed_names, skipped_names


def load_inventory(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Inventory parquet not found: {path}")
    return pd.read_parquet(path)


def parse_json_field(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


def json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if pd.isna(value):
        return None
    return str(value)


def stable_json_text(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=json_default)


def normalize_events(events_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return events_df
    out = events_df.copy()
    out["processed_at_utc"] = pd.to_datetime(out["processed_at_utc"], utc=True, errors="coerce")
    for col in ["issues", "warns", "metrics_json"]:
        if col in out.columns:
            out[col] = out[col].map(parse_json_field)
    return out


def prepare_for_write(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    for col in ["issues", "warns", "metrics_json"]:
        if col in out.columns:
            out[col] = out[col].map(stable_json_text)
    return out


def derive_current(events_df: pd.DataFrame) -> pd.DataFrame:
    if events_df.empty:
        return events_df.copy()
    out = events_df.sort_values(["file", "processed_at_utc", "batch_id"]).drop_duplicates(subset=["file"], keep="last").reset_index(drop=True)
    out["current_as_of_utc"] = utc_now()
    return out


def derive_task_presence(inventory_df: pd.DataFrame) -> pd.DataFrame:
    inv = inventory_df.copy()
    inv["root_upper"] = inv["root"].astype(str).str.upper()
    grouped = inv.groupby("task_key", dropna=False)
    rows = []
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


def enrich_current_with_inventory(current_df: pd.DataFrame, inventory_df: pd.DataFrame) -> pd.DataFrame:
    if current_df.empty:
        return current_df.copy()
    inv_cols = ["file", "root", "root_path", "relpath", "ticker", "date", "task_key", "size_bytes", "mtime_utc"]
    inv_file = inventory_df[inv_cols].drop_duplicates(subset=["file"])
    task_presence = derive_task_presence(inventory_df)
    out = current_df.merge(inv_file, on="file", how="left", suffixes=("", "_inventory"))
    if "task_key" in out.columns:
        out = out.merge(task_presence, on="task_key", how="left")
    return out


def derive_retry_current(current_df: pd.DataFrame) -> pd.DataFrame:
    if current_df.empty:
        return current_df.copy()
    out = current_df[current_df["severity"].astype(str) != "PASS"].copy()
    out["retry_attempts_effective"] = 0
    out["retry_policy_status"] = "active_retry_candidate"
    out["last_retry_at_utc"] = pd.NaT
    return out.reset_index(drop=True)


def derive_retry_frozen(current_df: pd.DataFrame) -> pd.DataFrame:
    cols = list(current_df.columns) if not current_df.empty else ["file", "severity", "issues", "warns", "processed_at_utc"]
    out = pd.DataFrame(columns=cols)
    if "retry_attempts_effective" not in out.columns:
        out["retry_attempts_effective"] = pd.Series(dtype="int64")
    if "freeze_reason" not in out.columns:
        out["freeze_reason"] = pd.Series(dtype="object")
    if "frozen_at_utc" not in out.columns:
        out["frozen_at_utc"] = pd.Series(dtype="datetime64[ns, UTC]")
    return out


def detect_completion_status(manifest: dict[str, Any], checkpoint: dict[str, Any], validation_summary: dict[str, Any]) -> tuple[str, str]:
    manifest_finalized = bool(manifest.get("finalized", False))
    expected_batches = int(validation_summary.get("batches_written", 0) or 0)
    confirmed_batches = len(manifest.get("batch_files", [])) if isinstance(manifest.get("batch_files", []), list) else 0
    checkpoint_batches = int(checkpoint.get("completed_batches_count", 0) or 0)

    if manifest_finalized and expected_batches > 0 and confirmed_batches >= expected_batches:
        return "completed", "final"
    if confirmed_batches > 0 or checkpoint_batches > 0:
        return "partial", "partial"
    return "empty", "partial"


def make_live_status(
    run_id: str,
    current_df: pd.DataFrame,
    retry_current_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    validation_summary: dict[str, Any],
    manifest: dict[str, Any],
    checkpoint: dict[str, Any],
    outdir: Path,
    confirmed_batch_names: list[str],
    materialization_scope: str,
    validation_completion_status: str,
) -> dict[str, Any]:
    sev_counts = {}
    if not current_df.empty and "severity" in current_df.columns:
        sev_counts = {str(k): int(v) for k, v in current_df["severity"].value_counts(dropna=False).to_dict().items()}
    return {
        "run_id": run_id,
        "updated_utc": utc_now(),
        "materialization_utc": utc_now(),
        "backend_mode": "duckdb_parquet_contract_v2_materialized_exports",
        "current_materialized_from": str(outdir / "trades_current.parquet"),
        "retry_materialized_from": str(outdir / "retry_current.parquet"),
        "validation_checkpoint_source": str(outdir / "validation_checkpoint.json"),
        "validation_manifest_source": str(outdir / "validation_run_manifest.json"),
        "validation_completion_status": validation_completion_status,
        "materialization_scope": materialization_scope,
        "batches_seen": int(len(confirmed_batch_names)),
        "batches_expected": int(validation_summary.get("batches_written", 0) or 0),
        "files_discovered_total": int(len(inventory_df)),
        "files_pending": 0,
        "files_current_snapshot": int(len(current_df)),
        "severity_counts_current": sev_counts,
        "retry_pending_files_current": int(len(retry_current_df)),
        "validation_summary_source": validation_summary,
        "validation_checkpoint_state": checkpoint,
        "validation_manifest_state": {
            "finalized": bool(manifest.get("finalized", False)),
            "batch_files_count": len(manifest.get("batch_files", [])) if isinstance(manifest.get("batch_files", []), list) else 0,
        },
    }


def write_outputs(outdir: Path, current_df: pd.DataFrame, retry_current_df: pd.DataFrame, retry_frozen_df: pd.DataFrame, live_status: dict[str, Any]) -> None:
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

    (outdir / "live_status_trades_strict.json").write_text(json.dumps(live_status, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Materialize current/retry/live state from trades v2 append-only events")
    ap.add_argument("--validation-outdir", required=True)
    ap.add_argument("--inventory-parquet", required=True)
    ap.add_argument("--outdir", default="")
    ap.add_argument("--run-id", default="trades_v2_materialize_v020")
    args = ap.parse_args()

    validation_outdir = Path(args.validation_outdir)
    events_dir = validation_outdir / "events_batches"
    outdir = Path(args.outdir) if str(args.outdir).strip() else validation_outdir

    manifest_path = validation_outdir / "validation_run_manifest.json"
    checkpoint_path = validation_outdir / "validation_checkpoint.json"
    validation_summary_path = validation_outdir / "validation_run_summary.json"

    manifest = load_json(manifest_path, default={})
    checkpoint = load_json(checkpoint_path, default={})
    validation_summary = load_json(validation_summary_path, default={})

    inventory_df = load_inventory(Path(args.inventory_parquet))
    events_raw_df, confirmed_batch_names, skipped_batch_names = load_events(events_dir, manifest, checkpoint)
    events_df = normalize_events(events_raw_df)
    current_df = derive_current(events_df)
    current_df = enrich_current_with_inventory(current_df, inventory_df)
    retry_current_df = derive_retry_current(current_df)
    retry_frozen_df = derive_retry_frozen(current_df)

    validation_completion_status, materialization_scope = detect_completion_status(manifest, checkpoint, validation_summary)
    live_status = make_live_status(
        args.run_id,
        current_df,
        retry_current_df,
        inventory_df,
        validation_summary,
        manifest,
        checkpoint,
        outdir,
        confirmed_batch_names,
        materialization_scope,
        validation_completion_status,
    )
    write_outputs(outdir, current_df, retry_current_df, retry_frozen_df, live_status)

    summary = {
        "run_id": args.run_id,
        "materialized_at_utc": utc_now(),
        "validation_outdir": str(validation_outdir),
        "inventory_parquet": str(Path(args.inventory_parquet)),
        "outdir": str(outdir),
        "events_rows": int(len(events_df)),
        "current_rows": int(len(current_df)),
        "retry_current_rows": int(len(retry_current_df)),
        "retry_frozen_rows": int(len(retry_frozen_df)),
        "batches_read": int(len(confirmed_batch_names)),
        "batches_read_names": confirmed_batch_names,
        "batches_skipped_names": skipped_batch_names,
        "materialization_mode": materialization_scope,
        "validation_completion_status": validation_completion_status,
        "validation_checkpoint_source": str(checkpoint_path) if checkpoint_path.exists() else "",
        "validation_manifest_source": str(manifest_path) if manifest_path.exists() else "",
    }
    (outdir / "materialization_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

