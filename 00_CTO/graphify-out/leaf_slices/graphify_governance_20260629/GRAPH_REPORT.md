# Graph Report - C:\TSIS_Data  (2026-06-29)

## Corpus Check
- 22 files · ~64,775 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 39 nodes · 65 edges · 10 communities
- Extraction: 55% EXTRACTED · 45% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `362a031e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Refresh Queue Control|Refresh Queue Control]]
- [[_COMMUNITY_Operational Telemetry|Operational Telemetry]]
- [[_COMMUNITY_Refresh Queue Control|Refresh Queue Control]]
- [[_COMMUNITY_Certification Graph|Certification Graph]]
- [[_COMMUNITY_Agent Traceability|Agent Traceability]]
- [[_COMMUNITY_Governance Cluster 5|Governance Cluster 5]]
- [[_COMMUNITY_Governance Cluster 6|Governance Cluster 6]]
- [[_COMMUNITY_Agent Traceability|Agent Traceability]]
- [[_COMMUNITY_Refresh Queue Control|Refresh Queue Control]]
- [[_COMMUNITY_Data Foundation Graph|Data Foundation Graph]]

## God Nodes (most connected - your core abstractions)
1. `CTO Graphify Official Build Protocol` - 12 edges
2. `Data Foundation Graphify Official Build Protocol` - 11 edges
3. `Data Certification Graphify Official Build Protocol` - 8 edges
4. `Graph Delta Audit` - 7 edges
5. `Mandatory Reading Order` - 6 edges
6. `Long Running Operations Contract` - 6 edges
7. `Cross Project Graphify Governance Leaf Build` - 5 edges
8. `Progress Telemetry Standard` - 5 edges
9. `CTO Root Graph` - 5 edges
10. `Build Manifest Baseline` - 5 edges

## Surprising Connections (you probably didn't know these)
- `No Hidden State Assumption` --conceptually_related_to--> `Graph Delta Audit`  [INFERRED]
  AGENTS.md → 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Architecture Overview` --conceptually_related_to--> `CTO Root Graph`  [INFERRED]
  ARCHITECTURE_OVERVIEW.md → 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Data Foundation Graphify Refresh Queue` --conceptually_related_to--> `Graph Delta Audit`  [INFERRED]
  01_TSIS_backtest_SmallCaps/01_foundations/GRAPHIFY_REFRESH_QUEUE.md → 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md
- `Mandatory Reading Order` --references--> `Versioning Standards`  [EXTRACTED]
  AGENTS.md → VERSIONING_STANDARDS.md
- `Reproducibility Minimum` --conceptually_related_to--> `Build Manifest Baseline`  [INFERRED]
  AGENTS.md → 00_CTO/GRAPHIFY_OFFICIAL_BUILD_PROTOCOL.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Three Root Graphify Governance** — 00_cto_graphify_official_build_protocol_cto_root_graph, 01_tsis_backtest_smallcaps_01_foundations_graphify_official_build_protocol_data_foundation_root_graph, 01_tsis_backtest_smallcaps_01_research_01_auditoria_raw_data_00_data_certification_graphify_official_build_protocol_data_certification_root_graph [INFERRED 0.85]
- **Long Running Graphify Observability** — long_running_operations_contract_pre_manifest, long_running_operations_contract_heartbeat, long_running_operations_contract_pid_manifest, long_running_operations_contract_separate_monitor [EXTRACTED 1.00]

## Communities (10 total, 0 thin omitted)

### Community 0 - "Refresh Queue Control"
Cohesion: 0.40
Nodes (5): No API Mode, Data Foundation Graphify Official Build Protocol, Data Foundation Graphify Refresh Queue, Data Foundation README, SmallCaps Local Rules

### Community 1 - "Operational Telemetry"
Cohesion: 0.40
Nodes (5): Heartbeat, PID Manifest, Pre Manifest, Progress Telemetry Standard, Separate Monitor

### Community 2 - "Refresh Queue Control"
Cohesion: 0.50
Nodes (4): CTO Graphify Official Build Protocol, Leaf First Graph Build, CTO Graphify Refresh Queue, CTO Local Rules

### Community 3 - "Certification Graph"
Cohesion: 1.00
Nodes (4): CTO Root Graph, Root Merge Gate, Data Foundation Root Graph, Data Certification Root Graph

### Community 4 - "Agent Traceability"
Cohesion: 0.50
Nodes (4): Graphify Runtime Output, Institutional Artifacts, No Hidden State Assumption, TSIS Agents Contract

### Community 5 - "Governance Cluster 5"
Cohesion: 0.50
Nodes (4): Mandatory Reading Order, Architecture Overview, Project Operating System, Research Philosophy

### Community 6 - "Governance Cluster 6"
Cohesion: 0.50
Nodes (4): Cross Project Graphify Governance Leaf Build, Root Changelog, Long Running Operations Contract, Project Rules

### Community 7 - "Agent Traceability"
Cohesion: 0.67
Nodes (3): Build Manifest Baseline, Reproducibility Minimum, Versioning Standards

### Community 8 - "Refresh Queue Control"
Cohesion: 1.00
Nodes (3): Graph Delta Audit, Data Certification Graphify Official Build Protocol, Data Certification Graphify Refresh Queue

### Community 9 - "Data Foundation Graph"
Cohesion: 1.00
Nodes (3): Data Foundation Graph and Table Design Protocol, Data Foundation Outputs, Market State Tables

## Knowledge Gaps
- **10 isolated node(s):** `Project Operating System`, `Root Changelog`, `Research Philosophy`, `Pre Manifest`, `Heartbeat` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Data Foundation Graphify Official Build Protocol` connect `Refresh Queue Control` to `Refresh Queue Control`, `Certification Graph`, `Governance Cluster 6`, `Agent Traceability`, `Refresh Queue Control`, `Data Foundation Graph`?**
  _High betweenness centrality (0.328) - this node is a cross-community bridge._
- **Why does `CTO Graphify Official Build Protocol` connect `Refresh Queue Control` to `Refresh Queue Control`, `Certification Graph`, `Agent Traceability`, `Governance Cluster 6`, `Agent Traceability`, `Refresh Queue Control`?**
  _High betweenness centrality (0.289) - this node is a cross-community bridge._
- **Why does `Long Running Operations Contract` connect `Governance Cluster 6` to `Refresh Queue Control`, `Refresh Queue Control`, `Refresh Queue Control`, `Operational Telemetry`?**
  _High betweenness centrality (0.278) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `CTO Graphify Official Build Protocol` (e.g. with `CTO Local Rules` and `Cross Project Graphify Governance Leaf Build`) actually correct?**
  _`CTO Graphify Official Build Protocol` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Data Foundation Graphify Official Build Protocol` (e.g. with `Leaf First Graph Build` and `Data Foundation README`) actually correct?**
  _`Data Foundation Graphify Official Build Protocol` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Data Certification Graphify Official Build Protocol` (e.g. with `Leaf First Graph Build` and `Cross Project Graphify Governance Leaf Build`) actually correct?**
  _`Data Certification Graphify Official Build Protocol` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Graph Delta Audit` (e.g. with `CTO Graphify Refresh Queue` and `Data Foundation Graphify Refresh Queue`) actually correct?**
  _`Graph Delta Audit` has 4 INFERRED edges - model-reasoned connections that need verification._