# CRM Real Case Validation v0.1

Status: `architectural_review_v0_1`

Reviewed object: `C:\TSIS_Data\00_CTO_1\01_CANONICAL_REPRESENTATION_MATERIALIZATION`

Reviewed as: `candidate_architecture`

Review date: `2026-07-14`

## Purpose

This file tests whether the CRM framework can explain real TSIS outputs without forcing every table into the same pipeline. The central distinction is:

- A `Canonical Market Representation` is a governed semantic representation of market state/context used for decision or research state.
- An `Enabling Institutional Artifact` is a governed table, manifest, overlay, index, feature surface, boundary table, label table or quality artifact that enables representation work but is not itself canonical market state.

## Evidence Sources Used

- `C:\TSIS_Data\00_CTO_1\05_TABLES\README.md`
- `C:\TSIS_Data\00_CTO_1\05_TABLES\paths.md`
- `C:\TSIS_Data\00_CTO_1\05_TABLES\TABLES_CREATION_process_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`
- Table-specific schema, dataset contract, registry, policy, validator and sample files cited per case.

## Case Classification Summary

| Case | Classification | Current evidence state | Promotion reading |
|---|---|---|---|
| `000 instrument_master` | `Enabling Institutional Artifact` | `validated_for_declared_scope` | Operational for declared scope, not final full lifecycle engine. |
| `002 expected_data_calendar` | `Enabling Institutional Artifact` | `validated_for_declared_scope` | Coverage denominator, not proof of physical presence. |
| `003 dataset_certification_matrix` | `Enabling Institutional Artifact` | `validated_for_declared_scope` | Family-level gate, not row-level validator. |
| `007 event_windows_table` | `Enabling Institutional Artifact` | `validated_for_declared_scope` | Halt-derived event windows only, not all event families. |
| `008 outcomes_table` | `Enabling Institutional Artifact` | `validated_for_declared_scope` | Daily halt-derived labels/y, not feature source or RL reward. |
| `014 master_intraday_bar_table` | `Enabling Institutional Artifact` | `scoped_pilot`; v0.2 quote-guarded candidate not official | Intraday observable surface, not full-universe official state. |
| `015 microstructure_features_table` | `Enabling Institutional Artifact` | v0.1 seed; v0.2 controlled candidate not promoted | Feature surface for event/state design, not ML/RL-ready corpus. |
| `016 market_state_table` | `Canonical Market Representation` target | official v0.1 not materialized; candidates controlled not promoted | Candidate integration proof only. |
| `017 event_state_table` | `Canonical Market Representation` target | official v0.1 not materialized; candidates controlled not promoted | Candidate event-state proof only. |

## 000 - instrument_master

Authority source:

- `verified_current_state`: `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`, section `1. instrument_master`.
- `verified_current_state`: `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`, output row `instrument_master_v0_1`.

Entity represented:

- Temporal instrument identity: instrument id, ticker/name/exchange context, active/inactive state and lineage for the LT1B scope.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it represents identity/universe context required by every downstream representation, but it is not a market state snapshot, event state or feature state.

Justification type:

- Ontological: identifies the entity being observed.
- Governance: prevents ticker-label and survivorship ambiguity.
- Operational: supplies join keys and universe scope.

Materialization decision:

- Materialize compact full-history identity context because downstream contracts cannot be legal without stable instrument identity.

Physical Representation:

- `E:\TSIS\data\data_foundation_outputs\instrument_master\instrument_master_v0_1.parquet` documented in target contract.

Materialization strategy:

- Compact context/full source-history style artifact, not heavy microstructure materialization.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\instrument_master_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\instrument_master_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\instrument_master_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\instrument_master_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\instrument_master_validators.md`

Physical realization:

- Documented path and manifest in target contract: `_instrument_master_manifest_v0_1.json`, `_instrument_master_summary_v0_1.csv`.

Certification evidence:

- Status matrix: rows `4,824`, parquet files `1`, test evidence `Seven-table rerun passed`, status `validated_for_declared_scope`.

Promotion status:

- `validated_for_declared_scope`; not final lifecycle engine and no daily PTI market-cap reconstruction.

Lifecycle status:

- Operational for declared scope.

Architectural traceability:

- Raw/reference identity sources -> instrument master contract/schema/registry/policy/validator -> output manifest -> downstream identity context.

## 002 - expected_data_calendar

Authority source:

- `verified_current_state`: target contract section `4. expected_data_calendar`.
- `verified_current_state`: status matrix output row `expected_data_calendar_v0_1`.

Entity represented:

- Expected dataset-family/ticker/date/session coverage denominator.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it is a denominator and absence diagnostic, not a market state representation.

Justification type:

- Governance: distinguishes expected absence from pathological absence.
- Operational: supplies coverage denominator for validation and consumption gating.

Materialization decision:

- Materialize full expected calendar because downstream quality gates need a denominator.

Physical Representation:

- `E:\TSIS\data\data_foundation_outputs\expected_data_calendar\expected_data_calendar_v0_1`.

Materialization strategy:

- Full context-history denominator.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\expected_data_calendar_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\expected_data_calendar_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\expected_data_calendar_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\expected_data_calendar_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\expected_data_calendar_validators.md`

Physical realization:

- Target contract documents build run id `expected_data_calendar_v0_1_20260630T194807Z`.

Certification evidence:

- Status matrix: rows `29,478,796`, parquet files `88`, test evidence `2026-07-01 targeted contract rerun passed`, status `validated_for_declared_scope`.

Promotion status:

- `validated_for_declared_scope`; not proof of physical presence and must be joined to actual validators.

Lifecycle status:

- Operational coverage denominator.

Architectural traceability:

- Market calendar/instrument scope -> expected calendar contract/schema/registry/policy/validator -> output manifest -> coverage gates.

## 003 - dataset_certification_matrix

Authority source:

- `verified_current_state`: target contract section `13. dataset_certification_matrix`.
- `verified_current_state`: status matrix output row `dataset_certification_matrix_v0_1`.

Entity represented:

- Family-level dataset quality/certification state.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it certifies or gates dataset families; it is not a state vector, feature surface or event state.

Justification type:

- Governance: turns family quality/readiness into a governed table.
- Operational: supports consumer gates and institutional promotion review.

Materialization decision:

- Materialize as compact certification table because consumers need explicit family quality state.

Physical Representation:

- `E:\TSIS\data\data_foundation_outputs\dataset_certification_matrix\dataset_certification_matrix_v0_1.parquet`.

Materialization strategy:

- Compact governance matrix.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\dataset_certification_matrix_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\dataset_certification_matrix_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\dataset_certification_matrix_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\dataset_certification_matrix_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\dataset_certification_matrix_validators.md`

Physical realization:

- Target contract documents path, manifest, summary and build run id `dataset_certification_matrix_v0_1_20260622T154116Z`.

Certification evidence:

- Status matrix: rows `13`, parquet files `1`, test evidence `Seven-table rerun passed`, status `validated_for_declared_scope`.

Promotion status:

- `validated_for_declared_scope`; family-level only, not ticker/date row validation.

Lifecycle status:

- Operational governance artifact.

Architectural traceability:

- Family status matrix -> schema/contract/registry/policy/validator -> certification matrix parquet -> consumer gates.

## 007 - event_windows_table

Authority source:

- `verified_current_state`: target contract section `12b. event_windows_table`.
- `verified_current_state`: status matrix output row `event_windows_table_v0_1`.
- `documented_target`: Event Research Part III governs event windows conceptually.

Entity represented:

- Governed windows around source events: prior session, pre-event, event-response, same-session and next-session boundaries.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it defines temporal/legal boundaries for features and outcomes. It is not itself market state.

Justification type:

- Scientific: prevents private/inconsistent event-window definitions.
- Governance: enforces leakage boundaries.
- Operational: supplies window ids for feature/outcome builders.

Materialization decision:

- Materialize for halt-derived event windows under declared LT1B/calendar-covered scope.

Physical Representation:

- `E:\TSIS\data\data_foundation_outputs\event_windows_table\event_windows_table_v0_1.parquet`.

Materialization strategy:

- Full declared research population for halt-derived events, not all event families.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\event_windows_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\event_windows_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\event_windows_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\event_windows_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\event_windows_table_validators.md`

Physical realization:

- Target contract lists manifest `_event_windows_table_manifest_v0_1.json`, summary and materializer `scripts/materialize_event_windows_table.py`.

Certification evidence:

- Status matrix: rows `214,112`, isolated rerun passed, status `validated_for_declared_scope`.
- Sample file: `C:\TSIS_Data\00_CTO_1\05_TABLES\007_event_windows_table\PARQUET_CONTENT_SAMPLE.md`, fields include candidate/gate flags such as `valid_for_microstructure_feature_candidate`, `valid_for_ml_feature_candidate`, `valid_for_rl_state_component_candidate`.

Promotion status:

- `validated_for_declared_scope`; halts only, not all event families and not primary ML/RL/execution truth.

Lifecycle status:

- Operational event-window boundary table for declared halt scope.

Architectural traceability:

- Halts/instrument/calendar -> event windows contract/schema/registry/policy/validator -> event_windows parquet -> feature/outcome/state builders.

## 008 - outcomes_table

Authority source:

- `verified_current_state`: target contract section `12c. outcomes_table`.
- `verified_current_state`: status matrix output row `outcomes_table_v0_1`.
- Market/state composition contract separates X from y.

Entity represented:

- Post-event labels/outcomes for governed event windows and price views.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: outcomes are y/labels after the decision. They must remain separated from state/features.

Justification type:

- Scientific: enables outcome research.
- Governance: prevents leakage by keeping y separate from X.
- Operational: supports ML/strategy labels under allowed gates.

Materialization decision:

- Materialize daily next-session outcomes for halt-derived event windows and three daily price views.

Physical Representation:

- `E:\TSIS\data\data_foundation_outputs\outcomes_table\outcomes_table_v0_1.parquet`.

Materialization strategy:

- Full declared halt-derived daily outcome population, not intraday execution outcomes or RL rewards.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\outcomes_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\outcomes_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\outcomes_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\outcomes_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\outcomes_table_validators.md`

Physical realization:

- Target contract lists manifest `_outcomes_table_manifest_v0_1.json`, summary and materializer `scripts/materialize_outcomes_table.py`.

Certification evidence:

- Status matrix: rows `128,388`, isolated rerun passed, status `validated_for_declared_scope`.
- Sample file: `C:\TSIS_Data\00_CTO_1\05_TABLES\008_outcomes_table\PARQUET_CONTENT_SAMPLE.md` explicitly marks outcome fields as prohibited pre-event features and requiring feature/label separation.

Promotion status:

- `validated_for_declared_scope`; daily labels only, not intraday execution outcome, not RL reward and not all event families.

Lifecycle status:

- Operational label/outcome table for declared halt-derived daily scope.

Architectural traceability:

- Event windows -> outcome builder -> outcomes schema/contract/registry/policy/validator -> y table -> ML/strategy labels only under gates.

## 014 - master_intraday_bar_table

Authority source:

- `documented_target`: target contract section `6. master_intraday_bar_table`.
- `verified_current_state`: status matrix output row `master_intraday_bar_table_v0_1`.
- `controlled_candidate`: quote-guarded v0.2 candidate evidence in target/status contracts.

Entity represented:

- Intraday OHLCV/VWAP/session/minute-index observable surface, usually 1m.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it is an intraday observable surface used by state/event builders. It is not a complete market state.

Justification type:

- Representation: gives legal intraday observables.
- Operational: supports event detection, opening drive research, premarket/regular/afterhours context.

Materialization decision:

- v0.1 exists as scoped pilot.
- v0.2 quote-guarded path exists as scoped candidate, not official/full-universe.
- Wider/full-scope materialization requires denominator manifest, candidate status, tests and promotion review.

Physical Representation:

- v0.1: `E:\TSIS\data\data_foundation_outputs\master_intraday_bar_table\master_intraday_bar_table_v0_1`.
- v0.2 candidate: `E:\TSIS\data\data_foundation_outputs\master_intraday_bar_table\master_intraday_bar_table_v0_2_candidate_quote_guarded\data.parquet`.

Materialization strategy:

- Scoped pilot and quote-guarded candidate path; no full-universe claim until gates pass.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\master_intraday_bar_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\master_intraday_bar_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\master_intraday_bar_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\master_intraday_bar_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\master_intraday_bar_table_validators.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md`

Physical realization:

- v0.1 materialized as scoped pilot.
- v0.2 quote-guarded candidate has scoped E-root candidate evidence and validator passed, but `full_universe_claim=false`.

Certification evidence:

- Status matrix: v0.1 rows `175,252`, parquet files `14`, status `scoped_pilot`; v0.2 quote-guarded candidate status `scoped_candidate_materialized_not_official` in target/status addenda.
- Sample file: `C:\TSIS_Data\00_CTO_1\05_TABLES\014\PARQUET_CONTENT_SAMPLE.md`, note on `full_universe_claim` remaining false.

Promotion status:

- v0.1 scoped pilot; v0.2 controlled/scoped candidate not official; not execution truth.

Lifecycle status:

- Active candidate expansion loop; v0.1 should not be silently reused as full-universe.

Architectural traceability:

- Raw `ohlcv_1m` + quote-guarded repair manifest/overlay -> master intraday candidate -> validators/manifests -> downstream event/state builders under candidate gates.

## 015 - microstructure_features_table

Authority source:

- `documented_target`: target contract section `7. microstructure_features_table`.
- `verified_current_state`: status matrix rows `microstructure_features_table_v0_1` and `microstructure_features_table_v0_2_candidate_controlled_25_per_role`.
- `documented_target`: microstructure multi-window materialization plan.

Entity represented:

- Window-level microstructure features: spread, locked/crossed, tape intensity, odd lots, liquidity, quality, quote/trade texture and derived measures.

Canonical Market Representation:

- No. Classification: `Enabling Institutional Artifact`.
- Reason: it is a feature surface feeding state design. It is not state by itself.

Justification type:

- Scientific: captures microstructure texture around event windows.
- Representation: provides governed feature inputs.
- Operational: supplies candidate features for state builders under declared windows.

Materialization decision:

- v0.1 seed/smoke exists.
- v0.2 controlled candidate exists for halt event-window samples.
- Wider work should be event-window/multi-window candidate, not blind full-universe tick-level expansion.

Physical Representation:

- v0.1: `E:\TSIS\data\data_foundation_outputs\microstructure_features_table\microstructure_features_table_v0_1`.
- v0.2 candidate: `E:\TSIS\data\data_foundation_outputs\microstructure_features_table\microstructure_features_table_v0_2_candidate_controlled_25_per_role`.

Materialization strategy:

- Selective event windows / controlled candidate materialization.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\microstructure_features_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\microstructure_features_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\microstructure_features_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\microstructure_features_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\microstructure_features_table_validators.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md`

Physical realization:

- v0.1 has one-row seed/smoke proof.
- v0.2 controlled candidate has 50-row candidate materialization and visual evidence.

Certification evidence:

- Status matrix: v0.1 status `seed_state_sample`; v0.2 status `controlled_candidate_not_promoted`.
- Materialization plan current status: `controlled_50_window_candidate_materialized_and_tested_not_promoted`; `full_universe_claim_granted: false`.

Promotion status:

- Not ML/RL-ready, not core-backtest-ready, not execution-ready, not institutional microstructure training corpus.

Lifecycle status:

- Controlled candidate path exists; official wider corpus still pending gates.

Architectural traceability:

- Event windows -> quote/trade sources with root-state lineage -> candidate window manifest -> microstructure materializer -> validators/visual evidence -> state design candidates.

## 016 - market_state_table

Authority source:

- `documented_target`: `market_state_event_state_composition_contract_v0_1.md`.
- `documented_target`: `market_state_coverage_and_lookback_policy_v0_1.md`.
- `documented_target`: `state_builder_contract_v0_1.md`.
- `verified_current_state`: status matrix rows for `market_state_table_v0_1_candidate_microstructure_halt_controlled` and intraday quote-guarded candidate.

Entity represented:

- Market state row: identity, decision timestamp, state horizon, observable components, quality, lineage and gates under legal cutoff.

Canonical Market Representation:

- Yes, as target. It is the canonical market-state representation layer for decision-context rows.

Justification type:

- Ontological: state snapshot at decision time.
- Scientific: makes market context auditable.
- Governance: separates X from y, state from signal/strategy/outcome/reward/execution.
- Operational: supplies candidate state context for event/research builders.

Materialization decision:

- Official `market_state_table_v0_1` is not materialized.
- Controlled candidates may exist for integration proof but cannot be promoted without leakage/formula/timestamp/role/builder validators and raw-to-consumption lineage.

Physical Representation:

- Controlled halt candidate: `E:\TSIS\data\data_foundation_outputs\market_state_table\market_state_table_v0_1_candidate_microstructure_halt_controlled`.
- Controlled intraday quote-guarded candidate under test run: `C:\TSIS_Data\tests\test_runs\2026-07-05\market_state_intraday_quote_guarded_candidate_v0_1`.

Materialization strategy:

- Controlled candidate first; future official candidate must obey declared coverage/lookback policy and component lineage.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\market_state_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\market_state_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\market_state_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\market_state_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\market_state_table_validators.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md`

Physical realization:

- Controlled candidate builder implemented.
- Official general builder/materialization not complete.

Certification evidence:

- Composition contract current readiness: official `market_state_table_v0_1` is not materialized; controlled candidate is materialized as `controlled_candidate_not_promoted`.
- Status matrix: controlled halt candidate rows `50`, test evidence passed, ML/RL candidate rows `0`.
- State builder contract: `controlled_candidate_builder_implemented = true`, `market_state_table_materialized = false`.

Promotion status:

- `contract_defined_not_materialized` for official target; `controlled_candidate_not_promoted` for candidates.

Lifecycle status:

- Target contract stack complete for declared scope; official materialization pending.

Architectural traceability:

- Market Representation/state contracts -> eligible observables and formula/timestamp/role contracts -> raw-to-consumption lineage -> state builder config/manifest -> candidate output -> validators/status matrix.

## 017 - event_state_table

Authority source:

- `documented_target`: `market_state_event_state_composition_contract_v0_1.md`.
- `documented_target`: `state_builder_contract_v0_1.md`.
- `verified_current_state`: status matrix rows for `event_state_table_v0_1_candidate_microstructure_halt_controlled` and intraday quote-guarded event-state candidate.

Entity represented:

- Event-scoped state view: market_state anchored to an event/window, decision timestamp, role and legal cutoff.

Canonical Market Representation:

- Yes, as target. It is the event-scoped canonical state representation for a decision/review role.

Justification type:

- Scientific: makes event decisions auditable.
- Governance: prevents each strategy/research pipeline from inventing private event state.
- Operational: provides event-context candidate surface for pattern discovery and downstream research.

Materialization decision:

- Official `event_state_table_v0_1` is not materialized.
- Controlled candidates exist as integration proof only.

Physical Representation:

- Controlled halt candidate: `E:\TSIS\data\data_foundation_outputs\event_state_table\event_state_table_v0_1_candidate_microstructure_halt_controlled`.
- Controlled intraday candidate under test run: `C:\TSIS_Data\tests\test_runs\2026-07-05\event_state_intraday_1m_quote_guarded_controlled`.

Materialization strategy:

- Controlled event-scoped candidates first; official materialization after state gates, event windows, lineage, validators and promotion evidence.

Institutional contracts:

- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas\outputs\event_state_table_schema_contract.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry\dataset_contracts\event_state_table_dataset_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies\event_state_table_consumption_policy.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry\outputs\event_state_table_registry_entry.yaml`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators\outputs\event_state_table_validators.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\market_state_event_state_composition_contract_v0_1.md`
- `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`

Physical realization:

- Controlled candidates exist.
- Official target not materialized.

Certification evidence:

- Composition contract current readiness: official `event_state_table_v0_1` is not materialized; controlled candidate is `controlled_candidate_not_promoted`.
- Status matrix: controlled halt candidate rows `50`, test evidence passed, ML/RL candidate rows `0`.
- State builder contract: `event_state_table_materialized = false`.

Promotion status:

- `contract_defined_not_materialized` for official target; `controlled_candidate_not_promoted` for candidates.

Lifecycle status:

- Target contract stack complete for declared scope; official materialization pending.

Architectural traceability:

- Event definition/window -> market_state candidate/official future row -> event_state builder with role/cutoff -> manifest/validators -> candidate output -> consumption gates.

## Real Case Conclusion

The CRM framework survives these cases only if it accepts multiple artifact roles:

1. `000`, `002`, `003`, `007`, `008`, `014` and `015` are not canonical market states. They are enabling institutional artifacts with different authority, promotion and consumption semantics.
2. `016` and `017` are the real canonical state targets, but their official forms are not materialized. Current materializations are controlled candidates and must not be promoted by language.
3. The framework must distinguish `contract_defined_not_materialized`, `controlled_candidate_not_promoted`, `validated_for_declared_scope` and `institutional`. A parquet or sample does not imply promotion.
4. The central verifiable change CRM can add is a mandatory mapping from semantic authority to physical artifact and current promotion status before materialization or promotion claims are allowed.

