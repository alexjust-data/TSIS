# Master Intraday Bar Table Consumption Policy `v0_1`

## Scope

This policy governs:

```text
master_intraday_bar_table_v0_1
```

Physical root:

```text
E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table
```

## Institutional Position

`master_intraday_bar_table_v0_1` is a scoped CAPA 1 output table. It is useful
for split-normalized intraday event-case research, but it is not a full-universe
1m feed.

It is also not evidence that `E:/TSIS/data/ohlcv_1m_split_normalized` contains
all normalized 1m data. That source folder is a validated proof/pilot of the
split-normalization method. It demonstrates that the normalization code and
semantics work on inspected split cases.

The required interpretation is:

```text
materialization_scope = scoped_split_normalized_event_cases
full_universe_claim = false
backtest_core_bar_candidate = false
```

## Required Consumer Filters

Every consumer must filter or preserve:

- `price_view`
- `materialization_scope`
- `full_universe_claim`
- `raw_quality_manifest_present`
- `raw_allowed_consumption`
- `vwap_consumption_state`
- `event_research_bar_candidate`
- `backtest_core_bar_candidate`
- `family_production_use_gate`
- `family_event_consumption_gate`

## Price-View Rules

`1m_raw` may be used for scoped raw-scale intraday inspection only.

`1m_split_normalized` may be used for scoped split-sensitive comparisons and
event-window research.

Consumers must not compare `1m_raw` and `1m_split_normalized` without declaring
which price view drives the feature, label or diagnostic.

## VWAP Rule

Direct use of `vwap` is permitted only when:

```text
vwap_consumption_state = allowed_with_declared_vw_policy
```

Rows with:

```text
vwap_consumption_state = blocked_by_raw_vw_quality
```

may still be used for OHLCV research that excludes VWAP, if the consumer
preserves `raw_allowed_consumption` and declares the exclusion.

## Allowed Uses

Allowed:

- scoped event-window drilldowns;
- split-normalized 1m validation;
- proof that the split-normalization pipeline can be applied correctly to
  selected ticker-months;
- visual audit reproduction;
- event-engine dry runs that preserve scoped flags;
- controlled research where the limited ticker-month universe is explicit.

## Restricted Uses

Restricted:

- broad backtest experiments;
- ML feature generation;
- outcome research that mixes full-universe and scoped surfaces.

Restricted consumers must document why the scoped surface is sufficient.

## Prohibited Uses

Prohibited by default:

- `backtest_core`;
- unflagged production backtesting;
- unflagged ML/RL training;
- execution simulation;
- live feed replacement;
- evidence that the full raw 1m universe is clean.
- evidence that all raw 1m ticker-months have already been split-normalized.

## Future Operational Use

When a strategy, event family or backtest case needs split-safe 1m data, the
consumer must not assume this table already contains the needed ticker-months.

The correct workflow is:

1. select the required ticker-months or event windows;
2. execute the audited split-normalization pipeline for those inputs;
3. emit a new scoped or promoted output with manifest, tests and registry entry;
4. declare whether the resulting scope is pilot, event-window, partial universe
   or full-universe.

## Quote-Guarded Candidate Rule

Planned candidate:

```text
master_intraday_bar_table_v0_2_candidate_quote_guarded
```

This candidate route exists only as a contract/config until the
`ohlcv_1m_quote_guarded` repair workstream finishes and promotes validated
artifacts under:

```text
E:/TSIS/data/data_foundation_outputs/ohlcv_1m_quote_guarded/
```

Until then, consumers must treat the route as:

```text
candidate_contract_defined_not_materialized
full_universe_claim=false
not_backtest_core
not_ml_primary
not_rl_allowed
not_execution_truth
```

If a downstream experiment uses bridge artifacts from:

```text
C:/TSIS_Data/01_TSIS_backtest_SmallCaps/runs/data_foundation/ohlcv_1m_quote_guarded/
```

it must label them as run artifacts, not governed output tables. The current
`D:/quotes` lineage is provisional candidate lineage only and must not be
presented as the final official E-root source.

## Required Citations

Any notebook, module or downstream table derived from this output must cite:

- `01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md`
- `01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md`
- `01_foundations/data_consumption_policies/master_intraday_bar_table_consumption_policy.md`
- `01_foundations/validators/outputs/master_intraday_bar_table_validators.md`
- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md`
- `01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md` when using the quote-guarded candidate route

## Final Rule

This table can help explain an intraday split-event case.

It cannot certify the full 1m universe, replace raw 1m, or authorize core
backtesting by itself.
