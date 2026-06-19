# Graph Report - C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification  (2026-06-19)

## Corpus Check
- Corpus is ~45,813 words - fits in a single context window. You may not need a graph.

## Summary
- 252 nodes · 322 edges · 22 communities (19 shown, 3 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 48 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Trades Certification|Trades Certification]]
- [[_COMMUNITY_Reference Certification|Reference Certification]]
- [[_COMMUNITY_Halts Certification|Halts Certification]]
- [[_COMMUNITY_Additional Certification|Additional Certification]]
- [[_COMMUNITY_Quotes Certification|Quotes Certification]]
- [[_COMMUNITY_Halts Certification 2|Halts Certification 2]]
- [[_COMMUNITY_Quotes Certification 2|Quotes Certification 2]]
- [[_COMMUNITY_Daily Certification|Daily Certification]]
- [[_COMMUNITY_Trades Certification 2|Trades Certification 2]]
- [[_COMMUNITY_Graphify Governance|Graphify Governance]]
- [[_COMMUNITY_Quotes Certification 3|Quotes Certification 3]]
- [[_COMMUNITY_Short Certification|Short Certification]]
- [[_COMMUNITY_Global Metrics|Global Metrics]]
- [[_COMMUNITY_OHLCV 1m Certification|OHLCV 1m Certification]]
- [[_COMMUNITY_Graphify Governance 2|Graphify Governance 2]]
- [[_COMMUNITY_Short Certification 2|Short Certification 2]]
- [[_COMMUNITY_Halts Certification 3|Halts Certification 3]]
- [[_COMMUNITY_Trades Certification 3|Trades Certification 3]]
- [[_COMMUNITY_OHLCV 1m Certification 2|OHLCV 1m Certification 2]]
- [[_COMMUNITY_Additional Certification 2|Additional Certification 2]]
- [[_COMMUNITY_Trades Certification 4|Trades Certification 4]]
- [[_COMMUNITY_Quotes Certification 4|Quotes Certification 4]]

## God Nodes (most connected - your core abstractions)
1. `Provisional Certification Policy` - 10 edges
2. `Bucket Synthesis` - 10 edges
3. `Final Recovery Policy` - 9 edges
4. `Recovery Synthesis` - 8 edges
5. `Recovery And Exclusion` - 7 edges
6. `Good Review Bad Certification States` - 7 edges
7. `Final Certification Process` - 7 edges
8. `Blocking Policy By Dataset` - 7 edges
9. `Trades Closeout Verdict` - 7 edges
10. `Certification Decisions Graph Protocol` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Empty Placeholders Not Failure` --conceptually_related_to--> `Recovery And Exclusion`  [INFERRED]
  auditoria/additional/01_contrato_additional.md → GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Daily Hard Invalid Exclusion` --conceptually_related_to--> `Recovery And Exclusion`  [INFERRED]
  auditoria/daily/04_daily_closeout.md → GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Nasdaq Recovered Intraday` --conceptually_related_to--> `Recovery And Exclusion`  [INFERRED]
  auditoria/halts/03_halts_root_cause_audit_phase1_closeout.md → GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Rescue Schema Only Good` --conceptually_related_to--> `Recovery And Exclusion`  [INFERRED]
  auditoria/ohlcv_1m/04_ohlcv_1m_closeout.md → GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Bad Unresolved Identity` --conceptually_related_to--> `Recovery And Exclusion`  [INFERRED]
  auditoria/reference/04_reference_closeout.md → GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Certification Decisions Governance Leaf** — graphify_official_build_protocol, graphify_refresh_queue, graphify_official_build_protocol_certification_decisions_graph, graphify_official_build_protocol_official_graphify_build, graphify_refresh_queue_pending_leaf_build [EXTRACTED 1.00]
- **Family Level Good Review Bad Policies** — additional_04_additional_closeout_additional_final_policy, daily_04_daily_closeout_daily_final_policy, halts_04_halts_closeout_halts_final_policy, ohlcv_1m_04_ohlcv_1m_closeout_ohlcv_1m_final_policy, v2_04_quotes_full_c_d_closeout_quotes_final_policy, reference_04_reference_closeout_reference_final_policy, additional_04_additional_closeout_family_level_certification_states [INFERRED 0.85]
- **Recovery Exclusion And Provider Baseline Decisions** — graphify_official_build_protocol_recovery_and_exclusion, daily_04_daily_closeout_daily_hard_invalid_exclusion, halts_03_halts_root_cause_audit_phase1_closeout_nasdaq_recovered_intraday, ohlcv_1m_04_ohlcv_1m_closeout_rescue_schema_only_good, short_01_contrato_short_finra_baseline, short_03_short_root_cause_audit_phase1_closeout_polygon_secondary_provider [INFERRED 0.75]
- **Recovery First Certification Pattern** — 1m_01_1m_recovery_policy_rescue_over_quarantine, daily_01_daily_recovery_and_coverage_coverage_recovery, daily_03_daily_closeout_recovery_states, v1_01_contrato_agent02_agent03_trades_04012026_trade_price_scale_mismatch_reclassification [INFERRED 0.85]
- **Traceable Global Metrics Evidence Layer** — global_metrics_00_global_metrics_tables_quantitative_summary_tables, global_metrics_01_global_metrics_tables_traceable_source_artifact_traceability, global_metrics_04_global_metrics_tables_traceable_plain_paths_plain_path_traceability, global_metrics_manifest_artifact_inventory [EXTRACTED 1.00]
- **Contextual Event Overlay Pattern** — halts_01_halts_overlay_and_recovery_microstructure_overlay, short_04_short_causal_overlay_closeout_short_context_not_universal_cause, additional_01_additional_subblock_policy_news_ambiguous_multiticker, additional_02_additional_closeout_accepted_heterogeneous_block [INFERRED 0.75]
- **Quotes Open Bucket Decision Set** — quotes_12_quotes_open_buckets_synthesis_open_bucket_final_classification, quotes_08_persistent_soft_crossed_mid_large_scale_bucket_review_decision, quotes_09_large_file_threshold_edge_hard_many_crosses_bucket_review_decision, quotes_10_medium_file_threshold_edge_hard_many_crosses_bucket_bad_decision, quotes_11_high_hard_crossed_10_to_20_bucket_bad_decision [EXTRACTED 1.00]
- **Reference Causal Fronts** — reference_01_reference_causal_value_events_to_halts_strong_signal, reference_01_reference_causal_value_events_to_quotes_mixed_signal, reference_01_reference_causal_value_splits_to_trades_small_defensible_subset, reference_01_reference_causal_value_splits_to_daily_1m_weak_alignment [EXTRACTED 1.00]
- **Certification Cross Layer Quality Context** — halts_03_halts_closeout_halts_event_truth_layer, quotes_12_quotes_open_buckets_synthesis_causal_context_vs_book_quality, reference_00_reference_current_state_reference_as_causal_layer, short_01_short_recovery_and_limits_short_recoverable_context, trades_00_current_state_from_raw_shards_acceptance_counts_distribution [INFERRED 0.75]
- **Trades Certification Foundation** — trades_00_trades_current_state_57f_full_clean_fast_same_schema, trades_02_trades_base_certification_decision_three_layer_certification_base, trades_03_trades_old_vs_new_bucket_bridge_old_vs_new_bucket_bridge, trades_04_trades_provisional_cert_policy_provisional_certification_policy [INFERRED 0.85]
- **Trades Review Bucket Taxonomy** — trades_07_trades_reference_scale_mismatch_reference_scale_mismatch, trades_06_trades_review_microstructure_review_microstructure, trades_05_trades_review_1m_reference_alignment_review_1m_reference_alignment, trades_09_trades_review_no_1m_reference_review_no_1m_reference, trades_11_trades_review_generic_review_generic, trades_08_trades_bad_data_bad_data, trades_12_trades_good_good [EXTRACTED 1.00]
- **Trades Final Recovery Policy States** — trades_19_trades_final_recovery_policy_final_recovery_policy, trades_19_trades_final_recovery_policy_final_certification_states, trades_13_trades_recovery_review_no_1m_reference_recovery_review_no_1m_reference, trades_17_trades_recovery_review_generic_recovery_review_generic, trades_15_trades_recovery_review_microstructure_recovery_review_microstructure, trades_16_trades_recovery_review_1m_reference_alignment_recovery_review_1m_reference_alignment, trades_14_trades_recovery_reference_scale_mismatch_recovery_reference_scale_mismatch, trades_20_trades_closeout_closeout_verdict [EXTRACTED 1.00]
- **Certification Decisions Graph Protocol Structure** — graphify_certification_decisions_graph_protocol_objective, graphify_certification_decisions_graph_protocol_corpus_inclusion_exclusion, graphify_certification_decisions_graph_protocol_expected_families, graphify_certification_decisions_graph_protocol_expected_relationships, graphify_certification_decisions_graph_protocol_acceptance_criteria, graphify_certification_decisions_graph_protocol_downstream_impact [EXTRACTED 1.00]

## Communities (22 total, 3 thin omitted)

### Community 0 - "Trades Certification"
Cohesion: 0.09
Nodes (33): Trades Provisional Certification Policy Document, Provisional Certification Policy, Trades Review 1m Reference Alignment Document, Review 1m Reference Alignment, Trades Review Microstructure Document, Review Microstructure, Trades Reference Scale Mismatch Document, Reference Scale Mismatch (+25 more)

### Community 1 - "Reference Certification"
Cohesion: 0.08
Nodes (28): Good Review Bad Certification States, Daily Closeout, Daily Final Policy, Daily Hard Invalid Exclusion, VW Illiquidity Review, Contrato Halts, Halts As Event Truth, OHLCV 1m Closeout (+20 more)

### Community 2 - "Halts Certification"
Cohesion: 0.10
Nodes (21): Contrato Additional, Additional Subblock Policy, Empty Placeholders Not Failure, Additional Causal Overlay Closeout, Additional Causal Overlay Policy, Additional Closeout, Additional Final Policy, Corporate Actions Additional Review (+13 more)

### Community 3 - "Additional Certification"
Cohesion: 0.18
Nodes (17): Additional Current State, Additional Subblock Policy, Additional Corporate Actions Secondary To Reference, Additional Ambiguous Multi Ticker News, Additional Six Subblocks, Additional Closeout, Additional Accepted Heterogeneous Block, Final Certification Process (+9 more)

### Community 4 - "Quotes Certification"
Cohesion: 0.17
Nodes (16): Persistent Soft Crossed Mid Large Scale Review Decision, Persistent Soft Crossed Mid Large Scale, Halt Explains But Does Not Clean Book, Large File Threshold Edge Hard Many Crosses Review Decision, Large File Threshold Edge Hard Many Crosses, Large File Mixed Severity Tail, Medium File Threshold Edge Hard Many Crosses Bad Decision, Medium File Threshold Edge Hard Many Crosses (+8 more)

### Community 5 - "Halts Certification 2"
Cohesion: 0.17
Nodes (15): Bad Unusable Event Marginal Residue, Halts Quality Policy, Halts Good Review Bad Quality States, Halts Closeout, Halts Accepted Event Truth Layer, Halts Final Quality Policy, Reference Identity Mostly Recovered, Reference Causal Value (+7 more)

### Community 6 - "Quotes Certification 2"
Cohesion: 0.19
Nodes (13): Quotes Certification Contract, Quotes Expected Not Closed, Quotes Present Materialization, Quotes Usable Policy, Quotes Expected Presence Logic, Quotes Expected Constraints, Synthetic Expected Set Deferred, Quotes Quality Policy (+5 more)

### Community 7 - "Daily Certification"
Cohesion: 0.22
Nodes (11): Daily Current State, Daily Recovery And Coverage, Daily Coverage Recovery, Daily Quality Policy, Daily Hard Invalid Tail, Daily Closeout, Daily Problematic 57 Review Not Rehabilitated, Daily Recovery States (+3 more)

### Community 8 - "Trades Certification 2"
Cohesion: 0.22
Nodes (11): Certification Decisions Graph Governance, Graphify Governance README, 57f Full Clean Fast Same Schema, Trades Current State Document, Trades Base Certification Decision Document, Three Layer Certification Base, Trades Certification Decision, Trades Old Versus New Bucket Bridge Document (+3 more)

### Community 9 - "Graphify Governance"
Cohesion: 0.33
Nodes (10): Graphify Official Build Protocol, Certification Decisions Graph, Expected Present Healthy Usable For, Leaf Graph Family, Notebooks Separate Leaf, Official Graphify Build, Recovery And Exclusion, Graphify Refresh Queue (+2 more)

### Community 10 - "Quotes Certification 3"
Cohesion: 0.22
Nodes (10): Quotes Certification Guide, Quotes Auditoria Master Sources, Quotes Certification Assembly Scope, Quotes Artifact Mapping, Quotes Canonical Certification Artifacts, Quotes Final Certification Artifact Gap, Quotes Certification Table Spec, Quotes Table Grain Ticker Date (+2 more)

### Community 11 - "Short Certification"
Cohesion: 0.29
Nodes (10): Short Current State, FINRA Short Baseline, Only Polygon Gap Overstated, Polygon Short Secondary Context, Short Recovery And Limits, Short Recoverable Context, Short Recovery Limits, Short Closeout (+2 more)

### Community 12 - "Global Metrics"
Cohesion: 0.25
Nodes (9): Global Metrics Tables, Global Quantitative Summary Tables, Global Metrics Tables Traceable, Global Metrics Source Artifact Traceability, Global Metrics Working Links, Global Metrics Tables Traceable Plain Paths, Global Metrics Plain Path Traceability, Global Metrics Manifest (+1 more)

### Community 13 - "OHLCV 1m Certification"
Cohesion: 0.29
Nodes (8): 1m Current State, 1m Recovery Policy, 1m Rescue Over Quarantine, 1m Quality Policy, 1m Good Review Bad Buckets, 1m VW Taxonomy, 1m Closeout, 1m Full Scope Caveat

### Community 14 - "Graphify Governance 2"
Cohesion: 0.39
Nodes (8): Acceptance Criteria, Corpus Inclusion And Exclusion, Certification Decisions Graph Protocol, Downstream Impact, Expected Data Families, Expected Graph Relationships, Notebooks Future Leaf, Certification Decisions Graph Objective

### Community 15 - "Short Certification 2"
Cohesion: 0.32
Nodes (8): Contrato Short, FINRA Baseline, Short Market Link, Short Root Cause Audit Phase 1 Closeout, Days To Cover ADV Zero Review, FINRA Short Volume Superior, Polygon Secondary Provider, Short Structural Phase 1 Decision

### Community 16 - "Halts Certification 3"
Cohesion: 0.33
Nodes (7): Halts Current State, Halts Solid Event Layer, Halts Overlay And Recovery, Halts Microstructure Overlay, Halts Problem Flags Context, Short Causal Overlay Closeout, Short Context Not Universal Cause

### Community 17 - "Trades Certification 3"
Cohesion: 0.38
Nodes (7): Reference Current State, Reference As Partial Causal Layer, Splits To Trades Narrow Signal, Trades Acceptance Counts Distribution, Trades Current State From Raw Shards, Trades Raw Shard Progress Snapshot, Trades Recompute Running Metadata

### Community 18 - "OHLCV 1m Certification 2"
Cohesion: 0.50
Nodes (4): Daily Agent02 Agent03 Contract, Daily File Validation Contract, OHLCV 1m Agent02 Agent03 Contract, Minute File Validation Contract

## Knowledge Gaps
- **57 isolated node(s):** `Additional Root Cause Audit Phase 1 Closeout`, `Additional Causal Overlay Closeout`, `Daily Agent02 Agent03 Contract`, `Contrato Halts`, `Halts Causal Overlay Closeout` (+52 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Quotes Open Bucket Final Classification` connect `Quotes Certification` to `Quotes Certification 2`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `Transversal Layer Strength For Quotes Residue` connect `Quotes Certification` to `Trades Certification 3`, `Halts Certification 2`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Recovery And Exclusion` (e.g. with `Empty Placeholders Not Failure` and `Daily Hard Invalid Exclusion`) actually correct?**
  _`Recovery And Exclusion` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Additional Root Cause Audit Phase 1 Closeout`, `Additional Causal Overlay Closeout`, `Daily Agent02 Agent03 Contract` to the rest of the system?**
  _58 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Trades Certification` be split into smaller, more focused modules?**
  _Cohesion score 0.0928030303030303 - nodes in this community are weakly interconnected._
- **Should `Reference Certification` be split into smaller, more focused modules?**
  _Cohesion score 0.07936507936507936 - nodes in this community are weakly interconnected._
- **Should `Halts Certification` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._