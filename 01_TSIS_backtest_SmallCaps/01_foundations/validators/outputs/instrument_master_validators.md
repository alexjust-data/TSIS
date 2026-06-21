# Instrument Master Validators `v0_1`

## 1. Scope

Este documento define validadores minimos para:

- `instrument_master_v0_1`

Raiz objetivo:

```text
E:/TSIS/data/data_foundation_outputs/instrument_master
```

## 2. Artefactos gobernados

- dataset contract: `01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/instrument_master_consumption_policy.md`
- builder: `01_TSIS_backtest_SmallCaps/scripts/materialize_instrument_master.py`

## 3. Unidad de validacion

Unidad:

```text
one instrument_master row
```

Clave:

```text
ticker
```

Scope:

```text
tickers incluidos en lt1b_universe_v0_1
```

## 4. Validadores minimos

### 4.1 Root and artifact presence

Debe comprobar:

- existe `E:/TSIS/data/data_foundation_outputs/instrument_master`;
- existe `instrument_master_v0_1.parquet`;
- existe `_instrument_master_manifest_v0_1.json`;
- existe `_instrument_master_summary_v0_1.csv`.

### 4.2 Schema conformity

Debe comprobar:

- columnas requeridas por el schema;
- tipos parseables;
- `schema_version = instrument_master_v0_1`;
- fechas `valid_from`, `valid_to` parseables.

### 4.3 Key integrity

Hard failures:

- `ticker` nulo;
- `instrument_id` nulo;
- duplicado de `ticker`;
- filas fuera del universo `<1B>`;
- `valid_from > valid_to`.

### 4.4 Universe reconciliation

Debe comprobar:

- row count igual a `lt1b_universe_v0_1`;
- tickers en output == tickers en parquet `<1B>`;
- `lt1b_classification_1b` solo usa clases incluidas.

### 4.5 Identity quality

Debe contar:

- `share_class_figi`;
- `composite_figi`;
- `cik_ticker`;
- `ticker_only_fallback`.

Review:

- cualquier `ticker_only_fallback`;
- CIK/FIGI ausentes;
- `reference_snapshot_timing = after_anchor`.

### 4.6 Instrument type policy

Debe comprobar:

- `ticker_type_code` reconocido en `ticker_types`;
- `is_common_stock` coherente con `ticker_type_code = CS`;
- consumidores common-stock reciben flag para excluir no-CS.

Review:

- tipo ausente;
- tipo no reconocido;
- no-common-stock dentro del universo operativo.

### 4.7 Ticker change risk

Debe comprobar:

- `ticker_change_event_count >= 0`;
- si `ticker_change_event_count > 0`, marcar `review_ticker_change`.

No debe concluir:

- continuidad economica final;
- merger/remap cerrado;
- ni continuidad de serie historica.

## 5. Salida minima esperada

Un run de validacion debe emitir:

- `run_id`;
- `validated_at_utc`;
- `dataset_id`;
- `source_root`;
- `rows_checked`;
- `ticker_count`;
- `duplicate_ticker_count`;
- `missing_instrument_id_count`;
- `invalid_window_count`;
- `identity_resolution_counts`;
- `non_common_stock_count`;
- `ticker_change_review_count`;
- `hard_fail_count`;
- `review_count`;
- `manifest_path`;
- `schema_contract`;
- `dataset_contract`;
- `policy`;
- `registry_entry`.

## 6. Regla final

Pasar estos validadores habilita consumo de identidad y scope.

No habilita lifecycle final ni feature engineering sin policy adicional.
