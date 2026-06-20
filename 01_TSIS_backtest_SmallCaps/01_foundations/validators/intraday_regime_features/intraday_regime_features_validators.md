# Intraday Regime Features Validators

## Scope

This validator contract governs:

```text
intraday_regime_features_v0_1
```

Physical root:

```text
E:/TSIS/data/intraday_regime_features
```

## Authorities

Read with:

- `contract_registry/dataset_contracts/intraday_regime_features_dataset_contract_v0_1.md`
- `data_consumption_policies/intraday_regime_features_consumption_policy.md`
- `dataset_registry/features/intraday_regime_features_registry_entry.yaml`
- `canonical_schemas/features/intraday_regime_features_schema_contract.md`
- `module_contracts/intraday_regime_features_consumer_contract_v0_1.md`
- `module_contracts/intraday_regime_features_variable_taxonomy_v0_1.md`
- `inspection_dossiers/intraday_regime_features/intraday_regime_features_semantic_pilot_readout_v0_1.md`
- `data_quality_report/families/intraday_regime_features_quality_report_v0_1.md`

## Validation Unit

The current pilot validation unit is:

```text
ticker + year/month/day feature row
```

The semantic pilot comparison unit is:

```text
ticker + month + role
```

where role is one of:

- `reverse_split`;
- `forward_split`;
- `control`.

## Required Checks

### Root And Layout

The validator must check:

- root exists;
- ticker partition directories exist;
- materialization summary exists:
  - `E:/TSIS/data/intraday_regime_features/_intraday_regime_features_materialization_summary.csv`;
- feature parquet files are readable.

### Schema

Feature files must match:

- `canonical_schemas/features/intraday_regime_features_schema_contract.md`

Required checks include:

- ticker identity;
- date/day identity;
- expected feature columns;
- numeric parseability;
- no hidden label/target columns;
- no downstream target leakage;
- source reference to `ohlcv_1m_split_normalized`.

### Semantic Pilot

The validator must preserve the pilot's core question:

```text
Do cross-session features change when raw 1m would create a split-driven mechanical shock, and remain neutral when no such shock should exist?
```

Required checks:

- compare raw-derived vs split-normalized-derived feature values;
- preserve `future_split_factor`;
- classify positive strong cases;
- classify coherent boundary cases;
- classify controls;
- emit max absolute differences for sensitive features.

### Production Boundary

The validator must not treat the pilot as full production promotion.

Missing before full promotion:

- full-universe materialization;
- stable production schedule;
- broader feature coverage audit;
- feature null/outlier profile;
- downstream model contract;
- leakage gate beyond pilot scope.

## Current Observed Status

Observed physical footprint:

- 8 ticker directories;
- 8 parquet files;
- 1 materialization summary CSV.

Semantic pilot cases:

- 4 reverse splits;
- 4 forward splits;
- 2 controls.

The pilot successfully demonstrates that `ohlcv_1m_split_normalized` prevents false cross-session regime shocks in the tested cases.

## Acceptance States

Allowed states:

- `complete_scoped_pilot`;
- `feature_layer_provisional`;
- `blocked_for_production`;
- `promoted_after_full_feature_audit`.

Current family state:

```text
complete_scoped_pilot
```

## Forbidden Conclusions

The validator must not conclude:

- the feature layer is full-universe complete;
- the feature layer is production-ready for all models;
- the feature layer replaces raw/split-normalized upstream audit;
- the pilot proves alpha;
- the pilot removes all leakage risk.

## Output Contract

A compliant future validator must emit:

- materialization summary;
- schema validation table;
- null/outlier profile;
- feature drift profile;
- raw-vs-split-normalized comparison table;
- case evidence;
- consumer matrix;
- final human readout.
