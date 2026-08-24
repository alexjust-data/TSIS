[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 226
unverified_code_nodes: 0
raw_edges: 268
valid_candidate_edges: 260
missing_endpoint_edges: 0
dangling_endpoint_edges: 8
self_loop_edges: 0
exact_duplicate_edges: 3
directed_unique_endpoint_pairs: 251
directed_same_endpoint_collapsed_edges: 9
undirected_unique_endpoint_pairs: 251
undirected_same_endpoint_collapsed_edges: 9
same_endpoint_group_count: 7
relation_variant_groups: 3
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 3
post_build_graph_type: Graph
post_build_edges: 251
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
  - 03_tsis_lab_06_validators_validate_visual_inspection_manifest_resolve_path -> path edges=3 relations=['calls', 'references'] locations=['L89', 'L90'] contexts=['call', 'parameter_type', 'return_type']
  - 03_tsis_lab_06_validators_validate_visual_inspection_manifest_write_report -> path edges=3 relations=['references'] locations=['L350'] contexts=['parameter_type']
  - 03_tsis_lab_06_validators_validate_visual_inspection_manifest_read_manifest -> dataframe edges=2 relations=['calls', 'references'] locations=['L104', 'L114'] contexts=['call', 'return_type']
  - 03_tsis_lab_06_validators_validate_visual_inspection_manifest_find_manifest -> path edges=2 relations=['references'] locations=['L118'] contexts=['parameter_type', 'return_type']
  - 03_tsis_lab_06_validators_validate_visual_inspection_manifest_bbox_overlap -> series edges=2 relations=['references'] locations=['L131'] contexts=['parameter_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.