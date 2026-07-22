from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_DATA_FOUNDATION")
FOUNDATIONS_ROOT = PROJECT_ROOT / "01_foundations"
DOSSIER_ROOT = FOUNDATIONS_ROOT / "inspection_dossiers" / "additional"
OUT_ROOT = DOSSIER_ROOT / "evidence_assets"

HISTORICAL_ADDITIONAL_ROOT = (
    PROJECT_ROOT
    / "01_research"
    / "01_auditoria_RAW_DATA"
    / "00_data_certification"
    / "auditoria"
    / "additional"
)
HISTORICAL_CACHE = HISTORICAL_ADDITIONAL_ROOT / "cache_v2"
RUN_AUDIT_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "additional_audit"
    / "20260405_additional_lt1b_coverage"
)
DOWNLOAD_TICKER_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "additional_downloads"
    / "20260405_full_refresh_ticker_based"
)
DOWNLOAD_MACRO_ROOT = (
    PROJECT_ROOT
    / "runs"
    / "backtest"
    / "additional_downloads"
    / "20260405_full_refresh_macro"
)
ACTIVE_DATA_ROOT = Path(r"E:\TSIS\data\additional")

EXPECTED_SUBROOTS = ["financials", "corporate_actions", "economic", "ipos", "news"]

DATASET_PROFILES: dict[str, dict[str, str]] = {
    "income_statements": {
        "raw_vendor_role": "RAW vendor fundamentals/context",
        "quality_state": "good_context_candidate",
        "master_table_destination": "master_daily_table context; data_quality_report",
        "validator_focus": "filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity",
        "forbidden_interpretation": "Do not treat filing-period facts as decision-time fields without point-in-time filing logic.",
    },
    "balance_sheets": {
        "raw_vendor_role": "RAW vendor fundamentals/context",
        "quality_state": "good_context_candidate",
        "master_table_destination": "master_daily_table context; symbol_master; data_quality_report",
        "validator_focus": "filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity",
        "forbidden_interpretation": "Do not treat balance-sheet fields as always-known on period_end.",
    },
    "cash_flow_statements": {
        "raw_vendor_role": "RAW vendor fundamentals/context",
        "quality_state": "good_context_candidate",
        "master_table_destination": "master_daily_table context; data_quality_report",
        "validator_focus": "filing_date, period_end, fiscal_year, fiscal_quarter, ticker identity",
        "forbidden_interpretation": "Do not use as alpha-ready features without point-in-time filing availability.",
    },
    "ratios": {
        "raw_vendor_role": "RAW vendor ratios/context",
        "quality_state": "review_sparse_snapshot",
        "master_table_destination": "data_quality_report; deferred context only",
        "validator_focus": "date key, sparsity, denominator sanity, vendor derivation caveat",
        "forbidden_interpretation": "Do not promote to primary ML feature layer from coverage alone.",
    },
    "news": {
        "raw_vendor_role": "RAW vendor news/event context",
        "quality_state": "good_review_attribution_aware",
        "master_table_destination": "master_daily_table news_flag; event/context table; data_quality_report",
        "validator_focus": "published_utc, ticker attribution, multi-ticker ambiguity, timezone",
        "forbidden_interpretation": "Do not read requested ticker as sole causal subject when article tickers are multi-name.",
    },
    "ipos": {
        "raw_vendor_role": "RAW vendor IPO/event context",
        "quality_state": "good_review_sparse_event",
        "master_table_destination": "symbol_master listing context; master_daily_table ipo_age/ipo_flag; data_quality_report",
        "validator_focus": "listing_date, announced_date fallback, issuer identity, sparse expected coverage",
        "forbidden_interpretation": "Do not treat sparse IPO files as missing-data failure for mature tickers.",
    },
    "dividends": {
        "raw_vendor_role": "RAW vendor corporate-action context",
        "quality_state": "review_secondary_to_reference",
        "master_table_destination": "corporate_actions_table reconciliation; data_quality_report",
        "validator_focus": "reference overlap, ex_dividend_date, id, cash amount",
        "forbidden_interpretation": "Do not override reference dividends without reconciliation.",
    },
    "splits": {
        "raw_vendor_role": "RAW vendor corporate-action context",
        "quality_state": "review_secondary_to_reference",
        "master_table_destination": "corporate_actions_table reconciliation; data_quality_report",
        "validator_focus": "reference overlap, execution_date, split ratio, id",
        "forbidden_interpretation": "Do not adjust prices from additional splits when reference disagrees.",
    },
    "ticker_events": {
        "raw_vendor_role": "RAW vendor corporate-event context",
        "quality_state": "review_secondary_to_reference",
        "master_table_destination": "event/reference reconciliation; data_quality_report",
        "validator_focus": "event taxonomy, date key, reference reconciliation",
        "forbidden_interpretation": "Do not treat ticker_events as canonical identity/corporate-action authority.",
    },
    "inflation": {
        "raw_vendor_role": "RAW vendor macro context",
        "quality_state": "good_macro_context",
        "master_table_destination": "calendar_table macro context; data_quality_report",
        "validator_focus": "date continuity, release/calendar semantics, macro-only scope",
        "forbidden_interpretation": "Do not claim ticker-level causality from macro-date presence.",
    },
    "inflation_expectations": {
        "raw_vendor_role": "RAW vendor macro context",
        "quality_state": "good_macro_context",
        "master_table_destination": "calendar_table macro context; data_quality_report",
        "validator_focus": "date continuity, release/calendar semantics, macro-only scope",
        "forbidden_interpretation": "Do not claim ticker-level causality from macro-date presence.",
    },
    "treasury_yields": {
        "raw_vendor_role": "RAW vendor macro context",
        "quality_state": "good_macro_context",
        "master_table_destination": "calendar_table macro context; data_quality_report",
        "validator_focus": "date continuity, curve fields, macro-only scope",
        "forbidden_interpretation": "Do not claim ticker-level causality from macro-date presence.",
    },
}


def _ensure_dirs() -> None:
    for path in [
        OUT_ROOT / "historical_cache_inventory",
        OUT_ROOT / "download_inventory",
        OUT_ROOT / "physical_root_audit",
        OUT_ROOT / "quality_tables",
        OUT_ROOT / "reference_reconciliation",
        OUT_ROOT / "news_attribution",
        OUT_ROOT / "ipo_context",
        OUT_ROOT / "visual_overview",
        DOSSIER_ROOT / "good_justification",
        DOSSIER_ROOT / "flagged_case_evidence_packs",
        DOSSIER_ROOT / "coverage_case_evidence_packs",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "_No rows available._"
    view = df.head(max_rows).copy()
    for col in view.columns:
        view[col] = view[col].map(_stringify_cell)
    headers = [str(col) for col in view.columns]
    rows = view.astype(str).values.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        safe_row = [cell.replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(safe_row) + " |")
    return "\n".join(lines)


def _stringify_cell(value: Any) -> str:
    if isinstance(value, (list, tuple, set)):
        return ", ".join(map(str, value))
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, dict):
        text = json.dumps(value, sort_keys=True)
    else:
        text = str(value)
    text = text.replace("\n", " ")
    return text[:180] + "..." if len(text) > 180 else text


def _write_csv_and_md(df: pd.DataFrame, csv_path: Path, md_path: Path, title: str, note: str = "") -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    body = [f"# {title}", ""]
    if note:
        body.extend([note, ""])
    body.extend([_md_table(df), ""])
    md_path.write_text("\n".join(body), encoding="utf-8")


def build_historical_cache_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if HISTORICAL_CACHE.exists():
        for path in sorted(HISTORICAL_CACHE.iterdir()):
            if path.is_file():
                rows.append(
                    {
                        "artifact": path.name,
                        "relative_path": _rel(path),
                        "suffix": path.suffix.lower(),
                        "size_bytes": path.stat().st_size,
                        "sha256": _sha256(path),
                    }
                )
    img_root = HISTORICAL_ADDITIONAL_ROOT / "img"
    if img_root.exists():
        for path in sorted(img_root.glob("*.png")):
            rows.append(
                {
                    "artifact": path.name,
                    "relative_path": _rel(path),
                    "suffix": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    df = pd.DataFrame(rows)
    _write_csv_and_md(
        df,
        OUT_ROOT / "historical_cache_inventory" / "additional_historical_cache_inventory_v0_2.csv",
        OUT_ROOT / "historical_cache_inventory" / "additional_historical_cache_inventory_v0_2.md",
        "Additional Historical Cache Inventory v0.2",
        "Inventory of preserved historical audit artifacts used as upstream evidence. These files are read-only evidence; this builder does not modify them.",
    )
    return df


def build_download_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label, root in [("ticker_based", DOWNLOAD_TICKER_ROOT), ("macro", DOWNLOAD_MACRO_ROOT)]:
        summary = _read_json(root / "download_summary.json")
        manifest_csv = root / "download_manifest.csv"
        manifest_parquet = root / "download_manifest.parquet"
        rows.append(
            {
                "download_family": label,
                "root": _rel(root),
                "root_exists": root.exists(),
                "summary_exists": bool(summary),
                "manifest_csv_exists": manifest_csv.exists(),
                "manifest_parquet_exists": manifest_parquet.exists(),
                "summary_keys": ", ".join(sorted(summary.keys())) if summary else "",
                "summary_sha256": _sha256(root / "download_summary.json"),
                "manifest_csv_sha256": _sha256(manifest_csv),
                "manifest_parquet_sha256": _sha256(manifest_parquet),
            }
        )
    df = pd.DataFrame(rows)
    _write_csv_and_md(
        df,
        OUT_ROOT / "download_inventory" / "additional_download_inventory_v0_2.csv",
        OUT_ROOT / "download_inventory" / "additional_download_inventory_v0_2.md",
        "Additional Download Inventory v0.2",
        "Download manifests that prove materialization provenance for the Additional block.",
    )
    return df


def build_physical_root_audit() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for subroot in EXPECTED_SUBROOTS:
        path = ACTIVE_DATA_ROOT / subroot
        parquet_count = sum(1 for _ in path.rglob("*.parquet")) if path.exists() else 0
        rows.append(
            {
                "expected_subroot": subroot,
                "active_path": str(path).replace("\\", "/"),
                "exists": path.exists(),
                "parquet_files_detected": parquet_count,
                "interpretation": "present" if path.exists() else "missing_or_not_mounted",
            }
        )
    df = pd.DataFrame(rows)
    _write_csv_and_md(
        df,
        OUT_ROOT / "physical_root_audit" / "additional_physical_root_audit_v0_2.csv",
        OUT_ROOT / "physical_root_audit" / "additional_physical_root_audit_v0_2.md",
        "Additional Physical Root Audit v0.2",
        "Light physical check of the active `E:/TSIS/data/additional` root. Coverage authority remains the run evidence and historical cache.",
    )
    return df


def build_quality_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    coverage = _read_parquet(HISTORICAL_CACHE / "additional_effective_coverage_summary.parquet")
    if coverage.empty:
        coverage = pd.concat(
            [
                _read_parquet(RUN_AUDIT_ROOT / "additional_ticker_datasets_summary.parquet"),
                _read_parquet(RUN_AUDIT_ROOT / "additional_macro_datasets_summary.parquet"),
            ],
            ignore_index=True,
        )
    rows: list[dict[str, Any]] = []
    for _, row in coverage.iterrows():
        dataset = str(row.get("dataset", ""))
        profile = DATASET_PROFILES.get(dataset, {})
        rows.append(
            {
                "dataset": dataset,
                "dataset_family": row.get("dataset_family", ""),
                "dataset_kind": row.get("dataset_kind", ""),
                "raw_vendor_role": profile.get("raw_vendor_role", "RAW vendor context"),
                "quality_state": profile.get("quality_state", "review"),
                "master_table_destination": profile.get("master_table_destination", "data_quality_report"),
                "validator_focus": profile.get("validator_focus", "schema, identity, coverage, semantics"),
                "files_present": row.get("files_present", ""),
                "files_non_empty": row.get("files_non_empty", ""),
                "coverage_non_empty_pct": row.get("coverage_non_empty_pct", ""),
                "rows_total": row.get("rows_total", row.get("effective_rows_total", "")),
                "date_min": row.get("date_min", ""),
                "date_max": row.get("date_max", ""),
                "forbidden_interpretation": profile.get("forbidden_interpretation", "Do not consume as uniform dataset."),
            }
        )
    quality_df = pd.DataFrame(rows)
    quality_order = [
        "income_statements",
        "balance_sheets",
        "cash_flow_statements",
        "ratios",
        "news",
        "ipos",
        "dividends",
        "splits",
        "ticker_events",
        "inflation",
        "inflation_expectations",
        "treasury_yields",
    ]
    quality_df["order"] = quality_df["dataset"].map({name: idx for idx, name in enumerate(quality_order)})
    quality_df = quality_df.sort_values(["order", "dataset"]).drop(columns=["order"]).reset_index(drop=True)

    _write_csv_and_md(
        quality_df,
        OUT_ROOT / "quality_tables" / "additional_subfamily_quality_table_v0_2.csv",
        OUT_ROOT / "quality_tables" / "additional_subfamily_quality_table_v0_2.md",
        "Additional Subfamily Quality Table v0.2",
        "Quality table for CAPA 1. It separates RAW vendor provenance from functional role, audit state and table destination.",
    )

    readiness_rows = [
        {
            "target_table": "data_quality_report",
            "additional_role": "subfamily quality flags, coverage state, attribution risk, reference overlap",
            "readiness": "ready_for_contextual_quality_columns",
            "blocking_limit": "Not a single uniform dataset; each subfamily must keep its state.",
        },
        {
            "target_table": "master_daily_table",
            "additional_role": "news_flag, IPO age/listing context, financial context with filing-date guardrails, macro day overlays",
            "readiness": "partial_context_ready",
            "blocking_limit": "No direct alpha/feature promotion without point-in-time and attribution controls.",
        },
        {
            "target_table": "master_intraday_table",
            "additional_role": "event-time context for news/IPO/macro calendar only",
            "readiness": "indirect_context_only",
            "blocking_limit": "Does not replace quotes, trades or 1m intraday market evidence.",
        },
        {
            "target_table": "symbol_master",
            "additional_role": "issuer/listing/fundamental identity context",
            "readiness": "partial_context_ready",
            "blocking_limit": "Reference identity remains primary authority.",
        },
        {
            "target_table": "corporate_actions_table",
            "additional_role": "secondary reconciliation for dividends, splits and ticker_events",
            "readiness": "secondary_reconciliation_only",
            "blocking_limit": "Reference corporate actions remain primary authority.",
        },
        {
            "target_table": "calendar_table",
            "additional_role": "macro date series for inflation, expectations and treasury yields",
            "readiness": "macro_context_ready",
            "blocking_limit": "Macro presence is not ticker-level causality.",
        },
    ]
    readiness_df = pd.DataFrame(readiness_rows)
    _write_csv_and_md(
        readiness_df,
        OUT_ROOT / "quality_tables" / "additional_master_table_readiness_v0_1.csv",
        OUT_ROOT / "quality_tables" / "additional_master_table_readiness_v0_1.md",
        "Additional Master Table Readiness v0.1",
        "How Additional may feed CAPA 1 outputs without displacing raw market data or reference authority.",
    )
    return quality_df, readiness_df


def build_reference_reconciliation() -> pd.DataFrame:
    df = _read_parquet(HISTORICAL_CACHE / "additional_corp_actions_reference_overlap_summary.parquet")
    if not df.empty:
        df = df.copy()
        df["institutional_reading"] = df["overlap_bucket"].map(
            {
                "reference_exact_overlap": "secondary confirmation; reference remains primary",
                "reference_present_no_exact_overlap": "review queue; do not override reference",
            }
        ).fillna("review")
    _write_csv_and_md(
        df,
        OUT_ROOT / "reference_reconciliation" / "additional_corporate_actions_reference_reconciliation_v0_1.csv",
        OUT_ROOT / "reference_reconciliation" / "additional_corporate_actions_reference_reconciliation_v0_1.md",
        "Additional Corporate Actions Reference Reconciliation v0.1",
        "Reference reconciliation summary for Additional corporate-action subfamilies.",
    )
    return df


def build_news_attribution_assets() -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = _read_parquet(HISTORICAL_CACHE / "additional_news_link_summary.parquet")
    multi = _read_parquet(HISTORICAL_CACHE / "additional_news_multi_ticker_summary.parquet")
    if not summary.empty:
        summary = summary.copy()
        summary["institutional_reading"] = summary["news_link_bucket"].map(
            {
                "review_multi_ticker_ambiguous_news": "high attribution risk; context only unless ticker attribution is explicit",
                "news_near_market_anomaly": "candidate event context with market evidence; still not causal proof",
                "news_context_only": "contextual news without nearby market anomaly",
                "news_near_halt_market_event": "strongest contextual bucket; halt/event evidence required",
                "news_near_short_flow_only": "short-flow context only; not price authority",
            }
        ).fillna("review")
    _write_csv_and_md(
        summary,
        OUT_ROOT / "news_attribution" / "additional_news_attribution_quality_v0_1.csv",
        OUT_ROOT / "news_attribution" / "additional_news_attribution_quality_v0_1.md",
        "Additional News Attribution Quality v0.1",
        "News bucket quality summary. Multi-ticker ambiguity is an institutional restriction, not a corruption finding.",
    )
    if not multi.empty:
        multi = multi.sort_values(["max_tickers_per_news", "mean_tickers_per_news"], ascending=False)
    _write_csv_and_md(
        multi.head(25),
        OUT_ROOT / "news_attribution" / "additional_news_multi_ticker_examples_v0_1.csv",
        OUT_ROOT / "news_attribution" / "additional_news_multi_ticker_examples_v0_1.md",
        "Additional News Multi-Ticker Examples v0.1",
        "Examples proving why requested ticker is not always enough to infer causal attribution.",
    )
    return summary, multi


def build_ipo_context_assets() -> pd.DataFrame:
    df = _read_parquet(HISTORICAL_CACHE / "additional_ipo_link_summary.parquet")
    if not df.empty:
        df = df.copy()
        df["institutional_reading"] = df["ipo_link_bucket"].map(
            {
                "ipo_near_market_anomaly": "candidate early-life event context",
                "ipo_market_clean": "sparse valid IPO context without nearby anomaly",
                "ipo_near_halt_market_event": "strong IPO/halt context; requires event-aware handling",
            }
        ).fillna("review")
    _write_csv_and_md(
        df,
        OUT_ROOT / "ipo_context" / "additional_ipo_context_quality_v0_1.csv",
        OUT_ROOT / "ipo_context" / "additional_ipo_context_quality_v0_1.md",
        "Additional IPO Context Quality v0.1",
        "IPO context buckets and their permitted institutional reading.",
    )
    return df


def build_casepacks(quality_df: pd.DataFrame) -> None:
    financials = quality_df[quality_df["dataset"].isin(["income_statements", "balance_sheets", "cash_flow_statements"])]
    (DOSSIER_ROOT / "good_justification" / "additional_financials_core_good_cases_v0_1.md").write_text(
        "\n".join(
            [
                "# Additional Financials Core Good Cases v0.1",
                "",
                "Financial statement subfamilies are the strongest Additional ticker-based block.",
                "",
                _md_table(
                    financials[
                        [
                            "dataset",
                            "files_present",
                            "files_non_empty",
                            "coverage_non_empty_pct",
                            "rows_total",
                            "validator_focus",
                            "forbidden_interpretation",
                        ]
                    ]
                ),
                "",
                "Institutional reading:",
                "",
                "- Coverage is high enough for contextual audit use.",
                "- The mandatory guardrail is point-in-time filing availability.",
                "- These files can inform CAPA 1 quality/context tables, but they are not alpha features by default.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    news_candidates = _read_parquet(HISTORICAL_CACHE / "additional_news_market_link_candidates.parquet")
    if not news_candidates.empty:
        cols = [
            "ticker",
            "news_date",
            "publisher_name",
            "title",
            "n_tickers",
            "quotes_severity",
            "trades_severity",
            "news_link_bucket",
        ]
        samples = (
            news_candidates[cols]
            .sort_values(["news_link_bucket", "n_tickers"], ascending=[True, False])
            .groupby("news_link_bucket", as_index=False)
            .head(3)
        )
        samples["title"] = samples["title"].astype(str).str.slice(0, 120)
    else:
        samples = pd.DataFrame()
    (DOSSIER_ROOT / "flagged_case_evidence_packs" / "additional_news_attribution_review_cases_v0_1.md").write_text(
        "\n".join(
            [
                "# Additional News Attribution Review Cases v0.1",
                "",
                "These rows are not bad data by default. They prove why `news` requires attribution flags before consumption.",
                "",
                _md_table(samples, max_rows=20),
                "",
                "Institutional reading:",
                "",
                "- `published_utc` and `news_date` make this useful for event context.",
                "- `n_tickers` and multi-name articles prevent naive ticker causality.",
                "- Market evidence can support a context label, but it does not prove the news caused the move.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    corp = _read_parquet(HISTORICAL_CACHE / "additional_corp_actions_reference_overlap_summary.parquet")
    (DOSSIER_ROOT / "flagged_case_evidence_packs" / "additional_corporate_actions_reference_review_v0_1.md").write_text(
        "\n".join(
            [
                "# Additional Corporate Actions Reference Review v0.1",
                "",
                "`additional/corporate_actions` is RAW vendor context, but not primary authority for adjustment.",
                "",
                _md_table(corp, max_rows=20),
                "",
                "Institutional reading:",
                "",
                "- Exact reference overlap can be used as secondary confirmation.",
                "- Non-overlap is a review queue, not permission to overwrite reference.",
                "- CAPA 1 `corporate_actions_table` must keep reference as primary source until a separate reconciliation promotion exists.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    sparse = quality_df[quality_df["quality_state"].isin(["review_sparse_snapshot", "good_review_sparse_event"])]
    (DOSSIER_ROOT / "coverage_case_evidence_packs" / "additional_sparse_valid_context_cases_v0_1.md").write_text(
        "\n".join(
            [
                "# Additional Sparse Valid Context Cases v0.1",
                "",
                "Some Additional subfamilies are expected to be sparse. Sparse does not automatically mean broken.",
                "",
                _md_table(
                    sparse[
                        [
                            "dataset",
                            "quality_state",
                            "files_present",
                            "files_non_empty",
                            "coverage_non_empty_pct",
                            "master_table_destination",
                            "forbidden_interpretation",
                        ]
                    ],
                    max_rows=20,
                ),
                "",
                "Institutional reading:",
                "",
                "- IPO and ratios coverage must be interpreted by expectedness, not by file presence alone.",
                "- Sparse context can still support `data_quality_report` and selected master-table fields.",
                "- It cannot be promoted as broad feature coverage without a later point-in-time validator.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_visuals(quality_df: pd.DataFrame, readiness_df: pd.DataFrame) -> None:
    visual_dir = OUT_ROOT / "visual_overview"
    ticker_df = quality_df[pd.to_numeric(quality_df["coverage_non_empty_pct"], errors="coerce").notna()].copy()
    ticker_df["coverage_non_empty_pct"] = pd.to_numeric(ticker_df["coverage_non_empty_pct"], errors="coerce")
    ticker_df = ticker_df.sort_values("coverage_non_empty_pct", ascending=True)
    if not ticker_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(ticker_df["dataset"], ticker_df["coverage_non_empty_pct"], color="#4c78a8")
        ax.set_xlabel("Non-empty coverage pct")
        ax.set_title("Additional coverage by subfamily")
        ax.set_xlim(0, 105)
        for idx, value in enumerate(ticker_df["coverage_non_empty_pct"]):
            ax.text(value + 1, idx, f"{value:.1f}%", va="center", fontsize=8)
        fig.tight_layout()
        fig.savefig(visual_dir / "additional_coverage_by_dataset_v0_2.png", dpi=160)
        plt.close(fig)

    counts = quality_df.groupby("quality_state", dropna=False).size().reset_index(name="datasets")
    if not counts.empty:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(counts["quality_state"], counts["datasets"], color="#59a14f")
        ax.set_ylabel("Datasets")
        ax.set_title("Additional institutional quality states")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        fig.savefig(visual_dir / "additional_quality_role_by_family_v0_2.png", dpi=160)
        plt.close(fig)

    readout = [
        "# Additional Visual Overview v0.2",
        "",
        "Generated visual assets:",
        "",
        "- `additional_coverage_by_dataset_v0_2.png`",
        "- `additional_quality_role_by_family_v0_2.png`",
        "",
        "These images summarize coverage and quality roles. They are not a substitute for the subfamily contracts or validators.",
        "",
        "## Master table readiness",
        "",
        _md_table(readiness_df, max_rows=20),
        "",
    ]
    (visual_dir / "additional_visual_overview_v0_2.md").write_text("\n".join(readout), encoding="utf-8")


def write_readout(
    quality_df: pd.DataFrame,
    readiness_df: pd.DataFrame,
    reconciliation_df: pd.DataFrame,
    news_summary: pd.DataFrame,
    ipo_summary: pd.DataFrame,
) -> None:
    lines = [
        "# Additional Inspection Readout v0.2",
        "",
        "## Scope",
        "",
        "`additional_v0_1` is RAW vendor context data from Polygon. It includes financials, corporate actions, economic/macro series, IPOs and news.",
        "",
        "This readout does not promote Additional into core market data. It promotes the inspection package that explains how Additional contributes to CAPA 1 data-quality and master-table design.",
        "",
        "## Verdict",
        "",
        "Additional is institutional as a governed RAW vendor context block with subfamily-specific restrictions.",
        "",
        "It must not be consumed as one uniform dataset. Its subfamilies feed quality/context tables differently:",
        "",
        _md_table(readiness_df, max_rows=20),
        "",
        "## Subfamily quality table",
        "",
        _md_table(
            quality_df[
                [
                    "dataset",
                    "dataset_family",
                    "quality_state",
                    "coverage_non_empty_pct",
                    "rows_total",
                    "master_table_destination",
                ]
            ],
            max_rows=30,
        ),
        "",
        "## Corporate actions reconciliation",
        "",
        _md_table(reconciliation_df, max_rows=20),
        "",
        "## News attribution",
        "",
        _md_table(news_summary, max_rows=20),
        "",
        "## IPO context",
        "",
        _md_table(ipo_summary, max_rows=20),
        "",
        "## Core restrictions",
        "",
        "- `reference` remains the primary authority for identity and corporate actions.",
        "- `daily`, `quotes`, `trades` and `ohlcv_1m` remain the primary raw market-data authorities.",
        "- Additional financials require point-in-time filing logic before feature use.",
        "- News requires ticker-attribution and timestamp guardrails.",
        "- Macro/economic series can populate calendar context, not ticker-level causal proof.",
        "",
        "## Evidence assets",
        "",
        "- `evidence_assets/quality_tables/additional_subfamily_quality_table_v0_2.csv`",
        "- `evidence_assets/quality_tables/additional_master_table_readiness_v0_1.csv`",
        "- `evidence_assets/reference_reconciliation/additional_corporate_actions_reference_reconciliation_v0_1.csv`",
        "- `evidence_assets/news_attribution/additional_news_attribution_quality_v0_1.csv`",
        "- `evidence_assets/ipo_context/additional_ipo_context_quality_v0_1.csv`",
        "- `evidence_assets/visual_overview/additional_coverage_by_dataset_v0_2.png`",
        "- `evidence_assets/visual_overview/additional_quality_role_by_family_v0_2.png`",
        "",
        "## Human casepacks",
        "",
        "- `good_justification/additional_financials_core_good_cases_v0_1.md`",
        "- `flagged_case_evidence_packs/additional_news_attribution_review_cases_v0_1.md`",
        "- `flagged_case_evidence_packs/additional_corporate_actions_reference_review_v0_1.md`",
        "- `coverage_case_evidence_packs/additional_sparse_valid_context_cases_v0_1.md`",
        "",
        "## Open limits",
        "",
        "The package raises Additional above the old auxiliary-only state, but does not close every subfamily at 100%. Remaining limits are intentional:",
        "",
        "- ratios remain sparse and vendor-derived;",
        "- news remains attribution-sensitive;",
        "- corporate actions remain secondary to reference;",
        "- macro/economic data remains calendar context, not ticker causality;",
        "- no downstream feature promotion is granted by this readout alone.",
        "",
    ]
    (DOSSIER_ROOT / "additional_inspection_readout_v0_2.md").write_text("\n".join(lines), encoding="utf-8")


def write_root_readme() -> None:
    lines = [
        "# Additional Inspection Dossier",
        "",
        "## Role",
        "",
        "This dossier governs `additional_v0_1` as RAW vendor context data inside `01_foundations`.",
        "",
        "It exists to make the Additional block inspectable by subfamily. It does not turn Additional into a uniform market-data dataset and does not let Additional override `daily`, `quotes`, `trades`, `ohlcv_1m`, `reference` or `halts`.",
        "",
        "## Entry Points",
        "",
        "- `additional_institutional_closeout_v0_1.md`: first institutional closeout migrated from historical audit.",
        "- `additional_inspection_readout_v0_2.md`: current CAPA 1 quality/master-table readout.",
        "- `build_additional_inspection_pack.md`: rebuild instructions and source list.",
        "- `evidence_assets/`: generated tables, images and inventories.",
        "- `good_justification/`: positive evidence for high-quality subfamilies.",
        "- `flagged_case_evidence_packs/`: review evidence for attribution, reference overlap and restricted use.",
        "- `coverage_case_evidence_packs/`: sparse-but-valid context evidence.",
        "",
        "## Reading Rule",
        "",
        "Read Additional by subfamily:",
        "",
        "- financial statements: fundamentals/context with point-in-time filing guardrails;",
        "- ratios: sparse vendor-derived snapshots under review;",
        "- news: event context with attribution guardrails;",
        "- IPOs: sparse event/listing context;",
        "- corporate actions: secondary reconciliation against reference;",
        "- economic: macro calendar context.",
        "",
        "## CAPA 1 Boundary",
        "",
        "Additional can enrich CAPA 1 outputs such as `data_quality_report`, `master_daily_table`, `symbol_master`, `corporate_actions_table` and `calendar_table`.",
        "",
        "It cannot certify raw market prices, intraday book/tape quality or primary corporate-action adjustment by itself.",
        "",
    ]
    (DOSSIER_ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_build_doc(manifest: dict[str, Any]) -> None:
    lines = [
        "# Build Additional Inspection Pack",
        "",
        "## Command",
        "",
        "```powershell",
        "python C:\\TSIS_Data\\01_TSIS_DATA_FOUNDATION\\scripts\\inspection\\additional\\build_additional_inspection_pack.py",
        "```",
        "",
        "## Inputs",
        "",
        "- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/cache_v2/`",
        "- `runs/backtest/additional_audit/20260405_additional_lt1b_coverage/`",
        "- `runs/backtest/additional_downloads/20260405_full_refresh_ticker_based/`",
        "- `runs/backtest/additional_downloads/20260405_full_refresh_macro/`",
        "- `E:/TSIS/data/additional` for light physical root presence only",
        "",
        "## Outputs",
        "",
        "- `additional_inspection_readout_v0_2.md`",
        "- `README.md`",
        "- `evidence_assets/quality_tables/`",
        "- `evidence_assets/reference_reconciliation/`",
        "- `evidence_assets/news_attribution/`",
        "- `evidence_assets/ipo_context/`",
        "- `evidence_assets/visual_overview/`",
        "- `good_justification/`",
        "- `flagged_case_evidence_packs/`",
        "- `coverage_case_evidence_packs/`",
        "",
        "## Run Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Rule",
        "",
        "This builder reads preserved evidence and emits a current inspection package. It must not rewrite the historical `01_research` audit tree.",
        "",
    ]
    (DOSSIER_ROOT / "build_additional_inspection_pack.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    _ensure_dirs()
    cache_inventory = build_historical_cache_inventory()
    download_inventory = build_download_inventory()
    physical_audit = build_physical_root_audit()
    quality_df, readiness_df = build_quality_tables()
    reconciliation_df = build_reference_reconciliation()
    news_summary, _ = build_news_attribution_assets()
    ipo_summary = build_ipo_context_assets()
    build_casepacks(quality_df)
    build_visuals(quality_df, readiness_df)
    write_readout(quality_df, readiness_df, reconciliation_df, news_summary, ipo_summary)
    write_root_readme()

    manifest = {
        "run_id": "additional_inspection_pack_v0_2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script": _rel(Path(__file__)),
        "historical_cache": _rel(HISTORICAL_CACHE),
        "run_audit_root": _rel(RUN_AUDIT_ROOT),
        "active_data_root": str(ACTIVE_DATA_ROOT).replace("\\", "/"),
        "historical_cache_artifacts": int(len(cache_inventory)),
        "download_inventory_rows": int(len(download_inventory)),
        "physical_audit_rows": int(len(physical_audit)),
        "quality_rows": int(len(quality_df)),
        "readiness_rows": int(len(readiness_df)),
        "reconciliation_rows": int(len(reconciliation_df)),
        "news_bucket_rows": int(len(news_summary)),
        "ipo_bucket_rows": int(len(ipo_summary)),
    }
    (OUT_ROOT / "run_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    write_build_doc(manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
