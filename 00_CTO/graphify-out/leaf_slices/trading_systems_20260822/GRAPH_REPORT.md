# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 84 files · ~119,339 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 455 nodes · 1142 edges · 15 communities (14 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 101 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DAS Widget Analytics
- Gap-and-Go Widgets
- Frontside Pattern Statistics
- Steven Dux Factors
- DAS Observable Strategy
- Strategy Visualization Toolkit
- Event Behavior Library
- Reproducible Strategy Evaluation
- DAS Candidate State Builder
- Experimental Statistics Report
- EduTrades Event Candidates
- Visual Manifest Overlay
- Extension Break Event
- Strategy Promotion Boundary
- Momentum Exhaustion Family

## God Nodes (most connected - your core abstractions)
1. `_clean_value()` - 28 edges
2. `_build_cases()` - 27 edges
3. `make_das_chart()` - 20 edges
4. `_build_visual_inspection_rows()` - 18 edges
5. `export_run_event_day_detail_images()` - 18 edges
6. `Steven Dux Source Strategy Index` - 18 edges
7. `_das_rows_for_session()` - 17 edges
8. `build_table()` - 16 edges
9. `DasConfig` - 15 edges
10. `export_run_premarket_detail_images()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `_load_chart_window()` --calls--> `_select_vwap()`  [INFERRED]
  00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py → 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/strategy_widgets_common.py
- `make_das_chart()` --calls--> `make_strategy_1m_chart()`  [INFERRED]
  00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py → 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/strategy_widgets_common.py
- `_terminal_command_from_config()` --calls--> `_ps_quote()`  [INFERRED]
  00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py → 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/gap&go/gap_and_go_widgets.py
- `_find_momentum_end()` --calls--> `_compute_vwap()`  [INFERRED]
  00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py → 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/gap&go/gap_and_go_widgets.py
- `_das_rows_for_session_v1()` --calls--> `_compute_vwap()`  [INFERRED]
  00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/scripts/das_widgets.py → 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/gap&go/gap_and_go_widgets.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Event-First Trading System Chain** — 00_cto_13_trading_systems_readme_event_strategy_decision_separation, 00_cto_13_trading_systems_00_event_library_readme_observable_event_boundary, 00_cto_13_trading_systems_01_event_engine_model_readme_reproducible_event_table [INFERRED 0.95]
- **PM Extension Acceptance Break Definition Chain** — 00_cto_13_trading_systems_00_event_library_01_momentum_expansion_readme_momentum_expansion_family, 00_cto_13_trading_systems_00_event_library_01_momentum_expansion_pm_accepted_extension_break_event_source_note_response_clone_extension_acceptance_break_sequence, 00_cto_13_trading_systems_00_event_library_01_momentum_expansion_pm_accepted_extension_break_event_event_definition_draft_v0_1_pm_accepted_extension_break_event [INFERRED 0.95]
- **Discretionary Sources to Event Candidates** — 00_cto_13_trading_systems_00_event_library_source_assets_edu_trades_07_long_plays_edutrades_discretionary_long_playbook, 00_cto_13_trading_systems_00_event_library_traders_strategies_edutrades_long_plays_source_event_index_v0_1_edutrades_observable_event_candidates, 00_cto_13_trading_systems_00_event_library_source_assets_mosquito_smallcaps_la_formula_exacta_para_entrar_en_trades_media_4xh34affgjc_001_1080p_pdf_mosquito_discretionary_playbook, 00_cto_13_trading_systems_00_event_library_traders_strategies_mosquito_smallcaps_source_event_index_v0_1_mosquito_observable_event_candidates [INFERRED 0.95]
- **Dux Factor Interaction Model** — 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_crowded_ticker_context_factor_crowding_degradation_and_future_resistance, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_float_rotation_factor_traded_volume_to_float_rotation, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_liquidity_gain_loss_factor_dynamic_liquidity_adjusted_volume, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_neutralized_area_factor_neutralized_reward_risk_area, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_pattern_variation_acceptable_range_factor_volume_supported_breakout_quality, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_short_seller_trap_layers_factor_layered_short_covering_chain_risk, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_factors_volume_prediction_factor_projected_day_volume_context [INFERRED 0.95]
- **Dux Resistance Short Strategy Family** — 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_bounce_plus_gap_up_short_strategy_gap_into_historical_resistance_short, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_bounce_short_strategy_low_volume_retest_into_prior_resistance, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_double_layer_resistance_strategy_historical_and_failed_intraday_resistance_layers, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_gap_up_short_strategy_gap_push_consolidation_breakdown_short [INFERRED 0.85]
- **Multi-Day Runner Transition Research** — 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_long_dip_buying_multi_day_runner_strategy_panic_into_support_on_active_runner, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_double_intraday_top_strategy_second_intraday_top_crack, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_first_red_day_strategy_multi_day_runner_first_red_transition, 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_multi_day_top_risk_reward_strategy_air_gap_below_multi_day_top, 00_cto_13_trading_systems_02_outcome_research_readme_post_event_outcome_table [INFERRED 0.85]
- **Breakout Research Package** — 00_cto_13_trading_systems_03_strategy_library_long_breakout_edge_hypothesis_breakout_pressure_and_covering_edge, 00_cto_13_trading_systems_03_strategy_library_long_breakout_execution_model_breakout_entry_and_risk_model, 00_cto_13_trading_systems_03_strategy_library_long_breakout_failure_modes_breakout_failure_taxonomy, 00_cto_13_trading_systems_03_strategy_library_long_breakout_market_structure_breakout_supply_demand_imbalance, 00_cto_13_trading_systems_03_strategy_library_long_breakout_ml_features_breakout_candidate_feature_set, 00_cto_13_trading_systems_03_strategy_library_long_breakout_pattern_mining_questions_breakout_pattern_research_questions, 00_cto_13_trading_systems_03_strategy_library_long_breakout_readme_breakout_strategy_classification, 00_cto_13_trading_systems_03_strategy_library_long_breakout_squeeze_relevance_squeeze_relevance_gradient, 00_cto_13_trading_systems_03_strategy_library_long_breakout_strategy_observable_breakout_strategy_decomposition [EXTRACTED 1.00]
- **DAS Frontside Research Workflow** — 00_cto_13_trading_systems_03_strategy_library_long_das_00_privado_das_frontside_measurement_questions, 00_cto_13_trading_systems_03_strategy_library_long_das_das_candidate_state_table_experimental_spec_v0_1_das_experimental_candidate_state_table, 00_cto_13_trading_systems_03_strategy_library_long_das_das_frontside_state_and_alphaevolve_research_plan_v0_1_das_frontside_state_research_protocol, 00_cto_13_trading_systems_03_strategy_library_long_das_das_scanner_usage_and_overlay_runbook_v0_1_governed_scanner_overlay_for_das, 00_cto_13_trading_systems_03_strategy_library_long_das_readme_das_experimental_research_workspace, 00_cto_13_trading_systems_03_strategy_library_long_das_strategy_observable_das_strategy_decomposition, 00_cto_13_trading_systems_03_strategy_library_long_das_das_visual_casebook_das_archive_visual_casebook_v0_1_das_visual_case_taxonomy [EXTRACTED 1.00]
- **Source Playbook to Strategy Translation** — 00_cto_13_trading_systems_03_strategy_library_01_steven_dux_short_parabolic_breakout_failed_breakout_strategy_failed_breakout_volume_sufficiency, 00_cto_13_trading_systems_03_strategy_library_03_edu_trades_07_long_plays_edutrades_long_strategy_source_playbook, 00_cto_13_trading_systems_03_strategy_library_03_edu_trades_07_short_plays_edutrades_short_strategy_source_playbook, 00_cto_13_trading_systems_03_strategy_library_long_breakout_strategy_observable_breakout_strategy_decomposition, 00_cto_13_trading_systems_03_strategy_library_long_das_strategy_observable_das_strategy_decomposition [INFERRED 0.75]
- **Governed Trading Research Chain** — 00_cto_13_trading_systems_03_strategy_library_long_gap_go_strategy_observable_gap_and_go_strategy, 00_cto_13_trading_systems_04_strategy_research_readme_reproducible_strategy_evaluation, 00_cto_13_trading_systems_05_edge_hypotheses_readme_falsifiable_edge_hypothesis, 00_cto_13_trading_systems_06_pattern_discovery_readme_governed_data_pattern_candidate, 00_cto_13_trading_systems_07_cluster_research_readme_market_behavior_cluster_families, 00_cto_13_trading_systems_08_execution_models_readme_realistic_execution_constraints, 00_cto_13_trading_systems_09_decision_models_readme_constrained_action_policy, 00_cto_13_trading_systems_10_evolution_systems_readme_governed_evolutionary_candidate_search [INFERRED 0.85]
- **Squeeze Research Integration** — 00_cto_13_trading_systems_11_squeeze_research_readme_squeeze_research_integration, 00_cto_13_trading_systems_05_edge_hypotheses_readme_falsifiable_edge_hypothesis, 00_cto_13_trading_systems_04_strategy_research_readme_reproducible_strategy_evaluation, 00_cto_13_trading_systems_03_strategy_library_long_gap_go_strategy_observable_gap_and_go_strategy [EXTRACTED 1.00]
- **Unpromoted Knowledge Containment** — 00_cto_13_trading_systems_90_discretionary_frameworks_readme_unmechanized_discretionary_doctrine, 00_cto_13_trading_systems_99_experimental_readme_experimental_containment_boundary, 00_cto_13_trading_systems_05_edge_hypotheses_readme_falsifiable_edge_hypothesis, 00_cto_13_trading_systems_08_execution_models_readme_realistic_execution_constraints, 00_cto_13_trading_systems_09_decision_models_readme_constrained_action_policy [INFERRED 0.85]

## Communities (15 total, 1 thin omitted)

### Community 0 - "DAS Widget Analytics"
Cohesion: 0.06
Nodes (109): _add_first_push_level_segment(), _add_premarket_open_to_extension_high_measurement(), _add_premarket_open_to_first_push_measurement(), _assert_no_legacy_visual_text(), _bar_x_for_ts(), _bbox_intersects(), build_arg_parser(), _build_visual_inspection_rows() (+101 more)

### Community 1 - "Gap-and-Go Widgets"
Cohesion: 0.09
Nodes (63): config_from_args(), Namespace, _add_compact_session_backgrounds(), build_arg_parser(), _candidate_detail_image_name(), _candidate_rows_for_file(), _compute_vwap(), config_from_args() (+55 more)

### Community 2 - "Frontside Pattern Statistics"
Cohesion: 0.13
Nodes (43): _bars_between(), _bucket(), build(), _build_cases(), BuildConfig, _classify_quality(), _exists_any(), _fmt() (+35 more)

### Community 3 - "Steven Dux Factors"
Cohesion: 0.06
Nodes (44): Outcome Research Model, Post-Event Outcome Table, Crowded Ticker Context Factor, Crowding Degradation and Future Resistance, Float Rotation Factor, Traded Volume to Float Rotation, Dynamic Liquidity-Adjusted Volume, Liquidity Gain-Loss Factor (+36 more)

### Community 4 - "DAS Observable Strategy"
Cohesion: 0.07
Nodes (40): Failed Breakout Volume Sufficiency, Parabolic Breakout Failed Breakout Strategy, EduTrades Long Plays Source, EduTrades Long Strategy Source Playbook, EduTrades Short Plays Source, EduTrades Short Strategy Source Playbook, Breakout Edge Hypothesis, Breakout Pressure and Covering Edge (+32 more)

### Community 5 - "Strategy Visualization Toolkit"
Cohesion: 0.14
Nodes (28): _add_compact_session_backgrounds(), _add_ema_wilder_columns(), _add_ema_wilder_overlay(), _add_masked_line(), _add_regime_band(), _compute_vwap(), _delete_run_command(), load_lt1b_universe() (+20 more)

### Community 6 - "Event Behavior Library"
Cohesion: 0.09
Nodes (26): Price-Level Interaction Events, Resistance and Breakouts Event Family, DAS Event Definition, Dips After Squeeze Reactivation, Short Pressure and Forced-Covering Events, Short Squeeze Dynamics Event Family, Experimental Event Containment, Unpromoted Event Ideas (+18 more)

### Community 7 - "Reproducible Strategy Evaluation"
Cohesion: 0.14
Nodes (24): Gap and Go Initial Strategy Definition, Observable Gap and Go Strategy, Short Strategy Library Readme, Short Strategy Research Workspace, Reproducible Strategy Evaluation, Strategy Research Readme, Edge Hypotheses Readme, Falsifiable Edge Hypothesis (+16 more)

### Community 8 - "DAS Candidate State Builder"
Cohesion: 0.28
Nodes (21): _bool_column(), build_table(), _candidate_state(), _column(), _column_classification(), _config_value(), _json_dumps(), main() (+13 more)

### Community 9 - "Experimental Statistics Report"
Cohesion: 0.35
Nodes (11): _bucket_table(), build_report(), _fmt(), main(), _markdown_table(), _numeric_summary(), DataFrame, Path (+3 more)

### Community 10 - "EduTrades Event Candidates"
Cohesion: 0.20
Nodes (10): VWAP Control Changes, VWAP Control Event Family, Intraday Control Reversals, Intraday Reversals Event Family, Multi-Session Runner Lifecycle, Runner Lifecycle Event Family, EduTrades Discretionary Long Playbook, EduTrades Long Plays Source Asset (+2 more)

### Community 11 - "Visual Manifest Overlay"
Cohesion: 0.32
Nodes (8): _draw_dotted_line(), _draw_visual_box(), _draw_visual_manifest_overlay(), _draw_visual_marker(), _visual_font(), _visual_overlay_styles(), ImageDraw, ImageFont

### Community 12 - "Extension Break Event"
Cohesion: 0.40
Nodes (6): PM Accepted Extension Break Definition, PM Accepted Extension Break Event, Extension-Acceptance-Break Sequence, PM Accepted Extension Break Source Note, Momentum Expansion Event Family, Momentum Expansion Family

### Community 13 - "Strategy Promotion Boundary"
Cohesion: 0.50
Nodes (4): Strategy Factors Readme, Trader Factor Promotion Boundary, Neutral Shared Strategy Infrastructure, Shared Strategy Infrastructure Readme

## Knowledge Gaps
- **42 isolated node(s):** `Trading Systems Historical Architecture Note`, `Momentum Expansion Family`, `VWAP Control Event Family`, `Intraday Reversals Event Family`, `Momentum Exhaustion Event Family` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_outputs()` connect `DAS Candidate State Builder` to `DAS Widget Analytics`, `Experimental Statistics Report`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `build_report()` connect `Experimental Statistics Report` to `DAS Widget Analytics`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `load_split_events_for_chart()` connect `Gap-and-Go Widgets` to `DAS Widget Analytics`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **What connects `Trading Systems Historical Architecture Note`, `Momentum Expansion Family`, `VWAP Control Event Family` to the rest of the system?**
  _42 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DAS Widget Analytics` be split into smaller, more focused modules?**
  _Cohesion score 0.06453726453726454 - nodes in this community are weakly interconnected._
- **Should `Gap-and-Go Widgets` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `Frontside Pattern Statistics` be split into smaller, more focused modules?**
  _Cohesion score 0.1341350601295097 - nodes in this community are weakly interconnected._