# Build Manifest: certification_decisions

- **Run ID:** `certification_decisions_20260805T073308Z`
- **Status:** `complete`
- **Build completed (UTC):** `2026-08-05T08:51:21.9510773Z`
- **Graph family / leaf:** `data_certification / certification_decisions`
- **Mode:** full semantic rebuild plus governed three-file delta
- **Directionality:** undirected

## Provenance

- **Repository:** `C:\TSIS_Data`
- **Branch:** `integrate/main-data-quality-dossiers-20260613`
- **Commit:** `b54680664270d9d9a2f46468331fc1ae4308f3e5`
- **Dirty at authorization:** yes, 96 paths; unrelated user changes preserved
- **Graphify package:** `0.9.33`
- **Upstream:** `https://github.com/Graphify-Labs/graphify`
- **Skill:** `C:\Users\AlexJ\.codex\skills\graphify\SKILL.md`
- **Skill SHA-256:** `9024289348CCEB6140AF33E9875742DC55F55E5D574E44E5A21BB36239B1BCF4`
- **Corpus manifest SHA-256:** `DFF7661B0AB2A2D00C6D30E90904816685FBA8E7AF7EEB15F9E07F9B60843B9B`

## Corpus

- **Canonical evidence root:** `C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_research\01_auditoria_RAW_DATA\00_data_certification`
- **Controlled build root:** `C:\tmp\TSIS_graphify_workspaces\certification_decisions\corpus`
- **Files / words:** 88 / 46,992
- **Structured files:** 1 JSON
- **Semantic documents:** 87

Included: certification Markdown, lightweight global-metrics JSON, selected audit
contracts/closeouts/policies, and four Graphify governance documents.

Excluded: notebooks, images, CSV/Parquet evidence, runtime outputs, prior graphs,
and living authority contracts owned by `01_foundations`.

## Extraction

- **External API:** none
- **Semantic engine:** Codex host
- **Initial extraction:** four workers over 22, 22, 22 and 21 documents
- **Governance delta:** one worker over 3 changed documents; 84 cache hits
- **AST:** 48 nodes / 47 edges
- **Semantic:** 235 nodes / 267 edges, including 3 hyperedges
- **Token accounting:** unavailable from Codex subagent transport; zero is recorded, not estimated
- **Semantic cache:** all 87 documents stamped with extraction-spec provenance

## Result

- **Nodes:** 283
- **Edges:** 314
- **Communities:** 19
- **Duplicate node IDs / edges:** 0 / 0
- **Dangling / missing endpoints:** 0 / 0
- **Self-loops / collapsed edges:** 0 / 0
- **Graph type:** `Graph`

## Acceptance

- Built with `graphify.build.build_from_json(..., directed=False)`
- Diagnosed with `graphify.diagnostics.diagnose_extraction`
- Published artifact diagnosed with `graphify diagnose multigraph --json`
- Smoke query: `graphify explain "Final Certification Process"`
- HTML regenerated after the final semantic delta

## Refresh

- **Incremental command:** run `graphify update` from the controlled build root
- **Full rebuild triggers:** extraction-spec or protocol change, authority-boundary change, or intentional graph shrink
- **Completed queue item:** official `certification_decisions_graph` semantic leaf
- **Pending:** notebook evidence leaf, `01_foundations` authority graph, and higher-level fusion graphs

## Artifacts

- `graph.json`
- `graph.html`
- `GRAPH_REPORT.md`
- `GRAPH_HEALTH.json` and `GRAPH_HEALTH.txt`
- `manifest.json` and `corpus_manifest.json`
- `.graphify_labels.json`
- `cost.json`

The stable path is canonical for new integrations. Dated leaves remain preserved
as historical audit evidence.
