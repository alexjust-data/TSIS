# Runtime Provider-Consumer Contract Compatibility Regression v0.1.2 Readout

Gate: `runtime_provider_consumer_contract_compatibility_regression_v0_1_2`
Date: `2026-07-29`
Status: `CLOSED_PASS_PROVIDER_CONSUMER_CONTROL_PLANE_COMPATIBLE_WITH_RESTRICTIONS_NO_CONSUMPTION`

## Summary

```text
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
accepted_provider_zip = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T141808Z.zip
accepted_provider_zip_sha256 = 191f40e40f2cfe374ce2f493fb9dd3e2509e33f64b9ed8f3969c9c8b0badf759

case_count = 18
failed_cases = 0
restricted_cases = 2

consumer_contract_status = DRAFT_NOT_INTEGRATION_VALIDATED
provider_consumer_control_plane = COMPATIBLE_WITH_RESTRICTIONS
StateBundle physical consumption = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption = false
production = false
downstream = false
```

## Result

The accepted provider v0.1.2 contracts remain compatible with the backtest consumer draft at the control-plane boundary:

```text
BacktestRunSpec
-> StateResolutionRequest v0.1.2
-> RuntimeInvocationResponse v0.1.2
-> StateBundleManifest v0.1.2 reference
```

This does not mean the backtester can consume rows. The current provider still returns references only, with `official_dataset = false`, `production = false`, `downstream = false` and no physical row delivery.

## Restrictions Preserved

```text
runtime_requests_executed = 0
runtime_resolutions_executed = 0
runtime_builds_executed = 0
physical_file_reads = 0
state_bundle_rows_delivered = 0
state_replay_feed_events = 0
backtest_runs_started = 0
datasets_written = 0
registry_mutations = 0
```

## Consumer Notes

The backtester contracts remain:

```text
BACKTEST_CONSUMER_CONTRACTS = DRAFT_NOT_INTEGRATION_VALIDATED
BACKTEST_STATE_CONSUMPTION = NOT_AUTHORIZED
STATE_REPLAY_FEED = NOT_AUTHORIZED
```

The current consumer draft still carries conditional references to `market_state_request` and `event_state_request`. Those provider files are auxiliary v0.1.1 documentation, while the executable v0.1.2 authority is `StateResolutionRequest`. Before removing `DRAFT`, the consumer should align that reference model explicitly.

## Next Gate

```text
state_bundle_manifest_physical_evidence_alignment_v0_1
```
