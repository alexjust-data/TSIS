from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DOSSIER_ROOT = PROJECT_ROOT / "01_foundations" / "inspection_dossiers" / "quotes"
EVIDENCE_ROOT = DOSSIER_ROOT / "evidence_assets"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.inspection.quotes.quotes_case_panel import build_quotes_case_pool


@dataclass(frozen=True)
class ScopeConfig:
    scope: str
    manifest_path: Path
    doc_path: Path
    expected_rows: int


SCOPE_CONFIGS: tuple[ScopeConfig, ...] = (
    ScopeConfig(
        scope="review",
        manifest_path=EVIDENCE_ROOT / "review" / "quotes_review_case_packs_manifest.csv",
        doc_path=DOSSIER_ROOT / "flagged_case_evidence_packs" / "quotes_review_cases_v0_1.md",
        expected_rows=64,
    ),
    ScopeConfig(
        scope="bad",
        manifest_path=EVIDENCE_ROOT / "bad" / "quotes_bad_case_packs_manifest.csv",
        doc_path=DOSSIER_ROOT / "bad_case_evidence_packs" / "quotes_bad_cases_v0_1.md",
        expected_rows=15,
    ),
)


def _case_key(frame: pd.DataFrame) -> pd.Series:
    return frame["ticker"].astype(str) + "|" + frame["date"].astype(str)


def _extract_total_cases(md_text: str) -> int | None:
    match = re.search(r"Total cases:\s*`(\d+)`", md_text)
    if not match:
        return None
    return int(match.group(1))


def _extract_menu_entries(md_text: str) -> list[str]:
    return re.findall(r"^\d+\.\s+\[([A-Z0-9\.\-]+)\s+(\d{4}-\d{2}-\d{2})\]", md_text, flags=re.M)


def _existing_paths(row: pd.Series) -> list[Path]:
    cols = [
        "case_dir",
        "event_month_png",
        "adjusted_proxy_png",
        "event_month_quotes_png",
        "raw_window_png",
        "full_session_png",
        "structure_diag_png",
        "summary_card_png",
        "historical_context_png",
        "case_note_md",
    ]
    out: list[Path] = []
    for col in cols:
        value = row.get(col)
        if pd.isna(value) or not str(value).strip():
            continue
        out.append(Path(str(value)))
    return out


def _audit_scope(config: ScopeConfig, source_pool: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    expected = source_pool.loc[source_pool["scope_name"].eq(config.scope)].copy()
    expected["case_key"] = _case_key(expected)

    manifest = pd.read_csv(config.manifest_path)
    manifest["case_key"] = _case_key(manifest)

    expected_keys = set(expected["case_key"])
    manifest_keys = set(manifest["case_key"])

    missing_from_manifest = sorted(expected_keys - manifest_keys)
    extra_in_manifest = sorted(manifest_keys - expected_keys)

    md_text = config.doc_path.read_text(encoding="utf-8")
    md_total = _extract_total_cases(md_text)
    menu_entries = _extract_menu_entries(md_text)
    menu_keys = sorted([f"{ticker}|{date}" for ticker, date in menu_entries])

    manifest_existing = 0
    manifest_missing_assets = 0
    missing_asset_rows: list[str] = []
    for _, row in manifest.iterrows():
        paths = _existing_paths(row)
        missing_here = [str(p) for p in paths if not p.exists()]
        if missing_here:
            manifest_missing_assets += 1
            missing_asset_rows.append(row["case_key"])
        else:
            manifest_existing += 1

    result = {
        "scope": config.scope,
        "expected_rows": int(len(expected)),
        "manifest_rows": int(len(manifest)),
        "expected_rows_contract": int(config.expected_rows),
        "doc_total_cases": md_total if md_total is not None else -1,
        "menu_entries": int(len(menu_entries)),
        "missing_from_manifest": int(len(missing_from_manifest)),
        "extra_in_manifest": int(len(extra_in_manifest)),
        "menu_mismatch_vs_manifest": int(len(set(menu_keys) ^ manifest_keys)),
        "manifest_rows_all_assets_present": int(manifest_existing),
        "manifest_rows_with_missing_assets": int(manifest_missing_assets),
        "status": (
            "PASS"
            if len(expected) == config.expected_rows
            and len(manifest) == config.expected_rows
            and md_total == config.expected_rows
            and len(menu_entries) == config.expected_rows
            and not missing_from_manifest
            and not extra_in_manifest
            and set(menu_keys) == manifest_keys
            and manifest_missing_assets == 0
            else "FAIL"
        ),
        "missing_from_manifest_keys": ";".join(missing_from_manifest),
        "extra_in_manifest_keys": ";".join(extra_in_manifest),
        "missing_asset_case_keys": ";".join(missing_asset_rows),
    }
    return manifest, result


def _build_readout(summary_df: pd.DataFrame, out_path: Path) -> None:
    lines: list[str] = [
        "# Quotes Open Casepacks Audit v0.1",
        "",
        "## Rol",
        "",
        "Este documento audita la trazabilidad completa de la bolsa abierta de `quotes`.",
        "No valida una transformacion derivada como en `1m_split_normalized`.",
        "Valida otra cosa: que los casos abiertos que llegan al inspector (`review` y `bad`) coinciden exactamente con el pool historico abierto y que sus assets existen realmente.",
        "",
        "## Que se audita",
        "",
        "- correspondencia exacta entre `build_quotes_case_pool()` y los manifests exportados;",
        "- conteos esperados por scope (`64 review`, `15 bad`);",
        "- coherencia entre manifest y markdown de cada dossier;",
        "- y existencia fisica de los assets referenciados por cada caso.",
        "",
        "## Resultado agregado",
        "",
    ]
    for _, row in summary_df.iterrows():
        lines.extend(
            [
                f"### Scope `{row['scope']}`",
                "",
                f"- `status`: `{row['status']}`",
                f"- `expected_rows_from_pool`: `{int(row['expected_rows'])}`",
                f"- `expected_rows_contract`: `{int(row['expected_rows_contract'])}`",
                f"- `manifest_rows`: `{int(row['manifest_rows'])}`",
                f"- `doc_total_cases`: `{int(row['doc_total_cases'])}`",
                f"- `menu_entries`: `{int(row['menu_entries'])}`",
                f"- `missing_from_manifest`: `{int(row['missing_from_manifest'])}`",
                f"- `extra_in_manifest`: `{int(row['extra_in_manifest'])}`",
                f"- `menu_mismatch_vs_manifest`: `{int(row['menu_mismatch_vs_manifest'])}`",
                f"- `manifest_rows_all_assets_present`: `{int(row['manifest_rows_all_assets_present'])}`",
                f"- `manifest_rows_with_missing_assets`: `{int(row['manifest_rows_with_missing_assets'])}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Lectura tecnica",
            "",
            "Si ambos scopes pasan, la conclusion correcta es esta:",
            "",
            "- la cola abierta de `quotes` no se construyo ad hoc;",
            "- no faltan casos del pool historico abierto;",
            "- no sobran casos inventados en los dossiers;",
            "- y cada caso publicado por el inspector referencia assets realmente existentes.",
            "",
            "Esto no equivale a una auditoria full-universe de transformacion semantica, porque `quotes` aqui no esta validando una vista derivada nueva como `1m_split_normalized`.",
            "Pero si cierra la deuda institucional correcta para `quotes`: demostrar que la bolsa final `review/bad` es completa, trazable y reproducible.",
            "",
            "## Veredicto",
            "",
            "Si el resultado es `PASS` en `review` y `bad`, el inspector puede asumir que la frontera abierta final de `quotes` esta cerrada con integridad de coverage y de assets.",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    pool = build_quotes_case_pool().copy()
    summary_rows: list[dict[str, object]] = []
    for config in SCOPE_CONFIGS:
        _, summary = _audit_scope(config, pool)
        summary_rows.append(summary)

    summary_df = pd.DataFrame(summary_rows)
    out_dir = DOSSIER_ROOT / "evidence_assets" / "open_casepacks_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(out_dir / "quotes_open_casepacks_audit_summary.csv", index=False)
    summary_df.to_parquet(out_dir / "quotes_open_casepacks_audit_summary.parquet", index=False)

    readout_path = DOSSIER_ROOT / "quotes_open_casepacks_audit_v0_1.md"
    _build_readout(summary_df, readout_path)
    print(summary_df.to_string(index=False))
    print(f"\nreadout={readout_path}")


if __name__ == "__main__":
    main()
