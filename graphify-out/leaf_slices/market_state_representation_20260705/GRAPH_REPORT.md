# Graph Report - C:\TSIS_Data  (2026-07-05)

## Corpus Check
- 70 files · ~160,446 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 80 nodes · 351 edges · 9 communities (7 shown, 2 thin omitted)
- Extraction: 1% EXTRACTED · 99% INFERRED · 0% AMBIGUOUS · INFERRED: 348 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f94bc013`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Graph Cluster 7|Graph Cluster 7]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]

## God Nodes (most connected - your core abstractions)
1. `Market State Builder` - 64 edges
2. `Outcomes Separated From State` - 51 edges
3. `Quote-Guarded Intraday Path` - 44 edges
4. `Representation Layer` - 42 edges
5. `ML/RL/AlphaEvolve Production Disabled` - 40 edges
6. `Intraday Controlled Path` - 33 edges
7. `Event Candidate Tables` - 28 edges
8. `Canonical State` - 27 edges
9. `Daily Controlled Path` - 21 edges
10. `CHANGELOG` - 10 edges

## Surprising Connections (you probably didn't know these)
- `materialize_intraday_scanner_candidates_table_v0_1` --defines_or_references--> `Market State Builder`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_intraday_scanner_candidates_table_v0_1.py → 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
- `materialize_master_intraday_quote_guarded_candidate_scoped` --defines_or_references--> `Market State Builder`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py → 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
- `test_master_intraday_quote_guarded_candidate_scoped_builder` --defines_or_references--> `Market State Builder`  [INFERRED]
  01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_intraday_quote_guarded_candidate_scoped_builder.py → 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
- `test_daily_strategy_event_windows_candidate_builder` --defines_or_references--> `Outcomes Separated From State`  [INFERRED]
  01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_strategy_event_windows_candidate_builder.py → 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
- `materialize_daily_scanner_candidates_table` --defines_or_references--> `Canonical State`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_daily_scanner_candidates_table.py → 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Market State v3 Route 20260705** — tsis_market_state_concept_canonical_state, tsis_market_state_concept_representation_layer, tsis_market_state_concept_market_state_builder, tsis_market_state_concept_event_candidate_tables, tsis_market_state_concept_quote_guarded_intraday_path, tsis_market_state_concept_raw_to_consumption_lineage, tsis_market_state_concept_daily_controlled_path, tsis_market_state_concept_intraday_controlled_path, tsis_market_state_concept_outcomes_separated, tsis_market_state_concept_ml_rl_alphaevolve_disabled [INFERRED 0.90]

## Communities (9 total, 2 thin omitted)

### Community 0 - "Quote Guarded Intraday"
Cohesion: 0.16
Nodes (17): README, scanner_table_and_contract_map_v0_1, strategy_scanner_overlay_policy_v0_1, GRAPHIFY_REFRESH_QUEUE, intraday_1m_strategy_candidate_events_table_schema_contract, state_derived_observables_formula_contract_v0_1, materialize_daily_scanner_candidates_table_v0_2, materialize_daily_scanner_candidates_table_v0_3 (+9 more)

### Community 1 - "Quote Guarded Intraday"
Cohesion: 0.23
Nodes (16): 05_07_2026, market_state_representation_contract_v0_1, daily_strategy_candidate_events_table_schema_contract, state_canonical_vs_representation_layer_contract_v0_1, state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1, materialize_daily_strategy_event_windows_candidate, materialize_intraday_1m_strategy_event_windows_candidate, materialize_strategy_candidate_events_table (+8 more)

### Community 2 - "Quote Guarded Intraday"
Cohesion: 0.27
Nodes (13): AlphaEnvolve, intraday_scanner_candidates_contract_v0_1, scanner_base_universe_and_profiles_contract_v0_2, scanner_candidate_selection_architecture_v0_1, scanner_to_market_state_promotion_path_v0_1, market_state_representation_source_file_map_v0_1, data_foundation_outputs_target_contract_v0_1, state_decision_timestamp_policy_v0_1 (+5 more)

### Community 3 - "Quote Guarded Intraday"
Cohesion: 0.22
Nodes (9): market_state_tables_status_and_operating_map_2026_07_01_v3, scanner_base_and_in_play_momentum_contract_v0_3, data_foundation_outputs_status_matrix_v0_1, event_candidate_table_validators_contract_v0_1, event_candidate_tables_contract_v0_1, materialize_daily_scanner_candidates_table, materialize_event_state_intraday_quote_guarded_candidate, materialize_market_state_intraday_quote_guarded_candidate (+1 more)

### Community 4 - "Quote Guarded Intraday"
Cohesion: 0.25
Nodes (8): market_state_tables_status_and_operating_map_2026_07_01, market_state_tables_status_and_operating_map_2026_07_01_v2, state_builder_contract_v0_1, materialize_master_intraday_quote_guarded_candidate_scoped, test_intraday_1m_strategy_event_windows_candidate_builder, test_master_intraday_quote_guarded_candidate_sample_builder, test_master_intraday_quote_guarded_candidate_scoped_builder, Quote-Guarded Intraday Path

### Community 5 - "Quote Guarded Intraday"
Cohesion: 0.25
Nodes (8): CHANGELOG, state_raw_to_consumption_lineage_contract_v0_1, state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1, state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1, state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1, state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1, CHANGELOG, Raw To Consumption Lineage

### Community 6 - "Quote Guarded Intraday"
Cohesion: 0.29
Nodes (7): GRAPHIFY_REFRESH_QUEUE, master_intraday_bar_table_quote_guarded_candidate_contract_v0_1, materialize_intraday_1m_event_outcomes_candidate, materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded, materialize_master_intraday_quote_guarded_candidate_sample, test_market_state_intraday_quote_guarded_candidate_builder, Intraday Controlled Path

## Knowledge Gaps
- **7 isolated node(s):** `scanner_definitions_trade_station_vs_broad_discovery_v0_1`, `test_daily_scanner_candidates_table_builder`, `test_daily_scanner_candidates_table_builder_v0_2`, `test_daily_scanner_candidates_table_builder_v0_3`, `test_intraday_scanner_candidates_table_builder_v0_1` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Market State Builder` connect `Quote Guarded Intraday` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`?**
  _High betweenness centrality (0.364) - this node is a cross-community bridge._
- **Why does `Outcomes Separated From State` connect `Quote Guarded Intraday` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Why does `Quote-Guarded Intraday Path` connect `Quote Guarded Intraday` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `Market State Builder` (e.g. with `05_07_2026` and `AlphaEnvolve`) actually correct?**
  _`Market State Builder` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 50 inferred relationships involving `Outcomes Separated From State` (e.g. with `05_07_2026` and `AlphaEnvolve`) actually correct?**
  _`Outcomes Separated From State` has 50 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `Quote-Guarded Intraday Path` (e.g. with `AlphaEnvolve` and `market_state_tables_status_and_operating_map_2026_07_01`) actually correct?**
  _`Quote-Guarded Intraday Path` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Representation Layer` (e.g. with `05_07_2026` and `AlphaEnvolve`) actually correct?**
  _`Representation Layer` has 40 INFERRED edges - model-reasoned connections that need verification._