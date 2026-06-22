# Ohlcv 1m Split Normalized Validators `v0_1`

## 1. Scope

Dataset:

```text
ohlcv_1m_split_normalized
```

Canonical dataset contract:

```text
01_foundations/contract_registry/dataset_contracts/ohlcv_1m_split_normalized_dataset_contract_v0_1.md
```

Canonical schema:

```text
01_foundations/canonical_schemas/ohlcv_1m/ohlcv_1m_split_normalized_schema_contract.md
```

Consumption policy:

```text
01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
```

Registry:

```text
01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml
```

Inspection evidence:

```text
01_foundations/inspection_dossiers/1m_split_normalized/
01_foundations/data_quality_report/families/ohlcv_1m_split_normalized_quality_report_v0_1.md
```

## 2. Unit Of Validation

Primary unit:

```text
ticker + minute timestamp + split-normalized bar
```

Materialization unit:

```text
ticker-month parquet file
```

Event audit unit:

```text
ticker + split event date + pre/post minute window
```

## 3. Required Inputs

Validators must inspect:

- `E:/TSIS/data/ohlcv_1m_split_normalized/`
- source raw 1m lineage when referenced;
- source split lineage when referenced;
- split-event audit assets;
- visual inspector pack and population readouts.

## 4. Required Columns

Minimum columns:

- `ticker`
- `ts_utc`
- `date`
- `year`
- `month`
- raw OHLCV fields preserved where available;
- `future_split_factor`
- `o_split_normalized`
- `h_split_normalized`
- `l_split_normalized`
- `c_split_normalized`
- `vw_split_normalized`
- `materialized_price_view`
- `source_1m_file`
- `source_splits_file`

## 5. Hard Failures

Hard failures:

- unreadable parquet file;
- missing required split-normalized columns;
- duplicate `ticker + ts_utc`;
- missing `ticker` or `ts_utc`;
- non-positive split factor;
- `high < low` in raw or split-normalized view;
- split-normalized value missing when raw price and factor exist;
- `materialized_price_view` not equal to the declared split-normalized view;
- missing source 1m lineage;
- missing source split lineage for an adjusted split event;
- event audit invariant failure around a split boundary.

## 6. Review / Conditional States

Review states:

- source raw 1m missing on one side of split event;
- no pre-window or no post-window coverage;
- scoped pilot materialization instead of full-universe replacement;
- ticker lifecycle boundary near split event;
- raw 1m `vw` debt inherited from upstream.

## 7. Output Fields

A validator should emit at minimum:

- `run_id`;
- `dataset_id`;
- `source_root`;
- `rows_checked`;
- `files_checked`;
- `tickers_checked`;
- `split_events_checked`;
- `pass_event_count`;
- `coverage_limited_event_count`;
- `duplicate_key_count`;
- `bad_factor_count`;
- `bad_ohlc_count`;
- `missing_source_lineage_count`;
- `hard_fail_count`;
- `review_count`;
- `evidence_paths`;
- `schema_version`;
- `contract_version`;
- `policy_version`.

## 8. Evidence Requirements

Passing validation requires:

- split-event casepack evidence;
- visual inspector pack evidence;
- source lineage to raw 1m and splits;
- explicit scope statement saying whether the materialization is full-universe
  or scoped/pilot;
- preservation of inherited raw 1m limitations.

## 9. Pass Criteria

The dataset can be used only inside the declared scope when:

- hard failures are zero for validated split events;
- review/coverage-limited events remain flagged;
- every consumer keeps the `split_normalized` price-view marker;
- no consumer treats this layer as raw observed intraday truth.

## 10. Non-Goals

This validator does not prove:

- global replacement of raw 1m unless a full-universe materialization explicitly exists;
- quote or trade tape quality;
- live execution quality;
- absence of raw upstream `vw` issues;
- alpha.

## 11. Final Rule

`ohlcv_1m_split_normalized` is a derived comparability view. It must remain
distinct from `ohlcv_1m_raw` in contracts, validators, consumers and tests.
