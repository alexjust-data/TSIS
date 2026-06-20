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
    case_path = PACK_ROOT / "reference_visual_case_manifest_v0_1.csv"
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

    audit_path = PACK_ROOT / "reference_visual_asset_audit_v0_1.csv"
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


def _identity_quality_panel(population: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    identity = population[population["family"] == "identity"].copy()
    overview = population[population["family"] == "overview_404"].copy()
    order = [
        "good_identity_snapshot",
        "review_transient_symbol",
        "bad_unresolved_identity",
    ]
    identity["bucket"] = pd.Categorical(identity["bucket"], categories=order, ordered=True)
    identity = identity.sort_values("bucket")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.1, 1]})
    colors = ["#2f7d4f", "#cf8d2e", "#9b2f2f"]
    ax1.bar(identity["bucket"].astype(str), identity["rows"], color=colors)
    ax1.set_title("Identity quality distribution")
    ax1.set_ylabel("tickers / rows")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    for index, row in identity.reset_index(drop=True).iterrows():
        ax1.text(index, row["rows"] * 1.03, f"{int(row['rows']):,}", ha="center", fontsize=8)

    ax2.bar(overview["bucket"], overview["rows"], color="#8b5a2b")
    ax2.set_title("Overview 404 residual classification")
    ax2.set_ylabel("rows")
    ax2.tick_params(axis="x", rotation=25)
    ax2.grid(axis="y", alpha=0.25)
    for index, row in overview.reset_index(drop=True).iterrows():
        ax2.text(index, row["rows"] * 1.05, f"{int(row['rows']):,}", ha="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: identity is mostly resolved, but review and bad residual identity must remain visible to consumers.",
        fontsize=8,
    )
    _savefig(
        "reference_identity_quality_panel_v0_1.png",
        manifest_rows,
        category="identity_quality",
        evidence_sources="reference_population_summary_v0_1.csv",
        what_it_shows="Good, review and bad identity buckets plus overview 404 residual classification.",
        inspector_question="Is the identity layer mostly usable while preserving unresolved identity debt?",
        interpretation="Yes. Good identity dominates, but review and bad identity residuals are explicit.",
        status="usable_with_identity_flags",
    )


def _endpoint_status_panel(endpoints: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = endpoints.copy()
    metrics = ["ok_pct", "error_pct", "http_404_pct"]
    labels = ["ok", "error", "http 404"]
    matrix = data.set_index("dataset")[metrics].to_numpy(dtype=float)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw={"width_ratios": [1.35, 1]})
    colors = ["#2f7d4f", "#9b2f2f", "#cf8d2e"]
    x = np.arange(len(data))
    width = 0.24
    for offset, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
        ax1.bar(x + (offset - 1) * width, data[metric], width=width, label=label, color=color)
    ax1.set_title("Download endpoint status percentages")
    ax1.set_ylabel("percent")
    ax1.set_xticks(x, data["dataset"], rotation=25, ha="right")
    ax1.set_ylim(0, 105)
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.25)

    cmap = LinearSegmentedColormap.from_list("reference_endpoints", ["#f7faf8", "#dcecec", "#8fb9c8", "#2b6174"])
    image = ax2.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax2.set_title("Endpoint status heatmap")
    ax2.set_xticks(range(len(labels)), labels)
    ax2.set_yticks(range(len(data)), data["dataset"])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax2.text(j, i, f"{matrix[i, j]:.1f}%", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=ax2, label="percent")
    fig.text(
        0.01,
        0.01,
        "Read: events 404s are mostly no-event semantics, while overview 404s map to unresolved identity debt.",
        fontsize=8,
    )
    _savefig(
        "reference_download_endpoint_status_panel_v0_1.png",
        manifest_rows,
        category="endpoint_quality",
        evidence_sources="reference_download_endpoint_summary_v0_1.csv",
        what_it_shows="OK/error/http-404 percentages and endpoint status shape by reference subfamily.",
        inspector_question="Which endpoints have true residual risk versus expected operational semantics?",
        interpretation="Overview errors are identity residual; events 404s should not be read as corruption by default.",
        status="usable_with_endpoint_semantics",
    )


def _payload_family_panel(population: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    payload = population[population["family"].isin(["events", "splits", "dividends"])].copy()
    payload["label"] = payload["family"] + "\n" + payload["bucket"].str.replace("_", " ")
    payload = payload.sort_values("rows", ascending=True)
    colors = payload["bucket"].map(
        lambda value: "#2f7d4f" if str(value).startswith("good") or "ok_event" in str(value) else "#cf8d2e"
    )
    fig, ax = plt.subplots(figsize=(11, 6.0))
    ax.barh(payload["label"], payload["rows"], color=colors)
    ax.set_xscale("log")
    ax.set_title("Reference payload families mix real events and no-payload placeholders")
    ax.set_xlabel("rows, log scale")
    ax.grid(axis="x", alpha=0.25)
    for index, row in payload.reset_index(drop=True).iterrows():
        ax.text(row["rows"] * 1.08, index, f"{int(row['rows']):,}", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: dividends are large and real, splits are real but sparse, and events are mainly ticker-change plus empty/no-event payloads.",
        fontsize=8,
    )
    _savefig(
        "reference_payload_family_panel_v0_1.png",
        manifest_rows,
        category="payload_semantics",
        evidence_sources="reference_population_summary_v0_1.csv",
        what_it_shows="Events, splits and dividends payload buckets on a log-scale count panel.",
        inspector_question="Which reference payload families carry real consumable events?",
        interpretation="Dividends and splits have real payloads; no-payload placeholders and ticker-change semantics must stay explicit.",
        status="usable_with_payload_flags",
    )


def _causal_alignment_panel(population: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    causal = population[population["family"].str.startswith("causal:")].copy()
    causal["family_short"] = causal["family"].str.replace("causal:", "", regex=False)
    causal["label"] = causal["family_short"] + "\n" + causal["bucket"].str.replace("_", " ")
    causal = causal.sort_values("rows", ascending=True)
    colors = causal["bucket"].map(
        lambda value: "#2f7d4f" if "explains" in str(value) or "near_halt" in str(value) else "#cf8d2e"
    )
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    ax.barh(causal["label"], causal["rows"], color=colors)
    ax.set_title("Reference causal overlays are useful but not uniformly decisive")
    ax.set_xlabel("rows")
    ax.grid(axis="x", alpha=0.25)
    for index, row in causal.reset_index(drop=True).iterrows():
        ax.text(row["rows"] + max(causal["rows"].max() * 0.01, 2), index, f"{int(row['rows']):,}", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: events->halts and splits->trades carry strong causal value; quotes/daily/1m alignments retain review boundaries.",
        fontsize=8,
    )
    _savefig(
        "reference_causal_alignment_panel_v0_1.png",
        manifest_rows,
        category="causal_overlay",
        evidence_sources="reference_population_summary_v0_1.csv",
        what_it_shows="Causal overlay buckets against halts, quotes, trades, daily and 1m evidence.",
        inspector_question="Where does reference explain downstream anomalies versus only flag review context?",
        interpretation="Strongest evidence is events->halts and splits->trades; other overlays remain review scoped.",
        status="usable_with_causal_boundaries",
    )


def _listing_presence_boundary_panel(
    listing: pd.DataFrame,
    case_manifest: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    values = listing.set_index("metric")["value"].astype(int)
    decisions = pd.DataFrame(
        [
            ("corporate_actions_table", "allowed"),
            ("price_view_builders", "allowed"),
            ("universe support", "allowed with policy"),
            ("event overlays", "allowed"),
            ("backtest_core", "restricted"),
            ("ML/RL/live", "not enabled"),
            ("all_tickers as final universe", "not enabled"),
            ("ticker_change as trading signal", "not enabled"),
        ],
        columns=["consumer", "decision"],
    )
    score = {"allowed": 2, "allowed with policy": 1.5, "restricted": 1, "not enabled": 0}
    color = {"allowed": "#2f7d4f", "allowed with policy": "#6d8f57", "restricted": "#cf8d2e", "not enabled": "#9b2f2f"}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.8), gridspec_kw={"width_ratios": [1, 1.25]})
    ax1.axis("off")
    rows = [
        ["all_tickers observed tickers", f"{int(values['listing_snapshot_summary_rows']):,}"],
        ["all_tickers snapshot rows", f"{int(values['listing_snapshot_rows_total']):,}"],
        ["LT1B tickers", f"{int(values['listing_tickers_lt1b']):,}"],
        ["casepacks", f"{len(case_manifest):,}"],
        ["boundary", "presence support, not final universe"],
    ]
    table = ax1.table(cellText=rows, colLabels=["metric", "value"], loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.25)
    ax1.set_title("Listing/presence evidence")

    ax2.barh(decisions["consumer"], decisions["decision"].map(score), color=decisions["decision"].map(color))
    ax2.invert_yaxis()
    ax2.set_xlim(0, 2.35)
    ax2.set_title("Consumer boundary")
    ax2.set_xticks([0, 1, 1.5, 2], ["not enabled", "restricted", "policy", "allowed"])
    ax2.grid(axis="x", alpha=0.25)
    for index, row in decisions.iterrows():
        ax2.text(score[row["decision"]] + 0.05, index, row["decision"], va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: all_tickers supports temporal presence, but it is not a final PTI universe or trading signal.",
        fontsize=8,
    )
    _savefig(
        "reference_listing_presence_boundary_panel_v0_1.png",
        manifest_rows,
        category="coverage_boundary",
        evidence_sources="reference_listing_presence_summary_v0_1.csv; reference_case_manifest_v0_1.csv",
        what_it_shows="Listing snapshot density, LT1B overlap, casepack count and downstream consumer boundaries.",
        inspector_question="Can all_tickers or ticker_change be used as final universe or trading signal?",
        interpretation="No. Reference supports presence, corporate actions and overlays under policy, not final universe or alpha.",
        status="human_inspector_ready_with_boundaries",
    )


def _casepack_status_panel(case_manifest: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    table_data = case_manifest[["status", "casepack"]].copy()
    table_data["casepack"] = table_data["casepack"].str.replace("_v0_1.md", "", regex=False)
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    ax.axis("off")
    table = ax.table(cellText=table_data.values, colLabels=table_data.columns, loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(7.5)
    table.scale(1.0, 1.25)
    ax.set_title("Reference casepacks preserve good, review, bad, causal and coverage boundaries")
    fig.text(
        0.01,
        0.01,
        "Read: casepacks are state/family examples, not a silent promotion of every reference payload to production use.",
        fontsize=8,
    )
    _savefig(
        "reference_casepack_status_panel_v0_1.png",
        manifest_rows,
        category="good_review_bad_boundary",
        evidence_sources="reference_case_manifest_v0_1.csv",
        what_it_shows="Inventory of good, review, bad, causal and coverage reference casepacks.",
        inspector_question="Are casepack states separated for human inspection?",
        interpretation="Yes. The visual pack preserves explicit case families instead of collapsing them into one pass/fail claim.",
        status="human_inspector_ready",
    )


def _copy_population_visuals(manifest_rows: list[dict[str, str]]) -> None:
    visuals = [
        (
            "01_identity_quality_distribution.png",
            "identity_historical",
            "Existing population overview for identity quality.",
            "What is the identity good/review/bad distribution?",
            "Good identity dominates, with review and bad residuals explicit.",
            "usable_with_identity_flags",
        ),
        (
            "02_download_endpoint_status.png",
            "endpoint_historical",
            "Existing population overview for endpoint download status.",
            "Which endpoints have ok/error/404 status mass?",
            "Overview has identity-linked 404/error residual; events 404s have no-event semantics.",
            "usable_with_endpoint_semantics",
        ),
        (
            "03_payload_family_distribution.png",
            "payload_historical",
            "Existing population overview for events, splits and dividends payload families.",
            "Which payload families contain real events?",
            "Dividends and splits have real payload; empty/no-event payloads remain explicit.",
            "usable_with_payload_flags",
        ),
        (
            "04_causal_alignment_distribution.png",
            "causal_historical",
            "Existing population overview for reference causal overlays.",
            "Where does reference explain downstream market-data anomalies?",
            "Events->halts and splits->trades are strongest; other overlays remain review.",
            "usable_with_causal_boundaries",
        ),
        (
            "05_listing_snapshot_density.png",
            "coverage_historical",
            "Existing population overview for all_tickers listing snapshot density.",
            "Can all_tickers support temporal presence?",
            "Yes as support, not as final PTI universe membership.",
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

    population = pd.read_csv(POPULATION_ROOT / "reference_population_summary_v0_1.csv")
    endpoints = pd.read_csv(POPULATION_ROOT / "reference_download_endpoint_summary_v0_1.csv")
    listing = pd.read_csv(POPULATION_ROOT / "reference_listing_presence_summary_v0_1.csv")
    case_manifest = pd.read_csv(EVIDENCE_ROOT / "case_manifest" / "reference_case_manifest_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _identity_quality_panel(population, manifest_rows)
    _endpoint_status_panel(endpoints, manifest_rows)
    _payload_family_panel(population, manifest_rows)
    _causal_alignment_panel(population, manifest_rows)
    _listing_presence_boundary_panel(listing, case_manifest, manifest_rows)
    _casepack_status_panel(case_manifest, manifest_rows)
    _copy_population_visuals(manifest_rows)
    _write_manifest(manifest_rows)


if __name__ == "__main__":
    main()
