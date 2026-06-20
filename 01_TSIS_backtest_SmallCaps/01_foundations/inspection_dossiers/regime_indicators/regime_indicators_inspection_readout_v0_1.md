# Regime Indicators Inspection Readout v0.1

## 1. Verdict

`regime_indicators_v0_1` is governed but blocked for daily use.

Current state:

```text
blocked_daily_scoped_minute_review_v0_1
```

Foundations completion status:

```text
human_inspector_ready
```

Visual inspection status:

```text
visual_complete
```

Minute files are schema-readable in representative inspection, but are not yet feature-production-ready.

Daily files are blocked because observed `date` and `datetime` semantics are invalid.

## 2. Scope

Physical root:

```text
E:/TSIS/data/regime_indicators
```

Contents:

- ETF bars under `etfs/`;
- index bars under `indices/`;
- `download_metadata.json`;
- `ticker_ranges.json`.

## 3. Authorities

Contracts and registry:

- `../../contract_registry/dataset_contracts/regime_indicators_dataset_contract_v0_1.md`
- `../../dataset_registry/regime_indicators/regime_indicators_registry_entry.yaml`
- `../../data_consumption_policies/regime_indicators_consumption_policy.md`
- `../../validators/regime_indicators/regime_indicators_validators.md`

Schemas:

- `../../canonical_schemas/regime_indicators/regime_etf_bars_schema_contract.md`
- `../../canonical_schemas/regime_indicators/regime_index_bars_schema_contract.md`
- `../../canonical_schemas/regime_indicators/regime_metadata_schema_contract.md`
- `../../canonical_schemas/regime_indicators/regime_indicators_quality_notes.md`

Data-quality report:

- `../../data_quality_report/families/regime_indicators_quality_report_v0_1.md`

Dossier-local evidence:

- `evidence_assets/README.md`
- `evidence_assets/regime_indicators_evidence_assets_manifest_v0_1.csv`
- `visual_inspector_pack/README.md`
- `visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md`
- `visual_inspector_pack/regime_indicators_visual_case_manifest_v0_1.csv`
- `visual_inspector_pack/regime_indicators_visual_asset_audit_v0_1.csv`
- `good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md`
- `bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md`
- `flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md`
- `coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md`
- `build_regime_indicators_inspection_pack.md`

## 4. Physical Root Profile

Observed physical footprint:

| Type | Count |
| --- | ---: |
| parquet files | 67 |
| JSON files | 2 |
| observed daily parquet files | 34 |
| symbols in `ticker_ranges.json` | 34 |
| minute parquet files | 33 |
| parquet read errors | 0 |

Observed root contents:

- `etfs`;
- `indices`;
- `download_metadata.json`;
- `ticker_ranges.json`.

## 5. File Structure And Technical Profile

ETF minute files:

- representative schema: `timestamp`, `open`, `high`, `low`, `close`, `volume`, `vwap`;
- minute rows across all minute files: 64,348,953;
- timestamp range across all minute files: `2004-01-02 13:00:00` to `2025-12-02 14:29:00`;
- duplicate timestamp rows observed in scoped review: 0;
- non-monotonic minute files observed in scoped review: 0;
- `high < low` rows observed in scoped review: 204, all in `etfs/UVXY/minute.parquet`.

ETF daily files:

- representative schema: `volume`, `vwap`, `open`, `close`, `high`, `low`, `trades`, `datetime`, `date`;
- current daily date semantics are invalid.

Index minute files:

- representative schema: `timestamp`, `open`, `high`, `low`, `close`;
- representative `I_NDX` minute rows: 25,701;
- representative timestamp range: `2023-08-01 13:30:00` to `2025-12-01 22:15:00`.

Index daily files:

- representative schema: `open`, `close`, `high`, `low`, `datetime`, `date`;
- current daily date semantics are invalid.

## 6. Blocking Daily Finding

All observed ETF and index daily files have:

| Field | Observed issue |
| --- | --- |
| `date` minimum | `1970-01-01` |
| `date` maximum | `1970-01-01` |
| `date` unique values | 1 |
| `datetime` | clustered in 1970 |

Affected scope:

| Metric | Value |
| --- | ---: |
| Daily files affected | 34 |
| Daily rows affected | 153,397 |
| Daily files with only `1970-01-01` as `date` | 34 |

Interpretation:

- daily files are readable;
- daily files are not semantically usable as calendar-keyed regime bars;
- the defect affects both ETFs and indices.

## 7. Metadata

`ticker_ranges.json` records 34 symbols and observed ranges.

It is useful as coverage/range evidence.

It does not repair the daily files.

## 8. Case Evidence

| Evidence group | Path | Reading |
| --- | --- | --- |
| Good/scoped minute and metadata evidence | `good_justification/regime_indicators_minute_and_metadata_examples_v0_1.md` | Minute timestamps and metadata are useful for inspection, not production promotion. |
| Blocking daily evidence | `bad_case_evidence_packs/regime_indicators_daily_date_blocker_v0_1.md` | All 34 daily files are blocked by invalid 1970 date semantics. |
| Flagged minute evidence | `flagged_case_evidence_packs/regime_indicators_minute_review_cases_v0_1.md` | Minute review found 204 `high < low` rows in `UVXY`. |
| Coverage evidence | `coverage_case_evidence_packs/regime_indicators_inventory_coverage_v0_1.md` | Physical files are readable, but readability is not a quality pass. |
| Visual inspector pack | `visual_inspector_pack/regime_indicators_visual_inspector_pack_v0_1.md` | Shows daily date collapse, daily file heatmap, UVXY minute high/low flags, minute coverage, metadata examples and consumption boundaries. |
| Stable evidence assets | `evidence_assets/` | CSV/JSON summaries and sample payloads used by this readout. |

This satisfies the human-inspector package requirement because the visual
inspection layer is now present. It does not clear the daily blocker or promote
minute bars.

## 9. Consumer Matrix

| Consumer | Status | Reason |
| --- | --- | --- |
| `data_quality_report` | allowed | This family must be reported as blocked/scoped. |
| `source_validation` | allowed | Needed for repair planning. |
| `repair_planning` | allowed | Primary useful next step. |
| `minute research inspection` | restricted | Schema-readable but not fully validated. |
| `daily regime features` | blocked | Date semantics invalid. |
| `master_daily_table` | blocked | Daily files cannot provide valid calendar keys. |
| `backtest_core` | blocked | No production contract. |
| `ML/RL/live` | blocked | Daily blocked; minute not production audited. |

## 10. Open Debt

Blocking:

- repair or regenerate daily files;
- prove valid `symbol + date` keys;
- validate daily date ranges against metadata/source;
- validate minute bars beyond scoped timestamp/schema review;
- classify or repair 204 `high < low` minute rows in `UVXY`;
- update root references from `D:/regime_indicators` where needed;
- regenerate dossier evidence assets after repair or re-audit.

## 11. Final Verdict

`regime_indicators_v0_1` fails the current standard for daily consumption.

It now satisfies the foundation package requirement for a blocked/scoped family:

- it is visible;
- it is registered;
- it has a contract;
- it has a policy;
- it has validator rules;
- it has a human readout;
- it has dossier-local evidence assets;
- it has good/scoped, bad/blocking, flagged and coverage case evidence;
- and its blocker is explicit.

Final verdict:

```text
daily_bars_blocked_minute_bars_review_only
```
