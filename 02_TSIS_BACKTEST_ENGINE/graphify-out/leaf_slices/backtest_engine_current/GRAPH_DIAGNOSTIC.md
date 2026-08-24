[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 2574
unverified_code_nodes: 0
raw_edges: 7483
valid_candidate_edges: 6894
missing_endpoint_edges: 0
dangling_endpoint_edges: 589
self_loop_edges: 0
exact_duplicate_edges: 126
directed_unique_endpoint_pairs: 6525
directed_same_endpoint_collapsed_edges: 369
undirected_unique_endpoint_pairs: 6499
undirected_same_endpoint_collapsed_edges: 395
same_endpoint_group_count: 313
relation_variant_groups: 187
source_file_variant_groups: 0
source_location_variant_groups: 9
context_variant_groups: 45
post_build_graph_type: Graph
post_build_edges: 6491
producer_suppression_sites: 11
producer_suppression_examples:
  - L1099 seen_ids arity=unknown
  - L1253 seen_ids arity=unknown
  - L1255 seen_doc_refs arity=unknown
  - L1600 seen_ids arity=unknown
  - L2069 seen_keys arity=unknown
  - L2228 seen_keys arity=unknown
  - L3272 seen_ids arity=unknown
  - L3380 seen_ids arity=unknown
examples:
  - 02_tsis_backtest_engine_contracts_backtest_backtest_run_spec_contract_v0_1_properties_policy_id -> 02_tsis_backtest_engine_contracts_backtest_backtest_run_spec_contract_v0_1_policy_id_ref edges=4 relations=['contains'] locations=['L397', 'L553', 'L634', 'L654'] contexts=['']
  - 02_tsis_backtest_engine_src_tsis_backtest_backtest_runner_apply_fill_online -> 02_tsis_backtest_engine_src_tsis_backtest_backtest_runner_py_decimal edges=4 relations=['references'] locations=['L534'] contexts=['generic_arg', 'parameter_type']
  - 02_tsis_backtest_engine_src_tsis_backtest_market_state_consumer_marketstateconsumerv0_1_join_pairs -> 02_tsis_backtest_engine_src_tsis_backtest_market_state_consumer_py_any edges=4 relations=['references'] locations=['L725'] contexts=['generic_arg']
  - 02_tsis_backtest_engine_src_tsis_backtest_physical_replay_runner_physicalhistoricalreplayslicerunner_write_authorized_fixture_manifest -> 02_tsis_backtest_engine_src_tsis_backtest_physical_replay_runner_py_path edges=4 relations=['calls', 'references'] locations=['L517', 'L520'] contexts=['call', 'parameter_type', 'return_type']
  - 02_tsis_backtest_engine_src_tsis_backtest_physical_replay_runner_physicalhistoricalreplayslicerunner_final_manifest -> 02_tsis_backtest_engine_src_tsis_backtest_physical_replay_runner_py_any edges=4 relations=['references'] locations=['L600'] contexts=['generic_arg', 'parameter_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.