# Reference Dataset Contract v0.1

## 1. Rol

Este contrato institucionaliza `reference_v0_1` como capa fundacional de referencia del modulo 01.

`reference` no es una tabla unica. Es una familia de subdatasets que gobiernan:

- identidad de ticker;
- snapshots historicos de presencia;
- tipos de instrumento;
- exchanges y venues;
- corporate actions;
- eventos de continuidad;
- artefactos operacionales de descarga.

Su funcion principal es evitar que backtest, ML, price views, event overlays y auditorias de market data dependan de memoria conversacional o de inferencias desde nombres de carpeta.

## 2. Identidad del dataset

- `dataset_id`: `reference_v0_1`
- `domain`: `reference`
- `contract_type`: `foundation_reference_dataset`
- `logical_version`: `v0_1`
- `promotion_state`: `modern_dossier_complete_for_foundation_promotion`
- `active`: `true`

## 3. Raiz fisica canonica

Raiz operativa actual:

- `E:\TSIS\data\reference`

Subfamilias observadas:

- `_run`
- `all_tickers`
- `overview`
- `events`
- `splits`
- `dividends`
- `exchanges`
- `ticker_types`

Nota de compatibilidad:

- varios schemas historicos fueron inspeccionados originalmente contra `D:\reference`;
- la raiz operativa actual observada para este contrato es `E:\TSIS\data\reference`;
- el layout semantico declarado por los schemas se mantiene como autoridad de forma.

## 4. Que representa

`reference` representa metadata y eventos upstream que permiten razonar sobre:

- existencia temporal de tickers;
- cambios de simbolo;
- identidad parcial de instrumentos;
- tipos de instrumentos;
- splits y reverse splits;
- dividendos;
- exchanges y venues;
- presencia en snapshots;
- lineage y errores de descarga.

## 5. Que no representa

`reference` no representa:

- precio observado;
- libro `bid/ask`;
- prints de ejecucion;
- OHLCV diario o intradia;
- membership final del universo `<1B>`;
- continuidad corporativa economica completa por si solo;
- autorizacion automatica para backtest o ML;
- ni verdad point-in-time diaria de market cap.

Un `ticker_change` no equivale por si solo a continuidad economica cerrada.
Un ticker presente en `all_tickers` no equivale por si solo a elegibilidad de universo.
Un split/dividend presente no convierte automaticamente una serie raw en adjusted.

## 6. Subfamilias gobernadas

### `all_tickers`

Snapshots fechados de presencia y metadata basica de tickers.

Uso principal:

- universo bruto;
- presencia historica;
- filtros preliminares por market, locale, exchange o type.

No sustituye:

- `lt1b_universe`;
- universe builder final;
- continuidad corporativa;
- expected coverage diario.

### `overview`

Snapshot de metadata descriptiva y fundamental por ticker/request date.

Uso principal:

- identidad;
- market cap observado;
- metadata de instrumento;
- soporte para cortes o auditorias.

No sustituye una serie point-in-time diaria completa de market cap.

### `events`

Payload de eventos corporativos de identidad y continuidad.

Evento dominante observado:

- `ticker_change`

Uso principal:

- continuidad nominal;
- overlays causales;
- deteccion de fragilidad alrededor de cambios administrativos/corporativos.

No cierra continuidad economica completa sin policy adicional.

### `splits`

Eventos de split y reverse split por ticker.

Uso principal:

- `split_normalized`;
- `daily_adjusted`;
- auditoria de scale mismatch;
- validacion de `ohlcv_1m_split_normalized`.

### `dividends`

Eventos de dividendos por ticker.

Uso principal:

- `daily_adjusted`;
- retornos economicos;
- auditoria de corporate actions.

La cola no `CD` debe permanecer declarada como frontera semantica.

### `exchanges`

Tabla de venues, MIC, participant ids y metadata de exchange.

Uso principal:

- explicacion de venues;
- enriquecimiento de microestructura;
- validacion contextual de `quotes` y `trades`.

### `ticker_types`

Diccionario de tipos de instrumento.

Uso principal:

- separar `CS`, `PFD`, `WARRANT`, `RIGHT`, `ETF`, `ETN`, `ADRC` y otros codigos;
- evitar tratar todos los tickers como common stock por defecto.

### `_run`

Artefactos operativos de descarga.

Uso principal:

- trazabilidad;
- errores;
- progreso;
- audit operacional.

No es market data ni feature productiva.

## 7. Schemas canonicos

Schemas activos:

- `01_foundations/canonical_schemas/reference/all_tickers_snapshot_schema_contract.md`
- `01_foundations/canonical_schemas/reference/overview_schema_contract.md`
- `01_foundations/canonical_schemas/reference/events_schema_contract.md`
- `01_foundations/canonical_schemas/reference/splits_schema_contract.md`
- `01_foundations/canonical_schemas/reference/dividends_schema_contract.md`
- `01_foundations/canonical_schemas/reference/exchanges_schema_contract.md`
- `01_foundations/canonical_schemas/reference/ticker_types_schema_contract.md`
- `01_foundations/canonical_schemas/reference/operational_run_schema_contract.md`

## 8. Evidencia historica

La promocion se apoya en auditoria preservada bajo:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/`

Documentos principales:

- `04_reference_closeout.md`
- `04_reference_causal_overlay_closeout.md`
- `03_reference_root_cause_audit_phase1_closeout.md`

Certification historica obligatoria:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/00_reference_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/01_reference_causal_value.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/02_reference_closeout.md`

Gap audit moderno:

- `01_foundations/inspection_dossiers/reference/reference_modernization_gap_audit_2026-06-12.md`

Dossier moderno activo:

- `01_foundations/inspection_dossiers/reference/reference_inspection_readout_v0_2.md`
- `01_foundations/inspection_dossiers/reference/build_reference_inspection_pack.md`
- `01_foundations/inspection_dossiers/reference/reference_casepacks_traceability_audit_v0_1.md`
- `01_foundations/inspection_dossiers/reference/evidence_assets/run_manifest.json`
- `01_foundations/inspection_dossiers/reference/evidence_assets/population_visual_overview/`
- `01_foundations/inspection_dossiers/reference/evidence_assets/case_manifest/reference_case_manifest_v0_1.md`

Lectura cerrada por la auditoria:

- `overview`, `all_tickers`, `events`, `splits` y `dividends` ya fueron auditados a nivel de contenido real;
- `splits -> trades` valida un frente causal quirurgico;
- `events/ticker_change -> halts` valida un frente causal fuerte;
- `events/ticker_change -> quotes` valida un frente causal fuerte pero heterogeneo;
- `identity review -> trades` aparece como frente debil en la primera muestra.

## 9. Politica de calidad

### Estados `good`

- `good_identity_snapshot`
- `good_split_event`
- `split_explains_trade_scale_mismatch`
- `ticker_change_near_halt` cuando halt y reaccion de mercado son visualmente coherentes

### Estados `review`

- `review_transient_symbol`
- `review_instrument_type_ambiguity`
- `review_no_split_payload`
- `split_near_scale_mismatch_review`
- `ticker_change_near_quotes_anomaly`
- `reference_event_near_halt_review`
- `reference_event_near_quotes_review`
- `identity_review_residual`

### Estados `bad`

- `bad_unresolved_identity`

La auditoria historica no encontro una familia agregada `bad` dominante en el overlay de mercado.

## 10. Consumidores permitidos

Permitidos bajo contrato y policy:

- `corporate_actions_service`
- `price_view_builders`
- `daily_adjusted`
- `ohlcv_1m_split_normalized`
- `universe_builder`
- `lt1b_coverage_audits`
- `event_engine`
- `data_audit_overlay`
- `forensic_review`
- `research_only`

## 11. Consumidores restringidos

Requieren contrato adicional o flags:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`
- `execution_simulator`
- `live_downstream_candidate`
- `rl_allowed`

Reglas:

- `backtest_core` puede depender de `reference` para splits/dividends/universe filtering, pero no debe consumir eventos como alpha sin lag y contrato;
- ML puede usar eventos solo con disponibilidad temporal declarada y flags;
- execution puede usar `halts/reference` como contexto, no como precio;
- live y RL requieren contratos posteriores.

## 12. Limitaciones conocidas

- `ticker_change` no cierra continuidad economica completa.
- `ticker_change_near_quotes_anomaly` es detector fuerte, pero no `good` causal limpio.
- `identity_review` no emerge como explicador dominante de `trades`.
- `splits` explican un subconjunto real de scale mismatch, no el grueso del residuo global.
- `events` es payload anidado; debe expandirse antes de validar a nivel evento.
- `all_tickers` no es universe membership final.
- `overview.market_cap` no es serie diaria point-in-time completa.

## 13. Validators requeridos

El contrato requiere:

- `01_foundations/validators/reference/reference_validators.md`

Antes de promover un consumidor nuevo, deben existir checks o evidencia equivalente para:

- schema y parseabilidad;
- unicidad de claves por subfamilia;
- validez de fechas;
- ratios split positivos;
- dividendos no negativos;
- tipos de instrumento conocidos;
- eventos `ticker_change` parseables;
- coverage/sentinel forms;
- lineage operativo.

## 14. Politica de cambio

Debe versionarse o registrarse en changelog cuando cambie:

- raiz fisica canonica;
- subfamilias gobernadas;
- interpretacion de `ticker_change`;
- tratamiento de splits/dividends;
- allowed consumers;
- quality states;
- o rol de `reference` en price views, backtest, ML o event engine.

## 15. Veredicto operacional

`reference_v0_1` queda institucionalizado como foundation layer activa con dossier inspector moderno.

Su valor principal no es solo metadata estatica:

- gobierna identidad;
- habilita price views;
- explica parte de la fragilidad observada en `quotes`, `trades` y `halts`;
- y fija barreras contra errores de continuidad, instrumento y corporate actions.

Esta promocion no habilita consumidores nuevos fuera de `reference_consumption_policy.md`.
