# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 217 files · ~194,352 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1227 nodes · 2737 edges · 71 communities (69 shown, 2 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 99 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Strategy Event Builder
- Quote-Guarded Market State
- Short Context Builder
- Quote-Guarded Event State
- Intraday Outcomes Builder
- Event Candidate Validation
- Scanner Candidates V1
- Scanner Candidates V2
- Scanner Candidates V3
- Fundamentals As-Of Builder
- News Context Builder
- Output Table Schemas
- Output Registry Contracts
- State Builder Governance
- Intraday Scanner Builder
- Quote-Guarded Master Bars
- Microstructure Features Builder
- Output Dataset Contracts
- Daily Event Windows
- Intraday Strategy Events
- Intraday Event Windows
- Master Intraday Bars
- Regime Context Builder
- Repair Sample Builder
- State Consumption Policies
- Intraday Regime Builder
- Market State Builder
- Certification Matrix Builder
- Event State Builder
- Quote-Guarded Preflight
- Output Table Validators
- Event Windows Builder
- Outcomes Table Builder
- Presession Population Builder
- Microstructure Controlled Tests
- Expected Calendar Builder
- Master Daily Builder
- Scanner Definition Governance
- Split-Normalized Builder
- Daily Adjusted Builder
- Halts Table Builder
- Candidate Validator Tests
- Corporate Actions Builder
- Daily Return Labels
- Regime Context Tests
- Short Context Tests
- Market Calendar Builder
- Event State Contract Tests
- Market State Contract Tests
- Instrument Master Builder
- Daily Scanner Orchestrator
- Intraday Scanner Orchestrator
- Certification Matrix Tests
- Event Windows Contract Tests
- Fundamentals Contract Tests
- News Context Tests
- Corporate Actions Tests
- Expected Calendar Tests
- Halts Contract Tests
- Instrument Master Tests
- Market Calendar Tests
- Master Daily Tests
- Master Intraday Tests
- Candidate Manifest Tests
- Microstructure Contract Tests
- Outcomes Contract Tests
- Scanner Denominator Governance
- Intraday Scanner Tests
- Split Manifest Tests
- Outcomes Consumption Boundary
- Corporate Actions Registry

## God Nodes (most connected - your core abstractions)
1. `materialize_microstructure_features_table()` - 23 edges
2. `build()` - 19 edges
3. `materialize_news_context_table()` - 19 edges
4. `materialize_short_context_table()` - 18 edges
5. `materialize()` - 17 edges
6. `build()` - 17 edges
7. `materialize_master_intraday_bar_table()` - 17 edges
8. `materialize()` - 17 edges
9. `build()` - 16 edges
10. `build()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Daily Strategy Candidate Events Table Schema` --shares_data_with--> `Event Windows Table Schema`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/daily_strategy_candidate_events_table_schema_contract.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
- `Microstructure Features Table Schema` --shares_data_with--> `Event Windows Table Schema`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md
- `Market State Table Schema` --shares_data_with--> `Fundamentals As-Of Table Schema`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md
- `Intraday Scanner Candidates Table Schema` --shares_data_with--> `Master Intraday Bar Table Schema`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/intraday_scanner_candidates_table_schema_contract.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md
- `Market State Table Schema` --shares_data_with--> `News Context Table Schema`  [INFERRED]
  01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md → 01_TSIS_DATA_FOUNDATION/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **** — 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_instrument_master_schema_contract_instrument_master_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_market_calendar_schema_contract_market_calendar_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_expected_data_calendar_schema_contract_expected_data_calendar_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_dataset_certification_matrix_schema_contract_dataset_certification_matrix_schema [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_daily_scanner_candidates_table_schema_contract_daily_scanner_candidates_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_daily_strategy_candidate_events_table_schema_contract_daily_strategy_candidate_events_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_event_windows_table_schema_contract_event_windows_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_event_state_table_schema_contract_event_state_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_outcomes_table_schema_contract_outcomes_schema [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_market_state_table_schema_contract_market_state_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_fundamentals_asof_table_schema_contract_fundamentals_asof_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_news_context_table_schema_contract_news_context_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_short_context_table_schema_contract_short_context_schema, 01_tsis_data_foundation_01_foundations_canonical_schemas_outputs_regime_context_table_schema_contract_regime_context_schema [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_daily_scanner_candidates_table_dataset_contract_v0_1_daily_scanner_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_market_state_table_dataset_contract_v0_1_market_state_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_event_state_table_dataset_contract_v0_1_event_state_dataset_contract [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_event_windows_table_dataset_contract_v0_1_event_windows_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_microstructure_features_table_dataset_contract_v0_1_microstructure_features_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_outcomes_table_dataset_contract_v0_1_outcomes_dataset_contract [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_market_state_table_dataset_contract_v0_1_market_state_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_fundamentals_asof_table_dataset_contract_v0_1_fundamentals_asof_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_news_context_table_dataset_contract_v0_1_news_context_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_short_context_table_dataset_contract_v0_1_short_context_dataset_contract, 01_tsis_data_foundation_01_foundations_contract_registry_dataset_contracts_regime_context_table_dataset_contract_v0_1_regime_context_dataset_contract [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_instrument_master_registry_entry_instrument_master_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_market_calendar_registry_entry_market_calendar_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_expected_data_calendar_registry_entry_expected_data_calendar_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_dataset_certification_matrix_registry_entry_dataset_certification_registry_entry [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_halts_table_registry_entry_halts_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_event_windows_table_registry_entry_event_windows_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_event_state_table_registry_entry_event_state_registry_entry [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_data_consumption_policies_market_state_table_consumption_policy_market_state_consumption_policy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_master_daily_table_consumption_policy_master_daily_consumption_policy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_master_intraday_bar_table_consumption_policy_master_intraday_consumption_policy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_news_context_table_consumption_policy_news_context_consumption_policy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_short_context_table_consumption_policy_short_context_consumption_policy, 01_tsis_data_foundation_01_foundations_data_consumption_policies_regime_context_table_consumption_policy_regime_context_consumption_policy [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_module_contracts_outputs_daily_scanner_candidates_table_target_contract_v0_1_daily_scanner_target_v0_1, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_daily_scanner_candidates_table_target_contract_v0_2_daily_scanner_target_v0_2, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_daily_scanner_candidates_table_target_contract_v0_3_daily_scanner_target_v0_3, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_daily_scanner_candidates_table_target_contract_v0_3_base_eligible_in_play_strategy_overlay_separation [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_01_foundations_module_contracts_outputs_event_candidate_tables_contract_v0_1_event_candidate_tables_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_event_candidate_table_validators_contract_v0_1_event_candidate_validator_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_event_research_design_contract_v0_1_event_research_design_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_market_state_event_state_composition_contract_v0_1_state_composition_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_market_state_event_state_build_loop_runbook_v0_1_state_build_loop_runbook [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_market_state_table_registry_entry_market_state_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_master_daily_table_registry_entry_master_daily_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_master_intraday_bar_table_registry_entry_master_intraday_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_microstructure_features_table_registry_entry_microstructure_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_news_context_table_registry_entry_news_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_regime_context_table_registry_entry_regime_registry_entry, 01_tsis_data_foundation_01_foundations_dataset_registry_outputs_short_context_table_registry_entry_short_registry_entry [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_builder_contract_v0_1_state_builder_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_observable_eligibility_contract_v0_1_observable_eligibility_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_derived_observables_formula_contract_v0_1_derived_observables_formula_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_decision_timestamp_policy_v0_1_decision_timestamp_policy, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_snapshot_roles_contract_v0_1_snapshot_roles_contract, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_raw_to_consumption_lineage_contract_v0_1_raw_to_consumption_lineage_contract [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1_intraday_quote_guarded_lineage, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1_intraday_event_windows_lineage, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1_intraday_event_state_lineage, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1_intraday_outcomes_lineage [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_01_foundations_module_contracts_outputs_scanner_framework_and_definitions_contract_v0_1_scanner_framework_v0_1, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_scanner_framework_and_definitions_contract_v0_2_scanner_framework_v0_2, 01_tsis_data_foundation_01_foundations_module_contracts_outputs_scanner_framework_and_definitions_contract_v0_3_scanner_framework_v0_3, 01_tsis_data_foundation_01_foundations_validators_outputs_daily_scanner_candidates_table_validators_daily_scanner_validators [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_01_foundations_validators_outputs_instrument_master_validators_instrument_master_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_market_calendar_validators_market_calendar_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_expected_data_calendar_validators_expected_data_calendar_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_master_daily_table_validators_master_daily_validators [INFERRED 0.95]
- **** — 01_tsis_data_foundation_01_foundations_validators_outputs_event_windows_table_validators_event_windows_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_market_state_table_validators_market_state_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_event_state_table_validators_event_state_validators, 01_tsis_data_foundation_01_foundations_validators_outputs_outcomes_table_validators_outcomes_validators [INFERRED 0.95]
- **** — 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_base_in_play_universe_scanner_v0_2_base_in_play_universe_scanner, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_das_research_profile_v0_2_das_research_profile, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_dollar_volume_tradability_profile_v0_2_dollar_volume_tradability_profile, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_base_eligible_smallcap_denominator_v0_3_base_eligible_smallcap_denominator, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_in_play_momentum_candidate_denominator_v0_3_in_play_momentum_candidate_denominator [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_trade_station_like_scanner_v0_1_trade_station_like_scanner_v0_1, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_trade_station_like_profile_v0_2_trade_station_like_profile_v0_2, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_trade_station_like_profile_v0_3_trade_station_like_profile_v0_3 [INFERRED 0.95]
- **** — 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_percent_change_profile_v0_2_percent_change_profile, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_relative_volume_profile_v0_2_relative_volume_profile, 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_trade_station_like_profile_v0_2_trade_station_like_profile_v0_2 [EXTRACTED 1.00]
- **** — 01_tsis_data_foundation_configs_data_foundation_outputs_scanner_definitions_readme_scanner_definitions_guide, 01_tsis_data_foundation_tests_data_foundation_outputs_readme_data_foundation_output_test_contract, 01_tsis_data_foundation_tests_data_foundation_outputs_readme_independent_adversarial_validation [INFERRED 0.95]

## Communities (71 total, 2 thin omitted)

### Community 0 - "Strategy Event Builder"
Cohesion: 0.17
Nodes (35): _add_minutes(), _as_posix(), _bool_series(), _bool_value(), build(), _common_row(), _daily_event_row(), _date_str() (+27 more)

### Community 1 - "Quote-Guarded Market State"
Cohesion: 0.15
Nodes (32): _bool(), build(), _build_state_rows(), _iso_z(), _json_bundle(), _load_intraday_frame(), main(), _nullable_float() (+24 more)

### Community 2 - "Short Context Builder"
Cohesion: 0.20
Nodes (31): _copy_output(), _create_short_context_source_output(), _fetch_dict(), _fetch_one(), _finra_interest_sql(), _finra_volume_sql(), _json_default(), _load_manifest() (+23 more)

### Community 3 - "Quote-Guarded Event State"
Cohesion: 0.16
Nodes (28): build(), _iso(), _json_bundle(), main(), parse_args(), Any, DataFrame, Namespace (+20 more)

### Community 4 - "Intraday Outcomes Builder"
Cohesion: 0.17
Nodes (27): build(), _iso(), _json_bundle(), main(), parse_args(), _pct(), Any, DataFrame (+19 more)

### Community 5 - "Event Candidate Validation"
Cohesion: 0.26
Nodes (28): _add(), _allowed_policies(), _check_consumer_gates(), _check_daily(), _check_definition(), _check_identity(), _check_intraday(), _check_lineage() (+20 more)

### Community 6 - "Scanner Candidates V1"
Cohesion: 0.19
Nodes (26): _as_posix(), build(), _build_sql(), _default_output_root(), main(), parse_args(), Any, DuckDBPyConnection (+18 more)

### Community 7 - "Scanner Candidates V2"
Cohesion: 0.19
Nodes (26): _as_posix(), build(), _build_sql(), _default_output_root(), main(), parse_args(), Any, DuckDBPyConnection (+18 more)

### Community 8 - "Scanner Candidates V3"
Cohesion: 0.19
Nodes (26): _as_posix(), build(), _build_sql(), _default_output_root(), main(), parse_args(), Any, DuckDBPyConnection (+18 more)

### Community 9 - "Fundamentals As-Of Builder"
Cohesion: 0.21
Nodes (27): _create_source_inventory_table(), _family_pattern(), _fetch_dict(), _fetch_one(), _json_default(), _load_manifest(), main(), materialize() (+19 more)

### Community 10 - "News Context Builder"
Cohesion: 0.23
Nodes (26): _create_source_inventory(), _fetch_dict(), _fetch_one(), _json_default(), _load_manifest(), main(), materialize_news_context_table(), _materialize_output() (+18 more)

### Community 11 - "Output Table Schemas"
Cohesion: 0.12
Nodes (26): Corporate Actions Table Schema, Daily Scanner Candidates Table Schema, Scanner Candidate Defines Where to Look, Daily Strategy Candidate Events Table Schema, Dataset Certification Matrix Schema, Event State Table Schema, Event Windows Table Schema, Expected Data Calendar Schema (+18 more)

### Community 12 - "Output Registry Contracts"
Cohesion: 0.11
Nodes (26): Market state table registry entry, Master daily table registry entry, Master intraday bar table registry entry, Microstructure features table registry entry, News context table registry entry, Outcomes table registry entry, Regime context table registry entry, Short context table registry entry (+18 more)

### Community 13 - "State Builder Governance"
Cohesion: 0.11
Nodes (26): No blind full-universe materialization, Master intraday bar table wider-scope materialization plan, Microstructure features multi-window materialization plan, Scanner framework and definitions contract v0.1, Scanner framework and definitions contract v0.2, Scanner framework and definitions contract v0.3, Short-sale constraints data acquisition runbook, Short-sale constraints table target contract (+18 more)

### Community 14 - "Intraday Scanner Builder"
Cohesion: 0.20
Nodes (25): _as_posix(), _build(), _build_sql(), _default_output_root(), main(), _minute_files(), _month_keys(), _parse_date() (+17 more)

### Community 15 - "Quote-Guarded Master Bars"
Cohesion: 0.16
Nodes (24): _bool_series(), build(), _build_rows(), _close_enough(), _find_shards(), _iso(), main(), _merged_scope() (+16 more)

### Community 16 - "Microstructure Features Builder"
Cohesion: 0.26
Nodes (25): _event_id(), _instrument_for_window(), _iso(), _load_manifest(), _locate_quotes_file(), _locate_trades_file(), main(), materialize_microstructure_features_table() (+17 more)

### Community 17 - "Output Dataset Contracts"
Cohesion: 0.11
Nodes (25): Daily Scanner Candidates Dataset Contract, Event State Dataset Contract, Event Windows Dataset Contract, Fundamentals As-Of Dataset Contract, Halts Table Dataset Contract, Instrument Master Dataset Contract, Intraday Scanner Candidates Dataset Contract, Market Calendar Dataset Contract (+17 more)

### Community 18 - "Daily Event Windows"
Cohesion: 0.18
Nodes (23): _as_posix(), build(), _build_windows(), _date(), _iso(), main(), parse_args(), Any (+15 more)

### Community 19 - "Intraday Strategy Events"
Cohesion: 0.17
Nodes (23): _bool(), build(), build_source_candidates(), _dollar_value(), _iso_z(), main(), parse_args(), Any (+15 more)

### Community 20 - "Intraday Event Windows"
Cohesion: 0.19
Nodes (23): build(), _build_windows(), _date(), _iso(), main(), parse_args(), Any, DataFrame (+15 more)

### Community 21 - "Master Intraday Bars"
Cohesion: 0.23
Nodes (24): _base_frame(), _build_ids(), _load_manifest(), main(), materialize_master_intraday_bar_table(), parse_args(), _path_for_json(), _price_integrity_state() (+16 more)

### Community 22 - "Regime Context Builder"
Cohesion: 0.24
Nodes (24): _copy_output(), _create_aggregates(), _json_default(), _load_manifest(), main(), materialize(), parse_args(), _path_for_json() (+16 more)

### Community 23 - "Repair Sample Builder"
Cohesion: 0.18
Nodes (21): _bool_series(), build(), _build_output(), _close_enough(), _iso(), main(), parse_args(), Any (+13 more)

### Community 24 - "State Consumption Policies"
Cohesion: 0.13
Nodes (22): Instrument Master Consumption Policy, Intraday Scanner Candidates Consumption Policy, Market Calendar Consumption Policy, Component Cutoffs Compose Legal State, Market State Consumption Policy, Master Daily Consumption Policy, Master Intraday Bar Consumption Policy, Microstructure Features Consumption Policy (+14 more)

### Community 25 - "Intraday Regime Builder"
Cohesion: 0.24
Nodes (21): _build_cross_session_features(), _daily_normalized_features(), _daily_raw_features(), FeaturesConfig, _iter_normalized_files(), _iter_ticker_dirs(), _load_ticker_frames(), main() (+13 more)

### Community 26 - "Market State Builder"
Cohesion: 0.22
Nodes (20): _component_state(), contract_status(), _json_bundle(), main(), materialize_market_state_candidate(), parse_args(), Any, DataFrame (+12 more)

### Community 27 - "Certification Matrix Builder"
Cohesion: 0.23
Nodes (19): _artifact_present(), _canonical_family(), _clean_cell(), _count_casepack_docs(), _count_files(), _find_visual_pack(), _gate_from_verdict(), _json_array() (+11 more)

### Community 28 - "Event State Builder"
Cohesion: 0.24
Nodes (19): contract_status(), _json_bundle(), main(), materialize_event_state_candidate(), parse_args(), Any, DataFrame, Namespace (+11 more)

### Community 29 - "Quote-Guarded Preflight"
Cohesion: 0.20
Nodes (17): _as_posix(), _load_json(), main(), parse_args(), _path_from_config(), Any, Namespace, Path (+9 more)

### Community 30 - "Output Table Validators"
Cohesion: 0.17
Nodes (18): Event state table validators, Post-event state is not decision-safe, Event windows table validators, Expected data calendar validators, Expected denominator is not observed presence, Fundamentals as-of table validators, Halts table validators, Instrument master validators (+10 more)

### Community 31 - "Event Windows Builder"
Cohesion: 0.27
Nodes (16): _build_windows(), _date_or_none(), _hash_parts(), _iso_or_none(), _load_manifest(), _localize_et_to_utc(), main(), materialize_event_windows_table() (+8 more)

### Community 32 - "Outcomes Table Builder"
Cohesion: 0.32
Nodes (16): _add_outcome_semantics(), _build_joined_frame(), _dataset_glob(), _hash_parts(), _load_manifest(), main(), materialize_outcomes_table(), _norm() (+8 more)

### Community 33 - "Presession Population Builder"
Cohesion: 0.28
Nodes (15): _atomic_write_json(), main(), materialize(), _parquet_glob(), _parser(), Any, ArgumentParser, date (+7 more)

### Community 34 - "Microstructure Controlled Tests"
Cohesion: 0.27
Nodes (15): _load_manifest(), _parquet_files(), Any, DataFrame, Path, Timestamp, _read_candidate_frame(), _sha256_partitioned_parquet_tree() (+7 more)

### Community 35 - "Expected Calendar Builder"
Cohesion: 0.37
Nodes (13): _dataset_glob(), _family_values_sql(), _load_manifest(), main(), materialize_expected_data_calendar(), parse_args(), Any, Namespace (+5 more)

### Community 36 - "Master Daily Builder"
Cohesion: 0.40
Nodes (13): _dataset_glob(), _file_inventory(), _load_manifest(), main(), materialize_master_daily_table(), parse_args(), Any, Namespace (+5 more)

### Community 37 - "Scanner Definition Governance"
Cohesion: 0.24
Nodes (13): First-cross timing requires intraday data, Intraday in-play momentum candidate denominator v0.1, Percent-change profile v0.2, Top-N ranking requires a minimum motion threshold, Scanner candidate is not market state, Scanner definitions guide, Daily RVOL is not intraday volume acceleration, Relative-volume profile v0.2 (+5 more)

### Community 38 - "Split-Normalized Builder"
Cohesion: 0.32
Nodes (12): _find_split_file(), _load_optional_parquet(), main(), MaterializationConfig, materialize_case(), _output_path(), parse_args(), DataFrame (+4 more)

### Community 39 - "Daily Adjusted Builder"
Cohesion: 0.36
Nodes (12): _find_action_file(), _iter_daily_files(), _iter_ticker_dirs(), _load_optional_parquet(), main(), MaterializationConfig, materialize_ticker(), _output_path() (+4 more)

### Community 40 - "Halts Table Builder"
Cohesion: 0.32
Nodes (12): _build_event_states(), _hash_parts(), main(), materialize_halts_table(), _non_empty_string(), _norm(), Any, DataFrame (+4 more)

### Community 41 - "Candidate Validator Tests"
Cohesion: 0.46
Nodes (12): _payload(), Path, _run_validator(), test_daily_event_candidate_blocks_intraday_claim_without_source(), test_daily_event_candidate_blocks_outcome_inline(), test_daily_event_candidate_good_fixture_passes(), test_event_candidate_validator_contract_check(), test_intraday_event_candidate_blocks_future_cutoff_and_open_bar() (+4 more)

### Community 42 - "Corporate Actions Builder"
Cohesion: 0.42
Nodes (11): _load_manifest(), main(), materialize_corporate_actions_table(), parse_args(), Any, Namespace, Path, _require() (+3 more)

### Community 43 - "Daily Return Labels"
Cohesion: 0.36
Nodes (11): _build_labels(), _iter_adjusted_files(), _iter_ticker_dirs(), LabelsConfig, main(), materialize_ticker(), _output_path(), parse_args() (+3 more)

### Community 44 - "Regime Context Tests"
Cohesion: 0.39
Nodes (11): _connect(), _dict(), _glob(), _manifest(), DuckDBPyConnection, Path, _scalar(), test_regime_context_gate_semantics_and_role_counts() (+3 more)

### Community 45 - "Short Context Tests"
Cohesion: 0.39
Nodes (11): _connect(), _dict(), _glob(), _manifest(), DuckDBPyConnection, Path, _scalar(), test_short_context_duplicate_and_missing_family_guards() (+3 more)

### Community 46 - "Market Calendar Builder"
Cohesion: 0.36
Nodes (10): _load_source(), main(), materialize_market_calendar(), parse_args(), Any, DataFrame, Namespace, Path (+2 more)

### Community 47 - "Event State Contract Tests"
Cohesion: 0.33
Nodes (8): _config_with_fixture(), Path, test_event_state_builder_fixture_sample(), test_event_state_builder_rejects_inline_label(), test_event_state_builder_rejects_post_event_review_as_ml_feature(), test_event_state_builder_skeleton_contract_check(), test_event_state_candidate_materializes_from_market_state_candidate(), test_event_state_contract_stack_exists()

### Community 48 - "Market State Contract Tests"
Cohesion: 0.33
Nodes (8): _config_with_fixture(), Path, test_market_state_builder_fixture_sample(), test_market_state_builder_rejects_future_asof(), test_market_state_builder_rejects_prohibited_feature(), test_market_state_builder_skeleton_contract_check(), test_market_state_candidate_materializes_from_microstructure(), test_market_state_contract_stack_exists()

### Community 49 - "Instrument Master Builder"
Cohesion: 0.40
Nodes (9): build_instrument_master(), main(), parse_args(), Any, Namespace, Path, _require_path(), _sha256() (+1 more)

### Community 50 - "Daily Scanner Orchestrator"
Cohesion: 0.36
Nodes (7): Add-JsonLine(), ConvertTo-Arg(), Get-DriveFreeGbForPath(), Get-ProcessPerfSnapshot(), Invoke-BuilderForWindow(), Write-JsonAtomic(), Write-OperationHeartbeat()

### Community 51 - "Intraday Scanner Orchestrator"
Cohesion: 0.36
Nodes (7): Add-JsonLine(), ConvertTo-Arg(), Get-DriveFreeGbForPath(), Get-ProcessPerfSnapshot(), Invoke-BuilderForWindow(), Write-JsonAtomic(), Write-OperationHeartbeat()

### Community 52 - "Certification Matrix Tests"
Cohesion: 0.44
Nodes (9): _frame(), _manifest(), DataFrame, Path, _source_summary_rows(), test_dataset_certification_matrix_evidence_links_are_real(), test_dataset_certification_matrix_manifest_hashes_and_contract_links(), test_dataset_certification_matrix_reconciles_to_source_matrix_and_gate_rules() (+1 more)

### Community 53 - "Event Windows Contract Tests"
Cohesion: 0.40
Nodes (9): _dataset_glob(), _frame(), _manifest(), DataFrame, Path, test_event_windows_manifest_hashes_contracts_and_sources(), test_event_windows_schema_scope_counts_and_gates(), test_event_windows_source_reconciliation() (+1 more)

### Community 54 - "Fundamentals Contract Tests"
Cohesion: 0.40
Nodes (9): _frame(), _glob(), _manifest(), DataFrame, Path, test_fundamentals_asof_manifest_hashes_contracts_and_sources(), test_fundamentals_asof_schema_counts_quality_and_gates(), test_fundamentals_asof_source_reconciliation_and_family_counts() (+1 more)

### Community 55 - "News Context Tests"
Cohesion: 0.47
Nodes (9): _dict(), _glob(), _manifest(), Path, _sql(), test_news_context_attribution_and_year_partitions(), test_news_context_manifest_hashes_contracts_and_sources(), test_news_context_schema_counts_quality_and_gates() (+1 more)

### Community 56 - "Corporate Actions Tests"
Cohesion: 0.44
Nodes (8): _frame(), _manifest(), DataFrame, Path, test_corporate_actions_manifest_hashes_contracts_and_source_fingerprints(), test_corporate_actions_payload_integrity_rules(), test_corporate_actions_reconciles_counts_to_source_roots(), test_corporate_actions_schema_lineage_and_manifest_counts()

### Community 57 - "Expected Calendar Tests"
Cohesion: 0.44
Nodes (8): _dataset_glob(), _manifest(), Path, _scalar(), test_expected_data_calendar_key_window_and_family_rules(), test_expected_data_calendar_manifest_tree_hashes_and_contract_links(), test_expected_data_calendar_reconciles_to_instrument_calendar_intersection(), test_expected_data_calendar_schema_lineage_and_counts()

### Community 58 - "Halts Contract Tests"
Cohesion: 0.50
Nodes (8): _frame(), _manifest(), DataFrame, Path, test_halts_table_manifest_hashes_contracts_and_source(), test_halts_table_quality_gates_and_known_anomalies(), test_halts_table_schema_counts_and_lineage(), test_halts_table_source_reconciliation()

### Community 59 - "Instrument Master Tests"
Cohesion: 0.47
Nodes (8): _frame(), _manifest(), DataFrame, Path, test_instrument_master_identity_and_operational_filters(), test_instrument_master_manifest_paths_hashes_and_contract_links(), test_instrument_master_reconciles_to_lt1b_source_universe(), test_instrument_master_schema_lineage_and_manifest_counts()

### Community 60 - "Market Calendar Tests"
Cohesion: 0.47
Nodes (8): _frame(), _manifest(), DataFrame, Path, test_market_calendar_manifest_paths_hashes_and_contract_links(), test_market_calendar_schema_lineage_and_manifest_counts(), test_market_calendar_session_contract_rules(), test_market_calendar_source_and_known_session_edges()

### Community 61 - "Master Daily Tests"
Cohesion: 0.53
Nodes (8): _dataset_glob(), _file_inventory(), _manifest(), Path, test_master_daily_manifest_tree_hashes_and_contract_links(), test_master_daily_price_view_semantics_metrics_and_source_inventory(), test_master_daily_reconciles_expected_denominator_and_rows_by_price_view(), test_master_daily_schema_counts_price_views_and_flags()

### Community 62 - "Master Intraday Tests"
Cohesion: 0.47
Nodes (8): _dataset_glob(), _manifest(), Path, test_master_intraday_manifest_tree_hashes_and_contract_links(), test_master_intraday_price_view_formula_integrity(), test_master_intraday_quality_gate_invariants(), test_master_intraday_reconciles_split_source_and_rows_by_price_view(), test_master_intraday_schema_scope_price_views_and_flags()

### Community 63 - "Candidate Manifest Tests"
Cohesion: 0.47
Nodes (8): DataFrame, Path, _run_builder(), test_microstructure_candidate_manifest_builds_from_event_windows_denominator(), test_microstructure_candidate_manifest_contract_stack_exists(), test_microstructure_candidate_manifest_does_not_touch_official_v0_1(), test_microstructure_candidate_manifest_preserves_leakage_semantics(), test_microstructure_candidate_materializer_writes_candidate_only()

### Community 64 - "Microstructure Contract Tests"
Cohesion: 0.44
Nodes (8): _dataset_glob(), _frame(), _manifest(), DataFrame, Path, test_microstructure_manifest_hashes_and_contract_links(), test_microstructure_recomputes_seed_metrics_from_raw_sources(), test_microstructure_schema_scope_and_seed_counts()

### Community 65 - "Outcomes Contract Tests"
Cohesion: 0.44
Nodes (8): _frame(), _manifest(), DataFrame, Path, test_outcomes_manifest_hashes_contracts_and_sources(), test_outcomes_price_view_grain_and_source_reconciliation(), test_outcomes_return_math_labels_and_leakage_guards(), test_outcomes_schema_counts_quality_and_gates()

### Community 66 - "Scanner Denominator Governance"
Cohesion: 0.29
Nodes (8): Intraday scanner candidates table validators, Base eligible small-cap denominator v0.3, Eligibility is not in-play selection, Base in-play universe scanner v0.2, Broad in-play discovery scanner v0.1, DAS research profile v0.2, Dollar-volume tradability profile v0.2, In-play momentum candidate denominator v0.3

### Community 67 - "Intraday Scanner Tests"
Cohesion: 0.54
Nodes (7): _fixture_sources(), _minute_rows(), DataFrame, Path, test_intraday_scanner_detects_first_cross_segments_and_gates(), _write_json(), _write_minute_file()

### Community 68 - "Split Manifest Tests"
Cohesion: 0.73
Nodes (5): Path, test_all_existing_manifest_uses_partition_direct_scan(), test_split_affected_manifest_uses_split_ticker_direct_partitions(), _touch_minute_file(), _write_splits()

## Knowledge Gaps
- **28 isolated node(s):** `Halts Table Schema`, `Microstructure Features Table Schema`, `Corporate Actions Dataset Contract`, `Instrument Master Dataset Contract`, `Intraday Scanner Candidates Dataset Contract` (+23 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Halts Table Schema`, `Microstructure Features Table Schema`, `Corporate Actions Dataset Contract` to the rest of the system?**
  _28 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Quote-Guarded Market State` be split into smaller, more focused modules?**
  _Cohesion score 0.14795008912655971 - nodes in this community are weakly interconnected._
- **Should `Output Table Schemas` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `Output Registry Contracts` be split into smaller, more focused modules?**
  _Cohesion score 0.11076923076923077 - nodes in this community are weakly interconnected._
- **Should `State Builder Governance` be split into smaller, more focused modules?**
  _Cohesion score 0.1076923076923077 - nodes in this community are weakly interconnected._
- **Should `Output Dataset Contracts` be split into smaller, more focused modules?**
  _Cohesion score 0.10666666666666667 - nodes in this community are weakly interconnected._
- **Should `State Consumption Policies` be split into smaller, more focused modules?**
  _Cohesion score 0.1341991341991342 - nodes in this community are weakly interconnected._