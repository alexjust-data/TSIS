# Daily Adjusted Validators `v0_1`

## 1. Scope

Dataset:

```text
ohlcv_daily_adjusted
```

Canonical dataset contract:

```text
01_foundations/contract_registry/dataset_contracts/daily_adjusted_dataset_contract_v0_1.md
```

Canonical schema:

```text
01_foundations/canonical_schemas/daily/daily_adjusted_schema_contract.md
```

Consumption policy:

```text
01_foundations/data_consumption_policies/daily_adjusted_consumption_policy.md
```

Registry:

```text
01_foundations/dataset_registry/daily/daily_adjusted_registry_entry.yaml
```

Inspection evidence:

```text
01_foundations/inspection_dossiers/daily_adjusted/
01_foundations/data_quality_report/families/daily_adjusted_quality_report_v0_1.md
```

## 2. Unit Of Validation

Primary unit:

```text
ticker + date + adjusted daily bar
```

File-level unit:

```text
ticker-year adjusted parquet file
```

## 3. Required Inputs

Validators must be able to inspect:

- `E:/TSIS/data/ohlcv_daily_adjusted/`
- raw daily lineage when referenced;
- split/dividend/corporate-action lineage when referenced;
- full-universe materialization audit assets;
- visual inspector pack and quality report.

## 4. Required Columns

Minimum adjusted output columns:

- `ticker`
- `date`
- `year`
- raw OHLCV fields preserved from source where available;
- `future_split_factor`
- `future_dividend_factor`
- `future_adjustment_factor`
- `o_split_normalized`
- `h_split_normalized`
- `l_split_normalized`
- `c_split_normalized`
- `o_adjusted`
- `h_adjusted`
- `l_adjusted`
- `c_adjusted`

## 5. Hard Failures

Hard failures:

- unreadable parquet file;
- missing required adjusted columns;
- duplicate `ticker + date`;
- missing `ticker` or `date`;
- non-positive raw OHLC where raw bar is present;
- `high < low` in raw, split-normalized or adjusted views;
- non-positive split or adjustment factor;
- adjusted OHLC value missing when a valid raw bar and factor exist;
- source lineage missing for a materialized adjusted file;
- materialized adjusted ticker-year file missing when the full-universe audit declares it expected.

## 6. Review / Conditional States

Review states:

- complex corporate-action tail;
- ticker change boundary requiring identity review;
- dividend-only adjustment case where raw vs adjusted interpretation affects return labels;
- source reference gap that does not invalidate the adjusted row but limits audit confidence;
- extra output file not matched to active raw daily source.

## 7. Output Fields

A validator should emit at minimum:

- `run_id`;
- `dataset_id`;
- `source_root`;
- `rows_checked`;
- `files_checked`;
- `tickers_checked`;
- `missing_required_columns`;
- `duplicate_key_count`;
- `bad_factor_count`;
- `bad_ohlc_count`;
- `missing_expected_output_count`;
- `extra_output_count`;
- `review_count`;
- `hard_fail_count`;
- `evidence_paths`;
- `schema_version`;
- `contract_version`;
- `policy_version`.

## 8. Evidence Requirements

Passing validation requires:

- tabular audit evidence;
- visual inspector pack evidence;
- explicit line from raw daily to adjusted output where applicable;
- explicit treatment of complex split/dividend/ticker-change cases;
- documentation of any scoped limitation.

## 9. Pass Criteria

The dataset can be treated as validated for its declared scope only when:

- all hard failures are zero or documented as repaired in a later version;
- review cases are preserved with flags or evidence;
- output coverage matches the declared full-universe audit;
- consumption remains inside `daily_adjusted_consumption_policy.md`.

## 10. Non-Goals

This validator does not prove:

- intraday execution realism;
- quote/trade correctness;
- live price availability;
- alpha;
- that adjusted prices are suitable for microstructure.

## 11. Final Rule

`ohlcv_daily_adjusted` is an economic daily price view. It must never replace
raw daily bars for vendor reconciliation or intraday execution truth.
