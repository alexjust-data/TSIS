# `ohlcv_1m_raw` Consumption Policy v0.1

## Scope

This policy governs consumption of `ohlcv_1m_raw_v0_1`.

It applies to raw one-minute OHLCV bars before split normalization. It does not govern `ohlcv_1m_split_normalized_v0_1`, which has its own dataset contract and promotion path.

## Institutional Position

`ohlcv_1m_raw_v0_1` is an understood and documented raw foundation layer. It is not a globally clean production layer.

The correct reading is:

- raw coverage has been reconciled against the modern `<1B>` universe;
- the dominant quality debt is known and quantified;
- consumers may use the layer only with the documented quality-state filters;
- split-sensitive consumers must use the split-normalized layer instead.

## Required Filters

Any `<1B>` use must apply:

- membership in `lt1b_universe_v0_1`;
- PTI-window intersection using `first_seen_date` and `last_observed_date`;
- `ohlcv_1m_raw` quality state from the closeout evidence;
- explicit inclusion/exclusion declaration for `good`, `review`, and `bad`.

## Quality-State Consumption

### `good`

Permitted for:

- raw minute-bar diagnostics;
- controlled intraday research;
- construction checks for `ohlcv_1m_split_normalized` layers;
- baseline raw-bar sanity checks.

The consumer must still declare that the price scale is raw observed, not split-normalized.

### `review`

Permitted only for:

- flagged exploratory research;
- sensitivity analysis;
- forensic comparison;
- candidate rescue analysis.

`review` rows must not silently enter a baseline backtest, a production ML dataset, or a production factor table.

### `bad`

Permitted only for:

- forensic analysis;
- root-cause investigation;
- exclusion manifests;
- validator development.

`bad` rows are disallowed for production research, baseline backtests, target generation, and ML training.

## Field-Level Rules

`open`, `high`, `low`, `close`, `volume`, and `transactions` may be consumed only after schema and value checks pass.

`vw` requires additional severity handling. The known families include:

- `vw_mild_low_ratio`
- `vw_moderate_ratio`
- `vw_severe_tiny_base`
- `vw_severe_small_mass`
- `vw_severe_large_mass_diffuse`
- `vw_severe_large_mass_persistent`

Any consumer that uses `vw` directly must report which families are included or excluded. Any consumer that does not use `vw` must still preserve the file-level quality state produced by the closeout.

## Prohibited Uses

The raw layer must not be used as:

- a split-adjusted cross-session feature source;
- an unflagged production backtest feed;
- an unflagged ML training matrix;
- a substitute for quote/trade execution evidence;
- evidence that the full `<1B>` minute universe is production-clean.

## Required Citations

Any notebook, module, or dataset derived from `ohlcv_1m_raw` must cite:

- `01_foundations/contract_registry/dataset_contracts/ohlcv_1m_raw_dataset_contract_v0_1.md`
- `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_raw_registry_entry.yaml`
- `01_foundations/validators/ohlcv_1m/ohlcv_1m_raw_validators.md`
- `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`

For split-sensitive work, the consumer must additionally cite the `ohlcv_1m_split_normalized` contract.
