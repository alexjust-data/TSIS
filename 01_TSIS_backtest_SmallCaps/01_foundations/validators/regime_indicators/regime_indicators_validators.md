# Regime Indicators Validators

## Scope

This validator contract governs:

```text
regime_indicators_v0_1
```

Physical root:

```text
E:/TSIS/data/regime_indicators
```

## Authorities

Read with:

- `contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md`
- `data_consumption_policies/regime_indicators_consumption_policy.md`
- `dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml`
- `canonical_schemas/regime_indicators/`
- `inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md`
- `data_quality_report/families/regime_indicators_quality_report_v0_1.md`

## Validation Units

| Subfamily | Validation unit |
| --- | --- |
| ETF minute bars | `ETF_SYMBOL + timestamp` |
| ETF daily bars | blocked `ETF_SYMBOL + date` |
| Index minute bars | `logical_symbol + timestamp` |
| Index daily bars | blocked `logical_symbol + date` |
| Metadata | root JSON file |

## Required Checks

### Root And Inventory

The validator must check:

- root exists;
- `etfs/` exists;
- `indices/` exists;
- `download_metadata.json` exists;
- `ticker_ranges.json` exists;
- expected symbols are explicit;
- file counts by extension are emitted.

### Minute Bars

Minute validation must check:

- file readability;
- required columns;
- timestamp parseability;
- timestamp range;
- duplicate timestamps;
- monotonicity;
- OHLC sanity;
- nonnegative volume where present;
- VWAP presence for ETFs where expected;
- missing file availability by symbol.

### Daily Bars

Daily validation must check:

- `date` parseability;
- `datetime` parseability;
- `date` uniqueness;
- realistic date range;
- `symbol + date` uniqueness;
- OHLC sanity.

Current blocking condition:

```text
all observed daily files have date = 1970-01-01
```

This must produce a blocking validator status.

### Metadata

Metadata validation must check:

- JSON parseability;
- symbol keys;
- `start`, `end`, `detected_at` parseability in `ticker_ranges.json`;
- mismatch between metadata ranges and physical bar rows.

Metadata may support repair planning, but cannot certify repaired bars by itself.

## Current Observed Status

| Area | Status |
| --- | --- |
| ETF minute schema | coherent representative schema |
| Index minute schema | coherent representative schema |
| Metadata | coherent |
| ETF daily bars | blocked |
| Index daily bars | blocked |

Known daily defect:

- `date_min = 1970-01-01`;
- `date_max = 1970-01-01`;
- `date_unique = 1`;
- `datetime` clustered in 1970.

## Acceptance States

Allowed states:

- `blocked_daily_invalid_dates`;
- `minute_schema_readable_review`;
- `metadata_coverage_evidence`;
- `repair_required`;
- `promoted_after_repair`.

Current family state:

```text
blocked_daily_invalid_dates
```

## Forbidden Conclusions

The validator must not conclude:

- daily files are usable because they are readable;
- metadata date ranges repair daily bars automatically;
- ETF/index regime symbols are small-cap tradables;
- minute files are feature-ready without coverage and sanity audit;
- current daily bars can feed master daily tables.

## Output Contract

A compliant future validator must emit:

- inventory table;
- minute coverage table;
- daily date quality table;
- metadata consistency table;
- blocked daily issue table;
- repair candidate plan;
- final human readout.
