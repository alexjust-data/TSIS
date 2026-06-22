# Market Calendar Schema Contract `v0_1`

## 1. Rol

Este documento define el schema canonico para:

- `market_calendar_v0_1`

`market_calendar` es una tabla de sesiones oficiales usada por CAPA 1 Data
Foundation para construir ventanas temporales comparables, expected coverage,
event windows y filtros de trading day.

## 2. Unidad logica

Unidad:

```text
exchange trading session
```

Grain:

```text
calendar + session_date
```

## 3. Layout fisico objetivo

Raiz operativa:

```text
E:/TSIS/data/data_foundation_outputs/market_calendar
```

Artefactos:

```text
market_calendar_v0_1.parquet
_market_calendar_summary_v0_1.csv
_market_calendar_manifest_v0_1.json
```

Builder/materializer:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_market_calendar.py
```

## 4. Fuentes

Fuente local gobernante para v0.1:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.parquet
```

Artefacto de metadata fuente:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/data/reference/market_calendar_official_XNYS_20050101_20251231.meta.json
```

Script historico de generacion:

```text
01_TSIS_backtest_SmallCaps/scripts/agent05_build_market_calendar_official.py
```

## 5. Columnas requeridas

- `session_date`
- `open_utc`
- `close_utc`
- `open_et`
- `close_et`
- `session_minutes`
- `is_early_close`
- `year`
- `month`
- `dow`
- `calendar`
- `timezone`
- `source_calendar_artifact`
- `build_run_id`
- `schema_version`
- `created_at_utc`

## 6. Tipos semanticos esperados

- `session_date`: date parseable
- `open_utc`, `close_utc`: timestamp UTC parseable
- `open_et`, `close_et`: timestamp America/New_York parseable
- `session_minutes`: numeric positive
- `is_early_close`: bool
- `year`: integer
- `month`: integer 1..12
- `dow`: weekday label
- `calendar`: string, v0.1 expected `XNYS`
- `timezone`: string, v0.1 expected `America/New_York`
- lineage fields: string no vacio

## 7. Reglas estructurales minimas

Hard failures:

- duplicate `calendar + session_date`;
- missing required columns;
- unparseable date/timestamp;
- `open_utc >= close_utc`;
- `session_minutes <= 0`;
- `calendar != XNYS` en v0.1;
- `timezone != America/New_York` en v0.1;
- no sessions.

Review:

- unexpected early-close count;
- source artifact hash changed without manifest update;
- date range not matching declared source range.

## 8. Interpretacion

Permitido:

- determinar trading sessions;
- construir windows premarket/regular/after-hours con timezone explicita;
- medir expected sessions para coverage;
- validar event dates.

No permitido:

- inferir precio, liquidez o market quality;
- sustituir halts;
- sustituir calendario oficial futuro si cambia exchange/source policy;
- usar para calendario non-US sin nuevo contrato.

## 9. Documentos relacionados

- `01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/market_calendar_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml`
- `01_foundations/validators/outputs/market_calendar_validators.md`
- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
