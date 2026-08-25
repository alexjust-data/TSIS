# Corrected RAW Daily Full Run Closeout v0.1

Fecha: 2026-08-25  
Run: `20260825_full_raw_daily_v0_1`  
Estado: `PASS_EVIDENCE_READY_LOCALHOST_ACTIVE`

## Fuente y lineage

- fuente exclusiva: `G:/TSIS/data/ohlcv_daily`;
- semántica: Massive `adjusted=true`, ajustada por splits por el proveedor;
- capa excluida: `G:/TSIS/data/ohlcv_daily_adjusted`;
- commit de ejecución: `668e13b47d7d52797eccbaff7e47be7881230b36`;
- config SHA-256: `7381df79cc16e5bf08e11c3d45f999a1446333eb78d12a2ebc35d19cf5aac677`.

## Alcance certificado

- tickers: 4.824;
- sesiones: 9.290.966;
- archivos fuente: 44.423;
- shards: 8/8 PASS;
- fechas: 2005-01-03 a 2026-03-06;
- ticker-fechas faltantes o adicionales: 0;
- fallos de shard: 0.

## Auditorías

- terminal certification: PASS;
- auditoría independiente: PASS;
- 12 fórmulas recalculadas: error absoluto máximo 0;
- schema variants: 1 por tabla sobre 4.824 parts;
- claves duplicadas/nulas e infinitos: 0;
- outcome quality, roles, lineage, artifacts y operación: PASS;
- tests Python/API: 36/36 PASS;
- app production build: PASS;
- smoke HTTP: API PASS y UI 200.

## Outputs principales

Los outputs inmutables viven bajo:
`runs/20260825_full_raw_daily_v0_1/final`.

Incluyen `terminal_certification.json`, `probe_variable_audit_v0_1.json`,
`FINAL_CENSUS_READOUT_v0_2.md`, once Parquet finales y sus hashes en
`run_manifest.json`.

## Promoción local

`start_atlas_local.ps1` y el selector Python excluyen todo run que declare la
raíz adjusted defectuosa. `http://localhost:3000` sirve este full corregido.
El run anterior se conserva como evidencia histórica invalidada y no es elegible.