# Market Calendar Consumption Policy `v0_1`

## 1. Dataset gobernado

- `dataset_id`: `market_calendar_v0_1`
- contrato: `01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml`
- validators: `01_foundations/validators/outputs/market_calendar_validators.md`

## 2. Regla central

`market_calendar` puede usarse para sesiones y ventanas temporales.

No puede usarse como fuente de:

- precio;
- liquidez;
- halts;
- venue routing;
- corporate events;
- execution realism.

## 3. Consumidores permitidos

### `event_engine`

Permitido para:

- validar que una fecha es trading session;
- construir ventanas pre/post event;
- manejar early close.

### `backtest_core`

Permitido para:

- expected sessions;
- session filtering;
- evitar comparar dias no equivalentes.

### `master_daily_table`

Permitido para:

- completar trading-day scaffold;
- expected rows por ticker/window.

### `master_intraday_bar_table`

Permitido para:

- session boundaries;
- premarket/regular/after-hours policy cuando aplique.

### `data_quality_report`

Permitido para:

- coverage;
- missing session diagnostics;
- anomalous date detection.

## 4. Consumidores restringidos

### `execution_simulator`

Solo puede usarlo para calendario base.

No puede inferir:

- halt windows;
- auction behavior;
- venue-specific outages;
- liquidity availability.

### `live_downstream_candidate`

No queda habilitado para fechas posteriores a `2025-12-31` sin extension del
calendario y manifest nuevo.

## 5. Flags obligatorias

Deben preservarse o ser recuperables:

- `calendar`
- `timezone`
- `session_date`
- `open_utc`
- `close_utc`
- `is_early_close`
- `schema_version`
- `build_run_id`

## 6. Regla final

Todo consumidor que declare session-aware behavior debe citar que calendario y
version uso.
