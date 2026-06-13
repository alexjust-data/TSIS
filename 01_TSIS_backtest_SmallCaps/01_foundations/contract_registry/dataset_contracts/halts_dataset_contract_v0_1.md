# Halts Dataset Contract v0.1

## 1. Rol

Este contrato institucionaliza `halts_v0_1` como capa oficial de eventos de halt/suspension dentro del modulo 01.

`halts` no es una tabla de precio ni una senal de estrategia. Es una familia de artefactos oficiales y derivados que permiten:

- localizar eventos de trading halt;
- separar halt intradia completo de contexto regulatorio;
- anotar ventanas temporales sobre `quotes`, `trades`, `daily` y `ohlcv_1m`;
- explicar segmentos de microestructura bajo evento;
- y mantener evidencia reproducible para backtest, ML y auditoria sin depender de memoria conversacional.

## 2. Identidad del dataset

- `dataset_id`: `halts_v0_1`
- `domain`: `halts`
- `contract_type`: `official_event_reference_dataset`
- `logical_version`: `v0_1`
- `promotion_state`: `modern_dossier_complete_for_foundation_promotion`
- `active`: `true`

## 3. Raiz fisica canonica

Raiz operativa actual:

- `E:\TSIS\data\Halts`

Raiz historica observada y preservada:

- `D:\Halts`

El root audit moderno verifica que ambas raices tienen la misma huella agregada en el momento de esta promocion:

- `5702` files;
- `5` parquets;
- `17` CSV;
- `5662` XML;
- `16` HTML;
- `2` JSON;
- `392678889` bytes.

La raiz canonica para nuevos contratos TSIS es `E:\TSIS\data\Halts`. `D:\Halts` queda como compatibilidad historica observada.

## 4. Fuentes oficiales gobernadas

Fuentes upstream:

- Nasdaq Trader halts;
- NYSE halts;
- SEC suspensions.

El dataset combina:

- raw official downloads;
- source-specific outputs;
- master multisource;
- summaries operacionales;
- coverage summaries;
- overlays historicos contra market data.

## 5. Que representa

`halts` representa:

- eventos oficiales de halt/suspension;
- fecha de halt;
- hora de inicio y reanudacion cuando existe;
- fuente oficial;
- codigo/tipo de halt cuando existe;
- issuer/name contextual;
- links o release numbers de fuente;
- taxonomia institucional de evento;
- cobertura frente al universo `<1B>`;
- y evidencia de coherencia o tension contra `quotes` y `trades`.

## 6. Que no representa

`halts` no representa:

- precio observado;
- libro `bid/ask`;
- prints de ejecucion;
- OHLCV diario o intradia;
- liquidez normal;
- elegibilidad de universo;
- continuidad corporativa;
- ni una senal de trading.

Reglas criticas:

- un halt no autoriza por si solo una estrategia;
- una ausencia de halt no prueba mercado limpio;
- un evento SEC sin timestamp intradia no debe tratarse como ventana operable;
- un bucket visual contra `quotes` o `trades` no reemplaza el evento oficial;
- y una senal de microestructura sin halt claro queda en review, no en good.

## 7. Artefactos canonicos

Schemas activos:

- `01_foundations/canonical_schemas/halts/halts_master_multisource_schema_contract.md`
- `01_foundations/canonical_schemas/halts/halts_operational_summary_schema_contract.md`
- `01_foundations/canonical_schemas/halts/halts_raw_sources_schema_contract.md`
- `01_foundations/canonical_schemas/halts/halts_source_specific_outputs_schema_contract.md`
- `01_foundations/canonical_schemas/halts/halts_universe_coverage_schema_contract.md`

Dossier moderno activo:

- `01_foundations/inspection_dossiers/halts/halts_inspection_readout_v0_1.md`
- `01_foundations/inspection_dossiers/halts/build_halts_inspection_pack.md`
- `01_foundations/inspection_dossiers/halts/halts_casepacks_traceability_audit_v0_1.md`
- `01_foundations/inspection_dossiers/halts/evidence_assets/run_manifest.json`
- `01_foundations/inspection_dossiers/halts/evidence_assets/population_visual_overview/`
- `01_foundations/inspection_dossiers/halts/evidence_assets/case_manifest/halts_case_manifest_v0_1.md`

## 8. Evidencia historica

La promocion se apoya en auditoria preservada bajo:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/`

Documentos historicos principales:

- `00_descarga_datos_halts.md`
- `01_contrato_halts.md`
- `02_diseno_implementacion_halts_v2.md`
- `03_halts_root_cause_audit_phase1_closeout.md`
- `04_halts_causal_overlay_closeout.md`
- `04_halts_closeout.md`

Certification historica obligatoria:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/00_halts_current_state.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/01_halts_overlay_and_recovery.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/02_halts_quality_policy.md`
- `01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/03_halts_closeout.md`

Cache historico preservado:

- `01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/cache_v2/`

El dossier moderno no copia parquets historicos pesados. Los inventaria, resume y enlaza como fuente de verdad preservada.

## 9. Foto poblacional institucional

### Source quality

| Source | Rows | Ticker non-null | Unique tickers | Semantic event keys |
| --- | ---: | ---: | ---: | ---: |
| `nasdaq` | 119630 | 119619 | 16572 | 118475 |
| `nyse` | 13178 | 13172 | 2568 | 12436 |
| `sec` | 1346 | 250 | 250 | 1346 |

### Canonical event taxonomy

| Event taxonomy | Events | Source rows | Tickers |
| --- | ---: | ---: | ---: |
| `good_full_intraday_event` | 129638 | 131524 | 16232 |
| `good_date_level_event` | 1272 | 1273 | 1180 |
| `review_partial_identity` | 1096 | 1096 | 0 |
| `regulatory_context_only` | 250 | 250 | 250 |
| `bad_unusable_event` | 1 | 11 | 0 |

### LT1B event taxonomy

| Event taxonomy | Events | Tickers |
| --- | ---: | ---: |
| `good_full_intraday_event` | 53720 | 3900 |
| `good_date_level_event` | 186 | 152 |
| `regulatory_context_only` | 3 | 3 |

### Visual case buckets

| Visual bucket | Rows |
| --- | ---: |
| `confirmed_halt_microstructure_coherent` | 18591 |
| `halt_with_trades_signal_only` | 3914 |
| `halt_with_quotes_signal_only` | 1896 |
| `halt_present_but_market_clean` | 516 |
| `market_signal_without_clear_halt_window` | 384 |

## 10. Politica de calidad

### Estados `good`

- `good_full_intraday_event`
- `good_date_level_event`
- `confirmed_halt_microstructure_coherent`

`good_date_level_event` es good para contexto de evento/date-level, no para simulacion intradia con ventana exacta.

### Estados `review`

- `review_partial_identity`
- `regulatory_context_only` cuando se pretenda uso intradia;
- `halt_with_trades_signal_only`
- `halt_with_quotes_signal_only`
- `halt_present_but_market_clean`
- `market_signal_without_clear_halt_window`

### Estados `bad`

- `bad_unusable_event`

La familia `bad` agregada observada es marginal: `1` evento canonico que recoge `11` source rows residuales Nasdaq sin payload util.

## 11. Consumidores permitidos

Permitidos bajo contrato y policy:

- `event_engine`
- `data_audit_overlay`
- `forensic_review`
- `quotes_halt_overlay`
- `trades_halt_overlay`
- `minute_halt_overlay`
- `daily_event_context`
- `backtest_event_mask_candidate` solo con flags y temporalidad declarada;
- `research_only`.

## 12. Consumidores restringidos

Requieren contrato adicional o flags:

- `backtest_core`
- `backtest_extended`
- `ml_flagged`
- `execution_simulator`
- `live_downstream_candidate`
- `rl_allowed`
- cualquier sistema que convierta halts en alpha.

Reglas:

- backtest puede usar halts como mask/contexto cuando se declare decision-time availability;
- ML puede usar halts solo con lag, flags y bloqueo de leakage;
- execution puede usar halts para contexto o suspension windows, no como ejecucion observada;
- live y RL quedan bloqueados hasta contratos posteriores.

## 13. Limitaciones conocidas

- SEC suspensions aportan contexto regulatorio, pero normalmente no hora intradia.
- `review_partial_identity` no debe mezclarse con eventos intradia completos.
- `halt_present_but_market_clean` no prueba error de halt; puede reflejar coverage o ventanas sin senal visible.
- `market_signal_without_clear_halt_window` no prueba evento oficial.
- La cobertura `<1B>` refleja tickers con eventos matcheados, no una obligacion de que todo ticker tenga halt.
- La evidencia visual historica se resume en casepacks modernos; los parquets fuente permanecen en `01_research`.

## 14. Validators requeridos

El contrato requiere:

- `01_foundations/validators/halts/halts_validators.md`

Antes de abrir consumidores sensibles deben existir checks o evidencia equivalente para:

- presencia de root y processed master;
- conformidad de schema multisource;
- parseabilidad de fechas/hora ET;
- source allowlist;
- deduplicacion y reconciliacion multisource;
- taxonomia de evento;
- separacion good/review/bad;
- cobertura `<1B>` si aplica;
- y coherencia visual/forense cuando se use como explicacion de market data.

## 15. Politica de cambio

Debe versionarse o registrarse en changelog cuando cambie:

- raiz fisica canonica;
- fuentes oficiales;
- schema master;
- taxonomia de evento;
- allowed consumers;
- semantica de SEC/regulatory context;
- tratamiento de ausencia de halt;
- o rol de halts en backtest, ML, live, RL o execution.

## 16. Veredicto operacional

`halts_v0_1` queda institucionalizado como event/reference layer activa con dossier inspector moderno.

La capa es fuerte para:

- evento oficial;
- contexto regulatorio;
- overlays forenses;
- y masks/event context con flags.

No habilita por si sola:

- alpha;
- live trading;
- RL;
- execution simulation final;
- ni consumo intradia sin distinguir eventos completos, date-level, SEC y review.
