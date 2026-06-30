# Graph Report - C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS  (2026-06-18)

## Corpus Check
- Corpus is ~21,561 words - fits in a single context window. You may not need a graph.

## Summary
- 438 nodes · 614 edges · 19 communities
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.81)
- Token cost: 22,684 input · 15,540 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `Breakout` - 16 edges
2. `Short Imbalance Model` - 16 edges
3. `Event Library` - 14 edges
4. `Event Engine Model` - 12 edges
5. `Candidate Features` - 12 edges
6. `Long Plays Playbook` - 12 edges
7. `Long Imbalance Model` - 12 edges
8. `TSIS Lab Functional Chain` - 11 edges
9. `Short Plays` - 11 edges
10. `First Red Day` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Strategy Research` --semantically_similar_to--> `Strategy Research`  [INFERRED] [semantically similar]
  11_SQUEEZE_RESEARCH/README.md → 04_STRATEGY_RESEARCH/README.md
- `Execution Models` --semantically_similar_to--> `Execution Models`  [INFERRED] [semantically similar]
  04_STRATEGY_RESEARCH/README.md → 08_EXECUTION_MODELS/README.md
- `AlphaEvolve OpenEvolve Event Proposals` --semantically_similar_to--> `AlphaEvolve Agent`  [INFERRED] [semantically similar]
  00_EVENT_LIBRARY/99_EXPERIMENTAL/README.md → revision.md
- `Promotion or Rejection Notes` --semantically_similar_to--> `Promotion Gates`  [INFERRED] [semantically similar]
  04_STRATEGY_RESEARCH/README.md → 10_EVOLUTION_SYSTEMS/README.md
- `Rough Hypotheses` --conceptually_related_to--> `Edge Hypotheses`  [INFERRED]
  99_EXPERIMENTAL/README.md → 05_EDGE_HYPOTHESES/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Trading Systems Event-First Flow** — readme_data_foundation_dependency, readme_event_library_layer, readme_event_engine_model_layer, 01_event_engine_model_readme_event_table, readme_outcome_research_layer, 02_outcome_research_readme_outcome_table, readme_strategy_research_layer, readme_decision_models_layer, readme_evolution_systems_layer [EXTRACTED 1.00]
- **Event Library Taxonomy** — 01_momentum_expansion_readme_momentum_expansion, 02_vwap_control_readme_vwap_control, 03_intraday_reversals_readme_intraday_reversals, 04_momentum_exhaustion_readme_momentum_exhaustion, 05_runner_lifecycle_readme_runner_lifecycle, 06_resistance_and_breakouts_readme_resistance_and_breakouts, 07_short_squeeze_dynamics_readme_short_squeeze_dynamics, 99_experimental_readme_experimental_events [EXTRACTED 1.00]
- **Event Definition Lifecycle** — 00_event_library_readme_event_library, 00_event_library_readme_event_template, 01_event_engine_model_readme_detector_design_notes, 01_event_engine_model_readme_event_table, 00_event_library_readme_outcome_validation, 02_outcome_research_readme_evidence_rules [EXTRACTED 1.00]
- **Breakout Operational Response** — breakout_readme_breakout, breakout_edge_hypothesis_breakout_edge_hypothesis, breakout_execution_model_execution_model, breakout_failure_modes_failure_modes, breakout_market_structure_market_structure, breakout_ml_features_candidate_features, breakout_pattern_mining_questions_research_questions, breakout_squeeze_relevance_squeeze_relevance [INFERRED 0.85]
- **Breakout Pressure Mechanism** — breakout_edge_hypothesis_important_resistance_break, breakout_edge_hypothesis_above_average_volume, breakout_edge_hypothesis_short_covering, breakout_edge_hypothesis_long_chasing, breakout_edge_hypothesis_price_expansion, breakout_market_structure_supply_demand_imbalance [INFERRED 0.85]
- **Breakout ML Research Alignment** — breakout_ml_features_candidate_features, breakout_ml_features_float, breakout_ml_features_pm_volume, breakout_ml_features_market_cap, breakout_ml_features_sector, breakout_pattern_mining_questions_research_questions, breakout_pattern_mining_questions_best_float_question, breakout_pattern_mining_questions_pm_volume_question, breakout_pattern_mining_questions_market_cap_question, breakout_pattern_mining_questions_sector_question [INFERRED 0.85]
- **Long Play Confirmation Stack** — 03_strategy_library_07_long_plays_long_play, 03_strategy_library_07_long_plays_technical_confirmation, 03_strategy_library_07_long_plays_credible_volume, 03_strategy_library_07_long_plays_clear_structure, 03_strategy_library_07_long_plays_active_filings_dilution_filter [EXTRACTED 1.00]
- **VWAP Long Setup Family** — 03_strategy_library_07_long_plays_vwap_bounce, 03_strategy_library_07_long_plays_vwap_reclaim, 03_strategy_library_07_long_plays_vwap_support, 03_strategy_library_07_long_plays_first_day_runner_dip_buying [INFERRED 0.85]
- **Opening Momentum Reversal Family** — 03_strategy_library_07_long_plays_red_to_green, 03_strategy_library_07_long_plays_gap_and_grab_reversal, 03_strategy_library_07_long_plays_gap_and_go, 03_strategy_library_07_long_plays_premarket_high_breakout, 03_strategy_library_07_long_plays_short_squeeze [INFERRED 0.85]
- **Primary Short Setups** — 03_strategy_library_07_short_plays_first_red_day, 03_strategy_library_07_short_plays_overextended_gap_down, 03_strategy_library_07_short_plays_late_day_fade [EXTRACTED 1.00]
- **Short Entry Filter Stack** — 03_strategy_library_07_short_plays_overextension, 03_strategy_library_07_short_plays_active_dilution, 03_strategy_library_07_short_plays_overhead_resistance, 03_strategy_library_07_short_plays_adequate_float [EXTRACTED 1.00]
- **Exhaustion Confirmation Stack** — 03_strategy_library_07_short_plays_decreasing_volume, 03_strategy_library_07_short_plays_vwap, 03_strategy_library_07_short_plays_j_lines, 03_strategy_library_07_short_plays_green_to_red, 03_strategy_library_07_short_plays_vwap_rejection, 03_strategy_library_07_short_plays_technical_confirmation [INFERRED 0.85]
- **Small Cap Supply Demand Framework** — 03_strategy_library_day_trading_en_small_caps_xvntrading_small_caps, 03_strategy_library_day_trading_en_small_caps_xvntrading_penny_stock_framework, 03_strategy_library_day_trading_en_small_caps_xvntrading_dilution, 03_strategy_library_day_trading_en_small_caps_xvntrading_catalyst_quality, 03_strategy_library_day_trading_en_small_caps_xvntrading_long_imbalance_model, 03_strategy_library_day_trading_en_small_caps_xvntrading_short_imbalance_model, 03_strategy_library_day_trading_en_small_caps_xvntrading_overhead_resistance, 03_strategy_library_day_trading_en_small_caps_xvntrading_short_squeeze [EXTRACTED 1.00]
- **VWAP Centered Trade Setups** — 03_strategy_library_day_trading_en_small_caps_xvntrading_vwap, 03_strategy_library_day_trading_en_small_caps_xvntrading_vwap_bounce, 03_strategy_library_day_trading_en_small_caps_xvntrading_vwap_reclaim, 03_strategy_library_day_trading_en_small_caps_xvntrading_vwap_rejection, 03_strategy_library_day_trading_en_small_caps_xvntrading_short_squeeze, 03_strategy_library_day_trading_en_small_caps_xvntrading_risk_reward [EXTRACTED 1.00]
- **Trader Preparation Risk Feedback Loop** — 03_strategy_library_day_trading_en_small_caps_xvntrading_scanner_gappers, 03_strategy_library_day_trading_en_small_caps_xvntrading_watchlist_construction, 03_strategy_library_day_trading_en_small_caps_xvntrading_risk_management, 03_strategy_library_day_trading_en_small_caps_xvntrading_position_sizing, 03_strategy_library_day_trading_en_small_caps_xvntrading_journaling, 03_strategy_library_day_trading_en_small_caps_xvntrading_scalability_process, 03_strategy_library_day_trading_en_small_caps_xvntrading_risk_parameters [EXTRACTED 1.00]
- **Research to Decision Layer Chain** — 04_strategy_research_readme_strategy_research, 08_execution_models_readme_execution_models, 09_decision_models_readme_decision_models [INFERRED 0.85]
- **Evidence and Promotion Flow** — 05_edge_hypotheses_readme_edge_hypotheses, 06_pattern_discovery_readme_pattern_discovery, 99_experimental_readme_experimental_area [INFERRED 0.75]
- **Governed Search Constraints** — 08_execution_models_readme_realism_constraints, 09_decision_models_readme_risk_gates, 10_evolution_systems_readme_locked_evaluators [INFERRED 0.75]

## Communities (19 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (58): Absorption, Baby Shelf Restriction, Bagholders, Breakout Long, Catalyst Quality, Contracts and Partnerships, Dilution, Displacement (+50 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (43): Event Library, Event Lifecycle, Minimum Event Template, Market Event, Outcome Validation, Events Do Not Define Trading Actions, Gap And Go Event, Momentum Expansion (+35 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (41): Active Filings Dilution Filter, Breakout, Buy Weakness Sell Strength, Capital Preservation, Catalyst, Clear Structure, Credible Volume, Dip Buying Panic (+33 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (40): Active Dilution, Adequate Float, All Day Fade, All-Time High Avoidance, Big Picture Discipline, Bull Trap, Buyer Control Loss, Decreasing Volume (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (37): Backtest Output and Manifest Boundary, Cost, Slippage and Risk Assumptions, event_table, Execution Models, Failure Mode Evidence, outcome_table, Robustness Checks, Strategy Candidate Evaluation (+29 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (35): Causal or Structural Hypotheses, Edge Existence Rationale, Edge Hypotheses, Empirical Anomalies, Links to Events and Outcomes, Evidence Requirements, Market Science, Outcome Research Evidence (+27 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (32): Detector Design Notes, Event Engine Model, event_table, Event Versioning Rules, Required Lineage Fields, Reproducibility Requirements, Market Consequences Not Trading Decisions, Outcome Horizons (+24 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (30): Event Library, Candidate Patterns, Data-Discovered Patterns, Links to Event Families, Event Library or Edge Hypotheses Promotion, Support and Stability Notes, Behavior Families, Cluster Definitions (+22 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (24): Promotion or Rejection Notes, Falsification Criteria, Audited Market Data, Event Tables, Feature Candidates, Outcome Tables, Pattern Discovery, Pattern Mining Outputs (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.18
Nodes (15): Important Resistance Break, Long Chasing, Price Expansion, Execution Model, Exhaustion Exit, Partial Scaling, Resistance Break Entry, Risk Below Resistance (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (15): First Pullback Entry, Market Structure, Optimal Pullback Question, Breakout, Breakout Setup, Continuation, Intraday, Long (+7 more)

### Community 11 - "Community 11"
Cohesion: 0.19
Nodes (14): Broker Firebreaks, Daily Max Loss, Dip Buying Panics, ECN Fees, Expected Value, Journaling, Market Order Risk, Position Sizing (+6 more)

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (13): atr, Candidate Features, float, gap_pct, market_cap, news_score, pm_volume, sector (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.20
Nodes (10): Candidate Proposal Protocols, Candidate Structures, Canonical Authority Boundary, Clarified Work Items, Experimental Area, Exploratory Notes, Rejection Notes, Rough Hypotheses (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.29
Nodes (7): No Upstream Semantics Redefinition, Strategy Definitions, Strategy Library, No Event Or Data Contracts, No Promoted Short Strategy Dossier, Short Side Strategy Definitions, Short Strategy Concepts

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (6): Edge Hypotheses, Event Library Inputs, Execution Constraints, Operational Responses To Events, Outcome Research Inputs, Breakout Edge Hypothesis

### Community 16 - "Community 16"
Cohesion: 0.33
Nodes (6): Above Average Volume, Short Covering, Low Volume Breakout, Shorts, relative_volume, PM Squeeze Extreme

### Community 17 - "Community 17"
Cohesion: 0.40
Nodes (6): Bull Trap, Dilution Event, Failure Modes, Fake Breakout, Market Weakness, Failure Modes

### Community 18 - "Community 18"
Cohesion: 0.33
Nodes (6): distance_to_vwap, Breakout Medium Squeeze, Gap And Crap Reversal High Squeeze, Red To Green Very High Squeeze, Squeeze Relevance, VWAP Bounce Low Squeeze

## Knowledge Gaps
- **160 isolated node(s):** `Strategy Library Layer`, `Strategy Research Layer`, `Pattern Discovery Layer`, `Cluster Research Layer`, `Execution Models Layer` (+155 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Event Library` connect `Community 1` to `Community 6`, `Community 7`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `Experimental Events` connect `Community 7` to `Community 1`?**
  _High betweenness centrality (0.118) - this node is a cross-community bridge._
- **Why does `Promotion Candidates` connect `Community 7` to `Community 13`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Breakout` (e.g. with `Execution Model` and `First Pullback Entry`) actually correct?**
  _`Breakout` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Candidate Features` (e.g. with `Breakout` and `Research Questions`) actually correct?**
  _`Candidate Features` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Event-First Architecture`, `Event Setup Strategy Decision Boundary`, `Strategy Library Layer` to the rest of the system?**
  _175 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0544464609800363 - nodes in this community are weakly interconnected._