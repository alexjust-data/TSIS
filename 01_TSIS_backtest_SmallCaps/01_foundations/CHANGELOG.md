# 01 Foundations Changelog

## 2026-07-04 | market_state | event candidate executable validators fixture-scope

- Se crea `scripts/validate_event_candidate_tables.py` como primera implementacion ejecutable fixture-scope del contrato `event_candidate_table_validators_contract_v0_1.md`.
- Se crean fixtures minimos daily/intradia en `tests/fixtures/data_foundation_outputs/event_candidate_tables_v0_1/`.
- Se crea `tests/data_foundation_outputs/test_event_candidate_table_validators.py`.
- Evidencia: `python -m pytest tests/data_foundation_outputs/test_event_candidate_table_validators.py -q` => `7 passed`.
- Lectura correcta: el validator ejecutable existe y pasa fixtures minimos; no valida tabla real todavia porque las tablas daily/1m de eventos candidatos no estan materializadas.
## 2026-07-04 | market_state | canonical vs representation layer contract cerrado

- Se crea `module_contracts/outputs/state_canonical_vs_representation_layer_contract_v0_1.md`.
- El contrato separa `Canonical State` de `Representation Layer` para evitar que scores, embeddings, parameter grids, semantic states o thresholds optimizados entren como verdad base de estado.
- Estado fijado: `state_canonical_vs_representation_layer_contract_v0_1 = complete_for_contract_defined_scope`.
- Lectura correcta: `Canonical State` es tablero estable y legal; `Representation Layer` es espacio de busqueda para AlphaEvolve/RL/ML y evaluadores posteriores.
- No cambia schemas oficiales ni materializa tablas o representaciones.
## 2026-07-04 | market_state | event candidate table validators contract cerrado

- Se crea `module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md`.
- El contrato fija validators comunes daily/1m, validators especificos daily, validators especificos intradia 1m, gates quote-guarded, lineage, prohibiciones de outcomes/labels/rewards y consumer gates ML/RL/AlphaEvolve.
- Estado fijado: `event_candidate_table_validators_contract_v0_1 = complete_for_contract_defined_scope`.
- Lectura correcta: contrato de validators cerrado; validators ejecutables, builders/materializacion y event_windows expansion siguen pendientes.


## 2026-07-04 | market_state | event candidate table schema contracts cerrados

- Se crean `canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md` y `canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md`.
- Los schemas bajan el contrato de eventos daily/1m a grano, columnas obligatorias, timestamp policies, lineage, quality gates y reglas no-outcome/no-label/no-reward.
- La ruta intradia queda condicionada por quote-guarded promotion rule; raw-only puede quedar como evidencia/review, no como candidato canonico promocionable.
- Estado fijado: schema contracts `complete_for_contract_defined_scope`; contrato de validators ya cerrado; validators ejecutables y builders/materializacion siguen pendientes.
## 2026-07-04 | market_state | event candidate tables contract cerrado

- Se crea y cierra `module_contracts/outputs/event_candidate_tables_contract_v0_1.md`.
- El contrato inserta la capa de eventos daily/1m entre scanners y `event_state_table`.
- Define targets conceptuales: `daily_strategy_candidate_events_table_v0_1` e `intraday_1m_strategy_candidate_events_table_v0_1`.
- Estado fijado: `event_candidate_tables_contract_v0_1 = complete_for_contract_defined_scope`.
- Siguiente trabajo recomendado: validators ejecutables, builders de eventos daily/1m, expansion de `event_windows` y fixture/event_state candidate.


## 2026-07-04 | market_state | state builder contract cerrado

- Se crea y cierra `module_contracts/outputs/state_builder_contract_v0_1.md`.
- El contrato fija como ensamblar filas `market_state` / `event_state` desde eligibility, formulas, timestamp policy y snapshot roles.
- Estado fijado: `state_builder_contract_v0_1 = complete_for_contract_defined_scope`.
- Queda explicito que el builder es un ensamblador determinista y auditable, no scanner, evaluador, estrategia ni AlphaEvolve.
- Siguiente trabajo recomendado: leakage/formula/timestamp/role/builder validators y fixture/candidate multi-componente antes de materializar estados.


## 2026-07-04 | market_state | state snapshot roles contract cerrado

- Se crea y cierra `module_contracts/outputs/state_snapshot_roles_contract_v0_1.md`.
- El contrato fija `state_role` como contrato de uso de la fotografia observable: discovery, event anchor, entry decision, risk, execution, RL transition y post-event analysis.
- Estado fijado: `state_snapshot_roles_contract_v0_1 = complete_for_contract_defined_scope`.
- Queda definido que outcomes, labels, rewards y actions no pueden ir inline en `market_state_table` ni `event_state_table` base.
- Siguiente trabajo recomendado: state builder contract y leakage/formula/timestamp/role validators antes de materializar estados.

## 2026-07-04 | market_state | state decision timestamp policy cerrado

- Se crea y cierra `module_contracts/outputs/state_decision_timestamp_policy_v0_1.md`.
- El contrato fija `decision_timestamp_utc` como reloj legal principal y separa observation time, availability time, received time, state cutoff y build time.
- Estado fijado: `state_decision_timestamp_policy_v0_1 = complete_for_contract_defined_scope`.
- Queda definido que ventanas post-decision/post-event no pueden alimentar X pre-decision; pertenecen a outcomes, post-analysis o evaluadores.
- Contrato siguiente ya cerrado: `state_snapshot_roles_contract_v0_1.md`. La ruta activa pasa a state builder contract y leakage/formula/timestamp/role validators antes de materializar estados.

## 2026-07-04 | market_state | state derived observables formula contract cerrado

- Se crea y cierra `module_contracts/outputs/state_derived_observables_formula_contract_v0_1.md`.
- El contrato fija formulas, ventanas, cutoffs, missingness, quality gates y lineage para derivadas declaradas de Daily, Intradia 1m, Microestructura, Contexto As-Of, Short Constraints / Float / Live Alerts, Soporte Legal, Calidad y Lineage.
- Estado fijado: `state_derived_observables_formula_contract_v0_1 = complete_for_contract_defined_scope`.
- AlphaEvolve, ML y RL no pueden mutar la verdad observable ni usar derivadas nuevas sin variante versionada de formula, ventana, cutoff, tests y aceptacion posterior.
- Contrato siguiente ya cerrado: `state_decision_timestamp_policy_v0_1.md`. La ruta activa pasa a state builder contract y leakage/formula/timestamp/role validators antes de materializar estados.

## 2026-07-04 | market_state | observable role taxonomy anadida

- Se amplia `module_contracts/outputs/state_observable_eligibility_contract_v0_1.md` con una taxonomia transversal de tipo/rol de observable.
- La regla queda explicita: `literal_or_derived` dice como nace el dato; `observable_role` dice para que sirve y como debe gobernarse.
- Se aclara que `no-derived` no equivale automaticamente a nuclear y que `derived` no equivale automaticamente a experimental.
- Se incorpora `observable_role` como campo logico requerido para futuros contratos/builders de estado.

## 2026-07-04 | market_state | state observable eligibility contract cerrado

- Se crea y cierra `module_contracts/outputs/state_observable_eligibility_contract_v0_1.md`.
- El contrato convierte el mapa conceptual de Market State en una matriz operativa de elegibilidad por area: Daily, Intradia 1m, Microestructura, Contexto As-Of, Short Constraints / Float / Live Alerts, Soporte Legal, Calidad y Lineage.
- Estado fijado: `state_observable_eligibility_contract_v0_1 = complete_for_contract_defined_scope`.
- No materializa `market_state_table` ni `event_state_table`; gobierna que observables puede consumir un futuro state builder.
- Contrato siguiente ya cerrado: `state_derived_observables_formula_contract_v0_1.md` y despues `state_decision_timestamp_policy_v0_1.md`. La ruta activa pasa a state builder contract y leakage/formula/timestamp/role validators.

## 2026-07-04 | quotes | Phase B SHA256 workers escalation

- Added `--resume-existing-results` to the quotes parity auditor so Phase B SHA256 shards can be relaunched without discarding completed per-ticker hash evidence.
- Stopped the old `workers=1` generation and relaunched all five `quotes_parity_sha256_s*_20260704` shards with `workers=2` and resume enabled.
- Preserved pre-escalation heartbeat/pre-manifest/pid evidence with `pre_workers2_20260704T140623Z` suffixes.

## 2026-07-04 | quotes | Phase B full SHA256 all shards active

- Started remaining Phase B full SHA256 parity shards `quotes_parity_sha256_s2_20260704`, `quotes_parity_sha256_s3_20260704`, and `quotes_parity_sha256_s4_20260704` with `workers=1` each.
- Phase B active set is now all five shards `s0..s4`, full SHA256, single-worker per shard.

## 2026-07-04 | quotes | Phase B full SHA256 s1 started

- Started Phase B full SHA256 parity for `quotes_parity_sha256_s1_20260704` with `workers=1` at operator request.
- Phase B active set is now `s0` and `s1`, both full SHA256, both single-worker.

## 2026-07-04 | quotes | Phase B full SHA256 s0 started

- Started Phase B full SHA256 parity for `quotes_parity_sha256_s0_20260704` after Phase A structural rerun passed for all five shards.
- Launched conservatively with `workers=1` and hold on shards `s1..s4` until `s0` demonstrates stable full-hash progress.

## 2026-07-04 | quotes | s0 parity rerun manifest recovery

- Recovered `quotes_parity_struct_rerun_s0_20260703` final manifest after the auditor process exited without writing `manifest.json`.
- Verified `1041/1041` ticker result JSON files, all `parity_ok=true`, with zero mismatches, missing results, and failed workers.
- Preserved stale heartbeat evidence and marked the recovered manifest with `recovered_manifest=true`.

Este changelog registra cambios locales de `01_foundations`.

No sustituye el changelog padre:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/CHANGELOG.md
```

Regla:

- este archivo conserva detalle local de contracts, schemas, registries,
  policies, validators, dossiers, module contracts, protocols y recovery docs;
- el changelog padre conserva hitos institucionales del modulo y cambios con
  impacto downstream, operativo o de reproducibilidad.

## 2026-07-03 | ohlcv_1m_quote_guarded | downstream docs aligned after manifest promotion

### Changed

- Se alinean los contratos y politicas downstream que aun trataban el manifest
  quote-guarded como pendiente.
- Los documentos ahora distinguen entre:
  - manifest LT1B promovido y disponible;
  - tabla `master_intraday_bar_table_v0_2_candidate_quote_guarded` aun no
    materializada;
  - scanner v0.2 quote-guarded aun pendiente de builder/validacion;
  - `D:/quotes` como lineage provisional candidate-only.
- Se actualizan referencias desde `repair_manifest_v0_2.parquet` hacia el
  artefacto aceptado:
  `repair_manifest_lt1b_v0_1.parquet`.

### Affected Documentation

- Workstream docs de `ohlcv_1m_quote_guarded`.
- Contrato candidate de `master_intraday_bar_table_v0_2_candidate_quote_guarded`.
- Plan wider-scope de `master_intraday_bar_table`.
- Politica de consumo, schema addendum, validators y dataset contract registry.
- Status matrix, target contract, module-contracts README y Graphify refresh queue.
## 2026-07-03 | ohlcv_1m_quote_guarded | final LT1B manifest promoted

### Completed

- La consolidacion final de tres run roots termino `PASS`.
- Gates finales:
  `4824 / 4824` tickers completos, `missing_tickers = 0`,
  `selected_repair_shards = 421533`, `written_shards = 421533`,
  `malformed_shard_names = 0`.
- Manifest promovido:
  `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1.parquet`.
- Filas finales del manifest: `301278342`.
- Tamano final observado: `27226860372` bytes.
- Summary promovido:
  `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/repair_manifest_lt1b_v0_1_summary.json`.

### Contract

La capa aceptada sigue siendo un overlay:

```text
raw ohlcv_1m + LT1B repair manifest = quote_guarded view
```
## 2026-07-03 | ohlcv_1m_quote_guarded | LICN supplement completed and preflight validated

### Validation

- El suplemento `quote_guarded_v0_2_lt1b_licn_repair_20260703` termino `DONE`:
  `12 / 12` meses, `12` shards, `19066` repair rows.
- Los shards regenerados `LICN_2025_01` y `LICN_2025_02` son Parquet legible
  con `8432` y `8723` filas respectivamente.
- El preflight con tres run roots paso en
  `C:/tmp/qg_lt1b_preflight_20260703_licn_patch`:
  `4824 / 4824` tickers completos, `421533` shards seleccionados,
  `missing_tickers = 0`, `malformed_shard_names = 0`.
- El indice seleccionado resuelve todos los meses `LICN` 2025 desde el nuevo
  suplemento con `run_index = 2`.

### Next Step

Relanzar la consolidacion final con tres `RunRoots`, dejando el suplemento LICN
como ultimo root para reemplazar los shards corruptos del broad run.
## 2026-07-03 | ohlcv_1m_quote_guarded | LICN corrupt shard diagnosis

### Fixed Forward

- Se diagnostica la parada repetida de la consolidacion LT1B alrededor del
  checkpoint `220500 / 421533`.
- El shard que rompe la lectura es
  `LICN_2025_01_repair_manifest.parquet`, posicion `220884` del indice LT1B.
- La causa raiz registrada por el broad run es disco lleno:
  `OSError(28, 'No space left on device')`.
- Se confirma que `LICN_2025_01` y `LICN_2025_02` tienen footer Parquet invalido.
- Un scan acotado de metadata sobre `1681` shards LT1B de la ventana sospechosa
  encontro exactamente esos dos corruptos.

### Operational Decision

No relanzar la consolidacion final hasta generar un suplemento `LICN`-only con
`-NoPromoteManifest`, incluirlo como ultimo `RunRoot`, y validar metadata del
indice seleccionado antes de la escritura grande del manifest.
## 2026-07-03 | ohlcv_1m_quote_guarded | manual consolidation outage documented

### Changed

- Se actualiza el protocolo LT1B para dejar constancia del corte de energia
  durante la consolidacion manual.
- Se documenta el ultimo estado durable:
  `220500 / 421533` shards escritos, `170851670` filas escritas y manifest
  parcial en `E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/`.
- Se documenta el preflight post-corte:
  `4824 / 4824` tickers completos, `421533` shards seleccionados,
  `missing_tickers = 0`, `malformed_shard_names = 0`.
- Se explicita que el consolidator v0_1 no es append-resumable: si falta
  `consolidation_summary.json`, el parquet parcial no es promovible y la
  escritura final del manifest debe relanzarse desde los shards durables.

### Rationale

La reparacion quote-guarded y los shards ya generados siguen siendo el trabajo
durable. Lo que se repite tras el corte es solo la escritura derivada del
manifest final.
## 2026-07-03 | quotes | post-copy parity audit power-loss recovery note

### Changed

- Se documenta en el runbook de quotes el corte de energia ocurrido durante la
  Phase A structural parity audit de `D:/quotes` contra
  `E:/TSIS/data/quotes_`.
- Los cinco shards `quotes_parity_struct_s0..s4_20260703` quedaron sin
  manifest final y con heartbeats stale en `running`; por tanto no cumplen el
  promotion gate.
- Se registra que los errores observados eran `worker_error`
  (`PermissionError`, `MemoryError`, recursos insuficientes), no evidencia
  aceptada de mismatch material de clone.
- Se anaden comandos copy/paste para relanzar Phase A con nuevos run ids
  `quotes_parity_struct_rerun_s0..s4_20260703`, `--workers 2` y monitores
  separados.

### Operational Rule

- No borrar la evidencia parcial anterior.
- No usar `--start-at-ticker` junto con `--shard-count 5` para reanudar esos
  shards, porque el auditor aplica `start-at` antes de dividir los shards.
- `E:/TSIS/data/quotes_` sigue bloqueado para consumo oficial hasta que una
  Phase A limpia produzca cinco manifests `completed_pass`.
## 2026-07-03 | ohlcv_1m_quote_guarded | LT1B consolidator schema normalization

### Fixed

- Se corrige el consolidator LT1B para escribir el manifiesto final con schema
  Parquet canonico.
- Cada shard se valida contra las columnas contractuales y se castea antes de
  llamar a `ParquetWriter.write_table`.
- El caso observado fue:

```text
AACT_2023_06_repair_manifest.parquet -> v: double
AAIC_2020_10_repair_manifest.parquet -> v: int64
```

### Validation

- `python -m py_compile` paso sobre el consolidator.
- Prueba temporal sobre shards reales:

```text
written_shards = 10000
rows = 10864177
output = C:/tmp/qg_lt1b_consolidator_schema_test.parquet
```

El output temporal fue eliminado despues de la prueba.

## 2026-07-03 | governance | LOCAL_RULES y changelog local iniciados

### Changed

- Se crea `01_foundations/LOCAL_RULES.md` como regla local obligatoria para
  trabajo dentro de foundations.
- Se crea `01_foundations/CHANGELOG.md` como bitacora local de cambios de
  foundations.
- Se actualiza `01_foundations/README.md` para enlazar las reglas y el changelog
  locales como superficies de gobierno.

### Rationale

`01_foundations` ya contiene suficientes superficies institucionales propias
como para necesitar memoria local:

- `canonical_schemas/`;
- `contract_registry/`;
- `dataset_registry/`;
- `data_consumption_policies/`;
- `validators/`;
- `inspection_dossiers/`;
- `data_quality_report/`;
- `module_contracts/`;
- `GRAPHIFY_REFRESH_QUEUE.md`.

El changelog padre sigue siendo obligatorio para impactos institucionales del
modulo completo.

## 2026-07-03 | ohlcv_1m_quote_guarded | LT1B scope recovery protocol

### Changed

- Se documenta el incidente de scope del run quote-guarded v0_2:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_20260627_091838
planned_tickers = 12168
```

- Se fija el scope valido para SmallCaps en:

```text
lt1b_universe_v0_1
expected_tickers = 4824
```

- Se crea el protocolo local:

```text
module_contracts/ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_lt1b_scope_recovery_protocol_v0_1.md
```

- Se anaden scripts operativos para consolidacion filtrada LT1B y monitor de
  consolidacion:

```text
scripts/inspection/minute/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.py
scripts/consolidate_ohlcv_1m_quote_guarded_lt1b_v0_1.ps1
scripts/monitor_ohlcv_1m_quote_guarded_lt1b_consolidation_v0_1.ps1
```

### Operational State

- El run broad no debe promoverse directamente.
- Los shards LT1B ya escritos se reutilizan mediante consolidacion filtrada.
- El suplemento activo para los 180 tickers LT1B pendientes es:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/quote_guarded_v0_2_lt1b_missing180_20260703_092956
```

### Gates

La consolidacion final solo es valida con:

```text
universe_tickers = 4824
completed_tickers = 4824
missing_tickers = 0
malformed_shard_names = 0
```

El resultado sigue siendo overlay:

```text
raw ohlcv_1m + LT1B repair manifest = quote_guarded view
```





