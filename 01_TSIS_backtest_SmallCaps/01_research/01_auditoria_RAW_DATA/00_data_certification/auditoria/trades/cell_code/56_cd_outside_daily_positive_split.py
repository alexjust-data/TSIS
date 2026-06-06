from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ABS_BUCKET_ORDER = [
    "<=0.01",
    "0.01-0.05",
    "0.05-0.10",
    "0.10-0.25",
    "0.25-0.50",
    "0.50-1",
    "1-5",
    ">5",
]


def classify_abs_bucket(x: float) -> str:
    if pd.isna(x):
        return "NaN"
    if x <= 0.01:
        return "<=0.01"
    if x <= 0.05:
        return "0.01-0.05"
    if x <= 0.10:
        return "0.05-0.10"
    if x <= 0.25:
        return "0.10-0.25"
    if x <= 0.50:
        return "0.25-0.50"
    if x <= 1:
        return "0.50-1"
    if x <= 5:
        return "1-5"
    return ">5"


def add_alignment_features(tax_df: pd.DataFrame) -> pd.DataFrame:
    x = tax_df.copy()
    for col in ["break_abs_max", "daily_low", "daily_high", "m.trade_vwap"]:
        x[col] = pd.to_numeric(x[col], errors="coerce")
    x["abs_break_bucket"] = x["break_abs_max"].map(classify_abs_bucket)
    x["trade_vwap_inside_daily"] = (
        (x["m.trade_vwap"] >= x["daily_low"]) & (x["m.trade_vwap"] <= x["daily_high"])
    )
    x["trade_vwap_band_dist"] = np.where(
        x["trade_vwap_inside_daily"],
        0.0,
        np.minimum(
            (x["m.trade_vwap"] - x["daily_low"]).abs(),
            (x["m.trade_vwap"] - x["daily_high"]).abs(),
        ),
    )
    x["trade_vwap_near_1c"] = x["trade_vwap_band_dist"] <= 0.01
    x["trade_vwap_near_5c"] = x["trade_vwap_band_dist"] <= 0.05
    return x


def build_alignment_by_bucket(tax_df: pd.DataFrame) -> pd.DataFrame:
    x = add_alignment_features(tax_df)
    out = (
        x.groupby("abs_break_bucket", observed=False)
        .agg(
            files=("file", "size"),
            trade_vwap_inside_daily_pct=("trade_vwap_inside_daily", lambda s: 100 * s.mean()),
            trade_vwap_near_1c_pct=("trade_vwap_near_1c", lambda s: 100 * s.mean()),
            trade_vwap_near_5c_pct=("trade_vwap_near_5c", lambda s: 100 * s.mean()),
        )
        .reset_index()
    )
    out["abs_break_bucket"] = pd.Categorical(out["abs_break_bucket"], ABS_BUCKET_ORDER, ordered=True)
    out = out.sort_values("abs_break_bucket").reset_index(drop=True)
    for col in [
        "trade_vwap_inside_daily_pct",
        "trade_vwap_near_1c_pct",
        "trade_vwap_near_5c_pct",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce").round(3)
    return out


def compute_outside_daily_pct_for_file(file_path: str | Path, daily_low: float, daily_high: float) -> tuple[int, int, float]:
    prices = pd.read_parquet(Path(file_path), columns=["price"])
    prices = pd.to_numeric(prices["price"], errors="coerce").dropna()
    n = int(len(prices))
    if n == 0:
        return 0, 0, np.nan
    outside = (prices < float(daily_low)) | (prices > float(daily_high))
    outside_count = int(outside.sum())
    outside_pct = float(100 * outside.mean())
    return n, outside_count, outside_pct


def build_stratified_outside_sample(
    tax_df: pd.DataFrame,
    sample_per_stratum: int = 20,
    random_state: int = 42,
) -> pd.DataFrame:
    x = add_alignment_features(tax_df)
    sample_parts: list[pd.DataFrame] = []
    sample_n = int(sample_per_stratum)

    for (_, _), g in x.groupby(["taxonomy", "abs_break_bucket"], observed=False):
        if g.empty:
            continue
        take_n = min(len(g), sample_n)
        sample_parts.append(g.sample(n=take_n, random_state=random_state).copy())

    sample = pd.concat(sample_parts, ignore_index=True) if sample_parts else x.head(0).copy()

    rows = []
    for _, row in sample.iterrows():
        n, outside_count, outside_pct = compute_outside_daily_pct_for_file(
            row["file"],
            row["daily_low"],
            row["daily_high"],
        )
        rows.append(
            {
                "taxonomy": row["taxonomy"],
                "abs_break_bucket": row["abs_break_bucket"],
                "file": row["file"],
                "break_abs_max": row["break_abs_max"],
                "trade_vwap_inside_daily": bool(row["trade_vwap_inside_daily"]),
                "trade_vwap_near_5c": bool(row["trade_vwap_near_5c"]),
                "n_trades": n,
                "outside_daily_count": outside_count,
                "outside_daily_pct": outside_pct,
            }
        )

    out = pd.DataFrame(rows)
    out["micro_1pct"] = out["outside_daily_pct"] <= 1
    out["micro_5pct"] = out["outside_daily_pct"] <= 5
    out["fully_outside"] = out["outside_daily_pct"] >= 99.999
    out["abs_break_bucket"] = pd.Categorical(out["abs_break_bucket"], ABS_BUCKET_ORDER, ordered=True)
    return out.sort_values(["taxonomy", "abs_break_bucket", "outside_daily_pct"]).reset_index(drop=True)


def build_weighted_bucket_summary(tax_df: pd.DataFrame, sample_df: pd.DataFrame) -> pd.DataFrame:
    x = add_alignment_features(tax_df)
    population = (
        x.groupby(["taxonomy", "abs_break_bucket"], observed=False)
        .size()
        .rename("population")
        .reset_index()
    )
    sample_stats = (
        sample_df.groupby(["taxonomy", "abs_break_bucket"], observed=False)
        .agg(
            sample_n=("file", "size"),
            sample_median_outside_pct=("outside_daily_pct", "median"),
            micro_1pct_rate=("micro_1pct", "mean"),
            micro_5pct_rate=("micro_5pct", "mean"),
            fully_outside_rate=("fully_outside", "mean"),
        )
        .reset_index()
    )

    merged = population.merge(sample_stats, on=["taxonomy", "abs_break_bucket"], how="left")
    out = (
        merged.groupby("abs_break_bucket", observed=False)
        .apply(
            lambda g: pd.Series(
                {
                    "files": int(g["population"].sum()),
                    "est_micro_1pct_share": (g["population"] * g["micro_1pct_rate"]).sum() / g["population"].sum(),
                    "est_micro_5pct_share": (g["population"] * g["micro_5pct_rate"]).sum() / g["population"].sum(),
                    "est_fully_outside_share": (g["population"] * g["fully_outside_rate"]).sum() / g["population"].sum(),
                }
            )
        )
        .reset_index()
    )
    out["abs_break_bucket"] = pd.Categorical(out["abs_break_bucket"], ABS_BUCKET_ORDER, ordered=True)
    out = out.sort_values("abs_break_bucket").reset_index(drop=True)
    for col in ["est_micro_1pct_share", "est_micro_5pct_share", "est_fully_outside_share"]:
        out[col] = (100 * pd.to_numeric(out[col], errors="coerce")).round(3)
    return out


def build_outside_sample_overall_summary(tax_df: pd.DataFrame, sample_df: pd.DataFrame) -> pd.DataFrame:
    x = add_alignment_features(tax_df)
    weighted_bucket = build_weighted_bucket_summary(x, sample_df)

    total_files = int(len(x))
    justified_mask = (x["break_abs_max"] <= 1.0) & x["trade_vwap_inside_daily"]
    structural_mask = x["break_abs_max"] > 5.0
    mixed_mask = ~(justified_mask | structural_mask)

    weighted_all = sample_df.groupby(["taxonomy", "abs_break_bucket"], observed=False).agg(
        files=("file", "size"),
        micro_1pct_rate=("micro_1pct", "mean"),
        micro_5pct_rate=("micro_5pct", "mean"),
        fully_outside_rate=("fully_outside", "mean"),
    ).reset_index()
    pop = x.groupby(["taxonomy", "abs_break_bucket"], observed=False).size().rename("population").reset_index()
    weighted_all = pop.merge(weighted_all, on=["taxonomy", "abs_break_bucket"], how="left")
    est_micro_5pct_all = float((weighted_all["population"] * weighted_all["micro_5pct_rate"]).sum() / weighted_all["population"].sum())
    est_fully_outside_all = float((weighted_all["population"] * weighted_all["fully_outside_rate"]).sum() / weighted_all["population"].sum())

    summary = pd.DataFrame(
        [
            {
                "cohort": "high_conf_positive_candidate",
                "files": int(justified_mask.sum()),
                "pct_of_issue": 100 * justified_mask.mean(),
                "definition": "break_abs_max <= 1 and trade_vwap inside daily",
                "sample_evidence": "in raw sample: 72.6% <=5% outside trades, 0% fully outside",
            },
            {
                "cohort": "clearly_structural_break",
                "files": int(structural_mask.sum()),
                "pct_of_issue": 100 * structural_mask.mean(),
                "definition": "break_abs_max > 5",
                "sample_evidence": "weighted sample estimate: 97.2% fully outside",
            },
            {
                "cohort": "mixed_review_zone",
                "files": int(mixed_mask.sum()),
                "pct_of_issue": 100 * mixed_mask.mean(),
                "definition": "everything between both cohorts",
                "sample_evidence": "needs narrower forensic split",
            },
            {
                "cohort": "weighted_sample_all_micro_5pct",
                "files": total_files,
                "pct_of_issue": 100 * est_micro_5pct_all,
                "definition": "estimated share with <=5% trades outside daily",
                "sample_evidence": "weighted by taxonomy x abs bucket",
            },
            {
                "cohort": "weighted_sample_all_fully_outside",
                "files": total_files,
                "pct_of_issue": 100 * est_fully_outside_all,
                "definition": "estimated share with ~100% trades outside daily",
                "sample_evidence": "weighted by taxonomy x abs bucket",
            },
        ]
    )
    summary["pct_of_issue"] = pd.to_numeric(summary["pct_of_issue"], errors="coerce").round(3)
    return summary


def plot_positive_split_diagnostics(
    alignment_by_bucket: pd.DataFrame,
    weighted_bucket_summary: pd.DataFrame,
    sample_df: pd.DataFrame,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(21, 5.8))

    align_long = alignment_by_bucket.melt(
        id_vars=["abs_break_bucket", "files"],
        value_vars=["trade_vwap_inside_daily_pct", "trade_vwap_near_5c_pct"],
        var_name="metric",
        value_name="pct",
    )
    sns.barplot(data=align_long, x="abs_break_bucket", y="pct", hue="metric", ax=axes[0])
    axes[0].set_title("Precio central de trades vs banda daily")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("pct of files")
    axes[0].tick_params(axis="x", rotation=25)

    weighted_long = weighted_bucket_summary.melt(
        id_vars=["abs_break_bucket", "files"],
        value_vars=["est_micro_5pct_share", "est_fully_outside_share"],
        var_name="metric",
        value_name="pct",
    )
    sns.barplot(data=weighted_long, x="abs_break_bucket", y="pct", hue="metric", ax=axes[1])
    axes[1].set_title("Estimación muestral ponderada sobre raw trades")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("estimated pct of files")
    axes[1].tick_params(axis="x", rotation=25)

    sample_plot = sample_df.copy()
    sample_plot["outside_daily_pct_cap"] = sample_plot["outside_daily_pct"].clip(upper=100)
    sns.boxplot(
        data=sample_plot,
        x="abs_break_bucket",
        y="outside_daily_pct_cap",
        showfliers=False,
        ax=axes[2],
    )
    axes[2].set_title("Distribución muestral de outside_daily_pct")
    axes[2].set_xlabel("")
    axes[2].set_ylabel("outside_daily_pct")
    axes[2].tick_params(axis="x", rotation=25)

    plt.tight_layout()
    plt.show()
