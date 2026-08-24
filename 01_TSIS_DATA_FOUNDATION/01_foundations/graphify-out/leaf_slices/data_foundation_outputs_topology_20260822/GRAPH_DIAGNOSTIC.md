[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 1227
unverified_code_nodes: 0
raw_edges: 3482
valid_candidate_edges: 3023
missing_endpoint_edges: 0
dangling_endpoint_edges: 459
self_loop_edges: 0
exact_duplicate_edges: 144
directed_unique_endpoint_pairs: 2726
directed_same_endpoint_collapsed_edges: 297
undirected_unique_endpoint_pairs: 2722
undirected_same_endpoint_collapsed_edges: 301
same_endpoint_group_count: 191
relation_variant_groups: 73
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 79
post_build_graph_type: Graph
post_build_edges: 2737
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
  - 01_tsis_data_foundation_scripts_materialize_master_daily_table_materialize_master_daily_table -> 01_tsis_data_foundation_scripts_materialize_master_daily_table_py_path edges=10 relations=['calls', 'references'] locations=['L106', 'L143'] contexts=['call', 'parameter_type']
  - 01_tsis_data_foundation_scripts_materialize_microstructure_features_table_materialize_microstructure_features_table -> 01_tsis_data_foundation_scripts_materialize_microstructure_features_table_py_path edges=10 relations=['references'] locations=['L428'] contexts=['parameter_type']
  - 01_tsis_data_foundation_scripts_materialize_master_intraday_bar_table_materialize_master_intraday_bar_table -> 01_tsis_data_foundation_scripts_materialize_master_intraday_bar_table_py_path edges=9 relations=['references'] locations=['L493'] contexts=['parameter_type']
  - 01_tsis_data_foundation_scripts_materialize_event_windows_table_materialize_event_windows_table -> 01_tsis_data_foundation_scripts_materialize_event_windows_table_py_path edges=7 relations=['references'] locations=['L314'] contexts=['parameter_type']
  - 01_tsis_data_foundation_scripts_materialize_population_target_presession_4824_candidate_materialize -> 01_tsis_data_foundation_scripts_materialize_population_target_presession_4824_candidate_py_path edges=7 relations=['references'] locations=['L133'] contexts=['parameter_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.