# Certification Decisions Topology Graphify Leaf Manifest

Date: 2026-07-05
Status: runtime, reconstructible Graphify leaf output.

Scope: deterministic topology refresh for `00_data_certification` certification decisions.
Leaf output: `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\graphify-out\leaf_slices\certification_decisions_topology_20260705`

## Graph Build Baseline

```yaml
graph_build_git_branch: integrate/main-data-quality-dossiers-20260613
graph_build_git_commit: f94bc013059e7c815efa4055c0d26e5c4b1165b9
graph_build_dirty_state: true
graph_build_timestamp_utc: 2026-07-05T19:40:20.405719+00:00
graphify_package_version: 0.9.1
graphify_skill_path: C:\Users\AlexJ\.codex\skills\graphify\SKILL.md
graphify_skill_sha256: 671a0c8e70cc7a74621fa072c118068bc428f4c025f254c6465c5034027bb510
graphify_upstream_reference: https://github.com/safishamsi/graphify
graphify_installed_vs_protocol_status: aligned_to_0_9_1_before_build
no_api_mode: true
semantic_extraction_mode: deterministic_certification_decision_topology
build_from_json_root_or_equivalent: C:\TSIS_Data
semantic_update_coverage: controlled_certification_decisions_topology
corpus_manifest_path: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\graphify-out\leaf_slices\certification_decisions_topology_20260705\corpus_manifest.json
corpus_file_count: 88
queue_entries_covered:
  - GFQ-20260628-002 graphify no-API and version-alignment protocol
  - GFQ-20260628-001 graphify build baseline provenance rule
queue_entries_left_pending:
  - full semantic refresh of certification_decisions_graph if field-level/case-level reasoning is required
diagnostics_command: graphify diagnose multigraph --graph "C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\graphify-out\leaf_slices\certification_decisions_topology_20260705\graph.json" --json
next_delta_commands:
  - git diff --name-status f94bc013059e7c815efa4055c0d26e5c4b1165b9...HEAD
  - git status --short
```

Important limitation:

```text
This leaf is a deterministic topology refresh. It maps families, documents,
doc types and explicit decision keywords from the controlled certification
corpus. It does not replace the 2026-06-19 semantic certification decisions
leaf and must not be presented as a full semantic re-extraction of every
closeout/policy body.
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

Inclusion rules:

```text
- certification/**/*.md
- certification/global_metrics/*.json
- auditoria/**/*closeout*.md
- auditoria/**/*policy*.md
- auditoria/**/*contrato*.md
- local Graphify governance docs
```

Exclusion rules:

```text
- graphify-out/
- notebooks
- parquet/csv
- images
- runtime/cache folders
- physical evidence assets
```

Corpus files:

```text
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/01_contrato_additional.md | sha256=0b71264b7f244f3e834f3da110218ef077ca5b6d3e845e46e029fcbec4125142 | family=additional | doc_type=contract | words=692
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/03_additional_root_cause_audit_phase1_closeout.md | sha256=3abfacd1c79921081be722ee11662ebf8f6829363a45ef766d7361b46ad63371 | family=additional | doc_type=closeout | words=428
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_causal_overlay_closeout.md | sha256=6d3b77aef15b2623190707469f49cc087d289bf9e31f4a9716489df223957cb4 | family=additional | doc_type=closeout | words=603
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/additional/04_additional_closeout.md | sha256=3caea6f023061518fdae09cfb9a7efd2ac31ab60cd33ce6d99bdfa5a6c4e6de0 | family=additional | doc_type=closeout | words=531
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/01_contrato_agent02_agent03_daily_04032026.md | sha256=0ef7a5cb968e5c76d1185fde6952b94cac1c136f8d20af0199f46e76cbdae6c8 | family=daily | doc_type=contract | words=944
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/daily/04_daily_closeout.md | sha256=abcbe63db5117ee604ad27cc5b777503d5c3bde10a1b302a1c9633102034587a | family=daily | doc_type=closeout | words=385
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/01_contrato_halts.md | sha256=ea4bc83621fa99fafa9c9176941bda4842b925807c41cae4cd61933760d71bdd | family=halts | doc_type=contract | words=430
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/03_halts_root_cause_audit_phase1_closeout.md | sha256=908e8dd19e6a978184f91267aed46999bd5012c78c1ff9ef4ae66303dcc68567 | family=halts | doc_type=closeout | words=988
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/04_halts_causal_overlay_closeout.md | sha256=8147627e6da23fd171ee2cb97fe343ce738759e83c6c825c65187a93f9963d95 | family=halts | doc_type=closeout | words=1389
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/halts/04_halts_closeout.md | sha256=f4f92f27b26b4904e191591500c795b2f09dfdfd19a85baceaf4d6bac6aab2b0 | family=halts | doc_type=closeout | words=486
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/01_contrato_agent02_agent03_ohlcv_1m_04032026.md | sha256=b64e474c577897856e096d6e2ee99c17e0a79535d46099a85f7def5b7edca636 | family=ohlcv_1m | doc_type=contract | words=792
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/ohlcv_1m/04_ohlcv_1m_closeout.md | sha256=c85a77302b391c20fe8889c37bc192d002245d94937d518f820fc28bf3271d52 | family=ohlcv_1m | doc_type=closeout | words=198
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v1/01_contrato_agent02_agent03_03312026.md | sha256=7f78abb7adcb982d99c09ca0d09efe1881cc2249fdb90530e4755fb0ca91137a | family=quotes | doc_type=contract | words=4264
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/quotes/v2/04_quotes_full_C_D_closeout.md | sha256=5e7470f12743bb9d5033fbe9cfcdb896e7b2f53fa7fbf0c3085c9c3fdef3c240 | family=quotes | doc_type=closeout | words=1307
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/01_contrato_reference.md | sha256=d8df7610029042c81d513b7421b94ecec7a0aa99e668d6fb515f08a39163752a | family=reference | doc_type=contract | words=1236
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/03_reference_root_cause_audit_phase1_closeout.md | sha256=0960f3d243cbb8c0fcbe63e459ab8d4705caa19fc4f735d9b7e6204e01165fb2 | family=reference | doc_type=closeout | words=919
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_causal_overlay_closeout.md | sha256=d02630b457cb82f00e86cbd1aa2cf00ab95413acd3625e35b72efffcd331ed83 | family=reference | doc_type=closeout | words=1228
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/reference/04_reference_closeout.md | sha256=9ce9256f033188adde450e1cecbd3c779686eeebb8c6afa88b572dd3ff2a85fa | family=reference | doc_type=closeout | words=307
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/01_contrato_short.md | sha256=b746bafe0d6fbdeb3fbf65d8e290ac77fee60f46aa1d3f314194873ef370ddd8 | family=short | doc_type=contract | words=450
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/03_short_root_cause_audit_phase1_closeout.md | sha256=328b04e6dc49dbbe766e8641081cc70650d3066ef7e25d4adf5440e4337890ad | family=short | doc_type=closeout | words=414
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/04_short_causal_overlay_closeout.md | sha256=87a779a634ecd751894416fb6d09b8cfeaa62843b632bb66babd093a9d07f2fd | family=short | doc_type=closeout | words=450
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/short/04_short_closeout.md | sha256=a23637a051ccef189770f931b24d2f1bf04d6a628babf994a121d232aae530e2 | family=short | doc_type=closeout | words=290
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/auditoria/trades/v1/01_contrato_agent02_agent03_trades_04012026.md | sha256=a7a44689431ee40f9c7204a7b851daf6bc78f4035df4254d2bb3e9fb1eda90d4 | family=trades | doc_type=contract | words=2622
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/00_final_certification_process.md | sha256=61f92484b93ebf6112111d9f27b0b457f551bb632bc8356168eab63cf6138cb8 | family=None | doc_type=certification_document | words=963
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/00_1m_current_state.md | sha256=be4fb55410a6ced8d7fd2c7374cd97bbf1a92d5fe71dd1e20d089b08e8c4d104 | family=ohlcv_1m | doc_type=current_state | words=103
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/01_1m_recovery_policy.md | sha256=82393cf52886f2d1bfd23eda551d97dee8e5ad3c983563de48c7526365dfbfc5 | family=ohlcv_1m | doc_type=policy | words=117
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/02_1m_quality_policy.md | sha256=66d8f61fd804c563b43f8f6a63a050df9ef650a7d28936c29d39ca11e1ff142a | family=ohlcv_1m | doc_type=policy | words=139
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/1m/03_1m_closeout.md | sha256=85eff72ff96c66b8fca15b57ddc8f472e680a21451861fa775cd6d24e648fc70 | family=ohlcv_1m | doc_type=closeout | words=186
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/additional/00_additional_current_state.md | sha256=880c2f1b599f503caa75629fabbb216d72189e7929ca8da505abc6eddde2ebeb | family=additional | doc_type=current_state | words=153
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/additional/01_additional_subblock_policy.md | sha256=52ad2aebc2b07a29cb2ad439fe325897b26fe9fc49f739e1edd09463fc463aa7 | family=additional | doc_type=policy | words=148
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/additional/02_additional_closeout.md | sha256=b385d39ed60d26d6661a0cfbad022c408236df88320ac3c2fefb397eecb8777f | family=additional | doc_type=closeout | words=103
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/00_daily_current_state.md | sha256=cd9ddf46207fbabf5f7ef02e3c106ec9134ff226a20ef8a2ef82281f148a0121 | family=daily | doc_type=current_state | words=114
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/01_daily_recovery_and_coverage.md | sha256=f7ad05f7bcd542669a528621552c6676585063a57ef6ebc5581c84d2d764284b | family=daily | doc_type=recovery | words=199
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/02_daily_quality_policy.md | sha256=b3134925a3ebf8325f25d3166156deb00c248dadadd227e0fd577d45359b4f8e | family=daily | doc_type=policy | words=116
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/daily/03_daily_closeout.md | sha256=d803513384e5493be867341e3363954ffaf5f5f8f6c5f0174866e6092c030566 | family=daily | doc_type=closeout | words=172
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/00_global_metrics_tables.md | sha256=56335e9985fde4caa72806d0f8444ca982579816bcde7fb75d57d2aa03030591 | family=global_metrics | doc_type=global_metrics | words=425
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/01_global_metrics_tables_traceable.md | sha256=17b820c48fd28a4501a4dbffd712194d70ce7c1f4be40f289d65e8bf9dfe4f97 | family=global_metrics | doc_type=global_metrics | words=714
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/02_working_links.md | sha256=7d72231e6950b6fa31286c4440c50650f19eca5918547f3e9bb0ef71331227b7 | family=global_metrics | doc_type=certification_document | words=40
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/04_global_metrics_tables_traceable_plain_paths.md | sha256=3d0b310bd5947486bc5455314cb9c1e47c08f21834cf054d54e1b5f6e5918f1c | family=global_metrics | doc_type=global_metrics | words=719
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/global_metrics/manifest.json | sha256=67fef3dbacfd49f93f2839cd8d9c3e0dd3ce430b1e9eaedcf55e6ee1e27290f0 | family=global_metrics | doc_type=global_metrics | words=47
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/00_halts_current_state.md | sha256=26cf3dcb5088fefd93695f8f9310b6970aa647e6c5060ade622f795cbebf065c | family=halts | doc_type=current_state | words=170
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/01_halts_overlay_and_recovery.md | sha256=fe8dbacbc73dc09c6d869355ef07b479445cc004b2905e2a97915c39d6708801 | family=halts | doc_type=recovery | words=160
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/02_halts_quality_policy.md | sha256=6363389e0475bc56226ce88fe6e880c1744166df93a761f8a14f240ea5865793 | family=halts | doc_type=policy | words=100
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/halts/03_halts_closeout.md | sha256=d0ff41f3ca5b5b4f807733c8406ec77e0f325bfa11d3146af2141e544c005d34 | family=halts | doc_type=closeout | words=114
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/00_quotes_certification_guide.md | sha256=37cc99a672bd971f9e81f564cc1e012596965a7db2fa8eaee632df6fea374d05 | family=quotes | doc_type=certification_document | words=203
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/01_quotes_certification_contract.md | sha256=1f59c753e1cca2c72eca5793aad4b98061f5c4e0abb2b422c15b5862f3943a64 | family=quotes | doc_type=contract | words=197
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/02_quotes_expected_presence_logic.md | sha256=911f160e5d1f2b6b58f4237de1246e3929b3799a586c865b65d2e86d35772319 | family=quotes | doc_type=certification_document | words=142
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/03_quotes_quality_policy.md | sha256=65833119c2277efe782aea3befc417e9f1d0519968316ad1ca26ef25531054ce | family=quotes | doc_type=policy | words=105
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/04_quotes_usage_policy.md | sha256=2c16f2affcdc7173b855e3cd79a1c763dbd8777bad3c89171a314e5a7347b531 | family=quotes | doc_type=policy | words=120
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/05_quotes_artifact_mapping.md | sha256=1a96303441484d3d036d0212cc7a05da7f5c94111a922b6489fa7a0082a0f5dd | family=quotes | doc_type=certification_document | words=114
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/06_quotes_cert_table_spec.md | sha256=68ad60e6926e631dd8e5d0a4a82020663f2d86a165749cc9a36b62c92cf2ecc3 | family=quotes | doc_type=certification_document | words=90
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/07_quotes_local_certification_build_plan.md | sha256=61ac99d72dedcc87c0dddafbed5712ed5d5ee35da7960a1535e276a5e84657ba | family=quotes | doc_type=certification_document | words=98
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/08_persistent_soft_crossed_mid_large_scale.md | sha256=e87f790c6419b8fecf2847a6807e4babe5bdfab75a5890609a4600aac08dbbe4 | family=quotes | doc_type=certification_document | words=321
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/09_large_file_threshold_edge_hard_many_crosses.md | sha256=2a74924f69bbe53b0f5c6dbf305887bcb7426ed48855521f2f79a528a19eb026 | family=quotes | doc_type=certification_document | words=375
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/10_medium_file_threshold_edge_hard_many_crosses.md | sha256=19f0aa67d6069b6f0c15ad77bc313bfe2e216a270f0248d8f5b6f5a5800fe081 | family=quotes | doc_type=certification_document | words=346
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/11_high_hard_crossed_10_to_20.md | sha256=19252cf32d964da92343cf2833d02118a29ba71a001c3dc538087f951c014bed | family=quotes | doc_type=certification_document | words=292
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/quotes/12_quotes_open_buckets_synthesis.md | sha256=eca50bfe6e3fa7ef7024ea823a99da20e6977b6a8057f9932779f074c84eefee | family=quotes | doc_type=certification_document | words=382
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/00_reference_current_state.md | sha256=60fe3224398287aca2ae71751f949ef067bd54fe702436f3fa4eaf60802c6148 | family=reference | doc_type=current_state | words=160
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/01_reference_causal_value.md | sha256=e74ec27fd84e2b64f8a962e544920e2f097fc742d0375fb9e6be3a4fbe00a440 | family=reference | doc_type=certification_document | words=140
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/reference/02_reference_closeout.md | sha256=15260523bbd3f3d059d4a6a52462ff6dc2fe5171499dcfc9e799b05b053e141d | family=reference | doc_type=closeout | words=114
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/short/00_short_current_state.md | sha256=2b266f2c7e05ae864202967c6b17effb2f6fcb0d8e41536a1f9eb0ef16122f21 | family=short | doc_type=current_state | words=157
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/short/01_short_recovery_and_limits.md | sha256=db176dbd3a5727cc6b05e8675f050a1233eebf2a2c96c5237a380b8911e74404 | family=short | doc_type=recovery | words=137
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/short/02_short_closeout.md | sha256=9276d1d548c93216c54fdebef900d6088b9edf9a848d42ba526356fc875ac04a | family=short | doc_type=closeout | words=98
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/00_trades_current_state.md | sha256=e2435c489ceac33c9cd85b48f6f0eb44192034c2ffec30e9b21c063a39d748b3 | family=trades | doc_type=current_state | words=485
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/01_trades_label_assessment.md | sha256=df275c74d43b039bdc632710a431c078c0c8b4d4ccacf7ddbedfe79e0ce9302b | family=trades | doc_type=certification_document | words=368
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/02_trades_base_certification_decision.md | sha256=96b7bb504a00726b1be9e6a29dc352ed87ba2a9b3fa7891b1515113f264176c3 | family=trades | doc_type=certification_document | words=340
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/03_trades_old_vs_new_bucket_bridge.md | sha256=e66ed8e30af48bf7b5dac1eb62d3c9402dc69b958ea166df5af29d69e0937237 | family=trades | doc_type=certification_document | words=175
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/04_trades_provisional_cert_policy.md | sha256=22fe5c56b45318dd473ed33b7e3cb6b9101679fe42f8316f00f7bbdc36256e72 | family=trades | doc_type=policy | words=337
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/05_trades_review_1m_reference_alignment.md | sha256=a8abe59632bdfd6c052fb331f698de46ae8bff0fceeca648b7e062f5b295480f | family=trades | doc_type=certification_document | words=139
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/06_trades_review_microstructure.md | sha256=2900db0931ac704970656b3dc0191b4c895feb453f911630d5a366b105cb2e55 | family=trades | doc_type=certification_document | words=132
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/07_trades_reference_scale_mismatch.md | sha256=2df55ca086814d985658287d56ebbb14563a0b8bc25f2badb9dd550762d04264 | family=trades | doc_type=certification_document | words=163
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/08_trades_bad_data.md | sha256=c0335f4b17cc56e10d7746f68303d8c0a9eaeb9eb0c5136777205b2c8cb587ae | family=trades | doc_type=certification_document | words=219
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/09_trades_review_no_1m_reference.md | sha256=3964fe3aaaedc43ffe3f3eb6bc669cfa08647f3236670a28096747552d7e7321 | family=trades | doc_type=certification_document | words=171
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/10_trades_bucket_synthesis.md | sha256=82521a45754c401b3e93d2859b57fb2aced6e53a46eff86c906cd33cbd04dd0b | family=trades | doc_type=certification_document | words=231
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/11_trades_review_generic.md | sha256=3d34f6875dd50b4ef8776330265a213228097c553798ffdede605f57deaa6b1d | family=trades | doc_type=certification_document | words=173
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/12_trades_good.md | sha256=df2b36929a344e1efb3ebae4ef7645a6ad5aa5ad22c21ff93c04072dec81edd6 | family=trades | doc_type=certification_document | words=185
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/13_trades_recovery_review_no_1m_reference.md | sha256=b4169c340f7a7a7befdec78c4731a91c1ffa6b315edd75d1f4cd99aae6076c83 | family=trades | doc_type=recovery | words=214
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/14_trades_recovery_reference_scale_mismatch.md | sha256=2cfad6bee81e356e2575e487807cc7266e1ba0e48f9963ed7a679d655b407b03 | family=trades | doc_type=recovery | words=237
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/15_trades_recovery_review_microstructure.md | sha256=e3ac3b088feba20215870fbe215757b23a14a3b25ada2e8de091c05a52af1eb2 | family=trades | doc_type=recovery | words=251
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/16_trades_recovery_review_1m_reference_alignment.md | sha256=5ce49b04c9768d07d31a2c7874ea27b153ba9497d0801611fcb107b43a362940 | family=trades | doc_type=recovery | words=201
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/17_trades_recovery_review_generic.md | sha256=ca9cc9e50c003e96a9e3c6f826a08454ecf74b8de2d097819594862d98d5db25 | family=trades | doc_type=recovery | words=271
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/18_trades_recovery_synthesis.md | sha256=8174a83cc3db4eab9c8d1de8beec21432087d14abd0d123a9469a706affb0434 | family=trades | doc_type=recovery | words=161
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/19_trades_final_recovery_policy.md | sha256=3cfcf096a8b7910c5ac08d543919d21f6ab57be3bd6546447dded5c99f50be4e | family=trades | doc_type=policy | words=324
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/certification/trades/20_trades_closeout.md | sha256=051687e962f0bb6c1011ec67591e04bfe0be849bde3f97338691e31ffec84974 | family=trades | doc_type=closeout | words=355
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=f75ed84964d62fe9ed9678acdaf7d5b1c2e91f3592410abe89616389d6d4f6c4 | family=None | doc_type=graphify_governance | words=1022
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md | sha256=207c3bffd887b4b972af118619e421fd28922b3f5a3f6c85c2f26144ff3746df | family=None | doc_type=graphify_governance | words=993
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/module_contracts/graphify/certification_decisions_graph_protocol.md | sha256=23add9859e5088655f6c57b4c71ba09ce9802400dc91e55329bdd7432102df3e | family=None | doc_type=graphify_governance | words=338
- 01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/module_contracts/graphify/README.md | sha256=ca03b7e8a50c31accc7b584efb402b648319cbccc397efd47951e7afdb478981 | family=None | doc_type=graphify_governance | words=221
```

## Leaf Stats

```yaml
extraction_nodes: 122
extraction_edges: 654
extraction_hyperedges: 9
nodes: 122
edges: 653
communities: 11
detected_files: 88
detected_words_approx: 37652
community_labels:
  0: Quotes Certification
  1: Trades Certification
  2: Trades Certification
  3: Quotes Certification
  4: Quotes Certification
  5: Halts Certification
  6: Short Certification
  7: Trades Certification
  8: Additional Certification
  9: Reference Certification
  10: 1m Certification
```

## Diagnostic

```yaml
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_same_endpoint_collapsed_edges: 0
undirected_same_endpoint_collapsed_edges: 1
```
