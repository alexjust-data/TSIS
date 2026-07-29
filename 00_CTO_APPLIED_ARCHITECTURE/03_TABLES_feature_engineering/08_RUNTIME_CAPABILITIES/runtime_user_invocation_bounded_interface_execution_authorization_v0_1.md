# Runtime User Invocation Bounded Interface Execution Authorization v0.1

Gate: `runtime_user_invocation_bounded_interface_execution_authorization_v0_1`
Date: `2026-07-28`
Status: `AUTHORIZED_WITH_RESTRICTIONS_NO_EXECUTION`

## Purpose

Authorize a bounded behavior test of the provider-side runtime invocation
interface.

This authorization is limited to control-plane behavior:

```text
validate request
normalize request
fingerprint request
resolve capability/effective policy
lookup candidate registry metadata
return governed reference or fail-closed decision
```

It does not authorize physical state row delivery, `StateReplayFeed`, backtest
execution, downstream consumption, production, new dataset materialization or
official dataset promotion.

## Authorized Cases

```text
1. Market State exact reuse hit -> governed reference only
2. Event State exact reuse hit -> governed reference only
3. halt_resumed Event State request -> blocked
4. new candidate request without execution authorization -> authorization_required
5. production/downstream request -> blocked
6. user supplied physical path -> blocked
7. partial candidate coverage -> unavailable contexts preserved
8. reuse hit -> zero build, zero source reads, zero registry mutations
```

## Boundaries

```text
interface_executions = 0
runtime_materializations = 0
physical_state_rows_delivered = 0
backtest_runs_started = 0
StateReplayFeed records emitted = 0
official_dataset = false
production = false
downstream = false
backtest_consumption = false
```

The next gate may execute the bounded interface test under this scope:

```text
runtime_user_invocation_bounded_interface_execution_v0_1
```
