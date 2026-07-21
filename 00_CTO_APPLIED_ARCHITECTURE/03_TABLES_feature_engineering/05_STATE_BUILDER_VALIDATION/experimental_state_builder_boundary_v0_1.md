# Experimental State Builder Boundary v0.1

Status: `experimental_builder_boundary_v0_1`
Date: `2026-07-21`
Scope: `phase_b_non_production_builder_probe_boundary`

Este documento fija la frontera del siguiente paso despues de completar los
12 disenos de Builder Validation de `TSIS Market Ontology v1`.

El siguiente builder no sera un builder de produccion.
Sera un builder experimental.

## 1. Boundary Decision

```text
TSIS_Market_Ontology_v1 = FROZEN
Operational_Mapping_v1 = COMPLETE
Builder_Validation_Designs_v1 = COMPLETE
next_builder_type = experimental_state_builder
production_builder_authorized = false
state_consumption_authorized = false
physical_materialization_authorized = false
dataset_promotion_authorized = false
market_state_operational_authority = false
```

## 2. Purpose

El builder experimental existe para descubrir problemas que los documentos no
pueden revelar de forma completa:

```text
source availability gaps
timestamp and cutoff ambiguity
join-key ambiguity
profile resolution failures
missing lineage
quality flag propagation failures
cross-object naming conflicts
blocked capability leaks
unexpected source/schema mismatch
```

## 3. Allowed Scope

```text
allowed =
  non_production_resolution_probe
  sample_instrument_runs
  sample_decision_timestamp_runs
  dry_run_state_rows
  pass_fail_matrix_generation
  missing_capability_report
  temporal_legality_report
  lineage_report
  mapping_feedback_report
```

## 4. Not Authorized

```text
not_authorized =
  production_market_state_builder
  production_event_state_builder
  live_trading_consumption
  canonical_schema_change
  physical_state_materialization
  promoted_dataset_output
  strategy_signal_authority
  execution_truth
```

## 5. Execution Contract

If the experimental builder run is long, it must comply with:

```text
C:\TSIS_Data\LONG_RUNNING_OPERATIONS_CONTRACT.md
```

Minimum execution evidence:

```text
experimental_builder_run_id
code_commit
input_mapping_versions
input_builder_validation_versions
sample_instruments
sample_decision_timestamps
source_table_versions
pass_fail_matrix
blocked_capability_report
temporal_legality_report
lineage_report
final_experimental_findings
```

## 6. Promotion Rule

```text
experimental_builder_findings != production_authority

production authority requires:
  reviewed builder validation evidence
  resolved blocking findings
  approved Market State Integration
  schema/materialization decision if needed
  explicit Operational Promotion
```

## 7. Evidence TSIS

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\05_STATE_BUILDER_VALIDATION
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\04_INFORMATION_OBJECT_OPERATIONAL_MAPPING
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\03_INFORMATION_OBJECTS\TSIS_MARKET_ONTOLOGY_V1_FREEZE.md
```
