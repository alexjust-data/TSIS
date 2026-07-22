# Expected Data Calendar Schema Contract `v0_1`

## 1. Rol

Este documento define el schema canonico inicial para:

- `expected_data_calendar_v0_1`

`expected_data_calendar` es una tabla de expectativa contractual de cobertura.
Su funcion es declarar para que combinaciones `dataset_family + ticker +
session_date` se espera observar dato o evaluar missingness.

No mide presencia real.
No mide calidad.
No reemplaza `data_quality_report`.

## 2. Unidad logica

Unidad:

```text
expected dataset-family ticker session
```

Grain:

```text
dataset_family + ticker + session_date
```

## 3. Layout fisico objetivo

Raiz operativa:

```text
E:/TSIS/data/data_foundation_outputs/expected_data_calendar
```

Artefactos:

```text
expected_data_calendar_v0_1/
_expected_data_calendar_summary_v0_1.csv
_expected_data_calendar_manifest_v0_1.json
```

Layout:

```text
partitioned parquet dataset by dataset_family/year
```

Builder:

```text
01_TSIS_DATA_FOUNDATION/scripts/materialize_expected_data_calendar.py
```

## 4. Fuentes

Fuentes gobernantes v0.1:

- `instrument_master_v0_1`
- `market_calendar_v0_1`

`instrument_master` aporta identidad y ventana valida.
`market_calendar` aporta sesiones XNYS.

## 5. Columnas requeridas

- `dataset_family`
- `expected_dataset_id`
- `expected_source_root`
- `instrument_id`
- `ticker`
- `session_date`
- `expected_session`
- `expected_reason`
- `expectation_scope`
- `calendar`
- `timezone`
- `year`
- `month`
- `valid_from`
- `valid_to`
- `instrument_master_schema_version`
- `instrument_master_build_run_id`
- `market_calendar_schema_version`
- `market_calendar_build_run_id`
- `expectation_policy_version`
- `build_run_id`
- `schema_version`
- `created_at_utc`

## 6. Valores esperados

`dataset_family` v0.1:

- `daily_raw`
- `ohlcv_1m_raw`
- `trades_raw`
- `quotes_raw`

`expected_session` debe ser `true` para todas las filas materializadas.

`expected_reason` v0.1:

```text
instrument_valid_window_and_xnys_session
```

`expectation_policy_version`:

```text
expected_data_calendar_policy_v0_1
```

`schema_version`:

```text
expected_data_calendar_v0_1
```

## 7. Reglas estructurales minimas

Hard failures:

- columnas requeridas ausentes;
- duplicado de `dataset_family + ticker + session_date`;
- `expected_session != true`;
- `session_date < valid_from`;
- `session_date > valid_to`;
- `calendar != XNYS`;
- `timezone != America/New_York`;
- `schema_version != expected_data_calendar_v0_1`;
- cero filas;
- ausencia de alguna familia v0.1.

Review:

- cambio de hash de `instrument_master` o `market_calendar` sin rematerializar;
- nueva familia de datos core no incluida;
- extension de calendario despues de `2026-03-09`;
- cambio de universe policy.

## 8. Interpretacion

Permitido:

- construir denominadores de coverage;
- separar missing esperado de missing no aplicable;
- alimentar `dataset_certification_matrix`;
- alimentar `data_quality_report`;
- auditar cobertura por familia/ticker/date.

No permitido:

- inferir que el dato existe;
- inferir que el dato es limpio;
- usar como precio, feature o senal;
- ocultar gaps de familias con baja presencia fisica;
- reemplazar validadores especificos de daily, 1m, trades o quotes.
