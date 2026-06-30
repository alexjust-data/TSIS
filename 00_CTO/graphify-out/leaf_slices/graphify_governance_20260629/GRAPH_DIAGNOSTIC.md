[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 39
raw_edges: 65
valid_candidate_edges: 65
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_unique_endpoint_pairs: 65
directed_same_endpoint_collapsed_edges: 0
undirected_unique_endpoint_pairs: 65
undirected_same_endpoint_collapsed_edges: 0
same_endpoint_group_count: 0
relation_variant_groups: 0
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
post_build_graph_type: Graph
post_build_edges: 65
producer_suppression_sites: 56
producer_suppression_examples:
  - L1444 seen_dyn_pairs arity=unknown
  - L2441 seen_ids arity=unknown
  - L2605 seen_swift_base arity=unknown
  - L2640 seen_swift_base arity=unknown
  - L3564 seen_call_pairs arity=2
  - L3565 seen_dyn_import_pairs arity=2
  - L3566 seen_static_ref_pairs arity=3
  - L3567 seen_helper_ref_pairs arity=3
note: normal graph.json is post-build; raw producer loss must be measured earlier.