[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 1534
unverified_code_nodes: 0
raw_edges: 4813
valid_candidate_edges: 4041
missing_endpoint_edges: 0
dangling_endpoint_edges: 772
self_loop_edges: 0
exact_duplicate_edges: 218
directed_unique_endpoint_pairs: 3691
directed_same_endpoint_collapsed_edges: 350
undirected_unique_endpoint_pairs: 3688
undirected_same_endpoint_collapsed_edges: 353
same_endpoint_group_count: 203
relation_variant_groups: 86
source_file_variant_groups: 0
source_location_variant_groups: 1
context_variant_groups: 42
post_build_graph_type: Graph
post_build_edges: 3690
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
  - 01_tsis_data_foundation_scripts_sec_pit_float_estimate_resolve_owner_exclusion_float -> 01_tsis_data_foundation_scripts_sec_pit_float_estimate_py_any edges=7 relations=['references'] locations=['L183'] contexts=['generic_arg']
  - 01_tsis_data_foundation_scripts_sec_pit_float_estimate_v2_resolve_owner_exclusion_float_v0_2 -> 01_tsis_data_foundation_scripts_sec_pit_float_estimate_v2_py_any edges=7 relations=['references'] locations=['L9'] contexts=['generic_arg']
  - 01_tsis_data_foundation_scripts_sec_pit_run_no_network_os_probe_execute -> 01_tsis_data_foundation_scripts_sec_pit_run_no_network_os_probe_py_path edges=7 relations=['calls', 'references'] locations=['L139', 'L93'] contexts=['call', 'parameter_type', 'return_type']
  - 01_tsis_data_foundation_scripts_sec_pit_run_owner_exclusion_resolution_batch_execute -> 01_tsis_data_foundation_scripts_sec_pit_run_owner_exclusion_resolution_batch_py_path edges=7 relations=['calls', 'references'] locations=['L110', 'L78'] contexts=['call', 'parameter_type', 'return_type']
  - 01_tsis_data_foundation_scripts_sec_pit_build_stratified_owner_case_configs_execute -> 01_tsis_data_foundation_scripts_sec_pit_build_stratified_owner_case_configs_py_path edges=6 relations=['references'] locations=['L29'] contexts=['parameter_type', 'return_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.