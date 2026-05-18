# Backward-compatible alias kept for notebooks that still import 58c.
# The canonical final viewer is 58d_trades_file_acceptance_view_lt1b_full_clean_fast_same_schema.py.

from __future__ import annotations

import json
import runpy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display


BASE_VIEW = Path(__file__).resolve().parent / "58_trades_file_acceptance_view.py"
RUN_DIR_LT1B = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged")
CACHE_DIR_LT1B_FULL = RUN_DIR_LT1B / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean_fast_same_schema"
MANIFEST_PATH_LT1B_FULL = CACHE_DIR_LT1B_FULL / "manifest.json"
PROGRESS_PATH_LT1B_FULL = CACHE_DIR_LT1B_FULL / "progress.json"
RAW_METRICS_SHARDS_DIR = CACHE_DIR_LT1B_FULL / "raw_metrics_shards"


_base = runpy.run_path(str(BASE_VIEW))
globals().update(_base)


def _load_parquet(name: str) -> pd.DataFrame:
    p = CACHE_DIR_LT1B_FULL / f"{name}.parquet"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_parquet(p)


def load_manifest() -> dict:
    if not MANIFEST_PATH_LT1B_FULL.exists():
        return {}
    return json.loads(MANIFEST_PATH_LT1B_FULL.read_text(encoding="utf-8"))


def load_progress() -> dict:
    if not PROGRESS_PATH_LT1B_FULL.exists():
        return {}
    return json.loads(PROGRESS_PATH_LT1B_FULL.read_text(encoding="utf-8"))


def load_all_artifacts() -> dict[str, pd.DataFrame]:
    keys = [
        "layer1_integrity_summary",
        "layer1_integrity_examples",
        "sample_index",
        "layer2_coverage_summary_full",
        "layer6_policy_summary_full",
    ]
    return {k: _load_parquet(k) for k in keys}


def show_manifest(manifest: dict, progress: dict | None = None) -> None:
    if not manifest:
        display(Markdown("**manifest** no encontrado. Verifica primero el cache final `57f/full_clean_fast_same_schema`."))
        return
    lines = [
        f"**mode:** `{manifest.get('mode', 'n/a')}`",
        f"**files_total:** {manifest.get('files_total', 'n/a')}",
        f"**total_index_shards:** {manifest.get('total_index_shards', 'n/a')}",
        f"**raw_metric_shards_written:** {manifest.get('raw_metric_shards_written', 'n/a')}",
        f"**cache dir:** `{manifest.get('cache_dir', 'n/a')}`",
        f"**built_at_utc:** `{manifest.get('built_at_utc', 'n/a')}`",
        f"**workers:** `{manifest.get('workers', 'n/a')}`",
    ]
    if progress:
        lines.extend(
            [
                f"**phase:** `{progress.get('phase', 'n/a')}`",
                f"**done_index_shards:** `{progress.get('done_index_shards', 'n/a')}`",
                f"**pending_shards:** `{progress.get('pending_shards', 'n/a')}`",
                f"**updated_at_utc:** `{progress.get('updated_at_utc', 'n/a')}`",
            ]
        )
    display(Markdown("  \n".join(lines)))


def summary_layer2_full(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "La segunda capa full todavía no está materializada."
    total = _metric_value(summary, "files_total_full_raw")
    one_m = _metric_value(summary, "files_with_1m_reference_pct")
    daily = _metric_value(summary, "files_with_daily_reference_pct")
    return (
        f"La segunda capa full ya no mira la muestra, sino el universo raw `<1B>` procesado. "
        f"Ahora mismo cubre {int(total):,} files; la referencia `1m` está presente en {one_m:.2f}% "
        f"y la referencia `daily` en {daily:.2f}%."
    )


def plot_layer2_full(summary: pd.DataFrame) -> None:
    if summary.empty:
        return
    plot_df = summary.copy()
    with plt.rc_context(PLOT_RC):
        fig, ax = plt.subplots(figsize=(8, 3.8))
        y = np.arange(len(plot_df))
        bars = ax.barh(y, plot_df["value"], color=["#4C72B0", "#55A868", "#C44E52"][: len(plot_df)])
        ax.set_yticks(y)
        ax.set_yticklabels(plot_df["metric"])
        ax.set_title("Capa 2 full | Cobertura de referencias")
        ax.grid(axis="x", alpha=0.2)
        ax.invert_yaxis()
        for bar, value in zip(bars, plot_df["value"]):
            label = f"{value:,.2f}" if value < 10000 else f"{int(value):,}"
            ax.text(value, bar.get_y() + bar.get_height() / 2, f" {label}", va="center", ha="left", fontsize=8)
        plt.tight_layout()
        plt.show()


def _score_policy_rows(df: pd.DataFrame) -> pd.Series:
    score = pd.Series(0.0, index=df.index)
    for col in [
        "core_outside_1m_pct",
        "core_outside_daily_pct",
        "outside_1m_regular_pct",
        "outside_daily_regular_pct",
        "trade_vwap_vs_daily_vw_diff_pct_raw",
    ]:
        if col in df.columns:
            score = score.add(pd.to_numeric(df[col], errors="coerce").fillna(0), fill_value=0)
    return score


def load_policy_examples_top(top_n_per_label: int = 10) -> pd.DataFrame:
    if not RAW_METRICS_SHARDS_DIR.exists():
        return pd.DataFrame()
    keep_cols = [
        "acceptance_label",
        "file",
        "ticker",
        "date",
        "scale_bucket_vw",
        "core_regular_round_trade_pct",
        "core_outside_daily_pct",
        "core_outside_1m_pct",
        "outside_daily_regular_pct",
        "outside_1m_regular_pct",
        "odd_lot_trade_pct",
        "trade_vwap_vs_daily_vw_diff_pct_raw",
        "has_1m_reference",
        "has_daily_reference",
    ]
    buckets: dict[str, pd.DataFrame] = {}
    for shard in sorted(RAW_METRICS_SHARDS_DIR.glob("raw_metrics_*.parquet")):
        df = pd.read_parquet(shard, columns=keep_cols)
        if df.empty or "acceptance_label" not in df.columns:
            continue
        df = df.copy()
        df["_policy_score"] = _score_policy_rows(df)
        for label, chunk in df.groupby("acceptance_label", observed=False):
            prev = buckets.get(label)
            merged = chunk if prev is None else pd.concat([prev, chunk], ignore_index=True)
            merged = merged.sort_values(["_policy_score", "outside_1m_regular_pct", "outside_daily_regular_pct"], ascending=[False, False, False])
            buckets[label] = merged.head(int(top_n_per_label)).copy()
    if not buckets:
        return pd.DataFrame()
    out = pd.concat([buckets[k] for k in sorted(buckets)], ignore_index=True)
    return out.sort_values(["acceptance_label", "_policy_score"], ascending=[True, False]).reset_index(drop=True)


def summary_closeout_full(policy: pd.DataFrame, coverage: pd.DataFrame) -> str:
    if policy.empty:
        return "El cierre full todavía no tiene política agregada."
    parts = [f"{row.acceptance_label}={int(row.files):,}" for row in policy.itertuples(index=False)]
    total = _metric_value(coverage, "files_total_full_raw") if not coverage.empty else np.nan
    return (
        f"El cierre full `<1B>` resume {int(total):,} files raw procesados. "
        "La política agregada queda en: " + ", ".join(parts) + "."
    )


RUN_DIR_CD = RUN_DIR_LT1B
CACHE_DIR = CACHE_DIR_LT1B_FULL
MANIFEST_PATH = MANIFEST_PATH_LT1B_FULL
