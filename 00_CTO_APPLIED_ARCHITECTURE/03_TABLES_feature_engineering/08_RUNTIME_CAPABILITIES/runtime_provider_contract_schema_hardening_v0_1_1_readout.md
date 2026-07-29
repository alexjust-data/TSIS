# Runtime Provider Contract Schema Hardening v0.1.1 Readout

Gate: `runtime_provider_contract_schema_hardening_v0_1_1`
Date: `2026-07-28`
Status: `CLOSED_PROVIDER_CONTRACT_SCHEMA_HARDENED_V0_1_1_WITH_RESTRICTIONS_NO_EXECUTION`

```text
case_count = 31
failed_cases = 0
jsonschema_compile = PASS
ajv_strict_static_lint = PASS
ajv_runtime_available = false
ajv_strict_runtime_executed = false
runtime_requests_executed = 0
datasets_written = 0
builds_materializations = 0
registry_mutations = 0
StateReplayFeed = NOT_AUTHORIZED
backtest_consumption_authority = false
production = false
downstream = false
```

Payload authority decision:

```text
StateResolutionRequest = only executable payload schema authority
market_state_request_contract = normative auxiliary, not executable
event_state_request_contract = normative auxiliary, not executable
```

Do not reopen provider-consumer compatibility until this provider-only package passes external adversarial audit.
