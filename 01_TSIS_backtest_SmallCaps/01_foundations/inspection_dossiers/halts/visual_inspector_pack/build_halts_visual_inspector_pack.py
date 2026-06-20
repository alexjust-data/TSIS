from __future__ import annotations

import csv
import shutil
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
POPULATION_ROOT = EVIDENCE_ROOT / "population_summary"
SOURCE_VISUAL_ROOT = EVIDENCE_ROOT / "population_visual_overview"


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


def _copy_existing_visual(
    source_name: str,
    manifest_rows: list[dict[str, str]],
    **row: str,
) -> None:
    source_path = SOURCE_VISUAL_ROOT / source_name
    target_path = IMAGE_ROOT / source_name
    shutil.copy2(source_path, target_path)
    manifest_rows.append(
        {
            "visual_id": target_path.stem,
            "image_path": f"images/{target_path.name}",
            "category": row["category"],
            "evidence_sources": row["evidence_sources"],
            "what_it_shows": row["what_it_shows"],
            "inspector_question": row["inspector_question"],
            "interpretation": row["interpretation"],
            "status": row["status"],
            "bytes": str(target_path.stat().st_size),
        }
    )


def _write_manifest(manifest_rows: list[dict[str, str]]) -> None:
    case_path = PACK_ROOT / "halts_visual_case_manifest_v0_1.csv"
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

    audit_path = PACK_ROOT / "halts_visual_asset_audit_v0_1.csv"
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


def _source_completeness_panel(source_quality: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = source_quality.copy()
    completeness_cols = [
        "ticker_nonnull_rows",
        "halt_date_nonnull_rows",
        "halt_start_nonnull_rows",
        "resume_trade_nonnull_rows",
        "issuer_name_nonnull_rows",
    ]
    matrix = np.vstack([(data[col] / data["rows"] * 100).to_numpy(dtype=float) for col in completeness_cols]).T
    labels = ["ticker", "halt date", "halt start", "resume trade", "issuer name"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    ax1.bar(data["source"], data["rows"], color=["#2c5c8a", "#6d8f57", "#8b5a2b"])
    ax1.set_title("Official source row mass")
    ax1.set_ylabel("rows")
    ax1.grid(axis="y", alpha=0.25)
    for index, row in data.iterrows():
        ax1.text(index, row["rows"] * 1.03, f"{int(row['rows']):,}", ha="center", fontsize=8)

    cmap = LinearSegmentedColormap.from_list("halts_quality", ["#9b2f2f", "#cf8d2e", "#f7faf8", "#6d8f57", "#2f7d4f"])
    image = ax2.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax2.set_title("Key field completeness by source")
    ax2.set_xticks(range(len(labels)), labels, rotation=25, ha="right")
    ax2.set_yticks(range(len(data)), data["source"])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax2.text(j, i, f"{matrix[i, j]:.1f}%", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax2, label="nonnull rows / rows")
    fig.text(
        0.01,
        0.01,
        "Read: Nasdaq/NYSE provide intraday halt timing; SEC is regulatory context and lacks halt-start/resume timing.",
        fontsize=8,
    )
    _savefig(
        "halts_source_completeness_panel_v0_1.png",
        manifest_rows,
        category="source_quality",
        evidence_sources="halts_source_quality_summary_v0_1.csv",
        what_it_shows="Rows and key-field completeness by official halt source.",
        inspector_question="Which halt sources support intraday event timing?",
        interpretation="Nasdaq/NYSE support intraday timing; SEC is date/context-level regulatory evidence.",
        status="usable_with_source_semantics",
    )


def _taxonomy_scope_panel(
    canonical: pd.DataFrame,
    lt1b: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    canon = canonical.sort_values("events", ascending=True)
    small = lt1b.sort_values("events", ascending=True)
    colors = {
        "good_full_intraday_event": "#2f7d4f",
        "good_date_level_event": "#6d8f57",
        "review_partial_identity": "#cf8d2e",
        "regulatory_context_only": "#8b5a2b",
        "bad_unusable_event": "#9b2f2f",
    }
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.35, 1]})
    ax1.barh(canon["event_taxonomy"], canon["events"], color=[colors.get(x, "#777777") for x in canon["event_taxonomy"]])
    ax1.set_title("Canonical halt event taxonomy")
    ax1.set_xlabel("events")
    ax1.grid(axis="x", alpha=0.25)
    for index, row in canon.reset_index(drop=True).iterrows():
        ax1.text(row["events"] * 1.01, index, f"{int(row['events']):,}", va="center", fontsize=8)

    ax2.barh(small["event_taxonomy"], small["events"], color=[colors.get(x, "#777777") for x in small["event_taxonomy"]])
    ax2.set_title("LT1B halt taxonomy")
    ax2.set_xlabel("events")
    ax2.grid(axis="x", alpha=0.25)
    for index, row in small.reset_index(drop=True).iterrows():
        ax2.text(row["events"] * 1.01, index, f"{int(row['events']):,}", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: full-intraday events dominate both the canonical halt layer and the LT1B subset; bad residual mass is marginal.",
        fontsize=8,
    )
    _savefig(
        "halts_event_taxonomy_scope_panel_v0_1.png",
        manifest_rows,
        category="population_taxonomy",
        evidence_sources="halts_event_taxonomy_summary_v0_1.csv; halts_lt1b_event_taxonomy_summary_v0_1.csv",
        what_it_shows="Canonical and LT1B halt event taxonomy distributions.",
        inspector_question="Does the event layer remain structurally usable in the project universe?",
        interpretation="Yes, with explicit separation between intraday, date-level, review and regulatory-context buckets.",
        status="usable_for_declared_scope",
    )


def _universe_coverage_panel(coverage: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    values = coverage.set_index("metric")["value"].astype(int)
    with_data = int(values["tickers_with_halt_data"])
    without_data = int(values["tickers_without_halt_data"])
    events = int(values["halt_events_total_for_universe"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.6), gridspec_kw={"width_ratios": [1, 1]})
    ax1.bar(["with halt event", "without halt event"], [with_data, without_data], color=["#2f7d4f", "#9aa4aa"])
    ax1.set_title("LT1B ticker relation to halt events")
    ax1.set_ylabel("tickers")
    ax1.grid(axis="y", alpha=0.25)
    for index, value in enumerate([with_data, without_data]):
        ax1.text(index, value * 1.03, f"{value:,}", ha="center", fontsize=8)

    ax2.axis("off")
    rows = [
        ["universe tickers", f"{int(values['universe_tickers']):,}"],
        ["tickers with halt data", f"{with_data:,}"],
        ["tickers without halt data", f"{without_data:,}"],
        ["LT1B halt events", f"{events:,}"],
        ["coverage reading", "absence is not missing data"],
    ]
    table = ax2.table(cellText=rows, colLabels=["metric", "value"], loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.25)
    ax2.set_title("Coverage interpretation")
    fig.text(
        0.01,
        0.01,
        "Read: halts coverage is event-to-universe relation, not daily panel completeness.",
        fontsize=8,
    )
    _savefig(
        "halts_lt1b_universe_coverage_panel_v0_1.png",
        manifest_rows,
        category="coverage_scope",
        evidence_sources="halts_coverage_summary_v0_1.csv",
        what_it_shows="LT1B tickers with and without matched halt events plus total matched halt events.",
        inspector_question="Does absence of a halt row imply missing data?",
        interpretation="No. Absence means no matched official event in the governed halt layer.",
        status="coverage_context",
    )


def _multisource_reconciliation_panel(reconciliation: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = reconciliation.copy()
    x = np.arange(len(data))
    width = 0.35
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.bar(x - width / 2, data["rows_pre_concat"], width=width, color="#2c5c8a", label="rows pre concat")
    ax.bar(x + width / 2, data["rows_post_builder_dedup"], width=width, color="#6d8f57", label="rows post builder dedup")
    ax.plot(x, data["dedup_delta"], marker="o", color="#9b2f2f", label="dedup delta")
    ax.set_xticks(x, data["scope"], rotation=20, ha="right")
    ax.set_title("Multisource reconciliation and deduplication")
    ax.set_ylabel("rows")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    for index, row in data.iterrows():
        if int(row["dedup_delta"]) > 0:
            ax.text(index, row["rows_pre_concat"] * 1.02, f"delta {int(row['dedup_delta']):,}", ha="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: the dedup delta is concentrated in Nasdaq; persisted multisource output has zero duplicate delta in this summary.",
        fontsize=8,
    )
    _savefig(
        "halts_multisource_reconciliation_panel_v0_1.png",
        manifest_rows,
        category="reconciliation",
        evidence_sources="halts_multisource_reconciliation_v0_1.csv",
        what_it_shows="Rows before concat, rows after builder dedup and dedup delta by source/scope.",
        inspector_question="Where does multisource reconciliation change row counts?",
        interpretation="The material dedup change is Nasdaq/all-source concat; this is governed and version-sensitive.",
        status="usable_with_versioning",
    )


def _casepack_boundary_panel(
    visual_buckets: pd.DataFrame,
    case_manifest: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    buckets = visual_buckets.sort_values("visual_rows", ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.8), gridspec_kw={"width_ratios": [1.25, 1]})
    color_map = {
        "confirmed_halt_microstructure_coherent": "#2f7d4f",
        "halt_with_trades_signal_only": "#2c5c8a",
        "halt_with_quotes_signal_only": "#6d8f57",
        "halt_present_but_market_clean": "#cf8d2e",
        "market_signal_without_clear_halt_window": "#8b5a2b",
    }
    ax1.barh(buckets["visual_case_bucket"], buckets["visual_rows"], color=[color_map.get(x, "#777777") for x in buckets["visual_case_bucket"]])
    ax1.set_title("Visual overlay bucket distribution")
    ax1.set_xlabel("rows")
    ax1.grid(axis="x", alpha=0.25)
    for index, row in buckets.reset_index(drop=True).iterrows():
        ax1.text(row["visual_rows"] * 1.01, index, f"{int(row['visual_rows']):,}", va="center", fontsize=8)

    ax2.axis("off")
    table_data = case_manifest[["status", "casepack"]].copy()
    table_data["casepack"] = table_data["casepack"].str.replace("_v0_1.md", "", regex=False)
    table = ax2.table(cellText=table_data.values, colLabels=table_data.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1.0, 1.25)
    ax2.set_title("Casepack coverage")
    fig.text(
        0.01,
        0.01,
        "Read: coherent overlays dominate, but asymmetric/no-clear-window cases remain review context, not automatic bad events.",
        fontsize=8,
    )
    _savefig(
        "halts_visual_casepack_boundary_panel_v0_1.png",
        manifest_rows,
        category="good_review_bad_boundary",
        evidence_sources="halts_visual_bucket_summary_v0_1.csv; halts_case_manifest_v0_1.csv",
        what_it_shows="Visual overlay bucket distribution plus good/review/bad/causal/coverage casepack inventory.",
        inspector_question="Does the visual evidence distinguish coherent, review and residual halt cases?",
        interpretation="Yes. Coherent cases dominate, and residual/review cases have explicit casepack boundaries.",
        status="human_inspector_ready",
    )


def _copy_population_visuals(manifest_rows: list[dict[str, str]]) -> None:
    visuals = [
        (
            "01_source_quality_rows.png",
            "source_quality_historical",
            "Existing population overview for row mass and source quality.",
            "Which source dominates the halt master?",
            "Nasdaq dominates row mass; NYSE and SEC have distinct source semantics.",
            "usable_with_source_semantics",
        ),
        (
            "02_canonical_event_taxonomy.png",
            "taxonomy_historical",
            "Existing population overview for canonical halt taxonomy.",
            "What is the overall canonical event distribution?",
            "Full-intraday events dominate; hard bad residual is marginal.",
            "usable_for_declared_scope",
        ),
        (
            "03_lt1b_event_taxonomy.png",
            "taxonomy_historical",
            "Existing population overview for LT1B halt taxonomy.",
            "Does the taxonomy remain strong inside the LT1B universe?",
            "The LT1B subset remains dominated by full-intraday events.",
            "usable_for_declared_scope",
        ),
        (
            "04_visual_case_bucket_distribution.png",
            "visual_overlay_historical",
            "Existing population overview for halt/quotes/trades overlay buckets.",
            "What visual overlay buckets exist in historical evidence?",
            "Coherent microstructure overlays dominate; asymmetric buckets are review.",
            "human_inspector_ready",
        ),
        (
            "05_top_tickers_by_halt_events.png",
            "coverage_historical",
            "Existing population overview for concentration by ticker.",
            "Is halt activity concentrated by ticker?",
            "Yes; sampling and casepacks must account for concentration.",
            "coverage_context",
        ),
    ]
    for name, category, shows, question, interpretation, status in visuals:
        _copy_existing_visual(
            name,
            manifest_rows,
            category=category,
            evidence_sources="evidence_assets/population_visual_overview/",
            what_it_shows=shows,
            inspector_question=question,
            interpretation=interpretation,
            status=status,
        )


def main() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    source_quality = pd.read_csv(POPULATION_ROOT / "halts_source_quality_summary_v0_1.csv")
    canonical = pd.read_csv(POPULATION_ROOT / "halts_event_taxonomy_summary_v0_1.csv")
    lt1b = pd.read_csv(POPULATION_ROOT / "halts_lt1b_event_taxonomy_summary_v0_1.csv")
    reconciliation = pd.read_csv(POPULATION_ROOT / "halts_multisource_reconciliation_v0_1.csv")
    coverage = pd.read_csv(POPULATION_ROOT / "halts_coverage_summary_v0_1.csv")
    visual_buckets = pd.read_csv(POPULATION_ROOT / "halts_visual_bucket_summary_v0_1.csv")
    case_manifest = pd.read_csv(EVIDENCE_ROOT / "case_manifest" / "halts_case_manifest_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _source_completeness_panel(source_quality, manifest_rows)
    _taxonomy_scope_panel(canonical, lt1b, manifest_rows)
    _universe_coverage_panel(coverage, manifest_rows)
    _multisource_reconciliation_panel(reconciliation, manifest_rows)
    _casepack_boundary_panel(visual_buckets, case_manifest, manifest_rows)
    _copy_population_visuals(manifest_rows)
    _write_manifest(manifest_rows)


if __name__ == "__main__":
    main()
