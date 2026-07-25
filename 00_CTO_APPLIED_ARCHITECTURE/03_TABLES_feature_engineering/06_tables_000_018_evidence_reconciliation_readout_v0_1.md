# Tables 000-018 Evidence Reconciliation Readout v0.1

Status: `CLOSED_WITH_FINDINGS_NO_PROMOTION`
Run: `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z`
Date: `2026-07-24`

## Boundary

```text
dataset promotion = false
official dataset registry write = false
official parquet write = false
production builder execution = false
downstream consumption = false
Market State materialization = false
Event State materialization = false
event type registry population = false
event detection execution = false
source_market_data_rows_read = 0
parquet_files_read = 0
```

## Summary

```text
tables_seen = 19
proven_restricted_datasets = 13
proven_validated_candidates = 2
partial_reconciliations = 3
proven_restricted_controlled_replay_candidates = 1
unresolved = 0
classified_tables = 19
classification_invariant_pass = True
official_datasets_inferred = 0
source_market_data_rows_read = 0
parquet_files_read = 0
dataset_promotions_written = 0
event_type_registry_entries_written = 0
event_detection_runs_started = 0
```

## Table Conclusions

| ID | Table | Data Foundation status | Conclusion | Confidence |
| --- | --- | --- | --- | --- |
| 000 | `instrument_master` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 001 | `market_calendar` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 002 | `expected_data_calendar` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 003 | `dataset_certification_matrix` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 004 | `master_daily_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 005 | `corporate_actions_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 006 | `halts_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 007 | `event_windows_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 008 | `outcomes_table` | `controlled_candidate_not_promoted,validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET_WITH_CANDIDATE_EXTENSION` | `PROVEN` |
| 009 | `fundamentals_asof_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 010 | `news_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 011 | `short_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 012 | `regime_context_table` | `validated_for_declared_scope` | `PROVEN_RESTRICTED_DATASET` | `PROVEN` |
| 013 | `ohlcv_1m_quote_guarded` | `FOUND_REPAIR_OVERLAY_AND_CANDIDATE_TREE` | `PARTIALLY_RECONCILED_WITH_PROMOTED_REPAIR_OVERLAY_AND_CANDIDATE_TREE` | `PARTIAL` |
| 014 | `master_intraday_bar_table` | `scoped_pilot` | `PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS` | `PROVEN` |
| 015 | `microstructure_features_table` | `controlled_candidate_not_promoted,seed_state_sample` | `PROVEN_VALIDATED_CANDIDATE_WITH_RESTRICTIONS` | `PROVEN` |
| 016 | `market_state_table` | `controlled_candidate_not_promoted` | `PARTIALLY_RECONCILED_WITH_SEMANTIC_PHYSICAL_SPLIT` | `PARTIAL` |
| 017 | `event_state_table` | `controlled_candidate_not_promoted` | `PARTIALLY_RECONCILED_WITH_DESIGN_ONLY_CURRENT_PROFILE` | `PARTIAL` |
| 018 | `intraday_scanner_candidates_table` | `FOUND_CONTROLLED_REPLAY_EVIDENCE` | `PROVEN_RESTRICTED_CONTROLLED_REPLAY_CANDIDATE` | `PROVEN` |

## Critical Interpretations

- `016_market_state_table` is reconciled as a semantic/physical split: Data Foundation has a legacy controlled candidate, while Applied Architecture has promoted `market_state_core_four_intraday_profile_v0_1` as an official semantic profile. This does not create an official physical Market State dataset.
- `017_event_state_table` remains design-only for the current Event State architecture. Legacy controlled candidate evidence does not populate the current Event Type registry and does not authorize Event State execution.
- `013_ohlcv_1m_quote_guarded` is reconciled as a promoted repair overlay plus candidate physical tree, not as an unrestricted official full-universe intraday dataset.
- `018_intraday_scanner_candidates_table` is reconciled as controlled replay/candidate detector evidence. It is not Event Type authority.

## Next Gate

At reconciliation close, the next architectural gate was `event_type_registry_seed_design_v0_1`. That gate has since closed as design-only. The current next possible Event State gate, only if explicitly authorized, is:

```text
event_type_registry_initial_population_authorization_v0_1
```

No execution, promotion, production or downstream consumption opens from this readout.
