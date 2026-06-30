# Data Foundation Outputs Topology Graphify Leaf Manifest

Date: 2026-06-29
Status: runtime, reconstructible Graphify leaf output.

Scope: deterministic topology of CAPA 1 Data Foundation output tables.
Leaf output: `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\leaf_slices\data_foundation_outputs_topology_20260629`

## Graph Build Baseline

```yaml
graph_build_git_branch: integrate/main-data-quality-dossiers-20260613
graph_build_git_commit: 362a031efd006fe44f5c1a775d1ee3af80634767
graph_build_dirty_state: true
graph_build_timestamp_utc: 2026-06-29T08:10:55.016701+00:00
graphify_package_version: 0.9.1
graphify_skill_path: C:\Users\AlexJ\.codex\skills\graphify\SKILL.md
graphify_skill_sha256: 671a0c8e70cc7a74621fa072c118068bc428f4c025f254c6465c5034027bb510
no_api_mode: true
semantic_extraction_mode: deterministic_file_topology_extraction
build_from_json_root_or_equivalent: C:\TSIS_Data
root_graph_updated: false
next_delta_commands:
  - git diff --name-status 362a031efd006fe44f5c1a775d1ee3af80634767...HEAD
  - git status --short
```

Important limitation:

```text
This leaf maps table-to-contract topology from governed filenames and explicit
module contracts. It is not a full semantic reading of every schema field or
validator rule. It is safe as a navigation/control graph, not as the final
semantic graph for all Data Foundation outputs.
```

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
 D "00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/BUENOS CORREGIDOS/BEEN_14_ENERO_26.png"
 D "00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/BUENOS CORREGIDOS/C.JMB_15_ENERO_26.png"
 D "00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/BUENOS CORREGIDOS/banderita.png"
 D "00_CTO/13_TRADING_SYSTEMS/03_STRATEGY_LIBRARY/LONG/DAS/BUENOS CORREGIDOS/resistence.png"
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
 M 01_TSIS_backtest_SmallCaps/scripts/supervise_ohlcv_1m_quote_guarded_repair_v0_2.ps1
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

## Corpus

Corpus files:

```text
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/corporate_actions_table_schema_contract.md | sha256=b1041ede1d9118936a1418bf4c07e8464867543e47726558dcb7e2aa28b23b03 | lines=167 | words=316
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/dataset_certification_matrix_schema_contract.md | sha256=c061c51ddd6b762efedf8673860d2e776367ddee9439c147d9a6a29b4cced2e3 | lines=216 | words=358
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_state_table_schema_contract.md | sha256=50d093482c0b2033560530cb53a4c42782d2255617678c1ebff423f8d78fff00 | lines=224 | words=385
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/event_windows_table_schema_contract.md | sha256=34a73fd7a89c948f05e6ca7ad7eb7730270a9836e042857ab23d9e854067991f | lines=170 | words=636
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/expected_data_calendar_schema_contract.md | sha256=64df01df7196c8ef64f981a3c0a8b3dbb9ea0ad292f5301b29af60d40f90b8a5 | lines=164 | words=279
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/fundamentals_asof_table_schema_contract.md | sha256=36a56592d44adb8a6aa9097a43d1f878c39f7bf737b6b2975f45ad91128fc8e9 | lines=224 | words=353
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/halts_table_schema_contract.md | sha256=5a169904aafa7f3cd0e31f4624865642c2dab4965c2be87316c21aef7d1293f7 | lines=143 | words=509
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/instrument_master_schema_contract.md | sha256=c9b78662dfbffc7cddc6f3fdc90a40d2333173850843030b4617f6dc338ae530 | lines=211 | words=382
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/market_calendar_schema_contract.md | sha256=065c2276c0ca46e4d3319f473ceb7d2e50ce56cf7f9370f8627c5441bd99a6b1 | lines=144 | words=254
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/market_state_table_schema_contract.md | sha256=6b2c69a032d5149e71a8e411c35f592e11a7e7297041a659edb5f5342b8fefd4 | lines=229 | words=387
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/master_daily_table_schema_contract.md | sha256=96d5e0c2b8ea2039799894da078fa65d301f4b9dabaf1f79bfbce0233d4c1eee | lines=243 | words=402
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/master_intraday_bar_table_schema_contract.md | sha256=499a45a69e103638bd73099bda89ae94e54addb041040a895181b6bf4e1df9bb | lines=268 | words=535
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/microstructure_features_table_schema_contract.md | sha256=b456cc3f91c957d5493cf35ec2afe9b4840464ed48ada55af82991e72d37f8fa | lines=259 | words=428
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/news_context_table_schema_contract.md | sha256=03163a075d1f07bf83ca3a6fefa6bc04ae29ced00aa2199e9cda9e52601b0123 | lines=273 | words=402
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/outcomes_table_schema_contract.md | sha256=126e5d47c1c24460f38117dda1b88d4be5acc351e8ef6dabbad2cfb4564400b2 | lines=359 | words=486
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/regime_context_table_schema_contract.md | sha256=fd7a8b754c0426cd885a156574f937d1f8ce9ddb24b1f9c9740e463d48bb10d4 | lines=274 | words=454
- 01_TSIS_backtest_SmallCaps/01_foundations/canonical_schemas/outputs/short_context_table_schema_contract.md | sha256=7132030a124cebb765cf554ab553b0f22e48d589c54f95e802144b59c69317a1 | lines=307 | words=461
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/corporate_actions_table_dataset_contract_v0_1.md | sha256=9ba10917cc5c6becdf1262e5b8fc441437479bf2a652a4dcea1944ad1e0bbfa2 | lines=137 | words=302
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/dataset_certification_matrix_dataset_contract_v0_1.md | sha256=5f9481895fc1ca67e30870e1799f27e32d5dc8a9094f759ca1d22daabd4d91c2 | lines=153 | words=373
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/event_state_table_dataset_contract_v0_1.md | sha256=877d04df39572c73504e4da8772d37182fbc428ec177da0f76b48f8f5edead3a | lines=139 | words=293
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/event_windows_table_dataset_contract_v0_1.md | sha256=2a43a8bf1f46773f3cdbb1e499c8f954080e533406b9f35887e697aff8ee6d44 | lines=183 | words=509
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/expected_data_calendar_dataset_contract_v0_1.md | sha256=a66c4fe4d223e18466480525ae8feceb29110a8cd836085cbea0ff8d3f92f2c3 | lines=125 | words=287
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/fundamentals_asof_table_dataset_contract_v0_1.md | sha256=9fe06e0be1dbcc7222875c4e6b5edde347d29c9c8b5b25667653e247ce72c370 | lines=157 | words=393
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/halts_table_dataset_contract_v0_1.md | sha256=9977c63de8ae0d17af8c7c856f382999fe052a1a3277667a00f93c52a60b25de | lines=212 | words=511
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/instrument_master_dataset_contract_v0_1.md | sha256=8e3a22560839f85f6abfc284d32dce8f5c2f4aaf8ebe0fbb8d366079b152794f | lines=165 | words=387
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/market_calendar_dataset_contract_v0_1.md | sha256=f1b15ba5c13e1ef56593a6b59b722ffe2de3b0251262e3c562ef734ff6c29e07 | lines=128 | words=213
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/market_state_table_dataset_contract_v0_1.md | sha256=65ca5ab9c1f61030a56096a93e68df26481fa4f4adcf66de049fb86f2204167a | lines=145 | words=346
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/master_daily_table_dataset_contract_v0_1.md | sha256=9fc0c5386be124b2fa75ba438bf3bce2280e23d668ca0a9d957c8c7377273f0e | lines=178 | words=377
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/master_intraday_bar_table_dataset_contract_v0_1.md | sha256=b3be9d64b6f1a221863bd426d60bb025630cc52a84cfbc328482270c02d7fc75 | lines=218 | words=637
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/microstructure_features_table_dataset_contract_v0_1.md | sha256=345778350b12d25ffa4ba8d3cc88cb7629a6b589e014e219ac2c78feed29517c | lines=432 | words=1206
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/news_context_table_dataset_contract_v0_1.md | sha256=bbb99b74bb02fffdae93d8d41bbf12c598c32902ddc649ec77b1935bed0dd6a1 | lines=170 | words=417
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/outcomes_table_dataset_contract_v0_1.md | sha256=bb2cead965fe5ff35721884b871ee967db1b0fa3116687471ec4b932c35f76aa | lines=177 | words=410
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/regime_context_table_dataset_contract_v0_1.md | sha256=6ca049e939144bb944d0d775637b8cae8b10fba97cfda2525a80f06d68b4812f | lines=183 | words=461
- 01_TSIS_backtest_SmallCaps/01_foundations/contract_registry/dataset_contracts/short_context_table_dataset_contract_v0_1.md | sha256=9b8c3a5ab0558419fe11fbcae4a9b0701e9364d3e738ac1cf2ae9c7a80089c8d | lines=173 | words=403
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/corporate_actions_table_consumption_policy.md | sha256=354d3d0d077413b9d3ef1f03ff038a92f237043e16d4253ddef8ab6bcad0c944 | lines=82 | words=175
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/dataset_certification_matrix_consumption_policy.md | sha256=ed8b1f4bea8bd01b2e1d687013b0a7ec3c876515a1b2398051e9257024c25ec7 | lines=109 | words=264
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/event_state_table_consumption_policy.md | sha256=bb03e6cb73fdc1b02a18e103d90eb047ce024a0ff74c1f6df6772d9953f9d0d4 | lines=135 | words=237
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/event_windows_table_consumption_policy.md | sha256=fd5f2c11e487485c8a1f50d6b24b6ed5c386dc90024a27699d989bde3bace8df | lines=90 | words=219
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/expected_data_calendar_consumption_policy.md | sha256=bc0c35804ae5b8464e06b2c386d1e3d300b279219cc052f05fe6f8f4a56a3e3a | lines=79 | words=168
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/fundamentals_asof_table_consumption_policy.md | sha256=27dfd0563f22d98a8ea521515f71ca907ef7235a073bc815d48439aff5d09e94 | lines=97 | words=224
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/halts_table_consumption_policy.md | sha256=7ddb48b87ec6ed838a2b02cd564c7572a25f12b82fec1a383da69055cef57bcf | lines=88 | words=208
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/instrument_master_consumption_policy.md | sha256=d6ed37f28cb6f7b93d527243ec9b24c33a5c41f6b0720bc4fb30dcf13f01399e | lines=146 | words=305
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/market_calendar_consumption_policy.md | sha256=28057aa541c1b5779005e1cf686eff25b03ccd918ea4e5b45d5474894bfef9f3 | lines=99 | words=174
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/market_state_table_consumption_policy.md | sha256=dcbb92aecd28c5b7918b33e34176b6ad8c3a79dd5aa8ef8728c91b406bb1b12c | lines=129 | words=227
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/master_daily_table_consumption_policy.md | sha256=53c5d4f1c55ec196b081dd3a222036b66112ea0e1c83cd43ff44b45d468ffd2d | lines=106 | words=258
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/master_intraday_bar_table_consumption_policy.md | sha256=e944550d6a709d5b7e808cb141ed89f24573d6232ead54e595a1fcb539cd7b39 | lines=142 | words=412
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/microstructure_features_table_consumption_policy.md | sha256=ac3923c94409ab0cb41b8088ba3b7bbfb1ce66ac0203fa28b99c1dfe98f9ccbc | lines=146 | words=370
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/news_context_table_consumption_policy.md | sha256=229abd71e8a8466abfeeb192070efd5e581d1e54bd75345be5b0b5776bcd5893 | lines=108 | words=257
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/outcomes_table_consumption_policy.md | sha256=a9feb502977431545b9f7bcdebde4e10ef70a148d892b8cdfc44eee2ba2253fb | lines=88 | words=217
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/regime_context_table_consumption_policy.md | sha256=2ca9e82a153bbe155366337dc3cbcf77675ef2ea60250ce3b88581c2917d2625 | lines=143 | words=283
- 01_TSIS_backtest_SmallCaps/01_foundations/data_consumption_policies/short_context_table_consumption_policy.md | sha256=9e493d97850726b8c49f5fae56897094c0e8643031c830e2013ca55233d5b2f3 | lines=132 | words=298
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/corporate_actions_table_registry_entry.yaml | sha256=a5f559aa39ff273a3f88ff903021f1fbcdea0721b12866b81c390dca4be836c7 | lines=93 | words=151
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/dataset_certification_matrix_registry_entry.yaml | sha256=e998b38eed82f2b84cda3ff2a0a01d61ca2b9ea277fc078805a113a63fbe341e | lines=79 | words=124
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/event_state_table_registry_entry.yaml | sha256=8e576a03b9e6d0e228b52e2d94a5e213ce758ae6dc10bcc7b8bd830338a4fede | lines=46 | words=70
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/event_windows_table_registry_entry.yaml | sha256=7151b1479a9eef5e831be6ca298ad6bc96add9d892fc68b79e53fe5cdc31be17 | lines=41 | words=80
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/expected_data_calendar_registry_entry.yaml | sha256=3812c617db0e9388b3726a58b29c1a6de6352faacd839d1ebff82fcd3c6bba40 | lines=87 | words=131
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/fundamentals_asof_table_registry_entry.yaml | sha256=ebabea2e9a6d91f0f2482767cddcd4e9a63d94af07802f739858479b52af269c | lines=61 | words=98
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/halts_table_registry_entry.yaml | sha256=06f240f32a957085310daf62522a31db7f4726d70834661e7f0367204abfa719 | lines=41 | words=77
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/instrument_master_registry_entry.yaml | sha256=c212f882429f6fba091cc3a49d214da1ffe4d1fd3e9fb9811d36d29f178603d8 | lines=102 | words=165
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/market_calendar_registry_entry.yaml | sha256=8721a3119b45b382ca6767c2174f408337f8a0e02b38d0cfcacf5d063682b410 | lines=105 | words=153
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/market_state_table_registry_entry.yaml | sha256=008d0fc1f35277d37914ca4a7a5ab9218d9ce4cbcdea462834a6f480dbfefde6 | lines=49 | words=73
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/master_daily_table_registry_entry.yaml | sha256=7aaa1992d5c6c438a8ed71a7dacbe4876179b3f1b0e545fc6c7788094ad55303 | lines=91 | words=141
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/master_intraday_bar_table_registry_entry.yaml | sha256=69e9a0a13d5a9988bf94d657c825076bf109658f13986e76dcf2331c75bc0588 | lines=103 | words=191
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/microstructure_features_table_registry_entry.yaml | sha256=bb144451799e17325581e9a87679e51339649847352ca8f43aadd843816bc918 | lines=96 | words=167
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/news_context_table_registry_entry.yaml | sha256=5fc61046322d4416ec536c3213e5e45c6d131e879c5b942fefe0f1f51c9bfd52 | lines=56 | words=89
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/outcomes_table_registry_entry.yaml | sha256=83d724dcb441eba29f178384cfdd557fb5a07991cc5f432193599a29a3a20561 | lines=58 | words=104
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/regime_context_table_registry_entry.yaml | sha256=bd9c22800a33c22475cde795cf066e09f3c3e981901a1f0bcf5532a2b96ef982 | lines=64 | words=104
- 01_TSIS_backtest_SmallCaps/01_foundations/dataset_registry/outputs/short_context_table_registry_entry.yaml | sha256=6608eea24092b4089a7113eb4009327af1912bc71cffd543ea2105df6c404381 | lines=62 | words=98
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md | sha256=20ecf3a3199e0490b510d8c78195b3a9eafe8178bf8312ea8e552356264fbd73 | lines=488 | words=1627
- 01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md | sha256=51c9aeef9fad062b283682ee4a54b0b15e5d1319f4326e9393bfb64d21bf619a | lines=3816 | words=9404
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md | sha256=e8f72580955af087f1749cd580d0f26bf686e79380f11ef82cd0d68658532ce0 | lines=539 | words=2289
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md | sha256=a87298f0fe0e0b3f9c9d58eca6574c8c701f0f86b7091f1fd9691c468c23ff80 | lines=3195 | words=8762
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_build_loop_runbook_v0_1.md | sha256=6c9266e0b92d546873e31e689a85c3fa29b5509cb110278f57eea340fffb050e | lines=323 | words=689
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/market_state_event_state_composition_contract_v0_1.md | sha256=46d41d18d632cd137a0af26f5730f0ba97068a97fd20ff01ae5aa099908d581a | lines=558 | words=1231
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md | sha256=1fcee7af60838ff04fefc409ab82f9b506bf608f8f1748a8a7aedc9718e024e7 | lines=395 | words=1148
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/microstructure_features_table_multi_window_materialization_plan_v0_1.md | sha256=0d76ce73d61c69ed256b2244d54d5c4cb5ddb60547dc174e125e388e7c16c78e | lines=469 | words=1376
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/short_sale_constraints_data_acquisition_runbook_v0_1.md | sha256=54ebaf02b215fc451a993716bd694beaa8151f8365bcbd47a5388e2422148974 | lines=516 | words=1388
- 01_TSIS_backtest_SmallCaps/01_foundations/module_contracts/outputs/short_sale_constraints_table_target_contract_v0_1.md | sha256=79e0a5ebd594cc09f6f4d9d940fca392bd3564dd01aeffed3f500080a6e252c3 | lines=466 | words=1068
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/corporate_actions_table_validators.md | sha256=ebc0a7558c29526572f50bb765ab40128682b3b4dae224217722699d64724d61 | lines=106 | words=190
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/dataset_certification_matrix_validators.md | sha256=1d7478c848269a64fbc1d9bf8fc7d92842975c7d306e4e87bbeb616d43a03bdc | lines=107 | words=233
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/event_state_table_validators.md | sha256=59d2de12fa5a07f836c49c2638e8f0dd5e45a94f972373f9a613350b529885ca | lines=112 | words=276
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/event_windows_table_validators.md | sha256=63d119dde1d735814844d1e167ff93cc197a7bcc96d1400b6c38ca4102a746d6 | lines=101 | words=231
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/expected_data_calendar_validators.md | sha256=8671996cf85e414a2e8b8f00170421aaeab05b63b9c04084e1b7f0c3159784c3 | lines=101 | words=186
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/fundamentals_asof_table_validators.md | sha256=7f75bb085a723d0ad56b46f0d219506365473211a5b0ddb8a15a7480c959874a | lines=98 | words=177
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/halts_table_validators.md | sha256=6386ba252f57d81f41e6873629ac4bc5e972c1c90860a103f65cc8abb482986b | lines=99 | words=233
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/instrument_master_validators.md | sha256=55e829f5b12dd4b6c5b9ff994fa61f13a76ab9572fd69afeca84634ecaabedfd | lines=152 | words=252
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/market_calendar_validators.md | sha256=11871c367acaa0cdd90136452fdea8200b048435eb26deb2ac9b1e475229e728 | lines=93 | words=135
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/market_state_table_validators.md | sha256=4e2e613ebcea1c6a29009d4e8665f352dc82deb78c6cc7f649c690630a0d5606 | lines=115 | words=281
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/master_daily_table_validators.md | sha256=40d9f5b52413e0cc1e04336d295d2b76dda285539df449076a99f46af211f9f9 | lines=117 | words=289
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/master_intraday_bar_table_validators.md | sha256=7794ae0053109c654990044462b675c92c6e6750c14ebf3ce3b997128790bb9b | lines=143 | words=308
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/microstructure_features_table_validators.md | sha256=e6617d6459cc9a7e8208c880fe977393266c92f89c055d012515d66acec136a7 | lines=97 | words=271
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/news_context_table_validators.md | sha256=b23ce13b722c7a2de05848feada32197a412c5cfd80bfb509dd8489580ce7e26 | lines=149 | words=277
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/outcomes_table_validators.md | sha256=2dc80324bc9a022bf20b2d0bce592835688abd756e4154b951f3fbc58c356d5d | lines=118 | words=315
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/regime_context_table_validators.md | sha256=964cf90b06945a4e4bdd66eb1cae0f3eed7304082ef0176bb13f414cd02610b9 | lines=132 | words=268
- 01_TSIS_backtest_SmallCaps/01_foundations/validators/outputs/short_context_table_validators.md | sha256=05f3981ac6b46d23b068d131ee4c5743a21e5447d1f51834ad517a94018b84cf | lines=133 | words=250
- 01_TSIS_backtest_SmallCaps/CHANGELOG.md | sha256=ad50f2143794961fe215da920ad89e67603fa53c9cf4cd9317cc5a7f6fcc4da2 | lines=5574 | words=18625
```

## Missing Components

```text
- short_sale_constraints_table / schema
- short_sale_constraints_table / dataset_contract
- short_sale_constraints_table / registry
- short_sale_constraints_table / consumption_policy
- short_sale_constraints_table / validator
```

## Leaf Stats

```yaml
extraction_nodes: 130
extraction_edges: 268
extraction_hyperedges: 2
nodes: 130
edges: 200
communities: 16
detected_files: 96
detected_words_approx: 72643
community_labels:
  0: Market Event State
  1: Short Context
  2: Short Context
  3: Schema Stack
  4: Intraday Microstructure
  5: Intraday Microstructure
  6: Schema Stack
  7: Schema Stack
  8: Schema Stack
  9: Schema Stack
  10: Reference Identity
  11: Reference Identity
  12: Schema Stack
  13: Schema Stack
  14: Schema Stack
  15: Schema Stack
```

## Diagnostic

```yaml
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_same_endpoint_collapsed_edges: 0
undirected_same_endpoint_collapsed_edges: 68
```
