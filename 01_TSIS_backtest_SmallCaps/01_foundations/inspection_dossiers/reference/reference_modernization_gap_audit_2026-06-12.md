# Reference Modernization Gap Audit - 2026-06-12

## 1. Veredicto

`reference` no esta todavia a la altura de excelencia de `daily`, `quotes`, `trades`, `minute` o `1m_split_normalized`.

La conclusion exacta es:

```text
reference esta institucionalizado como foundation layer minima, pero no esta cerrado como dossier inspector moderno.
```

Lo que se creo en `v0.4.43` es correcto como primera promocion documental:

- dataset contract;
- registry entry;
- consumption policy;
- validators contract;
- closeout compacto;
- enlaces a canonical schemas;
- enlace a auditoria historica.

Pero eso no iguala el estandar moderno que el propio proyecto exige para bloques auditados grandes.

## 2. Benchmark usado

Se comparo `reference` contra los bloques maduros:

- `daily`
- `quotes`
- `trades`
- `minute / ohlcv_1m_raw`
- `1m_split_normalized`

El estandar comun extraido es:

- lectura general a particular;
- mapa poblacional;
- distribuciones y masas;
- coverage o expected universe;
- evidence families;
- casos individuales;
- decision de consumo;
- manifests versionados;
- assets consumidos por markdown;
- imagenes incrustadas cuando la evidencia es visual;
- texto por grafico/caso con `Que muestra / Responde / No responde / Consecuencia`;
- builder/script reproducible;
- README local;
- actualizacion de `inspection_dossiers/README.md`;
- changelog cuando cambia madurez o consumo.

## 3. Estado estructural observado

Conteo de dossiers a 2026-06-12:

| Dossier | Dirs | Files | MD | IPYNB | PNG | CSV | Parquet |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `daily` | 18 | 374 | 9 | 0 | 181 | 172 | 7 |
| `minute` | 7 | 93 | 4 | 7 | 73 | 7 | 2 |
| `1m_split_normalized` | 6 | 58 | 6 | 2 | 44 | 5 | 1 |
| `quotes` | 101 | 720 | 103 | 0 | 611 | 5 | 1 |
| `trades` | 24 | 533 | 19 | 2 | 495 | 9 | 7 |
| `reference` | 0 | 1 | 1 | 0 | 0 | 0 | 0 |

Interpretacion:

- `reference` tiene un closeout compacto.
- No tiene README local hasta este upgrade documental.
- No tiene evidence assets activos en `01_foundations`.
- No tiene manifests modernos.
- No tiene population visuals.
- No tiene casepacks.
- No tiene builder/script en `scripts/inspection/reference/`.
- No tiene trazabilidad de casepacks.
- No tiene readout v0.2 con evidencia general-a-particular.

## 4. Evidencia real disponible

El problema no es falta de evidencia. Hay material suficiente.

Cache historico:

- `reference_endpoint_inventory.parquet`
- `reference_download_audit_summary.parquet`
- `reference_download_error_summary.parquet`
- `reference_schema_summary.parquet`
- `reference_identity_quality_summary.parquet`
- `reference_identity_case_index.parquet`
- `reference_listing_snapshots.parquet`
- `reference_listing_snapshot_summary.parquet`
- `reference_ticker_presence_timeline.parquet`
- `reference_snapshot_presence_gaps.parquet`
- `reference_remap_candidates.parquet`
- `reference_transient_symbol_review.parquet`
- `reference_events_exploded.parquet`
- `reference_event_type_summary.parquet`
- `reference_split_case_index.parquet`
- `reference_splits_summary.parquet`
- `reference_dividend_case_index.parquet`
- `reference_dividends_summary.parquet`
- `reference_overview_market_identity_links.parquet`
- `reference_split_market_link_candidates.parquet`
- `reference_split_daily_link_candidates.parquet`
- `reference_split_1m_link_candidates.parquet`
- `reference_event_halt_link_candidates.parquet`
- `reference_event_quotes_link_candidates.parquet`
- `reference_causal_alignment_summary.parquet`

Certification historica obligatoria:

- `certification/reference/00_reference_current_state.md`
- `certification/reference/01_reference_causal_value.md`
- `certification/reference/02_reference_closeout.md`

## 5. Radiografia factual observada

Root fisico actual:

- `E:/TSIS/data/reference`

Subfamilias fisicas:

- `all_tickers`: `3109` parquet files
- `overview`: `12468` ticker dirs, `12468` parquet files
- `events`: `12468` ticker dirs, `12468` parquet files
- `splits`: `12468` ticker dirs, `12468` parquet files
- `dividends`: `12468` ticker dirs, `12468` parquet files
- `exchanges`: `1` parquet file
- `ticker_types`: `1` parquet file
- `_run`: sin parquet, pero con artifacts operacionales no-parquet

Resumen historico clave:

- `good_identity_snapshot = 12093` rows (`96.99%`)
- `bad_unresolved_identity = 200` rows (`1.60%`)
- `review_transient_symbol = 175` rows (`1.40%`)
- `ok_event / ticker_change = 6953` rows
- `empty_events_payload = 6262` rows
- `good_split_event = 5902` rows
- `review_no_split_payload = 9007` rows
- `good_dividend_event = 266586` rows
- `review_no_dividend_payload = 7213` rows
- `ticker_change_near_halt = 775`
- `reference_event_near_halt_review = 173`
- `ticker_change_near_quotes_anomaly = 2330`
- `reference_event_near_quotes_review = 247`
- `reference_event_near_quotes_clean = 18`
- `split_explains_trade_scale_mismatch = 9`
- `split_near_scale_mismatch_review = 13`
- `review_no_daily_alignment = 21`
- `daily_split_ratio_review = 1`
- `review_no_1m_alignment = 21`
- `m1_split_ratio_review = 1`

## 6. Gaps concretos

### Gap 1 - No hay dossier inspector moderno

`reference_institutional_closeout_v0_1.md` resume conclusiones, pero no muestra evidencia general-a-particular.

Debe existir:

- `reference_inspection_readout_v0_2.md`
- population visuals;
- manifests;
- casepacks.

### Gap 2 - Falta absorber `certification/reference`

La primera promocion cita auditoria, pero no incorpora con suficiente autoridad:

- `00_reference_current_state.md`
- `01_reference_causal_value.md`
- `02_reference_closeout.md`

Esto contradice la regla de source hierarchy aplicada a bloques certificados.

### Gap 3 - No hay assets activos bajo `01_foundations`

Los caches historicos existen, pero no estan copiados, resumidos, versionados ni consumidos como evidence assets modernos.

Debe haber:

- cache inventory manifest;
- physical root audit summary;
- population visual manifest;
- casepack manifests;
- trazabilidad entre cache historico, output moderno y markdown que consume cada asset.

### Gap 4 - No hay visuals

El proyecto ya formalizo que una tabla o imagen no puede ser muda.

`reference` necesita visuals, por lo menos:

- endpoint/download status;
- identity quality distribution;
- listing presence/gaps;
- events payload/event type;
- split payload and ratio families;
- dividend payload/type families;
- causal alignment matrix;
- events vs halts timing;
- events vs quotes anomaly timing/severity;
- splits vs trades/daily/1m status.

### Gap 5 - No hay casepacks

Familias minimas:

- identity good/review/bad;
- transient symbols;
- overview 404;
- splits good/no payload/split-vs-trades good/review;
- dividends good/no payload/non-CD tail when present;
- events ticker_change near halts;
- events ticker_change near quotes anomalies;
- identity residual vs trades;
- listing presence gaps.

### Gap 6 - Validators no son ejecutables

`reference_validators.md` fija el contrato, pero no existe runner versionado ni output reproducible.

Debe existir por lo menos:

- `scripts/inspection/reference/audit_reference_foundation_physical_root.py`
- output `evidence_assets/physical_root_audit/*`
- manifest con `run_id`, root, counts, schema conformance, hard fails y review counts.

### Gap 7 - Maturity index sobreafirma

`inspection_dossiers/README.md` describia `reference` como alta madurez por compactacion. Eso es defendible para promocion contractual, pero no para paridad inspector-forense.

Se corrige la lectura:

```text
reference = promocion foundation minima; upgrade inspector moderno pendiente.
```

## 7. Roadmap recomendado

### Fase A - Reconciliacion de fuentes

Leer y mapear:

- contratos raiz;
- AGENTS/LOCAL_RULES/README/CHANGELOG de modulo 01;
- `inspection_dossier_model.md`;
- `auditoria_and_certification_source_hierarchy.md`;
- auditoria/reference;
- certification/reference;
- cache_v2/manifest.json;
- root fisico `E:/TSIS/data/reference`.

Output:

- `evidence_assets/historical_cache_inventory/reference_historical_cache_inventory_v0_1.csv`
- `evidence_assets/historical_cache_inventory/reference_historical_cache_inventory_v0_1.md`

### Fase B - Auditoria fisica moderna

Auditar `E:/TSIS/data/reference` sin mover nada.

Output:

- `evidence_assets/physical_root_audit/reference_physical_root_audit_v0_1.csv`
- `evidence_assets/physical_root_audit/reference_schema_conformance_v0_1.csv`
- `evidence_assets/physical_root_audit/reference_physical_root_audit_summary_v0_1.md`

### Fase C - Population visual overview

Crear visuals generales:

- download/endpoint status;
- identity status;
- listing presence;
- instrument/exchange mix;
- event payload/event type;
- splits/dividends payload;
- causal alignment matrix;
- timing overlays.

Output:

- `evidence_assets/population_visual_overview/*.png`
- `evidence_assets/population_visual_overview/reference_population_visual_manifest_v0_1.csv`

### Fase D - Casepacks

Crear casepacks versionados por familia.

Output minimo:

- `good_justification/reference_good_cases_v0_1.md`
- `flagged_case_evidence_packs/reference_review_cases_v0_1.md`
- `bad_case_evidence_packs/reference_bad_identity_cases_v0_1.md`
- `causal_case_evidence_packs/reference_causal_overlay_cases_v0_1.md`
- `coverage_case_evidence_packs/reference_presence_coverage_cases_v0_1.md`
- manifests CSV por carpeta.

### Fase E - Readout v0.2

Crear:

- `reference_inspection_readout_v0_2.md`

Debe incrustar visuals y explicar cada uno con:

- `Que muestra`
- `Responde`
- `No responde`
- `Consecuencia`

### Fase F - Trazabilidad y cierre

Crear:

- `reference_casepacks_traceability_audit_v0_1.md`
- `build_reference_inspection_pack.md`

Actualizar:

- `reference/README.md`
- `inspection_dossiers/README.md`
- `reference_dataset_contract_v0_1.md` si cambia frontera semantica;
- `reference_consumption_policy.md` si cambia consumo;
- `reference_registry_entry.yaml` si cambia estado o evidence refs;
- `CHANGELOG.md`.

## 8. Decision operativa

No conviene pasar ahora a `Halts` como si `reference` estuviera a la misma altura que los bloques maduros.

La secuencia correcta es:

1. cerrar el upgrade moderno de `reference`;
2. despues continuar con `Halts`, porque `Halts` depende de `reference/events` para una parte importante de su lectura causal;
3. luego `financial`;
4. luego `regime_indicators`;
5. luego `images_Flash_Research` solo si se confirma consumidor real.

## 9. Regla final

`reference` debe convertirse en el dossier puente entre identidad/corporate actions/eventos y el resto de la auditoria.

Si queda solo como closeout compacto, los futuros agentes seguiran entendiendo las conclusiones, pero no podran inspeccionar la evidencia con la misma calidad que ya existe en `quotes`, `trades`, `daily` y `1m`.