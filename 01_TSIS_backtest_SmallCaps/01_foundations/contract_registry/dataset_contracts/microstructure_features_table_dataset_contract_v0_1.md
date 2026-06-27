# Microstructure Features Table Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: microstructure_features_table_v0_1
family: data_foundation_outputs
class: event-window microstructure feature table
grain: event_window_id + ticker + window_start_utc + window_end_utc
materialization_scope: seed_event_window_smoke
full_universe_claim: false
```

## 2. Purpose

`microstructure_features_table` gives TSIS a governed place to store compact
quote/trade microstructure features for explicit event windows.

It answers:

```text
For this ticker and event window, what quote-book and trade-tape texture was
observed, and what source/gate lineage applies?
```

It does not answer:

```text
What is the full raw quote book or trade tape?
```

and it does not certify that every possible event window has already been
materialized.

## 2.1 Agent Interpretation Rule

`microstructure_features_table_v0_1` is valid as a governed state-component
seed.

It is not a finished market-state store.

Required interpretation:

```text
v0.1 proves schema shape, lineage, hashing, feature definitions and tests.
v0.1 does not prove full event-window coverage.
v0.1 does not support primary ML/RL training.
v0.1 does not support core backtesting or execution simulation.
```

To "leave microstructure right" for TSIS, the next promoted version must be a
new version, not a silent reinterpretation of v0.1.

Target future state:

```text
microstructure_features_table_v0_2_or_later
-> official E-root quotes source or documented D/E parity
-> official trades source
-> governed event-window input table
-> declared coverage universe
-> declared event families
-> data quality inheritance
-> leakage-safe as-of semantics
-> validators and recomputation tests
-> examples for human inspectors
```

Until that exists, agents must treat v0.1 as `scoped_state_sample`.

## 2.2 Is This Sufficient To Model Microstructure?

For `v0_1`, no.

The current table is sufficient to demonstrate a compact event-window
microstructure feature shape. It is not sufficient to train or model
microstructure institutionally.

Reason:

```text
rows = 1
tickers = 1
windows = 1
materialization_scope = seed_event_window_smoke
full_universe_claim = false
```

It can support:

- feature-definition review;
- lineage review;
- smoke tests;
- forensic inspection of the seed window.

It cannot support:

- full-universe ML/RL training;
- robust liquidity stress modeling;
- execution simulation;
- broad event-window sweeps;
- LOB/tape model validation across regimes.

For a later version to be sufficient as a microstructure modeling input, TSIS
needs at minimum:

- many governed event windows;
- declared universe and event-family coverage;
- official quotes/trades roots or documented parity;
- as-of/event-window legal cutoffs;
- spread, locked/crossed, quote update, trade intensity and liquidity features;
- missingness/staleness markers;
- quality inheritance from quotes/trades audits;
- labels or outcomes that are separated from pre-event features;
- walk-forward or out-of-sample evaluation splits;
- visual/forensic examples for good/review/bad windows;
- recomputation tests from raw source files.

## 2.2.1 Scientific Basis For This Limitation

The limitation is not arbitrary.

DeepLOB shows that useful LOB modeling depends on preserving spatial and
temporal structure of order-book data, not on treating market data as a generic
flat table.

```text
Zhang, Zohren, Roberts (2018/2020)
DeepLOB: Deep Convolutional Neural Networks for Limit Order Books
https://arxiv.org/abs/1808.03668
```

LOBFrame shows that even strong LOB forecasting performance does not necessarily
translate into actionable trading signals, and that microstructural
characteristics affect model efficacy.

```text
Briola, Bartolucci, Aste (2024)
Deep Limit Order Book Forecasting
https://arxiv.org/abs/2403.09267
```

JAX-LOB shows that RL/execution research over LOBs requires scalable simulation
and realistic LOB mechanisms.

```text
Frey et al. (2023)
JAX-LOB: A GPU-Accelerated limit order book simulator to unlock large scale
reinforcement learning for trading
https://arxiv.org/abs/2308.13289
```

Therefore, a one-window seed can validate the computation path, but it cannot
scientifically validate microstructure modeling, execution RL, liquidity stress
models or cross-regime robustness.

## 2.3 Why Build v0.1 If It Cannot Train Models?

Because v0.1 is a vertical slice.

It proves that the system can go from:

```text
explicit event window
-> raw quotes/trades source files
-> source hashes
-> compact microstructure features
-> manifest
-> schema validation
-> consumption gates
-> test evidence
```

without pretending to solve coverage.

This is necessary because microstructure data is heavy, path-sensitive and easy
to misuse. A wrong full-universe build would be expensive and dangerous.

v0.1 exists to answer:

```text
Can TSIS compute the right kind of microstructure state component at all?
Can TSIS preserve lineage back to raw files?
Can TSIS prevent a seed sample from being consumed as institutional training data?
```

v0.1 does not exist to answer:

```text
Does this feature generalize?
Can we train a liquidity stress model?
Can RL learn execution from this table?
Can this represent all event windows?
```

## 2.4 Promotion Ladder To A Trainable Microstructure Component

The required future path is:

### Stage 0 - Raw Root Authority

Complete or document:

- official quotes root;
- D/E parity decision if legacy D-root is used for recovery;
- official trades root;
- raw file layout contract;
- source hash policy.

### Stage 1 - Seed Vertical Slice

Current status:

```text
microstructure_features_table_v0_1
state_component_type = scoped_state_sample
```

Purpose:

- prove schema;
- prove lineage;
- prove feature computation;
- prove tests;
- prevent misuse.

### Stage 2 - Governed Event-Window Input

Required:

- event-window input contract;
- event_window_id semantics;
- event family linkage;
- window_start/window_end rules;
- timezone/session rules;
- as-of cutoffs.

### Stage 3 - Multi-Window Pilot

Required:

- many tickers;
- many dates;
- multiple event families;
- good/review/bad examples;
- visual/forensic inspector packs;
- recomputation tests from raw.

Purpose:

- test feature stability;
- test missingness;
- test pathological windows;
- validate quality inheritance.

### Stage 4 - Coverage Declaration

Required:

- declared universe;
- declared period;
- declared event families;
- declared excluded families;
- declared missingness;
- declared data-quality states.

No consumer may infer coverage from folder size or row count.

### Stage 5 - Institutional Microstructure State Component

Required:

- new dataset version;
- schema contract;
- registry entry;
- consumption policy;
- validators;
- test evidence;
- manifest;
- changelog;
- Graphify queue entry;
- explicit gates for Event Engine, research, backtest, ML/RL and execution.

### Stage 6 - ML/RL Readiness

Only after Stage 5 can a consumer consider:

- liquidity stress modeling;
- order-flow/tape-state embeddings;
- execution-risk modeling;
- event-state enrichment for ML;
- offline RL state inputs.

Even then, ML/RL readiness also requires:

- labels/outcomes separated from pre-event features;
- temporal splits;
- leakage checks;
- OOS validation;
- regime splits;
- uncertainty/coverage reporting.

## 3. Current Source Lineage

Current v0.1 was intentionally materialized as a seed/smoke window.

The exact data sources are:

```text
seed input:
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/microstructure_features_seed_windows_v0_1.csv

quotes source used now:
D:/quotes

future official quotes root:
E:/TSIS/data/quotes

quotes staging root:
E:/TSIS/data/quotes_

trades source used now:
E:/TSIS/data/trades_ticks_prod_2005_2026

identity source:
E:/TSIS/data/data_foundation_outputs/instrument_master/instrument_master_v0_1.parquet

family gate source:
E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix/dataset_certification_matrix_v0_1.parquet
```

The current row uses:

```text
event_window_id: seed_zyxi_20251201_full_day
ticker: ZYXI
session_date: 2025-12-01
quotes file: D:/quotes/ZYXI/year=2025/month=12/day=01/quotes.parquet
trades file: E:/TSIS/data/trades_ticks_prod_2005_2026/ZYXI/year=2025/month=12/day=2025-12-01/market.parquet
```

Hashes are stored in the table and manifest:

```text
quotes sha256: 9b73b6bdd3d1e23e65f95b39926b36a4416e82aa9f00ae1fe62544b0e2099245
trades sha256: d23f0dda5a5f8c65c9785d50675e061cee987b5e509da6007698dc60425d0646
```

## 4. Provisional Quotes Root Rule

This v0.1 may use `D:/quotes` only because the quotes raw storage parity work is
not complete.

Required interpretation:

```text
quotes_root_state = provisional_d_legacy_recovery_root_pending_e_parity
```

Before any production/backtest promotion:

1. `D:/quotes` and the governed `E:/TSIS/data/quotes` landing must be audited
   for parity or a new official E-root must be declared.
2. this table must be rebuilt from the governed E-root;
3. hashes and metrics must be compared against this v0.1 seed where the same
   files exist;
4. changelog, registry and validators must be updated.

## 5. Current Materialization

```text
build_run_id: microstructure_features_table_v0_1_20260625T155732Z
rows: 1
tickers: 1
windows: 1
quotes rows: 13288
trades rows: 18182
quotes crossed ratio all rows: 0.015051
quotes spread bps median: 76.628352
trades odd-lot ratio pct: 53.492465
trades duplicate exact ratio pct: 1.066989
hard_fail_count: 0
execution_sim_candidate_rows: 0
backtest_core_microstructure_candidate_rows: 0
```

## 6. Allowed Consumers

Allowed with scope flags:

- event discovery;
- event-window research;
- feature engineering smoke tests;
- data lineage validation;
- forensic review.

Restricted:

- backtest extended;
- ML flagged experiments.

Restricted consumers must preserve:

- `materialization_scope`;
- `full_universe_claim`;
- `quotes_root_state`;
- `source_quotes_file`;
- `source_trades_file`;
- source hashes.

## 7. Prohibited Consumers

Prohibited by default:

- `backtest_core`;
- execution simulator;
- live trading;
- ML/RL primary training;
- any consumer that needs full-universe microstructure coverage.

## 8. Change Policy

Version bump required when:

- the scope expands beyond the seed window;
- the quotes source moves from `D:/quotes` to an official E-root;
- the feature definitions change;
- row-level quality state semantics change;
- execution/backtest candidate flags change;
- source file layout changes;
- event-window input schema changes.
