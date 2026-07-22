# `ohlcv_1m_raw` Validators v0.1

## Scope

Validators for `ohlcv_1m_raw_v0_1`.

These checks define the minimum evidence required before `ohlcv_1m_raw` bars can be consumed under the dataset contract and consumption policy.

## Schema Validators

Required checks:

- file can be read with a schema-aware parquet reader;
- required fields from `canonical_schemas/ohlcv_1m/ohlcv_1m_schema_contract.md` are present;
- `ticker` identity matches the partition or file-level ticker evidence;
- `timestamp` is parseable as a minute timestamp;
- numeric fields have numeric physical types or lossless coercion rules;
- partition metadata is consistent with `ticker`, `year`, and `month` where present.

Known structural issue:

- schema merge conflicts around ticker encoding are part of the `RESCUE_SCHEMA_ONLY` family and must be handled explicitly.

## Value Validators

Required checks:

- `open`, `high`, `low`, `close` are positive when present;
- `high >= max(open, close, low)`;
- `low <= min(open, close, high)`;
- `volume >= 0`;
- `transactions >= 0` where present;
- duplicate ticker-minute rows are detected and classified;
- null rates are reported per field.

## VW Validators

The `vw` field requires dedicated classification.

Minimum families:

- `vw_mild_low_ratio`
- `vw_moderate_ratio`
- `vw_severe_tiny_base`
- `vw_severe_small_mass`
- `vw_severe_large_mass_diffuse`
- `vw_severe_large_mass_persistent`

The validator output must preserve enough information for a consumer to decide whether `vw` is excluded, repaired, or used only under a declared sensitivity policy.

## Universe Validators

Any `<1B>` assertion must validate:

- ticker membership in `lt1b_universe_v0_1`;
- intersection with `first_seen_date`;
- intersection with `last_observed_date`;
- count reconciliation against the active closeout evidence.

Ticker membership alone is insufficient.

## Quality-State Assignment

The validator must emit one of:

- `good`
- `review`
- `bad`

Consumption semantics:

- `good`: eligible under the raw consumption policy.
- `review`: flagged exploratory or diagnostic only.
- `bad`: forensic only.

The assignment must be reproducible from the documented schema, value, VW, and universe checks.

## Evidence Requirements

Validator outputs must be stored or cited with:

- execution timestamp;
- source root;
- universe reference;
- total files or task keys inspected;
- ticker count;
- row count;
- quality-state counts and percentages;
- `vw` family counts and percentages;
- list of hard failures.

Current institutional evidence:

- `01_foundations/inspection_dossiers/minute/raw_1m_lt1b_closeout_recalculation_v0_1.md`
- `01_foundations/inspection_dossiers/minute/raw_1m_schema_only_lt1b_inspection_readout_v0_1.md`
- `01_foundations/module_contracts/ohlcv_1m_historical_closeout_lt1b_reconciliation_v0_1.md`

## Promotion Rule

`ohlcv_1m_raw_v0_1` may not be promoted beyond `institutional_raw_closeout_reconciled_lt1b` unless a later validator run shows materially improved quality or an explicit downstream policy narrows the consumption scope.

The raw layer must remain distinct from `ohlcv_1m_split_normalized_v0_1`.
