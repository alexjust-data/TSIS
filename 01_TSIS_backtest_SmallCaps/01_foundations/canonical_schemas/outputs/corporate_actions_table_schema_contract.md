# Corporate Actions Table Schema Contract `v0_1`

## 1. Rol

Este documento define el schema canonico inicial para:

- `corporate_actions_table_v0_1`

`corporate_actions_table` es una tabla compacta de acciones corporativas para
CAPA 1 Data Foundation.

Su funcion es preservar splits, dividends y ticker changes con lineage
explicito para que daily, intradia, eventos, labels y data quality no mezclen
movimientos de mercado con eventos corporativos.

## 2. Unidad logica

Unidad:

```text
corporate action observation
```

Grain:

```text
instrument_id + ticker + action_type + action_date + source_system + source_event_id
```

El `source_system` forma parte del grano porque `reference` y `additional`
pueden traer la misma accion con distinto lineage.

## 3. Layout fisico objetivo

Raiz operativa:

```text
E:/TSIS/data/data_foundation_outputs/corporate_actions_table
```

Artefactos:

```text
corporate_actions_table_v0_1.parquet
_corporate_actions_table_summary_v0_1.csv
_corporate_actions_table_manifest_v0_1.json
```

Builder:

```text
01_TSIS_backtest_SmallCaps/scripts/materialize_corporate_actions_table.py
```

## 4. Fuentes

Fuentes gobernantes v0.1:

- `E:/TSIS/data/reference/splits`
- `E:/TSIS/data/reference/dividends`
- `E:/TSIS/data/reference/events`
- `E:/TSIS/data/additional/corporate_actions/splits`
- `E:/TSIS/data/additional/corporate_actions/dividends`
- `E:/TSIS/data/additional/corporate_actions/ticker_events`
- `instrument_master_v0_1`

`reference` es fuente primaria cuando existe.
`additional` se conserva como fuente secundaria y de reconciliacion.

## 5. Columnas requeridas

- `corporate_action_id`
- `instrument_id`
- `ticker`
- `action_type`
- `action_date`
- `action_year`
- `source_system`
- `source_dataset`
- `source_root`
- `source_priority`
- `source_event_id`
- `is_reference_primary_source`
- `is_additional_secondary_source`
- `split_from`
- `split_to`
- `split_ratio`
- `cash_amount`
- `currency`
- `declaration_date`
- `ex_dividend_date`
- `pay_date`
- `record_date`
- `dividend_type`
- `dividend_frequency`
- `ticker_change_date`
- `ticker_change_ticker`
- `event_name`
- `source_ingested_utc`
- `valid_from`
- `valid_to`
- `within_instrument_valid_window`
- `instrument_master_schema_version`
- `instrument_master_build_run_id`
- `build_run_id`
- `schema_version`
- `created_at_utc`

## 6. Valores esperados

`action_type` v0.1:

- `split`
- `dividend`
- `ticker_change`

`source_system` v0.1:

- `reference`
- `additional`

`schema_version`:

```text
corporate_actions_table_v0_1
```

## 7. Reglas estructurales minimas

Hard failures:

- `corporate_action_id` duplicado;
- `instrument_id` nulo;
- `ticker` nulo;
- `action_type` fuera de vocabulario;
- `action_date` nula;
- split con `split_from <= 0` o `split_to <= 0`;
- dividend con `cash_amount < 0`;
- `schema_version != corporate_actions_table_v0_1`;
- cero filas.

Review:

- `within_instrument_valid_window = false`;
- acciones futuras respecto al calendario objetivo;
- cross-source overlap entre `reference` y `additional`;
- ticker-change target no reconciliado con identidad economica futura;
- dividend fields incompletos salvo `ex_dividend_date` y `cash_amount`.

## 8. Interpretacion

Permitido:

- explicar gaps o discontinuidades;
- alimentar `daily_adjusted` y futuras vistas ajustadas;
- construir flags de eventos corporativos;
- evitar leakage de splits/dividends en labels o features;
- reconciliar `reference` contra `additional`.

No permitido:

- tratar `additional` como reemplazo primario de `reference`;
- inferir continuidad economica completa entre ticker changes;
- usar dividendos o splits como senal de estrategia sin contrato de evento;
- reparar precios sin preservar lineage.

