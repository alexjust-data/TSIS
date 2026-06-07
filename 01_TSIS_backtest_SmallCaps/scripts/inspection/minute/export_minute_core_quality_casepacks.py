from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
DOSSIER_DIR = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "minute"
CORE_ROOT = DOSSIER_DIR / "evidence_assets" / "core_quality"
MANIFEST_PATH = CORE_ROOT / "minute_core_quality_manifest_v0_1.parquet"
CASEPACK_ROOT = DOSSIER_DIR / "core_quality_case_evidence_packs"
IMAGES_DIR = CASEPACK_ROOT / "images"
CASE_MANIFEST_PATH = CASEPACK_ROOT / "minute_core_quality_visual_case_manifest_v0_1.csv"

CASES_PER_SECTION = 10


@dataclass(frozen=True)
class SectionSpec:
    section: str
    title: str
    description: str
    mask_kind: str
    sort_cols: tuple[str, ...]
    ascending: tuple[bool, ...]


SECTIONS = [
    SectionSpec(
        "core_good_vw_not_flagged",
        "Core good / vw not flagged",
        "Dense or active OHLCV months where the inherited closeout does not flag vw.",
        "core_good_vw_not_flagged",
        ("m.rows_after_parse", "ticker"),
        (False, True),
    ),
    SectionSpec(
        "core_good_vw_mild_or_moderate",
        "Core good / vw mild or moderate",
        "OHLCV-usable months where vw has visible residue but remains outside the hard bad families.",
        "core_good_vw_mild_or_moderate",
        ("vw_ratio_pct", "m.rows_after_parse"),
        (False, False),
    ),
    SectionSpec(
        "core_good_vw_bad_persistent",
        "Core good / vw bad persistent",
        "OHLCV-usable months where vw is persistently outside range and must be excluded from consumption.",
        "core_good_vw_bad_persistent",
        ("vw_ratio_pct", "m.rows_after_parse"),
        (False, False),
    ),
    SectionSpec(
        "core_good_vw_bad_diffuse",
        "Core good / vw bad diffuse",
        "OHLCV-usable months with broad vw damage that is severe but less persistent than the hardest family.",
        "core_good_vw_bad_diffuse",
        ("vw_ratio_pct", "m.rows_after_parse"),
        (False, False),
    ),
    SectionSpec(
        "core_review_large_gap",
        "Core review / large internal gap",
        "Months where continuity gaps force review even if price bars are otherwise interpretable.",
        "core_review_large_gap",
        ("m.max_gap_days", "m.rows_after_parse"),
        (False, False),
    ),
    SectionSpec(
        "core_review_sparse",
        "Core review / sparse coverage",
        "Months with too few active days or low coverage ratio for unflagged research.",
        "core_review_sparse",
        ("m.rows_after_parse", "ticker"),
        (False, True),
    ),
]


def load_manifest() -> pd.DataFrame:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(MANIFEST_PATH)
    return pd.read_parquet(MANIFEST_PATH)


def section_mask(df: pd.DataFrame, kind: str) -> pd.Series:
    core = df["core_quality_state"].astype(str)
    vw = df["vw_issue_family"].astype(str)
    combined = df["combined_quality_state"].astype(str)
    family = df["core_issue_family"].astype(str)

    if kind == "core_good_vw_not_flagged":
        return core.eq("good") & vw.eq("vw_not_flagged")
    if kind == "core_good_vw_mild_or_moderate":
        return core.eq("good") & vw.isin(["vw_mild_low_ratio", "vw_moderate_ratio", "vw_severe_tiny_base", "vw_severe_small_mass"])
    if kind == "core_good_vw_bad_persistent":
        return combined.eq("core_good_vw_bad") & vw.eq("vw_severe_large_mass_persistent")
    if kind == "core_good_vw_bad_diffuse":
        return combined.eq("core_good_vw_bad") & vw.eq("vw_severe_large_mass_diffuse")
    if kind == "core_review_large_gap":
        return core.eq("review") & family.str.contains("large_internal_gap", na=False)
    if kind == "core_review_sparse":
        return core.eq("review") & family.str.contains("coverage_sparse", na=False)
    raise ValueError(kind)


def select_cases(df: pd.DataFrame) -> pd.DataFrame:
    chunks = []
    for spec in SECTIONS:
        mask = section_mask(df, spec.mask_kind)
        subset = df.loc[mask].copy()
        existing_sort = [c for c in spec.sort_cols if c in subset.columns]
        ascending = list(spec.ascending[: len(existing_sort)])
        if existing_sort:
            subset = subset.sort_values(existing_sort, ascending=ascending, kind="mergesort")
        subset = subset.head(CASES_PER_SECTION).copy()
        subset["visual_section"] = spec.section
        subset["visual_section_title"] = spec.title
        subset["visual_section_description"] = spec.description
        subset["visual_rank"] = range(1, len(subset) + 1)
        chunks.append(subset)
    return pd.concat(chunks, ignore_index=True)


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    df["ts"] = pd.to_datetime(df["ts_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["ts"]).sort_values("ts")
    for col in ["o", "h", "l", "c", "v", "vw", "n"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date_key"] = df["ts"].dt.date.astype(str)
    return df


def add_visual_metrics(raw: pd.DataFrame) -> pd.DataFrame:
    out = raw.copy()
    price_scale = out[["h", "l", "vw"]].abs().max(axis=1).replace(0, np.nan)
    outside_signed = np.where(out["vw"] < out["l"], out["vw"] - out["l"], np.where(out["vw"] > out["h"], out["vw"] - out["h"], 0.0))
    out["vw_outside_strict"] = out["vw"].notna() & out["l"].notna() & out["h"].notna() & ((out["vw"] < out["l"]) | (out["vw"] > out["h"]))
    out["vw_outside_bps"] = 10000.0 * np.abs(outside_signed) / price_scale
    out["vw_outside_visual"] = out["vw_outside_strict"] & out["vw_outside_bps"].ge(1.0)
    return out


def daily_summary(raw: pd.DataFrame) -> pd.DataFrame:
    g = raw.groupby("date_key", dropna=False)
    out = g.agg(
        rows=("c", "size"),
        close=("c", "last"),
        high=("h", "max"),
        low=("l", "min"),
        volume=("v", "sum"),
        trades=("n", "sum"),
        vw_outside_strict=("vw_outside_strict", "sum"),
        vw_outside_visual=("vw_outside_visual", "sum"),
        max_vw_outside_bps=("vw_outside_bps", "max"),
    ).reset_index()
    out["strict_ratio_pct"] = 100.0 * out["vw_outside_strict"] / out["rows"].replace(0, np.nan)
    out["visual_ratio_pct"] = 100.0 * out["vw_outside_visual"] / out["rows"].replace(0, np.nan)
    out["date"] = pd.to_datetime(out["date_key"], errors="coerce")
    return out


def fmt(value, digits: int = 2) -> str:
    try:
        value = float(value)
    except Exception:
        return "nan"
    if np.isnan(value):
        return "nan"
    return f"{value:,.{digits}f}"


def plot_case(row: pd.Series, raw: pd.DataFrame, out_path: Path) -> dict:
    raw = add_visual_metrics(raw)
    daily = daily_summary(raw)
    visual = raw.loc[raw["vw_outside_visual"]].copy()

    fig = plt.figure(figsize=(14, 10), constrained_layout=True)
    gs = fig.add_gridspec(4, 1, height_ratios=[3.2, 1.25, 1.35, 1.6])
    ax_price = fig.add_subplot(gs[0, 0])
    ax_cov = fig.add_subplot(gs[1, 0], sharex=ax_price)
    ax_vw = fig.add_subplot(gs[2, 0], sharex=ax_price)
    ax_card = fig.add_subplot(gs[3, 0])

    ax_price.fill_between(raw["ts"], raw["l"], raw["h"], color="#b7d7f0", alpha=0.28, label="1m low-high")
    ax_price.plot(raw["ts"], raw["c"], color="#1f4e79", linewidth=0.8, label="close")
    ax_price.plot(raw["ts"], raw["vw"], color="#7a3b9a", linewidth=0.45, alpha=0.7, label="vw")
    if not visual.empty:
        ax_price.scatter(visual["ts"], visual["vw"], s=14, color="#d62728", alpha=0.82, label="vw outside >1bp")
    ax_price.set_title(
        f"{row['ticker']} {int(row['year'])}-{int(row['month']):02d} | {row['visual_section_title']}",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    ax_price.set_ylabel("price")
    ax_price.legend(loc="upper left", ncol=4, fontsize=8)
    ax_price.grid(True, alpha=0.25)

    ax_cov.bar(daily["date"], daily["rows"], color="#4c78a8", width=0.8)
    ax_cov.set_ylabel("rows")
    ax_cov.set_title("Daily row coverage inside the month", loc="left", fontsize=10)
    ax_cov.grid(True, axis="y", alpha=0.25)

    ax_vw.bar(daily["date"], daily["visual_ratio_pct"].fillna(0.0), color="#d62728", width=0.8, label="visual >1bp")
    ax_vw.plot(daily["date"], daily["strict_ratio_pct"].fillna(0.0), color="#7f7f7f", linewidth=1.1, label="strict any outside")
    ax_vw.axhline(5.0, color="#8c564b", linestyle="--", linewidth=1.0, alpha=0.8)
    ax_vw.set_ylabel("vw outside %")
    ax_vw.set_title("Daily vw outside low-high: strict vs visually material >1bp", loc="left", fontsize=10)
    ax_vw.legend(loc="upper left", fontsize=8)
    ax_vw.grid(True, axis="y", alpha=0.25)

    strict_rows = int(raw["vw_outside_strict"].sum())
    visual_rows = int(raw["vw_outside_visual"].sum())
    strict_ratio = 100.0 * strict_rows / max(len(raw), 1)
    visual_ratio = 100.0 * visual_rows / max(len(raw), 1)
    max_bps = float(raw["vw_outside_bps"].replace([np.inf, -np.inf], np.nan).max())

    ax_card.axis("off")
    card = dedent(
        f"""
        core_quality_state: {row['core_quality_state']}    vw_quality_state: {row['vw_quality_state']}    combined_quality_state: {row['combined_quality_state']}
        allowed_consumption: {row['allowed_consumption']}
        core_issue_family: {row['core_issue_family']}
        inherited_vw_issue_family: {row['vw_issue_family']}
        inherited_vw_outside_rows: {fmt(row.get('m.vw_outside_range_rows'), 0)}    inherited_vw_ratio_pct: {fmt(row.get('vw_ratio_pct'), 3)}
        recalculated_strict_vw_outside_rows: {strict_rows:,} ({strict_ratio:.3f}%)    visual_gt_1bp_rows: {visual_rows:,} ({visual_ratio:.3f}%)    max_outside_bps: {max_bps:.3f}
        rows_after_parse: {fmt(row['m.rows_after_parse'], 0)}    active_days: {fmt(row['m.active_days'], 0)}    coverage_ratio: {fmt(row['m.coverage_ratio_vs_active_days_est'], 3)}    max_gap_days: {fmt(row['m.max_gap_days'], 0)}
        file: {row['file']}
        """
    ).strip()
    ax_card.text(
        0.01,
        0.95,
        card,
        va="top",
        ha="left",
        fontsize=8.5,
        family="monospace",
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f7f7f7", "edgecolor": "#cccccc"},
    )

    ax_vw.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10))
    ax_vw.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    for label in ax_vw.get_xticklabels():
        label.set_rotation(30)
        label.set_horizontalalignment("right")

    fig.savefig(out_path, dpi=145)
    plt.close(fig)

    return {
        "recalc_strict_vw_outside_rows": strict_rows,
        "recalc_strict_vw_ratio_pct": strict_ratio,
        "visual_gt_1bp_vw_outside_rows": visual_rows,
        "visual_gt_1bp_vw_ratio_pct": visual_ratio,
        "max_vw_outside_bps": max_bps,
    }


def export() -> pd.DataFrame:
    manifest = load_manifest()
    cases = select_cases(manifest)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, row in cases.iterrows():
        raw = load_raw(Path(str(row["file"])))
        case_id = f"{row['visual_section']}_{int(row['visual_rank']):02d}_{row['ticker']}_{int(row['year'])}_{int(row['month']):02d}".lower()
        image_name = f"{case_id}.png"
        image_path = IMAGES_DIR / image_name
        metrics = plot_case(row, raw, image_path)
        record = row.to_dict()
        record.update(metrics)
        record["case_id"] = case_id
        record["image"] = f"images/{image_name}"
        record["image_path"] = str(image_path)
        rows.append(record)
    out = pd.DataFrame(rows)
    out.to_csv(CASE_MANIFEST_PATH, index=False)
    return out


def main() -> None:
    out = export()
    print(f"exported_cases={len(out)}")
    print(f"case_manifest={CASE_MANIFEST_PATH}")
    print(f"images_dir={IMAGES_DIR}")
    print(out[["visual_section", "visual_rank", "ticker", "year", "month", "case_id", "image"]].to_string(index=False))


if __name__ == "__main__":
    main()
