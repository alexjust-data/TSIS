# Market Calendar Validators `v0_1`

## 1. Scope

Dataset:

- `market_calendar_v0_1`

Raiz:

```text
E:/TSIS/data/data_foundation_outputs/market_calendar
```

## 2. Artefactos gobernados

- dataset contract: `01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/market_calendar_consumption_policy.md`
- materializer: `scripts/materialize_market_calendar.py`

## 3. Unidad de validacion

```text
calendar + session_date
```

## 4. Validadores minimos

### 4.1 Artifact presence

Debe comprobar:

- `market_calendar_v0_1.parquet`;
- `_market_calendar_manifest_v0_1.json`;
- `_market_calendar_summary_v0_1.csv`.

### 4.2 Schema conformity

Debe comprobar:

- columnas requeridas;
- fechas/timestamps parseables;
- `schema_version = market_calendar_v0_1`;
- `calendar = XNYS`;
- `timezone = America/New_York`.

### 4.3 Session integrity

Hard failures:

- duplicate `calendar + session_date`;
- `open_utc >= close_utc`;
- `session_minutes <= 0`;
- no rows;
- unordered or unparseable sessions.

### 4.4 Source reconciliation

Debe comprobar:

- source parquet hash;
- row count;
- first/last session;
- early close count;
- range declared in manifest.

## 5. Salida minima

Un validator debe emitir:

- `run_id`;
- `validated_at_utc`;
- `dataset_id`;
- `rows_checked`;
- `calendar`;
- `timezone`;
- `first_session`;
- `last_session`;
- `early_close_sessions`;
- `duplicate_session_count`;
- `invalid_window_count`;
- `hard_fail_count`;
- `manifest_path`;
- contratos/schema/policy usados.

## 6. Regla final

Pasar validadores habilita session-aware consumption.

No habilita inferencias de halts, liquidez o venue-specific execution behavior.
