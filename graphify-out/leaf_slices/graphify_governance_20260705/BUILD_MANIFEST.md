# graphify_governance_20260705 Graphify Leaf Manifest

Date: 2026-07-05
Status: runtime, reconstructible Graphify leaf output.

Scope: project operating system, agent rules, Graphify protocol, refresh queue, architecture, research governance and minute-data operating constraints
Leaf output: `C:\TSIS_Data\graphify-out\leaf_slices\graphify_governance_20260705`

## Graph Build Baseline

```yaml
graph_build_git_branch: integrate/main-data-quality-dossiers-20260613
graph_build_git_commit: f94bc013059e7c815efa4055c0d26e5c4b1165b9
graph_build_dirty_state: true
graph_build_dirty_paths_count: 122
graph_build_timestamp_utc: 2026-07-05T19:40:20.393422+00:00
graphify_package_version: 0.9.1
graphify_skill_path: C:\Users\AlexJ\.codex\skills\graphify\SKILL.md
graphify_skill_sha256: 671a0c8e70cc7a74621fa072c118068bc428f4c025f254c6465c5034027bb510
no_api_mode: true
semantic_extraction_mode: deterministic_curated_topology_extraction
build_from_json_root_or_equivalent: C:\TSIS_Data
root_graph_updated: false
queue_entries_left_pending: pending review after 20260705 leaf refresh
```

Important limitation:

```text
This governance leaf is built against the current working tree. It does not restore deleted/moved documents; missing baseline files are recorded and the dirty snapshot is explicit in BUILD_MANIFEST.md.
```

### Dirty Paths

```text
D 00_CTO/00_CTO_REFACTOR_PLAN.md
 D 00_CTO/00_TSIS_PAPERS/00_private.md
 M 00_CTO/00_private/notas_agentes_inicio.md
 M 00_CTO/01_RESEARCH_PHILOSOPHY/README.md
 D 00_CTO/01_RESEARCH_PHILOSOPHY/alpgaenvolve_vs_statics.md
 M 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/AlphaEnvolve_en_Tsis.md
 M 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/areas_de_trabajo.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_ARCHITECTURE.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_EXPERIMENTS.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_LEARNING_ROADMAP.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_OPEN_QUESTIONS.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_OVERVIEW.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_RESEARCH_LOG.md
 D 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/ALPHAEVOLVE_TSIS_VISION.md
 M 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/README.md
 M 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/README.md
 M 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/AlphaEnvolve.md
 M 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/market_state_tables_status_and_operating_map_2026_07_01_v3.md
 M 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md
 M 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/runbooks/2026-06-12_data_audit_agent_prompt_pack.md
 M 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/runbooks/2026-06-13_shutdown_handoff_note.md
 M 00_CTO/13_TRADING_SYSTEMS/00_EVENT_LIBRARY/traders_strategies/EDUTRADES_LONG_PLAYS_SOURCE_EVENT_INDEX_v0_1.md
 M 00_CTO/13_TRADING_SYSTEMS/README.md
 M 00_CTO/13_TRADING_SYSTEMS/revision.md
 M 00_CTO/CHANGELOG.md
 M 00_CTO/GRAPHIFY_REFRESH_QUEUE.md
 M 00_CTO/LOCAL_RULES.md
 M 00_CTO/README.md
 D 00_CTO/TSIS_LAB_ARCHITECTURE.md
 D 00_CTO/TSIS_LAB_ARCHITECTURE_v2.md
 M 00_CTO/tests/README.md
 M 00_CTO/tests/architecture_contracts/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/intraday_1m_strategy_candidate_events_table_schema_contract.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml
 M 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/master_intraday_bar_table_registry_entry.yaml
 M 01_TSIS_backtest_SmallCaps/01_foundations/inspection_dossiers/reference/reference_upgrade_agent_prompt_2026-06-12.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_table_validators_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_candidate_tables_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/master_intraday_bar_table_quote_guarded_candidate_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_builder_contract_v0_1.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/event_state_table_validators.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/market_state_table_validators.md
 M 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/outcomes_table_validators.md
 M 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
 M 01_TSIS_backtest_SmallCaps/CHANGELOG.md
 M 01_TSIS_backtest_SmallCaps/README.md
 M 01_TSIS_backtest_SmallCaps/configs/data_foundation_outputs/master_intraday_bar_table_quote_guarded_candidate_v0_2.json
 M 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_intraday_quote_guarded_candidate_contract.py
 M 02_TSIS_webSocket_SmallCaps/AGENTS.md
 M 02_TSIS_webSocket_SmallCaps/LOCAL_RULES.md
 M AGENTS.md
 D ARCHITECTURE_OVERVIEW.md
 M CHANGELOG.md
 M PROJECT_OPERATING_SYSTEM.md
 M PROJECT_RULES.md
 M README.md
 M RESEARCH_PHILOSOPHY.md
 M START_HERE.md
 M VERSIONING_STANDARDS.md
 M tests/institutional/README.md
?? 00_CTO/01_RESEARCH_PHILOSOPHY/00_CTO/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/00_MANIFESTO/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/01_KNOWLEDGE_MODEL/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/02_EXPERIMENTAL_METHOD/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/03_HUMAN_AND_AI_RESEARCHERS/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/04_MARKET_SCIENCE_PHILOSOPHY/
?? 00_CTO/01_RESEARCH_PHILOSOPHY/05_07_2026.md
?? 00_CTO/01_RESEARCH_PHILOSOPHY/05_RESEARCH_GOVERNANCE/
?? 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/00_AlphaEvolve_vs_sobreoptimizacion.md
?? 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/01_ALPHAEVOLVE_TSIS_VISION.md
?? 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/01_AlphaEvolve/00_CTO/02_ALPHAEVOLVE_AS_RESEARCH_EXPERIMENT_GENERATOR_v0_1.md
?? 00_CTO/11_MARKET_SCIENCE/010_portfolio/
?? 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/00_CTO/05_07_2026.md
?? 00_CTO/11_MARKET_SCIENCE/09_ImitationLearneing/
?? 00_CTO/98_TSIS_ours_PAPERS/
?? 00_CTO/TSIS_LAB_ARCHITECTURE_v3.md
?? 00_CTO/_archive/
?? 00_CTO/graphify-out/leaf_slices/graphify_governance_20260705/
?? 00_CTO/graphify-out/leaf_slices/market_state_representation_20260705/
?? 00_TSIS_Lab/
?? 01_TSIS_backtest_SmallCaps/01_foundations/graphify-out/leaf_slices/data_foundation_outputs_topology_20260705/
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/event_research_design_contract_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_contract_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_state_controlled_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_event_windows_controlled_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_outcomes_controlled_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md
?? 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/graphify-out/leaf_slices/certification_decisions_topology_20260705/
?? 01_TSIS_backtest_SmallCaps/scripts/graphify/build_certification_decisions_topology_leaf_20260705.py
?? 01_TSIS_backtest_SmallCaps/scripts/graphify/build_graphify_governance_refresh_20260705.py
?? 01_TSIS_backtest_SmallCaps/scripts/graphify/build_project_graphify_refresh_20260705.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_daily_strategy_event_windows_candidate.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_event_state_intraday_quote_guarded_candidate.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_intraday_1m_event_outcomes_candidate.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_intraday_1m_strategy_candidate_events_from_master_intraday_quote_guarded.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_intraday_1m_strategy_event_windows_candidate.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_market_state_intraday_quote_guarded_candidate.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_sample.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_master_intraday_quote_guarded_candidate_scoped.py
?? 01_TSIS_backtest_SmallCaps/scripts/materialize_strategy_candidate_events_table.py
?? 01_TSIS_backtest_SmallCaps/scripts/preflight_master_intraday_quote_guarded_candidate.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_daily_strategy_event_windows_candidate_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_event_state_intraday_quote_guarded_candidate_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_1m_event_outcomes_candidate_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_1m_strategy_candidate_events_from_master_intraday_qg.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_intraday_1m_strategy_event_windows_candidate_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_market_state_intraday_quote_guarded_candidate_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_intraday_quote_guarded_candidate_sample_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_master_intraday_quote_guarded_candidate_scoped_builder.py
?? 01_TSIS_backtest_SmallCaps/tests/data_foundation_outputs/test_strategy_candidate_events_table_builder.py
?? graphify-out/
```

## Corpus

```text
- 00_CTO/01_RESEARCH_PHILOSOPHY/05_07_2026.md | sha256=99a1a546ef259c9897bf1d9edc43cc7ab4c90eceb0860e8cc094319a81f7f95b | lines=204 | words=430
- 00_CTO/01_RESEARCH_PHILOSOPHY/README.md | sha256=7215451392061246a2373894da223a9b1aed56f06ca40fd459a64865ff05604e | lines=60 | words=116
- 00_CTO/10_AUTONOMOUS_RESEARCH_SYSTEMS/README.md | sha256=6c5fb0e2a87da38f1bac1953576287c2e07a44923cc4c64834ed69e053b8c659 | lines=80 | words=141
- 00_CTO/11_MARKET_SCIENCE/README.md | sha256=3cdd83ae86571dd98f8f31582410104b394bfceb9f9d4e78d7b469f4097eff44 | lines=771 | words=1001
- 00_CTO/CHANGELOG.md | sha256=89942df32b4b31e688b0d7bd86afd56d3eb3b80521135f36c89fac9aeb583ac4 | lines=1294 | words=6868
- 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=b733769c0cadfe06e3cb791511b66878664c8b713111d274991d7db842f94040 | lines=472 | words=2061
- 00_CTO/GRAPHIFY_REFRESH_QUEUE.md | sha256=d09ee7f497bc20bb10f61e4091d2d13ca8a54a14d455cf8593079c094d4c9ef7 | lines=2254 | words=5803
- 00_CTO/LOCAL_RULES.md | sha256=e43f85d8642c85ab3f9ea01cacbb967a41d217f40e43ca788af9d40ae9412fed | lines=364 | words=981
- 00_CTO/README.md | sha256=2a66fb18fc307b5d2eabce2644e9bc25c916aed6039943e5f3899ecbc9fdb5cd | lines=1102 | words=3619
- 00_CTO/TSIS_LAB_ARCHITECTURE_v3.md | sha256=d46ad89d7453f03496859f059c29dd05b5d0635615ead6bbddf5eb669445ae27 | lines=678 | words=1341
- 00_TSIS_Lab/00_CTO/00_privado.md | sha256=29596c7c7d59e103447ffb85fab1baec1325f80ad43b53c3026a3eba2d8ba6c0 | lines=229 | words=402
- 00_TSIS_Lab/00_CTO/01_privado2.md | sha256=006a19e36f40b302860f46bcf08cd93098b28ca8c2e41df2799845d7f32f5391 | lines=68 | words=206
- 00_TSIS_Lab/01_contracts/knowledge_object_promotion_contract_v0_1.md | sha256=81bbee20b3c47da0259528c168c5d896728c6bc88562d3798a9e0b1d4173d3d6 | lines=63 | words=104
- 00_TSIS_Lab/01_contracts/parameter_sweep_protocol_v0_1.md | sha256=bfe6a0915950d1f5c3bb491cd286954eaae30ed294f4ec987f5e749ad9aa998c | lines=76 | words=217
- 00_TSIS_Lab/01_contracts/research_experiment_contract_v0_1.md | sha256=93bb5990ab64399e46947d243e123a613931e7d430cc969fa484d87f0689209b | lines=144 | words=258
- 00_TSIS_Lab/01_contracts/research_experiment_execution_protocol_v0_1.md | sha256=397e997d8b1ffd5bdcd5cc757a9232d05bb3666a30822d524bd694016fbc7c3f | lines=131 | words=314
- 00_TSIS_Lab/01_contracts/scientific_validation_pipeline_contract_v0_1.md | sha256=46c38ca4b798107eeea41c1f57ce8ec50dbcffecb951393b3fb0abd365d935e5 | lines=70 | words=145
- 00_TSIS_Lab/02_registries/knowledge_object_registry_v0_1.md | sha256=375d17dc15069176163002117a1565028da155e781a845d936c41252c3bec88a | lines=13 | words=38
- 00_TSIS_Lab/02_registries/research_experiment_registry_v0_1.md | sha256=85b7d8a49fe489f64049f8c927d942314c9decbe929f52d99ad929b9cff12d8d | lines=12 | words=42
- 00_TSIS_Lab/03_templates/evidence_report_template.md | sha256=99da9b3adf089e9e66d5c8ddb40065a86f5afc418e87921331b45c1bfa5d933e | lines=36 | words=28
- 00_TSIS_Lab/04_experiments/_archive/superseded_2026_07_05/EXP_INTRADAY_MOMENTUM_EXTENSION_0001/README.md | sha256=67fb96aca1f1de55b7e79b17758008a1fb275fe38600b07005c58c989f421d56 | lines=71 | words=180
- 00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/README.md | sha256=1b3da571915fbac6cd89ca17b393bfde50d77fa572d2e0e5c518e36d19f04566 | lines=81 | words=297
- 00_TSIS_Lab/04_experiments/EXP_DAS_FRONTSIDE_DISCOVERY_0001/research_design.md | sha256=4a800e4736b8008a4ec4bf3dbe0d42adcf25f9009d860709f18f7585f5409f77 | lines=613 | words=1784
- 00_TSIS_Lab/05_adapters/smallcaps/data_sources.md | sha256=dc8d2113aabe632f57e2d7feb55c05625d4749720fa1e86292467bd6842d48d1 | lines=16 | words=31
- 00_TSIS_Lab/05_adapters/smallcaps/execution_bridge.md | sha256=2060f54bb9fa6687c1414f28ddc831b104ca045861bcd479a55c788ab8c04bdd | lines=25 | words=53
- 00_TSIS_Lab/05_adapters/smallcaps/README.md | sha256=eb7597220f23fd907c0c962fa23efe6636b580ed43c0866de7ffcc0e1f6acb17 | lines=23 | words=86
- 00_TSIS_Lab/README.md | sha256=89d2f21c8499d8a0a507c0be5f1f76ed25b7346b0f4505b591edb71879d5f868 | lines=120 | words=300
- 01_TSIS_backtest_SmallCaps/01_foundations/CHANGELOG.md | sha256=941f65e69df01258d6ab80e41f9f5da1c8965791ca8f743163ca16e4457ff467 | lines=424 | words=2534
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=0bf911d640c30bd6a0928ef55a4b4959a2212ec21adb85e1f237a05a17985345 | lines=512 | words=1721
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md | sha256=5cb34ef49646cedba6f3dfa763f928c28622704dfcb2d43ca16ddba7aada46a7 | lines=5661 | words=13946
- 01_TSIS_backtest_SmallCaps/01_foundations/LOCAL_RULES.md | sha256=52c4b7e0648c41b93aff994de8149837280d8473b629dbbc610d86ce35013f71 | lines=179 | words=561
- 01_TSIS_backtest_SmallCaps/01_foundations/README.md | sha256=edfc0f5f9e55d4e128df2eb52a8f151ac2e8cbff1d611d865796b6e27b5a935b | lines=834 | words=4668
- 01_TSIS_backtest_SmallCaps/AGENTS.md | sha256=67e6a6bc28411afba0d9fb26aa906da251f3afd3b057bad0c21e9949b22e564c | lines=340 | words=1265
- 01_TSIS_backtest_SmallCaps/CHANGELOG.md | sha256=30a2af69e5bbfc52a51d787f2f11d7c31b2e88cf16bb27916447b81b859248f6 | lines=6895 | words=23678
- 01_TSIS_backtest_SmallCaps/LOCAL_RULES.md | sha256=60c324fb8e6a2487ac249012852f2f25ea4e7f81a533ab8e6c231feb875cedec | lines=240 | words=943
- 01_TSIS_backtest_SmallCaps/README.md | sha256=11fa5e305e805244d1f9457bbf239f27031d560d12351ebc72c2832cd5bbb951 | lines=248 | words=742
- AGENTS.md | sha256=8f224c48e817071284233b67d0606c825f79a5d4cb5c2e34f64e486fa702c02d | lines=424 | words=1768
- CHANGELOG.md | sha256=22388cb68b8a384d7cbac9dbf28cc0069f65f03f79ac8a704b26ffa8c09891af | lines=691 | words=2236
- LONG_RUNNING_OPERATIONS_CONTRACT.md | sha256=6d9decd8cbcb794131d1a9970f49d0f58bafbc09923899f875a61f1dd05fcbdb | lines=375 | words=1328
- PROJECT_OPERATING_SYSTEM.md | sha256=8bf36cd68c5fc719a49778986428ffb45de5d8d62e0677c90330f0ccb3dce56f | lines=466 | words=1718
- PROJECT_RULES.md | sha256=d84d307190cc49d39c61a37fb68dd1fcdd551e281bb2f6b2275747c63e418972 | lines=626 | words=2556
- README.md | sha256=58f81dcd2bb11d5a96190156fae3a838d842405c2cc70a68d1695d3404adbe85 | lines=86 | words=252
- RESEARCH_PHILOSOPHY.md | sha256=0f15329e706e500c33ee58a095e75e6e20cd0fc1df1b2b0a90ee2fac17720518 | lines=725 | words=2806
- START_HERE.md | sha256=20a3b3452e6cfe820292b859b6efdbe2b62612efb90bba3f405fc63d3c5efc43 | lines=459 | words=1822
- VERSIONING_STANDARDS.md | sha256=138937f6bf3f62ef863dbce25a5f79ae630edc56304bffb413369cd3408cfac8 | lines=1404 | words=3968
```

## Missing Components

```text
- none
```

## Leaf Stats

```yaml
extraction_nodes: 57
extraction_edges: 252
extraction_hyperedges: 1
nodes: 57
edges: 252
communities: 9
detected_files: 45
detected_words_approx: 95358
community_labels:
  0: Graph Cluster 0
  1: Graph Cluster 1
  2: Graph Cluster 2
  3: Graph Cluster 3
  4: Graph Cluster 4
  5: Graph Cluster 5
  6: Graph Cluster 6
  7: Graph Cluster 7
  8: Graph Cluster 8
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
