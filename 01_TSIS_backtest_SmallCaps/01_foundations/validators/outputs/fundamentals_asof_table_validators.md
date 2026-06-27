# Fundamentals As-Of Table Validators `v0_1`

## 1. Scope

Validators apply to:

```text
fundamentals_asof_table_v0_1
```

## 2. Manifest Validators

Required checks:

- manifest exists;
- dataset path exists;
- summary exists;
- contract paths exist;
- output tree hash matches manifest;
- source root is `E:/TSIS/data/additional/financials`;
- excluded sources are declared for `ratios` and `E:/TSIS/data/financial`.

## 3. Schema Validators

Required columns include:

- `fundamental_asof_id`
- `ticker`
- `instrument_id`
- `statement_family`
- `period_end`
- `filing_date`
- `as_of_date`
- `fundamental_quality_state`
- `valid_for_event_context_candidate`
- `valid_for_ml_feature_candidate`
- `valid_for_rl_training_direct`
- `source_file_relative_path`
- `source_file_row_number`
- `materialization_scope`
- `quality_policy_version`
- `schema_version`
- `build_run_id`

Required statement families:

```text
income_statements
balance_sheets
cash_flow_statements
```

## 4. As-Of Validators

Required checks:

- `as_of_date = filing_date`;
- `period_end_is_availability_date = false`;
- no primary-valid row has `period_end > as_of_date`;
- no row with missing filing date or period end is primary-valid;
- `valid_for_event_context_candidate` equals `good_statement_asof`.

## 5. Consumer Gate Validators

Required checks:

- `full_universe_claim` is always false;
- `valid_for_rl_training_direct` is always false;
- `requires_event_time_filter` is always true;
- `prohibited_without_asof_filter` is always true;
- `ratios_excluded_from_core_v0_1` is always true;
- `standalone_financial_root_excluded_from_core_v0_1` is always true.

## 6. Source Reconciliation Validators

Required current v0.1 checks:

- source statement files: `14472`;
- business rows: `621756`;
- empty sentinel files: `36`;
- output rows: `621756`;
- duplicate `fundamental_asof_id`: `0`;
- duplicate source grain: `0`.

## 7. Evidence

Executable pytest contract:

```text
tests/data_foundation_outputs/test_fundamentals_asof_table_contract.py
```

Test output must be stored under:

```text
C:/TSIS_Data/tests/test_runs/YYYY-MM-DD/data_foundation_outputs_fundamentals_asof_table_v0_1/
```
