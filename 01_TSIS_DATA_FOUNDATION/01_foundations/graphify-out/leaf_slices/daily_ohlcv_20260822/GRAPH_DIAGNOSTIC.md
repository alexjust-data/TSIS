[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 251
unverified_code_nodes: 0
raw_edges: 325
valid_candidate_edges: 325
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 0
directed_unique_endpoint_pairs: 325
directed_same_endpoint_collapsed_edges: 0
undirected_unique_endpoint_pairs: 325
undirected_same_endpoint_collapsed_edges: 0
same_endpoint_group_count: 0
relation_variant_groups: 0
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
post_build_graph_type: Graph
post_build_edges: 325
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
note: normal graph.json is post-build; raw producer loss must be measured earlier.