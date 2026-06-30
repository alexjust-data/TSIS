# Market State Representation Graphify Leaf Manifest

Date: 2026-06-28
Status: runtime, reconstructible Graphify leaf output.

Scope: C:\TSIS_Data\00_CTO\11_MARKET_SCIENCE\05_MARKET_STATE_REPRESENTATION
Leaf output: C:\TSIS_Data\00_CTO\graphify-out\leaf_slices\market_state_representation_20260628

## Graph Build Baseline

```yaml
graph_build_git_branch: integrate/main-data-quality-dossiers-20260613
graph_build_git_commit: 362a031efd006fe44f5c1a775d1ee3af80634767
graph_build_dirty_state: true
graph_build_timestamp_utc: 2026-06-28T16:57:49.258654+00:00
graph_build_backend_or_agent_mode: codex_subagent_semantic_extraction_no_api_keys_no_ollama
graph_build_command: codex_subagent_semantic_extraction + graphify.build.build_from_json + graphify.cluster.cluster + graphify.export.to_json/to_html + graphify.report.generate
corpus_manifest_path: C:\TSIS_Data\00_CTO\graphify-out\leaf_slices\market_state_representation_20260628\corpus_manifest.json
corpus_file_count: 2
queue_entries_covered:
  - 00_CTO GRAPHIFY_REFRESH_QUEUE: 2026-06-25 - Market State Representation contract
queue_entries_left_pending:
  - 00_CTO GRAPHIFY_REFRESH_QUEUE: 2026-06-28 - Strategy Library trader-source reorganization
  - 00_CTO GRAPHIFY_REFRESH_QUEUE: 2026-06-28 - Graphify build baseline provenance rule
next_delta_commands:
  - git diff --name-status 362a031efd006fe44f5c1a775d1ee3af80634767...HEAD
  - git status --short
```

Dirty paths at build time are intentionally recorded because this leaf was built
against the current working tree, not a clean committed checkout.

### Dirty Paths

```text
0_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/07_Long_plays.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/07_Short_Plays.md
"00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/Day Trading en Small Caps - XVNTrading.pdf"
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Crowded_Ticker_Context/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Float_Rotation/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Liquidity_Gain_Loss/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Neutralized_Area/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Pattern_Variation_Acceptable_Range/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Short_Seller_Trap_Layers/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/stevenDux/Volume_Prediction/FACTOR.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_case_explorer.ipynb
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/das_widgets.py
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Dip_Buying_Multi_Day_Runner/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/stevenDux/Gap_Up_Buying/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Bounce_Plus_Gap_Up_Short/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Bounce_Short/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Intraday_Top/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Double_Layer_Resistance/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/First_Red_Day/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/First_Red_Day/estrtategia.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Gap_Up_Short/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Multi_Day_Top_Risk_Reward/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/SHORT/stevenDux/Parabolic_Breakout_Failed_Breakout/STRATEGY.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/STEVEN_DUX_SOURCE_STRATEGY_INDEX_v0_1.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/_shared/strategy_widgets_common.py
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/000CAR.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/001SLV.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/003BIRD.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/004BRID.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/005EEIQ.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/006EEIQ.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/007ASTC.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/01_30.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/02SLV.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/02_40.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/04_51.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/06_00.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/07_41.png
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/steven_dux/08ASTC.png
00_CTO/13_TRADING_SYSTEMS/README.md
00_CTO/CHANGELOG.md
00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
00_CTO/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/ohlcv_1m_split_normalized_consumption_policy.md
01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/ohlcv_1m/ohlcv_1m_split_normalized_registry_entry.yaml
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/README.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_quote_guarded/ohlcv_1m_quote_guarded_live_supervision_validation_protocol_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_full_universe_materialization_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_operational_landing_v0_1.md
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/quotes/quotes_staging_clone_runbook_v0_1.md
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
01_TSIS_backtest_SmallCaps/01_research/01_auditoria_RAW_DATA/00_data_certification/GRAPHIFY_REFRESH_QUEUE.md
01_TSIS_backtest_SmallCaps/CHANGELOG.md
01_TSIS_backtest_SmallCaps/scripts/data_ops/clone_quotes_to_staging.ps1
01_TSIS_backtest_SmallCaps/scripts/monitor_long_running_operation.ps1
01_TSIS_backtest_SmallCaps/scripts/run_1m_split_normalized_materialization.ps1
01_TSIS_backtest_SmallCaps/scripts/validate_ohlcv_1m_quote_guarded_repair_v0_2.ps1
CHANGELOG.md
LONG_RUNNING_OPERATIONS_CONTRACT.md
PROJECT_RULES.md
```

### Untracked Paths

```text
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/01_Steven_Dux/
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/03_Edu_Trades/
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/04_Xavineta/
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/FACTORS/README.md
00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/source_assets/999.png
01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/ohlcv_1m_split_normalized_split_affected_materialization_results_v0_1.md
```

## Procedure

- Controlled corpus selected from `00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION`.
- Corpus manifest written before semantic extraction.
- Graphify Codex semantic extraction performed by a Codex subagent without API keys and without Ollama.
- Official Graphify `build_from_json` assembly over `.graphify_extract.json`.
- Official Graphify community detection with `graphify.cluster.cluster`.
- Official Graphify JSON and HTML exports with `graphify.export.to_json` and `graphify.export.to_html`.
- Official Graphify report generated with `graphify.report.generate`.
- Official Graphify `diagnose multigraph` verification on exported `graph.json`.
- Root `00_CTO/graphify-out/graph.json` intentionally not updated.

## Corpus

Inclusion rules:

```text
- market_state_representation_contract_v0_1.md
- market_state_representation_source_file_map_v0_1.md
```

Exclusion rules:

```text
- no graphify-out
- no runtime
- no notebooks
- no images
- no physical data
```

Corpus files:

```text
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_contract_v0_1.md | sha256=9e2834eb6cefe42c03ad25fea9b2d130ec2e06b14c26f7b33d567bebb04d7355
- 00_CTO/11_MARKET_SCIENCE/05_MARKET_STATE_REPRESENTATION/market_state_representation_source_file_map_v0_1.md | sha256=7fb88a90a0ad8dac884772e84adb5859bc60c602fabd00720a4513ba0f036e7d
```

## Leaf Stats

```yaml
extraction_nodes: 60
extraction_edges: 84
extraction_hyperedges: 0
nodes: 60
edges: 83
communities: 7
detected_files: 2
detected_words_approx: 4035
```

## Diagnostic

Command:

```powershell
graphify diagnose multigraph --graph "C:\TSIS_Data\00_CTO\graphify-out\leaf_slices\market_state_representation_20260628\graph.json" --json
```

Result:

```yaml
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_same_endpoint_collapsed_edges: 0
relation_variant_groups: 0
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
```

Validation query:

```powershell
graphify explain "Market State Representation" --graph "C:\TSIS_Data\00_CTO\graphify-out\leaf_slices\market_state_representation_20260628\graph.json"
```

## Build Notes

- `.graphify_extract.json` was post-corrected only to rename duplicate `Source File Map` labels. This avoided Graphify ghost-duplicate collapse producing a self-loop; node ids and semantic relationships were otherwise preserved.
- The final diagnostic is clean: 0 missing endpoints, 0 dangling endpoints, 0 self-loops and 0 exact duplicate edges.
- This is a leaf refresh only. It does not replace or merge the stale `00_CTO` root graph.
