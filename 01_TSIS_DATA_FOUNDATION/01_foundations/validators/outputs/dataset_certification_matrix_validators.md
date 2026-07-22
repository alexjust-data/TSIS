# Dataset Certification Matrix Validators `v0_1`

## 1. Scope

Dataset:

```text
dataset_certification_matrix_v0_1
```

Root:

```text
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix
```

## 2. Governed Artifacts

- dataset contract: `01_foundations/contract_registry/dataset_contracts/dataset_certification_matrix_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/dataset_certification_matrix_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/dataset_certification_matrix_consumption_policy.md`
- materializer: `scripts/materialize_dataset_certification_matrix.py`

## 3. Unit Of Validation

```text
dataset_family + certification_scope + quality_policy_version
```

## 4. Minimum Validators

### 4.1 Artifact Presence

Must check:

- parquet file `dataset_certification_matrix_v0_1.parquet`;
- `_dataset_certification_matrix_manifest_v0_1.json`;
- `_dataset_certification_matrix_summary_v0_1.csv`;
- all contract paths declared in the manifest.

### 4.2 Schema Conformity

Must check:

- required columns exist;
- `schema_version = dataset_certification_matrix_v0_1`;
- `quality_policy_version = dataset_certification_matrix_policy_v0_1`;
- one non-empty `certification_id` per row;
- no duplicate `dataset_family`.

### 4.3 Source Matrix Reconciliation

Must check:

- source matrix file exists;
- source matrix SHA matches manifest;
- row count equals the 13 source families;
- parsed verdict/status counts match manifest validations.

### 4.4 Evidence Link Integrity

Hard failures:

- missing physical root;
- missing quality report;
- missing inspection dossier;
- missing schema contract;
- missing dataset contract;
- missing registry entry;
- missing consumption policy;
- missing validator;
- visual-complete row with zero images;
- artifact matrix presence claim contradicted by missing file evidence.

### 4.5 Gate Integrity

Must check:

- `blocked_by_data_defect` maps to `blocked_from_backtest_core`;
- scoped completion or scoped verdict maps to `scoped_only`;
- usable declared-scope verdict maps to `declared_scope_allowed`;
- blocked/scoped counts match manifest.

## 5. Output Fields

A validator must emit:

- run id;
- dataset id;
- rows checked;
- family count;
- missing artifact counts;
- duplicate family count;
- status counts;
- source matrix sha;
- output sha;
- hard fail count;
- evidence artifacts path.

## 6. Final Rule

Passing this validator proves that the family-level gate is structurally
coherent and evidence-linked.

It does not prove row-level data quality in any family.
