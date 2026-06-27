# Data Foundation Output Tests

Este directorio contiene los tests ejecutables de las tablas objetivo de
`CAPA 1 - DATA FOUNDATION`.

Las tablas viven bajo:

```text
E:/TSIS/data/data_foundation_outputs/
```

Los contratos viven bajo:

```text
01_foundations/module_contracts/outputs/
```

## Tablas objetivo

Aqui deben validarse, como minimo:

- `instrument_master`
- `market_calendar`
- `expected_data_calendar`
- `corporate_actions_table`
- `dataset_certification_matrix`
- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `halts_table`
- `event_windows_table`
- `outcomes_table`
- `real_time_corporate_event_alerts_table`
- `fundamentals_asof_table`
- `news_context_table`
- `short_context_table`
- `short_sale_constraints_table`
- `regime_context_table`
- `market_state_table`
- `event_state_table`
- `data_quality_report`

## Estado actual

Tablas CAPA 1 con tests contractuales ejecutables y materializacion v0.1:

- `instrument_master`
- `market_calendar`
- `expected_data_calendar`
- `corporate_actions_table`
- `dataset_certification_matrix`
- `master_daily_table`
- `master_intraday_bar_table`
- `microstructure_features_table`
- `halts_table`
- `event_windows_table`
- `outcomes_table`
- `fundamentals_asof_table`
- `news_context_table`
- `short_context_table`
- `regime_context_table`

Contract/fixture stacks with executable tests but no materialized parquet yet:

- `market_state_table`
- `event_state_table`

Ultima evidencia integrada:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_microstructure_features_table_v0_1_rerun/
tests = 3
passed = 3
failed = 0
skipped = 0
```

Ultima evidencia aislada de `halts_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_halts_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `event_windows_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-25/data_foundation_outputs_event_windows_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `outcomes_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_outcomes_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `fundamentals_asof_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_fundamentals_asof_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `news_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_news_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `short_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-26/data_foundation_outputs_short_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia aislada de `regime_context_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_regime_context_table_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia skeleton de `market_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia skeleton de `event_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_event_state_table_contract_skeleton_v0_1/
tests = 4
passed = 4
failed = 0
skipped = 0
```

Ultima evidencia fixture/adversarial conjunta de `market_state_table_v0_1` y
`event_state_table_v0_1`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_market_event_state_fixture_loop_v0_1/
tests = 14
passed = 14
failed = 0
skipped = 0
```

Esta evidencia ejecuta builders fixture-only contra:

- fixtures buenos deterministas;
- fixture `market_state` con as-of futuro;
- fixture `market_state` con feature prohibida `label__*`;
- fixture `event_state` con label inline;
- fixture `event_state` con `post_event_review` marcado como feature ML.

No materializa parquet oficial ni escribe en `E:/TSIS/data`.

Ultima evidencia de manifest candidato para
`microstructure_features_table_v0_2_candidate`:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_candidate_window_manifest_v0_1/
tests = 5
passed = 5
failed = 0
skipped = 0
```

Esta evidencia ejecuta
`scripts/build_microstructure_candidate_window_manifest.py` contra
`event_windows_table_v0_1` y despues ejecuta
`scripts/materialize_microstructure_features_table.py` en modo candidato bajo
`artifacts/`.

Resultado semantico:

```text
source_event_windows_rows = 214112
eligible_microstructure_rows = 85658
eligible_role_counts:
  pre_event_30m = 42829
  same_session_regular = 42829
selected_rows_in_test_manifest = 6
candidate_feature_rows_materialized_under_test_artifacts = 6
candidate_quotes_file_present_rows = 6
candidate_trades_file_present_rows = 6
candidate_hard_fail_count = 0
official_dataset_created = false
```

No escribe parquet oficial y no modifica `microstructure_features_table_v0_1`.
La prueba reconcilia hashes y conteos de filas contra raw quotes/trades para
las ventanas candidatas seleccionadas.

Guardia de regresion de `microstructure_features_table_v0_1` despues de
parametrizar el materializer:

```text
C:/TSIS_Data/tests/test_runs/2026-06-27/data_foundation_outputs_microstructure_features_table_v0_1_default_guard/
tests = 3
passed = 3
failed = 0
skipped = 0
```

Evidencia anterior de las siete primeras tablas:

```text
C:/TSIS_Data/tests/test_runs/2026-06-23/data_foundation_outputs_seven_tables_v0_1_rerun/
tests = 29
passed = 29
failed = 0
skipped = 0
```

## Cinco capas minimas de test

Cada tabla institucional debe tener cinco familias de pruebas.

1. Schema contract test

Valida columnas, tipos, nullability, claves, unicidad, version logica y campos
obligatorios. No basta con que el parquet abra.

2. Manifest and hash test

Valida que el output materializado coincide con su manifest: ruta, `run_id`,
`sha256`, conteos, version, source fingerprints y timestamp de construccion.

3. Source reconciliation test

Reconcilia la tabla contra las fuentes declaradas. Ejemplos: `instrument_master`
contra universe/reference, `market_calendar` contra el parquet oficial XNYS,
`corporate_actions_table` contra splits/dividends/events declarados.

4. Third-party evidence test

Compara una muestra deterministica contra fuentes externas independientes o
evidencia congelada. Ejemplos: SEC EDGAR, NYSE, Nasdaq, OpenFIGI o proveedor
certificado.

Estos tests no deben depender de internet por defecto. Deben usar evidencia
cacheada o requerir una variable como `TSIS_RUN_THIRD_PARTY=1`.

5. Adversarial or mutation test

Inyecta errores controlados y comprueba que el validador falla. Ejemplos:
duplicados, fechas imposibles, `open_utc >= close_utc`, tickers vacios, CIK mal
formateado, outputs sin manifest o hashes incorrectos.

## Criterio contra trampas al solitario

Una tabla no queda institucionalizada porque su propio script diga que esta bien.
Debe haber pruebas que la ataquen desde fuera:

- contrato independiente;
- manifest independiente;
- reconciliacion con fuentes;
- evidencia externa o cacheada;
- mutaciones que demuestren que el test falla cuando debe fallar.

## Evidencia humana

Los tests ejecutables no sustituyen los dossiers visuales. Cuando una tabla o
familia de datos requiere inspeccion humana, el test debe validar que existe la
ruta de evidencia esperada bajo:

```text
01_foundations/data_quality_report/
```

o bajo el dossier especifico definido por contrato.
