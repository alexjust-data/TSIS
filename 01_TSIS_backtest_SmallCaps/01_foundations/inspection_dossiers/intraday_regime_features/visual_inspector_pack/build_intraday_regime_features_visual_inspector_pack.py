from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap


PACK_ROOT = Path(__file__).resolve().parent
DOSSIER_ROOT = PACK_ROOT.parent
EVIDENCE_ROOT = DOSSIER_ROOT / "evidence_assets"
IMAGE_ROOT = PACK_ROOT / "images"
SOURCE_IMAGE_ROOT = DOSSIER_ROOT / "images"


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


def _copy_case_image(
    source_relative: str,
    manifest_rows: list[dict[str, str]],
    **row: str,
) -> None:
    source_path = DOSSIER_ROOT / source_relative
    target_path = IMAGE_ROOT / source_path.name
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
    case_path = PACK_ROOT / "intraday_regime_features_visual_case_manifest_v0_1.csv"
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

    audit_path = PACK_ROOT / "intraday_regime_features_visual_asset_audit_v0_1.csv"
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


def _population_map(
    materialization: pd.DataFrame,
    summary: dict,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = materialization.sort_values(["days_written", "ticker"], ascending=[False, True])
    feature_summary = summary["feature_summary"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), gridspec_kw={"width_ratios": [1.35, 1]})

    ax1.bar(data["ticker"], data["days_written"], color="#2c5c8a")
    ax1.set_title("Scoped pilot population")
    ax1.set_ylabel("ticker-day rows")
    ax1.grid(axis="y", alpha=0.25)
    for index, row in data.reset_index(drop=True).iterrows():
        ax1.text(index, row["days_written"] + 1.0, str(int(row["days_written"])), ha="center", fontsize=8)

    ax2.axis("off")
    summary_rows = [
        ["parquet files", summary["parquet_files"]],
        ["read errors", summary["read_errors"]],
        ["tickers", feature_summary["ticker_count"]],
        ["ticker-day rows", feature_summary["rows_total"]],
        ["columns", feature_summary["columns_count"]],
        ["date min", feature_summary["date_min"]],
        ["date max", feature_summary["date_max"]],
        ["duplicate ticker+date rows", feature_summary["duplicate_ticker_date_rows"]],
    ]
    table = ax2.table(cellText=summary_rows, colLabels=["metric", "value"], loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.25)
    ax2.set_title("Physical evidence snapshot")

    fig.text(
        0.01,
        0.01,
        "Read: this is an intentionally scoped 8-ticker semantic pilot, not a production feature-store census.",
        fontsize=8,
    )
    _savefig(
        "intraday_regime_features_pilot_population_map_v0_1.png",
        manifest_rows,
        category="coverage_scope",
        evidence_sources="intraday_regime_features_materialization_summary_v0_1.csv; intraday_regime_features_audit_summary_v0_1.json",
        what_it_shows="Ticker-day population, physical footprint, date span and duplicate-key summary for the pilot.",
        inspector_question="What exactly is covered by this feature pilot?",
        interpretation="The package proves the declared pilot population only; it must not be read as full-universe materialization.",
        status="scoped",
    )


def _semantic_case_summary(cases: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = cases.sort_values("max_abs_gap_diff_pct", ascending=True).reset_index(drop=True)
    colors = {
        "reverse_split": "#8f2d2d",
        "forward_split": "#2c5c8a",
        "control": "#6d8f57",
    }
    labels = data["ticker"] + " " + data["month"] + "\n" + data["role"].str.replace("_", " ")

    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.barh(labels, data["max_abs_gap_diff_pct"], color=[colors.get(role, "#777777") for role in data["role"]])
    ax.set_title("Raw vs split-normalized divergence is localized to split-sensitive cases")
    ax.set_xlabel("max absolute gap feature difference (%)")
    ax.grid(axis="x", alpha=0.25)
    for index, row in data.iterrows():
        value = float(row["max_abs_gap_diff_pct"])
        offset = max(data["max_abs_gap_diff_pct"].max() * 0.012, 8.0)
        ax.text(value + offset, index, f"{value:,.2f}%", va="center", fontsize=8)
    ax.axvline(50, color="#555555", linestyle="--", lw=1, alpha=0.7)
    ax.text(
        80,
        len(data) - 0.55,
        "50% review threshold",
        va="top",
        ha="left",
        fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 1.5},
    )
    fig.text(
        0.01,
        0.01,
        "Read: strong reverse-split cases show large cross-session feature divergence; controls remain at zero.",
        fontsize=8,
    )
    _savefig(
        "intraday_regime_features_semantic_case_summary_v0_1.png",
        manifest_rows,
        category="good_boundary_control",
        evidence_sources="intraday_regime_features_semantic_case_manifest_v0_1.csv",
        what_it_shows="Maximum raw-vs-normalized feature divergence by semantic pilot case.",
        inspector_question="Does the consumer react where split normalization should matter and remain neutral for controls?",
        interpretation="Yes within pilot scope: split-sensitive cases diverge strongly while controls remain neutral.",
        status="scoped_pass",
    )


def _lookback_null_boundary(nulls: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    top = nulls[nulls["nulls"] > 0].sort_values("null_pct", ascending=True).tail(12)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.barh(top["column"], top["null_pct"], color="#8b5a2b")
    ax.set_title("Nulls concentrate in expected lookback-dependent feature columns")
    ax.set_xlabel("null rows (%)")
    ax.grid(axis="x", alpha=0.25)
    for index, row in top.reset_index(drop=True).iterrows():
        ax.text(row["null_pct"] + 0.35, index, f"{int(row['nulls'])} nulls / {row['null_pct']:.2f}%", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: lookback features require previous sessions; nulls are boundary evidence, not silent corruption, inside this pilot scope.",
        fontsize=8,
    )
    _savefig(
        "intraday_regime_features_lookback_null_boundary_panel_v0_1.png",
        manifest_rows,
        category="boundary_case",
        evidence_sources="intraday_regime_features_null_summary_v0_1.csv",
        what_it_shows="Top non-zero null rates by feature column.",
        inspector_question="Are nulls concentrated in interpretable lookback boundaries?",
        interpretation="Yes for the pilot evidence: nulls are in z-score, multi-session and previous-session columns.",
        status="boundary_scoped",
    )


def _provenance_matrix(provenance: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    data = provenance.copy()
    data["match_ratio"] = data["matching_files"] / data["files"]
    matrix = data[["match_ratio"]].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8, 4.6))
    cmap = ListedColormap(["#9b2f2f", "#6d8f57"])
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks([0], ["matching files / files"])
    ax.set_yticks(range(len(data)), data["column"])
    ax.set_title("Provenance columns match the expected feature contract")
    for index, row in data.iterrows():
        ax.text(
            0,
            index,
            f"{int(row['matching_files'])}/{int(row['files'])}\n{row['unique_values']}",
            ha="center",
            va="center",
            fontsize=8,
        )
    fig.text(
        0.01,
        0.01,
        "Read: every feature file advertises the expected contract, grain and price-view semantics.",
        fontsize=8,
    )
    _savefig(
        "intraday_regime_features_provenance_matrix_v0_1.png",
        manifest_rows,
        category="provenance",
        evidence_sources="intraday_regime_features_provenance_summary_v0_1.csv",
        what_it_shows="Per-column provenance value matching across all feature files.",
        inspector_question="Can a downstream consumer reconstruct the intended data semantics from file metadata?",
        interpretation="Yes within pilot scope: all provenance columns match the expected values in all files.",
        status="scoped_pass",
    )


def _production_boundary_panel(manifest_rows: list[dict[str, str]]) -> None:
    decisions = pd.DataFrame(
        [
            ("ohlcv_1m_split_normalized validation", "allowed"),
            ("feature semantic inspection", "allowed"),
            ("research_only", "allowed with pilot scope"),
            ("backtest_extended", "restricted"),
            ("ml_flagged", "restricted"),
            ("backtest_core", "not enabled"),
            ("ml_primary", "not enabled"),
            ("execution_simulator", "not enabled"),
            ("rl_allowed", "not enabled"),
            ("live_downstream_candidate", "not enabled"),
        ],
        columns=["consumer", "decision"],
    )
    score = {
        "allowed": 2,
        "allowed with pilot scope": 1.5,
        "restricted": 1,
        "not enabled": 0,
    }
    color = {
        "allowed": "#2f7d4f",
        "allowed with pilot scope": "#6d8f57",
        "restricted": "#cf8d2e",
        "not enabled": "#9b2f2f",
    }
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.barh(decisions["consumer"], decisions["decision"].map(score), color=decisions["decision"].map(color))
    ax.invert_yaxis()
    ax.set_xlim(0, 2.4)
    ax.set_title("Production boundary: pilot-valid does not mean production-enabled")
    ax.set_xlabel("permission level")
    ax.set_xticks([0, 1, 1.5, 2], ["not enabled", "restricted", "pilot", "allowed"])
    ax.grid(axis="x", alpha=0.25)
    for index, row in decisions.iterrows():
        ax.text(score[row["decision"]] + 0.05, index, row["decision"], va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Read: the feature layer is institutionally inspectable as a semantic pilot, but production consumers remain blocked.",
        fontsize=8,
    )
    _savefig(
        "intraday_regime_features_production_boundary_panel_v0_1.png",
        manifest_rows,
        category="production_boundary",
        evidence_sources="intraday_regime_features_quality_report_v0_1.md",
        what_it_shows="Allowed, restricted and not-enabled downstream consumers for this scoped pilot.",
        inspector_question="Which consumers may treat this pilot as usable input?",
        interpretation="Only scoped validation/inspection/research uses are allowed; production and live surfaces are not enabled.",
        status="scoped_boundary",
    )


def _copy_semantic_case_images(cases: pd.DataFrame, manifest_rows: list[dict[str, str]]) -> None:
    for _, row in cases.iterrows():
        role = str(row["role"])
        if role == "control":
            category = "control_case"
            status = "control_pass"
            interpretation = "Control case remains neutral under raw-vs-normalized comparison."
        elif float(row["max_abs_gap_diff_pct"]) >= 50:
            category = "good_split_case"
            status = "scoped_pass"
            interpretation = "Split-sensitive case shows material raw-vs-normalized divergence."
        else:
            category = "boundary_split_case"
            status = "boundary_scoped"
            interpretation = "Split case remains coherent but below the 50% review threshold."

        ticker_month = f"{row['ticker']} {row['month']}"
        _copy_case_image(
            str(row["image"]),
            manifest_rows,
            category=category,
            evidence_sources="intraday_regime_features_semantic_case_manifest_v0_1.csv; dossier images/",
            what_it_shows=(
                f"{ticker_month} {role} raw-vs-split-normalized feature comparison with future split factor."
            ),
            inspector_question="Does this concrete ticker/month show the expected split-normalization behavior?",
            interpretation=interpretation,
            status=status,
        )


def main() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    materialization = pd.read_csv(EVIDENCE_ROOT / "intraday_regime_features_materialization_summary_v0_1.csv")
    nulls = pd.read_csv(EVIDENCE_ROOT / "intraday_regime_features_null_summary_v0_1.csv")
    provenance = pd.read_csv(EVIDENCE_ROOT / "intraday_regime_features_provenance_summary_v0_1.csv")
    cases = pd.read_csv(EVIDENCE_ROOT / "intraday_regime_features_semantic_case_manifest_v0_1.csv")
    with (EVIDENCE_ROOT / "intraday_regime_features_audit_summary_v0_1.json").open("r", encoding="utf-8") as handle:
        summary = json.load(handle)

    manifest_rows: list[dict[str, str]] = []
    _population_map(materialization, summary, manifest_rows)
    _semantic_case_summary(cases, manifest_rows)
    _lookback_null_boundary(nulls, manifest_rows)
    _provenance_matrix(provenance, manifest_rows)
    _production_boundary_panel(manifest_rows)
    _copy_semantic_case_images(cases, manifest_rows)
    _write_manifest(manifest_rows)


if __name__ == "__main__":
    main()
