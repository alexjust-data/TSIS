# Foundations Authority Graphify Leaf Manifest

Date: 2026-06-20
Status: runtime, reconstructible Graphify leaf output.

Scope: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations
Leaf output: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\leaf_slices\foundations_authority_20260620
Staging source: C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\graphify-out\_graphify_staging_foundations_authority_20260620

Procedure:
- Official Graphify detect on `01_foundations` with local `.graphifyignore` scope controls.
- Official Graphify AST extraction for supported code files.
- Graphify semantic extraction with 16 chunk files under staging.
- Chunks 01-12 used Codex worker extraction and wrote validated `.graphify_chunk_NN.json` files.
- Chunks 13-16 used deterministic bounded structural extraction from Markdown headings, file identity, family terms, and explicit intra-chunk structure after worker subagents failed to write chunk files within the operational window.
- Semantic chunks were normalized, deduplicated, and merged with AST into `.graphify_extract.json`.
- Official Graphify `build_from_json` assembly.
- Official Graphify clustering, analysis, report generation, JSON export, and HTML export.
- Root `01_foundations/graphify-out/graph.json` intentionally not created.

Leaf stats:
- nodes: 1002
- edges: 1381
- communities: 93
- detected_files: 341
- detected_words: 476827
- semantic_chunks: 16
- semantic_nodes_before_build: 944
- semantic_edges_before_build: 1168
- hyperedges_before_build: 48
- extract_nodes_before_build: 1004
- extract_edges_before_build: 1438
- extract_hyperedges_before_build: 48

Chunk status:
- .graphify_chunk_01.json: codex_worker; nodes=78; edges=71; hyperedges=3
- .graphify_chunk_02.json: codex_worker; nodes=83; edges=67; hyperedges=3
- .graphify_chunk_03.json: codex_worker; nodes=57; edges=71; hyperedges=3
- .graphify_chunk_04.json: codex_worker; nodes=63; edges=55; hyperedges=3
- .graphify_chunk_05.json: codex_worker; nodes=72; edges=77; hyperedges=3
- .graphify_chunk_06.json: codex_worker; nodes=50; edges=61; hyperedges=3
- .graphify_chunk_07.json: codex_worker; nodes=57; edges=68; hyperedges=3
- .graphify_chunk_08.json: codex_worker; nodes=51; edges=60; hyperedges=3
- .graphify_chunk_09.json: codex_worker; nodes=46; edges=50; hyperedges=3
- .graphify_chunk_10.json: codex_worker; nodes=58; edges=74; hyperedges=3
- .graphify_chunk_11.json: codex_worker; nodes=42; edges=53; hyperedges=3
- .graphify_chunk_12.json: codex_worker; nodes=40; edges=57; hyperedges=3
- .graphify_chunk_13.json: deterministic_bounded_structural; nodes=69; edges=115; hyperedges=3
- .graphify_chunk_14.json: deterministic_bounded_structural; nodes=72; edges=127; hyperedges=3
- .graphify_chunk_15.json: deterministic_bounded_structural; nodes=60; edges=98; hyperedges=3
- .graphify_chunk_16.json: deterministic_bounded_structural; nodes=46; edges=64; hyperedges=3

Inclusion policy:
- Included semantic authority documents, contracts, schemas, registries, policies, validators, data quality report Markdown, and `inspection_dossiers/` Markdown/YAML readouts.
- Excluded `evidence_assets/`, prior `graphify-out/`, notebooks, parquet/CSV/runtime data, images, and binary evidence assets according to `.graphifyignore`.

Build notes:
- No Ollama or local LLM backend was used.
- Chunks 13-16 are intentionally marked as deterministic bounded structural extraction because subagent extraction did not produce files. This is not hidden as equivalent to full worker semantic extraction.
- The authoritative leaf artifacts are the files in this directory.
- Temporary staging is reconstructible and not the promoted leaf output.

Built at UTC: 2026-06-20T23:09:08.992554+00:00
