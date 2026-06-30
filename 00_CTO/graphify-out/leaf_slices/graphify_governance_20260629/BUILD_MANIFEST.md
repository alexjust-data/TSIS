# Graphify Governance Leaf Manifest

Date: 2026-06-29
Status: runtime, reconstructible Graphify leaf output.

Scope: cross-project Graphify governance contracts for `00_CTO`, `01_foundations`, and `00_data_certification`.
Leaf output: `C:\TSIS_Data\00_CTO\graphify-out\leaf_slices\graphify_governance_20260629`

## Graph Build Baseline

```yaml
graph_build_git_branch: integrate/main-data-quality-dossiers-20260613
graph_build_git_commit: 362a031efd006fe44f5c1a775d1ee3af80634767
graph_build_dirty_state: true
graph_build_timestamp_utc: 2026-06-29T08:02:47.807759+00:00
graphify_package_version: 0.9.1
graphify_skill_path: C:\Users\AlexJ\.codex\skills\graphify\SKILL.md
graphify_skill_sha256: 671a0c8e70cc7a74621fa072c118068bc428f4c025f254c6465c5034027bb510
graphify_upstream_reference: https://github.com/safishamsi/graphify
graphify_installed_vs_protocol_status: aligned_to_0_9_1_before_build
no_api_mode: true
semantic_extraction_mode: codex_host_inline_manual_semantic_extraction
gemini_api_key_present: false
build_from_json_root_or_equivalent: C:\TSIS_Data
semantic_update_coverage: curated_governance_docs_only
root_graph_updated: false
queue_entries_covered:
  - graphify_governance_protocol_alignment
  - build_manifest_commit_and_corpus_baseline
  - no_api_graphify_semantic_extraction_rule
next_delta_commands:
  - git diff --name-status 362a031efd006fe44f5c1a775d1ee3af80634767...HEAD
  - git status --short
```

Dirty paths are recorded because this leaf was built against the current working
tree. This leaf is not a promotion of every dirty path; it only covers the
corpus listed below.

### Dirty Paths

```text
D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/07_Long_plays.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/07_Short_Plays.md
 D "00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/Day Trading en Small Caps - XVNTrading.pdf"
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Crowded_Ticker_Context/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Float_Rotation/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Liquidity_Gain_Loss/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Neutralized_Area/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Pattern_Variation_Acceptable_Range/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Short_Seller_Trap_Layers/FACTOR.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Volume_Prediction/FACTOR.md
 M 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_case_explorer.ipynb
 M 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_widgets.py
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Dip_Buying_Multi_Day_Runner/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Gap_Up_Buying/STRATEGY.md
 M 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Bounce_Plus_Gap_Up_Short/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Bounce_Short/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Intraday_Top/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Layer_Resistance/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/First_Red_Day/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/First_Red_Day/estrtategia.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Gap_Up_Short/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Multi_Day_Top_Risk_Reward/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Parabolic_Breakout_Failed_Breakout/STRATEGY.md
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/STEVEN_DUX_SOURCE_STRATEGY_INDEX_v0_1.md
 M 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/strategy_widgets_common.py
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/000CAR.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/001SLV.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/003BIRD.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/004BRID.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/005EEIQ.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/006EEIQ.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/007ASTC.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/01_30.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/02SLV.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/02_40.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/04_51.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/06_00.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/07_41.png
 D 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/08ASTC.png
 M 00_CTO/13_TRADING_SYSTEMS/README.md
 M 00_CTO/CHANGELOG.md
 M 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
 M 00_CTO/GRAPHIFY_REFRESH_QUEUE.md
 M 00_CTO/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
 M 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
 M 01_TSIS_backtest_SmallCaps/CHANGELOG.md
 M 01_TSIS_backtest_SmallCaps/scripts/data_ops/clone_quotes_to_staging.ps1
 M 01_TSIS_backtest_SmallCaps/scripts/monitor_long_running_operation.ps1
 M 01_TSIS_backtest_SmallCaps/scripts/run_1m_split_normalized_materialization.ps1
 M 01_TSIS_backtest_SmallCaps/scripts/validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1
 M CHANGELOG.md
 M LONG_RUNNING_OPERATIONS_CONTRACT.md
 M PROJECT_RULES.md
?? 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/01_Steven_Dux/
?? 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/03_Edu_Trades/
?? 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/04_Xavineta/
?? 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/README.md
?? 00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/999.png
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md
?? 01_TSIS_backtest_SmallCaps/scripts/graphify/
```

### Delta Since Build Commit

```text
(no committed delta from HEAD)
```

## Procedure

- Controlled corpus selected from root, `00_CTO`, `01_foundations`, and `00_data_certification` governance docs.
- Graphify package and Codex skill were aligned to `graphifyy 0.9.1` before build.
- No external API key was required or requested.
- Semantic extraction was performed inline by the host Codex agent using the Graphify extraction schema.
- Official Graphify `build_from_json` assembly was used.
- Official Graphify community detection, JSON export, HTML export, report generation and diagnostics were used.
- Root `00_CTO/graphify-out/graph.json` was intentionally not updated.

## Corpus

Inclusion rules:

```text
- root governance docs required by AGENTS.md
- Graphify official build protocols
- Graphify refresh queues
- Graphify table/design protocol for Data Foundation graph coupling
- long-running operations contract
```

Exclusion rules:

```text
- no raw data
- no data_foundation_outputs materializations
- no graphify-out historical graph payloads
- no notebooks
- no images
- no private documents beyond explicit governance files
```

Corpus files:

```text
- AGENTS.md | sha256=27550fec14ebbdfbca71bc3d41953aace87541b9b97b2e5a987fc9d8376229c3 | lines=385 | words=1460
- CHANGELOG.md | sha256=44c2cb02e051367ec9b6612e652d3055b0704df5f45c1acdd4abf45c3a1a724e | lines=446 | words=968
- PROJECT_OPERATING_SYSTEM.md | sha256=52a02ff0cc8e91c76aa1f0e6bcabd13d1566aef6c3157321995baa6b29d58241 | lines=330 | words=1244
- PROJECT_RULES.md | sha256=b84c483eaf82ea6f1042fecf36f27b035c6de4c98a929b4f4ee8693385a73f18 | lines=579 | words=2334
- VERSIONING_STANDARDS.md | sha256=13550868a8997b181cb0ff88532a74e415ac737ba3c2f78dcb0a1b7c7b17d6a7 | lines=1151 | words=3312
- ARCHITECTURE_OVERVIEW.md | sha256=b36bdc3c6286a108db5a3e4a3863b03b97dc261c76ba7077b48e25227e5c2429 | lines=1 | words=5
- RESEARCH_PHILOSOPHY.md | sha256=dc61561620e0e3b7cddfa0ce1759f2f622266139b07caba9f78de846ee9abbda | lines=567 | words=2353
- LONG_RUNNING_OPERATIONS_CONTRACT.md | sha256=6d9decd8cbcb794131d1a9970f49d0f58bafbc09923899f875a61f1dd05fcbdb | lines=375 | words=1328
- 00_CTO/LOCAL_RULES.md | sha256=cd50fc6d4d808d2a42f7366c6f4e80b5e219da0c3dc413da4521b0cbd4167390 | lines=363 | words=981
- 00_CTO/README.md | sha256=441461ccc6a864cfec10d79500b238fad5c774806718eee4b8174bfab7856c7c | lines=1029 | words=3387
- 00_CTO/CHANGELOG.md | sha256=4d8af7f60b9290ac98c543b55593782f68591b0f6c2f796462d8429a12bdc8ac | lines=1039 | words=4696
- 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=bcd7f3a4d8e6ca088b6d6b14961bc0231ad5190e2df30aaabface9f8a79ed275 | lines=450 | words=1980
- 00_CTO/GRAPHIFY_REFRESH_QUEUE.md | sha256=1dea8426d3e8c77f6a88407c462d1465d740d196f5aecfc408975df597e7b73b | lines=783 | words=1806
- 01_TSIS_backtest_SmallCaps/LOCAL_RULES.md | sha256=60c324fb8e6a2487ac249012852f2f25ea4e7f81a533ab8e6c231feb875cedec | lines=240 | words=943
- 01_TSIS_backtest_SmallCaps/CHANGELOG.md | sha256=ad50f2143794961fe215da920ad89e67603fa53c9cf4cd9317cc5a7f6fcc4da2 | lines=5574 | words=18625
- 01_TSIS_backtest_SmallCaps/01_foundations/README.md | sha256=f56332fd67a7f13cbc7c527dfc62a49b3f4508832aa4ec8be11d52f604f6a06c | lines=806 | words=4521
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=20ecf3a3199e0490b510d8c78195b3a9eafe8178bf8312ea8e552356264fbd73 | lines=488 | words=1627
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md | sha256=51c9aeef9fad062b283682ee4a54b0b15e5d1319f4326e9393bfb64d21bf619a | lines=3816 | words=9404
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/README.md | sha256=e9a6a435ef3db945b828f428a1f32b4dc6248d44aa6d17b47b00715eed2303aa | lines=152 | words=509
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/graphify/data_foundation_graph_and_table_design_protocol.md | sha256=b1b7cb3084f823eb24ade1956a931e9b61e4e57fd8b78edf80f4549ae0ea2e1e | lines=600 | words=1551
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=48b78fa64a293a238fd729d022170a752e0f965da932560e98c7a5809bc4aec7 | lines=280 | words=954
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md | sha256=4b0e79ea52558d4442a53d99f25e75e6801a81a11e093769c495aa90b24c0e09 | lines=342 | words=787
```

## Leaf Stats

```yaml
extraction_nodes: 39
extraction_edges: 65
extraction_hyperedges: 2
nodes: 39
edges: 65
communities: 10
detected_files: 22
detected_words_approx: 64775
community_labels:
  0: Refresh Queue Control
  1: Operational Telemetry
  2: Refresh Queue Control
  3: Certification Graph
  4: Agent Traceability
  5: Governance Cluster 5
  6: Governance Cluster 6
  7: Agent Traceability
  8: Refresh Queue Control
  9: Data Foundation Graph
```

## Diagnostic

```yaml
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_same_endpoint_collapsed_edges: 0
undirected_same_endpoint_collapsed_edges: 0
```

## Build Notes

- This is a leaf refresh only.
- This leaf establishes the governance graph standard for the next larger rebuilds.
- It does not claim full semantic coverage of `00_CTO`, `01_foundations`, or `00_data_certification`.
- The next work item is to rebuild each root through bounded leaves and merge only after diagnostics are clean.
