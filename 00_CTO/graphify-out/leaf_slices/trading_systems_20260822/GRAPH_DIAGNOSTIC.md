[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 455
unverified_code_nodes: 0
raw_edges: 1340
valid_candidate_edges: 1282
missing_endpoint_edges: 0
dangling_endpoint_edges: 58
self_loop_edges: 0
exact_duplicate_edges: 29
directed_unique_endpoint_pairs: 1159
directed_same_endpoint_collapsed_edges: 123
undirected_unique_endpoint_pairs: 1141
undirected_same_endpoint_collapsed_edges: 141
same_endpoint_group_count: 95
relation_variant_groups: 54
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 38
post_build_graph_type: Graph
post_build_edges: 1142
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
  - 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_export_run_event_day_detail_images -> 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_py_path edges=5 relations=['calls', 'references'] locations=['L3244', 'L3279'] contexts=['call', 'generic_arg', 'parameter_type']
  - 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_find_structural_rebreak -> 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_py_series edges=4 relations=['references'] locations=['L581'] contexts=['generic_arg', 'parameter_type']
  - 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_export_run_premarket_detail_images -> 00_cto_13_trading_systems_03_strategy_library_long_das_scripts_das_widgets_py_path edges=4 relations=['references'] locations=['L3401'] contexts=['generic_arg', 'parameter_type']
  - 00_cto_13_trading_systems_03_strategy_library_long_gap_go_gap_and_go_widgets_export_run_event_day_detail_images -> 00_cto_13_trading_systems_03_strategy_library_long_gap_go_gap_and_go_widgets_py_path edges=4 relations=['references'] locations=['L1376'] contexts=['generic_arg', 'parameter_type']
  - 00_cto_13_trading_systems_03_strategy_library_shared_strategy_widgets_common_session_segment -> 00_cto_13_trading_systems_03_strategy_library_shared_strategy_widgets_common_py_series edges=3 relations=['calls', 'references'] locations=['L80', 'L82'] contexts=['call', 'parameter_type', 'return_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.