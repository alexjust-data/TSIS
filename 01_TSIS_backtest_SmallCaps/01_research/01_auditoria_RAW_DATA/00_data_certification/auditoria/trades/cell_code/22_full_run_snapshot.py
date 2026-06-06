from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import Markdown, display


SEVERITY_ORDER = ["PASS", "SOFT_FAIL", "HARD_FAIL"]
SEVERITY_PALETTE = {
    "PASS": "#2a9d8f",
    "SOFT_FAIL": "#e9c46a",
    "HARD_FAIL": "#e76f51",
}


def configure_full_notebook_style() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["figure.figsize"] = (14, 7)
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False
    pd.set_option("display.max_columns", 120)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.max_colwidth", 160)


def build_full_run_context(mod00: dict[str, Any], run_dir_full: Path) -> dict[str, Any]:
    current_parquet = run_dir_full / "trades_current.parquet"
    summary_json = run_dir_full / "validation_run_summary.json"
    live_status_json = run_dir_full / "live_status_trades_strict.json"
    checkpoint_json = run_dir_full / "validation_checkpoint.json"
    materialization_json = run_dir_full / "materialization_summary.json"

    assert run_dir_full.exists(), run_dir_full
    assert current_parquet.exists(), current_parquet

    full_current = mod00["load_current_parquet"](current_parquet)

    if "processed_at_utc" in full_current.columns:
        full_current["processed_at_utc"] = pd.to_datetime(full_current["processed_at_utc"], utc=True, errors="coerce")
    if "date" in full_current.columns:
        full_current["date_ts"] = pd.to_datetime(full_current["date"], errors="coerce")
        full_current["year"] = full_current["date_ts"].dt.year
        full_current["month"] = full_current["date_ts"].dt.to_period("M").astype(str)
    if "file" in full_current.columns:
        full_current["file_key"] = full_current["file"].astype(str)

    numeric_cols_full = [
        "m.off_session_trade_pct",
        "m.duplicate_excess_ratio_pct",
        "m.max_trades_same_timestamp",
        "m.trade_volume_vs_daily_ratio",
        "m.trade_volume_vs_1m_ratio",
        "m.possible_price_scale_factor_vs_daily",
        "m.possible_price_scale_factor_vs_1m",
        "m.price_min",
        "m.price_max",
        "m.trade_vwap",
        "m.vw",
        "m.l",
        "m.h",
        "m.ohlcv_1m_low_min",
        "m.ohlcv_1m_high_max",
    ]
    for col in numeric_cols_full:
        if col in full_current.columns:
            full_current[col] = pd.to_numeric(full_current[col], errors="coerce")

    if "batch_id" in full_current.columns:
        full_current["batch_num"] = pd.to_numeric(
            full_current["batch_id"].astype(str).str.extract(r"(\d+)")[0],
            errors="coerce",
        )

    return {
        "run_dir_full": run_dir_full,
        "summary_full": mod00["load_json"](summary_json, required=False),
        "live_status_full": mod00["load_json"](live_status_json, required=False),
        "checkpoint_full": mod00["load_json"](checkpoint_json, required=False),
        "materialization_full": mod00["load_json"](materialization_json, required=False),
        "full_current": full_current,
    }


def build_severity_counts_full(full_current: pd.DataFrame) -> pd.DataFrame:
    out = (
        full_current["severity"]
        .value_counts()
        .rename_axis("severity")
        .reset_index(name="files")
    )
    out["pct"] = 100.0 * out["files"] / max(len(full_current), 1)
    out["severity"] = pd.Categorical(out["severity"], categories=SEVERITY_ORDER, ordered=True)
    return out.sort_values("severity").reset_index(drop=True)


def build_snapshot_full(summary_full: dict[str, Any], full_current: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "run_id": summary_full.get("run_id"),
            "selected_files": summary_full.get("selected_files"),
            "current_rows": int(len(full_current)),
            "batches_written": summary_full.get("batches_written"),
            "workers": summary_full.get("workers"),
            "chunk_size": summary_full.get("chunk_size"),
            "hard_fail": int((full_current["severity"] == "HARD_FAIL").sum()),
            "soft_fail": int((full_current["severity"] == "SOFT_FAIL").sum()),
            "pass": int((full_current["severity"] == "PASS").sum()),
            "pass_rate_pct": round(100.0 * (full_current["severity"] == "PASS").mean(), 3),
            "hard_fail_rate_pct": round(100.0 * (full_current["severity"] == "HARD_FAIL").mean(), 3),
            "soft_fail_rate_pct": round(100.0 * (full_current["severity"] == "SOFT_FAIL").mean(), 3),
        }
    ])


def build_batch_snapshot_full(full_current: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    batch_mix_full = (
        full_current.groupby(["batch_num", "severity"], dropna=False)
        .size()
        .rename("files")
        .reset_index()
    )
    batch_pivot_full = (
        batch_mix_full.pivot(index="batch_num", columns="severity", values="files")
        .fillna(0)
        .sort_index()
    )
    batch_rate_full = batch_pivot_full.div(batch_pivot_full.sum(axis=1), axis=0) * 100.0
    batch_rate_roll50 = (
        batch_rate_full[[c for c in SEVERITY_ORDER if c in batch_rate_full.columns]]
        .rolling(50, min_periods=1)
        .mean()
    )
    return batch_mix_full, batch_pivot_full, batch_rate_roll50


def plot_full_severity_snapshot(sev_counts_full: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    sns.barplot(
        data=sev_counts_full,
        x="severity",
        y="files",
        hue="severity",
        palette=SEVERITY_PALETTE,
        legend=False,
        ax=axes[0],
    )
    axes[0].set_title("Conteo por severidad")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("files")

    sns.barplot(
        data=sev_counts_full,
        x="severity",
        y="pct",
        hue="severity",
        palette=SEVERITY_PALETTE,
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Peso relativo por severidad")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("pct")
    plt.tight_layout()
    plt.show()


def plot_full_batch_snapshot(batch_pivot_full: pd.DataFrame, batch_rate_roll50: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(18, 10), sharex=True)
    batch_pivot_full[[c for c in SEVERITY_ORDER if c in batch_pivot_full.columns]].plot(
        ax=axes[0],
        color=SEVERITY_PALETTE,
        alpha=0.8,
    )
    axes[0].set_title("Conteo por batch")
    axes[0].set_ylabel("files")

    batch_rate_roll50.plot(
        ax=axes[1],
        color=SEVERITY_PALETTE,
    )
    axes[1].set_title("Tasa por severidad suavizada (rolling 50 batches)")
    axes[1].set_ylabel("pct")
    axes[1].set_xlabel("batch_num")
    plt.tight_layout()
    plt.show()


def display_full_run_header(full_current: pd.DataFrame, run_dir_full: Path) -> None:
    display(
        Markdown(
            f"**full rows:** {len(full_current):,}  \n"
            f"**run dir:** `{run_dir_full}`"
        )
    )
