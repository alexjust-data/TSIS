from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"
CORE_ROOT = DOSSIER_DIR / "evidence_assets" / "core_quality"
RAW_ROOT = DOSSIER_DIR / "evidence_assets" / "raw_1m_lt1b_closeout"
CASEPACK_ROOT = DOSSIER_DIR / "core_quality_case_evidence_packs"
POP_ROOT = CASEPACK_ROOT / "population_visual_overview"
POP_ROOT.mkdir(parents=True, exist_ok=True)

CORE_MANIFEST_PATH = CORE_ROOT / "minute_core_quality_manifest_v0_1.parquet"
RAW_CLOSEOUT_PATH = RAW_ROOT / "raw_1m_lt1b_filtered_closeout.parquet"
RAW_BUCKET_SUMMARY_PATH = RAW_ROOT / "raw_1m_lt1b_bucket_summary.csv"
VISUAL_CASE_MANIFEST_PATH = CASEPACK_ROOT / "minute_core_quality_visual_case_manifest_v0_1.csv"
POP_MANIFEST_PATH = POP_ROOT / "minute_population_visual_manifest_v0_1.csv"


def load_core() -> pd.DataFrame:
    return pd.read_parquet(CORE_MANIFEST_PATH)


def savefig(fig: plt.Figure, name: str, title: str, question: str) -> dict[str, str]:
    path = POP_ROOT / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return {
        "image": name,
        "title": title,
        "question": question,
        "image_path": str(path),
    }


def barh_counts(ax, counts: pd.Series, title: str, color: str = "#4c78a8", max_labels: int = 20) -> None:
    counts = counts.head(max_labels).sort_values()
    ax.barh(counts.index.astype(str), counts.values, color=color)
    ax.set_title(title, loc="left", fontsize=11, weight="bold")
    ax.grid(True, axis="x", alpha=0.25)
    total = counts.sum()
    for i, (idx, val) in enumerate(counts.items()):
        ax.text(val, i, f" {val:,}", va="center", fontsize=8)
    ax.set_xlabel("ticker-month rows")


def export_state_overview(df: pd.DataFrame) -> dict[str, str]:
    fig, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
    dims = [
        ("core_quality_state", "Core quality state", "#4c78a8"),
        ("vw_quality_state", "VW quality state", "#d62728"),
        ("combined_quality_state", "Combined core/vw state", "#7a5195"),
        ("allowed_consumption", "Allowed consumption", "#59a14f"),
    ]
    for ax, (col, title, color) in zip(axes.ravel(), dims):
        counts = df[col].astype(str).value_counts()
        ax.bar(counts.index.astype(str), counts.values, color=color)
        ax.set_title(title, loc="left", fontsize=11, weight="bold")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(True, axis="y", alpha=0.25)
        for i, val in enumerate(counts.values):
            ax.text(i, val, f"{val:,}", ha="center", va="bottom", fontsize=8)
    fig.suptitle("Minute raw <1B> | core/vw states and consumption", fontsize=16, weight="bold")
    return savefig(
        fig,
        "00_population_core_vw_state_overview.png",
        "Core/VW State Overview",
        "How the full <1B> minute universe splits across core quality, vw quality, combined state and allowed consumption.",
    )


def export_core_vw_matrix(df: pd.DataFrame) -> dict[str, str]:
    mat = pd.crosstab(df["core_quality_state"], df["vw_quality_state"]).reindex(index=["good", "review", "bad"], columns=["good", "review", "bad"]).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    im = ax.imshow(mat.values, cmap="Blues")
    ax.set_xticks(range(len(mat.columns)), mat.columns)
    ax.set_yticks(range(len(mat.index)), mat.index)
    ax.set_xlabel("vw_quality_state")
    ax.set_ylabel("core_quality_state")
    ax.set_title("Core x VW quality matrix", loc="left", fontsize=13, weight="bold")
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{int(mat.iloc[i, j]):,}", ha="center", va="center", color="#111111")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return savefig(
        fig,
        "01_population_core_vw_matrix.png",
        "Core/VW Matrix",
        "Which combinations dominate: core good with vw bad, core good with vw usable, or core review.",
    )


def export_family_distributions(df: pd.DataFrame) -> list[dict[str, str]]:
    outputs = []
    fig, axes = plt.subplots(1, 2, figsize=(17, 7), constrained_layout=True)
    barh_counts(axes[0], df["core_issue_family"].astype(str).value_counts(), "Core issue families", "#4c78a8")
    barh_counts(axes[1], df["vw_issue_family"].astype(str).value_counts(), "VW issue families", "#d62728")
    fig.suptitle("Minute raw <1B> | issue family distributions", fontsize=16, weight="bold")
    outputs.append(
        savefig(
            fig,
            "02_population_issue_family_distributions.png",
            "Issue Family Distributions",
            "Which core and vw families explain the full universe before looking at individual cases.",
        )
    )
    return outputs


def export_coverage(df: pd.DataFrame) -> dict[str, str]:
    fig, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
    axes[0, 0].hist(df["m.active_days"].dropna(), bins=50, color="#4c78a8")
    axes[0, 0].set_title("Active days per ticker-month", loc="left", weight="bold")
    axes[0, 1].hist(df["m.coverage_ratio_vs_active_days_est"].dropna(), bins=50, color="#59a14f")
    axes[0, 1].set_title("Coverage ratio vs estimated active days", loc="left", weight="bold")
    axes[1, 0].hist(df["m.max_gap_days"].dropna(), bins=50, color="#f28e2b")
    axes[1, 0].set_title("Max internal gap days", loc="left", weight="bold")
    by_year = df.groupby("year").size()
    axes[1, 1].plot(by_year.index, by_year.values, color="#7a5195", marker="o", linewidth=1.5)
    axes[1, 1].set_title("Ticker-month rows by year", loc="left", weight="bold")
    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    fig.suptitle("Minute raw <1B> | coverage and temporal footprint", fontsize=16, weight="bold")
    return savefig(
        fig,
        "03_population_coverage_and_temporal_footprint.png",
        "Coverage And Temporal Footprint",
        "Whether review states are driven by sparse months, large gaps, or temporal availability.",
    )


def export_schema_only(df: pd.DataFrame) -> dict[str, str]:
    raw = pd.read_parquet(RAW_CLOSEOUT_PATH)
    schema = raw[raw["operational_decision"].astype(str).eq("RESCUE_SCHEMA_ONLY")].copy()
    if "warn_signature" not in schema.columns:
        schema["warn_signature"] = schema.get("warns", "").astype(str)
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), constrained_layout=True)
    warn_counts = schema["warn_signature"].astype(str).value_counts().head(10).sort_values()
    axes[0, 0].barh(warn_counts.index, warn_counts.values, color="#4c78a8")
    axes[0, 0].set_title("Schema-only warning signatures", loc="left", weight="bold")
    ticker_counts = schema["ticker"].astype(str).value_counts().head(15).sort_values()
    axes[0, 1].barh(ticker_counts.index, ticker_counts.values, color="#59a14f")
    axes[0, 1].set_title("Top tickers in schema-only", loc="left", weight="bold")
    axes[1, 0].hist(pd.to_numeric(schema.get("rows_after_parse", schema.get("m.rows_after_parse")), errors="coerce").dropna(), bins=50, color="#f28e2b")
    axes[1, 0].set_title("Rows after parse in schema-only", loc="left", weight="bold")
    if "ym" in schema.columns:
        ym = schema.groupby("ym").size()
    else:
        ym = schema.assign(ym=schema["year"].astype(str) + "-" + schema["month"].astype(int).astype(str).str.zfill(2)).groupby("ym").size()
    axes[1, 1].plot(range(len(ym)), ym.values, color="#7a5195", linewidth=1.2)
    axes[1, 1].set_title("Schema-only cases over year-month sequence", loc="left", weight="bold")
    for ax in axes.ravel():
        ax.grid(True, alpha=0.25)
    fig.suptitle("Minute raw <1B> | schema-only block anatomy", fontsize=16, weight="bold")
    return savefig(
        fig,
        "04_population_schema_only_anatomy.png",
        "Schema-Only Anatomy",
        "Whether the 5.89% non-vw block is heterogeneous or dominated by structural schema/readability issues.",
    )


def export_visual_recalc_delta(df: pd.DataFrame) -> dict[str, str]:
    visual = pd.read_csv(VISUAL_CASE_MANIFEST_PATH)
    subset = visual[visual["visual_section"].eq("core_good_vw_not_flagged")].copy()
    fig, axes = plt.subplots(1, 2, figsize=(15, 5), constrained_layout=True)
    labels = subset["ticker"].astype(str) + " " + subset["year"].astype(int).astype(str) + "-" + subset["month"].astype(int).astype(str).str.zfill(2)
    axes[0].bar(labels, subset["visual_gt_1bp_vw_ratio_pct"], color="#d62728")
    axes[0].set_title("Visual recalculated vw outside >1bp in vw_not_flagged sample", loc="left", weight="bold")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].set_ylabel("visual >1bp vw outside %")
    axes[1].scatter(subset["recalc_strict_vw_ratio_pct"], subset["visual_gt_1bp_vw_ratio_pct"], color="#4c78a8", s=55)
    for _, r in subset.iterrows():
        axes[1].annotate(str(r["ticker"]), (r["recalc_strict_vw_ratio_pct"], r["visual_gt_1bp_vw_ratio_pct"]), fontsize=8)
    axes[1].set_xlabel("strict recalculated vw outside %")
    axes[1].set_ylabel("visual >1bp vw outside %")
    axes[1].set_title("Strict vs visually material recalculation", loc="left", weight="bold")
    for ax in axes:
        ax.grid(True, alpha=0.25)
    fig.suptitle("Minute raw <1B> | inherited vw_not_flagged vs visual recalculation", fontsize=16, weight="bold")
    return savefig(
        fig,
        "05_population_vw_not_flagged_visual_recalc_delta.png",
        "VW Not Flagged Visual Recalculation Delta",
        "Whether inherited vw_not_flagged means visually clean in the exported case sample.",
    )


def export_consumption_by_time(df: pd.DataFrame) -> dict[str, str]:
    pivot = df.pivot_table(index="year", columns="allowed_consumption", values="ticker", aggfunc="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(15, 6), constrained_layout=True)
    pivot.plot(kind="area", stacked=True, ax=ax, alpha=0.85)
    ax.set_title("Allowed consumption by year", loc="left", fontsize=13, weight="bold")
    ax.set_ylabel("ticker-month rows")
    ax.grid(True, alpha=0.25)
    return savefig(
        fig,
        "06_population_allowed_consumption_by_year.png",
        "Allowed Consumption By Year",
        "How consumption states distribute across the 2005-2026 footprint.",
    )


def main() -> None:
    df = load_core()
    rows = []
    rows.append(export_state_overview(df))
    rows.append(export_core_vw_matrix(df))
    rows.extend(export_family_distributions(df))
    rows.append(export_coverage(df))
    rows.append(export_schema_only(df))
    rows.append(export_visual_recalc_delta(df))
    rows.append(export_consumption_by_time(df))
    out = pd.DataFrame(rows)
    out.to_csv(POP_MANIFEST_PATH, index=False)
    print(f"exported_population_visuals={len(out)}")
    print(POP_MANIFEST_PATH)
    print(out[["image", "title"]].to_string(index=False))


if __name__ == "__main__":
    main()
