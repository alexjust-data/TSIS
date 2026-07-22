# Graph Report - C:\TSIS_Data  (2026-06-29)

## Corpus Check
- 96 files · ~72,643 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 130 nodes · 200 edges · 16 communities
- Extraction: 62% EXTRACTED · 38% INFERRED · 0% AMBIGUOUS · INFERRED: 76 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `362a031e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Market Event State|Market Event State]]
- [[_COMMUNITY_Short Context|Short Context]]
- [[_COMMUNITY_Short Context|Short Context]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Intraday Microstructure|Intraday Microstructure]]
- [[_COMMUNITY_Intraday Microstructure|Intraday Microstructure]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Reference Identity|Reference Identity]]
- [[_COMMUNITY_Reference Identity|Reference Identity]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]
- [[_COMMUNITY_Schema Stack|Schema Stack]]

## God Nodes (most connected - your core abstractions)
1. `market_state_table` - 23 edges
2. `Data Foundation Outputs Target Contract` - 18 edges
3. `Data Foundation Outputs Status Matrix` - 18 edges
4. `E:/TSIS/data/data_foundation_outputs` - 18 edges
5. `event_state_table` - 15 edges
6. `master_intraday_bar_table` - 10 edges
7. `microstructure_features_table` - 10 edges
8. `halts_table` - 10 edges
9. `news_context_table` - 10 edges
10. `short_context_table` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Market State Event State Build Loop` --rationale_for--> `event_state_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `Market State Event State Build Loop` --rationale_for--> `market_state_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `instrument_master validator` --conceptually_related_to--> `instrument_master`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/instrument_master_validators.md → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `market_calendar validator` --conceptually_related_to--> `market_calendar`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/market_calendar_validators.md → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
- `corporate_actions_table validator` --conceptually_related_to--> `corporate_actions_table`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/corporate_actions_table_validators.md → 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Data Foundation Output Table Contract Stack** — data_foundation_outputs_contract_target_contract, data_foundation_outputs_contract_status_matrix, data_foundation_outputs_filesystem_data_foundation_outputs [EXTRACTED 1.00]
- **Market State Event State Composition Stack** — data_foundation_outputs_contract_market_state_event_state_composition, data_foundation_outputs_contract_market_state_event_state_build_loop, data_foundation_outputs_table_market_state_table, data_foundation_outputs_table_event_state_table [INFERRED 0.85]

## Communities (16 total, 0 thin omitted)

### Community 0 - "Market Event State"
Cohesion: 0.16
Nodes (16): event_state_table consumption_policy, market_state_table consumption_policy, Market State Event State Build Loop, Market State Event State Composition, event_state_table dataset_contract, market_state_table dataset_contract, E:/TSIS/data/data_foundation_outputs/event_state_table, E:/TSIS/data/data_foundation_outputs/market_state_table (+8 more)

### Community 1 - "Short Context"
Cohesion: 0.22
Nodes (11): short_context_table consumption_policy, Short Sale Constraints Target Contract, Data Foundation Outputs Status Matrix, short_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/short_context_table, short_context_table registry, Short Sale Constraints Acquisition Runbook, short_context_table schema (+3 more)

### Community 2 - "Short Context"
Cohesion: 0.25
Nodes (9): expected_data_calendar consumption_policy, expected_data_calendar dataset_contract, E:/TSIS/data/data_foundation_outputs, E:/TSIS/data/data_foundation_outputs/expected_data_calendar, E:/TSIS/data/data_foundation_outputs/short_sale_constraints_table, expected_data_calendar registry, expected_data_calendar schema, expected_data_calendar (+1 more)

### Community 3 - "Schema Stack"
Cohesion: 0.29
Nodes (8): corporate_actions_table consumption_policy, Data Foundation Outputs Target Contract, corporate_actions_table dataset_contract, E:/TSIS/data/data_foundation_outputs/corporate_actions_table, corporate_actions_table registry, corporate_actions_table schema, corporate_actions_table, corporate_actions_table validator

### Community 4 - "Intraday Microstructure"
Cohesion: 0.29
Nodes (8): master_intraday_bar_table consumption_policy, master_intraday_bar_table dataset_contract, E:/TSIS/data/data_foundation_outputs/master_intraday_bar_table, Master Intraday Wider Scope Plan, master_intraday_bar_table registry, master_intraday_bar_table schema, master_intraday_bar_table, master_intraday_bar_table validator

### Community 5 - "Intraday Microstructure"
Cohesion: 0.29
Nodes (8): microstructure_features_table consumption_policy, microstructure_features_table dataset_contract, E:/TSIS/data/data_foundation_outputs/microstructure_features_table, Microstructure Multi Window Plan, microstructure_features_table registry, microstructure_features_table schema, microstructure_features_table, microstructure_features_table validator

### Community 6 - "Schema Stack"
Cohesion: 0.33
Nodes (7): dataset_certification_matrix consumption_policy, dataset_certification_matrix dataset_contract, E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix, dataset_certification_matrix registry, dataset_certification_matrix schema, dataset_certification_matrix, dataset_certification_matrix validator

### Community 7 - "Schema Stack"
Cohesion: 0.33
Nodes (7): event_windows_table consumption_policy, event_windows_table dataset_contract, E:/TSIS/data/data_foundation_outputs/event_windows_table, event_windows_table registry, event_windows_table schema, event_windows_table, event_windows_table validator

### Community 8 - "Schema Stack"
Cohesion: 0.33
Nodes (7): fundamentals_asof_table consumption_policy, fundamentals_asof_table dataset_contract, E:/TSIS/data/data_foundation_outputs/fundamentals_asof_table, fundamentals_asof_table registry, fundamentals_asof_table schema, fundamentals_asof_table, fundamentals_asof_table validator

### Community 9 - "Schema Stack"
Cohesion: 0.33
Nodes (7): halts_table consumption_policy, halts_table dataset_contract, E:/TSIS/data/data_foundation_outputs/halts_table, halts_table registry, halts_table schema, halts_table, halts_table validator

### Community 10 - "Reference Identity"
Cohesion: 0.33
Nodes (7): instrument_master consumption_policy, instrument_master dataset_contract, E:/TSIS/data/data_foundation_outputs/instrument_master, instrument_master registry, instrument_master schema, instrument_master, instrument_master validator

### Community 11 - "Reference Identity"
Cohesion: 0.33
Nodes (7): market_calendar consumption_policy, market_calendar dataset_contract, E:/TSIS/data/data_foundation_outputs/market_calendar, market_calendar registry, market_calendar schema, market_calendar, market_calendar validator

### Community 12 - "Schema Stack"
Cohesion: 0.33
Nodes (7): master_daily_table consumption_policy, master_daily_table dataset_contract, E:/TSIS/data/data_foundation_outputs/master_daily_table, master_daily_table registry, master_daily_table schema, master_daily_table, master_daily_table validator

### Community 13 - "Schema Stack"
Cohesion: 0.33
Nodes (7): news_context_table consumption_policy, news_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/news_context_table, news_context_table registry, news_context_table schema, news_context_table, news_context_table validator

### Community 14 - "Schema Stack"
Cohesion: 0.33
Nodes (7): outcomes_table consumption_policy, outcomes_table dataset_contract, E:/TSIS/data/data_foundation_outputs/outcomes_table, outcomes_table registry, outcomes_table schema, outcomes_table, outcomes_table validator

### Community 15 - "Schema Stack"
Cohesion: 0.33
Nodes (7): regime_context_table consumption_policy, regime_context_table dataset_contract, E:/TSIS/data/data_foundation_outputs/regime_context_table, regime_context_table registry, regime_context_table schema, regime_context_table, regime_context_table validator

## Knowledge Gaps
- **72 isolated node(s):** `instrument_master schema`, `instrument_master dataset_contract`, `instrument_master consumption_policy`, `instrument_master validator`, `market_calendar schema` (+67 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Data Foundation Outputs Target Contract` connect `Schema Stack` to `Market Event State`, `Short Context`, `Short Context`, `Intraday Microstructure`, `Intraday Microstructure`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Reference Identity`, `Reference Identity`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Schema Stack`?**
  _High betweenness centrality (0.277) - this node is a cross-community bridge._
- **Why does `Data Foundation Outputs Status Matrix` connect `Short Context` to `Market Event State`, `Short Context`, `Schema Stack`, `Intraday Microstructure`, `Intraday Microstructure`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Reference Identity`, `Reference Identity`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Schema Stack`?**
  _High betweenness centrality (0.277) - this node is a cross-community bridge._
- **Why does `market_state_table` connect `Market Event State` to `Short Context`, `Schema Stack`, `Intraday Microstructure`, `Intraday Microstructure`, `Schema Stack`, `Schema Stack`, `Schema Stack`, `Reference Identity`, `Reference Identity`, `Schema Stack`, `Schema Stack`, `Schema Stack`?**
  _High betweenness centrality (0.234) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `market_state_table` (e.g. with `Market State Event State Build Loop` and `dataset_certification_matrix`) actually correct?**
  _`market_state_table` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `E:/TSIS/data/data_foundation_outputs` (e.g. with `E:/TSIS/data/data_foundation_outputs/corporate_actions_table` and `E:/TSIS/data/data_foundation_outputs/dataset_certification_matrix`) actually correct?**
  _`E:/TSIS/data/data_foundation_outputs` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `event_state_table` (e.g. with `Market State Event State Build Loop` and `E:/TSIS/data/data_foundation_outputs/event_state_table`) actually correct?**
  _`event_state_table` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `instrument_master schema`, `instrument_master dataset_contract`, `instrument_master consumption_policy` to the rest of the system?**
  _72 weakly-connected nodes found - possible documentation gaps or missing edges._