[graphify] MultiDiGraph edge-collapse diagnostic
input: <in-memory>
input_stage: provided JSON (normal graph.json is post-build)
effective_directed: <direct-call>
nodes: 495
unverified_code_nodes: 0
raw_edges: 716
valid_candidate_edges: 716
missing_endpoint_edges: 0
dangling_endpoint_edges: 0
self_loop_edges: 0
exact_duplicate_edges: 2
directed_unique_endpoint_pairs: 697
directed_same_endpoint_collapsed_edges: 19
undirected_unique_endpoint_pairs: 683
undirected_same_endpoint_collapsed_edges: 33
same_endpoint_group_count: 18
relation_variant_groups: 16
source_file_variant_groups: 0
source_location_variant_groups: 0
context_variant_groups: 0
post_build_graph_type: Graph
post_build_edges: 683
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
  - 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_global_metrics_01_global_metrics_tables_traceable_traceable_global_metrics -> 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_certification_global_metrics_00_global_metrics_tables_global_metrics_surface edges=3 relations=['implements', 'references'] locations=[''] contexts=['']
  - 01_tsis_data_foundation_01_foundations_inspection_dossiers_microstructure_features_microstructure_candidate_controlled_visual_readout_v0_2_controlled_microstructure_candidate -> 01_tsis_data_foundation_01_foundations_inspection_dossiers_microstructure_features_microstructure_candidate_visual_readout_v0_1_initial_microstructure_candidate edges=2 relations=['conceptually_related_to', 'semantically_similar_to'] locations=[''] contexts=['']
  - 01_tsis_data_foundation_01_foundations_inspection_dossiers_reference_reference_inspection_readout_v0_2_reference_consumption_readout -> 01_tsis_data_foundation_01_foundations_inspection_dossiers_reference_reference_institutional_closeout_v0_1_reference_institutional_closeout edges=2 relations=['conceptually_related_to', 'references'] locations=[''] contexts=['']
  - 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_03_additional_root_cause_audit_phase1_closeout_additional_structural_closeout -> 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_additional_01_contrato_additional_additional_audit_contract edges=2 relations=['implements', 'references'] locations=[''] contexts=['']
  - 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_04_daily_closeout_daily_final_closeout -> 01_tsis_data_foundation_01_research_01_auditoria_raw_data_00_data_certification_auditoria_daily_01_contrato_agent02_agent03_daily_04032026_daily_agent_contract edges=2 relations=['implements', 'references'] locations=[''] contexts=['']
note: normal graph.json is post-build; raw producer loss must be measured earlier.