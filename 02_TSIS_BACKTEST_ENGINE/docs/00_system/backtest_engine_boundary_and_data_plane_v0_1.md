# Backtest Engine Boundary and Data Plane Decision v0.1

Status: `module_decision_record`
Date: 2026-07-23
Owner module: `02_TSIS_BACKTEST_ENGINE`

## Decision

`00_CTO/14_BACKTEST_ENGINE` and `02_TSIS_BACKTEST_ENGINE` must not contain the same kind of material.

The boundary is:

```text
00_CTO defines what must exist and why.
02_TSIS_BACKTEST_ENGINE implements and executes.
```

## Layer Roles

```text
00_CTO/14_BACKTEST_ENGINE
= architecture, decisions and governance
```

Allowed material:

```text
system maps
architecture decisions
scope
component boundaries
construction phases
authorizations
reviews
reference designs
```

```text
02_TSIS_BACKTEST_ENGINE
= executable technical product
```

Allowed material:

```text
source code
configs
tests
experiments
notebooks
outputs
schemas
runtime manifests
```

## Data Plane

The current physical data provider root for backtest-engine work is:

```text
G:/TSIS/data
```

This physical root does not own dataset semantics. The engine must consume data through Data Foundation contracts and authorized physical roots.

```text
01_TSIS_DATA_FOUNDATION
= logical and semantic data authority

G:/TSIS/data
= current physical data plane for source payloads and heavy materializations

02_TSIS_BACKTEST_ENGINE
= consumer, resolver, simulator and accounting layer
```

Inside `02_TSIS_BACKTEST_ENGINE`, do not copy ambiguous raw market data. Only these data-adjacent artifacts are allowed:

```text
dataset manifests
resolution manifests
run-local extracts
temporary caches
outputs derived from an experiment
```

Any `run-local extract` or cache must declare source dataset, logical version, physical source path, quality policy, price view, generated time, and retention policy.

## Lab Boundary

`02_TSIS_BACKTEST_ENGINE/experiments` and `03_TSIS_Lab/04_experiments` also have separate roles.

```text
02_TSIS_BACKTEST_ENGINE/experiments
= executable engine experiments
```

They contain technical execution material:

```text
configuration
strategy binding
universe binding
run references
ledgers
technical metrics
runtime manifests
```

```text
03_TSIS_Lab/04_experiments
= scientific governance of experiments
```

They contain scientific material:

```text
research question
hypothesis
authorization
exploratory/confirmatory classification
evidence
scientific decision
conclusions
```

Relationship:

```text
TSIS Lab experiment
        -> authorizes
Backtest Engine experiment
        -> executes
TSIS Lab
        -> interprets and validates
Knowledge Layer
        -> preserves the conclusion
```

## Current Physical Scaffold Policy

The scaffold already created is intentionally minimal. Do not materialize the larger future tree until a concrete need exists.

Current physical scope:

```text
configs/datasets
configs/universes
configs/strategies
configs/execution
configs/experiments
docs/00_system
src/tsis_backtest/common
src/tsis_backtest/dataset_resolution
src/tsis_backtest/temporal
src/tsis_backtest/universe
src/tsis_backtest/loaders
src/tsis_backtest/strategies/open_to_close
src/tsis_backtest/execution
src/tsis_backtest/portfolio
src/tsis_backtest/engines/tabular
src/tsis_backtest/metrics
src/tsis_backtest/validation
src/tsis_backtest/experiments
src/tsis_backtest/reports
notebooks/00_data_inspection
notebooks/01_universe_research
notebooks/02_single_day_backtest
notebooks/03_validation
experiments/EXP_0001_INPLAY_OPEN_TO_CLOSE
outputs/EXP_0001_INPLAY_OPEN_TO_CLOSE
tests/unit
tests/integration
tests/hand_calculated_cases
```

Future folders such as `orders`, `engines/vectorized`, `engines/event_driven`, `configs/portfolios`, `configs/validation`, richer docs, richer tests and `scripts/` are allowed only when a promoted construction phase or concrete implementation task requires them.

## Verdict

```text
Place the engine inside C:/TSIS_Data
= correct

Create 02_TSIS_BACKTEST_ENGINE
= correct

Preserve 00_CTO/14_BACKTEST_ENGINE
= correct

Use both for the same material
= incorrect
```

Final architecture:

```text
00_CTO
= defines

01_TSIS_DATA_FOUNDATION
= provides governed data semantics

G:/TSIS/data
= provides the current physical data plane

02_TSIS_BACKTEST_ENGINE
= executes and accounts

03_TSIS_Lab
= governs, validates and interprets

Knowledge Layer
= preserves conclusions
```
