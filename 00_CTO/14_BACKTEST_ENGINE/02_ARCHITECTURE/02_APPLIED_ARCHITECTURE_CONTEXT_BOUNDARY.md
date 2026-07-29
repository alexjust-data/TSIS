# Applied Architecture context boundary

Status: `ACTIVE_BOUNDARY`

## Permitted context

The following files may be read to understand the role of
`00_CTO_APPLIED_ARCHITECTURE`:

```text
00_CTO_APPLIED_ARCHITECTURE/AGENTS.md
00_CTO_APPLIED_ARCHITECTURE/README.md
00_CTO_APPLIED_ARCHITECTURE/CHANGELOG.md
```

They are external architectural context. They do not replace the local
contracts or governance records of `02_TSIS_BACKTEST_ENGINE`.

## Future provider reference

This file may be read as a closed future reference:

```text
00_CTO_APPLIED_ARCHITECTURE/
03_TABLES_feature_engineering/
09_STATE_CONSUMPTION_BOUNDARY/README.md
```

The role separation recorded for future compatibility is:

```text
Provider
= validates, resolves, builds/reuses and references StateBundles

Consumption Boundary
= authorizes bounded physical opening

Consumer
= reads, types, orders and replays under its own contracts
```

## Binding status

```text
FUTURE_PROVIDER_REGISTRY_INTEGRATION = NOT_AUTHORIZED
StateReplayFeed = NOT_AUTHORIZED
backtest_strategy_execution = false
state_bundle_physical_read = BLOCKED
Market State consumption = NOT_AUTHORIZED
Event State consumption = NOT_AUTHORIZED
```

Provider progress cannot silently authorize consumer behavior. A later,
explicit provider-consumer compatibility and physical-consumption gate is
required.
