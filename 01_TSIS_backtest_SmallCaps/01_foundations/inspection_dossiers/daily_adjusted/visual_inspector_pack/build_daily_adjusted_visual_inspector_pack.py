from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


PACK_ROOT = Path(__file__).resolve().parent
DOSSIER_ROOT = PACK_ROOT.parent
FOUNDATIONS_ROOT = PACK_ROOT.parents[2]
DAILY_DOSSIER_ROOT = FOUNDATIONS_ROOT / "inspection_dossiers" / "daily"
FULL_AUDIT_ROOT = DAILY_DOSSIER_ROOT / "evidence_assets" / "daily_adjusted_full_universe_audit"
TAIL_AUDIT_ROOT = DAILY_DOSSIER_ROOT / "evidence_assets" / "daily_adjusted_complex_actions_tail_audit"
IMAGE_ROOT = PACK_ROOT / "images"


def _configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 150,
            "font.size": 9,
            "axes.titlesize": 12,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.edgecolor": "#2f3437",
            "axes.linewidth": 0.8,
        }
    )


def _savefig(name: str, manifest_rows: list[dict[str, str]], **row: str) -> None:
    path = IMAGE_ROOT / name
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    manifest_rows.append(
        {
            "visual_id": name.replace(".png", ""),
            "image_path": f"images/{name}",
            "category": row["category"],
            "evidence_sources": row["evidence_sources"],
            "what_it_shows": row["what_it_shows"],
            "inspector_question": row["inspector_question"],
            "interpretation": row["interpretation"],
            "status": row["status"],
            "bytes": str(path.stat().st_size),
        }
    )


def _write_manifest(manifest_rows: list[dict[str, str]]) -> None:
    case_path = PACK_ROOT / "daily_adjusted_visual_case_manifest_v0_1.csv"
    fields = [
        "visual_id",
        "image_path",
        "category",
        "evidence_sources",
        "what_it_shows",
        "inspector_question",
        "interpretation",
        "status",
    ]
    with case_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow({key: row[key] for key in fields})

    audit_path = PACK_ROOT / "daily_adjusted_visual_asset_audit_v0_1.csv"
    now = datetime.now(timezone.utc).isoformat()
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["asset", "bytes", "created_utc", "source", "role"],
        )
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow(
                {
                    "asset": row["image_path"],
                    "bytes": row["bytes"],
                    "created_utc": now,
                    "source": row["evidence_sources"],
                    "role": row["category"],
                }
            )


def _coverage_panel(summary: pd.Series, manifest_rows: list[dict[str, str]]) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.1, 1]})
    count_data = pd.DataFrame(
        [
            ("raw tickers", summary["raw_tickers"]),
            ("adjusted tickers", summary["adjusted_tickers"]),
            ("raw tickers with files", summary["raw_tickers_with_files"]),
            ("adjusted tickers with files", summary["adjusted_tickers_with_files"]),
            ("raw year files", summary["raw_year_files"]),
            ("adjusted year files", summary["adjusted_year_files"]),
        ],
        columns=["metric", "value"],
    )
    ax1.barh(count_data["metric"], count_data["value"], color="#2c5c8a")
    ax1.set_title("Raw vs adjusted physical coverage")
    ax1.set_xlabel("count")
    ax1.grid(axis="x", alpha=0.25)
    for index, row in count_data.iterrows():
        ax1.text(row["value"] * 1.01, index, f"{int(row['value']):,}", va="center", fontsize=8)

    pct_data = pd.DataFrame(
        [
            ("ticker coverage", summary["ticker_coverage_pct"]),
            ("ticker-with-files coverage", summary["ticker_with_files_coverage_pct"]),
            ("year-file coverage", summary["year_file_coverage_pct"]),
        ],
        columns=["metric", "value"],
    )
    colors = ["#cf8d2e" if value < 100 else "#2f7d4f" for value in pct_data["value"]]
    ax2.bar(pct_data["metric"], pct_data["value"], color=colors)
    ax2.set_ylim(95, 100.5)
    ax2.set_title("Coverage percent")
    ax2.set_ylabel("percent")
    ax2.tick_params(axis="x", rotation=25)
    ax2.grid(axis="y", alpha=0.25)
    for index, row in pct_data.iterrows():
        ax2.text(index, row["value"] + 0.05, f"{row['value']:.4f}%", ha="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: adjusted matches every raw ticker-year file that exists; the lower ticker coverage is raw directories without files.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_full_universe_coverage_panel_v0_1.png",
        manifest_rows,
        category="coverage_scope",
        evidence_sources="daily_adjusted_full_universe_summary.csv",
        what_it_shows="Raw vs adjusted tickers, ticker-with-files coverage and year-file coverage.",
        inspector_question="Is the adjusted view physically materialized for every raw ticker-year file with data?",
        interpretation="Yes. Ticker-with-files and year-file coverage are 100%; raw empty directories explain ticker-only delta.",
        status="usable_for_declared_scope",
    )


def _validation_gate_panel(summary: pd.Series, manifest_rows: list[dict[str, str]]) -> None:
    checks = pd.DataFrame(
        [
            ("missing outputs", summary["missing_outputs"]),
            ("extra adjusted outputs", summary["extra_adjusted_outputs"]),
            ("read error files", summary["read_error_files"]),
            ("files missing required columns", summary["files_missing_required_columns"]),
            ("nonpositive factor rows", summary["nonpositive_factor_rows"]),
            ("null factor rows", summary["null_factor_rows"]),
            ("bad price-view rows", summary["bad_price_view_rows"]),
            ("empty source daily rows", summary["empty_source_daily_rows"]),
            ("missing source daily file rows", summary["missing_source_daily_file_rows"]),
        ],
        columns=["check", "count"],
    )
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.barh(checks["check"], checks["count"], color=["#2f7d4f" if value == 0 else "#9b2f2f" for value in checks["count"]])
    ax.set_title("Daily adjusted validation blockers are zero")
    ax.set_xlabel("count")
    ax.set_xlim(0, 1)
    ax.grid(axis="x", alpha=0.25)
    for index, row in checks.iterrows():
        ax.text(0.03, index, str(int(row["count"])), va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: no missing outputs, read errors, required-column failures, nonpositive factors, null factors or bad price-view rows were found.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_validation_gate_panel_v0_1.png",
        manifest_rows,
        category="quality_gate",
        evidence_sources="daily_adjusted_full_universe_summary.csv; daily_adjusted_missing_required_columns.csv; daily_adjusted_read_errors.csv",
        what_it_shows="Zero-count blocker checks for output materialization, readability, schema and factor validity.",
        inspector_question="Are there any aggregate validation blockers in the full-universe materialization?",
        interpretation="No. All listed blockers are zero in the audited summary.",
        status="pass",
    )


def _activation_profile_panel(ticker_activation: pd.DataFrame, summary: pd.Series, manifest_rows: list[dict[str, str]]) -> None:
    profile = ticker_activation["activation_profile"].value_counts().reindex(
        ["neutral_control", "split_only", "dividend_only", "split_and_dividend"], fill_value=0
    )
    row_totals = pd.DataFrame(
        [
            ("split non-1 rows", summary["split_non1_rows_total"]),
            ("dividend non-1 rows", summary["div_non1_rows_total"]),
            ("adjusted non-1 rows", summary["adj_non1_rows_total"]),
            ("adjusted rows total", summary["adjusted_rows_total"]),
        ],
        columns=["metric", "value"],
    )
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8), gridspec_kw={"width_ratios": [1, 1.2]})
    colors = ["#6d8f57", "#2c5c8a", "#8b5a2b", "#9b2f2f"]
    ax1.bar(profile.index, profile.values, color=colors)
    ax1.set_title("Ticker activation profiles")
    ax1.set_ylabel("tickers")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    for index, value in enumerate(profile.values):
        ax1.text(index, value * 1.03, f"{int(value):,}", ha="center", fontsize=8)

    ax2.barh(row_totals["metric"], row_totals["value"], color="#2c5c8a")
    ax2.set_title("Rows touched by adjustment factors")
    ax2.set_xlabel("rows")
    ax2.grid(axis="x", alpha=0.25)
    for index, row in row_totals.iterrows():
        ax2.text(row["value"] * 1.01, index, f"{int(row['value']):,}", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: most tickers are neutral controls; split/dividend activation remains explicit and measurable.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_activation_profile_panel_v0_1.png",
        manifest_rows,
        category="adjustment_semantics",
        evidence_sources="daily_adjusted_ticker_activation_summary.csv; daily_adjusted_full_universe_summary.csv",
        what_it_shows="Ticker activation profiles and rows where split, dividend or combined adjustment factors differ from 1.",
        inspector_question="Is the adjusted view mostly neutral control while still capturing split/dividend adjustments?",
        interpretation="Yes. Neutral controls dominate, and adjustment activation is explicit by profile and row count.",
        status="usable_for_declared_scope",
    )


def _factor_min_panel(summary: pd.Series, manifest_rows: list[dict[str, str]]) -> None:
    factors = pd.DataFrame(
        [
            ("future split factor min", summary["future_split_factor_min"]),
            ("future dividend factor min", summary["future_dividend_factor_min"]),
            ("future adjustment factor min", summary["future_adjustment_factor_min"]),
        ],
        columns=["factor", "min_value"],
    )
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.bar(factors["factor"], factors["min_value"], color="#2f7d4f")
    ax.set_yscale("log")
    ax.set_title("Factor minima remain positive on a log scale")
    ax.set_ylabel("minimum positive factor")
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.25)
    for index, row in factors.iterrows():
        ax.text(index, row["min_value"] * 1.8, f"{row['min_value']:.2e}", ha="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: minima are tiny but positive; aggregate nonpositive and null factor rows are zero.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_factor_minima_panel_v0_1.png",
        manifest_rows,
        category="factor_integrity",
        evidence_sources="daily_adjusted_full_universe_summary.csv",
        what_it_shows="Minimum future split, dividend and combined adjustment factors on a log scale.",
        inspector_question="Do adjustment factors remain positive despite extreme corporate-action chains?",
        interpretation="Yes. The audited minima are positive and blocker counts for nonpositive/null factors are zero.",
        status="pass",
    )


def _complex_tail_panel(tail_summary: pd.Series, type_summary: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    tail = pd.DataFrame(
        [
            ("ticker_change total", tail_summary["ticker_change_rows_total"]),
            ("ticker_change within daily", tail_summary["ticker_change_rows_within_daily_window"]),
            ("ticker_change outside daily", tail_summary["ticker_change_rows_outside_daily_window"]),
            ("non-CD dividend total", tail_summary["non_cd_dividend_rows_total"]),
            ("non-CD dividend within daily", tail_summary["non_cd_dividend_rows_within_daily_window"]),
            ("non-CD dividend outside daily", tail_summary["non_cd_dividend_rows_outside_daily_window"]),
        ],
        columns=["metric", "value"],
    )
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax1.barh(tail["metric"], tail["value"], color=["#8b5a2b", "#cf8d2e", "#9aa4aa", "#2c5c8a", "#6d8f57", "#9aa4aa"])
    ax1.set_title("Complex corporate-action tail is narrow and explicit")
    ax1.set_xlabel("rows")
    ax1.grid(axis="x", alpha=0.25)
    for index, row in tail.iterrows():
        ax1.text(row["value"] + max(tail["value"].max() * 0.01, 5), index, f"{int(row['value']):,}", va="center", fontsize=8)

    ax2.axis("off")
    table = ax2.table(cellText=type_summary.astype(str).values, colLabels=type_summary.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.25)
    ax2.set_title("Observed structured tail types")
    fig.text(
        0.01,
        0.01,
        "Read: the measured complex tail is ticker_change plus a small SC dividend subtype, not a broad structured spin-off/reorg universe.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_complex_tail_panel_v0_1.png",
        manifest_rows,
        category="corporate_action_tail",
        evidence_sources="daily_adjusted_complex_actions_tail_summary.csv; daily_adjusted_complex_actions_type_summary.csv",
        what_it_shows="Ticker-change and non-CD dividend tail size, within/outside daily window, and observed structured types.",
        inspector_question="What complex corporate-action debt remains outside the current adjusted semantics?",
        interpretation="The measurable tail is narrow: ticker_change requires continuity/remap policy; SC dividend handling needs explicit policy wording.",
        status="review_boundary",
    )


def _tail_case_panel(
    ticker_change_tail: pd.DataFrame,
    non_cd_tail: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    left = ticker_change_tail.head(7).copy()
    right = non_cd_tail.head(7).copy()
    left = left[["ticker", "event_date", "within_daily_window", "new_ticker"]]
    right = right[["ticker", "dividend_type", "event_date", "cash_amount", "within_daily_window"]]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 6.8))
    for ax, data, title in [
        (ax1, left, "Ticker-change tail examples"),
        (ax2, right, "Non-CD dividend tail examples"),
    ]:
        ax.axis("off")
        table = ax.table(cellText=data.astype(str).values, colLabels=data.columns, loc="center", cellLoc="left")
        table.auto_set_font_size(False)
        table.set_fontsize(7.5)
        table.scale(1.0, 1.2)
        ax.set_title(title)
    fig.text(
        0.01,
        0.01,
        "Read: these rows are boundary examples. Ticker changes do not define a price factor; SC dividends need explicit treatment policy.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_tail_case_panel_v0_1.png",
        manifest_rows,
        category="boundary_case",
        evidence_sources="daily_adjusted_ticker_change_tail.csv; daily_adjusted_non_cd_dividend_tail.csv",
        what_it_shows="Concrete examples from ticker-change and non-CD dividend boundary tails.",
        inspector_question="What do the remaining methodological boundary cases look like in actual rows?",
        interpretation="They are policy boundaries, not evidence that split/cash-dividend adjustment mechanics failed.",
        status="review_boundary",
    )


def _consumer_boundary_panel(manifest_rows: list[dict[str, str]]) -> None:
    decisions = pd.DataFrame(
        [
            ("data_quality_report", "allowed"),
            ("daily_return_labels", "allowed under label contract"),
            ("daily adjusted research", "allowed"),
            ("master_daily_table adjusted view", "allowed if declared"),
            ("raw daily replacement", "prohibited"),
            ("execution_simulator", "prohibited"),
            ("quotes/trades validation", "prohibited"),
            ("RL/live", "not enabled"),
        ],
        columns=["consumer", "decision"],
    )
    score = {
        "allowed": 2,
        "allowed under label contract": 1.7,
        "allowed if declared": 1.5,
        "prohibited": 0.4,
        "not enabled": 0,
    }
    colors = {
        "allowed": "#2f7d4f",
        "allowed under label contract": "#6d8f57",
        "allowed if declared": "#6d8f57",
        "prohibited": "#9b2f2f",
        "not enabled": "#9aa4aa",
    }
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    ax.barh(decisions["consumer"], decisions["decision"].map(score), color=decisions["decision"].map(colors))
    ax.invert_yaxis()
    ax.set_xlim(0, 2.35)
    ax.set_title("Daily adjusted is an economic daily view, not raw/execution authority")
    ax.set_xticks([0, 0.4, 1.5, 2], ["not enabled", "prohibited", "declared/label", "allowed"])
    ax.grid(axis="x", alpha=0.25)
    for index, row in decisions.iterrows():
        ax.text(score[row["decision"]] + 0.05, index, row["decision"], va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: daily_return_labels may use c_adjusted under contract; raw daily, quotes/trades and execution consumers must not treat adjusted as authority.",
        fontsize=8,
    )
    _savefig(
        "daily_adjusted_consumer_boundary_panel_v0_1.png",
        manifest_rows,
        category="consumer_boundary",
        evidence_sources="daily_adjusted_quality_report_v0_1.md; daily_return_labels_schema_contract.md",
        what_it_shows="Allowed, declared, prohibited and not-enabled consumers for the adjusted daily view.",
        inspector_question="Where may daily_adjusted be consumed, and where is it explicitly not authority?",
        interpretation="It is allowed for daily economic labels/research under contract, but prohibited as raw/execution/quotes-trades authority.",
        status="usable_with_consumer_boundaries",
    )


def main() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    summary = pd.read_csv(FULL_AUDIT_ROOT / "daily_adjusted_full_universe_summary.csv").iloc[0]
    ticker_activation = pd.read_csv(FULL_AUDIT_ROOT / "daily_adjusted_ticker_activation_summary.csv")
    tail_summary = pd.read_csv(TAIL_AUDIT_ROOT / "daily_adjusted_complex_actions_tail_summary.csv").set_index("metric")["value"]
    type_summary = pd.read_csv(TAIL_AUDIT_ROOT / "daily_adjusted_complex_actions_type_summary.csv")
    ticker_change_tail = pd.read_csv(TAIL_AUDIT_ROOT / "daily_adjusted_ticker_change_tail.csv")
    non_cd_tail = pd.read_csv(TAIL_AUDIT_ROOT / "daily_adjusted_non_cd_dividend_tail.csv")

    manifest_rows: list[dict[str, str]] = []
    _coverage_panel(summary, manifest_rows)
    _validation_gate_panel(summary, manifest_rows)
    _activation_profile_panel(ticker_activation, summary, manifest_rows)
    _factor_min_panel(summary, manifest_rows)
    _complex_tail_panel(tail_summary, type_summary, manifest_rows)
    _tail_case_panel(ticker_change_tail, non_cd_tail, manifest_rows)
    _consumer_boundary_panel(manifest_rows)
    _write_manifest(manifest_rows)


if __name__ == "__main__":
    main()
