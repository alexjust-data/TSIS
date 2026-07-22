# Graph Report - C:\TSIS_Data  (2026-07-05)

## Corpus Check
- 157 files · ~163,552 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 210 nodes · 259 edges · 40 communities (18 shown, 22 thin omitted)
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 88 edges (avg confidence: 0.88)
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
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Graph Cluster 19|Graph Cluster 19]]
- [[_COMMUNITY_Graph Cluster 20|Graph Cluster 20]]
- [[_COMMUNITY_Graph Cluster 21|Graph Cluster 21]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Event Candidates|Event Candidates]]
- [[_COMMUNITY_Event Candidates|Event Candidates]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Quote Guarded Intraday|Quote Guarded Intraday]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Validation Stack|Validation Stack]]
- [[_COMMUNITY_Event Candidates|Event Candidates]]

## God Nodes (most connected - your core abstractions)
1. `Data Foundation Outputs Target` - 53 edges
2. `event_state_table` - 22 edges
3. `market_state_table` - 22 edges
4. `Data Foundation Outputs Status Matrix` - 20 edges
5. `E:/TSIS/data/data_foundation_outputs` - 20 edges
6. `event_windows_table` - 14 edges
7. `master_intraday_bar_table` - 12 edges
8. `outcomes_table` - 11 edges
9. `daily_strategy_candidate_events_table` - 9 edges
10. `intraday_1m_strategy_candidate_events_table` - 9 edges

## Surprising Connections (you probably didn't know these)
- `materialize_master_intraday_quote_guarded_candidate_sample` --builds_or_validates--> `master_intraday_bar_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_sample.py → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `materialize_master_intraday_quote_guarded_candidate_scoped` --builds_or_validates--> `master_intraday_bar_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `preflight_master_intraday_quote_guarded_candidate` --builds_or_validates--> `master_intraday_bar_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/preflight_master_intraday_quote_guarded_candidate.py → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `materialize_strategy_candidate_events_table` --builds_or_validates--> `daily_strategy_candidate_events_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/materialize_strategy_candidate_events_table.py → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `validate_event_candidate_tables` --builds_or_validates--> `daily_strategy_candidate_events_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/scripts/validate_event_candidate_tables.py → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Data Foundation State Candidate Stack 20260705** — tsis_contract_data_foundation_outputs_target, tsis_contract_data_foundation_outputs_status, tsis_table_market_state_table, tsis_table_event_state_table, tsis_table_outcomes_table [INFERRED 0.90]

## Communities (40 total, 22 thin omitted)

### Community 0 - "Quote Guarded Intraday"
Cohesion: 0.10
Nodes (26): materialize_event_state_intraday_quote_guarded_candidate, materialize_market_state_intraday_quote_guarded_candidate, Market State Intraday Quote-Guarded Candidate, Master Intraday Quote-Guarded Candidate, event_state_table consumption_policy, market_state_table consumption_policy, event_state_table dataset_contract, market_state_table dataset_contract (+18 more)

### Community 1 - "Quote Guarded Intraday"
Cohesion: 0.08
Nodes (25): Data Foundation Outputs Target, daily_scanner_candidates_table_target_contract_v0_1, daily_scanner_candidates_table_target_contract_v0_2, daily_scanner_candidates_table_target_contract_v0_3, data_foundation_outputs_status_matrix_v0_1, data_foundation_outputs_target_contract_v0_1, event_research_design_contract_v0_1, intraday_scanner_candidates_table_target_contract_v0_1 (+17 more)

### Community 2 - "Quote Guarded Intraday"
Cohesion: 0.16
Nodes (15): materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded, materialize_strategy_candidate_events_table, validate_event_candidate_tables, E:/TSIS/data/data_foundation_outputs, event_candidate_table_validators_contract_v0_1, event_candidate_tables_contract_v0_1, E:/TSIS/data/data_foundation_outputs/daily_strategy_candidate_events_table, E:/TSIS/data/data_foundation_outputs/event_state_table (+7 more)

### Community 3 - "Quote Guarded Intraday"
Cohesion: 0.15
Nodes (13): materialize_intraday_1m_event_outcomes_candidate, Event State Intraday Quote-Guarded Candidate, Intraday 1m Event Windows Candidate, Intraday 1m Strategy Candidate Events Quote-Guarded, Outcomes Intraday 1m Quote-Guarded Candidate, outcomes_table consumption_policy, outcomes_table dataset_contract, state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1 (+5 more)

### Community 4 - "Quote Guarded Intraday"
Cohesion: 0.17
Nodes (12): materialize_daily_strategy_event_windows_candidate, materialize_intraday_1m_strategy_event_windows_candidate, Daily Strategy Candidate Events Controlled, Daily Strategy Event Windows Candidate, event_windows_table consumption_policy, event_windows_table dataset_contract, state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1, state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1 (+4 more)

### Community 5 - "Quote Guarded Intraday"
Cohesion: 0.20
Nodes (10): materialize_master_intraday_quote_guarded_candidate_sample, materialize_master_intraday_quote_guarded_candidate_scoped, preflight_master_intraday_quote_guarded_candidate, master_intraday_bar_table consumption_policy, master_intraday_bar_table dataset_contract, E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table, master_intraday_bar_table registry, master_intraday_bar_table schema (+2 more)

### Community 6 - "Validation Stack"
Cohesion: 0.20
Nodes (10): short_context_table consumption_policy, Data Foundation Outputs Status Matrix, short_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/short_context_table, E:/TSIS/data/data_foundation_outputs/short_sale_constraints_table, short_context_table registry, short_context_table schema, short_context_table (+2 more)

### Community 7 - "Validation Stack"
Cohesion: 0.29
Nodes (7): corporate_actions_table consumption_policy, corporate_actions_table dataset_contract, E:/TSIS/data/data_foundation_outputs/corporate_actions_table, corporate_actions_table registry, corporate_actions_table schema, corporate_actions_table, corporate_actions_table validator

### Community 8 - "Validation Stack"
Cohesion: 0.29
Nodes (7): dataset_certification_matrix consumption_policy, dataset_certification_matrix dataset_contract, E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix, dataset_certification_matrix registry, dataset_certification_matrix schema, dataset_certification_matrix, dataset_certification_matrix validator

### Community 9 - "Validation Stack"
Cohesion: 0.29
Nodes (7): expected_data_calendar consumption_policy, expected_data_calendar dataset_contract, E:/TSIS/data/data_foundation_outputs/expected_data_calendar, expected_data_calendar registry, expected_data_calendar schema, expected_data_calendar, expected_data_calendar validator

### Community 10 - "Validation Stack"
Cohesion: 0.29
Nodes (7): fundamentals_asof_table consumption_policy, fundamentals_asof_table dataset_contract, E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table, fundamentals_asof_table registry, fundamentals_asof_table schema, fundamentals_asof_table, fundamentals_asof_table validator

### Community 11 - "Validation Stack"
Cohesion: 0.29
Nodes (7): halts_table consumption_policy, halts_table dataset_contract, E:/TSIS/data/data_foundation_outputs/halts_table, halts_table registry, halts_table schema, halts_table, halts_table validator

### Community 12 - "Validation Stack"
Cohesion: 0.29
Nodes (7): instrument_master consumption_policy, instrument_master dataset_contract, E:/TSIS/data/data_foundation_outputs/instrument_master, instrument_master registry, instrument_master schema, instrument_master, instrument_master validator

### Community 13 - "Validation Stack"
Cohesion: 0.29
Nodes (7): market_calendar consumption_policy, market_calendar dataset_contract, E:/TSIS/data/data_foundation_outputs/market_calendar, market_calendar registry, market_calendar schema, market_calendar, market_calendar validator

### Community 14 - "Validation Stack"
Cohesion: 0.29
Nodes (7): master_daily_table consumption_policy, master_daily_table dataset_contract, E:/TSIS/data/data_foundation_outputs/master_daily_table, master_daily_table registry, master_daily_table schema, master_daily_table, master_daily_table validator

### Community 15 - "Validation Stack"
Cohesion: 0.29
Nodes (7): microstructure_features_table consumption_policy, microstructure_features_table dataset_contract, E:/TSIS/data/data_foundation_outputs/microstructure_features_table, microstructure_features_table registry, microstructure_features_table schema, microstructure_features_table, microstructure_features_table validator

### Community 16 - "Validation Stack"
Cohesion: 0.29
Nodes (7): news_context_table consumption_policy, news_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/news_context_table, news_context_table registry, news_context_table schema, news_context_table, news_context_table validator

### Community 17 - "Validation Stack"
Cohesion: 0.29
Nodes (7): regime_context_table consumption_policy, regime_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/regime_context_table, regime_context_table registry, regime_context_table schema, regime_context_table, regime_context_table validator

## Knowledge Gaps
- **143 isolated node(s):** `instrument_master schema`, `instrument_master dataset_contract`, `instrument_master registry`, `instrument_master consumption_policy`, `instrument_master validator` (+138 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Data Foundation Outputs Target` connect `Quote Guarded Intraday` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`?**
  _High betweenness centrality (0.465) - this node is a cross-community bridge._
- **Why does `Data Foundation Outputs Status Matrix` connect `Validation Stack` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`, `Validation Stack`?**
  _High betweenness centrality (0.216) - this node is a cross-community bridge._
- **Why does `event_windows_table` connect `Quote Guarded Intraday` to `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Quote Guarded Intraday`, `Validation Stack`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `event_state_table` (e.g. with `materialize_event_state_intraday_quote_guarded_candidate` and `Event State Intraday Quote-Guarded Candidate`) actually correct?**
  _`event_state_table` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `market_state_table` (e.g. with `materialize_market_state_intraday_quote_guarded_candidate` and `Market State Intraday Quote-Guarded Candidate`) actually correct?**
  _`market_state_table` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `E:/TSIS/data/data_foundation_outputs` (e.g. with `E:/TSIS/data/data_foundation_outputs/corporate_actions_table` and `E:/TSIS/data/data_foundation_outputs/daily_strategy_candidate_events_table`) actually correct?**
  _`E:/TSIS/data/data_foundation_outputs` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `instrument_master schema`, `instrument_master dataset_contract`, `instrument_master registry` to the rest of the system?**
  _143 weakly-connected nodes found - possible documentation gaps or missing edges._