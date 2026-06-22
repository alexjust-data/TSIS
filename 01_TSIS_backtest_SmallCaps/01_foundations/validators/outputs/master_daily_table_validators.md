# Master Daily Table Validators `v0_1`

## 1. Scope

Dataset:

```text
master_daily_table_v0_1
```

Root:

```text
E:/TSIS/data/data_foundation_outputs/master_daily_table
```

## 2. Governed Artifacts

- dataset contract: `01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md`
- schema: `01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md`
- registry: `01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml`
- policy: `01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md`
- materializer: `scripts/materialize_master_daily_table.py`

## 3. Unit Of Validation

```text
instrument_id + ticker + session_date + price_view
```

## 4. Minimum Validators

### 4.1 Artifact Presence

Must check:

- parquet dataset `master_daily_table_v0_1/`;
- `_master_daily_table_manifest_v0_1.json`;
- `_master_daily_table_summary_v0_1.csv`;
- all contract paths declared in manifest.

### 4.2 Schema Conformity

Must check:

- required columns exist;
- `schema_version = master_daily_table_v0_1`;
- `quality_policy_version = master_daily_table_policy_v0_1`;
- allowed `price_view` values only;
- one build id per materialization.

### 4.3 Grain Integrity

Hard failures:

- duplicate `ticker + session_date + price_view`;
- missing `ticker`, `instrument_id`, `session_date` or `price_view`;
- row count not equal to `expected_daily_rows * 3`;
- missing one of `daily_raw`, `split_normalized`, `adjusted`.

### 4.4 Price Integrity

Must report:

- selected OHLC null when `data_present = true`;
- non-positive selected OHLC;
- `high < low`;
- negative volume;
- missing expected data rows.

Price-integrity failures are row-level flags unless the structure itself is
broken. They must set `backtest_core_row_candidate = false`.

### 4.5 Source Reconciliation

Must check:

- expected daily denominator from `expected_data_calendar`;
- corporate action source SHA;
- dataset certification matrix source SHA;
- source daily and daily-adjusted file inventory;
- rows by price view.

### 4.6 Metric Integrity

Must check:

- `gap_pct` is null when prior close is unavailable or non-positive;
- `daily_return_pct` is null when prior close is unavailable or non-positive;
- `rvol_20d` is null when prior volume average is unavailable or zero;
- `dollar_volume = close * volume` where both are present.

## 5. Output Fields

A validator must emit:

- run id;
- dataset id;
- rows checked;
- rows by price view;
- present and missing rows;
- duplicate key groups;
- price-integrity issue counts;
- backtest candidate rows;
- source build ids;
- output tree hash;
- hard fail count;
- evidence artifacts path.

## 6. Final Rule

Passing this validator proves the master daily table is structurally coherent,
price-view-aware and source-linked.

It does not prove quote/trade quality, execution realism, or that non-v0.1
context families have been joined.
