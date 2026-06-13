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
DOSSIER_ROOT = FOUNDATIONS / "inspection_dossiers" / "halts"
OUT_ROOT = DOSSIER_ROOT / "evidence_assets"

HIST_AUDIT_ROOT = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "auditoria" / "halts"
HIST_CACHE = HIST_AUDIT_ROOT / "cache_v2"
HIST_CERT_ROOT = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "certification" / "halts"
GLOBAL_METRICS = PROJECT_ROOT / "01_research" / "01_auditoria_RAW_DATA" / "00_data_certification" / "certification" / "global_metrics"

PHYSICAL_ROOT = Path(r"E:\TSIS\data\Halts")
LEGACY_ROOT = Path(r"D:\Halts")


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
    rows = []
    for path in sorted(HIST_CACHE.glob("*")):
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

    csv_path = out_dir / "halts_historical_cache_inventory_v0_1.csv"
    _write_csv(csv_path, rows, ["artifact_name", "relative_path", "bytes", "suffix", "sha256", "rows", "columns", "consumption"])
    md_path = out_dir / "halts_historical_cache_inventory_v0_1.md"
    md_path.write_text(
        "\n".join(
            [
                "# Halts Historical Cache Inventory v0.1",
                "",
                "Este inventario registra caches historicos read-only. No copia parquets pesados a `01_foundations`.",
                "",
                f"- Historical audit root: `{_rel(HIST_AUDIT_ROOT)}`",
                f"- Historical cache root: `{_rel(HIST_CACHE)}`",
                f"- Artifacts inventariados: `{len(rows)}`",
                "",
                _md_table(pd.DataFrame(rows)),
            ]
        ),
        encoding="utf-8",
    )
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def build_certification_inventory() -> dict:
    out_dir = OUT_ROOT / "historical_certification_inventory"
    rows = []
    for path in sorted(HIST_CERT_ROOT.glob("*")):
        if path.is_file():
            rows.append({"artifact_name": path.name, "relative_path": _rel(path), "bytes": path.stat().st_size, "sha256": _sha256(path), "consumption": "certification_source"})
    for path in sorted(GLOBAL_METRICS.glob("halts_*")):
        if path.is_file():
            rows.append({"artifact_name": path.name, "relative_path": _rel(path), "bytes": path.stat().st_size, "sha256": _sha256(path), "consumption": "global_metric_source"})
    csv_path = out_dir / "halts_certification_inventory_v0_1.csv"
    _write_csv(csv_path, rows, ["artifact_name", "relative_path", "bytes", "sha256", "consumption"])
    md_path = out_dir / "halts_certification_inventory_v0_1.md"
    md_path.write_text("# Halts Certification Inventory v0.1\n\n" + _md_table(pd.DataFrame(rows)), encoding="utf-8")
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def _root_summary(root: Path, root_role: str) -> list[dict]:
    rows = []
    if not root.exists():
        return [{"root_role": root_role, "root": str(root).replace("\\", "/"), "subtree": "", "dirs": 0, "files": 0, "parquet_files": 0, "csv_files": 0, "xml_files": 0, "html_files": 0, "json_files": 0, "other_files": 0, "bytes": 0, "write_policy": "read_only_missing"}]
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        subtree_root = child if child.is_dir() else root
        subtree = child.name if child.is_dir() else "."
        dirs = 0
        files = 0
        parquet = 0
        csv_count = 0
        xml = 0
        html = 0
        json_count = 0
        other = 0
        bytes_total = 0
        iterator = subtree_root.rglob("*") if subtree_root.is_dir() else [child]
        for item in iterator:
            if item.is_dir():
                dirs += 1
                continue
            files += 1
            bytes_total += item.stat().st_size
            suffix = item.suffix.lower()
            if suffix == ".parquet":
                parquet += 1
            elif suffix == ".csv":
                csv_count += 1
            elif suffix == ".xml":
                xml += 1
            elif suffix in {".html", ".htm"}:
                html += 1
            elif suffix == ".json":
                json_count += 1
            else:
                other += 1
        rows.append(
            {
                "root_role": root_role,
                "root": str(root).replace("\\", "/"),
                "subtree": subtree,
                "dirs": dirs,
                "files": files,
                "parquet_files": parquet,
                "csv_files": csv_count,
                "xml_files": xml,
                "html_files": html,
                "json_files": json_count,
                "other_files": other,
                "bytes": bytes_total,
                "write_policy": "read_only",
            }
        )
    return rows


def build_physical_root_audit() -> dict:
    out_dir = OUT_ROOT / "physical_root_audit"
    rows = _root_summary(PHYSICAL_ROOT, "canonical_current") + _root_summary(LEGACY_ROOT, "legacy_observed")
    csv_path = out_dir / "halts_physical_root_audit_v0_1.csv"
    _write_csv(csv_path, rows, ["root_role", "root", "subtree", "dirs", "files", "parquet_files", "csv_files", "xml_files", "html_files", "json_files", "other_files", "bytes", "write_policy"])
    md_path = out_dir / "halts_physical_root_audit_summary_v0_1.md"
    md_path.write_text(
        "\n".join(
            [
                "# Halts Physical Root Audit v0.1",
                "",
                f"- Canonical current root: `{str(PHYSICAL_ROOT).replace(chr(92), '/')}`",
                f"- Legacy observed root: `{str(LEGACY_ROOT).replace(chr(92), '/')}`",
                "- Policy: read-only. Este builder no modifica ni reorganiza ninguna raiz fisica.",
                "",
                _md_table(pd.DataFrame(rows)),
            ]
        ),
        encoding="utf-8",
    )
    return {"csv": _rel(csv_path), "md": _rel(md_path), "rows": len(rows)}


def build_population_summary() -> dict:
    out_dir = OUT_ROOT / "population_summary"
    source = _read_parquet("source_quality_summary.parquet")
    taxonomy = _read_parquet("event_taxonomy_summary.parquet")
    visual = _read_parquet("halts_quotes_trades_visual_cases.parquet", columns=["visual_case_bucket", "event_taxonomy", "events_in_visual", "ticker", "rank_score"])
    visual_summary = visual.groupby("visual_case_bucket", dropna=False).size().reset_index(name="visual_rows").sort_values("visual_rows", ascending=False)
    lt1b = _read_parquet("halts_lt1b_event_index.parquet", columns=["event_taxonomy", "ticker"])
    lt1b_summary = lt1b.groupby("event_taxonomy", dropna=False).agg(events=("event_taxonomy", "size"), tickers=("ticker", "nunique")).reset_index().sort_values("events", ascending=False)
    coverage = _read_parquet("ticker_halt_coverage_summary.parquet")
    coverage_summary = pd.DataFrame(
        [
            {"metric": "universe_tickers", "value": len(coverage), "reading": "tickers in lt1b coverage summary"},
            {"metric": "tickers_with_halt_data", "value": int(coverage["has_halt_data"].fillna(False).sum()), "reading": "tickers with at least one matched halt event"},
            {"metric": "tickers_without_halt_data", "value": int((~coverage["has_halt_data"].fillna(False)).sum()), "reading": "absence means no matched event, not missing coverage"},
            {"metric": "halt_events_total_for_universe", "value": int(coverage["halt_events_count"].sum()), "reading": "total events attached to universe tickers"},
        ]
    )
    recon = _read_parquet("multisource_builder_reconciliation.parquet")

    combined_rows = []
    for _, r in source.iterrows():
        combined_rows.append({"family": "source_quality", "bucket": r["source"], "count": int(r["rows"]), "secondary": int(r["ticker_nonnull_rows"])})
    for _, r in taxonomy.iterrows():
        combined_rows.append({"family": "canonical_event_taxonomy", "bucket": r["event_taxonomy"], "count": int(r["events"]), "secondary": int(r["source_rows"])})
    for _, r in lt1b_summary.iterrows():
        combined_rows.append({"family": "lt1b_event_taxonomy", "bucket": r["event_taxonomy"], "count": int(r["events"]), "secondary": int(r["tickers"])})
    for _, r in visual_summary.iterrows():
        combined_rows.append({"family": "visual_case_bucket", "bucket": r["visual_case_bucket"], "count": int(r["visual_rows"]), "secondary": ""})

    csv_path = out_dir / "halts_population_summary_v0_1.csv"
    _write_csv(csv_path, combined_rows, ["family", "bucket", "count", "secondary"])
    source_csv = out_dir / "halts_source_quality_summary_v0_1.csv"
    source.to_csv(source_csv, index=False)
    taxonomy_csv = out_dir / "halts_event_taxonomy_summary_v0_1.csv"
    taxonomy.to_csv(taxonomy_csv, index=False)
    lt1b_csv = out_dir / "halts_lt1b_event_taxonomy_summary_v0_1.csv"
    lt1b_summary.to_csv(lt1b_csv, index=False)
    visual_csv = out_dir / "halts_visual_bucket_summary_v0_1.csv"
    visual_summary.to_csv(visual_csv, index=False)
    coverage_csv = out_dir / "halts_coverage_summary_v0_1.csv"
    coverage_summary.to_csv(coverage_csv, index=False)
    recon_csv = out_dir / "halts_multisource_reconciliation_v0_1.csv"
    recon.to_csv(recon_csv, index=False)

    md_path = out_dir / "halts_population_summary_v0_1.md"
    md_path.write_text(
        "\n".join(
            [
                "# Halts Population Summary v0.1",
                "",
                "Resumen ligero promovido desde cache historico. Los parquets pesados siguen en `01_research`.",
                "",
                "## Source quality",
                "",
                _md_table(source),
                "## Canonical event taxonomy",
                "",
                _md_table(taxonomy),
                "## LT1B event taxonomy",
                "",
                _md_table(lt1b_summary),
                "## Visual buckets",
                "",
                _md_table(visual_summary),
                "## Universe coverage",
                "",
                _md_table(coverage_summary),
                "## Multisource reconciliation",
                "",
                _md_table(recon),
            ]
        ),
        encoding="utf-8",
    )
    return {
        "csv": _rel(csv_path),
        "source_csv": _rel(source_csv),
        "taxonomy_csv": _rel(taxonomy_csv),
        "lt1b_csv": _rel(lt1b_csv),
        "visual_csv": _rel(visual_csv),
        "coverage_csv": _rel(coverage_csv),
        "recon_csv": _rel(recon_csv),
        "md": _rel(md_path),
        "rows": len(combined_rows),
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

    source = _read_parquet("source_quality_summary.parquet")
    source_path = out_dir / "01_source_quality_rows.png"
    _barh(source, "source", "rows", "Halts source row mass", source_path, "#4c72b0")
    manifest_rows.append(
        {
            "visual_id": "01_source_quality_rows",
            "path": _rel(source_path),
            "source": _rel(HIST_CACHE / "source_quality_summary.parquet"),
            "what_it_shows": "event row mass by official source",
            "answers": "which sources dominate the consolidated halt/suspension master",
            "does_not_answer": "whether each source has identical intraday granularity",
            "consequence": "Nasdaq dominates mass, NYSE is stable venue evidence, SEC is regulatory context",
        }
    )

    taxonomy = _read_parquet("event_taxonomy_summary.parquet")
    taxonomy_path = out_dir / "02_canonical_event_taxonomy.png"
    _barh(taxonomy, "event_taxonomy", "events", "Halts canonical event taxonomy", taxonomy_path, "#55a868")
    manifest_rows.append(
        {
            "visual_id": "02_canonical_event_taxonomy",
            "path": _rel(taxonomy_path),
            "source": _rel(HIST_CACHE / "event_taxonomy_summary.parquet"),
            "what_it_shows": "canonical event usability taxonomy",
            "answers": "how much of halts is usable intraday/date-level/review/bad",
            "does_not_answer": "visual coherence with quotes/trades",
            "consequence": "halts is structurally strong, with one marginal hard-bad canonical event",
        }
    )

    lt1b = _read_parquet("halts_lt1b_event_index.parquet", columns=["event_taxonomy", "ticker"])
    lt1b_summary = lt1b.groupby("event_taxonomy", dropna=False).agg(events=("event_taxonomy", "size"), tickers=("ticker", "nunique")).reset_index()
    lt1b_path = out_dir / "03_lt1b_event_taxonomy.png"
    _barh(lt1b_summary, "event_taxonomy", "events", "Halts LT1B event taxonomy", lt1b_path, "#64b5cd")
    manifest_rows.append(
        {
            "visual_id": "03_lt1b_event_taxonomy",
            "path": _rel(lt1b_path),
            "source": _rel(HIST_CACHE / "halts_lt1b_event_index.parquet"),
            "what_it_shows": "event taxonomy after LT1B universe intersection",
            "answers": "whether the strong structural reading survives project universe filtering",
            "does_not_answer": "whether every LT1B halt has visual raw linked",
            "consequence": "LT1B subset remains overwhelmingly good_full_intraday_event",
        }
    )

    visual = _read_parquet("halts_quotes_trades_visual_cases.parquet", columns=["visual_case_bucket"])
    visual_summary = visual.groupby("visual_case_bucket", dropna=False).size().reset_index(name="visual_rows")
    visual_path = out_dir / "04_visual_case_bucket_distribution.png"
    _barh(visual_summary, "visual_case_bucket", "visual_rows", "Halts visual case bucket distribution", visual_path, "#dd8452")
    manifest_rows.append(
        {
            "visual_id": "04_visual_case_bucket_distribution",
            "path": _rel(visual_path),
            "source": _rel(HIST_CACHE / "halts_quotes_trades_visual_cases.parquet"),
            "what_it_shows": "visual overlay bucket mass",
            "answers": "whether official halts align visually with quotes/trades",
            "does_not_answer": "manual visual truth for every individual case",
            "consequence": "confirmed_halt_microstructure_coherent dominates; residual buckets are review, not bad families",
        }
    )

    coverage = _read_parquet("ticker_halt_coverage_summary.parquet")
    top = coverage.sort_values("halt_events_count", ascending=False).head(20)[["ticker", "halt_events_count"]]
    top_path = out_dir / "05_top_tickers_by_halt_events.png"
    _barh(top, "ticker", "halt_events_count", "Top LT1B tickers by halt events", top_path, "#8172b2")
    manifest_rows.append(
        {
            "visual_id": "05_top_tickers_by_halt_events",
            "path": _rel(top_path),
            "source": _rel(HIST_CACHE / "ticker_halt_coverage_summary.parquet"),
            "what_it_shows": "ticker concentration of halt events",
            "answers": "whether halt activity is evenly spread or concentrated",
            "does_not_answer": "whether high-count tickers are bad data",
            "consequence": "sampling must account for concentration; top active tickers should not define global quality alone",
        }
    )

    manifest_path = out_dir / "halts_population_visual_manifest_v0_1.csv"
    _write_csv(
        manifest_path,
        manifest_rows,
        ["visual_id", "path", "source", "what_it_shows", "answers", "does_not_answer", "consequence"],
    )
    md_path = out_dir / "halts_population_visual_manifest_v0_1.md"
    md_path.write_text("# Halts Population Visual Manifest v0.1\n\n" + _md_table(pd.DataFrame(manifest_rows)), encoding="utf-8")
    return {"manifest_csv": _rel(manifest_path), "manifest_md": _rel(md_path), "visuals": len(manifest_rows)}


def _sample(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if df.empty:
        return df
    return df.head(n).copy()


def build_casepacks() -> dict:
    good_dir = DOSSIER_ROOT / "good_justification"
    flagged_dir = DOSSIER_ROOT / "flagged_case_evidence_packs"
    bad_dir = DOSSIER_ROOT / "bad_case_evidence_packs"
    causal_dir = DOSSIER_ROOT / "causal_case_evidence_packs"
    coverage_dir = DOSSIER_ROOT / "coverage_case_evidence_packs"
    for d in [good_dir, flagged_dir, bad_dir, causal_dir, coverage_dir]:
        d.mkdir(parents=True, exist_ok=True)

    visual = _read_parquet("halts_quotes_trades_visual_cases.parquet")
    canonical = _read_parquet("canonical_event_summary.parquet")
    residual = _read_parquet("nasdaq_final_residual_rows.parquet")
    coverage = _read_parquet("ticker_halt_coverage_summary.parquet")
    source = _read_parquet("source_quality_summary.parquet")
    recon = _read_parquet("multisource_builder_reconciliation.parquet")

    good_cases = _sample(visual.loc[visual["visual_case_bucket"] == "confirmed_halt_microstructure_coherent"].sort_values("rank_score", ascending=False), 12)
    review_cases = _sample(visual.loc[visual["visual_case_bucket"] != "confirmed_halt_microstructure_coherent"].sort_values(["visual_case_bucket", "rank_score"], ascending=[True, False]), 20)
    bad_events = canonical.loc[canonical["event_taxonomy"] == "bad_unusable_event"].copy()
    top_coverage = _sample(coverage.sort_values("halt_events_count", ascending=False), 12)
    no_halt = _sample(coverage.loc[~coverage["has_halt_data"].fillna(False)], 12)

    packs = [
        {
            "path": good_dir / "halts_good_coherent_visual_cases_v0_1.md",
            "title": "Halts Good Coherent Visual Cases v0.1",
            "tables": [("Confirmed halt microstructure coherent sample", good_cases)],
            "reading": "Muestra casos donde el evento oficial queda alineado con quotes y trades.",
            "status": "good",
        },
        {
            "path": flagged_dir / "halts_review_visual_cases_v0_1.md",
            "title": "Halts Review Visual Cases v0.1",
            "tables": [("Review visual bucket sample", review_cases)],
            "reading": "Muestra asimetrias libro/tape, mercado limpio o falta de enlace visual; no son bad por defecto.",
            "status": "review",
        },
        {
            "path": bad_dir / "halts_bad_residual_cases_v0_1.md",
            "title": "Halts Bad Residual Cases v0.1",
            "tables": [("Bad unusable canonical event", bad_events), ("Nasdaq raw missing payload residual rows", residual)],
            "reading": "Muestra el residuo estructural duro: un evento canonico y 11 raws Nasdaq vacios.",
            "status": "bad_residual_marginal",
        },
        {
            "path": causal_dir / "halts_causal_overlay_cases_v0_1.md",
            "title": "Halts Causal Overlay Cases v0.1",
            "tables": [("Visual overlay sample", visual.sort_values("rank_score", ascending=False).head(20)), ("Source quality", source)],
            "reading": "Muestra que halts funciona como verdad del evento y capa causal contra quotes/trades.",
            "status": "causal",
        },
        {
            "path": coverage_dir / "halts_universe_coverage_cases_v0_1.md",
            "title": "Halts Universe Coverage Cases v0.1",
            "tables": [("Top halt-count tickers", top_coverage), ("Tickers without halt matches sample", no_halt), ("Multisource reconciliation", recon)],
            "reading": "Muestra coverage y concentracion: ausencia de evento no equivale a missing data.",
            "status": "coverage",
        },
    ]

    manifest_rows = []
    for pack in packs:
        lines = [
            f"# {pack['title']}",
            "",
            "Fuente: cache historico read-only de `halts`.",
            "",
            "## Lectura",
            "",
            pack["reading"],
            "",
            "## Que muestra",
            "",
            "Casos o tablas representativas derivados de los indices historicos.",
            "",
            "## Responde",
            "",
            "Que familias concretas sostienen el estado institucional del bucket.",
            "",
            "## No responde",
            "",
            "No reemplaza la inspeccion manual de todos los eventos ni prueba calidad de quotes/trades por si solo.",
            "",
            "## Consecuencia",
            "",
            f"Estos casos soportan estado `{pack['status']}` bajo las limitaciones del readout.",
            "",
        ]
        for section, table_df in pack["tables"]:
            keep = table_df.copy()
            if len(keep.columns) > 14:
                keep = keep[keep.columns[:14]]
            lines.extend([f"## {section}", "", _md_table(keep), ""])
        pack["path"].write_text("\n".join(lines), encoding="utf-8")
        manifest_rows.append({"casepack": pack["path"].name, "relative_path": _rel(pack["path"]), "status": pack["status"], "reading": pack["reading"]})

    manifest_dir = OUT_ROOT / "case_manifest"
    manifest_path = manifest_dir / "halts_case_manifest_v0_1.csv"
    _write_csv(manifest_path, manifest_rows, ["casepack", "relative_path", "status", "reading"])
    manifest_md = manifest_dir / "halts_case_manifest_v0_1.md"
    manifest_md.write_text("# Halts Case Manifest v0.1\n\n" + _md_table(pd.DataFrame(manifest_rows)), encoding="utf-8")
    return {"manifest_csv": _rel(manifest_path), "manifest_md": _rel(manifest_md), "casepacks": len(manifest_rows)}


def write_run_manifest(results: dict, started_at: str) -> dict:
    out_path = OUT_ROOT / "run_manifest.json"
    manifest = {
        "run_id": "halts_inspection_pack_v0_1_2026-06-13",
        "status": "pass",
        "started_at_utc": started_at,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "builder": _rel(Path(__file__)),
        "protected_roots_read_only": [
            str(PHYSICAL_ROOT).replace("\\", "/"),
            str(LEGACY_ROOT).replace("\\", "/"),
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
    parser = argparse.ArgumentParser(description="Build the halts inspection evidence pack.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()
    results = build()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("halts inspection pack built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
