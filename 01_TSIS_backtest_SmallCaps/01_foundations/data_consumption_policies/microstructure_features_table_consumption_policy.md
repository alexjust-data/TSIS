# Microstructure Features Table Consumption Policy `v0_1`

## Scope

This policy governs:

```text
microstructure_features_table_v0_1
```

Physical root:

```text
E:/TSIS/data/data_foundation_outputs/microstructure_features_table
```

## Institutional Position

`microstructure_features_table_v0_1` is a scoped seed materialization.

Required interpretation:

```text
materialization_scope = seed_event_window_smoke
full_universe_claim = false
execution_sim_candidate = false
backtest_core_microstructure_candidate = false
```

It is useful to prove the table shape, source lineage, feature definitions and
tests. It is not a production microstructure feature store.

## Target State Required To Make It Production-Useful

The desired TSIS target is not to discard this table.

The desired target is to promote a later version that turns the current seed
into a governed event-window microstructure state component.

Required future properties:

```text
scope: declared event-window coverage, not one seed case
quotes_root: governed E-root or documented D/E parity
trades_root: governed E-root
event_windows: produced by governed Event Discovery/Event Engine input
lineage: source files + hashes + manifests
quality: inherited from quotes/trades/data_quality_report gates
leakage: as-of/event-window legal
tests: recompute features from raw source files
inspection: visual/forensic examples for good/review/bad windows
consumers: explicit gates for research, backtest, ML/RL and execution
```

Until those properties exist, v0.1 remains:

```text
state_component_type = scoped_state_sample
```

It must not be promoted by changing language alone. It requires a new
materialization, contracts, validators and evidence.

## Source Rule

The current quotes source is:

```text
D:/quotes
```

This is provisional. The future official source must be a governed E-root after
raw storage parity is audited.

Every consumer must preserve:

- `quotes_root_used`;
- `quotes_root_state`;
- `future_official_quotes_root`;
- `quotes_staging_root`;
- `source_quotes_file`;
- `source_quotes_file_sha256`.

## Required Consumer Filters

Every consumer must filter or preserve:

- `materialization_scope`
- `full_universe_claim`
- `microstructure_quality_state`
- `event_research_microstructure_candidate`
- `execution_sim_candidate`
- `backtest_core_microstructure_candidate`
- `quotes_family_event_consumption_gate`
- `trades_family_event_consumption_gate`
- `source_quotes_file_present`
- `source_trades_file_present`

## Allowed Uses

Allowed:

- scoped event-window analysis;
- forensic microstructure inspection;
- feature-definition smoke tests;
- lineage checks during D/E raw parity work;
- notebooks that explicitly show the provisional scope.

## Restricted Uses

Restricted:

- broad event sweeps;
- ML feature experiments;
- backtest-extended prototypes.

Restriction condition:

```text
the consumer must state that v0.1 has one seed window and uses provisional
D:/quotes lineage.
```

## Prohibited Uses

Prohibited:

- core backtesting;
- execution simulation;
- live trading;
- full-universe ML/RL training;
- treating D-root metrics as final official metrics;
- using the table without source hash lineage.

## Promotion Requirement

Promotion beyond seed scope requires:

1. event-window input contract;
2. official E-root quotes source or documented parity;
3. source-file hashes;
4. manifest;
5. schema, registry, policy and validators update;
6. tests that recompute features from raw source files;
7. changelog and Graphify queue update.
