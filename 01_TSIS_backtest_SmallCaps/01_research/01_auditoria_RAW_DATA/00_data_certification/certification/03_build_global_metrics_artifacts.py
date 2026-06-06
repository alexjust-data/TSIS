from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CERT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\certification")
OUT_DIR = CERT_ROOT / "global_metrics"
IMG_DIR = OUT_DIR / "img"

AUDIT_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\00_data_certification\auditoria")
RUNS_ROOT = Path(r"C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest")


def pct(part: float, total: float) -> float:
    return round((100.0 * float(part) / float(total)), 6) if total else 0.0


def write_df(df: pd.DataFrame, stem: str) -> None:
    df.to_parquet(OUT_DIR / f"{stem}.parquet", index=False)
    df.to_csv(OUT_DIR / f"{stem}.csv", index=False)


def build_daily_tables() -> dict[str, pd.DataFrame]:
    excl_summary = json.loads(
        (RUNS_ROOT / "daily_v2_audit" / "daily_lt1b_hard_invalid_exclusion_v030" / "daily_lt1b_hard_invalid_exclusion_summary.json").read_text(encoding="utf-8")
    )
    current_path = Path(excl_summary["source_current_path"])
    target_path = Path(excl_summary["target_lt1b_path"])
    target = set(pd.read_parquet(target_path, columns=["ticker"])["ticker"].dropna().astype(str))
    daily_current = pd.read_parquet(current_path, columns=["ticker"])
    total = int(daily_current["ticker"].astype(str).isin(target).sum())
    bad = int(excl_summary["files_excluded"])
    good_like = total - bad
    quality = pd.DataFrame(
        [
            {"block": "daily", "scope": "ticker_year", "status": "good_or_review", "count": good_like, "pct": pct(good_like, total)},
            {"block": "daily", "scope": "ticker_year", "status": "bad", "count": bad, "pct": pct(bad, total)},
        ]
    )

    cov = json.loads(
        (RUNS_ROOT / "daily_v2_audit" / "problematic57_cross_1m_quotes_trades_full" / "problematic57_cross_1m_quotes_trades_summary.json").read_text(encoding="utf-8")
    )
    coverage = pd.DataFrame(
        [
            {"block": "daily", "scope": "ticker", "status": "complete_daily_present", "count": 4171, "pct": pct(4171, 4824)},
            {"block": "daily", "scope": "ticker", "status": "likely_valid_gap_only", "count": 374, "pct": pct(374, 4824)},
            {"block": "daily", "scope": "ticker", "status": "ambiguous_review", "count": 222, "pct": pct(222, 4824)},
            {"block": "daily", "scope": "ticker", "status": "unexpected_problematic", "count": 57, "pct": pct(57, 4824)},
        ]
    )
    return {"daily_quality": quality, "daily_coverage": coverage, "daily_problematic57_cross": pd.DataFrame([cov])}


def build_1m_tables() -> dict[str, pd.DataFrame]:
    summary = pd.read_parquet(
        RUNS_ROOT / "ohlcv_1m_v2_materialized" / "ohlcv_1m_current_full" / "root_cause_operational_outputs" / "operational_decision_summary.parquet"
    )
    keep = summary.loc[:, ["operational_decision", "files"]].copy()
    total = int(keep["files"].sum())
    keep["block"] = "1m"
    keep["scope"] = "event"
    keep["pct"] = keep["files"].map(lambda x: pct(x, total))
    keep = keep.rename(columns={"operational_decision": "status", "files": "count"})
    return {"1m_operational": keep.sort_values("count", ascending=False).reset_index(drop=True)}


def build_quotes_tables() -> dict[str, pd.DataFrame]:
    import runpy

    ns = runpy.run_path(
        str(AUDIT_ROOT / "quotes" / "v2" / "cell_code" / "00_load_quotes_run_artifacts.py"),
        run_name="quotes_loader",
    )
    payload = ns["load_quotes_artifacts"]()
    handle = payload["quotes_handle_cd"]
    taxonomy = ns["build_taxonomy_summary_cached"](handle, refresh=False).copy()
    taxonomy["block"] = "quotes"
    taxonomy["scope"] = "ticker_date_file"

    open_map = {
        "persistent_soft_crossed_mid_large_scale": "review",
        "large_file_threshold_edge_hard_many_crosses": "review",
        "medium_file_threshold_edge_hard_many_crosses": "bad",
        "high_hard_crossed_10_to_20": "bad",
    }
    open_buckets = taxonomy[taxonomy["taxonomy"].isin(open_map.keys())].copy()
    open_buckets["final_status"] = open_buckets["taxonomy"].map(open_map)

    good_core_tax = {
        "clean_pass_or_other",
        "soft_crossed_micro_noise",
        "persistent_soft_crossed_low",
        "utc_rollover_large_day_clean",
    }
    good_core = taxonomy[taxonomy["taxonomy"].isin(good_core_tax)]["files"].sum()
    total = int(taxonomy["files"].sum())
    quotes_core = pd.DataFrame(
        [
            {"block": "quotes", "scope": "ticker_date_file", "status": "good_core_explicit", "count": int(good_core), "pct": pct(good_core, total)},
            {"block": "quotes", "scope": "ticker_date_file", "status": "review_open_explicit", "count": int(open_buckets.loc[open_buckets["final_status"] == "review", "files"].sum()), "pct": pct(int(open_buckets.loc[open_buckets["final_status"] == "review", "files"].sum()), total)},
            {"block": "quotes", "scope": "ticker_date_file", "status": "bad_open_explicit", "count": int(open_buckets.loc[open_buckets["final_status"] == "bad", "files"].sum()), "pct": pct(int(open_buckets.loc[open_buckets["final_status"] == "bad", "files"].sum()), total)},
            {"block": "quotes", "scope": "ticker_date_file", "status": "other_taxonomies_closed_elsewhere", "count": int(total - good_core - open_buckets["files"].sum()), "pct": pct(int(total - good_core - open_buckets["files"].sum()), total)},
        ]
    )
    return {"quotes_taxonomy": taxonomy, "quotes_open_buckets": open_buckets, "quotes_core_mix": quotes_core}


def build_trades_tables() -> dict[str, pd.DataFrame]:
    base = RUNS_ROOT / "trades_v2_materialized" / "trades_current_cd_merged" / "root_cause_exports" / "file_acceptance_cache_lt1b_full_clean"
    counts = {}
    for p in sorted((base / "raw_metrics_shards").glob("*.parquet")):
        df = pd.read_parquet(p, columns=["acceptance_label"])
        vc = df["acceptance_label"].astype(str).value_counts(dropna=False)
        for label, n in vc.items():
            counts[str(label)] = counts.get(str(label), 0) + int(n)
    total = sum(counts.values())
    raw = pd.DataFrame(
        [{"block": "trades", "scope": "file", "status": k, "count": v, "pct": pct(v, total)} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    )

    strict_recovered_review = 2427056
    residual_review = counts["review"] - strict_recovered_review
    recovery = pd.DataFrame(
        [
            {"block": "trades", "scope": "file", "status": "good", "count": counts["good"], "pct": pct(counts["good"], total)},
            {
                "block": "trades",
                "scope": "file",
                "status": "recoverable_with_flag",
                "count": strict_recovered_review + counts["review_microstructure"] + counts["review_no_1m_reference"] + counts["review_1m_reference_alignment"],
                "pct": pct(strict_recovered_review + counts["review_microstructure"] + counts["review_no_1m_reference"] + counts["review_1m_reference_alignment"], total),
            },
            {
                "block": "trades",
                "scope": "file",
                "status": "review_not_rehabilitated",
                "count": residual_review + counts["reference_scale_mismatch"],
                "pct": pct(residual_review + counts["reference_scale_mismatch"], total),
            },
            {"block": "trades", "scope": "file", "status": "bad", "count": counts["bad_data"], "pct": pct(counts["bad_data"], total)},
        ]
    )
    return {"trades_raw_labels": raw, "trades_final_recovery": recovery}


def build_halts_tables() -> dict[str, pd.DataFrame]:
    event_tax = pd.read_parquet(AUDIT_ROOT / "halts" / "cache_v2" / "event_taxonomy_summary.parquet")
    event_tax["block"] = "halts"
    event_tax["scope"] = "canonical_event"
    event_tax["pct"] = event_tax["events"].map(lambda x: pct(x, int(event_tax["events"].sum())))
    event_tax = event_tax.rename(columns={"event_taxonomy": "status", "events": "count"})

    lt1b = pd.read_parquet(AUDIT_ROOT / "halts" / "cache_v2" / "halts_lt1b_event_index.parquet", columns=["event_taxonomy"])
    vc = lt1b["event_taxonomy"].astype(str).value_counts(dropna=False)
    lt1b_df = pd.DataFrame(
        [{"block": "halts", "scope": "lt1b_event", "status": k, "count": int(v), "pct": pct(v, int(vc.sum()))} for k, v in vc.items()]
    )

    visual = pd.read_parquet(AUDIT_ROOT / "halts" / "cache_v2" / "halts_quotes_trades_visual_cases.parquet", columns=["visual_case_bucket"])
    vv = visual["visual_case_bucket"].astype(str).value_counts(dropna=False)
    visual_df = pd.DataFrame(
        [{"block": "halts", "scope": "visual_case", "status": k, "count": int(v), "pct": pct(v, int(vv.sum()))} for k, v in vv.items()]
    )
    return {"halts_event_taxonomy": event_tax, "halts_lt1b_event_taxonomy": lt1b_df, "halts_visual_cases": visual_df}


def build_reference_tables() -> dict[str, pd.DataFrame]:
    ident = pd.read_parquet(AUDIT_ROOT / "reference" / "cache_v2" / "reference_identity_quality_summary.parquet")
    ident["block"] = "reference"
    ident["scope"] = "identity_row"
    ident["pct"] = ident["rows"].map(lambda x: pct(x, int(ident["rows"].sum())))
    ident = ident.rename(columns={"identity_bucket": "status", "rows": "count"})

    causal = pd.read_parquet(AUDIT_ROOT / "reference" / "cache_v2" / "reference_causal_alignment_summary.parquet")
    causal["block"] = "reference"
    causal["scope"] = causal["causal_domain"]
    causal["pct_within_scope"] = causal.groupby("causal_domain")["rows"].transform(lambda s: (100.0 * s / s.sum()).round(6))
    causal = causal.rename(columns={"bucket": "status", "rows": "count"})
    return {"reference_identity": ident, "reference_causal": causal}


def build_short_tables() -> dict[str, pd.DataFrame]:
    provider = pd.read_parquet(AUDIT_ROOT / "short" / "cache_v2" / "short_provider_comparison_summary.parquet")
    meaningful = pd.read_parquet(AUDIT_ROOT / "short" / "cache_v2" / "short_only_polygon_tickers.parquet")
    rows = []
    for dataset in sorted(provider["dataset"].dropna().unique()):
        sub = provider[provider["dataset"] == dataset].copy()
        rows.append(
            {
                "block": "short",
                "dataset": dataset,
                "polygon_present_rows": int(sub["present_polygon"].sum()),
                "finra_present_rows": int(sub["present_finra"].sum()),
                "raw_only_polygon_rows": int(sub["only_polygon"].sum()),
                "meaningful_only_polygon_rows": int(((meaningful["dataset"] == dataset) & (meaningful["poly_rows"].fillna(0) > 0)).sum()),
                "zero_row_only_polygon_rows": int(((meaningful["dataset"] == dataset) & (meaningful["poly_rows"].fillna(0) == 0)).sum()),
            }
        )
    provider_df = pd.DataFrame(rows)

    causal = pd.read_parquet(AUDIT_ROOT / "short" / "cache_v2" / "short_causal_alignment_summary.parquet")
    causal["block"] = "short"
    causal["scope"] = "short_volume_context"
    causal["pct"] = causal["cases"].map(lambda x: pct(x, int(causal["cases"].sum())))
    causal = causal.rename(columns={"market_link_bucket": "status", "cases": "count"})

    si = pd.read_parquet(AUDIT_ROOT / "short" / "cache_v2" / "short_interest_context_summary.parquet")
    si["block"] = "short"
    si["scope"] = "short_interest_context"
    si["pct"] = si["cases"].map(lambda x: pct(x, int(si["cases"].sum())))
    si = si.rename(columns={"context_bucket": "status", "cases": "count"})
    return {"short_provider_baseline": provider_df, "short_volume_context": causal, "short_interest_context": si}


def build_additional_tables() -> dict[str, pd.DataFrame]:
    cov = pd.read_parquet(AUDIT_ROOT / "additional" / "cache_v2" / "additional_effective_coverage_summary.parquet")
    cov = cov.loc[:, ["dataset", "dataset_family", "effective_non_empty_pct", "files_non_empty", "files_present", "rows_total"]].copy()
    cov["block"] = "additional"

    news = pd.read_parquet(AUDIT_ROOT / "additional" / "cache_v2" / "additional_news_link_summary.parquet")
    news["block"] = "additional"
    news["scope"] = "news_event"
    news["pct"] = news["events"].map(lambda x: pct(x, int(news["events"].sum())))
    news = news.rename(columns={"news_link_bucket": "status", "events": "count"})

    ipo = pd.read_parquet(AUDIT_ROOT / "additional" / "cache_v2" / "additional_ipo_link_summary.parquet")
    ipo["block"] = "additional"
    ipo["scope"] = "ipo_event"
    ipo["pct"] = ipo["events"].map(lambda x: pct(x, int(ipo["events"].sum())))
    ipo = ipo.rename(columns={"ipo_link_bucket": "status", "events": "count"})

    corp = pd.read_parquet(AUDIT_ROOT / "additional" / "cache_v2" / "additional_corp_actions_reference_overlap_summary.parquet")
    corp["block"] = "additional"
    corp["scope"] = corp["dataset"]
    corp["pct_within_dataset"] = corp.groupby("dataset")["rows"].transform(lambda s: (100.0 * s / s.sum()).round(6))
    corp = corp.rename(columns={"overlap_bucket": "status", "rows": "count"})
    return {"additional_coverage": cov, "additional_news": news, "additional_ipos": ipo, "additional_corp_overlap": corp}


def plot_major_quality_mix(datasets: dict[str, pd.DataFrame]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    daily = datasets["daily_quality"].pivot(index="block", columns="status", values="pct").fillna(0)
    daily.plot(kind="barh", stacked=True, ax=axes[0, 0], color=["#4daf4a", "#e41a1c"])
    axes[0, 0].set_title("Daily Quality Mix (%)")
    axes[0, 0].set_xlabel("Percent")

    m1 = datasets["1m_operational"].copy()
    axes[0, 1].barh(m1["status"], m1["pct"], color=["#377eb8", "#66c2a5", "#ff7f00", "#e41a1c"])
    axes[0, 1].set_title("1m Operational Decisions (%)")
    axes[0, 1].set_xlabel("Percent")

    trades = datasets["trades_final_recovery"].copy()
    axes[1, 0].barh(trades["status"], trades["pct"], color=["#4daf4a", "#377eb8", "#ff7f00", "#e41a1c"])
    axes[1, 0].set_title("Trades Final Recovery Policy (%)")
    axes[1, 0].set_xlabel("Percent")

    halts = datasets["halts_lt1b_event_taxonomy"].copy().sort_values("pct", ascending=True)
    axes[1, 1].barh(halts["status"], halts["pct"], color="#377eb8")
    axes[1, 1].set_title("Halts LT1B Event Taxonomy (%)")
    axes[1, 1].set_xlabel("Percent")

    plt.tight_layout()
    fig.savefig(IMG_DIR / "01_major_quality_mix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_context_blocks(datasets: dict[str, pd.DataFrame]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ref = datasets["reference_identity"].sort_values("pct", ascending=True)
    axes[0, 0].barh(ref["status"], ref["pct"], color="#377eb8")
    axes[0, 0].set_title("Reference Identity Quality (%)")
    axes[0, 0].set_xlabel("Percent")

    short = datasets["short_provider_baseline"].copy()
    x = range(len(short))
    axes[0, 1].bar([i - 0.18 for i in x], short["polygon_present_rows"], width=0.36, label="Polygon", color="#ff7f00")
    axes[0, 1].bar([i + 0.18 for i in x], short["finra_present_rows"], width=0.36, label="FINRA", color="#4daf4a")
    axes[0, 1].set_xticks(list(x))
    axes[0, 1].set_xticklabels(short["dataset"])
    axes[0, 1].set_title("Short Provider Coverage (rows)")
    axes[0, 1].legend()

    news = datasets["additional_news"].sort_values("pct", ascending=True)
    axes[1, 0].barh(news["status"], news["pct"], color="#984ea3")
    axes[1, 0].set_title("Additional News Buckets (%)")
    axes[1, 0].set_xlabel("Percent")

    ipo = datasets["additional_ipos"].sort_values("pct", ascending=True)
    axes[1, 1].barh(ipo["status"], ipo["pct"], color="#a65628")
    axes[1, 1].set_title("Additional IPO Buckets (%)")
    axes[1, 1].set_xlabel("Percent")

    plt.tight_layout()
    fig.savefig(IMG_DIR / "02_context_blocks.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def df_to_md_table(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    rows = []
    rows.append("| " + " | ".join(cols) + " |")
    rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        vals = []
        for c in df.columns:
            v = row[c]
            if pd.isna(v):
                vals.append("")
            else:
                vals.append(str(v))
        rows.append("| " + " | ".join(vals) + " |")
    return "\n".join(rows)


def build_markdown(datasets: dict[str, pd.DataFrame]) -> None:
    lines: list[str] = ["# Global Metrics Tables", ""]
    ordered = [
        "daily_quality",
        "daily_coverage",
        "1m_operational",
        "quotes_core_mix",
        "quotes_open_buckets",
        "trades_final_recovery",
        "halts_lt1b_event_taxonomy",
        "reference_identity",
        "short_provider_baseline",
        "additional_coverage",
        "additional_news",
        "additional_ipos",
    ]
    for name in ordered:
        df = datasets[name]
        lines.append(f"## {name}")
        lines.append("")
        lines.append(df_to_md_table(df))
        lines.append("")
    lines.append("## Figures")
    lines.append("")
    lines.append("- [01_major_quality_mix.png](C:\\TSIS_Data\\v1\\backtest_SmallCaps\\data_auditoria_polygon\\00_data_certification\\certification\\global_metrics\\img\\01_major_quality_mix.png)")
    lines.append("- [02_context_blocks.png](C:\\TSIS_Data\\v1\\backtest_SmallCaps\\data_auditoria_polygon\\00_data_certification\\certification\\global_metrics\\img\\02_context_blocks.png)")
    (OUT_DIR / "00_global_metrics_tables.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    datasets: dict[str, pd.DataFrame] = {}
    for builder in [
        build_daily_tables,
        build_1m_tables,
        build_quotes_tables,
        build_trades_tables,
        build_halts_tables,
        build_reference_tables,
        build_short_tables,
        build_additional_tables,
    ]:
        datasets.update(builder())

    for name, df in datasets.items():
        write_df(df, name)

    plot_major_quality_mix(datasets)
    plot_context_blocks(datasets)
    build_markdown(datasets)

    manifest = {
        "artifacts": sorted([p.name for p in OUT_DIR.iterdir() if p.is_file()]),
        "figures": sorted([p.name for p in IMG_DIR.iterdir() if p.is_file()]),
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
