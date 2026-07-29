# Runtime User Invocation Bounded Interface Execution Readout v0.1

Gate: `runtime_user_invocation_bounded_interface_execution_v0_1`
Run: `runtime_user_invocation_bounded_interface_execution_v0_1_20260728T1731090000`
Date: `2026-07-28`
Status: `CLOSED_PASS_BOUNDED_INTERFACE_EXECUTION_WITH_RESTRICTIONS_PENDING_REVIEW`

## Result

```text
case_count = 8
hard_failures = 0
interface_invocations = 8
runtime_builds_executed = 0
materializer_executions = 0
source_market_data_rows_read = 0
datasets_written = 0
registry_mutations = 0
physical_state_rows_delivered = 0
StateReplayFeed records emitted = 0
backtest_runs_started = 0
```

The bounded provider interface behavior test produced governed response artifacts and, for reuse hits, metadata-only `StateBundleManifest` references. It did not build Market State or Event State, did not read physical state rows, did not mutate registries and did not authorize downstream consumption.

## Next Gate

```text
runtime_user_invocation_bounded_interface_execution_review_v0_1
```
