# Runtime User Invocation Bounded Interface Execution Regression v0.1.2 Authorization

Gate: `runtime_user_invocation_bounded_interface_execution_regression_v0_1_2`
Date: `2026-07-29`
Status: `AUTHORIZED_CONTROL_PLANE_REGRESSION_NO_PHYSICAL_READ`

## Purpose

Regress the prior bounded runtime user invocation behavior against the externally accepted provider v0.1.2 contracts and the hardened Market State core-four replay timestamp contract.

This gate does not run the runtime. It checks whether the evidence is sufficient to reissue a v0.1.2 `RuntimeInvocationResponse` and `StateBundleManifest` that can proceed to physical evidence alignment.

## Authority

```text
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
accepted_provider_zip = runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T141808Z.zip
accepted_provider_zip_sha256 = 191f40e40f2cfe374ce2f493fb9dd3e2509e33f64b9ed8f3969c9c8b0badf759
```

## Hard Boundaries

```text
runtime_requests_executed = 0
interface_invocations = 0
runtime_builds_executed = 0
physical_file_reads = 0
parquet_opened = false
state_rows_read = 0
physical_state_rows_delivered = 0
StateReplayFeed_records_emitted = 0
backtest_runs_started = 0
datasets_written = 0
registry_mutations = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

## Authorized Outputs

```text
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/configs/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_scope_v0_1.json
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_matrix_v0_1.json
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_readout_v0_1.md
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/scripts/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runner.py
```

If row-addressable replay availability evidence is missing, the correct close is blocked, not pass.
