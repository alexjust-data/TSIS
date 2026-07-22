from __future__ import annotations

import csv
import json
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
    case_path = PACK_ROOT / "regime_indicators_visual_case_manifest_v0_1.csv"
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

    audit_path = PACK_ROOT / "regime_indicators_visual_asset_audit_v0_1.csv"
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


def _daily_date_collapse_panel(
    daily_quality: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    sample_root = EVIDENCE_ROOT / "sample_payloads"
    spy = pd.read_csv(sample_root / "spy_day_broken_sample_v0_1.csv").head(8)
    ndx = pd.read_csv(sample_root / "i_ndx_day_broken_sample_v0_1.csv").head(8)

    counts = pd.DataFrame(
        {
            "state": ["daily files", "1970-only daily files", "daily rows"],
            "value": [
                len(daily_quality),
                int(daily_quality["has_1970_date_only"].sum()),
                int(daily_quality["rows"].sum()),
            ],
        }
    )

    fig = plt.figure(figsize=(12, 7))
    grid = fig.add_gridspec(2, 2, height_ratios=[0.9, 1.2])
    ax1 = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[0, 1])
    ax3 = fig.add_subplot(grid[1, :])

    ax1.bar(counts["state"], counts["value"], color=["#6a7f95", "#9b2f2f", "#c58b37"])
    ax1.set_title("Daily date blocker scope")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    ax1.set_ylim(0, max(counts["value"]) * 1.18)
    for index, value in enumerate(counts["value"]):
        ax1.text(index, value + max(counts["value"]) * 0.025, f"{int(value):,}", ha="center")

    summary = daily_quality.groupby("group").agg(files=("relative_path", "count"), rows=("rows", "sum")).reset_index()
    ax2.bar(summary["group"], summary["files"], color=["#567f62", "#80648b"])
    ax2.set_title("Daily files affected by group")
    ax2.set_ylabel("files")
    ax2.grid(axis="y", alpha=0.25)
    ax2.set_ylim(0, max(summary["files"]) * 1.25)
    for index, row in summary.iterrows():
        ax2.text(index, row["files"] + 0.4, f"{int(row['files'])} files\n{int(row['rows']):,} rows", ha="center")

    ax3.axis("off")
    table_source = pd.concat(
        [
            spy[["date", "datetime", "open", "high", "low", "close"]].assign(sample="SPY day"),
            ndx[["date", "datetime", "open", "high", "low", "close"]].assign(sample="I_NDX day"),
        ],
        ignore_index=True,
    ).head(10)
    table_source = table_source[["sample", "date", "datetime", "open", "high", "low", "close"]]
    table = ax3.table(
        cellText=table_source.astype(str).values,
        colLabels=table_source.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.25)
    ax3.set_title("Representative daily rows: calendar key collapsed to 1970-01-01")
    fig.text(
        0.01,
        0.01,
        "Read: daily bars are readable, but all inspected daily files collapse to date=1970-01-01; they cannot serve calendar-keyed regime features.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_daily_date_collapse_panel_v0_1.png",
        manifest_rows,
        category="bad_blocking",
        evidence_sources="regime_indicators_daily_date_quality_v0_1.csv; sample_payloads/spy_day_broken_sample_v0_1.csv; sample_payloads/i_ndx_day_broken_sample_v0_1.csv",
        what_it_shows="Daily blocker scope and concrete broken daily rows.",
        inspector_question="Is the daily defect isolated or structural?",
        interpretation="Structural. All 34 daily files are affected by 1970 date semantics.",
        status="blocking",
    )


def _daily_file_date_heatmap(
    daily_quality: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = daily_quality.sort_values(["group", "symbol_dir"]).copy()
    data["rows_scaled"] = data["rows"] / data["rows"].max()
    data["date_unique_scaled"] = data["date_unique"] / max(1, data["date_unique"].max())
    data["datetime_unique_scaled"] = data["datetime_unique"] / data["datetime_unique"].max()
    matrix = data[
        ["rows_scaled", "date_unique_scaled", "datetime_unique_scaled", "has_1970_date_only"]
    ].astype(float).to_numpy()

    labels = ["rows scaled", "date_unique scaled", "datetime_unique scaled", "1970-only flag"]
    fig, ax = plt.subplots(figsize=(8.5, 10.5))
    cmap = LinearSegmentedColormap.from_list("regime_heatmap", ["#f4f1e8", "#d6bd7b", "#8c3f3f"])
    image = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_title("Daily file date quality: every file has one bad calendar date")
    ax.set_xticks(range(len(labels)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(data)), data["relative_path"])
    for i in range(matrix.shape[0]):
        ax.text(3, i, "1970" if data.iloc[i]["has_1970_date_only"] else "ok", ha="center", va="center", fontsize=7)
    fig.colorbar(image, ax=ax, label="scaled value")
    fig.text(
        0.01,
        0.01,
        "Read: datetime has row-level variation, but date has one collapsed value per file; joins on date are invalid.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_daily_file_date_heatmap_v0_1.png",
        manifest_rows,
        category="coverage_blocker",
        evidence_sources="regime_indicators_daily_date_quality_v0_1.csv",
        what_it_shows="Per-file daily rows, date uniqueness, datetime uniqueness and 1970-only flag.",
        inspector_question="Which daily files are affected by the invalid date key?",
        interpretation="All inspected daily ETF and index files are affected.",
        status="blocking",
    )


def _minute_high_low_inversion_panel(
    minute_review: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    sample = pd.read_csv(EVIDENCE_ROOT / "sample_payloads" / "minute_high_lt_low_issue_samples_v0_1.csv")
    flagged = minute_review[minute_review["high_lt_low_rows"] > 0].copy()
    top = minute_review.sort_values("rows", ascending=False).head(10)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [0.9, 1.2]})
    ax1.bar(top["symbol_dir"], top["rows"], color="#6a7f95", label="minute rows")
    if not flagged.empty:
        ax1.scatter(flagged["symbol_dir"], flagged["rows"], s=140, color="#9b2f2f", label="has high < low rows", zorder=3)
        for _, row in flagged.iterrows():
            ax1.text(row["symbol_dir"], row["rows"] * 1.02, f"{int(row['high_lt_low_rows'])} flags", ha="center", color="#9b2f2f")
    ax1.set_title("Minute review: only UVXY carries high < low flags in scoped evidence")
    ax1.set_ylabel("rows")
    ax1.tick_params(axis="x", rotation=35)
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.25)

    ax2.axis("off")
    table_source = sample[["timestamp", "open", "high", "low", "close", "volume", "vwap"]].head(8)
    table = ax2.table(
        cellText=table_source.astype(str).values,
        colLabels=table_source.columns,
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1, 1.25)
    ax2.set_title("Representative UVXY high < low rows")
    fig.text(
        0.01,
        0.01,
        "Read: minute files are readable and mostly structurally coherent, but UVXY has 204 high<low rows requiring classification or repair.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_minute_high_low_inversion_panel_v0_1.png",
        manifest_rows,
        category="flagged_review",
        evidence_sources="regime_indicators_minute_schema_review_v0_1.csv; sample_payloads/minute_high_lt_low_issue_samples_v0_1.csv",
        what_it_shows="Minute row population, flagged UVXY file and concrete high<low samples.",
        inspector_question="Is the minute layer clean enough for production features?",
        interpretation="No. It is readable/scoped review only until UVXY and broader minute checks are resolved.",
        status="review",
    )


def _minute_coverage_readability_map(
    minute_review: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = minute_review.copy()
    data["timestamp_min_dt"] = pd.to_datetime(data["timestamp_min"], errors="coerce")
    data["timestamp_max_dt"] = pd.to_datetime(data["timestamp_max"], errors="coerce")
    data = data.sort_values(["group", "timestamp_min_dt", "symbol_dir"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1.4, 0.9]})
    for index, (_, row) in enumerate(data.iterrows()):
        color = "#2c5c8a" if row["group"] == "etfs" else "#6d5a8e"
        ax1.plot([row["timestamp_min_dt"], row["timestamp_max_dt"]], [index, index], lw=4, color=color)
    ax1.set_yticks(range(len(data)), data["symbol_dir"])
    ax1.set_title("Minute timestamp coverage windows")
    ax1.grid(axis="x", alpha=0.25)
    ax1.set_xlabel("timestamp range")

    status_counts = pd.DataFrame(
        {
            "check": [
                "minute files",
                "duplicate timestamp rows",
                "non-monotonic files",
                "negative volume rows",
                "high < low rows",
            ],
            "value": [
                len(minute_review),
                int(minute_review["duplicate_timestamp_rows"].sum()),
                int((minute_review["monotonic_increasing"] == False).sum()),
                int(minute_review["negative_volume_rows"].sum()),
                int(minute_review["high_lt_low_rows"].sum()),
            ],
        }
    )
    colors = ["#2f7d4f", "#2f7d4f", "#2f7d4f", "#2f7d4f", "#cf8d2e"]
    ax2.barh(status_counts["check"], status_counts["value"], color=colors)
    ax2.set_title("Scoped minute readability checks")
    ax2.grid(axis="x", alpha=0.25)
    for y_pos, value in enumerate(status_counts["value"]):
        ax2.text(value + max(status_counts["value"]) * 0.03 + 0.1, y_pos, f"{int(value):,}", va="center")
    fig.autofmt_xdate(rotation=30)
    fig.text(
        0.01,
        0.01,
        "Read: minute timestamps cover real historical ranges and pass basic scoped checks, but this is not a full feature-store certification.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_minute_coverage_readability_map_v0_1.png",
        manifest_rows,
        category="good_scoped",
        evidence_sources="regime_indicators_minute_schema_review_v0_1.csv",
        what_it_shows="Minute timestamp ranges and scoped readability checks.",
        inspector_question="What part of the family is still usable for inspection?",
        interpretation="Minute files are source-validation/research-inspection candidates, not production features.",
        status="scoped",
    )


def _metadata_good_examples(
    metadata_summary: pd.DataFrame,
    manifest_rows: list[dict[str, str]],
) -> None:
    data = metadata_summary.copy()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(data["file"], data["top_level_keys_count"], color=["#567f62", "#80648b"])
    ax.set_title("Metadata files are readable context, not daily repair")
    ax.set_ylabel("top-level keys")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", alpha=0.25)
    for index, row in data.iterrows():
        ax.text(
            index,
            row["top_level_keys_count"] + 0.6,
            f"{int(row['top_level_keys_count'])} keys\n{row['sample_keys']}",
            ha="center",
            fontsize=8,
        )
    fig.text(
        0.01,
        0.01,
        "Read: metadata gives coverage/range context, but it does not repair the invalid date field in daily bars.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_metadata_good_examples_v0_1.png",
        manifest_rows,
        category="good_scoped",
        evidence_sources="regime_indicators_metadata_summary_v0_1.csv",
        what_it_shows="Readable metadata files and their key counts/sample keys.",
        inspector_question="Can metadata make the broken daily files usable?",
        interpretation="No. Metadata is useful for inspection and repair planning only.",
        status="scoped",
    )


def _blocked_vs_scoped_consumption_panel(
    manifest_rows: list[dict[str, str]],
) -> None:
    decisions = pd.DataFrame(
        [
            ("data_quality_report", "allowed", "report blocked/scoped state"),
            ("source_validation", "allowed", "repair planning"),
            ("repair_planning", "allowed", "primary next use"),
            ("minute research inspection", "restricted", "schema-readable, not production audited"),
            ("daily regime features", "blocked", "invalid date keys"),
            ("master_daily_table", "blocked", "cannot provide calendar keys"),
            ("backtest_core", "blocked", "no production contract"),
            ("ml_primary", "blocked", "daily blocked; minute review"),
            ("rl_allowed", "blocked", "not PIT/production certified"),
            ("live_downstream_candidate", "blocked", "blocked/scoped only"),
        ],
        columns=["consumer", "decision", "reason"],
    )
    code = {"allowed": 2, "restricted": 1, "blocked": 0}
    decisions["score"] = decisions["decision"].map(code)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    cmap = LinearSegmentedColormap.from_list("consumption", ["#9b2f2f", "#cf8d2e", "#2f7d4f"])
    matrix = decisions[["score"]].to_numpy()
    ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_title("Consumption decision: daily blocked, minute scoped")
    ax.set_xticks([0], ["decision"])
    ax.set_yticks(range(len(decisions)), decisions["consumer"])
    for index, row in decisions.iterrows():
        ax.text(0, index, row["decision"], ha="center", va="center", color="white" if row["decision"] == "blocked" else "black")
        ax.text(0.65, index, row["reason"], va="center", fontsize=8)
    ax.set_xlim(-0.5, 4.8)
    ax.set_frame_on(False)
    fig.text(
        0.01,
        0.01,
        "Read: the only open use is audit/repair/scoped inspection. Calendar-keyed daily and production consumers remain blocked.",
        fontsize=8,
    )
    _savefig(
        "regime_indicators_blocked_vs_scoped_consumption_panel_v0_1.png",
        manifest_rows,
        category="consumption_policy",
        evidence_sources="regime_indicators_inspection_readout_v0_1.md; regime_indicators_quality_report_v0_1.md",
        what_it_shows="Allowed, restricted and blocked consumer decisions.",
        inspector_question="What may consume regime_indicators right now?",
        interpretation="Only audit, validation, repair and scoped minute inspection; production consumers remain blocked.",
        status="policy",
    )


def build() -> None:
    IMAGE_ROOT.mkdir(parents=True, exist_ok=True)
    _configure_matplotlib()

    daily_quality = pd.read_csv(EVIDENCE_ROOT / "regime_indicators_daily_date_quality_v0_1.csv")
    minute_review = pd.read_csv(EVIDENCE_ROOT / "regime_indicators_minute_schema_review_v0_1.csv")
    metadata_summary = pd.read_csv(EVIDENCE_ROOT / "regime_indicators_metadata_summary_v0_1.csv")

    manifest_rows: list[dict[str, str]] = []
    _daily_date_collapse_panel(daily_quality, manifest_rows)
    _daily_file_date_heatmap(daily_quality, manifest_rows)
    _minute_high_low_inversion_panel(minute_review, manifest_rows)
    _minute_coverage_readability_map(minute_review, manifest_rows)
    _metadata_good_examples(metadata_summary, manifest_rows)
    _blocked_vs_scoped_consumption_panel(manifest_rows)
    _write_manifest(manifest_rows)

    print(f"created {len(manifest_rows)} regime indicator visual assets")
    for row in manifest_rows:
        print(f"{row['image_path']} {row['bytes']} bytes")


if __name__ == "__main__":
    build()
