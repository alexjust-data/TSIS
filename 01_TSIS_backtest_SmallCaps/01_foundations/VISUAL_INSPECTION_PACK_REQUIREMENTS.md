# Visual Inspection Pack Requirements

Fecha: 2026-06-20
Estado: contrato operativo para cerrar deuda visual de auditorias de data.

## 1. Rol

Este documento fija que tipo de imagenes debe producir cada familia antes de
ser considerada completa al nivel de `trades`, `quotes`, `daily`, `minute` y
`ohlcv_1m_split_normalized`.

No sustituye:

- `FOUNDATIONS_FAMILY_COMPLETION_STANDARD.md`
- `DATA_AUDIT_QUALITY_STANDARD.md`
- contracts, schemas, policies, registries o validators.

Su funcion es convertir la exigencia humana en una cola visual concreta por
familia.

## 2. Regla

El estandar visual minimo es:

```text
population map
+ coverage map
+ quality-state distribution
+ good/pass visual cases
+ flagged/review visual cases
+ bad/blocking visual cases
+ manifest
+ asset audit
+ explicacion por imagen o familia visual
```

Una familia puede usar graficos agregados, paneles de timeline, heatmaps,
tablas renderizadas, small multiples, scatterplots, matrices o paneles de casos.
Lo importante es que el inspector vea la estructura y los errores sin depender
solo de CSVs.

## 3. Estados visuales

| Estado | Significado |
| --- | --- |
| `visual_complete` | Existe visual inspector pack suficiente para el scope declarado. |
| `visual_partial` | Existen algunas imagenes, pero falta pack formal, casos o asset audit. |
| `visual_required` | No hay imagenes suficientes y debe construirse visual pack. |
| `visual_waiver_required` | La familia podria no beneficiarse de imagenes, pero necesita waiver explicito. |
| `visual_waived` | Existe waiver versionado y defendible. |

Sin `visual_complete` o `visual_waived`, una familia no puede llamarse
`human_inspector_ready`.

## 4. Propuesta de imagenes por familia

### `additional`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/additional/visual_inspector_pack/
```

Tambien existen dos graficos historicos de overview:

- coverage by dataset;
- quality role by family.

Imagenes generadas para cerrar:

1. `subfamily_coverage_heatmap`
   - filas: subfamilias;
   - columnas: expected files, present files, non-empty files, rows, coverage;
   - objetivo: ver rapidamente donde hay cobertura fuerte, sparse o nula.
2. `financial_context_readiness_panel`
   - income statements, balance sheets, cash flows, ratios;
   - mostrar coverage, rows y restricciones PTI;
   - objetivo: separar contexto financiero util de features no promovibles.
3. `news_attribution_risk_panel`
   - distribucion de articulos single-ticker vs multi-ticker;
   - ejemplos renderizados de atribucion ambigua;
   - objetivo: impedir leer `requested ticker` como causalidad directa.
4. `corporate_actions_reference_overlap_panel`
   - additional splits/dividends/ticker_events vs reference;
   - objetivo: mostrar por que Additional es reconciliacion secundaria.
5. `macro_context_scope_panel`
   - series macro, rango temporal y ausencia de granularidad ticker;
   - objetivo: impedir inferencia ticker-level desde macro dates.
6. `good_review_bad_context_cases`
   - buenos: financial core payloads con filing_date interpretable;
   - review: ratios sparse y news multi-ticker;
   - bad/scope: claims prohibidos para corporate actions o macro causality.

### `financial`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/financial/visual_inspector_pack/
```

Imagenes generadas:

1. `endpoint_coverage_heatmap`
   - endpoints: income, balance, cash flow, ratios;
   - ejes: downloaded tickers, missing tickers, empty/sentinel files;
   - objetivo: ver coverage real por endpoint.
2. `severe_issue_distribution`
   - barras por issue class;
   - objetivo: visualizar los 13,337 severe issues y su concentracion.
3. `temporal_issue_timeline`
   - filing_date, period_end, fiscal_year/quarter;
   - objetivo: detectar incoherencias temporales y riesgo de lookahead.
4. `empty_sentinel_case_panel`
   - ejemplos de archivos/filas sentinel vacias renderizados;
   - objetivo: explicar por que un payload legible puede ser no interpretable.
5. `multi_cik_identity_panel`
   - tickers con multiples CIK o identidad ambigua;
   - objetivo: ver riesgo de mezclar entidades.
6. `payload_schema_drift_panel`
   - columnas observadas vs esperadas por endpoint;
   - objetivo: mostrar drift de schema sin abrir CSVs.

Lectura:

```text
human_inspector_ready, but blocked_by_data_defect
```

### `Halts`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/halts/visual_inspector_pack/
```

Imagenes generadas o formalizadas:

1. `source_coverage_by_year_source`
   - FINRA/Nasdaq/Polygon u otras fuentes segun dossier;
   - objetivo: ver cobertura y huecos por fuente.
2. `event_taxonomy_distribution`
   - halt/resume/event types;
   - objetivo: explicar la masa por taxonomia.
3. `multisource_reconciliation_panel`
   - matches, source-only, conflicts;
   - objetivo: ver que fuente sostiene cada decision.
4. `causal_overlay_cases`
   - ejemplos de halt con price/volume context;
   - objetivo: entender si el evento es regulatorio/contextual y no OHLCV.
5. `bad_residual_cases`
   - ejemplos visuales de eventos no reconciliados o ambiguos.

### `intraday_regime_features`

Estado actual:

```text
visual_complete_scoped
```

Visual inspector pack:

```text
inspection_dossiers/intraday_regime_features/visual_inspector_pack/
```

El pack formal contiene 5 paneles agregados nuevos y las 10 imagenes de
semantic pilot copiadas al contenedor gobernado.

Imagenes generadas o formalizadas para cerrar scope actual:

1. `pilot_population_map`
   - 8 tickers, 243 ticker-day rows, feature columns;
   - objetivo: visualizar el tamano real del piloto.
2. `split_feature_delta_cases`
   - los casos actuales BNGO, CEI, BXRX, COSM, EFSH, LIVE, PD, SAVA;
   - objetivo: explicar por que `1m_split_normalized` importa.
3. `control_cases_panel`
   - BXRX 2022-11 y BNGO 2025-02;
   - objetivo: demostrar que no se inventan deltas sin evento.
4. `lookback_boundary_null_panel`
   - lookback windows y nulls esperados;
   - objetivo: separar defecto de frontera natural.
5. `provenance_matrix`
   - intraday price view raw vs cross-session split-normalized;
   - objetivo: proteger semantica de features.
6. `production_boundary_panel`
   - piloto vs full-universe no materializado;
   - objetivo: impedir promocion indebida.

### `ohlcv_1m_raw`

Estado actual:

```text
visual_complete_scoped
```

Mantener y ampliar solo si cambia la politica. Visuales existentes:

- mapas poblacionales core/vw;
- 60 imagenes de caso;
- contact sheets;
- lectura por familia core/vw.

Imagenes futuras si se modifica:

1. `vw_recalculation_delta_panel`
2. `schema_merge_conflict_examples`
3. `coverage_gap_month_examples`
4. `core_good_vs_vw_bad_comparison`

### `ohlcv_1m_split_normalized`

Estado actual:

```text
visual_complete_scoped
```

Mantener el visual inspector pack existente.

Imagenes futuras requeridas si se materializa full-universe:

1. `full_universe_split_event_population_map`
2. `reverse_split_before_after_panels`
3. `forward_split_before_after_panels`
4. `no_split_control_panels`
5. `coverage_limited_event_panels`
6. `factor_integrity_distribution`

### `ohlcv_daily_adjusted`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/daily_adjusted/visual_inspector_pack/
```

Imagenes generadas:

1. `raw_vs_adjusted_factor_population_map`
2. `ticker_year_coverage_heatmap`
3. `bad_factor_or_missing_factor_panel`
4. `complex_corporate_action_tail_cases`
5. `daily_return_label_consumer_alignment_panel`

### `daily`

Estado actual:

```text
visual_complete
```

Mantener como benchmark.

Visuales existentes:

- good sample;
- non-good quality;
- hard invalid;
- coverage historical assets;
- daily adjusted / corporate action tail evidence.

Imagenes futuras si cambia el dataset:

1. `coverage_frontier_update`
2. `hard_invalid_tail_update`
3. `adjusted_factor_regression_cases`

### `quotes`

Estado actual:

```text
visual_complete
```

Mantener como benchmark.

Visuales existentes:

- global taxonomy and severity;
- per-case raw window;
- full session context;
- structure diagnostics;
- summary card;
- adjusted proxy context when relevant.

Imagenes futuras si cambia la policy:

1. `open_bucket_resolution_panel`
2. `external_context_not_rehabilitating_panel`
3. `positive_cross_policy_update`

### `reference`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/reference/visual_inspector_pack/
```

Imagenes generadas o formalizadas:

1. `identity_population_map`
2. `ticker_lifecycle_timeline_cases`
3. `corporate_action_presence_panel`
4. `identity_conflict_case_panel`
5. `quotes_reference_alignment_cases`
6. `bad_unresolved_identity_examples`

### `regime_indicators`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/regime_indicators/visual_inspector_pack/
```

Imagenes generadas:

1. `daily_date_collapse_panel`
   - fecha/datetime real vs 1970;
   - objetivo: mostrar visualmente el blocker.
2. `daily_file_date_heatmap`
   - archivos ETF/index y fecha minima/maxima;
   - objetivo: ver que el defecto no es un caso aislado.
3. `minute_high_low_inversion_panel`
   - casos UVXY con `high < low`;
   - objetivo: distinguir defecto OHLC real de ruido de perfil.
4. `minute_coverage_and_readability_map`
   - files legibles, rows, date ranges;
   - objetivo: separar daily blocked de minute review.
5. `metadata_good_examples`
   - assets metadata interpretables;
   - objetivo: mostrar que no todo el root esta inutilizable.
6. `blocked_vs_scoped_consumption_panel`
   - daily prohibido, minute review/scoped;
   - objetivo: proteger consumidores.

Lectura:

```text
human_inspector_ready, but daily_bars_blocked_minute_bars_review_only
```

### `short_review`

Estado actual:

```text
visual_complete
```

Visual inspector pack:

```text
inspection_dossiers/short_review/visual_inspector_pack/
```

Imagenes generadas:

1. `finra_short_interest_coverage_timeline`
   - tickers/rows por fecha;
   - objetivo: ver coverage oficial/free.
2. `short_volume_duplicate_key_concentration`
   - exceso por ticker y date;
   - objetivo: explicar los 5,250 duplicate excess rows.
3. `duplicate_key_case_panel`
   - CPS, OP, LFTR y otros concentradores;
   - objetivo: ver casos concretos de clave duplicada.
4. `finra_vs_local_overlap_panel`
   - overlap, FINRA-only, local-only;
   - objetivo: explicar scope/history boundaries.
5. `numeric_sanity_panel`
   - negativos, infinito, nulls y rangos;
   - objetivo: mostrar que el problema dominante no es numeric sanity.
6. `provenance_and_history_boundary_panel`
   - fuente oficial/free vs replacement prohibido;
   - objetivo: impedir promocion como short replacement completo.

Lectura:

```text
human_inspector_ready_scoped, but not a production short replacement
```

### `trades`

Estado actual:

```text
visual_complete
```

Mantener como benchmark.

Visuales existentes:

- global universe images;
- family casepacks good/review/bad/reference-scale;
- microstructure review;
- 1m reference alignment;
- historical assets.

Imagenes futuras si cambia la policy:

1. `review_rehabilitation_update`
2. `bad_data_subfamily_update`
3. `reference_scale_mismatch_update`
4. `odd_lot_or_duplicate_policy_update`

## 5. Work order

Prioridad de cierre visual:

```text
sin familias pendientes en esta matriz
```

Completado en este bucle:

1. `financial`
2. `regime_indicators`
3. `short_review`
4. `additional`
5. `intraday_regime_features`
6. `Halts`
7. `reference`
8. `ohlcv_daily_adjusted`

`daily`, `quotes`, `trades`, `ohlcv_1m_raw` y
`ohlcv_1m_split_normalized` se mantienen como benchmarks y solo se actualizan
si cambia su policy, scope o data.

## 6. Regla de implementacion

Cada familia debe cerrar con:

```text
visual_inspector_pack/README.md
visual_inspector_pack/<family>_visual_inspector_pack_v0_1.md
visual_inspector_pack/<family>_visual_case_manifest_v0_1.csv
visual_inspector_pack/<family>_visual_asset_audit_v0_1.csv
visual_inspector_pack/images/*.png
```

No basta con generar imagenes. El markdown debe explicar cada visual o familia
visual con:

```text
Que muestra
Responde
No responde
Consecuencia
```

Hasta que esa estructura exista, el estado correcto es:

```text
foundations_completion_status = visual_casepack_required
```
