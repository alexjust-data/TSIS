# Halts Inspection Dossier

## Estado

- Dataset: `halts_v0_1`
- Estado operativo: `modern_dossier_complete_for_foundation_promotion`
- Rol: capa oficial de eventos de halt/suspension y contexto regulatorio.
- Root canonico: `E:\TSIS\data\Halts`
- Root historico observado: `D:\Halts`

## Lectura obligatoria

1. `halts_inspection_readout_v0_1.md`
2. `build_halts_inspection_pack.md`
3. `halts_casepacks_traceability_audit_v0_1.md`
4. `integration_notes.md`
5. `evidence_assets/run_manifest.json`

## Contratos relacionados

- `../../contract_registry/dataset_contracts/halts_dataset_contract_v0_1.md`
- `../../dataset_registry/halts/halts_registry_entry.yaml`
- `../../data_consumption_policies/halts_consumption_policy.md`
- `../../validators/halts/halts_validators.md`
- `../../canonical_schemas/halts/`

## Evidencia moderna

Artefactos ligeros generados:

- `evidence_assets/historical_cache_inventory/`
- `evidence_assets/historical_certification_inventory/`
- `evidence_assets/physical_root_audit/`
- `evidence_assets/population_summary/`
- `evidence_assets/population_visual_overview/`
- `evidence_assets/case_manifest/`

Casepacks:

- `good_justification/halts_good_coherent_visual_cases_v0_1.md`
- `flagged_case_evidence_packs/halts_review_visual_cases_v0_1.md`
- `bad_case_evidence_packs/halts_bad_residual_cases_v0_1.md`
- `causal_case_evidence_packs/halts_causal_overlay_cases_v0_1.md`
- `coverage_case_evidence_packs/halts_universe_coverage_cases_v0_1.md`

## Evidencia historica preservada

La auditoria profunda original vive bajo:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/`

Este dossier no copia parquets historicos pesados a `01_foundations`. Los inventaria y promueve resumen, visuales, manifests y reglas de consumo.

## Regla de lectura

`halts` debe leerse como event/reference layer:

- eventos oficiales y contexto regulatorio;
- no precio;
- no tape;
- no alpha;
- no autorizacion automatica para live, RL o execution.

La decision de consumo esta en `halts_consumption_policy.md`.
