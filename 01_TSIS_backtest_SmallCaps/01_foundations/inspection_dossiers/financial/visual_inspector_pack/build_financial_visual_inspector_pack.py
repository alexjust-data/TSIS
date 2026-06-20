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
EVIDENCE_ROOT = DOSSIER_ROOT / "evidence_assets"
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
    manifest_path = PACK_ROOT / "financial_visual_case_manifest_v0_1.csv"
    fieldnames = [
        "visual_id",
        "image_path",
        "category",
        "evidence_sources",
        "what_it_shows",
        "inspector_question",
        "interpretation",
        "status",
    ]
    with manifest_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow({key: row[key] for key in fieldnames})

    audit_path = PACK_ROOT / "financial_visual_asset_audit_v0_1.csv"
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


def _endpoint_coverage_heatmap(
    coverage: pd.DataFrame,
    file_quality: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    merged = coverage.merge(file_quality, on="dataset", how="left")
    merged["business_file_pct"] = 100 * (
        merged["files"] - merged["zero_business_files"]
    ) / merged["files"]
    merged["zero_business_file_pct"] = (
        100 * merged["zero_business_files"] / merged["files"]
    )
    merged["missing_required_file_pct"] = (
        100 * merged["missing_required_files"] / merged["files"]
    )

    metrics = [
        "coverage_pct",
        "business_file_pct",
        "zero_business_file_pct",
        "missing_required_file_pct",
    ]
    labels = [
        "download coverage",
        "business files",
        "zero-business files",
        "missing-required files",
    ]
    values = merged.set_index("dataset")[metrics].to_numpy(dtype=float)

    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    cmap = LinearSegmentedColormap.from_list(
        "financial_audit", ["#f7faf8", "#dcecec", "#8fb9c8", "#2b6174"]
    )
    image = ax.imshow(values, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax.set_title("Financial endpoint coverage is complete, but quality is not")
    ax.set_xticks(range(len(labels)), labels, rotation=25, ha="right")
    ax.set_yticks(range(len(merged)), merged["dataset"])
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]:.1f}%", ha="center", va="center")
    fig.colorbar(image, ax=ax, label="percent")
    fig.text(
        0.01,
        0.01,
        "Read: all endpoints have 100% downloaded files; statement endpoints still have large zero-business/missing-required mass.",
        fontsize=8,
    )
    _savefig(
        "financial_endpoint_coverage_heatmap_v0_1.png",
        manifest_rows,
        category="population_coverage",
        evidence_sources="financial_coverage_by_endpoint_v0_1.csv; financial_file_level_quality_summary_v0_1.csv",
        what_it_shows="Coverage by endpoint plus business/zero-business/missing-required file rates.",
        inspector_question="Is physical coverage the same as usable quality?",
        interpretation="No. Coverage is 100%, but statement endpoints contain large zero-business/missing-required mass.",
        status="blocking_context",
    )


def _severe_issue_distribution(
    severe: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    severe = severe.sort_values("issue_count", ascending=False)
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    colors = ["#8f2d2d" if value > 0 else "#6b8e6b" for value in severe["issue_count"]]
    ax.barh(severe["dataset"], severe["issue_count"], color=colors)
    ax.invert_yaxis()
    ax.set_title("Severe issues are concentrated in statement sentinel forms")
    ax.set_xlabel("issue_count")
    for y_pos, value in enumerate(severe["issue_count"]):
        ax.text(value + 80, y_pos, f"{int(value):,}", va="center")
    ax.grid(axis="x", alpha=0.25)
    fig.text(
        0.01,
        0.01,
        "Read: all severe issues in the current evidence are missing_required_cols; ratios are not the severe-issue driver.",
        fontsize=8,
    )
    _savefig(
        "financial_severe_issue_distribution_v0_1.png",
        manifest_rows,
        category="bad_blocking",
        evidence_sources="financial_severe_issue_summary_v0_1.csv",
        what_it_shows="Severe issue counts by endpoint and issue class.",
        inspector_question="Where is the blocker concentrated?",
        interpretation="The blocker is the statement sentinel/schema-audit mismatch, not ratios.",
        status="blocking",
    )


def _temporal_issue_timeline(
    temporal: pd.DataFrame,
    temporal_cases: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    cases = temporal_cases.copy()
    for column in ["start_ref", "end_ref", "fin_min_date", "fin_max_date"]:
        cases[column] = pd.to_datetime(cases[column], errors="coerce", utc=True)

    sample = cases[
        cases["temporal_status"].isin(["ANOMALY_PRE_START", "ANOMALY_POST_END"])
    ].head(10)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [0.9, 1.4]}
    )
    order = ["OK", "NO_DATA", "ANOMALY_PRE_START", "ANOMALY_POST_END"]
    status = temporal.set_index("temporal_status").reindex(order).reset_index()
    colors = ["#2f7d4f", "#9aa4aa", "#cf8d2e", "#9b2f2f"]
    ax1.bar(status["temporal_status"], status["tickers"], color=colors)
    ax1.set_title("Temporal status by ticker")
    ax1.set_ylabel("tickers")
    ax1.tick_params(axis="x", rotation=35)
    for index, value in enumerate(status["tickers"]):
        ax1.text(index, value + 80, f"{int(value):,}", ha="center")
    ax1.grid(axis="y", alpha=0.25)

    for index, (_, row) in enumerate(sample.iterrows()):
        if pd.notna(row["start_ref"]) and pd.notna(row["end_ref"]):
            ax2.plot(
                [row["start_ref"], row["end_ref"]],
                [index, index],
                color="#2c5c8a",
                lw=5,
                solid_capstyle="butt",
                label="reference window" if index == 0 else None,
            )
        if pd.notna(row["fin_min_date"]) and pd.notna(row["fin_max_date"]):
            ax2.plot(
                [row["fin_min_date"], row["fin_max_date"]],
                [index + 0.22, index + 0.22],
                color="#a33a3a",
                lw=5,
                solid_capstyle="butt",
                label="financial observed window" if index == 0 else None,
            )
            ax2.text(
                row["fin_max_date"],
                index + 0.38,
                row["temporal_status"].replace("ANOMALY_", ""),
                fontsize=7,
            )
    ax2.set_yticks(range(len(sample)), sample["ticker"])
    ax2.invert_yaxis()
    ax2.set_title("Sample lifecycle/reference vs financial windows")
    ax2.legend(loc="lower right", fontsize=8)
    ax2.grid(axis="x", alpha=0.25)
    fig.autofmt_xdate(rotation=30)
    fig.text(
        0.01,
        0.01,
        "Read: temporal defects are about lifecycle/PIT alignment, not read errors. Filing availability must not be inferred from period_end alone.",
        fontsize=8,
    )
    _savefig(
        "financial_temporal_issue_timeline_v0_1.png",
        manifest_rows,
        category="flagged_review",
        evidence_sources="financial_temporal_status_summary_v0_1.csv; financial_temporal_issue_sample_manifest_v0_1.csv",
        what_it_shows="Temporal status distribution and concrete lifecycle/financial-window examples.",
        inspector_question="Are financial observations aligned to reference lifecycle windows?",
        interpretation="A large anomaly mass remains; consumption must stay blocked or explicitly filtered.",
        status="review_blocking",
    )


def _empty_sentinel_case_panel(
    file_quality: pd.DataFrame,
    empty: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    summary = file_quality[
        ["dataset", "files", "zero_business_files", "missing_required_files"]
    ].copy()
    summary["zero_business_pct"] = (
        100 * summary["zero_business_files"] / summary["files"]
    )
    examples = empty[
        [
            "dataset",
            "expected_ticker",
            "rows_total",
            "rows_business",
            "missing_required_cols",
            "issues",
        ]
    ].head(8)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6.5), gridspec_kw={"height_ratios": [1, 1.15]}
    )
    ax1.bar(
        summary["dataset"],
        summary["zero_business_files"],
        label="zero-business files",
        color="#b8792d",
    )
    ax1.bar(
        summary["dataset"],
        summary["missing_required_files"],
        bottom=0,
        label="missing-required files",
        color="none",
        edgecolor="#6e1f1f",
        linewidth=2,
    )
    ax1.set_title("Empty/sentinel files explain the statement severe issue mass")
    ax1.set_ylabel("files")
    ax1.tick_params(axis="x", rotation=20)
    for index, row in summary.iterrows():
        ax1.text(
            index,
            row["zero_business_files"] + 130,
            f"{int(row['zero_business_files']):,}\n{row['zero_business_pct']:.1f}%",
            ha="center",
            fontsize=8,
        )
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.25)

    ax2.axis("off")
    table = ax2.table(
        cellText=examples.astype(str).values,
        colLabels=examples.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.28)
    ax2.set_title("Representative empty sentinel rows flagged as missing_required_cols")
    fig.text(
        0.01,
        0.01,
        "Read: sentinel files are readable and expected by schema, but current audit classifies statement sentinels as severe.",
        fontsize=8,
    )
    _savefig(
        "financial_empty_sentinel_case_panel_v0_1.png",
        manifest_rows,
        category="bad_blocking_case",
        evidence_sources="financial_file_level_quality_summary_v0_1.csv; financial_empty_sentinel_example_manifest_v0_1.csv",
        what_it_shows="Zero-business/sentinel mass and concrete sample rows.",
        inspector_question="Are empty files unreadable, or readable sentinel forms with an audit/schema mismatch?",
        interpretation="They are readable sentinel forms, but the validator/audit currently marks statement sentinels severe.",
        status="blocking",
    )


def _multi_cik_identity_panel(
    date_range: pd.DataFrame,
    multi_cik: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    summary = date_range[["dataset", "multi_cik", "with_business_rows"]].copy()
    summary["multi_cik_pct_of_business"] = (
        100 * summary["multi_cik"] / summary["with_business_rows"]
    )
    examples = multi_cik[
        [
            "dataset",
            "expected_ticker",
            "rows_business",
            "cik_nunique",
            "date_start",
            "date_end",
            "issues",
        ]
    ].head(8)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 6.4), gridspec_kw={"height_ratios": [1, 1.1]}
    )
    ax1.bar(summary["dataset"], summary["multi_cik"], color="#6d5a8e")
    ax1.set_title("Multi-CIK examples are identity risk, not a file-read failure")
    ax1.set_ylabel("sampled tickers/files with multi_cik")
    ax1.tick_params(axis="x", rotation=20)
    for index, row in summary.iterrows():
        ax1.text(
            index,
            row["multi_cik"] + 6,
            f"{int(row['multi_cik'])}\n{row['multi_cik_pct_of_business']:.1f}% of business",
            ha="center",
            fontsize=8,
        )
    ax1.grid(axis="y", alpha=0.25)

    ax2.axis("off")
    table = ax2.table(
        cellText=examples.astype(str).values,
        colLabels=examples.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.22)
    ax2.set_title("Representative multi-CIK sample rows")
    fig.text(
        0.01,
        0.01,
        "Read: CIK multiplicity requires identity/lifecycle handling before symbol_master or PIT feature promotion.",
        fontsize=8,
    )
    _savefig(
        "financial_multi_cik_identity_panel_v0_1.png",
        manifest_rows,
        category="identity_review",
        evidence_sources="financial_date_range_summary_v0_1.csv; financial_multi_cik_example_manifest_v0_1.csv",
        what_it_shows="Multi-CIK counts and representative examples.",
        inspector_question="Where can one ticker map to multiple entities or CIK histories?",
        interpretation="Multi-CIK is present in statement endpoints and must remain a review/identity gate.",
        status="review",
    )


def _payload_schema_drift_panel(manifest_rows: list[dict[str, str]]) -> None:
    sample_root = EVIDENCE_ROOT / "sample_payloads"
    files = {
        "income payload": sample_root / "income_statements_A_sample_v0_1.csv",
        "balance payload": sample_root / "balance_sheets_A_sample_v0_1.csv",
        "cashflow payload": sample_root / "cash_flow_statements_A_sample_v0_1.csv",
        "ratio payload": sample_root / "ratios_A_sample_v0_1.csv",
        "statement sentinel": sample_root / "income_statements_AABA_sample_v0_1.csv",
        "ratio sentinel": sample_root / "ratios_AABA_sample_v0_1.csv",
    }
    column_sets = {
        label: set(pd.read_csv(path, nrows=1).columns) for label, path in files.items()
    }
    features = [
        ("ticker", "ticker"),
        ("tickers", "tickers"),
        ("cik", "cik"),
        ("period_end", "period_end"),
        ("filing_date", "filing_date"),
        ("fiscal fields", "fiscal_year"),
        ("timeframe", "timeframe"),
        ("date", "date"),
        ("_empty", "_empty"),
        ("_dataset", "_dataset"),
        ("_ingested_utc", "_ingested_utc"),
        ("business fields", "__business__"),
    ]
    metadata_columns = {
        "ticker",
        "tickers",
        "cik",
        "period_end",
        "filing_date",
        "fiscal_quarter",
        "fiscal_year",
        "timeframe",
        "date",
        "_empty",
        "_dataset",
        "_ingested_utc",
    }
    matrix = []
    counts = []
    for label, columns in column_sets.items():
        row = []
        for _, column in features:
            if column == "__business__":
                row.append(1 if len(columns - metadata_columns) > 0 else 0)
            else:
                row.append(1 if column in columns else 0)
        matrix.append(row)
        counts.append((label, len(columns), max(0, len(columns - metadata_columns))))

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.6, 0.8]}
    )
    cmap = LinearSegmentedColormap.from_list("presence", ["#f3f1ed", "#2f7d4f"])
    ax1.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax1.set_title("Observed payload forms: business rows vs empty sentinels")
    ax1.set_xticks(
        range(len(features)), [feature[0] for feature in features], rotation=45, ha="right"
    )
    ax1.set_yticks(range(len(files)), list(files.keys()))
    for i in range(len(files)):
        for j in range(len(features)):
            ax1.text(j, i, "yes" if matrix[i][j] else "-", ha="center", va="center", fontsize=7)

    ax2.axis("off")
    count_df = pd.DataFrame(counts, columns=["form", "columns", "business_like_cols"])
    table = ax2.table(
        cellText=count_df.astype(str).values,
        colLabels=count_df.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.25)
    ax2.set_title("Column counts")
    fig.text(
        0.01,
        0.01,
        "Read: payload rows have business columns and PIT fields; sentinels are compact by design. The audit must distinguish valid sentinel form from missing required business payload.",
        fontsize=8,
    )
    _savefig(
        "financial_payload_schema_drift_panel_v0_1.png",
        manifest_rows,
        category="schema_form",
        evidence_sources="sample_payloads/*.csv; financial_empty_sentinel_example_manifest_v0_1.csv",
        what_it_shows="Observed column-form matrix across payloads and sentinels.",
        inspector_question="Are all files expected to have the same business columns?",
        interpretation="No. Sentinels are a different valid physical form, but current audit treats some as severe missing-required cases.",
        status="blocking_context",
    )


def build() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    coverage = pd.read_csv(EVIDENCE_ROOT / "financial_coverage_by_endpoint_v0_1.csv")
    file_quality = pd.read_csv(EVIDENCE_ROOT / "financial_file_level_quality_summary_v0_1.csv")
    severe = pd.read_csv(EVIDENCE_ROOT / "financial_severe_issue_summary_v0_1.csv")
    temporal = pd.read_csv(EVIDENCE_ROOT / "financial_temporal_status_summary_v0_1.csv")
    temporal_cases = pd.read_csv(
        EVIDENCE_ROOT / "financial_temporal_issue_sample_manifest_v0_1.csv"
    )
    empty = pd.read_csv(EVIDENCE_ROOT / "financial_empty_sentinel_example_manifest_v0_1.csv")
    multi_cik = pd.read_csv(EVIDENCE_ROOT / "financial_multi_cik_example_manifest_v0_1.csv")
    date_range = pd.read_csv(EVIDENCE_ROOT / "financial_date_range_summary_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _endpoint_coverage_heatmap(coverage, file_quality, manifest_rows)
    _severe_issue_distribution(severe, manifest_rows)
    _temporal_issue_timeline(temporal, temporal_cases, manifest_rows)
    _empty_sentinel_case_panel(file_quality, empty, manifest_rows)
    _multi_cik_identity_panel(date_range, multi_cik, manifest_rows)
    _payload_schema_drift_panel(manifest_rows)
    _write_manifest(manifest_rows)

    print(f"created {len(manifest_rows)} financial visual assets")
    for row in manifest_rows:
        print(f"{row['image_path']} {row['bytes']} bytes")


if __name__ == "__main__":
    build()
