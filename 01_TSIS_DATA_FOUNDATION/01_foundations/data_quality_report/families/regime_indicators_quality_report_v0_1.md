# Regime Indicators Quality Report v0.1

## 1. Scope And Role

Family:

```text
regime_indicators_v0_1
```

Physical root:

```text
E:/TSIS/data/regime_indicators
```

Role:

- broad-market/sector regime context;
- ETF and index proxy bars;
- not small-cap raw market authority;
- not alpha or production feature layer by default.

## 2. Final Status

```text
blocked_daily_scoped_minute_review
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

Daily bars are blocked. Minute bars remain review/scoped.

## 3. Artifact Map

| Artifact | Status | Path |
| --- | --- | --- |
| Dataset contract | present | `01_foundations/contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md` |
| Registry entry | present | `01_foundations/dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml` |
| Consumption policy | present | `01_foundations/data_consumption_policies/regime_indicators_consumption_policy.md` |
| Validators | present as contract | `01_foundations/validators/regime_indicators/regime_indicators_validators.md` |
| Inspection readout | present | `01_foundations/inspection_dossiers/regime_indicators/regime_indicators_inspection_readout_v0_1.md` |
| Schemas | present | `01_foundations/canonical_schemas/regime_indicators/` |
| Dossier evidence assets | present | `01_foundations/inspection_dossiers/regime_indicators/evidence_assets/` |
| Visual inspector pack | present | `01_foundations/inspection_dossiers/regime_indicators/visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md` |
| Good/scoped examples | present | `01_foundations/inspection_dossiers/regime_indicators/good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md` |
| Bad/blocking cases | present | `01_foundations/inspection_dossiers/regime_indicators/bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md` |
| Flagged minute cases | present | `01_foundations/inspection_dossiers/regime_indicators/flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md` |
| Coverage evidence | present | `01_foundations/inspection_dossiers/regime_indicators/coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md` |

## 4. File Structure And Technical Profile

Observed footprint:

| Type | Count |
| --- | ---: |
| parquet files | 67 |
| JSON files | 2 |
| daily parquet files | 34 |
| metadata symbols | 34 |
| minute parquet files | 33 |
| parquet read errors | 0 |

Observed layout:

- `etfs/<ETF_SYMBOL>/minute.parquet`;
- `etfs/<ETF_SYMBOL>/day.parquet`;
- `indices/<INDEX_SYMBOL_DIRECTORY>/minute.parquet` where available;
- `indices/<INDEX_SYMBOL_DIRECTORY>/day.parquet`;
- root metadata JSON files.

## 5. Schema Expected Vs Observed

Expected minute ETF schema:

- `timestamp`, `open`, `high`, `low`, `close`, `volume`, `vwap`.

Expected minute index schema:

- `timestamp`, `open`, `high`, `low`, `close`.

Expected daily schema:

- OHLC columns plus valid date/datetime fields.

Observed:

- minute schemas are coherent in representative inspection;
- daily columns are present but date semantics are invalid;
- minute timestamp review found no duplicate timestamp rows and no non-monotonic files;
- minute OHLC review found 204 `high < low` rows in `etfs/UVXY/minute.parquet`.

## 6. Blocking Quality Finding

All observed daily files have:

```text
date = 1970-01-01
```

and `datetime` values clustered in 1970.

This makes the daily files non-interpretable as calendar-keyed regime data.

Affected scope:

| Metric | Value |
| --- | ---: |
| Daily files | 34 |
| Daily rows | 153,397 |
| Files with only `1970-01-01` as `date` | 34 |
| Maximum per-file `date` unique count | 1 |

## 7. Cleanliness And Interpretability

Readable does not mean usable.

Daily files are structurally readable but semantically dirty because the key field needed for any daily join is invalid.

Minute files are not declared clean. They still require:

- duplicate timestamp audit;
- timestamp coverage audit;
- OHLC sanity;
- session/timezone interpretation;
- symbol coverage audit.

Current scoped minute review found:

| Metric | Value |
| --- | ---: |
| Minute files | 33 |
| Minute rows | 64,348,953 |
| Duplicate timestamp rows | 0 |
| Non-monotonic files | 0 |
| Negative ETF volume rows | 0 |
| `high < low` rows | 204 |

The `high < low` rows are concentrated in `etfs/UVXY/minute.parquet`.

## 8. Case Evidence

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good/scoped evidence | `01_foundations/inspection_dossiers/regime_indicators/good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md` | Minute and metadata evidence can support inspection/repair planning only. |
| Bad/blocking evidence | `01_foundations/inspection_dossiers/regime_indicators/bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md` | Daily bars are blocked because every daily file has invalid 1970 date semantics. |
| Flagged minute evidence | `01_foundations/inspection_dossiers/regime_indicators/flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md` | Scoped minute review found 204 `high < low` rows in `UVXY`. |
| Coverage evidence | `01_foundations/inspection_dossiers/regime_indicators/coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md` | Physical inventory and readability are documented. |
| Visual inspector pack | `01_foundations/inspection_dossiers/regime_indicators/visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md` | Visualizes the daily blocker, minute review scope, metadata context and consumption boundary. |
| Evidence assets | `01_foundations/inspection_dossiers/regime_indicators/evidence_assets/` | Stable CSV/JSON summaries and sample payloads. |

## 9. Consumer Matrix

| Consumer | Decision |
| --- | --- |
| `data_quality_report` | allowed |
| `source_validation` | allowed |
| `repair_planning` | allowed |
| `minute research inspection` | restricted |
| `daily regime features` | blocked |
| `master_daily_table` | blocked |
| `backtest_core` | blocked |
| `ml_primary` | blocked |
| `rl_allowed` | blocked |
| `live_downstream_candidate` | blocked |

## 10. Open Debt

Blocking:

- repair or regenerate daily files;
- demonstrate valid `symbol + date` keys;
- validate daily date ranges;
- audit minute files beyond representative schemas;
- classify or repair 204 `high < low` minute rows in `UVXY`;
- define whether metadata can be used in a documented repair.

## 11. Verdict

`regime_indicators_v0_1` does not meet the standard for daily regime consumption.

It now meets the foundation package standard for a blocked/scoped family:

```text
daily_bars_blocked_minute_bars_review_only
```
