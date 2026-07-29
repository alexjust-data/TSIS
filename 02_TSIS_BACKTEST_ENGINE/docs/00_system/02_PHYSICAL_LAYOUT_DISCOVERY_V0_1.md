# Physical Layout Discovery V0.1

Status: `PHYSICAL_LAYOUT_DISCOVERED_AND_FIXTURE_CANDIDATE_SELECTED`
Date: 2026-07-28

This document records the physical evidence needed before implementing `RealDataInspector`.
It does not execute real-data preflight and does not promote any dataset.

## Dataset

```text
dataset_id = ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
dataset_version = v0_2_candidate
promotion_state = candidate_not_promoted
root = C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
file_format = parquet
partitioning = year=YYYY/ticker=SYMBOL/month=MM/part-000.parquet
validation_manifest = C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\final_manifest_validation.json
validation_manifest_sha256 = 7baf90cc64d382b66cf4bde6e434f1ec6a0656e51bec5d45945f36e4b7787ddf
merge_manifest = C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_build_runs\qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z\final_manifest_merge.json
merge_manifest_sha256 = a4f203d1bfb43817fc80b5f84069189629a487a849268486b57275b58b40d282
```

Observed sample file:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\year=2026\ticker=ABAT\month=01\part-000.parquet
```

Observed columns:

```text
ticker, ts_utc, date, year, month, o, h, l, c, v, vw, n, t, o_raw, h_raw, l_raw, c_raw, quote_guarded_repair_applied, quote_guarded_view, repair_lookup_state, repair_state, repair_reason, source_quote_guarded_repair_manifest, vw_quote_guarded_status, quote_bid_floor, quote_ask_cap, quote_mid_p50, quote_count, source_quotes_path, dataset_id, build_run_id, created_utc, source_raw_path
```


Minimum columns for the first `RealDataInspector`:

```text
ticker, ts_utc, date, year, month, o, h, l, c, v, t,
o_raw, h_raw, l_raw, c_raw, quote_guarded_repair_applied,
quote_guarded_view, repair_lookup_state,
source_quote_guarded_repair_manifest, dataset_id, build_run_id,
created_utc, source_raw_path
```

Optional columns observed in the selected fixture files:

```text
n, vw, vw_quote_guarded_status, quote_bid_floor, quote_ask_cap,
quote_mid_p50, quote_count, source_quotes_path, repair_state, repair_reason
```

Vendor-derived field policy:

```text
vw = PRESENT_BUT_NON_CONSUMABLE_VENDOR_DERIVED_FIELD
RealDataInspector ignores vendor_vw; absence, nullity or value cannot fail DATA preflight.
TSIS_VWAP may exist later only if built internally with a formal PIT-safe method.
```

Expected row lineage inside the selected fixture files:

```text
allowed_row_dataset_ids = ohlcv_1m_quote_guarded_full_universe_v0_1
expected_row_build_run_ids = qg_1m_full_2025_2026_v0_1_20260707T095701Z
```

Implementation note: the five selected fixture files have the 33-column schema above, but a non-fixture sample `AAA` file was observed with 27 columns. The inspector should validate the minimum contract columns and record optional columns, not assume full-tree optional-column uniformity.

Timestamp interpretation for the engine:

```text
ts_start = ts_utc
ts_end = ts_start + 1 minute
available_at = ts_end
source epoch column = t, observed as milliseconds matching ts_utc
physical timezone = UTC/Z
```

For the selected session `2026-01-05`, regular market hours are treated as:

```text
14:30:00Z <= ts_utc < 21:00:00Z
```

## Universe

```text
universe_id = lt1b_universe_v0_1
universe_run_id = 20260320_market_cap_last_observed_cutoff
physical_path = C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet
sha256 = 7b7d056785aae7e3e097219dc5f24c25e2fe193eb28c139354c4d9f8aff88468
filter_policy = ticker_plus_pti_window
limitation = operational <1B cut, not daily fully point-in-time market-cap membership
```

Selected members:

| Ticker | Class | First Seen | Last Observed | Session Inside PTI | Market Cap |
| --- | --- | --- | --- | ---: | ---: |
| ABAT | active_lt_1b_last_classifiable | 2023-09-21 | 2026-03-09 | True | 253812257.70 |
| ABEO | active_lt_1b_last_classifiable | 2016-10-25 | 2026-03-09 | True | 256698537.47 |
| ABSI | active_lt_1b_last_classifiable | 2021-07-22 | 2026-03-09 | True | 248691509.19 |
| ABTC | active_lt_1b_last_classifiable | 2025-09-03 | 2026-03-09 | True | 296463836.12 |
| ACB | active_lt_1b_last_classifiable | 2018-10-23 | 2026-03-09 | True | 284793651.20 |

## Corporate Actions

```text
dataset_id = corporate_actions_table_v0_1
physical_path = G:\TSIS\data\data_foundation_outputs\corporate_actions_table\corporate_actions_table_v0_1.parquet
table_sha256 = 01989eb301a2cdd83e297fbf6384e0bd4d5b4fb300bdccee6b1adbde87d5e4ce
manifest_path = G:\TSIS\data\data_foundation_outputs\corporate_actions_table\_corporate_actions_table_manifest_v0_1.json
manifest_sha256 = 2c37d8d75d531458f33941ee902d637fff0d71e2391cf0fff567980df92cfcf2
exact_action_rows_on_2026_01_05 = 0
nearby_action_rows_2025_12_29_to_2026_01_12 = 0
```

Note: registry contracts still mention `E:/TSIS/data`; the active mounted physical data root observed for this artifact is `G:/TSIS/data`.

## Fixture Candidate

```text
fixture_id = TSIS_REAL_DATA_FIXTURE_2026_01_05_LT1B_QG5_V0_1
fixture_kind = TSIS_REAL_DATA_FIXTURE
session_date = 2026-01-05
calendar_id = XNYS
session_policy = REGULAR_ONLY
timezone = America/New_York
symbols = ABAT, ABEO, ABSI, ABTC, ACB
signal.price_view = quote_guarded_1m
signal.allowed_use = allowed_controlled
execution.price_view = quote_guarded_1m
execution.allowed_use = proxy_allowed_for_engine_mechanics_only
execution.execution_semantics_state = pending_execution_semantics_review
valuation.price_view = quote_guarded_1m
valuation.allowed_use = allowed_controlled
```

Per ticker-day evidence:

| Ticker | Session Rows | Missing Regular Minutes | Has 14:30 | Has 20:59 | Duplicate Timestamps | Invalid Core Rows | Repair Rows | File SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| ABAT | 390 | 0 | True | True | 0 | 0 | 0 | `a3deef58908d17cefe4a4d91531309f248fde1c44681868535c94c93045f7b01` |
| ABEO | 338 | 52 | True | True | 0 | 0 | 0 | `13631ba7e613fda4daae499a9917969270af61848a5203776905b777d7909dea` |
| ABSI | 384 | 6 | True | True | 0 | 0 | 0 | `68f97c6dbf27ed6d0014f8921177689e8222b5f7d5af59dbb8d6f3ded811f41c` |
| ABTC | 390 | 0 | True | True | 0 | 0 | 0 | `e2714ffa0cb8df363c85862732f0af8887c846c4ae2e366d3e61913d500bfe36` |
| ACB | 326 | 64 | True | True | 0 | 0 | 0 | `1d0280a2921811174b4a5cb009168d90b5ce366db54d20439561db2e03049708` |

Why this fixture is useful:

- all symbols are inside `lt1b_universe_v0_1` and inside their PTI windows;
- all symbols have open/close proxy bars for the mechanical smoke test;
- `ABAT` and `ABTC` have complete 390-minute regular sessions;
- `ABEO`, `ABSI` and `ACB` contain interior gaps, useful for no-imputation inspection;
- no exact or nearby corporate actions were observed for these symbols in the checked window.

## Next Gate

```text
REAL_DATA_INSPECTOR_IMPLEMENTED
```

The inspector should consume this JSON companion:

```text
C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE\docs\00_system\02_PHYSICAL_LAYOUT_DISCOVERY_V0_1.json
```
