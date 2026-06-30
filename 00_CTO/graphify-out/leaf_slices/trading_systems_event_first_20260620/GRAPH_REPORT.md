# Graph Report - C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS  (2026-06-21)

## Corpus Check
- Corpus is ~30,071 words - fits in a single context window. You may not need a graph.

## Summary
- 313 nodes · 408 edges · 20 communities (16 shown, 4 thin omitted)
- Extraction: 92% EXTRACTED · 7% INFERRED · 1% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80f63248`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_02_OUTCOME_RESEARCH README|02_OUTCOME_RESEARCH README]]
- [[_COMMUNITY_Breakout|Breakout]]
- [[_COMMUNITY_Behavioral Mechanics Policy|Behavioral Mechanics Policy]]
- [[_COMMUNITY_Event Behavioral Mechanics Guide v0.1|Event Behavioral Mechanics Guide v0.1]]
- [[_COMMUNITY_Detector Design Notes|Detector Design Notes]]
- [[_COMMUNITY_ECN Fees|ECN Fees]]
- [[_COMMUNITY_Momentum Expansion README|Momentum Expansion README]]
- [[_COMMUNITY_Acceptance Duration Ambiguity|Acceptance Duration Ambiguity]]
- [[_COMMUNITY_Active Dilution|Active Dilution]]
- [[_COMMUNITY_Event Library|Event Library]]
- [[_COMMUNITY_Borrow Or Short Interest Proxies|Borrow Or Short Interest Proxies]]
- [[_COMMUNITY_Corporate Actions Context|Corporate Actions Context]]
- [[_COMMUNITY_13 Trading Systems|13 Trading Systems]]
- [[_COMMUNITY_Detector Candidate|Detector Candidate]]
- [[_COMMUNITY_Event Window Highlight|Event Window Highlight]]
- [[_COMMUNITY_AlphaEvolve OpenEvolve Style Systems|AlphaEvolve OpenEvolve Style Systems]]
- [[_COMMUNITY_All Day Fade|All Day Fade]]
- [[_COMMUNITY_J-Lines|J-Lines]]
- [[_COMMUNITY_Short Sale Restriction|Short Sale Restriction]]
- [[_COMMUNITY_Journaling|Journaling]]

## God Nodes (most connected - your core abstractions)

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Active Event Families** — 01_momentum_expansion_readme_momentum_expansion, 02_vwap_control_readme_vwap_control, 03_intraday_reversals_readme_intraday_reversals, 04_momentum_exhaustion_readme_momentum_exhaustion, 05_runner_lifecycle_readme_runner_lifecycle, 06_resistance_and_breakouts_readme_resistance_and_breakouts, 07_short_squeeze_dynamics_readme_short_squeeze_dynamics, 99_experimental_readme_experimental [EXTRACTED 1.00]
- **Breakout Dossier Components** — breakout_readme_breakout, breakout_edge_hypothesis_resistance_break_volume, breakout_edge_hypothesis_shorts_cover_longs_chase, breakout_execution_model_resistance_break_or_pullback, breakout_execution_model_risk_management_exit, breakout_market_structure_supply_demand_imbalance, breakout_ml_features_candidate_features, breakout_squeeze_relevance_squeeze_scale [INFERRED 0.95]
- **Event First Lab Functional Chain** — readme_data_foundation, readme_event_library, readme_event_engine_model, readme_outcome_research, readme_strategy_library, readme_strategy_research, readme_edge_hypotheses, readme_pattern_discovery, readme_cluster_research, readme_execution_models, readme_decision_models, readme_evolution_systems [EXTRACTED 1.00]
- **Event Lifecycle Pipeline** — 00_event_library_readme_source_note, 00_event_library_readme_draft_event_definition, 00_event_library_readme_detector_candidate, 00_event_library_readme_event_table_version, 00_event_library_readme_outcome_validation, 00_event_library_readme_promoted_event [EXTRACTED 1.00]
- **Event Non Strategy Boundary** — 00_event_library_readme_event_strategy_boundary, pm_accepted_extension_break_event_event_definition_draft_v0_1_pm_accepted_extension_break_event, das_event_event_definition_draft_v0_1_das_event, 00_event_library_event_behavioral_mechanics_guide_v0_1_strategy_layer [INFERRED 0.95]
- **Governed Evolution Prerequisites** — readme_audited_market_data, readme_event_table, readme_outcome_table, readme_locked_evaluators, readme_execution_constraints, readme_oos_validation_policy, readme_evolution_systems [EXTRACTED 1.00]
- **Accepted Extension Break Sequence** — img_000_pre_break_consolidation, img_000_three_bar_push, img_000_vertical_momentum_expansion, img_000_post_break_acceptance [INFERRED 0.85]
- **Long Strategy Family** — 03_strategy_library_07_long_plays_breakout, 03_strategy_library_07_long_plays_red_to_green, 03_strategy_library_07_long_plays_vwap_bounce, 03_strategy_library_07_long_plays_vwap_reclaim, 03_strategy_library_07_long_plays_dip_buying_panics, 03_strategy_library_07_long_plays_first_green_day, 03_strategy_library_07_long_plays_gap_and_go [EXTRACTED 1.00]
- **Short Strategy Family** — 03_strategy_library_07_short_plays_first_red_day, 03_strategy_library_07_short_plays_overextended_gap_down, 03_strategy_library_07_short_plays_short_into_resistance, 03_strategy_library_07_short_plays_late_day_fade, 03_strategy_library_07_short_plays_gap_and_crap, 03_strategy_library_07_short_plays_gap_and_extension, 03_strategy_library_07_short_plays_vwap_rejection [EXTRACTED 1.00]
- **Strategy Execution Decision Stack** — readme_strategy_research, readme_execution_models, readme_decision_models, readme_ml_predictions, readme_risk_portfolio_state, readme_execution_constraints [INFERRED 0.85]

## Communities (20 total, 4 thin omitted)

### Community 0 - "02_OUTCOME_RESEARCH README"
Cohesion: 0.06
Nodes (51): 02_OUTCOME_RESEARCH README, Outcome Research Excludes Trading Decisions, Outcome Metrics, 04_STRATEGY_RESEARCH README, Failure Mode Evidence, Robustness Checks, Walk Forward Requirements, 05_EDGE_HYPOTHESES README (+43 more)

### Community 1 - "Breakout"
Cohesion: 0.07
Nodes (44): Breakout, Buy Dips on First Runner Day, Long Entry Requires Technical Confirmation Volume and Structure, Dip Buying Panics, 07 Long Plays, First Green Day, First Green Day Bounce, Gap and Go (+36 more)

### Community 2 - "Behavioral Mechanics Policy"
Cohesion: 0.06
Nodes (36): Behavioral Mechanics Policy, Evidence Ladder, Falsifiability Requirement, Game Theoretic Pressure, Herding And Crowd Attention, Human Hypothesis, Liquidity Vacuum, Measurable Evidence Layer (+28 more)

### Community 3 - "Event Behavioral Mechanics Guide v0.1"
Cohesion: 0.08
Nodes (28): Event Behavioral Mechanics Guide v0.1, Cluster Research, Data Foundation, Event Library README, Event Library, Outcome Research, Pattern Discovery, VWAP Control README (+20 more)

### Community 4 - "Detector Design Notes"
Cohesion: 0.11
Nodes (24): Detector Design Notes, 01_EVENT_ENGINE_MODEL README, Event Versioning Rules, Reproducibility Requirements, 11_SQUEEZE_RESEARCH README, Liquidity Vacuum, Low Float Runner, Squeeze Families (+16 more)

### Community 5 - "ECN Fees"
Cohesion: 0.11
Nodes (24): ECN Fees, Risk Management, Breakout Edge Hypothesis Document, Resistance Break With Above Average Volume, Shorts Cover and Longs Chase, Breakout Execution Model Document, Resistance Break or First Pullback Entry, Risk Below Resistance and Exit on Upper Resistance or Exhaustion (+16 more)

### Community 6 - "Momentum Expansion README"
Cohesion: 0.10
Nodes (20): Momentum Expansion README, Gap And Go Event, Master Daily Table, Master Intraday Table, Momentum Expansion, Opening Drive Event, Parabolic Expansion Event, PM Squeeze Event (+12 more)

### Community 7 - "Acceptance Duration Ambiguity"
Cohesion: 0.15
Nodes (16): Acceptance Duration Ambiguity, Accepted Extension Sequence, Accepted Price Shelf, PM Accepted Extension Break Event Definition Draft v0.1, Event Timestamp At Break Start, Impulse Bar Count Ambiguity, Initial Extension, Initial Extension Measurement Ambiguity (+8 more)

### Community 8 - "Active Dilution"
Cohesion: 0.18
Nodes (11): Active Dilution, Overextension, Short Playbook, At-the-Market Offering, Dilution, Hot Sector Sympathy Play, SEC Filings, Short Ecosystem Offer Over Demand (+3 more)

### Community 9 - "Event Library"
Cohesion: 0.27
Nodes (11): Event Library, Execution Constraints, No Upstream Semantics Redefinition, Outcome Research, Strategy Definitions, Strategy Library, Breakout Dossier README, Edge Hypotheses (+3 more)

### Community 10 - "Borrow Or Short Interest Proxies"
Cohesion: 0.22
Nodes (9): Borrow Or Short Interest Proxies, Short Squeeze Dynamics README, Float And Liquidity Context, Forced Covering Event, High Short Interest Event, Short Squeeze Dynamics, Short Squeeze Event, SSR And Halt Context (+1 more)

### Community 11 - "Corporate Actions Context"
Cohesion: 0.25
Nodes (8): Corporate Actions Context, Runner Lifecycle README, First Green Day Event, First Red Day Event, Multi Day Runner Event, Runner Collapse Event, Runner Continuation Event, Runner Lifecycle

### Community 12 - "13 Trading Systems"
Cohesion: 0.25
Nodes (8): 13 Trading Systems, 13_TRADING_SYSTEMS README, Event-First Architecture, Event Setup Strategy Decision Separation, Graphify Official Build Protocol, Graphify Root Preserves Old Trading System Paths, Trading Systems Revision Note, Historical Trading Systems Structure Proposal

### Community 13 - "Detector Candidate"
Cohesion: 0.29
Nodes (7): Detector Candidate, Draft Event Definition, Event Lifecycle, Event Table Version, Outcome Validation, Promoted Event, Source Note

### Community 14 - "Event Window Highlight"
Cohesion: 0.33
Nodes (7): Event Window Highlight, Orderly Fade After Acceptance, PM Accepted Extension Break Chart, Post-Break Acceptance Above Extension, Pre-Break Consolidation, 3-Bar Push, Vertical Momentum Expansion

### Community 15 - "AlphaEvolve OpenEvolve Style Systems"
Cohesion: 0.50
Nodes (5): AlphaEvolve OpenEvolve Style Systems, AlphaEvolve, AlphaEvolve Arxiv Paper, Google DeepMind AlphaEvolve Blog, Objective Evaluator

## Ambiguous Edges - Review These
- `Continuation Versus DAS Ambiguity` → `DAS Event`  [AMBIGUOUS]
  00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md · relation: conceptually_related_to
- `Short Covering Validation Ambiguity` → `DAS Event`  [AMBIGUOUS]
  00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md · relation: conceptually_related_to
- `Acceptance Duration Ambiguity` → `PM Accepted Extension Break Event`  [AMBIGUOUS]
  00_EVENT_LIBRARY/01_MOMENTUM_EXPANSION/PM_ACCEPTED_EXTENSION_BREAK_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md · relation: conceptually_related_to
- `Impulse Bar Count Ambiguity` → `PM Accepted Extension Break Event`  [AMBIGUOUS]
  00_EVENT_LIBRARY/01_MOMENTUM_EXPANSION/PM_ACCEPTED_EXTENSION_BREAK_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md · relation: conceptually_related_to
- `Initial Extension Measurement Ambiguity` → `PM Accepted Extension Break Event`  [AMBIGUOUS]
  00_EVENT_LIBRARY/01_MOMENTUM_EXPANSION/PM_ACCEPTED_EXTENSION_BREAK_EVENT/EVENT_DEFINITION_DRAFT_v0_1.md · relation: conceptually_related_to
- `Historical Trading Systems Structure Proposal` → `Event-First Architecture`  [AMBIGUOUS]
  revision.md · relation: conceptually_related_to

## Knowledge Gaps
- **131 isolated node(s):** `Data Foundation`, `Detector Candidate`, `Draft Event Definition`, `Event Table Version`, `Outcome Research` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.