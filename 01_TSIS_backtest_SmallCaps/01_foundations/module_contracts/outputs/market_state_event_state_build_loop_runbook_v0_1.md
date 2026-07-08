# Market State / Event State Build Loop Runbook v0.1

## 2026-07-07 Quotes Root Supersession

`D:/quotes -> E:/TSIS/data/quotes_` is closed and approved. The official quotes E-root for new downstream work is `E:/TSIS/data/quotes_`, backed by Phase A structural parity and Phase B SHA256 retry evidence. Historical artifacts built from `D:/quotes` remain pre-approval/provenance evidence and must be rebuilt against the approved E-root before promotion to an official downstream table. The legacy `E:/TSIS/data/quotes` tree remains incomplete for this decision.


## Estado

Tipo: build-loop runbook / continuity note.

Modulo: `01_TSIS_backtest_SmallCaps`.

Ambito: `CAPA 1 - DATA FOUNDATION`.

Status:

```text
contract_stack_skeleton_complete
market_state_table_materialized = false
event_state_table_materialized = false
```

## Decision Operativa Provisional Sobre Quotes

Fecha: `2026-06-29`.

Para desbloquear el siguiente loop controlado, TSIS acepta trabajar
provisionalmente con:

```text
quotes_root_used = D:/quotes
quotes_root_state = pre_approval_d_recovery_lineage_requires_rebuild
target_official_quotes_root = E:/TSIS/data/quotes_
legacy_incomplete_e_quotes_root = E:/TSIS/data/quotes
```

Esta decision solo habilita candidatos y muestras controladas. No habilita:

- promocion institucional final;
- ML/RL primary training;
- backtest-core directo;
- execution simulation;
- sustitucion de la futura raiz oficial objetivo `E:/TSIS/data/quotes_`.

Todo output de microestructura, `market_state_table` o `event_state_table` que
use esta raiz debe conservar lineage visible por fila o manifest:

```text
quotes_root_used
quotes_root_state
target_official_quotes_root
legacy_incomplete_e_quotes_root
source_quotes_file
source_quotes_file_sha256
requires_rebuild_after_quotes_root_approval = true
```

Cuando termine la clonacion/auditoria de `D:/quotes -> E:/TSIS/data/quotes_` y
`E:/TSIS/data/quotes_` quede aceptada como raiz oficial, cualquier candidato
basado en `D:/quotes` debera recomputarse o quedar marcado como lineage
provisional. `E:/TSIS/data/quotes` queda tratado como raiz E incompleta/legacy,
no como raiz oficial futura.

Contrato base:

```text
01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md
```

Contrato companion obligatorio para decidir cobertura, scanner diario y
lookbacks:

```text
01_foundations/module_contracts/outputs/market_state_coverage_and_lookback_policy_v0_1.md
```

## Objetivo Del Loop

Construir la estructura gobernada minima para que futuros agentes puedan
materializar:

```text
market_state_table_v0_1
event_state_table_v0_1
```

sin confundir estado con:

```text
signal
strategy
outcome
reward
execution fill
```

Este runbook existe para que el trabajo sea recuperable si se interrumpe la
sesion, se apaga la maquina o cambia el agente.

## Regla De Continuidad

Si el loop queda interrumpido, el siguiente agente debe continuar en este orden:

1. Leer este runbook completo.
2. Leer
   `market_state_event_state_composition_contract_v0_1.md`.
3. Leer
   `market_state_coverage_and_lookback_policy_v0_1.md`.
4. Revisar `CHANGELOG.md` y `GRAPHIFY_REFRESH_QUEUE.md`.
5. Verificar que no se ha materializado ningun parquet oficial bajo:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/
E:/TSIS/data/data_foundation_outputs/event_state_table/
```

6. Continuar desde el primer item pendiente en la checklist.

## Checklist De Trabajo

### Fase 1 - Contratos De Schema

Crear:

```text
01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
```

Estado: `completed`

### Fase 2 - Dataset Contracts

Crear:

```text
01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md
01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md
```

Estado: `completed`

### Fase 3 - Consumption Policies

Crear:

```text
01_foundations/data_consumption_policies/market_state_table_consumption_policy.md
01_foundations/data_consumption_policies/event_state_table_consumption_policy.md
```

Estado: `completed`

### Fase 4 - Validators

Crear:

```text
01_foundations/validators/outputs/market_state_table_validators.md
01_foundations/validators/outputs/event_state_table_validators.md
```

Estado: `completed`

### Fase 5 - Registry Target Entries

Crear target entries con status `contract_defined_not_materialized`, no como
outputs fisicos validados:

```text
01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml
01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml
```

Estado: `completed`

### Fase 6 - Builder Skeletons

Crear skeletons no destructivos:

```text
scripts/materialize_market_state_table.py
scripts/materialize_event_state_table.py
```

Estado: `completed`

Estos scripts deben fallar con un error explicito si se ejecutan sin config
validada. No deben producir outputs oficiales por defecto.

### Fase 7 - Test Skeletons

Crear tests contractuales iniciales:

```text
tests/data_foundation_outputs/test_market_state_table_contract.py
tests/data_foundation_outputs/test_event_state_table_contract.py
```

Estado: `completed`

Los tests v0.1 iniciales deben comprobar existencia/coherencia de contratos,
prohibiciones de materializacion prematura y reglas de leakage documentadas.
No deben fingir que existe una tabla parquet materializada.

### Fase 8 - Indices Y Trazabilidad

Actualizar:

```text
01_foundations/canonical_schemas/README.md
01_foundations/contract_registry/dataset_contracts/README.md
01_foundations/data_consumption_policies/README.md
01_foundations/dataset_registry/README.md
01_foundations/validators/README.md
01_foundations/module_contracts/README.md
01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
tests/README.md
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/README.md
```

Estado: `completed`

## Barreras No Negociables

Mientras no existan builders, manifests y tests de materializacion:

```text
market_state_table_v0_1 materialized = false
event_state_table_v0_1 materialized = false
valid_for_rl_training_direct = false
execution_truth = false
```

Ningun agente puede afirmar:

- que existe un market state institucional final;
- que existe un event state institucional final;
- que los outputs CAPA 1 actuales son suficientes por si solos para RL;
- que `outcomes_table_v0_1` puede usarse como feature;
- que `short_context_table_v0_1` prueba borrow, locate o SSR;
- que `regime_context_table_v0_1` puede usarse como estado intradia
  same-session antes del cierre;
- que `microstructure_features_table_v0_1` es full-universe o trainable;
- que `master_intraday_bar_table_v0_1` es full-universe.

## Criterio De Cierre De Este Loop

Este loop queda completo cuando existan y esten enlazados:

- 2 schema contracts;
- 2 dataset contracts;
- 2 consumption policies;
- 2 validator contracts;
- 2 registry target entries;
- 2 builder skeletons que no materializan por accidente;
- 2 test skeletons;
- indices actualizados;
- changelog actualizado;
- Graphify refresh queue actualizada.

Estado actual:

```text
loop_contract_stack_closed = true
```

## Evidencia De Tests

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0

C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

## Siguiente Loop Permitido

El siguiente loop ya no debe volver a definir conceptualmente que es estado.
Debe crear:

- fixtures deterministas pequenos;
- configs reales de builder;
- tests adversariales de leakage;
- primer builder que produzca una muestra controlada, no full universe.

Queda fuera de este loop:

- materializar parquet oficial;
- crear fixture de datos real;
- componer millones de estados;
- entrenar ML/RL;
- crear rewards o transitions;
- conectar live feeds.

## Fixture Loop v0.1

Estado: `completed`

Este loop crea la primera pieza ejecutable controlada para comprobar el contrato
sin materializar tablas oficiales.

Artefactos creados o activados:

```text
tests/fixtures/data_foundation_outputs/market_event_state_v0_1/
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/market_state_builder_fixture_v0_1.json
01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/event_state_builder_fixture_v0_1.json
01_TSIS_backtest_SmallCaps/scripts/_state_fixture_builder.py
01_TSIS_backtest_SmallCaps/scripts/materialize_market_state_table.py
01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_table.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_state_table_contract.py
01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_table_contract.py
```

Lectura institucional:

```text
fixture_builder_implemented = true
official_builder_implemented = false
official_output_materialized = false
full_universe_claim = false
```

Los builders aceptan:

```text
--contract-check-only
--config <fixture_config> --output-dir <C:/TSIS_Data/tests/test_runs/...>
```

Los builders rechazan:

- output fuera de `C:/TSIS_Data/tests/test_runs`;
- `official_output_allowed = true`;
- features con prefijos `label__`, `outcome__`, `reward__`, `future__`,
  `signal__`, `strategy__`, `action__`, `policy__`, `fill__` o `pnl__`;
- componentes con `*_as_of_utc > decision_timestamp_utc`;
- `post_event_review` o `research_replay` marcados como
  `valid_for_ml_feature_candidate = true`.

Evidencia de tests:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
tests = 14
passed = 14
failed = 0
skipped = 0
```

El resultado del loop no crea:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/
E:/TSIS/data/data_foundation_outputs/event_state_table/
```

Siguiente loop permitido:

- producir una primera muestra controlada multi-componente mas rica;
- ampliar adversarial tests con fixtures de missing required component,
  namespace ilegal, flags ambiguos y output-dir ilegal;
- definir config de builder real contra outputs CAPA 1 ya materializados;
- mantener bloqueado cualquier parquet oficial o full-universe hasta que pasen
  recomputation tests, manifest policy y coverage gates.

## Controlled Candidate Loop v0.2

Estado: `completed_candidate_not_promoted`

Fecha: `2026-06-29`

Este loop crea la primera muestra controlada real sobre outputs CAPA 1:

```text
microstructure_features_table_v0_2_candidate_controlled_25_per_role
  -> market_state_table_v0_1_candidate_microstructure_halt_controlled
  -> event_state_table_v0_1_candidate_microstructure_halt_controlled
```

Builders activados:

```text
scripts/materialize_market_state_table.py --materialize-candidate
scripts/materialize_event_state_table.py --materialize-candidate
```

Salidas:

```text
E:/TSIS/data/data_foundation_outputs/market_state_table/market_state_table_v0_1_candidate_microstructure_halt_controlled/
E:/TSIS/data/data_foundation_outputs/market_state_table/_market_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
E:/TSIS/data/data_foundation_outputs/event_state_table/event_state_table_v0_1_candidate_microstructure_halt_controlled/
E:/TSIS/data/data_foundation_outputs/event_state_table/_event_state_table_manifest_v0_1_candidate_microstructure_halt_controlled.json
```

Resultados:

```text
market_state_candidate_rows = 50
market_state_candidate_tickers = 9
market_state_candidate_event_windows = 50
market_state_valid_for_event_context_candidate_rows = 50
market_state_valid_for_ml_feature_candidate_rows = 0
market_state_valid_for_rl_state_candidate_rows = 0
market_state_full_universe_claim_rows = 0
market_state_quality_counts = {"state_review_microstructure_seed_only":50}

event_state_candidate_rows = 50
event_state_candidate_tickers = 9
event_state_candidate_event_windows = 50
event_state_pre_event_rows = 25
event_state_post_event_review_rows = 25
event_state_valid_for_pattern_discovery_rows = 50
event_state_valid_for_ml_feature_candidate_rows = 0
event_state_valid_for_rl_state_candidate_rows = 0
event_state_full_universe_claim_rows = 0
event_state_quality_counts = {"event_state_review_microstructure_seed_only":50}
```

Evidencia ejecutable:

```text
python -m pytest tests/data_foundation_outputs/test_market_state_table_contract.py tests/data_foundation_outputs/test_event_state_table_contract.py -q
tests = 16
passed = 16
failed = 0
```

Lectura institucional:

```text
candidate_builder_implemented = true
controlled_candidate_materialized = true
official_builder_implemented = false
official_output_promoted = false
full_universe_claim = false
direct_ml_rl_backtest_execution_use_allowed = false
```

Bloqueos que permanecen:

- hereda `quotes_root_state=pre_approval_d_recovery_lineage_requires_rebuild`;
- requiere rebuild despues de la paridad/auditoria de `E:/TSIS/data/quotes_`;
- no usa short-sale constraints reales porque SSR/borrow/locate siguen sin
  fuente gobernada;
- no contiene labels, outcomes, rewards, acciones, fills, PnL, estrategia ni
  senales;
- no es dataset final de entrenamiento ML/RL.
