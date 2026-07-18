# ohlcv_1m_quote_guarded Dataset Contract v0.1

Status: `candidate_contract`

Date: 2026-07-16

## 1. Dataset Identity

```text
dataset_id: ohlcv_1m_quote_guarded_v0_2_candidate
dataset_family: ohlcv_1m
dataset_layer: derived_quote_guarded_minute_bars
canonical_price_view: quote_guarded_1m
current_status: validated_candidate_for_controlled_downstream_consumption
unrestricted_institutional_promotion: false
```

Authoritative companion artifacts:

- Policy: `01_foundations/data_consumption_policies/ohlcv_1m_quote_guarded_consumption_policy.md`
- Registry entry: `01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_quote_guarded_registry_entry.yaml`
- Status matrix: `01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md`

## 2. Purpose

`ohlcv_1m_quote_guarded` is a derived 1-minute OHLCV price view whose purpose is to repair known impossible or invalid minute-bar price values using quote-guarded evidence and to preserve explicit provenance for every repaired or inherited file.

It exists to provide a controlled input for downstream intraday table construction, especially:

- `014 master_intraday_bar_table`
- `018 intraday_scanner_candidates`
- controlled intraday diagnostics and forensic review

## 3. What It Represents

This dataset represents a quote-guarded 1-minute OHLCV derived price view over the TSIS small-cap intraday universe.

It may contain:

- original raw OHLCV values inherited from the raw 1m dataset;
- quote-guarded repaired OHLCV values where a repair was authorized by the repair manifest;
- raw-value provenance columns;
- repair status columns;
- source path and build provenance columns.

## 4. What It Does Not Represent

This dataset is not:

- the raw 1-minute OHLCV source of truth;
- a mutation of `ohlcv_1m_raw`;
- split-normalized data;
- dividend-adjusted data;
- trade-level evidence;
- quote-level evidence;
- an execution-quality simulator;
- a live feed substitute;
- an unrestricted ML/RL training source.

## 5. Source Lineage

The current validated candidate is produced from:

```text
raw source:
  C:/TSIS_Data/data/ohlcv_1m

historical candidate base:
  C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_1

failed-case delta repair:
  C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate

validated candidate output:
  C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

The v0.2 candidate was produced as a technical merge:

- files outside the failed 2015-2020 repair set were hardlinked from v0.1;
- failed 2015-2020 ticker-date outputs were replaced by the validated delta rerun;
- the raw layer was not modified.

## 6. Materialization Evidence

Merge manifest:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_build_runs/qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z/final_manifest_merge.json
```

Merge result:

```text
status: complete
errors: 0
original_files_seen: 1272004
original_files_linked: 1228331
original_files_skipped_expected_delta_pair: 43673
delta_files_seen: 43673
delta_files_linked: 43673
```

Validation manifest:

```text
C:/TSIS_Data/data/data_foundation_outputs/ohlcv_1m_quote_guarded_full_universe_v0_2_candidate/_validation_runs/qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z/final_manifest_validation.json
```

Validation result:

```text
status: PASS
errors: 0
warnings: 0
candidate_files_seen: 1272004
candidate_files_from_original: 1228331
candidate_files_from_delta: 43673
candidate_files_bad_source: 0
source_missing: 0
expected_delta_pairs_observed: 3918
schema_checked: 600
schema_mismatches: 0
promotion_authorization: false
```

## 7. Physical Schema Scope

The physical schema inherits the raw 1-minute OHLCV view and adds quote-guarded repair/provenance fields.

Expected core field families:

- identity and partition fields: `ticker`, `date`, `year`, `month`, timestamps;
- OHLCV fields: `o`, `h`, `l`, `c`, `v`, `vw`, `n`, `t`;
- raw provenance fields: `o_raw`, `h_raw`, `l_raw`, `c_raw`;
- quote-guarded repair fields: repair applied/state/reason fields;
- source and build fields: source path, dataset id, build run id, creation timestamp.

The current schema is validated by the validation manifest above. A dedicated canonical schema contract is required before unrestricted institutional promotion.

## 8. Allowed Consumers

Allowed controlled consumers:

- `014 master_intraday_bar_table` candidate builds;
- `018 intraday_scanner_candidates` candidate builds when explicitly configured to use `quote_guarded_1m`;
- intraday data-quality diagnostics;
- forensic comparison against raw 1m bars;
- controlled research that records dataset id, run id and policy.

## 9. Restricted Or Prohibited Uses

Restricted until further promotion:

- production backtests;
- ML/RL feature training;
- execution modeling;
- any dataset promoted as an unrestricted source of truth.

Prohibited:

- overwriting or mutating raw 1m data;
- treating quote-guarded bars as trade-level or quote-level evidence;
- silently replacing raw OHLCV in downstream code;
- using this dataset without recording its dataset id and validation manifest.

## 10. Quality And Coverage Contract

The current candidate may be consumed only if the following are true:

- final merge manifest exists and reports `status = complete`;
- final validation manifest exists and reports `status = PASS`;
- validation reports `errors = 0`;
- validation reports `schema_mismatches = 0`;
- downstream consumer records the dataset id and validation manifest path.

## 11. Change And Promotion Policy

Any semantic change requires a new logical version or a new candidate version.

Examples requiring a new version:

- repair logic changes;
- eligible repair universe changes;
- schema changes;
- source lineage changes;
- candidate is promoted to unrestricted institutional use.

Current contract verdict:

```text
current_verdict: validated_candidate_for_controlled_downstream_consumption
unrestricted_institutional_promotion: false
next_required_step: downstream_candidate_consumption_review
```
