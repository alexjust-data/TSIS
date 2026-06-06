from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\quotes")
IMG_DIR = ROOT / "img"

CASES = [
    {
        "name": "05_large_file_threshold_explained_sndl_2021_01_28",
        "title": "SNDL | 2021-01-28 | large_file_threshold_edge_hard_many_crosses | explained by halt context",
        "file": r"D:\quotes\SNDL\year=2021\month=01\day=28\quotes.parquet",
        "window": 800,
        "halt_start_et": "2021-01-28 09:44:58",
        "resume_trade_et": "2021-01-28 10:03:18",
    },
    {
        "name": "06_large_file_threshold_explained_wkhs_2021_02_23",
        "title": "WKHS | 2021-02-23 | large_file_threshold_edge_hard_many_crosses | explained by halt context",
        "file": r"C:\TSIS_Data\data\quotes\WKHS\year=2021\month=02\day=23\quotes.parquet",
        "window": 800,
        "halt_start_et": "2021-02-23 15:05:09",
        "resume_trade_et": "2021-02-23 15:48:01",
    },
    {
        "name": "07_large_file_threshold_unexplained_ctic_2006_09_19",
        "title": "CTIC | 2006-09-19 | large_file_threshold_edge_hard_many_crosses | not strongly explained",
        "file": r"D:\quotes\CTIC\year=2006\month=09\day=19\quotes.parquet",
        "window": 800,
    },
    {
        "name": "08_large_file_threshold_unexplained_cntb_2022_06_29",
        "title": "CNTB | 2022-06-29 | large_file_threshold_edge_hard_many_crosses | not strongly explained",
        "file": r"D:\quotes\CNTB\year=2022\month=06\day=29\quotes.parquet",
        "window": 800,
    },
]


def _load_case_frame(file_path: str) -> pd.DataFrame:
    df = pd.read_parquet(
        file_path,
        columns=["timestamp", "bid_price", "ask_price", "bid_size", "ask_size", "bid_exchange", "ask_exchange"],
    )
    df["bid_price"] = pd.to_numeric(df["bid_price"], errors="coerce")
    df["ask_price"] = pd.to_numeric(df["ask_price"], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["ts_ny"] = pd.to_datetime(df["timestamp"], unit="ns", utc=True, errors="coerce").dt.tz_convert("America/New_York")
    df["cross_positive"] = df["bid_price"].gt(df["ask_price"]) & df["ask_price"].gt(0)
    df["gap"] = df["bid_price"] - df["ask_price"]
    df["mid"] = (df["bid_price"] + df["ask_price"]) / 2.0
    df["gap_bps"] = np.where(df["mid"] > 0, df["gap"] / df["mid"] * 10000.0, np.nan)
    return df


def _plot_case(case: dict[str, object]) -> Path:
    out_path = IMG_DIR / f"{case['name']}.png"
    df = _load_case_frame(str(case["file"]))
    cross_idx = np.flatnonzero(df["cross_positive"].fillna(False).to_numpy())
    if len(cross_idx) == 0:
        raise RuntimeError(f"No crossed positive rows found in {case['file']}")

    window = int(case["window"])
    start = max(int(cross_idx.min()) - window, 0)
    end = min(int(cross_idx.max()) + window + 1, len(df))
    view = df.iloc[start:end].copy()
    crossed_view = view.loc[view["cross_positive"]].copy()

    if len(view) > 4000:
        step = max(int(math.ceil(len(view) / 4000)), 1)
        sampled = view.iloc[::step].copy()
        crossed_view = view.loc[view["cross_positive"]].copy()
        view = sampled

    x = view["ts_ny"]
    x_cross = crossed_view["ts_ny"] if not crossed_view.empty else np.array([])

    fig, axes = plt.subplots(2, 1, figsize=(16, 9), sharex=True, gridspec_kw={"height_ratios": [2.2, 1.2]})
    axes[0].plot(x, view["bid_price"], color="#0f766e", linewidth=1.1, label="bid_price")
    axes[0].plot(x, view["ask_price"], color="#b91c1c", linewidth=1.1, label="ask_price")
    if not crossed_view.empty:
        axes[0].scatter(x_cross, crossed_view["bid_price"], color="#f59e0b", s=18, alpha=0.9, label="crossed bid > ask > 0")
        axes[0].scatter(x_cross, crossed_view["ask_price"], color="#7c3aed", s=18, alpha=0.6, label="ask in crossed")
    axes[0].set_title(str(case["title"]))
    axes[0].set_ylabel("price")
    axes[0].legend(loc="best")
    axes[0].grid(alpha=0.2)

    halt_start = case.get("halt_start_et")
    halt_end = case.get("resume_trade_et")
    if halt_start and halt_end:
        halt_start_ts = pd.Timestamp(str(halt_start), tz="America/New_York")
        halt_end_ts = pd.Timestamp(str(halt_end), tz="America/New_York")
        for ax in axes:
            ax.axvline(halt_start_ts, color="#000000", linestyle="--", linewidth=1.1, label="halt start" if ax is axes[0] else None)
            ax.axvline(halt_end_ts, color="#000000", linestyle=":", linewidth=1.1, label="halt resume" if ax is axes[0] else None)
        axes[0].legend(loc="best")

    axes[1].plot(x, view["gap_bps"], color="#1d4ed8", linewidth=1.0, label="gap_bps")
    axes[1].axhline(0.0, color="#111827", linewidth=1.0, alpha=0.7)
    if not crossed_view.empty:
        axes[1].scatter(x_cross, crossed_view["gap_bps"], color="#ea580c", s=14, alpha=0.8)
    axes[1].set_ylabel("gap bps")
    axes[1].set_xlabel("ts_ny")
    axes[1].grid(alpha=0.2)

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        out = _plot_case(case)
        print(out)


if __name__ == "__main__":
    main()
