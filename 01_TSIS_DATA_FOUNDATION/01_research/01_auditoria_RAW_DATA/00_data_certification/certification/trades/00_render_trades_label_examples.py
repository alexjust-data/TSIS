from __future__ import annotations

import json
import math
import runpy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification\trades")
IMG_DIR = ROOT / "img"

CACHE_FULL = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_materialized\trades_current_cd_merged\root_cause_exports\file_acceptance_cache_lt1b_full_clean_fast_same_schema"
)
RAW_SHARDS_DIR = CACHE_FULL / "raw_metrics_shards"
PROGRESS_PATH = CACHE_FULL / "progress.json"
MANIFEST_PATH = CACHE_FULL / "manifest.json"
D_FULL_BUCKET_SUMMARY = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket_summary.parquet"
)
D_FULL_BUCKETS = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\trades_v2_validation\trades_validate_2005_2026_d_full\root_cause_exports\trades_full_root_cause_final_bucket.parquet"
)

FORENSIC_MOD = runpy.run_path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria\trades\cell_code\12_forensic_trade_vs_daily_1m_case.py"
)

OHLVC_DAILY_ROOT = Path(r"D:\ohlcv_daily")
OHLVC_1M_ROOT = Path(r"D:\ohlcv_1m")


def load_all_raw_metrics() -> pd.DataFrame:
    keep = [
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
    parts = []
    for shard in sorted(RAW_SHARDS_DIR.glob("raw_metrics_*.parquet")):
        parts.append(pd.read_parquet(shard, columns=keep))
    if not parts:
        return pd.DataFrame(columns=keep)
    return pd.concat(parts, ignore_index=True)


def score_rows(df: pd.DataFrame) -> pd.Series:
    cols = [
        "core_outside_daily_pct",
        "core_outside_1m_pct",
        "outside_daily_regular_pct",
        "outside_1m_regular_pct",
        "trade_vwap_vs_daily_vw_diff_pct_raw",
    ]
    return df[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)


def save_policy_distribution(df: pd.DataFrame) -> None:
    counts = df["acceptance_label"].value_counts().rename_axis("acceptance_label").reset_index(name="files")
    counts["pct"] = 100.0 * counts["files"] / counts["files"].sum()
    palette = {
        "review": "#4C72B0",
        "review_microstructure": "#DD8452",
        "reference_scale_mismatch": "#55A868",
        "review_1m_reference_alignment": "#C44E52",
        "bad_data": "#8172B2",
        "review_no_1m_reference": "#937860",
        "good": "#64B5CD",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [palette.get(x, "#999999") for x in counts["acceptance_label"]]
    ax.bar(counts["acceptance_label"], counts["files"], color=colors)
    ax.set_title("Trades full_clean current shard state | acceptance_label")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)
    for i, row in counts.iterrows():
        ax.text(i, row["files"], f"{int(row['files']):,}\n{row['pct']:.3f}%", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    fig.savefig(IMG_DIR / "00_current_policy_distribution_from_raw_shards.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def select_case(df: pd.DataFrame, ticker: str, date_str: str) -> pd.Series:
    sub = df.loc[(df["ticker"].astype(str) == ticker) & (df["date"].astype(str) == date_str)]
    if sub.empty:
        raise KeyError(f"Case not found: {ticker} {date_str}")
    return sub.iloc[0]


def render_case(case_row: pd.Series, out_name: str) -> None:
    refs = FORENSIC_MOD["load_trade_daily_1m_case_refs"](
        case_row=case_row,
        ohlcv_daily_root=OHLVC_DAILY_ROOT,
        ohlcv_1m_root=OHLVC_1M_ROOT,
    )
    trades_df, daily_low, daily_high, daily_open, daily_close, daily_vw = FORENSIC_MOD["annotate_trade_outside_daily"](
        refs["trades_df"],
        refs["daily_row"],
    )
    summary_rows = FORENSIC_MOD["build_case_summary_table"](
        trades_df=trades_df,
        daily_low=daily_low,
        daily_high=daily_high,
        daily_vw=daily_vw,
    )
    FORENSIC_MOD["plot_trade_vs_daily_1m_case"](
        ticker=refs["ticker"],
        date_str=refs["date_str"],
        trades_df=trades_df,
        m1_day=refs["m1_day"],
        daily_low=daily_low,
        daily_high=daily_high,
        daily_open=daily_open,
        daily_close=daily_close,
        daily_vw=daily_vw,
        summary_rows=summary_rows,
    )
    fig = plt.gcf()
    fig.savefig(IMG_DIR / out_name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def write_current_status_json(df: pd.DataFrame) -> None:
    counts = df["acceptance_label"].value_counts().to_dict()
    total = int(len(df))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else {}
    progress = json.loads(PROGRESS_PATH.read_text(encoding="utf-8")) if PROGRESS_PATH.exists() else {}
    payload = {
        "raw_shards_found": len(list(RAW_SHARDS_DIR.glob("raw_metrics_*.parquet"))),
        "files_processed_from_raw_shards": total,
        "files_total_manifest": int(manifest.get("files_total", 0) or 0),
        "processed_pct_vs_manifest": (100.0 * total / manifest["files_total"]) if manifest.get("files_total") else None,
        "acceptance_counts_current_raw_shards": counts,
        "progress_snapshot": progress,
    }
    (ROOT / "00_current_state_from_raw_shards.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_d_full_bucket_distribution() -> None:
    df = pd.read_parquet(D_FULL_BUCKET_SUMMARY).copy()
    total = df["files"].sum()
    df["pct"] = 100.0 * df["files"] / total
    palette = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["final_bucket"], df["files"], color=palette[: len(df)])
    ax.set_title("Trades D full residual | final_bucket")
    ax.set_ylabel("files")
    ax.tick_params(axis="x", rotation=22)
    ax.grid(axis="y", alpha=0.2)
    for i, row in df.iterrows():
        ax.text(i, row["files"], f"{int(row['files']):,}\n{row['pct']:.3f}%", ha="center", va="bottom", fontsize=8)
    plt.tight_layout()
    fig.savefig(IMG_DIR / "11_d_full_final_bucket_distribution.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def save_d_full_scale_contamination() -> None:
    df = pd.read_parquet(
        D_FULL_BUCKETS,
        columns=[
            "final_bucket",
            "m.possible_price_scale_factor_vs_daily",
            "m.possible_price_scale_factor_vs_1m",
            "m.trade_vwap_vs_daily_vw_diff_pct",
        ],
    ).copy()
    rows = []
    for bucket in [
        "likely_real_break_confirmed_by_1m",
        "likely_dup_heavy_break",
        "likely_minor_unconfirmed_break",
        "manual_review",
        "scale_suspect",
    ]:
        sub = df.loc[df["final_bucket"] == bucket]
        sd = pd.to_numeric(sub["m.possible_price_scale_factor_vs_daily"], errors="coerce")
        s1 = pd.to_numeric(sub["m.possible_price_scale_factor_vs_1m"], errors="coerce")
        vwap = pd.to_numeric(sub["m.trade_vwap_vs_daily_vw_diff_pct"], errors="coerce")
        near1 = (((sd >= 0.8) & (sd <= 1.25)) | ((s1 >= 0.8) & (s1 <= 1.25))).mean() * 100
        far1 = (((sd < 0.5) | (sd > 2)) | ((s1 < 0.5) | (s1 > 2))).mean() * 100
        extreme = (((sd < 0.2) | (sd > 5)) | ((s1 < 0.2) | (s1 > 5))).mean() * 100
        vwap20 = (vwap >= 20).mean() * 100
        rows.append(
            {
                "final_bucket": bucket,
                "near1_pct": near1,
                "far1_pct": far1,
                "extreme_pct": extreme,
                "vwap_diff_ge_20_pct": vwap20,
            }
        )
    out = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = range(len(out))
    width = 0.2
    ax.bar([i - 1.5 * width for i in x], out["near1_pct"], width=width, label="near 1x", color="#4C72B0")
    ax.bar([i - 0.5 * width for i in x], out["far1_pct"], width=width, label="far from 1x", color="#DD8452")
    ax.bar([i + 0.5 * width for i in x], out["extreme_pct"], width=width, label="extreme scale", color="#C44E52")
    ax.bar([i + 1.5 * width for i in x], out["vwap_diff_ge_20_pct"], width=width, label="VWAP diff >= 20%", color="#55A868")
    ax.set_xticks(list(x))
    ax.set_xticklabels(out["final_bucket"], rotation=22)
    ax.set_ylim(0, 105)
    ax.set_ylabel("pct of files")
    ax.set_title("Trades D full residual | scale contamination by final_bucket")
    ax.grid(axis="y", alpha=0.2)
    ax.legend()
    plt.tight_layout()
    fig.savefig(IMG_DIR / "12_d_full_scale_contamination_by_bucket.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_all_raw_metrics()
    if df.empty:
        raise SystemExit("No raw_metrics shards found.")

    df = df.copy()
    df["_score"] = score_rows(df)
    write_current_status_json(df)
    save_policy_distribution(df)
    save_d_full_bucket_distribution()
    save_d_full_scale_contamination()

    cases = [
        ("reference_scale_mismatch", "SGA", "2009-01-05", "01_reference_scale_mismatch_sga_2009_01_05.png"),
        ("reference_scale_mismatch", "LPCN", "2014-07-07", "02_reference_scale_mismatch_lpcn_2014_07_07.png"),
        ("review_microstructure", "QRTEB", "2019-07-24", "03_review_microstructure_qrteb_2019_07_24.png"),
        ("review_microstructure", "CZFS", "2022-08-11", "04_review_microstructure_czfs_2022_08_11.png"),
        ("review_1m_reference_alignment", "RELV", "2018-06-07", "05_review_1m_reference_alignment_relv_2018_06_07.png"),
        ("review_1m_reference_alignment", "METC", "2021-03-22", "06_review_1m_reference_alignment_metc_2021_03_22.png"),
        ("bad_data", "BWL.A", "2009-03-26", "07_bad_data_bwl_a_2009_03_26.png"),
        ("bad_data", "ANDA", "2012-05-10", "08_bad_data_anda_2012_05_10.png"),
        ("review_no_1m_reference", "GLBL", "2024-09-19", "09_review_no_1m_reference_glbl_2024_09_19.png"),
        ("review", "TOF", "2010-06-21", "10_review_tof_2010_06_21.png"),
    ]

    for expected_label, ticker, date_str, out_name in cases:
        row = select_case(df, ticker, date_str)
        if str(row["acceptance_label"]) != expected_label:
            raise ValueError(f"{ticker} {date_str} expected {expected_label} got {row['acceptance_label']}")
        render_case(row, out_name)


if __name__ == "__main__":
    main()
