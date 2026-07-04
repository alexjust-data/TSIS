# Event Candidate Table Validators Contract v0.1

## Estado

Tipo: validators contract.
Modulo: `01_TSIS_backtest_SmallCaps`.
Ambito: `CAPA 1 - DATA FOUNDATION`.
Fecha: 2026-07-04.

Status:

```text
contract_defined
event_candidate_table_validators_contract_complete_for_declared_scope = true
executable_validators_implemented = false
daily_strategy_candidate_events_table_materialized = false
intraday_1m_strategy_candidate_events_table_materialized = false
event_windows_expansion_materialized = false
event_state_table_materialized = false
ml_ready_dataset_enabled = false
rl_training_dataset_enabled = false
alphaevolve_evaluator_enabled = false
```

Este contrato fija que deben comprobar los validators antes de construir o
materializar tablas de eventos candidatas daily/1m.

Regla corta:

```text
schema contract = que forma debe tener la tabla
validators contract = que debe fallar antes de permitir construir/consumir
builder = produce filas candidate solo si los validators pasan
```

Este documento no implementa codigo. Define la obligacion que luego deben cumplir
los validators ejecutables.

## 1. Por Que Existe Este Contrato

Las tablas candidatas de eventos quedan entre scanners y `event_state_table`.
Por eso son un punto peligroso: si una fila de evento queda mal anclada, todo lo
que venga despues puede heredar leakage o una definicion imposible de auditar.

Este contrato existe para impedir que futuros builders:

- materialicen eventos sin `event_definition_id/version`;
- usen thresholds sin definicion versionada;
- afirmen timestamps intradia que un source daily no puede probar;
- promocionen spikes raw-only rechazados por quote-guarded;
- metan outcomes, labels, rewards, fills o PnL dentro de la tabla de eventos;
- declaren full-universe sin denominador/certificacion;
- habiliten ML/RL/AlphaEvolve antes de tener event_state/outcomes/evaluadores.

## 2. Fuentes Normativas

```text
C:/TSIS_Data/00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_decision_timestamp_policy_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_snapshot_roles_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
```

## 3. Targets Que Deben Validarse

Este contrato aplica a:

```text
daily_strategy_candidate_events_table_v0_1
intraday_1m_strategy_candidate_events_table_v0_1
```

Tambien aplica a cualquier `event_windows` expansion que consuma esas tablas como
`source_event_table`.

No aplica directamente a:

```text
market_state_table
event_state_table
outcomes_table
semantic_state_representation
state_transition_dataset
```

Esas capas tienen o tendran validators propios, pero dependen de que los eventos
candidatos sean legales.

## 4. Severidad De Validators

| Severidad | Significado | Consecuencia |
| --- | --- | --- |
| `hard_fail` | viola contrato, cutoff, schema, lineage o prohibicion sensible | bloquea materializacion/consumo |
| `review_fail` | puede existir como evidencia controlada, pero no como candidato canonico | permite dossier/replay, bloquea promocion |
| `warning` | no bloquea por si solo, pero debe quedar en manifest | requiere seguimiento |
| `info` | metrica o conteo de auditoria | no bloquea |

Regla:

```text
hard_fail count > 0 => no materializar candidate table
review_fail count > 0 => no promocionar ni habilitar ML/RL/AlphaEvolve
```

## 5. Salida Esperada De Un Validator Ejecutable

Cuando se implemente el validator ejecutable, debe producir como minimo:

```text
validator_run_id
validator_contract_id
validated_dataset_id
validated_dataset_path
schema_contract_path
row_count
hard_fail_count
review_fail_count
warning_count
validator_results_table_path
validator_summary_path
created_at_utc
source_manifest_path
source_manifest_sha256
```

Cada fallo debe preservar:

```text
validator_id
severity
primary_key_value
event_id
event_definition_id
event_table_id
column_name
observed_value
expected_rule
failure_message
```

## 6. Validators Comunes Daily/1m

### 6.1 Identidad Y Grano

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_missing_event_id` | `hard_fail` | daily/intradia | falta `event_id` |
| `event_bad_missing_primary_id` | `hard_fail` | daily/intradia | falta `daily_event_id` o `intraday_event_id` segun tabla |
| `event_bad_duplicate_primary_id` | `hard_fail` | daily/intradia | primary id duplicado |
| `event_bad_duplicate_declared_grain` | `hard_fail` | daily/intradia | grano logico duplicado sin policy explicita |
| `event_bad_event_table_id_mismatch` | `hard_fail` | daily/intradia | `event_table_id` no coincide con el dataset validado |
| `event_bad_schema_version_mismatch` | `hard_fail` | daily/intradia | `schema_version` / `event_schema_version` no coincide con schema esperado |
| `event_bad_missing_instrument_session` | `hard_fail` | daily/intradia | falta `instrument_id`, `ticker` o `session_date` |
| `event_bad_instrument_identity_temporal_match` | `hard_fail` | daily/intradia | `instrument_identity_temporal_match != true` para fila consumible |
| `event_bad_calendar_session` | `hard_fail` | daily/intradia | `calendar_session_valid != true` para fila consumible |

### 6.2 Definicion De Evento Y Thresholds

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_missing_event_definition_id` | `hard_fail` | daily/intradia | falta `event_definition_id` |
| `event_bad_missing_event_definition_version` | `hard_fail` | daily/intradia | falta `event_definition_version` |
| `event_bad_missing_definition_params_bundle` | `hard_fail` | daily/intradia | falta `event_definition_params_bundle` |
| `event_bad_missing_trigger_observables_bundle` | `hard_fail` | daily/intradia | falta `trigger_observables_bundle` |
| `event_bad_threshold_without_definition` | `hard_fail` | daily/intradia | aparece threshold sin definicion/version y `thresholds_bundle` |
| `event_bad_best_threshold_as_truth` | `hard_fail` | daily/intradia | aparece un threshold descubierto como verdad oficial no versionada |
| `event_bad_definition_version_drift` | `hard_fail` | daily/intradia | mismo `event_definition_id/version` produce parametros distintos sin nuevo versionado |
| `event_bad_alphaevolve_definition_without_contract` | `hard_fail` | daily/intradia | `definition_is_alphaevolve_candidate=true` sin definicion candidata/versionada |

Lectura correcta:

```text
un threshold puede existir como parametro de una definicion de evento;
no puede existir como feature privilegiada ni como verdad del estado base.
```

### 6.3 Tiempo, Cutoff Y Disponibilidad

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_future_availability` | `hard_fail` | daily/intradia | `event_availability_utc > as_of_utc` |
| `event_bad_source_cutoff_future` | `hard_fail` | daily/intradia | `source_data_availability_cutoff_utc > as_of_utc` |
| `event_bad_detection_after_asof` | `hard_fail` | daily/intradia | `detection_timestamp_utc > as_of_utc` cuando detection existe |
| `event_bad_missing_timestamp_policy` | `hard_fail` | daily/intradia | falta `event_timestamp_policy` |
| `event_bad_unknown_timestamp_policy` | `hard_fail` | daily/intradia | policy no esta permitida por el schema de esa tabla |
| `event_bad_decision_timestamp_policy_missing` | `hard_fail` | daily/intradia | falta `decision_timestamp_policy_id` |
| `event_bad_cutoff_policy_version_missing` | `hard_fail` | daily/intradia | falta `definition_cutoff_policy_version` o `cutoff_policy_version` requerido |

## 7. Validators Especificos Daily

| Validator | Severidad | Debe fallar si |
| --- | --- | --- |
| `daily_event_bad_intraday_claim_without_source` | `hard_fail` | `contains_intraday_timestamp_claim=true` sin fuente intradia que pruebe `event_timestamp_utc` |
| `daily_event_bad_intraday_policy_without_timestamp` | `hard_fail` | `event_timestamp_policy=intraday_proven` y `event_timestamp_utc` es null |
| `daily_event_bad_eod_proxy_as_intraday_truth` | `hard_fail` | un evento `date_level` o `session_close_available` se promociona como timestamp intradia real |
| `daily_event_bad_session_close_fields_before_close` | `hard_fail` | se usan campos de sesion completa antes de cierre/disponibilidad |
| `daily_event_bad_session_date_event_date_mismatch` | `review_fail` | `event_date` y `session_date` divergen sin razon declarada |
| `daily_event_bad_source_candidate_missing_for_scanner_event` | `hard_fail` | evento derivado de scanner no preserva `source_candidate_id` / source scanner lineage |

Regla diaria:

```text
daily puede anclar un evento a sesion/fecha;
solo puede afirmar timestamp intradia si una fuente intradia lo prueba.
```

## 8. Validators Especificos Intradia 1m

| Validator | Severidad | Debe fallar si |
| --- | --- | --- |
| `intraday_event_bad_missing_timestamp` | `hard_fail` | falta `event_timestamp_utc` |
| `intraday_event_bad_missing_bar_timestamps` | `hard_fail` | falta `event_bar_ts_utc` o `event_bar_end_utc` |
| `intraday_event_bad_bar_not_closed` | `hard_fail` | `event_bar_end_utc > as_of_utc` bajo `closed_1m_bar` |
| `intraday_event_bad_uncontracted_live_bar` | `hard_fail` | `uses_incomplete_bar=true` sin `live_bar_policy` contratada |
| `intraday_event_bad_bar_size` | `hard_fail` | `event_bar_size != 1m` |
| `intraday_event_bad_unknown_session_phase` | `review_fail` | `event_session_phase=unknown_review` y se intenta promocionar la fila |
| `intraday_event_bad_missing_quote_guarded_manifest` | `hard_fail` | ruta canonica claim `ohlcv_1m_quote_guarded` sin `source_quote_guarded_repair_manifest` |
| `intraday_event_bad_quote_guarded_not_confirmed` | `hard_fail` | fila canonica tiene `quote_guarded_event_confirmed != true` |
| `intraday_event_bad_raw_only_promoted` | `hard_fail` | evento raw-only marcado como `candidate` consumible o promocionable |
| `intraday_event_bad_raw_spike_selected` | `hard_fail` | `raw_event_detected=true`, `quote_guarded_event_confirmed=false` y `event_selection_state=candidate` |
| `intraday_event_bad_qg_view_false_for_canonical` | `hard_fail` | fila candidate canonica tiene `quote_guarded_view != true` |
| `intraday_event_bad_qg_lineage_missing_run_id` | `review_fail` | falta `source_quote_guarded_run_id` en fila quote-guarded |

Regla intradia:

```text
la ruta canonica 1m debe ser quote-guarded;
raw-only puede quedar como evidencia/review, no como candidato promocionable.
```

## 9. Lineage, Manifest Y Fuente

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_missing_source_candidate` | `hard_fail` | daily/intradia | evento derivado de scanner/source no conserva `source_candidate_id` o razon directa alternativa |
| `event_bad_missing_source_candidate_dataset` | `hard_fail` | daily/intradia | falta `source_candidate_dataset_id` |
| `event_bad_missing_source_manifest` | `hard_fail` | daily/intradia | falta `source_manifest_path` |
| `event_bad_missing_manifest_hash` | `review_fail` | daily/intradia | falta `source_manifest_sha256` cuando la fuente debe ser hashable |
| `event_bad_missing_build_run_id` | `hard_fail` | daily/intradia | falta `build_run_id` |
| `event_bad_missing_created_at` | `hard_fail` | daily/intradia | falta `created_at_utc` |
| `event_bad_missing_materialization_scope` | `hard_fail` | daily/intradia | falta `materialization_scope` |
| `event_bad_price_view_missing` | `hard_fail` | daily/intradia | la definicion depende de precio y falta `source_price_view` |
| `event_bad_provisional_source_promoted` | `hard_fail` | daily/intradia | fuente provisional se marca como promocion oficial/full-universe |

## 10. Prohibiciones De Outcomes, Labels Y Acciones

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_prohibited_prefix` | `hard_fail` | daily/intradia | aparece columna con prefijo `outcome__`, `label__`, `reward__`, `action__`, `policy__`, `fill__`, `pnl__` o `future__` |
| `event_bad_outcome_inline` | `hard_fail` | daily/intradia | `contains_outcome_information=true` o valores de outcome inline |
| `event_bad_label_inline` | `hard_fail` | daily/intradia | `contains_label_information=true` o labels inline |
| `event_bad_reward_inline` | `hard_fail` | daily/intradia | `contains_reward_information=true` o rewards inline |
| `event_bad_execution_truth` | `hard_fail` | daily/intradia | `execution_truth=true` |
| `event_bad_post_event_metric_inline` | `hard_fail` | daily/intradia | aparecen MFE, MAE, realized PnL, future return, fill posterior o winner/loser |

Permitido:

```text
outcome_join_key
event_window_join_key
market_state_join_key
```

Solo como llaves/referencias, no como valores de resultado.

## 11. Consumer Gates

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_ml_feature_gate` | `hard_fail` | daily/intradia | `valid_for_ml_feature_candidate=true` sin event_state legal/pre-decision probado |
| `event_bad_rl_state_gate` | `hard_fail` | daily/intradia | `valid_for_rl_state_candidate=true` antes de state/transition contract aplicable |
| `event_bad_alphaevolve_production_gate` | `hard_fail` | daily/intradia | se habilita production evaluator antes de evaluadores bloqueados |
| `event_bad_backtest_event_gate` | `review_fail` | daily/intradia | `valid_for_backtest_event_candidate=true` con timestamp/cutoff en review |
| `event_bad_event_windows_gate` | `hard_fail` | daily/intradia | `valid_for_event_windows_candidate=true` sin `event_id`, ancla temporal legal o source lineage |
| `event_bad_event_state_gate` | `hard_fail` | daily/intradia | `valid_for_event_state_candidate=true` sin poder construir event_windows legales |

Regla:

```text
estas tablas pueden anclar eventos;
no son features ML/RL directas ni evaluadores AlphaEvolve.
```

## 12. Full Universe, Materializacion Y Promocion

| Validator | Severidad | Aplica a | Debe fallar si |
| --- | --- | --- | --- |
| `event_bad_full_universe_claim` | `hard_fail` | daily/intradia | `full_universe_claim=true` sin denominador/certificacion/promocion |
| `event_bad_official_write_without_promotion` | `hard_fail` | daily/intradia | se escribe en root oficial como promoted sin promotion barrier |
| `event_bad_missing_validator_manifest` | `hard_fail` | daily/intradia | materializacion candidate no emite resultados de validator |
| `event_bad_candidate_scope_missing` | `hard_fail` | daily/intradia | scope candidate no esta declarado |
| `event_bad_materialized_without_schema_contract` | `hard_fail` | daily/intradia | tabla se materializa sin schema contract canonico |
| `event_bad_materialized_without_event_contract` | `hard_fail` | daily/intradia | tabla se materializa sin `event_candidate_tables_contract_v0_1.md` |

## 13. Orden De Ejecucion Requerido

Un builder futuro debe ejecutar gates en este orden:

```text
1. schema presence checks
2. identity/grain checks
3. event definition / threshold checks
4. timestamp / availability / cutoff checks
5. daily o intraday specific checks
6. source lineage / manifest checks
7. prohibited outcomes/labels/rewards checks
8. consumer gates
9. full-universe / promotion gates
10. deterministic rebuild / manifest summary
```

No se permite marcar una fila como consumible si fallo un gate anterior de
severidad `hard_fail`.

## 14. Relacion Con Event Windows

Antes de expandir `event_windows_table` para eventos no-halt, los event candidate
validators deben poder demostrar que cada source event tiene:

```text
event_id
event_table_id
event_definition_id
event_family
event_timestamp_utc o event_date legal
source_manifest_path
valid_for_event_windows_candidate = true
contains_outcome_information = false
contains_label_information = false
contains_reward_information = false
```

Si esto no pasa, `event_windows` no debe abrir ventanas sobre ese evento.

## 15. Relacion Con Event State

`event_state_table` solo puede anclarse a eventos que pasen:

```text
event_candidate_table validators
event_windows validators
state builder validators
```

Regla:

```text
evento valido no implica estado valido;
solo implica que el ancla del evento es legal para construir ventanas y estados.
```

## 16. Relacion Con AlphaEvolve / ML / RL

AlphaEvolve puede proponer nuevas definiciones de evento, thresholds o detectores.
Este contrato exige que esas propuestas entren como:

```text
event_definition_candidate
event_definition_version
event_definition_params_bundle
thresholds_bundle
validator result
```

No puede hacer esto:

```text
cambiar silenciosamente un threshold oficial
escribir outcomes inline
usar raw-only como verdad canonica
saltarse quote-guarded en intradia
habilitar evaluador production sin fitness/evaluador bloqueado
```

ML/RL solo podran consumir eventos despues de construir `event_state` y outcomes
separados bajo contratos posteriores.

## 17. Siguiente Trabajo Permitido

Despues de este contrato, el siguiente trabajo permitido es:

```text
1. implementar validators ejecutables de event candidate tables
2. crear tests/fixtures minimos daily e intradia para esos validators
3. construir builder/materializacion candidate daily solo si validators pasan
4. construir builder/materializacion candidate intradia solo si validators pasan
5. expandir event_windows para source_event_table != halts_table_v0_1
6. construir controlled event_state fixture con eventos daily/1m
```

No queda permitido todavia:

```text
materializacion oficial full-universe
ML/RL training directo
AlphaEvolve evaluator production
outcomes inline
promocion de intraday raw-only como canonico
```

## 18. Acceptance Criteria v0.1

| Criterio | Estado |
| --- | --- |
| validators comunes daily/1m definidos | `done` |
| validators especificos daily definidos | `done` |
| validators especificos intradia 1m definidos | `done` |
| quote-guarded promotion gates definidos | `done` |
| prohibiciones outcomes/labels/rewards definidas | `done` |
| consumer gates ML/RL/AlphaEvolve definidos | `done` |
| relacion con event_windows declarada | `done` |
| relacion con event_state declarada | `done` |
| contrato no implementa codigo ni materializa tablas | `done` |

Status final:

```text
event_candidate_table_validators_contract_v0_1 = complete_for_contract_defined_scope
```
