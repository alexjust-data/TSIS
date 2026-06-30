# Trading Systems Event-First Graphify Leaf Manifest

Date: 2026-06-20
Status: runtime, reconstructible Graphify leaf output.

Scope: C:\TSIS_Data\00_CTO\13_TRADING_SYSTEMS

Procedure:
- Official Graphify detect on the `13_TRADING_SYSTEMS` slice.
- Graphify Codex semantic extraction using 4 scoped worker chunks.
- Official Graphify `build_from_json` over the combined extraction.
- Official Graphify community detection and export.
- Official Graphify JSON, HTML and report generation.
- Official Graphify `diagnose multigraph` verification on exported `graph.json`.

Leaf stats:
- nodes: 313
- edges: 408
- communities: 20
- hyperedges: 10
- detected_files: 42
- detected_words: 30071
- detected_file_types:
  - code: 0
  - document: 40
  - paper: 1
  - image: 1
  - video: 0

Diagnostic:
- missing_endpoint_edges: 0
- dangling_endpoint_edges: 0
- self_loop_edges: 0
- exact_duplicate_edges: 0
- directed_same_endpoint_collapsed_edges: 0
- relation_variant_groups: 0
- source_file_variant_groups: 0
- source_location_variant_groups: 0

Updated semantic inputs:
- `00_EVENT_LIBRARY/EVENT_BEHAVIORAL_MECHANICS_GUIDE_v0_1.md`
- `00_EVENT_LIBRARY/01_MOMENTUM_EXPANSION/PM_ACCEPTED_EXTENSION_BREAK_EVENT/`
- `00_EVENT_LIBRARY/07_SHORT_SQUEEZE_DYNAMICS/DAS_EVENT/`

Root integration:
- Not performed.
- Root graph remains stale for `13_TRADING_SYSTEMS` until a controlled root
  rebuild or official slice-replacement flow removes historical path nodes.
