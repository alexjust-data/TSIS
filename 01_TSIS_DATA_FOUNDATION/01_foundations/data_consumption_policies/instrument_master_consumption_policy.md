# Instrument Master Consumption Policy `v0_1`

## 1. Dataset gobernado

- `dataset_id`: `instrument_master_v0_1`
- contrato: `01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml`
- validators: `01_foundations/validators/outputs/instrument_master_validators.md`

## 2. Regla central

`instrument_master` puede usarse para identidad, scope y flags.

No puede usarse como:

- feature alpha;
- membership diaria fully point-in-time;
- lifecycle/merger resolver final;
- fuente de precio;
- fuente de noticias;
- ni fuente de ejecucion.

## 3. Consumidores permitidos

### `event_engine`

Permitido.

Debe preservar:

- `instrument_id`;
- `ticker`;
- `valid_from/valid_to`;
- `ticker_type_code`;
- `identity_resolution_level`;
- `ticker_change_event_count`;
- `lt1b_*` fields.

Si `ticker_change_event_count > 0`, el evento debe poder entrar en review si
la logica depende de continuidad historica.

### `backtest_core`

Permitido para:

- filtrar ticker/scope `<1B>`;
- excluir o marcar tipos no common stock;
- evitar fechas fuera de ventana PTI.

No permitido:

- usar `overview_market_cap` como feature;
- inferir market cap diario;
- fusionar tickers por `instrument_id` sin policy adicional.

### `backtest_extended`

Permitido con las mismas restricciones de `backtest_core`.

Puede incluir casos review si las flags viajan a reportes y sensitivity.

### `ml_flagged`

Permitido si las flags viajan como masks/features de calidad:

- `identity_resolution_level`;
- `ticker_type_code`;
- `ticker_change_event_count`;
- `reference_snapshot_timing`;
- `has_reference_events`.

### `research_only`

Permitido para estudiar:

- cobertura de identidad;
- conflictos CIK/FIGI;
- tipos de instrumentos;
- ticker changes;
- preparacion de lifecycle tables.

## 4. Consumidores restringidos

### `ml_primary`

No habilitado por defecto.

Requiere:

- validacion de leakage temporal;
- policy sobre uso de campos reference actualizados;
- tratamiento de ticker changes.

### `execution_simulator`

Solo puede usar identidad/contexto.

No puede inferir liquidez, venue routing, fillability o slippage desde esta
tabla.

### `live_downstream_candidate`

No habilitado hasta que exista run operacional repetible y latencia/refresh
definidos.

## 5. Flags obligatorias

Deben preservarse downstream:

- `identity_resolution_level`
- `reference_snapshot_timing`
- `ticker_type_code`
- `is_common_stock`
- `ticker_change_event_count`
- `lt1b_classification_1b`
- `lt1b_first_seen_date`
- `lt1b_last_observed_date`

## 6. Estados de consumo

`good_identity`:

- `identity_resolution_level` en `share_class_figi`, `composite_figi`,
  `cik_ticker`;
- `ticker` no nulo;
- `valid_from <= valid_to`.

`review_identity`:

- `ticker_only_fallback`;
- `ticker_change_event_count > 0`;
- `reference_snapshot_timing = after_anchor`;
- tipo de instrumento no reconocido.

`restricted_non_common_stock`:

- `is_common_stock = false`.

No equivale a bad data, pero puede quedar fuera de estrategias common-stock.

## 7. Regla final

Toda tabla que use `instrument_master` debe conservar suficiente metadata para
reconstruir que version de identidad, universo y ventana PTI se aplico.
