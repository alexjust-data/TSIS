
## 2026-07-21 | phase b | experimental core-four Market State integration execution passed with restrictions

- Added `06_MARKET_STATE_INTEGRATION/experimental_core_four_market_state_integration_execution_authorization_v0_1.md`, `configs/core_four_market_state_integration_execution_scope_v0_1.json` and `scripts/core_four_market_state_integration_probe.py`.
- Executed reference run `experimental_core_four_market_state_integration_execution_v0_1_20260721T203448Z` from accepted core-four resolution records: 40 input records, 10 contexts, 8 non-canonical candidate records, 2 expected required-object-blocked rejects, 136 admitted value rows, 0 future leaks and 0 blocked values admitted.
- Added `experimental_core_four_market_state_integration_execution_readout_v0_1.md` and updated Market State Integration, Builder Validation, experimental probe, feature-engineering README and local AGENT handoff.
- Boundary preserved: no physical source market data read, parquet materialization, production builder, State consumption, downstream consumption, full-history/full-universe execution or dataset promotion was authorized. Next possible gate is design-only `core_four_market_state_materialization_design`.

## 2026-07-21 | phase b | experimental bounded quality and lineage gate passed with restrictions

- Added `experimental_bounded_quality_lineage_validation_authorization_v0_1.md` and `configs/experimental_bounded_quality_lineage_scope_v0_1.json` for the non-production State Builder probe.
- Added four bounded policies: `004_price_view_selection_policy_v0_1.md`, `014_duplicate_intraday_bar_policy_v0_1.md`, `raw_quote_ordering_policy_v0_1.md` and `raw_quote_quality_policy_v0_1.md`.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_9` with `bounded_quality_and_lineage_validation`, quality/lineage field classification, policy derivation reports, builder execution blockers and promotion-only restrictions.
- Executed run `experimental_state_builder_probe_v0_9_20260721T184537Z`: `bounded_quality_lineage_validation = PASS_WITH_RESTRICTIONS`, `rows_read = 12271`, `maximum_rows_authorized = 20000`, `builder_execution_blockers = 2`, `core_four_builder_execution_blockers = 0`, `quote_dependent_builder_execution_blockers = 2` and `promotion_only_restrictions = 8`.
- Added `experimental_state_builder_probe_bounded_quality_lineage_readout_v0_1.md` and updated probe README, Builder Validation README, feature-engineering README and local AGENT handoff.
- Boundary preserved: no feature builder execution, production builder, State consumption, full data read, physical materialization, dataset promotion or Market State Integration was authorized. Next allowed gate is `experimental_builder_validation_execution_core_four`.

## 2026-07-21 | phase b | experimental bounded grain gate passed with restrictions

- Added `experimental_bounded_grain_validation_authorization_v0_1.md` and `configs/experimental_bounded_grain_scope_v0_1.json` for the non-production State Builder probe.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_8` with `bounded_grain_validation`, candidate key checks, duplicate classification, null-key reporting, hidden-dimension findings and raw quote same-timestamp reporting.
- Executed run `experimental_state_builder_probe_v0_8_20260721T171358Z`: `bounded_grain_validation = PASS_WITH_RESTRICTIONS`, `rows_read = 12271`, `maximum_rows_authorized = 20000`, `null_key_rows = 0`, `duplicate_key_groups = 1016`, `identical_duplicate_groups = 1001`, `conflicting_duplicate_groups = 15` and `raw_quotes_same_timestamp_groups = 16`.
- Added `experimental_state_builder_probe_bounded_grain_readout_v0_1.md` and updated probe README, Builder Validation README, feature-engineering README and local AGENT handoff.
- Boundary preserved: no feature builder execution, production builder, State consumption, full data read, physical materialization, dataset promotion or Market State Integration was authorized. Next gate is `bounded_quality_and_lineage_validation` design.

## 2026-07-21 | phase b | experimental bounded identity and temporal gate passed with restrictions

- Added `experimental_bounded_sample_validation_authorization_v0_1.md` and `configs/experimental_bounded_sample_scope_v0_1.json` to authorize only bounded row reads for five execution-critical aliases: `004_master_daily_table`, `013_ohlcv_1m_quote_guarded`, `014_master_intraday_bar_table_candidate`, `015_microstructure_features_table_candidate` and `raw_quotes`.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_7` with `bounded_identity_and_temporal_validation`, bounded Parquet batch reads, identity evidence checks, timestamp parsing, raw quote timestamp-unit detection, cutoff legality checks and daily availability policy execution.
- Executed run `experimental_state_builder_probe_v0_7_20260721T161612Z`: `bounded_sample_validation = PASS_WITH_RESTRICTIONS`, `rows_read = 6271`, `maximum_rows_authorized = 10000`, `identity_failures = 0`, `timestamp_parse_failures = 0`, `cutoff_future_bar_leaks = 0` and `daily_availability_policy_failures = 0`.
- Added `experimental_state_builder_probe_bounded_identity_temporal_readout_v0_1.md` and updated probe README, Builder Validation README, feature-engineering README and local AGENT handoff.
- Boundary preserved: no grain validation, feature builder execution, production builder, State consumption, full data read, physical materialization, dataset promotion or Market State Integration was authorized.

## 2026-07-21 | phase b | experimental column binding blockers resolved with restrictions

- Added `experimental_state_builder_probe/policies/daily_row_availability_policy_v0_1.md` and `experimental_state_builder_probe/policies/intraday_bar_identity_and_cutoff_policy_v0_1.md`.
- Updated `experimental_column_binding_registry_v0_1.json` to resolve the three prior critical blockers as restricted metadata bindings and to correct eight `valid_for_event_context_candidate` / `valid_for_state_component_candidate` expected type families from `date` to `boolean`.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_6`; identity-required physical-column bindings now report `RESOLVED_WITH_RESTRICTIONS`.
- Executed run `experimental_state_builder_probe_v0_6_20260721T154601Z` in `logical_to_physical_binding_check_only` mode: `logical_column_resolution = PASS_WITH_RESTRICTIONS`, `logical_fields_expected = 154`, `logical_fields_resolved = 125`, `logical_fields_resolved_with_restrictions = 22`, `logical_fields_unresolved = 6`, `critical_state_fields_blocked = 0`, `critical_temporal_fields_unresolved = 0`.
- Added `experimental_state_builder_probe_column_binding_readout_v0_2.md` and updated probe README, Builder Validation README, feature-engineering README and local AGENT handoff.
- Boundary preserved: no bounded sample reads, full data reads, grain validation, temporal value validation, State materialization, production builder execution, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | phase b | experimental logical-to-physical column binding gate executed

- Added `experimental_state_builder_probe/configs/experimental_column_binding_registry_v0_1.json` with explicit bindings for all active logical fields, including nominal matches, partition-key bindings, manifest/dataset metadata bindings, unavailable source-fix blockers and cast policy requirements.
- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_5` with `logical_to_physical_binding_check_only` and column-binding reports.
- Executed run `experimental_state_builder_probe_v0_5_20260721T144225Z`: `physical_source_binding = PASS`, `path_validation = PASS`, `schema_resolution = REEXECUTED_WITH_COLUMN_BINDINGS`, `logical_column_resolution = BLOCKED`, 154 fields expected, 118 resolved, 27 resolved with restrictions and 9 unresolved.
- Added `experimental_state_builder_probe_column_binding_readout_v0_1.md`; current critical blockers are `004_master_daily_table.as_of_utc`, `014_master_intraday_bar_table_candidate.instrument_id` and `014_master_intraday_bar_table_candidate.decision_timestamp_or_bar_end`.
- Boundary preserved: no bounded sample reads, full data reads, grain validation, temporal value validation, State materialization, production builder execution, dataset promotion or Market State Integration is authorized.

## 2026-07-21 | phase b | experimental schema metadata gate failed pending column binding

- Updated `experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_4`, added `binding_and_schema_check_only`, schema availability reporting, column compatibility reporting and schema fingerprint reporting.
- Executed run `experimental_state_builder_probe_v0_4_20260721T123345Z`: contract, ontology-to-mapping, blocked-capability, physical source binding and path gates pass; schema metadata gate fails.
- Result: `unique_sources_schema_checked = 10`, `unique_sources_schema_passed = 3`, `unique_sources_schema_failed = 7`, `minimum_columns_missing = 13`, `temporal_fields_missing = 5`, `quality_fields_missing = 9`, `lineage_fields_missing = 15`.
- Added `experimental_state_builder_probe_schema_metadata_readout_v0_1.md` and updated probe README, Builder Validation README and local AGENT handoff.
- Next required artifact is `configs/experimental_column_binding_registry_v0_1.json`; no bounded sample reads, full data reads, grain validation, temporal value validation, State materialization or Market State Integration is authorized.

# 03_TABLES_feature_engineering Changelog

This changelog records table-specific semantic and operational changes inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering
```

It does not replace the operational changelogs in:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
```

Use it to record table reading changes, maturity changes, validation evidence,
and important dependency decisions.

---

## 2026-07-21 | phase b | experimental physical source binding completed

- Bound the final active governed physical candidate root batch in `experimental_source_binding_registry_v0_1.json`: `010_news_context_table`, `009_fundamentals_asof_table`, `011_short_context_table`, `012_regime_context_table` and `006_halts_table`.
- Executed run `experimental_state_builder_probe_v0_3_20260721T105146Z` in `binding_and_path_check_only` mode: `physical_candidate_roots = BOUND`, `physical_source_binding = PASS`, `path_validation = PASS`, `physical_paths_checked = 10`, `physical_paths_found = 10` and `unbound_unique_source_aliases = 0`.
- Added `experimental_state_builder_probe_batch3_binding_readout_v0_1.md` and updated the probe README, Builder Validation README and local AGENT handoff.
- Next recommended gate is an explicit `binding_and_schema_check_only` mode for schema metadata only; grain uniqueness, temporal legality, quality semantics, data reads and State materialization remain later gates.
- Boundary preserved: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | experimental physical source binding batch 2 partial pass

- Bound the second governed physical candidate root batch in `experimental_source_binding_registry_v0_1.json`: `raw_quotes` and `015_microstructure_features_table_candidate`.
- Verified the quotes clone evidence before binding `raw_quotes`: `G:/TSIS/data/quotes_` is the local path-probe mirror of official `E:/TSIS/data/quotes_`; `G:/TSIS/data/quotes` is not used for this binding decision.
- Executed run `experimental_state_builder_probe_v0_3_20260721T103259Z` in `binding_and_path_check_only` mode: `physical_source_binding = PARTIAL`, `path_validation = PASS`, `physical_paths_checked = 5`, `physical_paths_found = 5` and `unbound_unique_source_aliases = 5`.
- Added `experimental_state_builder_probe_batch2_binding_readout_v0_1.md` and updated the probe README, Builder Validation README and local AGENT handoff.
- Boundary preserved: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | experimental physical source binding batch 1 partial pass

- Bound the first governed physical candidate root batch in `experimental_source_binding_registry_v0_1.json`: `004_master_daily_table`, `013_ohlcv_1m_quote_guarded` and `014_master_intraday_bar_table_candidate`.
- Executed run `experimental_state_builder_probe_v0_3_20260721T102009Z` in `binding_and_path_check_only` mode: `physical_source_binding = PARTIAL`, `path_validation = PASS`, `physical_paths_checked = 3`, `physical_paths_found = 3` and `unbound_unique_source_aliases = 7`.
- Added `experimental_state_builder_probe_batch1_binding_readout_v0_1.md` and updated the probe README, Builder Validation README and local AGENT handoff.
- Boundary preserved: no production builder, State consumption, schema metadata discovery, bounded/full data read, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | experimental physical source binding gate opened v0_3

- Updated the experimental State Builder probe to `experimental_state_builder_probe_v0_3` with `binding_and_path_check_only` replacing the superseded `binding_and_schema_check_only` mode name.
- Made source binding registry validation mode-aware: `contract_check_only` no longer requires filesystem/schema metadata authority, while `binding_and_path_check_only` requires only filesystem metadata authority.
- Replaced textual prefix root checks with `Path.relative_to()` boundary checks for allowed roots.
- Executed smoke run `experimental_state_builder_probe_v0_3_20260721T095712Z`: `contract_check = CLOSED_PASS`, `experimental_physical_source_binding = OPEN`, `physical_candidate_roots = PENDING`, `path_validation = NOT_EXECUTED`, `schema_validation = NOT_EXECUTED`, `data_validation = NOT_AUTHORIZED`.
- Boundary preserved: no production builder, State consumption, schema metadata discovery, bounded/full data read, schema change, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | experimental source binding registry v0_2 probe passed pending bindings

- Added `experimental_state_builder_probe/configs/experimental_source_binding_registry_v0_1.json` as the governed experimental registry separating logical `source_alias` from physical source surface.
- Updated `experimental_state_builder_probe/scripts/experimental_state_builder_probe.py` to `experimental_state_builder_probe_v0_2`, accepting `binding_and_schema_check_only`, loading the external registry and making `source_warn_count` affect `overall_status`.
- Executed smoke run `experimental_state_builder_probe_v0_2_20260721T093704Z`: `contract_resolution = PASS`, `physical_source_binding = INCOMPLETE`, `active_source_alias_usages = 21`, `unique_active_source_aliases = 10`, `unbound_unique_source_aliases = 10` and `physical_paths_checked = 0`.
- Added `experimental_state_builder_probe_smoke_readout_v0_2.md` and updated the local handoff so the next gate is governed physical binding for the 10 unique active aliases.
- Boundary preserved: no production builder, State consumption, bounded sample read, full data read, schema change, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | experimental state builder probe scaffolded and smoked

- Added `05_STATE_BUILDER_VALIDATION/experimental_state_builder_probe/` with config, script, run root and smoke readout.
- Executed smoke run `experimental_state_builder_probe_v0_1_20260721T091253Z` in `contract_check_only` mode: 12 objects checked, 48 dry-run resolution snapshots, 0 failures, 21 source-binding warnings, 1 expected block and 0 blocked-capability leaks.
- Recorded the first engineering finding: source aliases need governed experimental physical bindings before physical path/schema checks.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration was authorized.
## 2026-07-21 | phase b | builder validation v1 designs completed

- Completed Builder Validation design coverage for all 12 `TSIS Market Ontology v1` Information Objects.
- Added `liquidity_builder_validation_v0_1.md`, `market_microstructure_state_builder_validation_v0_1.md`, `order_flow_pressure_builder_validation_v0_1.md`, `news_catalyst_context_builder_validation_v0_1.md`, `fundamental_context_builder_validation_v0_1.md`, `short_side_context_builder_validation_v0_1.md`, `broad_market_context_builder_validation_v0_1.md` and `halt_context_builder_validation_v0_1.md`.
- Recorded `Order Flow Pressure` as blocked pending trade-quote alignment, side classifier and classifier confidence policy.
- Added `05_STATE_BUILDER_VALIDATION/experimental_state_builder_boundary_v0_1.md` so the next executable is a non-production experimental builder.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration was authorized.

## 2026-07-21 | phase b | builder validation first batch added

- Added Builder Validation design artifacts for `Price Movement`, `Price Location / Structure` and `Volatility / Range State`.
- Added `05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_phase_b_ratification_v0_1.md` and aligned the original `Trading Activity` pilot with Phase B.
- Updated `05_STATE_BUILDER_VALIDATION/README.md` and `AGENT.md` to record the first Builder Validation batch as `design_ready_pending_execution`.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization, dataset promotion or Market State Integration was authorized.

## 2026-07-21 | phase b | operational mapping v1 batch completed

- Completed governed Operational Mapping coverage for all 12 admitted Information Objects in `TSIS Market Ontology v1`.
- Added `volatility_range_state_operational_mapping_v0_1.md`, `liquidity_operational_mapping_v0_1.md`, `market_microstructure_state_operational_mapping_v0_1.md`, `order_flow_pressure_operational_mapping_v0_1.md`, `news_catalyst_context_operational_mapping_v0_1.md`, `fundamental_context_operational_mapping_v0_1.md`, `short_side_context_operational_mapping_v0_1.md`, `broad_market_context_operational_mapping_v0_1.md`, `halt_context_operational_mapping_v0_1.md`, and `trading_activity_operational_mapping_phase_b_ratification_v0_1.md`.
- Updated `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/README.md` and `AGENT.md` to mark Operational Mapping complete for v1 and set `Builder Validation` as the next gate.
- Aligned `trading_activity_operational_mapping_v0_1.md` with its Phase B ratification so the pilot no longer carries a stale deferred-phase boundary.
- Preserved gates: `Order Flow Pressure` remains State-blocked until trade-quote alignment, side classifier and confidence policy are governed; advanced liquidity, VWAP, float PIT, borrow/locate, macro and model-derived context remain behind their declared policies.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization or dataset promotion was authorized.

## 2026-07-21 | phase b | price location structure operational mapping added

- Added `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_location_structure_operational_mapping_v0_1.md`.
- Mapped the minimum `Price Location / Structure` profile to `session_anchor_location_model` and `prior_close_location_model`, with prior/after-close daily structure as context only.
- Kept VWAP distance, HOD/LOD distance, session range position, anchored VWAP and pullback/retrace behind explicit policy, formula or boundary gates.
- Updated `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/README.md` and `AGENT.md` so the next recommended Operational Mapping object is `Volatility / Range State`.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization or dataset promotion was authorized.

## 2026-07-21 | phase b | price movement operational mapping added

- Added `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/price_movement_operational_mapping_v0_1.md`.
- Started Phase B with a governed Operational Mapping for `Price Movement`, using `intraday_return_to_reference_model`, `opening_gap_movement_model` and prior/after-close daily movement as the first core profile.
- Kept `intraday__bar_return`, speed, acceleration, momentum and reversal/fade behind explicit capability, variant or boundary gates.
- Updated `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/README.md` and `AGENT.md` so the next recommended Operational Mapping object is `Price Location / Structure`.
- Boundary preserved: no production builder, State consumption, schema change, physical materialization or dataset promotion was authorized.

## 2026-07-21 | information objects | market ontology v1 freeze act added

- Added `03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_FREEZE.md` as the institutional freeze act for `TSIS Market Ontology v1`.
- Closed Phase A with `ontology_status = FROZEN`, `ontology_lock_status = LOCKED`, `phase_a_status = CLOSED` and `phase_b_status = OPEN`.
- Authorized Phase B to start as governed engineering through Operational Mapping, followed by Builder Validation, Market State Integration, Event State Integration and Operational Promotion.
- Preserved hard boundaries: no production builder, State consumption, physical variables as state authority, schema/materialization or dataset promotion is authorized by the freeze alone.
- Updated `AGENT.md` so the local handoff points to the frozen ontology and Phase B Operational Mapping as the next active work.
- Aligned `README.md`, `03_INFORMATION_OBJECTS/README.md`, `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/README.md`, `05_STATE_BUILDER_VALIDATION/README.md` and `06_MARKET_STATE_INTEGRATION/README.md` with the frozen ontology and Phase B gate sequence.
## 2026-07-21 | information objects | cross-object ontology review added

- Added `03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_REVIEW.md`.
- Reviewed coverage, redundancies, gaps, boundaries, shared evidence, minimal semantic identities and critical pending concepts across all 12 admitted Information Objects.
- Decision: `passes_with_restrictions`; no Object requires merge/split before freeze and no new Information Object blocks v1 freeze.
- Updated `AGENT.md` so the next step is `TSIS Market Ontology v1 Freeze`.
- Boundary unchanged: no README, methodology, Operational Mapping, Builder Validation, Market State Integration, production builder work, schema change or physical variable was authorized.

## 2026-07-21 | information objects | remaining formal admissions completed

- Added Formal Admission artifacts for the 9 remaining main Information Objects: `volatility_range_state`, `liquidity`, `market_microstructure_state`, `order_flow_pressure`, `news_catalyst_context`, `fundamental_context`, `short_side_context`, `broad_market_context` and `halt_context`.
- Kept `Order Flow Pressure` operationally blocked for State until trade-quote alignment, side classifier and confidence policy are governed.
- Preserved Phase A boundary across all admissions: ontology authority only; Phase B engineering remains deferred.
- Updated `03_TABLES_feature_engineering/AGENT.md` so the handoff points to Cross-Object Ontology Review after completing all 12 Formal Admissions.
- Boundary unchanged: no README, methodology, Operational Mapping, Builder Validation, Market State Integration, production builder work, schema change or physical variable was authorized.

## 2026-07-21 | price location structure | formal admission added

- Added `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/price_location_structure_formal_admission_v0_1.md`.
- Accepted `Price Location / Structure` as an Information Object with high-confidence scientific identity and restricted operational readiness.
- Kept VWAP policy, HOD/LOD observed-only handling, range-position formula and pullback/retrace boundary decisions as restrictions for future review or Phase B mapping.
- Boundary unchanged: no Operational Mapping, Builder Validation, Market State Integration, production builder work, schema change or physical variable was authorized.

## 2026-07-21 | agent handoff | ontology phase continuation prompt added

- Added `AGENT.md` with the exact local reading path for agents entering `03_TABLES_feature_engineering`.
- Recorded current status: `Trading Activity` and `Price Movement` are formally admitted with restrictions; 10 Formal Admissions remain before Cross-Object Ontology Review.
- Recorded the expected path to `TSIS_MARKET_ONTOLOGY_V1_REVIEW.md` and the freeze criteria for `TSIS Market Ontology v1`.
- Boundary unchanged: no README, methodology, Operational Mapping, Builder Validation, Market State Integration or production builder work was changed.

## 2026-07-21 | price movement | formal admission added

- Added `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/price_movement_formal_admission_v0_1.md`.
- Accepted `Price Movement` as an Information Object with high-confidence scientific identity and restricted operational readiness.
- Kept Momentum as `representation_model_or_subobject_pending` and kept `intraday__bar_return` pending capability decision.
- Boundary unchanged: no Operational Mapping, Builder Validation, Market State Integration, production builder work, schema change or physical variable was authorized.

## 2026-07-21 | information objects | phase a/b readme boundary corrected

- Replaced the stale `trabajo activo pasa a validacion vertical` wording in `03_INFORMATION_OBJECTS/README.md`.
- Clarified that the active phase is Object Admission Review -> Formal Admission -> Cross-Object Ontology Review -> `TSIS Market Ontology v1 Freeze`.
- Clarified in `README.md` that lifecycle steps 8-12 are Phase B and remain deferred until ontology freeze.
- Boundary unchanged: no Operational Mapping expansion, Builder Validation expansion, Market State Integration expansion or production builder work was authorized.

## 2026-07-20 | information objects | ontology phase gate activated

- Added `03_INFORMATION_OBJECTS/04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md`.
- Added phase-boundary README files for `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/`, `05_STATE_BUILDER_VALIDATION/` and `06_MARKET_STATE_INTEGRATION/`.
- Marked Phase A as active: complete Formal Admission for all main Information Objects before expanding Phase B engineering.
- Updated feature-engineering `README.md` and `03_INFORMATION_OBJECTS/README.md` with the no-production-builder gate; the detailed rule lives in `03_INFORMATION_OBJECTS/04_TSIS_MARKET_ONTOLOGY_PHASE_v0_1.md`.
- Boundary unchanged: `Trading Activity` remains a pilot vertical; no operational consumption, schema, builder, dataset or materialization was authorized.

## 2026-07-20 | trading activity | formal admission vertical added

- Added `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/trading_activity_formal_admission_v0_1.md`.
- Added `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/trading_activity_operational_mapping_v0_1.md`.
- Added `05_STATE_BUILDER_VALIDATION/trading_activity_builder_validation_v0_1.md`.
- Added `06_MARKET_STATE_INTEGRATION/trading_activity_market_state_integration_v0_1.md`.
- Accepted scientific identity for `Trading Activity` while keeping operational readiness restricted pending builder validation and operational contract promotion.
- Updated `README.md` and `03_INFORMATION_OBJECTS/README.md` to reflect the new post-review vertical flow.
- Boundary unchanged: no State variable, schema, builder, contract, dataset or physical materialization was authorized.


## 2026-07-20 | information objects | domain-to-candidate-object status correction

- Reclassified the 12 domain outputs from accepted-with-restrictions object artifacts to candidate object definitions under `03_INFORMATION_OBJECTS/CANDIDATES/`.
- Replaced active landscape decision wording from `ready_for_object_admission` to `ready_to_define_candidate_object`.
- Clarified that the active scientific unit of work is the Domain; formal Information Object admission has not started for this batch.
- Updated `03_INFORMATION_OBJECTS/README.md` so active paths point to `CANDIDATES/` and not to `ACCEPTED_WITH_RESTRICTIONS/`.
- Boundary unchanged: no State variable was authorized, no physical variable was authorized, and no schema, builder, contract or dataset promotion changed.`r`n`r`n## 2026-07-20 | information objects | remaining context domains accepted with restrictions

- Created domain, landscape and accepted-with-restrictions artifacts for `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context` and `Halt Context`.
- Classified `Event Window Context` as infrastructure context, not an ordinary market Information Object.
- Kept all context objects under as-of, lag, source and model restrictions.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | microstructure and order flow accepted with restrictions

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/market_microstructure_state_domain_definition_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/market_microstructure_state_representation_landscape_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/market_microstructure_state_information_object_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/order_flow_pressure_domain_definition_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/order_flow_pressure_representation_landscape_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/order_flow_pressure_information_object_v0_1.md`.
- Accepted `Market Microstructure State` with restrictions as observable top-of-book/tape condition context.
- Accepted `Order Flow Pressure` with restrictions, blocked for State consumption until trade-quote alignment and side-classifier governance exist.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | liquidity accepted with restrictions

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/liquidity_domain_definition_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/liquidity_representation_landscape_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/liquidity_information_object_v0_1.md`.
- Accepted `Liquidity` with restrictions as the Information Object preserving observable cost, ease and availability of trading.
- Kept Trading Activity, Market Microstructure, Order Flow, Execution Outcomes and future realized spread outside the admitted core.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | volatility range state accepted with restrictions

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/volatility_range_state_domain_definition_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/volatility_range_state_representation_landscape_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/volatility_range_state_information_object_v0_1.md`.
- Accepted `Volatility / Range State` with restrictions as the Information Object preserving observable amplitude, dispersion and uncertainty.
- Kept Price Movement, Price Location, Activity, Liquidity and Outcomes outside the admitted object.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | price location structure accepted with restrictions

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/price_location_structure_domain_definition_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/price_location_structure_representation_landscape_v0_1.md`.
- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/price_location_structure_information_object_v0_1.md`.
- Accepted `Price Location / Structure` with restrictions as the Information Object preserving contextual price location against legal references in t.
- Kept Price Movement, Volatility/Range, Activity, Liquidity, Outcomes and Quality outside the admitted object.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | price movement accepted with restrictions

- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/price_movement_information_object_v0_1.md`.
- Accepted `Price Movement` as an Information Object with restrictions after Domain Definition and Representation Landscape review.
- Required operational mapping before any State consumption or physical variable authorization.
- Kept Price Location, Volatility/Range and future Outcome Response outside the admitted object.
- Noted that `intraday__bar_return` may require an explicit atomic derivable capability before mapping.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | price movement representation landscape v0_1

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/price_movement_representation_landscape_v0_1.md`.
- Reviewed daily, intraday, opening gap, speed, acceleration, momentum and reversal/fade representation models before formal Object admission.
- Kept `Price Movement` as the only candidate to forward by default.
- Kept `Price Location / Structure`, `Volatility / Range State` and `Outcome Response` outside the domain.
- Marked `Price Movement` as `ready_for_object_admission`.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | domain definitions | price movement domain v0_1 created

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/price_movement_domain_definition_v0_1.md`.
- Defined `Price Movement` as the domain preserving observable price change, direction, speed and acceleration under legal temporal references.
- Separated `Price Movement` from `Price Location / Structure`, `Volatility / Range State`, `Trading Activity`, `Liquidity`, `Order Flow Pressure`, `Quality` and `Outcome` layers.
- Marked `Momentum`, `Opening Gap Movement`, `Speed` and `Acceleration` as model/subobject questions for the upcoming Representation Landscape, not admitted Objects.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | trading activity accepted with restrictions

- Created `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/trading_activity_information_object_v0_1.md`.
- Accepted `Trading Activity` as an Information Object with restrictions after Domain Definition and Representation Landscape review.
- Required operational mapping before any State consumption or physical variable authorization.
- Kept scanner selection, signed/aggressor flow, short activity and true float turnover outside the admitted core until their own reviews or sources exist.
- Boundary unchanged: no variable was authorized for State, no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | trading activity representation landscape v0_1

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/trading_activity_representation_landscape_v0_1.md`.
- Reviewed the scientific representation models for `Trading Activity` before formal Object admission.
- Classified daily, intraday, relative, trade-window and scanner-adjacent models without admitting them as separate Objects by default.
- Moved `Short Activity` toward `Short-Side Context`, and signed/aggressor measures toward `Order Flow Pressure`.
- Marked `Trading Activity` as `ready_for_object_admission`.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | domain definitions | trading activity scientific review applied

- Renamed the first domain file from `trading_activity_and_participation_domain_definition_v0_1.md` to `trading_activity_domain_definition_v0_1.md`.
- Canonicalized the domain name as `Trading Activity`; participation is treated as the semantic property preserved by the domain, not a separate domain name.
- Removed scanner-quality wording from the domain definition and kept scanner material as selection-surface-adjacent.
- Added an anti-duplication rule: changes in baseline, normalization, window, parameterization or temporal resolution do not automatically create a new Information Object.
- Split derivable capabilities into indispensable, complementary and boundary/fronteriza groups for later Market State profile work.
- Added the semantic meaning principle to `03_INFORMATION_OBJECTS/README.md`: variable meaning belongs to Domain -> Object -> Representation Model -> legal use, not to the variable alone.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | domain definitions | trading activity domain v0_1 created

- Created `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/trading_activity_domain_definition_v0_1.md`.
- Created active `03_INFORMATION_OBJECTS/DOMAIN_DEFINITIONS/` folder for real domain definitions and representation landscapes before Object admission.
- Defined `Trading Activity` as the domain preserving intensity of negotiated participation across declared temporal scales.
- Marked `Daily Trading Activity` and `Intraday Trading Activity` as temporal/model specializations, not separate Objects by default.
- Kept `Attention Activity Candidate` as selection-surface-adjacent and not admitted.
- Updated `03_INFORMATION_OBJECTS/02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md` to allow `ready_for_representation_landscape`.
- Updated `03_INFORMATION_OBJECTS/README.md` with the `DOMAIN_DEFINITIONS/` folder role.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | representation landscape gate added

- Added `03_INFORMATION_OBJECTS/03_REPRESENTATION_LANDSCAPE_TEMPLATE_v0_1.md`.
- Strengthened `03_INFORMATION_OBJECTS/02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md` with two mandatory questions: why the domain deserves to exist, and what TSIS would lose if it disappeared.
- Updated `03_INFORMATION_OBJECTS/01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md` so the flow is: Semantic Domain Consolidation -> Domain Definition -> Representation Landscape -> Object Admission.
- Updated `03_INFORMATION_OBJECTS/README.md` with the new order before opening `CANDIDATES/` dossiers.
- Boundary unchanged: no Object was admitted, no representation model was selected, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | domain definition gate added

- Created `03_INFORMATION_OBJECTS/02_DOMAIN_DEFINITION_TEMPLATE_v0_1.md`.
- Inserted a lightweight `Domain Definition` step between `Semantic Domain Consolidation` and formal `Object Admission`.
- Renamed the nature bucket from `Observable Market Knowledge` to `Market Information Domains` to avoid overloading `Knowledge`, which is reserved for validated scientific knowledge in TSIS.
- Updated `03_INFORMATION_OBJECTS/01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md` so the next step is `domain_definition_cluster_1_trading_activity`.
- Updated `03_INFORMATION_OBJECTS/README.md` with the active order: candidate matrix -> semantic consolidation -> domain definition -> candidate dossiers.
- Boundary unchanged: no Object was admitted, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | semantic domain consolidation added

- Created `03_INFORMATION_OBJECTS/01_SEMANTIC_DOMAIN_CONSOLIDATION_v0_1.md`.
- Inserted a pre-admission consolidation phase between the candidate matrix and formal Information Object dossiers.
- Classified candidates by nature: infrastructure, quality/governance, Market Information Domains, canonical core representations, outcome layer and selection surfaces.
- Split the broad price area into provisional clusters: `Price Movement`, `Price Location / Structure`, and `Volatility / Range State`.
- Updated `03_INFORMATION_OBJECTS/00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md` so the next step is `semantic_domain_consolidation`, not direct Object admission.
- Updated `03_INFORMATION_OBJECTS/README.md` with the active order: candidate matrix -> semantic domain consolidation -> candidate dossiers.
- Boundary unchanged: no Object was admitted, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.

## 2026-07-20 | information objects | candidate normalization matrix v0_1

- Created `03_INFORMATION_OBJECTS/00_INFORMATION_OBJECT_CANDIDATE_MATRIX_v0_1.md`.
- Consolidated candidate Information Objects discovered in the `000-018` table discovery pass before formal Object admission.
- Classified raw candidates as provisional Information Objects, representation models, temporal specializations, context objects, infrastructure objects, quality/governance objects, canonical core representations, outcome-only artifacts or selection surfaces.
- Clarified that `Daily Trading Activity` and `Intraday Trading Activity` are provisional temporal/model variants under `Trading Activity`, not separate Objects by default.
- Clarified that `Market State` and `Event State` are canonical core representations, not ordinary Information Objects.
- Boundary unchanged: no Object was admitted, no variable was authorized for State, and no schema, builder, contract or dataset promotion changed.


## 2026-07-20 | table_representation_review | pass_01 discovery 000-018

- Created `02_TABLE_REPRESENTATION_REVIEW/00_DISCOVERY_PASS_000_018_v0_1.md` as the first transversal discovery matrix for tables 000-018.
- Created normalized `table_representation_audit_ES.md` files in each table folder from `000` through `018`.
- Scope is discovery only: no Information Object admission, no schema/builder changes, no dataset promotion.

## 2026-07-20 | event state | consumption_legality separated from state_role

- Clarified that `state_role` is not sufficient to authorize Event State consumption.
- Added `consumption_legality` values: `decision_safe`, `research_only`, `outcome_adjacent`, `prohibited_as_input`.
- Updated feature-engineering README/explainer, table-review local rules/templates, `017` review and handoff copies.
- Boundary unchanged: no Event State table, builder, promotion or downstream consumption authorization changed.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip`.
- New handoff ZIP SHA256: `95DC0EE26DFE73E3E62B7EA446EF7A010892B0E1E14A4B37CD245F70BE0806C5`.


## 2026-07-20 | market state | anti mega-table profile rule added

- Clarified that canonical Market State does not mean one physical row/table containing every attribute any consumer may want.
- Defined canonicality as common state semantics, stable `market_state_id`, temporal legality rules and compatible physical representation profiles.
- Added conceptual profile pattern: `market_state_core`, `market_state_daily_context`, `market_state_intraday`, `market_state_microstructure_extension`, and `market_state_news_extension`.
- Updated local rules, templates, `016` table review, handoff context copies and feature-engineering README/explainer.
- Boundary unchanged: no schema, builder, dataset promotion or downstream consumption authorization changed.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip`.
- New handoff ZIP SHA256: `1C7E26C887343DD6C762AE37D087E3D29D786548C9A44A35CD37CC8D461457F0`.


## 2026-07-20 | information objects | taxonomy axes separated

- Clarified that `Information Object Family` is a semantic axis only.
- Separated four axes that must not share a generic `family` field: `information_object_family`, `source_domain`, `temporal_resolution`, and `institutional_role`.
- Added starting values for each axis in `README.md`, `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md`, table-review `LOCAL_RULES.md`, `TABLE_REPRESENTATION_REVIEW_TEMPLATE.md`, `OBJECT_CANDIDATES_TEMPLATE.md`, handoff context copies and `03_INFORMATION_OBJECTS/README.md`.
- Clarified that legacy uses such as `Feature Family`, `dataset_family`, `event_family`, `quality family` or `outcome_family` are not interchangeable with Information Object Family.
- Boundary unchanged: no Information Object was admitted and no table/state consumption authorization changed.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip`.
- New handoff ZIP SHA256: `A8CF8EAF5728A5C17AC09109E120DA4AE84EC36F0C03E3309BCC2F592383F7BE`.

## 2026-07-20 | information objects | definition separated from representation model

- Replaced the ambiguous definition of `Information Object` as a representation of a market property.
- Canonical local definition is now: an Information Object is a semantic unit of information TSIS decides to preserve about one or more observable phenomena, independent of its Representation Model and physical implementation.
- Clarified the separation:
  - `Liquidity` = Information Object.
  - trading cost + depth + availability = Representation Model.
  - `spread_bps` + `depth` + `quote_count` = Physical Implementation.
- Updated `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md`, `00_TABLES_MARKET_STATE_EVENT_STATE.md`, `README.md`, table-review `LOCAL_RULES.md`, `OBJECT_CANDIDATES_TEMPLATE.md`, handoff context copies and `03_INFORMATION_OBJECTS/README.md`.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip`.
- New handoff ZIP SHA256: `E093B09524419B399B7952D8F59EA167E8B58830B8D41C521BC630D554910B4F`.
- Boundary unchanged: no Object was admitted and no table/state consumption was authorized.

## 2026-07-20 | information objects | Discovery vs Admission boundary formalized

- Added explicit distinction between `Object Discovery Process` and `Object Admission Process`.
- Clarified that table reviews, derivable capabilities and existing variables may discover candidate Information Objects but cannot admit them.
- Clarified that formal admission must reconstruct the scientific direction: phenomenon/scientific need -> Information Object -> Representation Model -> implementation candidates -> temporal legality -> decision.
- Updated `README.md`, `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md`, `02_TABLE_REPRESENTATION_REVIEW/LOCAL_RULES.md` and `OBJECT_CANDIDATES_TEMPLATE.md`.
- Replaced the unsafe variable wording with explicit states: `candidate_variable`, `admitted_variable`, and `state_eligible_variable`.
- Updated handoff context copies and regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip`.
- New handoff ZIP SHA256: `50ECEBA8A389DC6EF701AA69A53083C85A144ABB8C0B5CAC9467D90888690B9F`.

## 2026-07-20 | table review | Information Objects path corrected

- Replaced stale Information Objects path references with active `03_INFORMATION_OBJECTS` references in table-review local rules and object-candidate templates.
- Updated handoff context copies so external agents create candidate Object files under the correct active folder.
- Boundary unchanged: this is a path-authority correction only; no Object admission decision changed.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip` after the path correction.
- New handoff ZIP SHA256: `CEBD3A545B21DB9F0C032AC260FA353F39F46F0725F938B8AAE565915E8451CD`.

## 2026-07-20 | table review | canonical 013-018 DAG fixed in LOCAL_RULES

- Replaced the stale linear 013-018 dependency chain in `02_TABLE_REPRESENTATION_REVIEW/LOCAL_RULES.md`.
- Canonicalized `014_master_intraday_bar_table` and `015_microstructure_features_table` as sibling representation surfaces.
- Clarified that `015` may have a full/general microstructure profile and selective event-window materialization profiles.
- Clarified that `018_intraday_scanner_candidates_table` is optional scanner/candidate context for `016_market_state_table`, not a universal upstream prerequisite.
- Added explicit dependency classes: `semantic_dependency`, `physical_source_dependency`, `eligibility_dependency`, and `materialization_selection_dependency`.
- Updated the handoff `_context/LOCAL_RULES.md` copy to avoid carrying the old DAG inside the table review package folder.
- Regenerated `TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip` after the rule correction.
- New handoff ZIP SHA256: `DC983452A93CC196416AFDC63922270C92489FEC6F1E928E99ED04F8975D3658`.
## 2026-07-20 | table review | table representation review handoff package 000-018

- Added structured external-agent handoff package under `02_TABLE_REPRESENTATION_REVIEW`:

```text
TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720/
TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip
```

- Included `000-012` table documents plus their Spanish representation audits.
- Included `013` operational reading and `014-018` current table target documents.
- Included `LOCAL_RULES.md`, `TABLE_REPRESENTATION_REVIEW_TEMPLATE.md`, `OBJECT_CANDIDATES_TEMPLATE.md`, manifest and README.
- Boundary: handoff inventory only; no table status, promotion, schema, validator or downstream consumption authorization changed.
## 2026-07-20 | README | operational map aligned with active structure

- Updated `README.md` from `readme_v0_2_current_structure` to `readme_v0_3_operational_map`.
- Replaced stale paths and names with the active structure:
  - `01_INFORMATION_OBJECT_ADMISSION_PROCESS.md`
  - `02_TABLE_REPRESENTATION_REVIEW/`
  - `03_INFORMATION_OBJECTS/`
  - `99_archive/`
- Separated table review from Information Object admission.
- Corrected the 013-018 relationship from a linear chain to parallel intraday bar and microstructure surfaces feeding Market State.
- Clarified that `008_outcomes_table` remains a separated label/outcome surface, not an observable Market State input.
- Updated `02_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md` header/path references after folder renaming.

## 2026-07-20 | table review | first architectural question refined

- Refined the first table review question in `01_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md` and `TABLE_REPRESENTATION_REVIEW_TEMPLATE.md`.
- Replaced the overloaded question "what phenomenon or representation does the table materialize?" with:
  - what entity, representation or institutional function does the table materialize;
  - whether it represents market information, infrastructure, context, quality, governance, event, state or outcome;
  - which market phenomena are described when the table actually stores market information.
- This prevents infrastructure tables such as `001_market_calendar` and governance tables such as `003_dataset_certification_matrix` from being forced into a market-phenomenon frame.

## 2026-07-20 | table review | per-table folder roles specified

- Extended `01_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md` with the expected three-file structure for each table review folder:
  - `<table_name>.md` for current physical/contractual/schema state;
  - `table_representation_audit_ES.md` for the table-level audit;
  - `object_candidates.md` as the bridge to Information Object admission.
- Added `01_TABLE_REPRESENTATION_REVIEW\OBJECT_CANDIDATES_TEMPLATE.md`.
- Clarified that table audits identify candidate Information Objects, but the scientific object admission must live under `03_INFORMATION_OBJECTS`.

## 2026-07-20 | table review | two-level review standard added

- Updated `01_TABLE_REPRESENTATION_REVIEW\LOCAL_RULES.md` to separate table review into:
  - Level 1 architectural questions;
  - Level 2 physical and boundary questions.
- Added `01_TABLE_REPRESENTATION_REVIEW\TABLE_REPRESENTATION_REVIEW_TEMPLATE.md` so reviews of tables `000-018` can be compared with the same structure.
- Clarified that the six architectural questions decide whether a table has conceptual reason to exist, while the physical/boundary questions decide whether it is correctly designed, governed and consumable.

## 2026-07-18 | README | active folder map synchronized

- Replaced the outdated `README.md` content with the current working structure.
- Active root documents are now documented as:
  - `00_TABLES_MARKET_STATE_EVENT_STATE.md`
  - `01_FEATURE_ADMISION_PROCESS.md`
  - `LOCAL_RULES.md`
  - `CHANGELOG.md`
- Clarified that `_01_OBJECTS` is the reserved folder for one file per admitted Information Object.
- Clarified that `archive\` contains historical/superseded/non-active documents, including the previous representation catalog.
- Preserved the rule that this folder is an applied reading surface, not a source of truth or promotion authority.

## 2026-07-17 | information model | family catalog refactored to information objects

- Refactored `01_MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md` from an attribute-by-family inventory into a Market Representation Information Model.
- New structure:

```text
Family
  -> Information Object
    -> phenomenon
    -> hypothesis
    -> physical variables
    -> table location
    -> consumers
    -> coverage status
```

- Preserved the historical filename for continuity while declaring logical name `MARKET_REPRESENTATION_INFORMATION_MODEL_ES` inside the document.
- Clarified the relationship with `00_FEATURE_ADMISION_PROCESS.md`: admission process decides what may enter; information model catalogs what currently exists and what remains pending.


## 2026-07-16 | families | consolidated attribute index added

- Added `MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md`.
- Purpose: consolidate market representation families with the attributes/variables identified across tables `000` through `012`.
- Boundary: marks explicitly which families remain pending for `013-018` instead of treating them as already covered.


## 2026-07-16 | 000-012 | ES audits reformatted with readable blocks

- Reformatted Spanish concise representation readings `000` through `012`.
- Each family field now uses its own fenced `text` block with line breaks for readability:
  - phenomenon;
  - hypothesis;
  - questions;
  - minimum variables;
  - target table;
  - consumers.
- Updated `TABLE_REPRESENTATION_AUDIT_TEMPLATE_ES.md` to enforce the block format.


## 2026-07-16 | 000-012 | ES audits reduced to concise family readings

- Replaced verbose Spanish per-table audits `000` through `012` with concise representation readings.
- New format answers only:
  - market phenomenon represented;
  - scientific hypothesis;
  - questions answered;
  - minimum variables;
  - target table;
  - downstream consumers.
- English originals are left untouched for now; Spanish versions are the preferred human-facing working documents.


## 2026-07-16 | 000-012 | versiones castellanas de auditorias

- Added Spanish copies without deleting the English originals:
  - `TABLES_REPRESENTATION_OF_MARKET_ES.md`
  - `TABLE_REPRESENTATION_AUDIT_TEMPLATE_ES.md`
  - one `*_representation_audit_ES.md` document inside each table folder from `000` through `012`.
- Boundary: English originals remain available as historical/source versions; Spanish copies are the human-facing reading versions.


## 2026-07-16 | 000-012 | representation audits generated

- Created one representation/feature-engineering audit document inside each table folder from `000` through `012`.
- Each audit applies `TABLE_REPRESENTATION_OF_MARKET.md` and `TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Each audit records:
  - table being / non-being;
  - market representation families covered;
  - scientific hypothesis behind variable groups;
  - current physical sample column count from the folder-named physical sample file;
  - leakage/as-of risks;
  - downstream consumption verdict;
  - final audit decision.
- Boundary preserved: these audits do not promote a dataset by themselves; official status remains governed by registry, contracts, validators, manifests and certification matrices.


## 2026-07-16 | feature engineering | representation guardrails added

- Added `TABLES_REPRESENTATION_OF_MARKET.md`.
- Added `TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Updated README and LOCAL_RULES to reflect the renamed `03_TABLES_feature_engineering` role.
- Established the central guardrail:

```text
What do we need to know
to correctly describe
the state of the market
at an instant t?
```

- Established the variable admission rule: every variable must justify why it deserves to exist, which scientific hypothesis it represents, which market representation family it belongs to and which downstream consumer can use it.

## 2026-07-16 | 013 | contract policy registry linked

- Linked the validated `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` to foundations governance artifacts:

```text
contract = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\ohlcv_1m_quote_guarded_dataset_contract_v0_1.md
policy = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\ohlcv_1m_quote_guarded_consumption_policy.md
registry = C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\ohlcv_1m\ohlcv_1m_quote_guarded_registry_entry.yaml
```

- Operational decision: 013 can now be used as a controlled downstream input for candidate 014/018 work when the consumer records `price_view = quote_guarded_1m` and the validation manifest.
- Boundary preserved: this is not unrestricted institutional promotion.

## 2026-07-16 | local governance | table rules added

- Added `03_TABLES_feature_engineering/LOCAL_RULES.md`.
- Established mandatory six-question gate before defining table attributes.
- Fixed the rule that table status must be proven from contracts, manifests,
  validators, tests, status matrices or physical inspection.

## 2026-07-16 | 013 | quote-guarded overlay verified

- Updated `013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md`
  to `operational_reading_v0_2`.
- Verified the promoted/PASS repair manifest under:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

- Recorded focused tests:

```text
7 passed in 2.81s
```

- Final reading:

```text
013 is already materialized as a governed quote-guarded overlay.
013 is not an official full-universe physical replacement tree.
014 and downstream consumers must prove correct overlay consumption.
```

## 2026-07-16 | 013 | physical full-universe failure correction

- Corrected the operational reading of `013_ohlcv_1m_quote_guarded` to separate
  the promoted/PASS LT1B repair overlay from the physical full-universe
  candidate tree.
- Confirmed that `ohlcv_1m_quote_guarded_full_universe_v0_1` remains
  `candidate_not_official` with `full_universe_claim=false`.
- Recorded unresolved `complete_with_failures` summaries for 2015..2020:

```text
2015 failed_tickers = 548
2016 failed_tickers = 571
2017 failed_tickers = 596
2018 failed_tickers = 758
2019 failed_tickers = 744
2020 failed_tickers = 701
```

- Current next action: controlled rematerialization/reconciliation of failed
  2015..2020 ticker-year cases before any clean full-universe claim.


- Generated operational failure manifest: `013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv` with 3,918 failed ticker-year rows for controlled rematerialization.

## 2026-07-16 | 013 | failed-rerun launcher prepared and smoke passed

- Prepared non-destructive delta rerun root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
```

- Generated year task plans for 3,918 failed ticker-year cases across 2015..2020.
- Rewrote task-plan raw input paths from `E:\TSIS\data\ohlcv_1m` to `G:\TSIS\data\ohlcv_1m` for this machine.
- Created governed launcher and monitor:

```text
run_full_rerun_2015_2020.ps1
monitor_full_rerun_2015_2020.ps1
```

- Executed short smoke test on separate smoke root:

```text
completed_tickers = 3
failed_tickers = 0
rows_written = 102,678
repairs_applied = 6
```

- Full rerun not launched by agent because `LONG_RUNNING_OPERATIONS_CONTRACT.md` requires human-visible launch command and monitor before long materialization runs.

## 2026-07-16 | 013 | failed 2015-2020 delta rerun completed

- Completed the controlled delta rerun for previously failed 2015..2020 physical candidate cases.
- Launcher final status:

```text
final_status = complete
exit_code = 0
completed_years = 6/6
```

- Year summaries verified:

```text
2015 complete failed_tickers=0 rows=21,995,617 repairs=627,338
2016 complete failed_tickers=0 rows=20,924,494 repairs=535,880
2017 complete failed_tickers=0 rows=22,619,373 repairs=711,769
2018 complete failed_tickers=0 rows=28,141,678 repairs=1,378,332
2019 complete failed_tickers=0 rows=27,102,457 repairs=1,021,067
2020 complete failed_tickers=0 rows=29,686,897 repairs=1,412,098
```

- Aggregate delta output:

```text
rows_written = 150,470,516
repairs_applied = 5,686,484
failed_tickers = 0
```

- Boundary preserved: this creates a parallel candidate delta root and does not by itself promote `013` or mutate the original `v0_1` tree.
- Next gate: reconcile original `v0_1` plus delta candidate, validate partitions/rows/schema/repair counts, then decide merge/promote path.

## 2026-07-16 | 013 | reconciliation PASS before technical merge

- Added reusable reconciliation script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\reconcile_ohlcv_1m_qg_failed_delta_v0_1.py
```

- Accepted reconciliation run:

```text
run_id = qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
status = PASS
errors = 0
warnings = 0
expected_unique_pairs = 3,918
committed_pairs = 3,918
output_file_missing = 0
schema_checked_files = 600
schema_mismatches = 0
```

- Evidence root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_reconciliation_runs\qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
```

- Decision boundary: reconciliation PASS authorizes preparing a technical `v0_2_candidate` merge; it does not authorize institutional promotion.

## 2026-07-16 | 013 | technical merge candidate v0_2 completed

- Created physical technical merge candidate:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Merge run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z
status = complete
mode = hardlink
errors = 0
original_files_seen = 1,272,004
original_files_linked = 1,228,331
original_files_skipped_expected_delta_pair = 43,673
delta_files_seen = 43,673
delta_files_linked = 43,673
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_build_runs\qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z\final_manifest_merge.json
```

- Boundary: this completes a technical candidate merge only. It does not promote the dataset. Next gate is validation of `v0_2_candidate`.

## 2026-07-16 | 013 | v0_2 candidate validation PASS

- Validated merged candidate tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Validation run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z
status = PASS
errors = 0
warnings = 0
candidate_files_seen = 1,272,004
candidate_files_from_original = 1,228,331
candidate_files_from_delta = 43,673
candidate_files_bad_source = 0
source_missing = 0
expected_delta_pairs_observed = 3,918
schema_checked = 600
schema_mismatches = 0
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\final_manifest_validation.json
```

- Boundary: `v0_2_candidate` is now a validated technical candidate tree and is eligible for promotion review. It is not yet promoted.
