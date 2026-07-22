# Expected Data Calendar Dataset Contract `v0_1`

## 1. Dataset Identity

```text
dataset_id: expected_data_calendar_v0_1
family: data_foundation_outputs
class: certification/quality table
grain: dataset_family + ticker + session_date
```

## 2. Purpose

`expected_data_calendar` defines the expected coverage denominator for core
market-data families.

It answers:

```text
For this dataset family, ticker and XNYS session, should downstream quality
checks expect a data observation or file-level coverage evidence?
```

It does not answer whether data is present, clean, usable or complete.

## 3. Source Lineage

Authoritative inputs v0.1:

- `instrument_master_v0_1`
- `market_calendar_v0_1`

The table materializes the intersection of:

- operational `<1B>` instrument valid window;
- XNYS trading sessions;
- core dataset families included by v0.1 expectation policy.

## 4. Dataset Families v0.1

- `daily_raw`
- `ohlcv_1m_raw`
- `trades_raw`
- `quotes_raw`

These are expectation families, not proof of physical file presence.

## 5. Physical Layout

```text
E:/TSIS/data/data_foundation_outputs/expected_data_calendar/
  expected_data_calendar_v0_1/
  _expected_data_calendar_summary_v0_1.csv
  _expected_data_calendar_manifest_v0_1.json
```

The parquet dataset is partitioned by:

```text
dataset_family/year
```

## 6. Allowed Consumers

Permitted:

- `data_quality_report`
- `dataset_certification_matrix`
- `master_daily_table` coverage denominator
- `master_intraday_bar_table` coverage denominator
- `research_only`
- `forensic_only`

Restricted:

- `backtest_core`
- `ml_primary`
- `execution_simulator`
- `rl_allowed`

The table can support coverage gates, but is not itself tradable data.

## 7. Quality Policy

Good:

- one row per `dataset_family + ticker + session_date`;
- lineage fields point to the exact instrument/calendar source builds;
- all rows are within instrument valid windows;
- all rows are XNYS sessions.

Bad:

- duplicate expectation key;
- expectation outside valid window;
- missing core family;
- source manifests missing;
- schema_version mismatch.

Review:

- new family required;
- source table rematerialized;
- calendar range extended;
- universe policy changed.

## 8. Known Limitations

- v0.1 does not encode family-specific historical availability exceptions.
- v0.1 intentionally does not use physical file presence to suppress expected
  rows.
- v0.1 ends where `market_calendar_v0_1` ends.
- It must be paired with actual presence/quality validators.

## 9. Change Policy

Version bump required when:

- the grain changes;
- included dataset families change;
- the expectation policy changes;
- market calendar or instrument identity semantics change;
- output layout changes.

