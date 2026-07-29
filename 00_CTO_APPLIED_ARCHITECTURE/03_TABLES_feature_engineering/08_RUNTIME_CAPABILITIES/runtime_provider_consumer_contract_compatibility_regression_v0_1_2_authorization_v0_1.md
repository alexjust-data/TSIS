# Runtime Provider-Consumer Contract Compatibility Regression v0.1.2 Authorization

Gate: `runtime_provider_consumer_contract_compatibility_regression_v0_1_2`
Date: `2026-07-29`
Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

Open one small control-plane regression against the externally accepted provider v0.1.2 contracts.

This gate checks whether the backtest consumer draft can still interpret the provider exchange contracts after hardening v0.1.2. It does not open physical StateBundle consumption.

## Authority

```text
ACTIVE_PROVIDER_AUTHORITY = runtime_provider_contract_schema_hardening_v0_1_2
accepted_provider_zip = 00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/runtime_provider_contract_schema_hardening_v0_1_2_provider_only_20260729T141808Z.zip
accepted_provider_zip_sha256 = 191f40e40f2cfe374ce2f493fb9dd3e2509e33f64b9ed8f3969c9c8b0badf759
```

## Inputs

```text
provider_contracts = 5 executable v0.1.2 contracts
specialized_payload_contracts = auxiliary v0.1.1 docs only
consumer_contracts = 2 backtest DRAFT contracts, read-only
```

## Restrictions

```text
02_TSIS_BACKTEST_ENGINE edits = forbidden
StateBundle physical reads = 0
StateBundle rows delivered = 0
StateReplayFeed events = 0
backtest runs = 0
runtime builds = 0
datasets written = 0
registry mutations = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

## Authorized Outputs

```text
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/configs/runtime_provider_consumer_contract_compatibility_regression_v0_1_2_scope_v0_1.json
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_provider_consumer_contract_compatibility_regression_v0_1_2_matrix_v0_1.json
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/08_RUNTIME_CAPABILITIES/runtime_provider_consumer_contract_compatibility_regression_v0_1_2_readout_v0_1.md
```

The accepted provider-only ZIP must remain unchanged.
