from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class CutoffSpec:
    label: str
    cutoff_b: int
    detail_name: str
    detail_csv_name: str
    cut_name: str
    cut_csv_name: str
    summary_name: str
    class_col: str
    reason_col: str


DEFAULT_POPULATION = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\population_target_pti\population_target_pti_run_01\population_target_pti.parquet"
)
DEFAULT_UNIVERSE = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti\tickers_2005_2026_upper.parquet"
)
DEFAULT_OUTDIR = Path(
    r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff"
)


def normalize_ticker_series(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.upper()


def load_universe_tickers(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    if "ticker" not in df.columns:
        raise ValueError(f"Missing ticker column in {path}")
    df["ticker"] = normalize_ticker_series(df["ticker"])
    df = df.dropna(subset=["ticker"])
    df = df[df["ticker"] != ""]
    return df[["ticker"]].drop_duplicates().sort_values("ticker").reset_index(drop=True)


def load_population(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    required = [
        "date",
        "ticker",
        "status",
        "close_t",
        "shares_outstanding_t",
        "shares_source",
        "shares_observed_date",
        "shares_period_end",
        "shares_age_days",
        "market_cap_t",
        "is_small_cap_t",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in population target: {missing}")
    df["ticker"] = normalize_ticker_series(df["ticker"])
    df = df.dropna(subset=["ticker", "date"])
    df = df[df["ticker"] != ""].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for c in ["shares_observed_date", "shares_period_end"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    df = df.dropna(subset=["date"]).copy()
    return df.sort_values(["ticker", "date"]).reset_index(drop=True)


def build_base(pop_df: pd.DataFrame, universe_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    pop = pop_df[pop_df["ticker"].isin(set(universe_df["ticker"]))].copy()
    if pop.empty:
        raise ValueError("Population target filtered by universe is empty")

    panel_end_date = pop["date"].max()

    by_ticker = pop.groupby("ticker", as_index=False).agg(
        first_seen_date=("date", "min"),
        last_observed_date=("date", "max"),
    )

    last_rows = pop.groupby("ticker", as_index=False).tail(1).copy()
    last_rows = last_rows.rename(
        columns={
            "date": "last_row_date",
            "status": "status_last_row",
            "close_t": "close_t_last_row",
            "shares_outstanding_t": "shares_outstanding_t_last_row",
            "shares_source": "shares_source_last_row",
            "shares_observed_date": "shares_observed_date_last_row",
            "shares_period_end": "shares_period_end_last_row",
            "shares_age_days": "shares_age_days_last_row",
            "market_cap_t": "market_cap_t_last_row",
            "is_small_cap_t": "is_small_cap_t_last_row",
        }
    )

    anchor_rows = pop[pop["market_cap_t"].notna()].groupby("ticker", as_index=False).tail(1).copy()
    anchor_rows = anchor_rows.rename(
        columns={
            "date": "anchor_date_used",
            "status": "status_at_anchor",
        }
    )

    base = universe_df.merge(by_ticker, on="ticker", how="left")
    base = base.merge(
        last_rows[
            [
                "ticker",
                "last_row_date",
                "status_last_row",
                "close_t_last_row",
                "shares_outstanding_t_last_row",
                "shares_source_last_row",
                "shares_observed_date_last_row",
                "shares_period_end_last_row",
                "shares_age_days_last_row",
                "market_cap_t_last_row",
                "is_small_cap_t_last_row",
            ]
        ],
        on="ticker",
        how="left",
    )
    base = base.merge(
        anchor_rows[
            [
                "ticker",
                "anchor_date_used",
                "status_at_anchor",
                "close_t",
                "shares_outstanding_t",
                "shares_source",
                "shares_observed_date",
                "shares_period_end",
                "shares_age_days",
                "market_cap_t",
                "is_small_cap_t",
            ]
        ],
        on="ticker",
        how="left",
    )

    base["status_rebuilt"] = "inactive"
    base.loc[base["last_observed_date"] == panel_end_date, "status_rebuilt"] = "active"
    return base, panel_end_date


def apply_cutoff(base: pd.DataFrame, spec: CutoffSpec) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    cutoff_value = spec.cutoff_b * 1_000_000_000
    out = base.copy()

    out[spec.class_col] = "unclassified_no_market_cap"
    out[spec.reason_col] = "no_market_cap_t_at_last_classifiable_date"

    mask_has_mc = out["market_cap_t"].notna()
    mask_lt = mask_has_mc & (out["market_cap_t"] < cutoff_value)
    mask_ge = mask_has_mc & (out["market_cap_t"] >= cutoff_value)
    mask_active = out["status_rebuilt"].eq("active")
    mask_inactive = out["status_rebuilt"].eq("inactive")

    out.loc[mask_ge, spec.class_col] = f"ge_{spec.label}_last_classifiable"
    out.loc[mask_ge, spec.reason_col] = f"market_cap_t_ge_{spec.label}"

    out.loc[mask_lt & mask_active, spec.class_col] = f"active_lt_{spec.label}_last_classifiable"
    out.loc[mask_lt & mask_active, spec.reason_col] = f"active_and_market_cap_t_lt_{spec.label}"

    out.loc[mask_lt & mask_inactive, spec.class_col] = f"inactive_died_lt_{spec.label}"
    out.loc[mask_lt & mask_inactive, spec.reason_col] = f"inactive_and_market_cap_t_lt_{spec.label}"

    cut = out[
        out[spec.class_col].isin(
            [
                f"active_lt_{spec.label}_last_classifiable",
                f"inactive_died_lt_{spec.label}",
            ]
        )
    ].copy()

    summary = {
        "cutoff_b": spec.cutoff_b,
        "universe_tickers": int(len(out)),
        "status_rebuilt_counts": {k: int(v) for k, v in out["status_rebuilt"].value_counts(dropna=False).to_dict().items()},
        "classification_counts": {k: int(v) for k, v in out[spec.class_col].value_counts(dropna=False).to_dict().items()},
    }
    return out, cut, summary


def write_outputs(outdir: Path, detail: pd.DataFrame, cut: pd.DataFrame, summary: dict, spec: CutoffSpec, panel_end_date: pd.Timestamp, run_id: str) -> None:
    detail_parquet = outdir / spec.detail_name
    detail_csv = outdir / spec.detail_csv_name
    cut_parquet = outdir / spec.cut_name
    cut_csv = outdir / spec.cut_csv_name
    summary_json = outdir / spec.summary_name

    detail.to_parquet(detail_parquet, index=False)
    detail.to_csv(detail_csv, index=False)
    cut.to_parquet(cut_parquet, index=False)
    cut.to_csv(cut_csv, index=False)

    payload = {
        "run_id": run_id,
        "panel_end_date": str(panel_end_date.date()),
        **summary,
        "outputs": {
            "detail_parquet": str(detail_parquet),
            "detail_csv": str(detail_csv),
            "cut_parquet": str(cut_parquet),
            "cut_csv": str(cut_csv),
        },
    }
    summary_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--population", default=str(DEFAULT_POPULATION))
    ap.add_argument("--universe", default=str(DEFAULT_UNIVERSE))
    ap.add_argument("--outdir", default=str(DEFAULT_OUTDIR))
    ap.add_argument("--run-id", default=DEFAULT_OUTDIR.name)
    args = ap.parse_args()

    population_path = Path(args.population)
    universe_path = Path(args.universe)
    outdir = Path(args.outdir)
    run_id = args.run_id

    if not population_path.exists():
        raise FileNotFoundError(population_path)
    if not universe_path.exists():
        raise FileNotFoundError(universe_path)

    outdir.mkdir(parents=True, exist_ok=True)

    universe_df = load_universe_tickers(universe_path)
    pop_df = load_population(population_path)
    base, panel_end_date = build_base(pop_df, universe_df)

    cutoffs = [
        CutoffSpec(
            label="2b",
            cutoff_b=2,
            detail_name="market_cap_last_observed_by_ticker.parquet",
            detail_csv_name="market_cap_last_observed_by_ticker.csv",
            cut_name="market_cap_cutoff_lt_2b_active_inactive.parquet",
            cut_csv_name="market_cap_cutoff_lt_2b_active_inactive.csv",
            summary_name="market_cap_cutoff_lt_2b_summary.json",
            class_col="classification",
            reason_col="classification_reason",
        ),
        CutoffSpec(
            label="1b",
            cutoff_b=1,
            detail_name="market_cap_last_observed_by_ticker_1b.parquet",
            detail_csv_name="market_cap_last_observed_by_ticker_1b.csv",
            cut_name="market_cap_cutoff_lt_1b_active_inactive.parquet",
            cut_csv_name="market_cap_cutoff_lt_1b_active_inactive.csv",
            summary_name="market_cap_cutoff_lt_1b_summary.json",
            class_col="classification_1b",
            reason_col="classification_reason_1b",
        ),
    ]

    print("=== INPUTS ===")
    print(f"population: {population_path}")
    print(f"universe:   {universe_path}")
    print(f"outdir:     {outdir}")
    print(f"panel_end_date: {panel_end_date.date()}")
    print(f"universe_tickers: {len(universe_df)}")

    for spec in cutoffs:
        detail, cut, summary = apply_cutoff(base, spec)
        write_outputs(outdir, detail, cut, summary, spec, panel_end_date, run_id)
        print("")
        print(f"=== CUTOFF LT {spec.cutoff_b}B ===")
        print(f"classification_col: {spec.class_col}")
        print(pd.Series(summary["classification_counts"]).to_string())
        print(f"detail_parquet: {outdir / spec.detail_name}")
        print(f"cut_parquet:    {outdir / spec.cut_name}")
        print(f"summary_json:   {outdir / spec.summary_name}")


if __name__ == "__main__":
    main()
