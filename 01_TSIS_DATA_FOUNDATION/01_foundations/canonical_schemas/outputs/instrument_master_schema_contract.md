# Instrument Master Schema Contract `v0_1`

## 1. Rol

Este documento define el schema canonico inicial para:

- `instrument_master_v0_1`

`instrument_master` es una tabla compacta de identidad operativa para CAPA 1
Data Foundation.

Su funcion es resolver, de forma trazable, que representa un ticker dentro del
marco operativo `<1B>` vigente y que identificadores/contexto minimo deben
viajar hacia Event Engine, backtests, research y futuras tablas maestras.

## 2. Unidad logica

Unidad logica:

```text
operational instrument identity row
```

Grain v0.1:

```text
ticker del universo lt1b_universe_v0_1
```

Nota:

`v0_1` no resuelve continuidad economica completa entre ticker changes. Marca
la existencia de eventos de ticker change, pero no fusiona instrumentos por
identidad economica.

## 3. Layout fisico objetivo

Raiz operativa recomendada:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master
```

Artefactos esperados:

```text
instrument_master_v0_1.parquet
_instrument_master_summary_v0_1.csv
_instrument_master_manifest_v0_1.json
```

Builder:

```text
01_TSIS_DATA_FOUNDATION/scripts/materialize_instrument_master.py
```

## 4. Claves

Clave primaria v0.1:

```text
ticker
```

Identificador operativo:

```text
instrument_id
```

`instrument_id` se construye por prioridad:

```text
share_class_figi -> composite_figi -> cik+ticker -> ticker
```

El campo `identity_resolution_level` debe declarar que nivel se uso.

## 5. Columnas requeridas

Identidad:

- `instrument_id`
- `ticker`
- `identity_resolution_level`
- `ticker_identity_scope`
- `valid_from`
- `valid_to`

Metadata reference:

- `name`
- `market`
- `locale`
- `primary_exchange`
- `ticker_type_code`
- `ticker_type_description`
- `is_common_stock`
- `active_in_reference`
- `currency_name`
- `cik`
- `composite_figi`
- `share_class_figi`

Exchange:

- `exchange_name`
- `exchange_acronym`
- `exchange_mic`
- `exchange_operating_mic`

Overview/context:

- `overview_request_date`
- `overview_market_cap`
- `overview_sic_code`
- `overview_sic_description`
- `overview_list_date`
- `overview_ticker_root`
- `overview_weighted_shares_outstanding`

Universo `<1B>`:

- `is_lt1b_operational`
- `lt1b_first_seen_date`
- `lt1b_last_observed_date`
- `lt1b_anchor_date_used`
- `lt1b_status_rebuilt`
- `lt1b_classification_1b`
- `lt1b_classification_reason_1b`
- `lt1b_market_cap_t`
- `lt1b_is_small_cap_t`
- `lt1b_shares_source`
- `lt1b_shares_observed_date`
- `lt1b_shares_age_days`

Ticker events:

- `has_reference_events`
- `ticker_change_event_count`
- `first_ticker_change_date`
- `latest_ticker_change_date`

Lineage:

- `reference_snapshot_date`
- `reference_snapshot_timing`
- `reference_last_updated_utc`
- `source_reference_root`
- `source_lt1b_universe_path`
- `build_run_id`
- `schema_version`
- `created_at_utc`

## 6. Tipos semanticos esperados

- `instrument_id`: string no vacio
- `ticker`: string no vacio
- `valid_from`, `valid_to`: date parseable
- `is_common_stock`, `is_lt1b_operational`, `has_reference_events`: boolean
- `ticker_change_event_count`: integer >= 0
- `overview_market_cap`, `lt1b_market_cap_t`: numeric nullable
- fechas `*_date`: date parseable o null permitido segun fuente
- timestamps `*_utc`: timestamp/string parseable cuando existan

## 7. Reglas estructurales minimas

Hard failures:

- `ticker` nulo o vacio;
- `instrument_id` nulo o vacio;
- duplicado de `ticker`;
- `valid_from > valid_to`;
- `lt1b_classification_1b` fuera de las clases incluidas por el contrato;
- `schema_version != instrument_master_v0_1`;
- `is_lt1b_operational != true`.

Review:

- `identity_resolution_level = ticker_only_fallback`;
- `ticker_type_code` nulo o no reconocido;
- `is_common_stock = false` si el consumidor exige common stock;
- `reference_snapshot_timing = after_anchor`;
- `ticker_change_event_count > 0`;
- CIK/FIGI ausentes.

## 8. Interpretacion

Permitido:

- resolver identidad operativa minima antes de unir daily/intraday/news/halts;
- filtrar por tipo de instrumento;
- preservar ventana PTI operacional `<1B>`;
- pasar flags de identidad hacia Event Engine y Strategy Research.

No permitido:

- tratar `instrument_master_v0_1` como universe membership diario fully PTI;
- inferir continuidad economica cerrada entre ticker changes;
- usar `overview_market_cap` como feature diaria point-in-time;
- reemplazar `reference_v0_1`, `lt1b_universe_v0_1` o futuros lifecycle tables.

## 9. Documentos relacionados

- `01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md`
- `01_foundations/data_consumption_policies/instrument_master_consumption_policy.md`
- `01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml`
- `01_foundations/validators/outputs/instrument_master_validators.md`
