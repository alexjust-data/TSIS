from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
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
    case_path = PACK_ROOT / "short_review_visual_case_manifest_v0_1.csv"
    case_fields = [
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
        writer = csv.DictWriter(handle, fieldnames=case_fields)
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow({key: row[key] for key in case_fields})

    audit_path = PACK_ROOT / "short_review_visual_asset_audit_v0_1.csv"
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


def _coverage_timeline(profile: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = profile.copy()
    data["date_min_dt"] = pd.to_datetime(data["date_min"], errors="coerce")
    data["date_max_dt"] = pd.to_datetime(data["date_max"], errors="coerce")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    width = 0.35
    x = range(len(data))
    ax1.bar([i - width / 2 for i in x], data["rows"], width=width, label="rows", color="#2c5c8a")
    ax1b = ax1.twinx()
    ax1b.bar([i + width / 2 for i in x], data["tickers"], width=width, label="tickers", color="#6d8f57")
    ax1.set_xticks(list(x), data["dataset"], rotation=20)
    ax1.set_title("FINRA baseline coverage")
    ax1.set_ylabel("rows")
    ax1b.set_ylabel("tickers")
    ax1.grid(axis="y", alpha=0.25)
    for index, row in data.iterrows():
        ax1.text(index - width / 2, row["rows"] * 1.03, f"{int(row['rows']):,}", ha="center", fontsize=8)
        ax1b.text(index + width / 2, row["tickers"] * 1.04, f"{int(row['tickers']):,}", ha="center", fontsize=8)

    for index, row in data.iterrows():
        color = "#2c5c8a" if row["dataset"] == "short_interest" else "#8b5a2b"
        ax2.plot([row["date_min_dt"], row["date_max_dt"]], [index, index], lw=10, color=color, solid_capstyle="butt")
        ax2.text(row["date_min_dt"], index + 0.18, str(row["date_min"]), fontsize=8, ha="left")
        ax2.text(row["date_max_dt"], index + 0.18, str(row["date_max"]), fontsize=8, ha="right")
    ax2.set_yticks(range(len(data)), data["dataset"])
    ax2.set_title("Available official/free date windows")
    ax2.grid(axis="x", alpha=0.25)
    fig.autofmt_xdate(rotation=30)
    fig.text(
        0.01,
        0.01,
        "Read: FINRA baseline coverage is strong for its available window, but it does not prove full 2005-2026 history.",
        fontsize=8,
    )
    _savefig(
        "short_review_finra_coverage_timeline_v0_1.png",
        manifest_rows,
        category="coverage_scope",
        evidence_sources="short_review_aggregate_profile_v0_1.csv",
        what_it_shows="Rows, tickers and official/free date windows for FINRA short interest and short volume.",
        inspector_question="What coverage does the FINRA baseline actually prove?",
        interpretation="It proves official/free baseline coverage within observed windows, not full-history replacement.",
        status="scoped",
    )


def _duplicate_key_concentration(
    dup_by_ticker: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = dup_by_ticker.sort_values("excess_rows", ascending=False)
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(data["ticker"], data["excess_rows"], color="#9b2f2f", label="excess rows")
    ax.plot(data["ticker"], data["duplicate_keys"], marker="o", color="#2c5c8a", label="duplicate keys")
    ax.set_title("Short volume duplicate keys are concentrated in three tickers")
    ax.set_ylabel("count")
    ax.grid(axis="y", alpha=0.25)
    ax.set_ylim(0, max(data["excess_rows"]) * 1.22)
    for index, row in data.iterrows():
        ax.text(row["ticker"], row["excess_rows"] + max(data["excess_rows"]) * 0.035, f"{int(row['excess_rows']):,} excess\n{row['date_min']} to {row['date_max']}", ha="center", fontsize=8)
    ax.legend(fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: duplicate-key risk is not spread evenly; CPS dominates, followed by OP and LFTR.",
        fontsize=8,
    )
    _savefig(
        "short_review_duplicate_key_concentration_v0_1.png",
        manifest_rows,
        category="flagged_review",
        evidence_sources="short_review_short_volume_duplicate_key_by_ticker_v0_1.csv",
        what_it_shows="Duplicate key and excess row concentration by ticker.",
        inspector_question="Where is duplicate short-volume key risk concentrated?",
        interpretation="CPS dominates duplicate excess rows; OP and LFTR are smaller but explicit review cases.",
        status="review",
    )


def _duplicate_key_case_panel(manifest_rows: list[dict[str, str]]) -> None:
    manifest = pd.read_csv(EVIDENCE_ROOT / "short_review_short_volume_duplicate_key_manifest_v0_1.csv")
    sample = pd.read_csv(EVIDENCE_ROOT / "sample_payloads" / "short_volume_duplicate_key_sample_v0_1.csv")
    table_1 = manifest.head(10)
    table_2 = sample.head(8)
    keep = [column for column in ["ticker", "date", "total_volume", "short_volume", "short_volume_ratio"] if column in table_2.columns]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.2), gridspec_kw={"height_ratios": [1, 1.1]})
    ax1.axis("off")
    t1 = ax1.table(cellText=table_1.astype(str).values, colLabels=table_1.columns, loc="center", cellLoc="left")
    t1.auto_set_font_size(False)
    t1.set_fontsize(7)
    t1.scale(1, 1.2)
    ax1.set_title("Duplicate key manifest sample")

    ax2.axis("off")
    t2 = ax2.table(cellText=table_2[keep].astype(str).values, colLabels=keep, loc="center", cellLoc="left")
    t2.auto_set_font_size(False)
    t2.set_fontsize(7)
    t2.scale(1, 1.25)
    ax2.set_title("Representative duplicate-key payload rows")
    fig.text(
        0.01,
        0.01,
        "Read: consumers must not collapse ticker+date duplicate rows silently; venue/source semantics need explicit handling.",
        fontsize=8,
    )
    _savefig(
        "short_review_duplicate_key_case_panel_v0_1.png",
        manifest_rows,
        category="flagged_case",
        evidence_sources="short_review_short_volume_duplicate_key_manifest_v0_1.csv; sample_payloads/short_volume_duplicate_key_sample_v0_1.csv",
        what_it_shows="Concrete duplicate ticker+date keys and representative payload rows.",
        inspector_question="What does a duplicate short-volume key look like in actual rows?",
        interpretation="Multiple rows can share ticker+date; consumers need a repair or aggregation policy.",
        status="review",
    )


def _finra_vs_local_overlap(
    comparison: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = comparison.copy()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(data["dataset"], data["intersection"], color="#2f7d4f", label="intersection")
    ax.bar(data["dataset"], data["local_only"], bottom=data["intersection"], color="#cf8d2e", label="local only")
    ax.bar(data["dataset"], data["finra_only"], bottom=data["intersection"] + data["local_only"], color="#6a7f95", label="FINRA only")
    ax.set_title("FINRA baseline overlaps local short, but does not replace it silently")
    ax.set_ylabel("ticker files")
    ax.grid(axis="y", alpha=0.25)
    for index, row in data.iterrows():
        ax.text(index, row["intersection"] / 2, f"overlap\n{int(row['intersection']):,}", ha="center", va="center", color="white", fontsize=8)
        ax.text(index, row["intersection"] + row["local_only"] / 2, f"local-only\n{int(row['local_only'])}", ha="center", va="center", fontsize=8)
    ax.legend(fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: FINRA covers the current common universe strongly, but local-only tickers remain review cases.",
        fontsize=8,
    )
    _savefig(
        "short_review_finra_vs_local_overlap_panel_v0_1.png",
        manifest_rows,
        category="coverage_comparison",
        evidence_sources="short_review_local_comparison_summary_v0_1.csv",
        what_it_shows="Intersection, local-only and FINRA-only counts against local short roots.",
        inspector_question="Can FINRA short_review silently replace local short?",
        interpretation="No. FINRA is a baseline/provenance layer; local-only tickers and history gaps remain.",
        status="scoped",
    )


def _numeric_sanity_panel(
    numeric: pd.DataFrame,
    nulls: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = numeric.copy()
    data["field"] = data["dataset"] + ":" + data["column"]
    data = data.sort_values(["dataset", "column"])
    matrix = data[["nulls", "negative_rows", "inf_rows"]].astype(float).to_numpy()
    max_value = matrix.max() if matrix.max() > 0 else 1
    matrix_scaled = matrix / max_value

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8), gridspec_kw={"width_ratios": [1.1, 0.9]})
    cmap = LinearSegmentedColormap.from_list("numeric", ["#f4f1e8", "#cf8d2e", "#9b2f2f"])
    ax1.imshow(matrix_scaled, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax1.set_title("Numeric sanity: null/negative/inf checks")
    ax1.set_xticks(range(3), ["nulls", "negative_rows", "inf_rows"], rotation=25, ha="right")
    ax1.set_yticks(range(len(data)), data["field"])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax1.text(j, i, f"{int(matrix[i, j]):,}", ha="center", va="center", fontsize=7)

    ranges = data[["field", "min", "max"]].head(16)
    ax2.axis("off")
    table = ax2.table(cellText=ranges.astype(str).values, colLabels=ranges.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.18)
    ax2.set_title("Value ranges for inspected numeric fields")
    fig.text(
        0.01,
        0.01,
        "Read: the dominant blocker is not null/negative/inf numeric sanity; it is scope/history plus short_volume duplicate keys.",
        fontsize=8,
    )
    _savefig(
        "short_review_numeric_sanity_panel_v0_1.png",
        manifest_rows,
        category="good_scoped",
        evidence_sources="short_review_numeric_sanity_v0_1.csv; short_review_null_profile_v0_1.csv",
        what_it_shows="Null, negative and infinite counts plus representative numeric ranges.",
        inspector_question="Is numeric sanity the primary blocker?",
        interpretation="No. Numeric sanity is clean in inspected fields; duplicate keys and source scope are the governing flags.",
        status="scoped",
    )


def _provenance_history_boundary_panel(
    scope: pd.DataFrame,
    provenance: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    scope_view = scope[["topic", "status", "scope"]].copy()
    prov = provenance[["path", "exists", "bytes"]].copy()
    prov["asset"] = prov["path"].astype(str).str.replace("\\", "/", regex=False).str.split("/").str[-1]
    prov_view = prov[["asset", "exists", "bytes"]]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 7), gridspec_kw={"height_ratios": [1.1, 1]})
    ax1.axis("off")
    t1 = ax1.table(cellText=scope_view.astype(str).values, colLabels=scope_view.columns, loc="center", cellLoc="left")
    t1.auto_set_font_size(False)
    t1.set_fontsize(7)
    t1.scale(1, 1.28)
    ax1.set_title("Scope and history boundaries")

    ax2.axis("off")
    t2 = ax2.table(cellText=prov_view.astype(str).values, colLabels=prov_view.columns, loc="center", cellLoc="left")
    t2.auto_set_font_size(False)
    t2.set_fontsize(7)
    t2.scale(1, 1.18)
    ax2.set_title("Provenance assets present")
    fig.text(
        0.01,
        0.01,
        "Read: provenance is strong, but official/free sources do not prove full-history replacement. Preserve source/date-window boundaries.",
        fontsize=8,
    )
    _savefig(
        "short_review_provenance_history_boundary_panel_v0_1.png",
        manifest_rows,
        category="scope_boundary",
        evidence_sources="short_review_scope_limitations_v0_1.csv; short_review_provenance_assets_v0_1.csv",
        what_it_shows="Scope/history limitations and present provenance assets.",
        inspector_question="What claims are explicitly blocked by source/history boundaries?",
        interpretation="Full-history replacement and consolidated short truth claims are blocked; baseline/provenance claims are supported.",
        status="boundary",
    )


def build() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    profile = pd.read_csv(EVIDENCE_ROOT / "short_review_aggregate_profile_v0_1.csv")
    dup_by_ticker = pd.read_csv(EVIDENCE_ROOT / "short_review_short_volume_duplicate_key_by_ticker_v0_1.csv")
    comparison = pd.read_csv(EVIDENCE_ROOT / "short_review_local_comparison_summary_v0_1.csv")
    numeric = pd.read_csv(EVIDENCE_ROOT / "short_review_numeric_sanity_v0_1.csv")
    nulls = pd.read_csv(EVIDENCE_ROOT / "short_review_null_profile_v0_1.csv")
    scope = pd.read_csv(EVIDENCE_ROOT / "short_review_scope_limitations_v0_1.csv")
    provenance = pd.read_csv(EVIDENCE_ROOT / "short_review_provenance_assets_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _coverage_timeline(profile, manifest_rows)
    _duplicate_key_concentration(dup_by_ticker, manifest_rows)
    _duplicate_key_case_panel(manifest_rows)
    _finra_vs_local_overlap(comparison, manifest_rows)
    _numeric_sanity_panel(numeric, nulls, manifest_rows)
    _provenance_history_boundary_panel(scope, provenance, manifest_rows)
    _write_manifest(manifest_rows)

    print(f"created {len(manifest_rows)} short_review visual assets")
    for row in manifest_rows:
        print(f"{row['image_path']} {row['bytes']} bytes")


if __name__ == "__main__":
    build()
