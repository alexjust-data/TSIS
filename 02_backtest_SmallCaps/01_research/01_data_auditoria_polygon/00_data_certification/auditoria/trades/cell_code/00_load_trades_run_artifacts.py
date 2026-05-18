from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


PAT_SINGLE = re.compile(r"'([^']+)'")
PAT_DOUBLE = re.compile(r'"([^\\"]+)"')


@dataclass
class TradesAuditHandle:
    path: Path

    def parquet(self) -> pq.ParquetFile:
        return pq.ParquetFile(self.path)

    def row_count(self) -> int:
        return self.parquet().metadata.num_rows

    def stream(
        self,
        columns: list[str] | tuple[str, ...],
        batch_size: int = 50_000,
        normalize: bool = False,
    ) -> Iterator[pd.DataFrame]:
        pf = self.parquet()
        for batch in pf.iter_batches(columns=list(columns), batch_size=batch_size):
            df = batch.to_pandas()
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            if normalize:
                df = normalize_event_like_df(df)
            yield df

    def load_projection(
        self,
        columns: list[str] | tuple[str, ...],
        filters: Callable[[pd.DataFrame], pd.Series] | None = None,
        batch_size: int = 50_000,
        normalize: bool = False,
    ) -> pd.DataFrame:
        chunks: list[pd.DataFrame] = []
        for df in self.stream(columns=columns, batch_size=batch_size, normalize=normalize):
            if filters is not None:
                df = df.loc[filters(df)]
            if not df.empty:
                chunks.append(df)
        if not chunks:
            return pd.DataFrame(columns=list(columns))
        return pd.concat(chunks, ignore_index=True)


def load_json(path: Path, required: bool = False) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_listish(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, np.ndarray):
        return list(value.tolist())
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, str):
        s = value.strip()
        if not s or s == "[]":
            return []
        try:
            out = json.loads(s)
            if isinstance(out, list):
                return out
        except Exception:
            pass
        hits = PAT_SINGLE.findall(s)
        if hits:
            return hits
        hits = PAT_DOUBLE.findall(s)
        if hits:
            return hits
        try:
            out = ast.literal_eval(s)
            if isinstance(out, (list, tuple, set, np.ndarray)):
                return list(out)
        except Exception:
            pass
        return [s]
    return [value]


def flatten_tokens(values: list[Any]) -> list[str]:
    out: list[str] = []
    for value in values:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue
        if isinstance(value, (list, tuple, set, np.ndarray)):
            out.extend(flatten_tokens(list(value)))
        else:
            out.append(str(value))
    return out


def parse_dictish(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return {}
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return {}
        try:
            out = json.loads(s)
            if isinstance(out, dict):
                return out
        except Exception:
            pass
        try:
            out = ast.literal_eval(s)
            if isinstance(out, dict):
                return out
        except Exception:
            pass
    return {}


def expand_metrics(df: pd.DataFrame, source_col: str = "metrics_json") -> pd.DataFrame:
    if df.empty or source_col not in df.columns:
        return df.copy()

    out = df.copy()
    out["metrics"] = out[source_col].map(parse_dictish)
    metrics_df = pd.json_normalize(out["metrics"]).add_prefix("m.")
    out = pd.concat([out.reset_index(drop=True), metrics_df.reset_index(drop=True)], axis=1)
    return out.loc[:, ~out.columns.duplicated()].copy()


def normalize_event_like_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()

    if "processed_at_utc" in out.columns:
        out["processed_at_utc"] = pd.to_datetime(out["processed_at_utc"], utc=True, errors="coerce")

    if "date" in out.columns:
        out["date_ts"] = pd.to_datetime(out["date"], errors="coerce")

    if "issues" in out.columns:
        out["issues_list"] = out["issues"].map(lambda x: flatten_tokens([parse_listish(x)]))

    if "warns" in out.columns:
        out["warns_list"] = out["warns"].map(lambda x: flatten_tokens([parse_listish(x)]))

    out = expand_metrics(out, source_col="metrics_json")

    if "batch_id" in out.columns:
        out["batch_num"] = pd.to_numeric(
            out["batch_id"].astype(str).str.extract(r"(\d+)")[0],
            errors="coerce",
        )

    return out


def extract_metrics_subset(
    df: pd.DataFrame,
    metric_keys: list[str] | tuple[str, ...],
    source_col: str = "metrics_json",
    prefix: str = "m.",
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    if source_col not in out.columns:
        for key in metric_keys:
            out[f"{prefix}{key}"] = pd.Series(index=out.index, dtype="object")
        return out

    metrics = out[source_col].map(parse_dictish)
    for key in metric_keys:
        out[f"{prefix}{key}"] = metrics.map(lambda d: d.get(key))
    return out


def load_events_batches(events_dir: Path) -> tuple[pd.DataFrame, list[Path]]:
    event_files = sorted(events_dir.glob("batch_*.parquet"))
    if not event_files:
        return pd.DataFrame(), []
    events = pd.concat([pd.read_parquet(p) for p in event_files], ignore_index=True)
    events = normalize_event_like_df(events)
    return events, event_files


def load_current_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    current = pd.read_parquet(path)
    return normalize_event_like_df(current)


def make_trades_audit_handle(path: Path | str) -> TradesAuditHandle:
    return TradesAuditHandle(Path(path))


def load_inventory_parquet(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    inventory = pd.read_parquet(path, columns=columns) if columns else pd.read_parquet(path)
    if "date" in inventory.columns:
        inventory["date"] = pd.to_datetime(inventory["date"], errors="coerce")
    return inventory


def merge_inventory_context(df: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    if df.empty or inventory.empty or "file" not in df.columns or "file" not in inventory.columns:
        return df.copy()

    inv_cols = [c for c in ["file", "root", "ticker", "date", "task_key"] if c in inventory.columns]
    out = df.copy()
    if "root" not in out.columns:
        out["root"] = pd.Series(index=out.index, dtype="object")
    out = out.merge(inventory[inv_cols], on="file", how="left", suffixes=("", "_inv"))

    if "root_inv" in out.columns and "root" in out.columns:
        out["root"] = out["root"].fillna(out["root_inv"])

    return out


def load_trades_run_artifacts(
    run_dir: Path,
    inventory_parquet: Path,
    load_events: bool = True,
    load_current: bool = True,
    merge_inventory_into_events: bool = True,
    merge_inventory_into_current: bool = False,
) -> dict[str, Any]:
    summary_json = run_dir / "validation_run_summary.json"
    live_status_json = run_dir / "live_status_trades_strict.json"
    checkpoint_json = run_dir / "validation_checkpoint.json"
    manifest_json = run_dir / "validation_run_manifest.json"
    current_parquet = run_dir / "trades_current.parquet"
    events_dir = run_dir / "events_batches"

    summary = load_json(summary_json, required=False)
    live_status = load_json(live_status_json, required=False)
    checkpoint = load_json(checkpoint_json, required=False)
    manifest = load_json(manifest_json, required=False)

    inventory = load_inventory_parquet(
        inventory_parquet,
        columns=["file", "root", "ticker", "date", "task_key"],
    )

    events = pd.DataFrame()
    event_files: list[Path] = []
    if load_events:
        events, event_files = load_events_batches(events_dir)
        if merge_inventory_into_events:
            events = merge_inventory_context(events, inventory)

    current = pd.DataFrame()
    if load_current:
        current = load_current_parquet(current_parquet)
        if merge_inventory_into_current:
            current = merge_inventory_context(current, inventory)

    return {
        "summary": summary,
        "live_status": live_status,
        "checkpoint": checkpoint,
        "manifest": manifest,
        "inventory": inventory,
        "events": events,
        "current": current,
        "event_files": event_files,
        "paths": {
            "run_dir": run_dir,
            "inventory_parquet": inventory_parquet,
            "current_parquet": current_parquet,
            "events_dir": events_dir,
        },
    }
