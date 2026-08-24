[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 273
unverified_code_nodes: 0
raw_edges: 747
valid_candidate_edges: 703
missing_endpoint_edges: 0
dangling_endpoint_edges: 44
self_loop_edges: 0
exact_duplicate_edges: 12
directed_unique_endpoint_pairs: 684
directed_same_endpoint_collapsed_edges: 19
undirected_unique_endpoint_pairs: 684
undirected_same_endpoint_collapsed_edges: 19
same_endpoint_group_count: 14
relation_variant_groups: 5
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 2
post_build_graph_type: Graph
post_build_edges: 684
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
  - 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_resolve_image -> 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_py_path edges=5 relations=['calls', 'references'] locations=['L458', 'L472'] contexts=['call', 'generic_arg', 'parameter_type']
  - 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_build_images -> 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_py_path edges=3 relations=['references'] locations=['L672'] contexts=['parameter_type']
  - 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_write_corpus_reports -> 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_py_any edges=3 relations=['references'] locations=['L1545'] contexts=['generic_arg']
  - 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_generate_sersan_p09_pilot_resolve_image_ref -> 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_generate_sersan_p09_pilot_py_path edges=2 relations=['calls', 'references'] locations=['L594', 'L596'] contexts=['call', 'return_type']
  - 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_rel_corpus -> 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_harness_toolchain_sersan_distillation_run_sersan_corpus_distillation_py_path edges=2 relations=['references'] locations=['L185'] contexts=['parameter_type']
note: normal graph.json is post-build; raw producer loss must be measured earlier.