# Expected Data Calendar Validators `v0_1`

## 1. Scope

Dataset:

- `expected_data_calendar_v0_1`

Raiz:

```text
E:/TSIS/data/data_foundation_outputs/expected_data_calendar
```

## 2. Artefactos gobernados

- dataset contract: `01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md`
- materializer: `scripts/materialize_expected_data_calendar.py`

## 3. Unidad de validacion

```text
dataset_family + ticker + session_date
```

## 4. Validadores minimos

### 4.1 Artifact presence

Debe comprobar:

- parquet dataset `expected_data_calendar_v0_1/`;
- `_expected_data_calendar_manifest_v0_1.json`;
- `_expected_data_calendar_summary_v0_1.csv`.

### 4.2 Schema conformity

Debe comprobar:

- columnas requeridas;
- `schema_version = expected_data_calendar_v0_1`;
- `expectation_policy_version = expected_data_calendar_policy_v0_1`;
- `expected_session = true`;
- `calendar = XNYS`;
- `timezone = America/New_York`.

### 4.3 Key integrity

Hard failures:

- duplicate `dataset_family + ticker + session_date`;
- missing `ticker`;
- missing `instrument_id`;
- missing family;
- no rows.

### 4.4 Window integrity

Debe comprobar:

- `session_date >= valid_from`;
- `session_date <= valid_to`;
- source build ids non-empty;
- output tree hash matches manifest.

### 4.5 Source reconciliation

Debe comprobar:

- source instrument master hash;
- source market calendar hash;
- expected row count from source intersection;
- rows by family equal the single-family denominator.

## 5. Salida minima

Un validator debe emitir:

- run id;
- dataset id;
- rows checked;
- rows by family;
- ticker count;
- first/last session;
- duplicate key count;
- invalid window count;
- hard fail count;
- source build ids;
- output tree hash.

## 6. Regla final

Pasar validadores prueba que el denominador de expectativa es estructuralmente
coherente.

No prueba presencia real ni calidad de daily, 1m, trades o quotes.

