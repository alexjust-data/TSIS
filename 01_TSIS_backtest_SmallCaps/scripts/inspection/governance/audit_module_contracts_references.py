from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_CONTRACTS_ROOT = PROJECT_ROOT / "01_foundations" / "module_contracts"
OUT_DIR = MODULE_CONTRACTS_ROOT / "evidence_assets" / "module_contracts_reference_audit"

TEXT_GLOBS = ("*.md", "*.ipynb", "*.py", "*.yaml", "*.yml")
SKIP_PARTS = {".git", ".venv", "__pycache__"}


def _iter_project_files() -> list[Path]:
    files: list[Path] = []
    for pattern in TEXT_GLOBS:
        for path in PROJECT_ROOT.rglob(pattern):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(path)
    return sorted(set(files))


def _module_contract_docs() -> dict[str, Path]:
    return {p.name: p for p in MODULE_CONTRACTS_ROOT.glob("*.md")}


def _future_target_for(name: str) -> str:
    if name in {
        "README.md",
        "module_contracts_migration_map_v0_1.md",
        "state_snapshot_standard.md",
        "policy_explanation_standard.md",
        "layer_validation_standard_v0_1.md",
        "layer_maturity_assessment_v0_1.md",
        "foundations_transversal_final_review_v0_1.md",
        "foundations_transversal_final_review_v0_2.md",
    }:
        return f"module_contracts/governance/{name}"
    if name in {
        "consumer_classes.md",
        "daily_return_labels_consumer_contract_v0_1.md",
        "daily_return_labels_operational_landing_v0_1.md",
        "intraday_regime_features_consumer_contract_v0_1.md",
        "intraday_regime_features_variable_taxonomy_v0_1.md",
        "intraday_regime_features_operational_landing_v0_1.md",
        "intraday_regime_features_initial_materialization_results_v0_1.md",
        "intraday_regime_features_semantic_pilot_results_v0_1.md",
        "intraday_regime_features_deferred_families_v0_1.md",
        "price_view_consumer_integration_status.md",
        "price_view_integration_priority_plan_v0_1.md",
    }:
        return f"module_contracts/consumers/{name}"
    if name in {
        "daily_acceptance_policy_explained.md",
        "daily_rules_explained_line_by_line.md",
        "daily_adjusted_full_universe_promotion_plan_v0_1.md",
        "daily_adjusted_incremental_materialization_plan_v0_1.md",
        "daily_adjusted_operational_landing_v0_1.md",
        "daily_adjusted_pilot_manifest_v0_1.md",
        "daily_adjusted_pilot_results_v0_1.md",
        "daily_adjusted_pilot_results_v0_2.md",
    }:
        return f"module_contracts/daily/{name}"
    if name in {
        "quotes_acceptance_policy_explained.md",
        "quotes_rules_explained_line_by_line.md",
    }:
        return f"module_contracts/quotes/{name}"
    if name in {
        "trades_acceptance_policy_explained.md",
        "trades_rules_explained_line_by_line.md",
    }:
        return f"module_contracts/trades/{name}"
    if name in {
        "ohlcv_1m_split_normalized_incremental_materialization_plan_v0_1.md",
        "ohlcv_1m_split_normalized_operational_landing_v0_1.md",
        "ohlcv_1m_split_normalized_pilot_manifest_v0_2.md",
        "ohlcv_1m_split_normalized_pilot_results_v0_1.md",
        "ohlcv_1m_split_normalized_semantic_pilot_v0_1.md",
    }:
        return f"module_contracts/minute/{name}"
    return f"module_contracts/transversal/{name}"


def main() -> None:
    docs = _module_contract_docs()
    if not docs:
        raise RuntimeError("No module_contracts markdown files found.")

    file_regex = "|".join(re.escape(name) for name in sorted(docs))
    path_pattern = re.compile(
        rf"(?P<raw>(?:[A-Za-z]:[\\/][^\s`<>\"\)\]]*?[\\/])?module_contracts[\\/](?P<name>{file_regex})|(?:01_foundations[\\/])module_contracts[\\/](?P<name2>{file_regex})|(?:\.\./)+(?:module_contracts[\\/])(?P<name3>{file_regex}))"
    )

    rows: list[dict[str, object]] = []
    for src in _iter_project_files():
        try:
            text = src.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel_src = src.relative_to(PROJECT_ROOT).as_posix()
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in path_pattern.finditer(line):
                target_name = match.group("name") or match.group("name2") or match.group("name3")
                if not target_name:
                    continue
                rows.append(
                    {
                        "source_file": rel_src,
                        "line_no": line_no,
                        "target_name": target_name,
                        "current_canonical_path": f"01_foundations/module_contracts/{target_name}",
                        "future_target_path": _future_target_for(target_name),
                        "matched_reference": match.group("raw") or match.group(0),
                        "source_kind": src.suffix.lower(),
                    }
                )

    ref_df = pd.DataFrame(rows).sort_values(["target_name", "source_file", "line_no"]).reset_index(drop=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ref_df.to_csv(OUT_DIR / "module_contracts_reference_hits.csv", index=False)
    ref_df.to_parquet(OUT_DIR / "module_contracts_reference_hits.parquet", index=False)

    if ref_df.empty:
        summary_df = pd.DataFrame(
            [
                {
                    "target_name": "",
                    "current_canonical_path": "",
                    "future_target_path": "",
                    "reference_hits": 0,
                    "unique_source_files": 0,
                }
            ]
        )
    else:
        summary_df = (
            ref_df.groupby(["target_name", "current_canonical_path", "future_target_path"], dropna=False)
            .agg(
                reference_hits=("target_name", "size"),
                unique_source_files=("source_file", "nunique"),
            )
            .reset_index()
            .sort_values(["unique_source_files", "reference_hits", "target_name"], ascending=[False, False, True])
        )
    summary_df.to_csv(OUT_DIR / "module_contracts_reference_summary.csv", index=False)
    summary_df.to_parquet(OUT_DIR / "module_contracts_reference_summary.parquet", index=False)

    source_summary_df = (
        ref_df.groupby(["source_file", "source_kind"], dropna=False)
        .agg(
            reference_hits=("target_name", "size"),
            unique_targets=("target_name", "nunique"),
        )
        .reset_index()
        .sort_values(["reference_hits", "unique_targets", "source_file"], ascending=[False, False, True])
    )
    source_summary_df.to_csv(OUT_DIR / "module_contracts_reference_sources.csv", index=False)
    source_summary_df.to_parquet(OUT_DIR / "module_contracts_reference_sources.parquet", index=False)

    total_hits = int(len(ref_df))
    total_sources = int(ref_df["source_file"].nunique()) if not ref_df.empty else 0
    total_targets = int(ref_df["target_name"].nunique()) if not ref_df.empty else 0

    top_targets_lines: list[str] = []
    for _, row in summary_df.head(15).iterrows():
        if not str(row["target_name"]).strip():
            continue
        top_targets_lines.append(
            f"- `{row['target_name']}` -> `{int(row['reference_hits'])}` referencias en `{int(row['unique_source_files'])}` archivos; destino previsto: `{row['future_target_path']}`"
        )

    top_sources_lines: list[str] = []
    for _, row in source_summary_df.head(15).iterrows():
        top_sources_lines.append(
            f"- `{row['source_file']}` -> `{int(row['reference_hits'])}` referencias a `module_contracts` sobre `{int(row['unique_targets'])}` documentos objetivo"
        )

    readout_lines = [
        "# Module Contracts Reference Pre-Audit v0.1",
        "",
        "## Rol",
        "",
        "Este documento mide cuantas referencias a paths planos de `module_contracts` siguen vivas en el proyecto antes de cualquier migracion fisica real.",
        "",
        "## Que se considero una referencia relevante",
        "",
        "- menciones a `01_foundations/module_contracts/<documento>.md`",
        "- menciones relativas del tipo `../../module_contracts/<documento>.md`",
        "- y menciones con path absoluto que siguen apuntando al root plano actual de `module_contracts`",
        "",
        "## Resultado agregado",
        "",
        f"- `reference_hits_total = {total_hits}`",
        f"- `unique_source_files = {total_sources}`",
        f"- `unique_target_documents = {total_targets}`",
        "",
        "## Targets mas citados",
        "",
        *top_targets_lines,
        "",
        "## Sources mas cargados",
        "",
        *top_sources_lines,
        "",
        "## Lectura tecnica",
        "",
        "Esta pre-auditoria no mueve nada.",
        "Su valor institucional es otro:",
        "",
        "- cuantifica la superficie real de ruptura potencial;",
        "- permite priorizar que documentos requeriran mas actualizacion si se ejecuta la migracion fisica;",
        "- y evita una migracion cosmetica que rompa referencias por volumen oculto.",
        "",
        "En particular, si un target tiene muchas referencias distribuidas en muchos archivos fuente, ese target debe tratarse como documento de alta sensibilidad de migracion.",
        "",
        "## Artefactos exportados",
        "",
        "- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_hits.csv`",
        "- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_summary.csv`",
        "- `evidence_assets/module_contracts_reference_audit/module_contracts_reference_sources.csv`",
        "",
        "## Veredicto",
        "",
        "El proyecto ya tiene medido el perimetro de referencias a paths planos de `module_contracts`.",
        "Eso no ejecuta la migracion, pero si convierte una futura reorganizacion en una operacion trazable en vez de una apuesta ciega.",
    ]

    (MODULE_CONTRACTS_ROOT / "module_contracts_reference_pre_audit_v0_1.md").write_text(
        "\n".join(readout_lines) + "\n",
        encoding="utf-8",
    )

    print(f"total_hits={total_hits}")
    print(f"unique_source_files={total_sources}")
    print(f"unique_target_documents={total_targets}")
    print("\nTop targets:")
    print(summary_df.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
