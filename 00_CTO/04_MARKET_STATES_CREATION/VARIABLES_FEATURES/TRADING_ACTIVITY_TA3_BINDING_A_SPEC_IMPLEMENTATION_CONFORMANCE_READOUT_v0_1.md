# TRADING ACTIVITY TA-3 BINDING A SPEC / IMPLEMENTATION CONFORMANCE READOUT v0.1

## 0. Control del artefacto

| Campo | Valor |
|---|---|
| `document_role` | `PROVISIONAL_SPEC_IMPLEMENTATION_CONFORMANCE_READOUT` |
| `document_status` | `EXECUTED_PROVISIONAL` |
| `audit_scope` | `FINALIZED_BLOCKS_ONLY` |
| `ta3_execution_status` | `RUNNING` |
| `canonical_promotion_status` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-09` |
| `git_branch` | `integrate/main-data-quality-dossiers-20260613` |
| `git_commit` | `175e3493f4d7385d98963152c39322427754f9a8` |

Este readout compara:

```text
Binding A exact specification v0.2
vs.
active configuration and implementation
vs.
schemas from finalized TA-3 blocks in G:
```

No abre Parquet del bloque activo. No valida valores estadísticos, OOS,
presupuesto de falsas alarmas ni promoción canónica.

## 1. Evidencia auditada

| Artefacto | SHA-256 |
|---|---|
| `TRADING_ACTIVITY_BINDING_A_EXACT_SPECIFICATION_v0_2.md` | `e6f59fae69dadc032d5d7f35add287110917e89926f6a0bead5ddaf644d29b19` |
| `trading_activity_binding_a_multisession_pilot_v0_1.json` | `17a4272449320ca16207f91ef12f5025a377324b2cd12f548e1ddeecc852d6a1` |
| `trading_activity_binding_a_kernel.py` | `575b6d105e1b0e021ea860df20e026294b9b4e30a4ac516da0e7fee0d85b2b46` |
| `trading_activity_binding_a_multisession_engine.py` | `644de090a05d4baee33da84e07dacd444c190b1aab0d334a4f8504a1cd2973d3` |
| `run_trading_activity_binding_a_multisession_pilot.py` | `7f5fac36ecb7df68e235be74bb615d7cf110e5ae70374dcc80bbb86f3fed6a76` |
| auditor ejecutable | `25ba07a00f233b4b5d65384030d6071c8e5b78efa2d5ad8f84ec3cffcb598ba2` |
| evidencia JSON | `3415cfc2d9f0353aeb406b28fbe987b77c92a625a708600d4eff45af3d063ee8` |

Evidencia machine-readable:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests\test_runs\
trading_activity_ta3_binding_a_conformance_provisional_v0_1.json
```

## 2. Cobertura provisional

```text
completed manifests audited = 62
missing finalized output roots = 0
```

| Parent run | Bloques finalizados |
|---|---:|
| `broad_s0of4` | 18 |
| `broad_s1of4` | 37 |
| `broad_s2of4` | 1 |
| `broad_s3of4` | 5 |
| `smoke` | 1 |

Los conteos son una fotografía del momento de auditoría y cambiarán mientras
TA-3 continúe.

## 3. Matriz de variables

| Familia / variable gobernada | Código | Schema finalizado | Veredicto |
|---|---|---|---|
| `eligible_trade_count_W` | Sí | `eligible_trade_count` | `CONFORMANT` |
| `eligible_share_volume_W` | Sí | `eligible_share_volume` | `CONFORMANT` |
| `eligible_dollar_volume_W` | Sí | `eligible_dollar_volume` | `CONFORMANT` |
| `trade_arrival_rate_W` | Sí | `trade_arrival_rate` | `CONFORMANT` |
| `median_intertrade_duration_us_W` | Sí | `median_intertrade_duration_us` | `CONFORMANT` |
| `p10_intertrade_duration_us_W` | Sí | `p10_intertrade_duration_us` | `CONFORMANT` |
| `largest_trade_volume_share_W` | Sí | `largest_trade_volume_share` | `CONFORMANT` |
| `active_subwindow_fraction_W_w` | Sí | `active_subwindow_fraction` | `CONFORMANT` |
| `max_subwindow_trade_share_W_w` | Sí | `max_subwindow_trade_share` | `CONFORMANT` |
| `max_subwindow_volume_share_W_w` | Sí | `max_subwindow_volume_share` | `CONFORMANT` |
| `consecutive_active_subwindows_W_w` | Sí | `consecutive_active_subwindows` | `CONFORMANT` |
| `activity_rate_multiscale_log_ratio_Ws_Wl` | Sí | `activity_rate_multiscale_log_ratio` | `CONFORMANT` |
| `trade_count_percentile_pit_W_B` | Sí | `trade_count_percentile_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `share_volume_percentile_pit_W_B` | Sí | `share_volume_percentile_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `dollar_volume_percentile_pit_W_B` | Sí | `dollar_volume_percentile_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `arrival_rate_percentile_pit_W_B` | Sí | `arrival_rate_percentile_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `trade_count_log_ratio_to_pit_W_B` | Sí | `trade_count_log_ratio_to_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `share_volume_log_ratio_to_pit_W_B` | Sí | `share_volume_log_ratio_to_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `dollar_volume_log_ratio_to_pit_W_B` | Sí | `dollar_volume_log_ratio_to_pit` | `CONFORMANT_WHEN_BASELINE_AVAILABLE` |
| `intertrade_duration_compression_W_B` | No | No | `SPECIFIED_NOT_IMPLEMENTED` |

Los sufijos conceptuales `W`, `w`, `Ws/Wl` y `B` se representan físicamente
mediante columnas de clave como `window_seconds`, `subwindow_seconds`,
`pair_id` y `baseline_candidate_id`; no tienen que formar parte del nombre de
la columna de valor.

## 4. Conformidad de configuración

| Requisito v0.2 | Configuración activa | Veredicto |
|---|---|---|
| ventanas `{5,15,30,60,300}` segundos | coincide | `CONFORMANT` |
| pares `{(5,60),(15,300)}` | coincide | `CONFORMANT` |
| baselines `{B20,B60,B120}` | coincide | `CONFORMANT` |
| latencia primaria `1000ms` | coincide | `CONFORMANT` |
| scope RTH reconciliado event-time | coincide semánticamente | `CONFORMANT_WITH_RESTRICTIONS` |
| `feature_version=v0_2` | output declara `v0_1` | `NONCONFORMANT_LINEAGE` |
| `binding_id` v0.2 | output declara candidate `v0_1` | `NONCONFORMANT_LINEAGE` |

Los 62 bloques inspeccionados declaran uniformemente:

```text
feature_spec_id = trading_activity_binding_a_experimental_physical_binding
feature_version = v0_1
binding_id = trading_activity_binding_a_candidate_v0_1
scope_id = legacy_rth_reconciled_event_time_research_only
future_window_used = false
```

Los cálculos principales están mayoritariamente alineados con v0.2, pero la
identidad declarada no lo demuestra. Los outputs actuales deben conservarse
como ejecución experimental legacy-v0.1-compatible y no renombrarse in place.

## 5. Conformidad de schema

```text
CURRENT_STATE schema variants = 1
MULTISCALE_CONTRAST schema variants = 1
PIT_BASELINE_AND_SURPRISE schema variants = 2
```

La segunda variante de baseline aparece cuando toda la población evaluada
tiene historia insuficiente. En esa variante se omiten las columnas de
estadísticos, percentiles y sorpresas, en vez de materializarlas con `NULL`.

```text
STABLE SCHEMA REQUIREMENT
= FAIL
```

Un consumidor no debería recibir schemas físicos diferentes según haya o no
historia suficiente. La implementación siguiente debe declarar el schema
completo antes de escribir y conservar esas columnas como `NULL` con
`baseline_calculation_state=BASELINE_INSUFFICIENT_HISTORY`.

## 6. Metadata obligatoria

La implementación usa:

```text
coverage_state
```

mientras v0.2 exige:

```text
coverage_mode
```

También faltan en las tres familias:

```text
duplicate_policy_id
coverage_mode
```

Disposición requerida:

```text
coverage_state
= estado observado de cobertura

coverage_mode
= política o modo con el que se resolvió la cobertura
```

No deben considerarse sinónimos automáticamente. `duplicate_policy_id` debe
persistirse aunque la política primaria conserve todos los eventos elegibles.

## 7. Hallazgos y severidad

### HIGH - Binding A v0.2 no está implementado completamente

`intertrade_duration_compression_W_B` está especificado pero no existe en el
kernel, motor ni schemas materializados. Requiere baseline PIT de
`median_intertrade_duration_us` y su transformación causal.

### HIGH - identidad de versión incorrecta

La ejecución afirma `feature_version=v0_1` y `binding_id=...v0_1` mientras se
está evaluando contra la especificación exacta v0.2. No se permite corregir
los outputs históricos in place.

### MEDIUM - schema baseline dependiente de los datos

Existen dos schemas físicos. La variante de historia insuficiente omite
columnas gobernadas.

### MEDIUM - metadata incompleta

Faltan `duplicate_policy_id` y `coverage_mode`. `coverage_state` no sustituye
la identidad de la política de cobertura.

### PASS - núcleo actual y causalidad declarada

Las once variables de `CURRENT_STATE` y el contraste multiescala están
presentes en todos los bloques finalizados. Todos los registros de metadata
muestreados declaran `future_window_used=false`.

## 8. Veredicto provisional

```text
CURRENT_STATE FEATURES
= PASS

MULTISCALE CONTRAST
= PASS

PIT BASELINE AND SURPRISE
= PASS_WITH_REQUIRED_REVISIONS

BINDING A v0.2 COMPLETE IMPLEMENTATION
= FAIL

TA-3 CURRENT OUTPUT USABILITY
= EXPERIMENTAL_RESEARCH_ONLY

CANONICAL PROMOTION
= NOT_AUTHORIZED
```

La ejecución actual no debe detenerse: conserva evidencia válida para las
variables implementadas. Al terminar TA-3 se emitirá el readout cuantitativo
final. Antes de otra materialización gobernada debe publicarse una nueva
versión del builder/config que:

1. implemente o retire formalmente `intertrade_duration_compression`;
2. estabilice el schema de baseline;
3. persista `duplicate_policy_id` y `coverage_mode`;
4. declare IDs coherentes con la especificación realmente ejecutada;
5. ejecute tests de equivalencia y migración sin reescribir TA-3.

