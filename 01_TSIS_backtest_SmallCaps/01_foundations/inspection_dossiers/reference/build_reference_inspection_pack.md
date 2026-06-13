# Build Reference Inspection Pack

Fecha: 2026-06-13
Estado: build guide v0.1

## Rol

Este documento describe como se genero el paquete inspector moderno de `reference`.

No sustituye el contrato del dataset.
No sustituye la auditoria historica.
No copia caches pesados.

El builder residente es:

```text
scripts/inspection/reference/build_reference_inspection_pack.py
```

## Comando

Desde `C:/TSIS_Data`:

```powershell
python "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\inspection\reference\build_reference_inspection_pack.py" --json
```

## Inputs read-only

```text
E:/TSIS/data/reference
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference
01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/cache_v2
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference
01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics
```

Ninguna de esas rutas se modifica.

## Outputs

```text
inspection_dossiers/reference/evidence_assets/run_manifest.json
inspection_dossiers/reference/evidence_assets/historical_cache_inventory/
inspection_dossiers/reference/evidence_assets/historical_certification_inventory/
inspection_dossiers/reference/evidence_assets/physical_root_audit/
inspection_dossiers/reference/evidence_assets/population_summary/
inspection_dossiers/reference/evidence_assets/population_visual_overview/
inspection_dossiers/reference/evidence_assets/case_manifest/
inspection_dossiers/reference/good_justification/
inspection_dossiers/reference/flagged_case_evidence_packs/
inspection_dossiers/reference/bad_case_evidence_packs/
inspection_dossiers/reference/causal_case_evidence_packs/
inspection_dossiers/reference/coverage_case_evidence_packs/
```

## Resultado de ejecucion

Run manifest:

- `evidence_assets/run_manifest.json`

Resultado:

- `status`: `pass`
- historical cache artifacts: `31`
- certification/global metric artifacts: `7`
- physical subfamilies audited: `8`
- population buckets promoted: `26`
- population visuals: `5`
- casepacks: `5`

## Que genera

### Historical cache inventory

Registra los parquets y manifests historicos disponibles en `cache_v2`.

No los copia a `01_foundations`.

### Historical certification inventory

Registra los markdowns de `certification/reference` y metricas `reference_*` en `global_metrics`.

### Physical root audit

Cuenta subfamilias, ficheros, parquet files y samples del root fisico actual:

```text
E:/TSIS/data/reference
```

### Population summary

Promueve tablas ligeras para:

- identity quality;
- overview 404;
- events;
- splits;
- dividends;
- causal alignment;
- download endpoint status;
- listing presence.

### Population visual overview

Genera cinco PNGs estables:

- identity quality distribution;
- download endpoint status;
- payload family distribution;
- causal alignment distribution;
- listing snapshot density.

### Casepacks

Genera casepacks representativos:

- good identity/payload;
- review identity/quotes;
- bad unresolved identity;
- causal overlays;
- presence/coverage.

## Reglas de seguridad

- No escribe en `E:/TSIS/data`.
- No escribe en `01_research`.
- No copia parquets historicos grandes a `01_foundations`.
- No crea outputs fuera del proyecto.
- No habilita consumidores nuevos.

## Regla final

Este builder promociona evidencia historica a un dossier moderno inspeccionable.

No reaudita `reference` desde cero.

