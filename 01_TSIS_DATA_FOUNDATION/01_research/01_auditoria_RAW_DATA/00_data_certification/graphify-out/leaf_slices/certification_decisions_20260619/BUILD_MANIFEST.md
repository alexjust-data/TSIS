# Certification Decisions Graphify Leaf Manifest

Date: 2026-06-19
Status: runtime, reconstructible Graphify leaf output.

Scope: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification
Leaf output: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_research\01_auditoria_RAW_DATA\00_data_certification\graphify-out\leaf_slices\certification_decisions_20260619

Procedure:
- Controlled certification decisions corpus selected from `00_data_certification` according to `module_contracts/graphify/certification_decisions_graph_protocol.md`.
- Official Graphify detect on the controlled corpus.
- Graphify Codex semantic extraction with 5 worker chunks.
- Official Graphify `build_from_json` assembly.
- Official Graphify clustering, analysis, report generation, JSON export, and HTML export.
- Root `00_data_certification/graphify-out/graph.json` intentionally not created.

Leaf stats:
- nodes: 252
- edges: 322
- communities: 22
- detected_files: 89
- detected_words: 45813
- semantic_chunks: 5
- semantic_nodes_before_build: 252
- semantic_edges_before_build: 322
- hyperedges_before_build: 13

Inclusion policy:
- Included local Graphify governance, certification Markdown, certification global metrics JSON, and selected auditoria closeout/policy/contrato Markdown.
- Excluded notebooks, images, physical data, runtime, caches, and evidence-heavy binary assets.

Build notes:
- Temporary staging copies were removed after export.
- The authoritative leaf artifacts are the files in this directory.

Built at UTC: 2026-06-19T12:32:47.947590+00:00
