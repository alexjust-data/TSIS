# LOCAL_RULES - 02_TSIS_BACKTEST_ENGINE

This module owns future backtest engine implementation, not Data Foundation governance and not CTO architecture authority.

## Layer Boundary

```text
00_CTO/14_BACKTEST_ENGINE
= architecture, decisions, scope, construction phases, authorizations, reviews and reference designs

02_TSIS_BACKTEST_ENGINE
= source code, configs, tests, executable experiments, notebooks, schemas, runtime manifests, ledgers, metrics and reports
```

Rule:

```text
00_CTO defines what must exist and why.
02_TSIS_BACKTEST_ENGINE implements and executes.
```

Do not duplicate architecture/governance documents from `00_CTO/14_BACKTEST_ENGINE` into this module. If a design decision must govern implementation, reference the CTO decision and create a local executable contract/config only when needed.

## Data Plane Boundary

The current physical data provider root for backtest-engine work is:

```text
G:/TSIS/data
```

This module must:

- consume certified or explicitly restricted Data Foundation outputs;
- resolve physical data through authorized manifests and contracts;
- never bypass `01_TSIS_DATA_FOUNDATION/01_foundations` contracts;
- never treat `G:/TSIS/data` as semantic authority by itself;
- never assume raw 1m bars are corrected in place;
- declare price view, corporate-action semantics and fill model in every run;
- preserve deterministic event ordering and run manifests;
- keep architecture/theory decisions in `00_CTO/14_BACKTEST_ENGINE` until promoted.

Do not store ambiguous raw market data under `02_TSIS_BACKTEST_ENGINE`.

Allowed data-adjacent local artifacts:

```text
dataset manifests
resolution manifests
run-local extracts
temporary caches
experiment-derived outputs
```

Each one must declare source dataset, logical version, physical source path, quality policy, price view, generated time and retention policy.

## Experiment Boundary

```text
02_TSIS_BACKTEST_ENGINE/experiments
= executable engine experiments

03_TSIS_Lab/04_experiments
= scientific governance of experiments
```

An engine experiment may execute only within a declared scope and must link back to its Lab experiment, authorization, or explicit engineering preflight when applicable.

## Scaffold Policy

The current scaffold is intentionally minimal. Do not materialize the larger future target tree until a concrete implementation task or promoted construction phase requires it.

Future additions such as `orders`, `engines/vectorized`, `engines/event_driven`, `configs/portfolios`, `configs/validation`, richer docs, richer tests and `scripts/` are allowed, but only with a clear reason and changelog entry.
