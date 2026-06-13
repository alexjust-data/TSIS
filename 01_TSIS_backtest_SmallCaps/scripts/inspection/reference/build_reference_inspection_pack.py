from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import matplotlib
import pandas as pd

matplotlib.use("Agg")
from matplotlib import pyplot as plt  # noqa: E402


PROJECT_ROOT = Path(r"C:\TSIS_Data\01_TSIS_backtest_SmallCaps")
FOUNDATIONS = PROJECT_ROOT / "01_foundations"
DOSSIER_ROOT = FOUNDATIONS / "inspection_dossiers" / "reference"
OUT_ROOT = DOSSIER_ROOT / "evidence_assets"

HIST_AUDIT_ROOT = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "auditoria" / "reference"
HIST_CACHE = HIST_AUDIT_ROOT / "cache_v2"
HIST_CERT_ROOT = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "certification" / "reference"
GLOBAL_METRICS = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "certification" / "global_metrics"
PHYSICAL_ROOT = Path(r"E:\TSIS\data\reference")


def _rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path).replace("\\", "/")


def _md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "- sin filas\n"
    x = df.copy()
    for col in x.columns:
        x[col] = x[col].map(lambda v: "" if pd.isna(v) else str(v))
    lines = [
        "| " + " | ".join(x.columns) + " |",
        "|" + "|".join(["---"] * len(x.columns)) + "|",
    ]
    for _, row in x.iterrows():
        vals = [str(row[c]).replace("|", "/") for c in x.columns]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _read_parquet(name: str, columns: list[str] | None = None) -> pd.DataFrame:
    path = HIST_CACHE / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_parquet(path, columns=columns)


def build_historical_cache_inventory() -> dict:
    out_dir = OUT_ROOT / "historical_cache_inventory"
    files = sorted(HIST_CACHE.glob("*"))
    rows = []
    for path in files:
        if not path.is_file():
            continue
        item = {
            "artifact_name": path.name,
            "relative_path": _rel(path),
            "bytes": path.stat().st_size,
            "suffix": path.suffix.lower(),
            "sha256": "",
            "rows": "",
            "columns": "",
            "consumption": "provenance_read_only",
        }
        if path.suffix.lower() == ".json":
            item["sha256"] = _sha256(path)
        if path.suffix.lower() == ".parquet":
            try:
                df = pd.read_parquet(path)
                item["rows"] = len(df)
                item["columns"] = len(df.columns)
            except Exception as exc:  # pragma: no cover - audit output
                item["rows"] = "read_error"
                item["columns"] = type(exc).__name__
        rows.append(item)

    csv_path = out_dir / "reference_historical_cache_inventory_v0_1.csv"
    _write_csv(csv_path, rows, ["artifact_name", "relative_path", "bytes", "suffix", "sha256", "rows", "columns", "consumption"])

    md_path = out_dir / "reference_historical_cache_inventory_v0_1.md"
    md = [
        "# Reference Historical Cache Inventory v0.1",
        "",
        "Este inventario no copia caches historicos a `01_foundations`.",
        "Solo registra que existe, donde vive y como debe consumirse como provenance read-only.",
        "",
        f"- Historical audit root: `{_rel(HIST_AUDIT_ROOT)}`",
        f"- Historical cache root: `{_rel(HIST_CACHE)}`",
        f"- Artifacts inventariados: `{len(rows)}`",
        "",
        _md_table(pd.DataFrame(rows)),
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def build_physical_root_audit() -> dict:
    out_dir = OUT_ROOT / "physical_root_audit"
    rows = []
    for child in sorted(PHYSICAL_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        dirs = 0
        files = 0
        parquet = 0
        csv_count = 0
        other = 0
        sample_file = ""
        for item in child.rglob("*"):
            if item.is_dir():
                dirs += 1
                continue
            files += 1
            if not sample_file:
                sample_file = str(item)
            suffix = item.suffix.lower()
            if suffix == ".parquet":
                parquet += 1
            elif suffix == ".csv":
                csv_count += 1
            else:
                other += 1
        rows.append(
            {
                "subfamily": child.name,
                "dirs": dirs,
                "files": files,
                "parquet_files": parquet,
                "csv_files": csv_count,
                "other_files": other,
                "sample_file": sample_file.replace("\\", "/"),
                "write_policy": "read_only",
            }
        )

    csv_path = out_dir / "reference_physical_root_audit_v0_1.csv"
    _write_csv(csv_path, rows, ["subfamily", "dirs", "files", "parquet_files", "csv_files", "other_files", "sample_file", "write_policy"])

    md_path = out_dir / "reference_physical_root_audit_summary_v0_1.md"
    md = [
        "# Reference Physical Root Audit v0.1",
        "",
        f"- Physical root: `{str(PHYSICAL_ROOT).replace(chr(92), '/')}`",
        "- Policy: read-only. Este builder no modifica ni reorganiza el root fisico.",
        "",
        _md_table(pd.DataFrame(rows)),
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def build_population_summary() -> dict:
    out_dir = OUT_ROOT / "population_summary"

    identity = _read_parquet("reference_identity_quality_summary.parquet")
    overview_404 = _read_parquet("reference_overview_404_summary.parquet")
    event_type = _read_parquet("reference_event_type_summary.parquet")
    splits = _read_parquet("reference_splits_summary.parquet")
    dividends = _read_parquet("reference_dividends_summary.parquet")
    causal = _read_parquet("reference_causal_alignment_summary.parquet")
    download = _read_parquet("reference_download_audit_summary.parquet")
    listing = _read_parquet("reference_listing_snapshot_summary.parquet")

    rows = []
    for _, r in identity.iterrows():
        rows.append({"family": "identity", "bucket": r["identity_bucket"], "rows": int(r["rows"]), "distinct_tickers": int(r["distinct_tickers"])})
    for _, r in overview_404.iterrows():
        rows.append({"family": "overview_404", "bucket": r["overview_404_bucket"], "rows": int(r["rows"]), "distinct_tickers": int(r["distinct_tickers"])})
    for _, r in event_type.iterrows():
        rows.append({"family": "events", "bucket": f"{r['event_status']}:{r['event_type']}", "rows": int(r["rows"]), "distinct_tickers": int(r["distinct_tickers"])})
    for _, r in splits.iterrows():
        rows.append({"family": "splits", "bucket": r["split_bucket"], "rows": int(r["rows"]), "distinct_tickers": int(r["distinct_tickers"])})
    for _, r in dividends.iterrows():
        rows.append({"family": "dividends", "bucket": r["dividend_bucket"], "rows": int(r["rows"]), "distinct_tickers": int(r["distinct_tickers"])})
    for _, r in causal.iterrows():
        rows.append({"family": f"causal:{r['causal_domain']}", "bucket": r["bucket"], "rows": int(r["rows"]), "distinct_tickers": ""})

    csv_path = out_dir / "reference_population_summary_v0_1.csv"
    _write_csv(csv_path, rows, ["family", "bucket", "rows", "distinct_tickers"])

    endpoint_csv = out_dir / "reference_download_endpoint_summary_v0_1.csv"
    download.to_csv(endpoint_csv, index=False)

    listing_summary = pd.DataFrame(
        [
            {
                "metric": "listing_snapshot_summary_rows",
                "value": len(listing),
                "reading": "tickers observed in all_tickers summary",
            },
            {
                "metric": "listing_snapshot_rows_total",
                "value": int(listing["snapshot_rows"].sum()),
                "reading": "total all_tickers snapshot rows represented by the summary",
            },
            {
                "metric": "listing_tickers_lt1b",
                "value": int(listing["in_lt1b_universe"].fillna(False).sum()),
                "reading": "tickers flagged in lt1b universe",
            },
        ]
    )
    listing_csv = out_dir / "reference_listing_presence_summary_v0_1.csv"
    listing_summary.to_csv(listing_csv, index=False)

    md_path = out_dir / "reference_population_summary_v0_1.md"
    md = [
        "# Reference Population Summary v0.1",
        "",
        "Resumen ligero promovido desde cache historico. Los parquets pesados siguen en `01_research`.",
        "",
        "## Buckets principales",
        "",
        _md_table(pd.DataFrame(rows)),
        "## Download endpoints",
        "",
        _md_table(download),
        "## Listing presence",
        "",
        _md_table(listing_summary),
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")

    return {
        "csv": _rel(csv_path),
        "endpoint_csv": _rel(endpoint_csv),
        "listing_csv": _rel(listing_csv),
        "md": _rel(md_path),
        "rows": len(rows),
    }


def _barh(df: pd.DataFrame, label_col: str, value_col: str, title: str, out_path: Path, color: str = "#4c72b0") -> None:
    x = df.copy()
    x[value_col] = pd.to_numeric(x[value_col], errors="coerce").fillna(0)
    x = x.sort_values(value_col, ascending=True)
    height = max(3.8, 0.42 * len(x) + 1.2)
    fig, ax = plt.subplots(figsize=(12, height))
    ax.barh(x[label_col].astype(str), x[value_col], color=color)
    ax.set_title(title)
    ax.set_xlabel(value_col)
    ax.grid(axis="x", alpha=0.2)
    for idx, value in enumerate(x[value_col]):
        ax.text(value, idx, f" {int(value):,}", va="center", fontsize=9)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def build_visuals() -> dict:
    out_dir = OUT_ROOT / "population_visual_overview"
    manifest_rows = []

    identity = _read_parquet("reference_identity_quality_summary.parquet")
    identity_path = out_dir / "01_identity_quality_distribution.png"
    _barh(identity, "identity_bucket", "rows", "Reference identity quality distribution", identity_path, "#4c72b0")
    manifest_rows.append(
        {
            "visual_id": "01_identity_quality_distribution",
            "path": _rel(identity_path),
            "source": _rel(HIST_CACHE / "reference_identity_quality_summary.parquet"),
            "what_it_shows": "identity bucket mass",
            "answers": "main identity recovery vs review/bad residue",
            "does_not_answer": "economic continuity after ticker changes",
            "consequence": "identity snapshot is usable with explicit review/bad flags",
        }
    )

    download = _read_parquet("reference_download_audit_summary.parquet")
    dl = download[["dataset", "ok_rows", "error_rows", "resume_skip_rows", "http_404_rows"]].melt(id_vars="dataset", var_name="status", value_name="rows")
    pivot = dl.pivot_table(index="dataset", columns="status", values="rows", aggfunc="sum").fillna(0)
    fig, ax = plt.subplots(figsize=(13, 5))
    pivot.plot(kind="bar", stacked=True, ax=ax, color=["#c44e52", "#dd8452", "#4c72b0", "#55a868"])
    ax.set_title("Reference download endpoint status")
    ax.set_ylabel("rows")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.2)
    download_path = out_dir / "02_download_endpoint_status.png"
    fig.savefig(download_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    manifest_rows.append(
        {
            "visual_id": "02_download_endpoint_status",
            "path": _rel(download_path),
            "source": _rel(HIST_CACHE / "reference_download_audit_summary.parquet"),
            "what_it_shows": "endpoint request status by subdataset",
            "answers": "which endpoints have real errors, resume-skips or 404 semantics",
            "does_not_answer": "row-level semantic correctness of each payload",
            "consequence": "events 404 must be read as no-events semantics, while overview 404 remains identity residue",
        }
    )

    payload_rows = []
    for name, bucket_col in [
        ("reference_event_type_summary.parquet", "event_status"),
        ("reference_splits_summary.parquet", "split_bucket"),
        ("reference_dividends_summary.parquet", "dividend_bucket"),
    ]:
        df = _read_parquet(name)
        for _, r in df.iterrows():
            if name.startswith("reference_event"):
                bucket = f"{r['event_status']}:{r['event_type']}"
            else:
                bucket = r[bucket_col]
            payload_rows.append({"bucket": bucket, "rows": int(r["rows"])})
    payload = pd.DataFrame(payload_rows)
    payload_path = out_dir / "03_payload_family_distribution.png"
    _barh(payload, "bucket", "rows", "Reference events/splits/dividends payload distribution", payload_path, "#55a868")
    manifest_rows.append(
        {
            "visual_id": "03_payload_family_distribution",
            "path": _rel(payload_path),
            "source": "historical event/split/dividend summary parquets",
            "what_it_shows": "payload vs placeholder mass in events, splits and dividends",
            "answers": "which subfamilies have usable event payload and which are placeholder-heavy",
            "does_not_answer": "market impact of each event",
            "consequence": "dividends are usable at scale; splits are real but sparse; events are mostly ticker_change plus no-event payloads",
        }
    )

    causal = _read_parquet("reference_causal_alignment_summary.parquet")
    causal["label"] = causal["causal_domain"].astype(str) + " | " + causal["bucket"].astype(str)
    causal_path = out_dir / "04_causal_alignment_distribution.png"
    _barh(causal, "label", "rows", "Reference causal alignment distribution", causal_path, "#dd8452")
    manifest_rows.append(
        {
            "visual_id": "04_causal_alignment_distribution",
            "path": _rel(causal_path),
            "source": _rel(HIST_CACHE / "reference_causal_alignment_summary.parquet"),
            "what_it_shows": "causal overlay bucket mass",
            "answers": "where reference has explanatory force across trades, daily, 1m, halts and quotes",
            "does_not_answer": "clean causal proof for every individual case",
            "consequence": "events->halts and splits->trades are strongest; events->quotes is detector/review",
        }
    )

    listing = _read_parquet("reference_listing_snapshot_summary.parquet")
    bins = pd.cut(
        listing["snapshot_rows"],
        bins=[0, 1, 10, 100, 1000, 4000],
        labels=["1", "2-10", "11-100", "101-1000", "1001+"],
        include_lowest=True,
    )
    listing_dist = bins.value_counts(dropna=False).rename_axis("snapshot_rows_bucket").reset_index(name="tickers")
    listing_path = out_dir / "05_listing_snapshot_density.png"
    _barh(listing_dist, "snapshot_rows_bucket", "tickers", "Reference all_tickers snapshot density", listing_path, "#8172b2")
    manifest_rows.append(
        {
            "visual_id": "05_listing_snapshot_density",
            "path": _rel(listing_path),
            "source": _rel(HIST_CACHE / "reference_listing_snapshot_summary.parquet"),
            "what_it_shows": "number of all_tickers snapshots per ticker",
            "answers": "whether all_tickers is a temporal presence layer rather than a one-shot inventory",
            "does_not_answer": "final membership for every backtest date",
            "consequence": "usable for presence support, not final universe membership without builder policy",
        }
    )

    manifest_path = out_dir / "reference_population_visual_manifest_v0_1.csv"
    _write_csv(
        manifest_path,
        manifest_rows,
        ["visual_id", "path", "source", "what_it_shows", "answers", "does_not_answer", "consequence"],
    )

    md_path = out_dir / "reference_population_visual_manifest_v0_1.md"
    md = [
        "# Reference Population Visual Manifest v0.1",
        "",
        "Cada visual tiene lectura operacional. Las imagenes no son decoracion.",
        "",
        _md_table(pd.DataFrame(manifest_rows)),
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    return {"manifest_csv": _rel(manifest_path), "manifest_md": _rel(md_path), "visuals": len(manifest_rows)}


def _sample_rows(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    if df.empty:
        return df
    return df.head(n).copy()


def build_casepacks() -> dict:
    rows = []
    case_manifest_rows = []

    good_dir = DOSSIER_ROOT / "good_justification"
    flagged_dir = DOSSIER_ROOT / "flagged_case_evidence_packs"
    bad_dir = DOSSIER_ROOT / "bad_case_evidence_packs"
    causal_dir = DOSSIER_ROOT / "causal_case_evidence_packs"
    coverage_dir = DOSSIER_ROOT / "coverage_case_evidence_packs"
    for d in [good_dir, flagged_dir, bad_dir, causal_dir, coverage_dir]:
        d.mkdir(parents=True, exist_ok=True)

    identity_cases = _read_parquet("reference_identity_case_index.parquet")
    good_identity = _sample_rows(identity_cases.loc[identity_cases["identity_bucket"] == "good_identity_snapshot"], 10)
    review_identity = _sample_rows(identity_cases.loc[identity_cases["identity_bucket"].astype(str).str.contains("review", na=False)], 10)
    bad_identity = _sample_rows(identity_cases.loc[identity_cases["identity_bucket"] == "bad_unresolved_identity"], 10)

    good_split = _sample_rows(_read_parquet("reference_split_case_index.parquet").loc[lambda x: x["split_bucket"] == "good_split_event"], 10)
    dividends = _read_parquet("reference_dividend_case_index.parquet", columns=["ticker", "cash_amount", "currency", "dividend_type", "ex_dividend_date", "pay_date", "record_date", "dividend_bucket", "in_lt1b_universe"])
    good_dividend = _sample_rows(dividends.loc[dividends["dividend_bucket"] == "good_dividend_event"], 10)

    causal_split = _sample_rows(_read_parquet("reference_split_market_link_candidates.parquet"), 12)
    causal_halts = _sample_rows(_read_parquet("reference_event_halt_link_candidates.parquet"), 12)
    causal_quotes = _sample_rows(_read_parquet("reference_event_quotes_link_candidates.parquet"), 12)
    overview_404 = _sample_rows(_read_parquet("reference_overview_404_case_index.parquet"), 12)
    listing_gaps = _sample_rows(_read_parquet("reference_snapshot_presence_gaps.parquet"), 12)

    packs = [
        {
            "path": good_dir / "reference_good_identity_and_payload_cases_v0_1.md",
            "title": "Reference Good Identity And Payload Cases v0.1",
            "tables": [("Good identity sample", good_identity), ("Good split event sample", good_split), ("Good dividend event sample", good_dividend)],
            "reading": "Muestra que la capa principal de identidad, splits y dividends tiene payload real y consumible con flags.",
            "status": "good",
        },
        {
            "path": flagged_dir / "reference_review_identity_and_quotes_cases_v0_1.md",
            "title": "Reference Review Identity And Quotes Cases v0.1",
            "tables": [("Review identity sample", review_identity), ("Events -> quotes review/anomaly sample", causal_quotes)],
            "reading": "Muestra los residuos que deben conservar review: simbolos transitorios y ticker_change cerca de quotes anomalies.",
            "status": "review",
        },
        {
            "path": bad_dir / "reference_bad_unresolved_identity_cases_v0_1.md",
            "title": "Reference Bad Unresolved Identity Cases v0.1",
            "tables": [("Bad unresolved identity sample", bad_identity), ("Overview 404 sample", overview_404)],
            "reading": "Muestra el residuo duro de identidad. Es pequeno pero no consumible como identidad resuelta.",
            "status": "bad",
        },
        {
            "path": causal_dir / "reference_causal_overlay_cases_v0_1.md",
            "title": "Reference Causal Overlay Cases v0.1",
            "tables": [("Splits -> trades candidates", causal_split), ("Events -> halts candidates", causal_halts), ("Events -> quotes candidates", causal_quotes)],
            "reading": "Muestra los tres frentes causales principales: splits->trades quirurgico, events->halts fuerte, events->quotes detector/review.",
            "status": "causal",
        },
        {
            "path": coverage_dir / "reference_presence_coverage_cases_v0_1.md",
            "title": "Reference Presence Coverage Cases v0.1",
            "tables": [("Overview 404 buckets sample", overview_404), ("Listing presence gap sample", listing_gaps)],
            "reading": "Muestra que all_tickers soporta presencia temporal, pero no sustituye un universe builder final.",
            "status": "coverage",
        },
    ]

    for pack in packs:
        lines = [
            f"# {pack['title']}",
            "",
            "Fuente: cache historico read-only de `reference`.",
            "",
            "## Lectura",
            "",
            pack["reading"],
            "",
            "## Que muestra",
            "",
            "Casos representativos derivados de los indices historicos.",
            "",
            "## Responde",
            "",
            "Que familias concretas sostienen el estado institucional del bucket.",
            "",
            "## No responde",
            "",
            "No reemplaza la lectura poblacional ni prueba causalidad economica universal.",
            "",
            "## Consecuencia",
            "",
            f"Estos casos soportan estado `{pack['status']}` bajo las limitaciones del readout.",
            "",
        ]
        for section, table_df in pack["tables"]:
            keep = table_df.copy()
            if len(keep.columns) > 12:
                keep = keep[keep.columns[:12]]
            lines.extend([f"## {section}", "", _md_table(keep), ""])
        pack["path"].write_text("\n".join(lines), encoding="utf-8")
        case_manifest_rows.append({"casepack": pack["path"].name, "relative_path": _rel(pack["path"]), "status": pack["status"], "reading": pack["reading"]})

    manifest_dir = OUT_ROOT / "case_manifest"
    manifest_path = manifest_dir / "reference_case_manifest_v0_1.csv"
    _write_csv(manifest_path, case_manifest_rows, ["casepack", "relative_path", "status", "reading"])
    manifest_md = manifest_dir / "reference_case_manifest_v0_1.md"
    manifest_md.write_text("# Reference Case Manifest v0.1\n\n" + _md_table(pd.DataFrame(case_manifest_rows)), encoding="utf-8")
    return {"manifest_csv": _rel(manifest_path), "manifest_md": _rel(manifest_md), "casepacks": len(case_manifest_rows)}


def build_certification_inventory() -> dict:
    out_dir = OUT_ROOT / "historical_certification_inventory"
    rows = []
    for path in sorted(HIST_CERT_ROOT.glob("*")):
        if path.is_file():
            rows.append({"artifact_name": path.name, "relative_path": _rel(path), "bytes": path.stat().st_size, "sha256": _sha256(path), "consumption": "certification_source"})
    for path in sorted(GLOBAL_METRICS.glob("reference_*")):
        if path.is_file():
            rows.append({"artifact_name": path.name, "relative_path": _rel(path), "bytes": path.stat().st_size, "sha256": _sha256(path), "consumption": "global_metric_source"})
    csv_path = out_dir / "reference_certification_inventory_v0_1.csv"
    _write_csv(csv_path, rows, ["artifact_name", "relative_path", "bytes", "sha256", "consumption"])
    md_path = out_dir / "reference_certification_inventory_v0_1.md"
    md_path.write_text("# Reference Certification Inventory v0.1\n\n" + _md_table(pd.DataFrame(rows)), encoding="utf-8")
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def write_run_manifest(results: dict, started_at: str) -> dict:
    finished_at = datetime.now(timezone.utc).isoformat()
    out_path = OUT_ROOT / "run_manifest.json"
    manifest = {
        "run_id": "reference_inspection_pack_v0_1_2026-06-13",
        "status": "pass",
        "started_at_utc": started_at,
        "finished_at_utc": finished_at,
        "builder": _rel(Path(__file__)),
        "protected_roots_read_only": [
            str(PHYSICAL_ROOT).replace("\\", "/"),
            _rel(HIST_AUDIT_ROOT),
            _rel(HIST_CERT_ROOT),
        ],
        "outputs": results,
        "notes": [
            "No raw data was modified.",
            "Historical parquets were not copied to foundations.",
            "Outputs are lightweight manifests, summaries, visuals and casepacks.",
        ],
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"manifest": _rel(out_path)}


def build() -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    results = {
        "historical_cache_inventory": build_historical_cache_inventory(),
        "certification_inventory": build_certification_inventory(),
        "physical_root_audit": build_physical_root_audit(),
        "population_summary": build_population_summary(),
        "population_visual_overview": build_visuals(),
        "casepacks": build_casepacks(),
    }
    results["run_manifest"] = write_run_manifest(results, started_at)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the reference inspection evidence pack.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()
    results = build()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("reference inspection pack built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
