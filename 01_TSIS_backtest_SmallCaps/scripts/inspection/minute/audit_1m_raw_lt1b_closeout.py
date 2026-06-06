from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
RUN_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "ohlcv_1m_v2_materialized"
    / "ohlcv_1m_current_full"
    / "root_cause_operational_outputs"
)
LT1B_PATH = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "market_cap_last_observed_cutoff"
    / "20260320_market_cap_last_observed_cutoff"
    / "market_cap_cutoff_lt_1b_active_inactive.parquet"
)
OUT_ROOT = (
    PROJECT_ROOT
    / "01_foundations"
    / "inspection_dossiers"
    / "minute"
    / "evidence_assets"
    / "raw_1m_lt1b_closeout"
)


def _load_lt1b_window() -> pd.DataFrame:
    df = pd.read_parquet(
        LT1B_PATH,
        columns=["ticker", "first_seen_date", "last_observed_date", "classification_1b"],
    ).copy()
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df["first_seen_date"] = pd.to_datetime(df["first_seen_date"], errors="coerce")
    df["last_observed_date"] = pd.to_datetime(df["last_observed_date"], errors="coerce")
    return df.set_index("ticker")


def _month_bounds(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "m.date_min" in out.columns and "m.date_max" in out.columns:
        out["file_date_min"] = pd.to_datetime(out["m.date_min"], errors="coerce")
        out["file_date_max"] = pd.to_datetime(out["m.date_max"], errors="coerce")
    else:
        out["file_date_min"] = pd.to_datetime(
            dict(year=out["year"], month=out["month"], day=1), errors="coerce"
        )
        out["file_date_max"] = out["file_date_min"] + pd.offsets.MonthEnd(0)
    return out


def _filter_lt1b_window(df: pd.DataFrame, lt1b: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ticker"] = out["ticker"].astype(str).str.upper()
    out = out[out["ticker"].isin(lt1b.index)].copy()
    out = _month_bounds(out)
    out = out.merge(
        lt1b.reset_index(),
        on="ticker",
        how="left",
        validate="many_to_one",
    )
    mask = (
        out["first_seen_date"].notna()
        & out["last_observed_date"].notna()
        & out["file_date_min"].notna()
        & out["file_date_max"].notna()
        & (out["file_date_max"] >= out["first_seen_date"])
        & (out["file_date_min"] <= out["last_observed_date"])
    )
    return out.loc[mask].copy()


def _read_bucket(name: str, lt1b: pd.DataFrame) -> pd.DataFrame:
    path = RUN_ROOT / f"{name}.parquet"
    df = pd.read_parquet(path)
    df["source_bucket_file"] = name
    return _filter_lt1b_window(df, lt1b)


def _ensure_vw_refined(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    numeric_cols = [
        "m.vw_outside_range_rows",
        "m.rows_after_parse",
        "m.active_days",
        "m.max_gap_days",
        "m.vw_mean",
        "m.v_sum",
        "m.n_sum",
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["vw_ratio_pct"] = np.where(
        out["m.rows_after_parse"] > 0,
        out["m.vw_outside_range_rows"] / out["m.rows_after_parse"] * 100.0,
        np.nan,
    )
    out["vw_per_active_day"] = np.where(
        out["m.active_days"] > 0,
        out["m.vw_outside_range_rows"] / out["m.active_days"],
        np.nan,
    )
    out["vw_taxonomy"] = np.select(
        [
            out["vw_ratio_pct"].le(1),
            out["vw_ratio_pct"].gt(1) & out["vw_ratio_pct"].le(5),
            out["vw_ratio_pct"].gt(5) & out["m.rows_after_parse"].lt(100),
            out["vw_ratio_pct"].gt(5)
            & out["m.rows_after_parse"].ge(100)
            & out["m.vw_outside_range_rows"].lt(100),
            out["vw_ratio_pct"].gt(5)
            & out["m.rows_after_parse"].ge(100)
            & out["m.vw_outside_range_rows"].ge(100)
            & out["vw_per_active_day"].lt(25),
            out["vw_ratio_pct"].gt(5)
            & out["m.rows_after_parse"].ge(100)
            & out["m.vw_outside_range_rows"].ge(100)
            & out["vw_per_active_day"].ge(25),
        ],
        [
            "vw_mild_low_ratio",
            "vw_moderate_ratio",
            "vw_severe_tiny_base",
            "vw_severe_small_mass",
            "vw_severe_large_mass_diffuse",
            "vw_severe_large_mass_persistent",
        ],
        default="vw_other",
    )
    return out


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    lt1b = _load_lt1b_window()

    rescue_schema_plus_vw = _ensure_vw_refined(_read_bucket("rescue_schema_plus_vw", lt1b))
    rescue_schema_only = _read_bucket("rescue_schema_only", lt1b)
    hard_quarantine = _read_bucket("hard_quarantine", lt1b)

    all_rows = pd.concat(
        [rescue_schema_plus_vw, rescue_schema_only, hard_quarantine],
        ignore_index=True,
        sort=False,
    )

    total_rows = int(len(all_rows))
    summary_rows = []
    decision_counts = (
        all_rows["operational_decision"].astype(str).value_counts(dropna=False).sort_index()
    )
    for key, count in decision_counts.items():
        summary_rows.append(
            {
                "category": "operational_decision",
                "key": key,
                "count": int(count),
                "pct_of_lt1b_current": float(count) / total_rows * 100.0 if total_rows else 0.0,
            }
        )

    good_review_bad_map = {
        "RESCUE_SCHEMA_ONLY": "good",
        "RESCUE_SCHEMA_PLUS_VW": "mixed_soft",
        "QUARANTINE_PARSE_INVALID": "bad",
        "QUARANTINE_PRICE_INVALID": "bad",
    }
    all_rows["grb_superbucket"] = all_rows["operational_decision"].map(good_review_bad_map).fillna("unknown")

    # Refine RESCUE_SCHEMA_PLUS_VW by historical soft bucket policy
    def _soft_to_policy_bucket(v: str) -> str:
        if v in {"vw_mild_low_ratio"}:
            return "good"
        if v in {"vw_moderate_ratio", "vw_severe_tiny_base", "vw_severe_small_mass"}:
            return "review"
        if v in {"vw_severe_large_mass_diffuse", "vw_severe_large_mass_persistent"}:
            return "bad"
        return "unknown"

    all_rows["final_policy_bucket_lt1b"] = all_rows["grb_superbucket"]
    soft_mask = all_rows["operational_decision"].astype(str) == "RESCUE_SCHEMA_PLUS_VW"
    all_rows.loc[soft_mask, "final_policy_bucket_lt1b"] = (
        all_rows.loc[soft_mask, "vw_taxonomy"].astype(str).map(_soft_to_policy_bucket).fillna("unknown")
    )

    policy_counts = all_rows["final_policy_bucket_lt1b"].astype(str).value_counts(dropna=False).sort_index()
    for key, count in policy_counts.items():
        summary_rows.append(
            {
                "category": "final_policy_bucket_lt1b",
                "key": key,
                "count": int(count),
                "pct_of_lt1b_current": float(count) / total_rows * 100.0 if total_rows else 0.0,
            }
        )

    if soft_mask.any():
        soft_counts = all_rows.loc[soft_mask, "vw_taxonomy"].astype(str).value_counts(dropna=False).sort_index()
        for key, count in soft_counts.items():
            summary_rows.append(
                {
                    "category": "vw_taxonomy_lt1b",
                    "key": key,
                    "count": int(count),
                    "pct_of_lt1b_current": float(count) / total_rows * 100.0 if total_rows else 0.0,
                }
            )

    top_ticker_counts = (
        all_rows.groupby(["ticker", "final_policy_bucket_lt1b"], dropna=False)
        .size()
        .reset_index(name="file_month_count")
        .sort_values(["file_month_count", "ticker"], ascending=[False, True])
    )

    exec_summary = pd.DataFrame(
        [
            {"metric": "lt1b_tickers_reference", "value": int(len(lt1b))},
            {"metric": "lt1b_current_1m_rows", "value": total_rows},
            {"metric": "lt1b_current_1m_unique_tickers", "value": int(all_rows["ticker"].nunique())},
            {"metric": "lt1b_current_1m_unique_task_keys", "value": int(all_rows["task_key"].nunique())},
            {
                "metric": "lt1b_current_1m_unique_good_tickers",
                "value": int(all_rows.loc[all_rows["final_policy_bucket_lt1b"] == "good", "ticker"].nunique()),
            },
            {
                "metric": "lt1b_current_1m_unique_review_tickers",
                "value": int(all_rows.loc[all_rows["final_policy_bucket_lt1b"] == "review", "ticker"].nunique()),
            },
            {
                "metric": "lt1b_current_1m_unique_bad_tickers",
                "value": int(all_rows.loc[all_rows["final_policy_bucket_lt1b"] == "bad", "ticker"].nunique()),
            },
        ]
    )

    exec_summary.to_csv(OUT_ROOT / "raw_1m_lt1b_exec_summary.csv", index=False)
    pd.DataFrame(summary_rows).to_csv(OUT_ROOT / "raw_1m_lt1b_bucket_summary.csv", index=False)
    top_ticker_counts.to_csv(OUT_ROOT / "raw_1m_lt1b_ticker_bucket_counts.csv", index=False)
    all_rows.to_parquet(OUT_ROOT / "raw_1m_lt1b_filtered_closeout.parquet", index=False)

    print(exec_summary.to_string(index=False))
    print()
    print(pd.DataFrame(summary_rows).to_string(index=False))


if __name__ == "__main__":
    main()
