# Corporate Actions Table Validators `v0_1`

## 1. Scope

Dataset:

- `corporate_actions_table_v0_1`

Raiz:

```text
E:/TSIS/data/data_foundation_outputs/corporate_actions_table
```

## 2. Artefactos gobernados

- dataset contract: `01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md`
- materializer: `scripts/materialize_corporate_actions_table.py`

## 3. Unidad de validacion

```text
corporate_action_id
```

Secondary key:

```text
instrument_id + ticker + action_type + action_date + source_system + source_event_id
```

## 4. Validadores minimos

### 4.1 Artifact presence

Debe comprobar:

- `corporate_actions_table_v0_1.parquet`;
- `_corporate_actions_table_manifest_v0_1.json`;
- `_corporate_actions_table_summary_v0_1.csv`.

### 4.2 Schema conformity

Debe comprobar:

- columnas requeridas;
- `schema_version = corporate_actions_table_v0_1`;
- `action_type` en vocabulario;
- `source_system` en vocabulario;
- lineage no vacio.

### 4.3 Payload integrity

Hard failures:

- duplicate `corporate_action_id`;
- missing `instrument_id`;
- missing `ticker`;
- missing `action_date`;
- split terms non-positive;
- dividend cash amount negative;
- no rows.

Review:

- ticker-change target unusual or not reconciled;
- action outside current instrument valid window;
- future action dates;
- cross-source overlaps.

### 4.4 Source reconciliation

Debe comprobar:

- source tree fingerprints;
- output hash;
- counts by `source_system + action_type`;
- exclusion of `_empty=True` source placeholders;
- join to `instrument_master_v0_1`.

## 5. Salida minima

Un validator debe emitir:

- run id;
- dataset id;
- rows checked;
- action type counts;
- source system counts;
- duplicate id count;
- invalid split count;
- negative dividend amount count;
- review counts;
- output hash;
- source fingerprints.

## 6. Regla final

Pasar validadores habilita uso como contexto corporativo y lineage de ajuste.

No habilita continuidad economica completa ni precio ajustado final.

