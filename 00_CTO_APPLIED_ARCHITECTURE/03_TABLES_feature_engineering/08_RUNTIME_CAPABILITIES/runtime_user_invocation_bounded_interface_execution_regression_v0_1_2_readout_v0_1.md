# Runtime User Invocation Bounded Interface Execution Regression v0.1.2 Readout

Gate: `runtime_user_invocation_bounded_interface_execution_regression_v0_1_2`
Date: `2026-07-29`
Status: `CLOSED_PASS_V0_1_2_CONTROL_PLANE_REISSUE_WITH_CANONICAL_BUNDLE_AND_EXACT_REUSE_EVIDENCE_NO_CONSUMPTION`

```text
case_count = 10
failed_cases = 0
reissued_state_resolution_request = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_resolution_request_instance_v0_1.json
reissued_runtime_invocation_response = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_runtime_invocation_response_v0_1.json
reissued_state_bundle_manifest = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_user_invocation_bounded_interface_execution_regression_v0_1_2_state_bundle_manifest_v0_1.json
runtime_requests_executed = 0
runtime_builds_executed = 0
physical_file_reads = 0
parquet_opened = false
state_rows_read = 0
StateReplayFeed_records_emitted = 0
backtest_consumption = false
production = false
downstream = false
```

The regression now binds the accepted provider v0.1.2 control-plane contracts to the exact scale-validation Market State candidate and its row-addressable replay availability sidecar. The emitted request, response and bundle are metadata/control-plane artifacts only; they do not authorize physical consumption.

Next gate:

```text
state_bundle_manifest_physical_evidence_alignment_v0_2
```
