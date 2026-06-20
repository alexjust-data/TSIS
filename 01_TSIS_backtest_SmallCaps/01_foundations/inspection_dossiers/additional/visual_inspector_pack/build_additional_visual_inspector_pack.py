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
    case_path = PACK_ROOT / "additional_visual_case_manifest_v0_1.csv"
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

    audit_path = PACK_ROOT / "additional_visual_asset_audit_v0_1.csv"
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


def _subfamily_coverage_heatmap(quality: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = quality.copy()
    data["coverage_non_empty_pct"] = pd.to_numeric(data["coverage_non_empty_pct"], errors="coerce")
    data["files_present"] = pd.to_numeric(data["files_present"], errors="coerce")
    data["files_non_empty"] = pd.to_numeric(data["files_non_empty"], errors="coerce")
    data["rows_total"] = pd.to_numeric(data["rows_total"], errors="coerce")
    data["coverage_fill"] = data["coverage_non_empty_pct"].fillna(100.0)
    data["rows_scaled"] = data["rows_total"] / data["rows_total"].max()
    data["files_scaled"] = data["files_present"].fillna(0) / max(1, data["files_present"].fillna(0).max())
    matrix = data[["coverage_fill", "rows_scaled", "files_scaled"]].copy()
    matrix["coverage_fill"] = matrix["coverage_fill"] / 100.0

    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    cmap = LinearSegmentedColormap.from_list("additional", ["#f4f1e8", "#d6bd7b", "#2f7d4f"])
    image = ax.imshow(matrix.to_numpy(), aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_title("Additional is heterogeneous: coverage and rows differ by subfamily")
    ax.set_xticks(range(3), ["non-empty coverage", "rows scaled", "files scaled"], rotation=25, ha="right")
    ax.set_yticks(range(len(data)), data["dataset"])
    for i, row in data.iterrows():
        cov = row["coverage_non_empty_pct"]
        text = "macro" if pd.isna(cov) else f"{cov:.1f}%"
        ax.text(0, i, text, ha="center", va="center", fontsize=7)
        ax.text(1, i, f"{int(row['rows_total']):,}", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, label="scaled value")
    fig.text(
        0.01,
        0.01,
        "Read: Additional cannot be evaluated as one flat dataset; each subfamily has its own role, coverage and restriction.",
        fontsize=8,
    )
    _savefig(
        "additional_subfamily_coverage_heatmap_v0_1.png",
        manifest_rows,
        category="population_coverage",
        evidence_sources="quality_tables/additional_subfamily_quality_table_v0_2.csv",
        what_it_shows="Coverage, row mass and file mass by additional subfamily.",
        inspector_question="Can Additional be treated as a homogeneous dataset?",
        interpretation="No. Quality and allowed uses are subfamily-specific.",
        status="scoped",
    )


def _financial_context_readiness(quality: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = quality[quality["dataset_family"].isin(["financials_core", "financials_ratios"])].copy()
    data["coverage_non_empty_pct"] = pd.to_numeric(data["coverage_non_empty_pct"], errors="coerce")
    data["rows_total"] = pd.to_numeric(data["rows_total"], errors="coerce")
    colors = ["#2f7d4f" if "good" in state else "#cf8d2e" for state in data["quality_state"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.05, 1.25]})
    ax1.bar(data["dataset"], data["coverage_non_empty_pct"], color=colors)
    ax1.set_title("Financial context readiness")
    ax1.set_ylabel("non-empty coverage %")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    for index, row in data.iterrows():
        ax1.text(index, row["coverage_non_empty_pct"] + 2, f"{row['coverage_non_empty_pct']:.1f}%", ha="center", fontsize=8)

    ax2.axis("off")
    table_source = data[["dataset", "quality_state", "rows_total", "forbidden_interpretation"]]
    table = ax2.table(cellText=table_source.astype(str).values, colLabels=table_source.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.15)
    ax2.set_title("Required interpretation")
    fig.text(
        0.01,
        0.01,
        "Read: financial core is good context with PIT filing guardrails; ratios remain sparse review context.",
        fontsize=8,
    )
    _savefig(
        "additional_financial_context_readiness_panel_v0_1.png",
        manifest_rows,
        category="good_and_review",
        evidence_sources="quality_tables/additional_subfamily_quality_table_v0_2.csv; good_justification/additional_financials_core_good_cases_v0_1.md",
        what_it_shows="Financial statement and ratio readiness with forbidden interpretations.",
        inspector_question="Which financial Additional subfamilies are context-ready?",
        interpretation="Statements are strong context candidates with PIT guardrails; ratios are sparse review snapshots.",
        status="scoped",
    )


def _news_attribution_risk(news: pd.DataFrame, examples: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.2), gridspec_kw={"height_ratios": [1, 1.05]})
    colors = ["#9b2f2f" if "ambiguous" in bucket else "#cf8d2e" if "context" in bucket else "#2f7d4f" for bucket in news["news_link_bucket"]]
    ax1.bar(news["news_link_bucket"], news["events"], color=colors)
    ax1.set_title("News attribution is useful but attribution-sensitive")
    ax1.set_ylabel("events")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    ax1.set_ylim(0, max(news["events"]) * 1.18)
    for index, row in news.iterrows():
        ax1.text(index, row["events"] * 1.03, f"{int(row['events']):,}\nmean tickers/news {row['mean_tickers_per_news']:.1f}", ha="center", fontsize=7)

    ax2.axis("off")
    table_source = examples[["ticker", "rows", "mean_tickers_per_news", "max_tickers_per_news"]].head(8)
    table = ax2.table(cellText=table_source.astype(str).values, colLabels=table_source.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.2)
    ax2.set_title("Multi-ticker attribution examples")
    fig.text(
        0.01,
        0.01,
        "Read: requested ticker is not enough to claim ticker-level causal subject when articles mention many tickers.",
        fontsize=8,
    )
    _savefig(
        "additional_news_attribution_risk_panel_v0_1.png",
        manifest_rows,
        category="flagged_review",
        evidence_sources="news_attribution/additional_news_attribution_quality_v0_1.csv; news_attribution/additional_news_multi_ticker_examples_v0_1.csv",
        what_it_shows="News buckets, event mass, mean tickers per news item and concrete multi-ticker examples.",
        inspector_question="Can news be consumed as direct ticker causality?",
        interpretation="No. It is context/event evidence requiring attribution guardrails.",
        status="review",
    )


def _corporate_actions_overlap(recon: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = recon.copy()
    pivot = data.pivot_table(index="dataset", columns="overlap_bucket", values="tickers", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(9.5, 5))
    bottom = None
    colors = {"reference_exact_overlap": "#2f7d4f", "reference_present_no_exact_overlap": "#cf8d2e"}
    for column in pivot.columns:
        ax.bar(pivot.index, pivot[column], bottom=bottom, label=column, color=colors.get(column, "#6a7f95"))
        bottom = pivot[column] if bottom is None else bottom + pivot[column]
    ax.set_title("Additional corporate actions are secondary to reference")
    ax.set_ylabel("tickers")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8)
    for index, dataset in enumerate(pivot.index):
        total = int(pivot.loc[dataset].sum())
        ax.text(index, total + max(pivot.sum(axis=1)) * 0.03, f"{total:,}", ha="center")
    fig.text(
        0.01,
        0.01,
        "Read: overlap can confirm reference, but Additional does not override primary corporate-action authority.",
        fontsize=8,
    )
    _savefig(
        "additional_corporate_actions_reference_overlap_panel_v0_1.png",
        manifest_rows,
        category="reference_reconciliation",
        evidence_sources="reference_reconciliation/additional_corporate_actions_reference_reconciliation_v0_1.csv",
        what_it_shows="Corporate-action overlap buckets against reference.",
        inspector_question="Can Additional corporate actions override reference?",
        interpretation="No. They are secondary reconciliation and review evidence.",
        status="review",
    )


def _macro_context_scope(quality: pd.DataFrame, readiness: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    macro = quality[quality["dataset_family"] == "economic"].copy()
    macro["rows_total"] = pd.to_numeric(macro["rows_total"], errors="coerce")
    calendar = readiness[readiness["target_table"] == "calendar_table"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})
    ax1.bar(macro["dataset"], macro["rows_total"], color="#6d8f57")
    ax1.set_title("Economic data is macro calendar context")
    ax1.set_ylabel("rows")
    ax1.tick_params(axis="x", rotation=20)
    ax1.grid(axis="y", alpha=0.25)
    for index, row in macro.iterrows():
        ax1.text(index, row["rows_total"] * 1.03, f"{int(row['rows_total']):,}", ha="center", fontsize=8)

    ax2.axis("off")
    table_source = calendar[["target_table", "additional_role", "readiness", "blocking_limit"]]
    table = ax2.table(cellText=table_source.astype(str).values, colLabels=table_source.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.35)
    ax2.set_title("Calendar-table scope")
    fig.text(
        0.01,
        0.01,
        "Read: macro series can support calendar context; they do not imply ticker-level causality.",
        fontsize=8,
    )
    _savefig(
        "additional_macro_context_scope_panel_v0_1.png",
        manifest_rows,
        category="good_scoped",
        evidence_sources="quality_tables/additional_subfamily_quality_table_v0_2.csv; quality_tables/additional_master_table_readiness_v0_1.csv",
        what_it_shows="Economic rows and calendar-table readiness/limits.",
        inspector_question="Can macro Additional data be read as ticker-level signal?",
        interpretation="No. It is calendar/macro context only.",
        status="scoped",
    )


def _consumption_boundary(readiness: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = readiness.copy()
    short_label = {
        "ready_for_contextual_quality_columns": "quality context",
        "partial_context_ready": "partial context",
        "indirect_context_only": "indirect only",
        "secondary_reconciliation_only": "secondary only",
        "macro_context_ready": "macro context",
    }
    score = {
        "ready_for_contextual_quality_columns": 2,
        "macro_context_ready": 2,
        "partial_context_ready": 1,
        "indirect_context_only": 1,
        "secondary_reconciliation_only": 1,
    }
    data["score"] = data["readiness"].map(score).fillna(0)
    fig, ax = plt.subplots(figsize=(11, 5.8))
    cmap = LinearSegmentedColormap.from_list("readiness", ["#9b2f2f", "#cf8d2e", "#2f7d4f"])
    matrix = data[["score"]].to_numpy()
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_title("Additional consumption boundary: context only, no silent promotion")
    ax.set_xticks([0], ["readiness"])
    ax.set_yticks(range(len(data)), data["target_table"])
    for index, row in data.iterrows():
        ax.text(0, index, short_label.get(row["readiness"], row["readiness"]), ha="center", va="center", fontsize=8)
        ax.text(0.65, index, row["blocking_limit"], va="center", fontsize=8)
    ax.set_xlim(-0.5, 5.8)
    ax.set_frame_on(False)
    fig.text(
        0.01,
        0.01,
        "Read: Additional can enrich quality/master tables as context, but does not certify market data or promote alpha features by itself.",
        fontsize=8,
    )
    _savefig(
        "additional_consumption_boundary_panel_v0_1.png",
        manifest_rows,
        category="consumption_policy",
        evidence_sources="quality_tables/additional_master_table_readiness_v0_1.csv",
        what_it_shows="Target-table readiness states and blocking limits.",
        inspector_question="What can Additional safely feed?",
        interpretation="Contextual quality/master-table columns only, with subfamily-specific restrictions.",
        status="policy",
    )


def build() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    quality = pd.read_csv(EVIDENCE_ROOT / "quality_tables" / "additional_subfamily_quality_table_v0_2.csv")
    readiness = pd.read_csv(EVIDENCE_ROOT / "quality_tables" / "additional_master_table_readiness_v0_1.csv")
    news = pd.read_csv(EVIDENCE_ROOT / "news_attribution" / "additional_news_attribution_quality_v0_1.csv")
    news_examples = pd.read_csv(EVIDENCE_ROOT / "news_attribution" / "additional_news_multi_ticker_examples_v0_1.csv")
    recon = pd.read_csv(EVIDENCE_ROOT / "reference_reconciliation" / "additional_corporate_actions_reference_reconciliation_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _subfamily_coverage_heatmap(quality, manifest_rows)
    _financial_context_readiness(quality, manifest_rows)
    _news_attribution_risk(news, news_examples, manifest_rows)
    _corporate_actions_overlap(recon, manifest_rows)
    _macro_context_scope(quality, readiness, manifest_rows)
    _consumption_boundary(readiness, manifest_rows)
    _write_manifest(manifest_rows)

    print(f"created {len(manifest_rows)} additional visual assets")
    for row in manifest_rows:
        print(f"{row['image_path']} {row['bytes']} bytes")


if __name__ == "__main__":
    build()
