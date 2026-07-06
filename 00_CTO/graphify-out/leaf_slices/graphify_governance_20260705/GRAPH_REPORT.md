# Graph Report - C:\TSIS_Data  (2026-07-05)

## Corpus Check
- 45 files · ~95,492 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 57 nodes · 251 edges · 7 communities
- Extraction: 1% EXTRACTED · 99% INFERRED · 0% AMBIGUOUS · INFERRED: 248 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f94bc013`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Graph Cluster 0|Graph Cluster 0]]
- [[_COMMUNITY_Graph Cluster 1|Graph Cluster 1]]
- [[_COMMUNITY_Graph Cluster 2|Graph Cluster 2]]
- [[_COMMUNITY_Graph Cluster 3|Graph Cluster 3]]
- [[_COMMUNITY_Graph Cluster 4|Graph Cluster 4]]
- [[_COMMUNITY_Graph Cluster 5|Graph Cluster 5]]
- [[_COMMUNITY_Graph Cluster 6|Graph Cluster 6]]

## God Nodes (most connected - your core abstractions)
1. `Dirty Working Tree Snapshot` - 46 edges
2. `CTO Architecture` - 35 edges
3. `Agent Rules` - 28 edges
4. `Versioning Standards` - 28 edges
5. `Data Foundation Module` - 26 edges
6. `Minute Data Uses E:/TSIS Root` - 23 edges
7. `Market Science` - 19 edges
8. `Project Operating System` - 16 edges
9. `Graphify Refresh Queue` - 14 edges
10. `Graphify Official Build Protocol` - 10 edges

## Surprising Connections (you probably didn't know these)
- `00_privado` --defines_or_references--> `CTO Architecture`  [INFERRED]
  00_TSIS_Lab/00_CTO/00_privado.md → PROJECT_OPERATING_SYSTEM.md
- `Dirty Working Tree Snapshot` --includes_current_file--> `README`  [INFERRED]
  PROJECT_OPERATING_SYSTEM.md → 00_TSIS_Lab/05_adapters/smallcaps/README.md
- `CHANGELOG` --defines_or_references--> `Project Operating System`  [INFERRED]
  00_CTO/CHANGELOG.md → PROJECT_OPERATING_SYSTEM.md
- `GRAPHIFY_REFRESH_QUEUE` --defines_or_references--> `Project Operating System`  [INFERRED]
  00_CTO/GRAPHIFY_REFRESH_QUEUE.md → PROJECT_OPERATING_SYSTEM.md
- `LOCAL_RULES` --defines_or_references--> `Project Operating System`  [INFERRED]
  00_CTO/LOCAL_RULES.md → PROJECT_OPERATING_SYSTEM.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Project Governance Refresh 20260705** — tsis_governance_concept_project_operating_system, tsis_governance_concept_agent_rules, tsis_governance_concept_versioning_standards, tsis_governance_concept_graphify_official_protocol, tsis_governance_concept_graphify_refresh_queue, tsis_governance_concept_cto_architecture, tsis_governance_concept_data_foundation, tsis_governance_concept_market_science, tsis_governance_concept_research_philosophy, tsis_governance_concept_long_running_operations, tsis_governance_concept_minute_data_e_root, tsis_governance_concept_dirty_snapshot [INFERRED 0.90]

## Communities (7 total, 0 thin omitted)

### Community 0 - "Graph Cluster 0"
Cohesion: 0.45
Nodes (11): GRAPHIFY_OFFICIAL_BUILD_PROTOCOL, GRAPHIFY_REFRESH_QUEUE, LOCAL_RULES, README, GRAPHIFY_OFFICIAL_BUILD_PROTOCOL, GRAPHIFY_REFRESH_QUEUE, LOCAL_RULES, README (+3 more)

### Community 1 - "Graph Cluster 1"
Cohesion: 0.18
Nodes (11): 00_privado, knowledge_object_promotion_contract_v0_1, parameter_sweep_protocol_v0_1, research_experiment_contract_v0_1, scientific_validation_pipeline_contract_v0_1, knowledge_object_registry_v0_1, research_experiment_registry_v0_1, evidence_report_template (+3 more)

### Community 2 - "Graph Cluster 2"
Cohesion: 0.42
Nodes (11): README, AGENTS, LONG_RUNNING_OPERATIONS_CONTRACT, PROJECT_OPERATING_SYSTEM, PROJECT_RULES, README, RESEARCH_PHILOSOPHY, START_HERE (+3 more)

### Community 3 - "Graph Cluster 3"
Cohesion: 0.33
Nodes (9): README, 01_privado2, README, research_design, data_sources, CHANGELOG, LOCAL_RULES, CTO Architecture (+1 more)

### Community 4 - "Graph Cluster 4"
Cohesion: 0.40
Nodes (5): 05_07_2026, README, TSIS_LAB_ARCHITECTURE_v3, CHANGELOG, Research Philosophy

### Community 5 - "Graph Cluster 5"
Cohesion: 0.40
Nodes (5): README, research_experiment_execution_protocol_v0_1, README, CHANGELOG, Minute Data Uses E:/TSIS Root

### Community 6 - "Graph Cluster 6"
Cohesion: 0.40
Nodes (5): CHANGELOG, execution_bridge, README, AGENTS, Data Foundation Module

## Knowledge Gaps
- **6 isolated node(s):** `knowledge_object_promotion_contract_v0_1`, `parameter_sweep_protocol_v0_1`, `knowledge_object_registry_v0_1`, `research_experiment_registry_v0_1`, `evidence_report_template` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Dirty Working Tree Snapshot` connect `Graph Cluster 1` to `Graph Cluster 0`, `Graph Cluster 2`, `Graph Cluster 3`, `Graph Cluster 4`, `Graph Cluster 5`, `Graph Cluster 6`?**
  _High betweenness centrality (0.414) - this node is a cross-community bridge._
- **Why does `CTO Architecture` connect `Graph Cluster 3` to `Graph Cluster 0`, `Graph Cluster 1`, `Graph Cluster 2`, `Graph Cluster 4`, `Graph Cluster 5`, `Graph Cluster 6`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Why does `Agent Rules` connect `Graph Cluster 0` to `Graph Cluster 1`, `Graph Cluster 2`, `Graph Cluster 3`, `Graph Cluster 4`, `Graph Cluster 5`, `Graph Cluster 6`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Dirty Working Tree Snapshot` (e.g. with `05_07_2026` and `README`) actually correct?**
  _`Dirty Working Tree Snapshot` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `CTO Architecture` (e.g. with `05_07_2026` and `README`) actually correct?**
  _`CTO Architecture` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `Agent Rules` (e.g. with `README` and `README`) actually correct?**
  _`Agent Rules` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `Versioning Standards` (e.g. with `05_07_2026` and `CHANGELOG`) actually correct?**
  _`Versioning Standards` has 27 INFERRED edges - model-reasoned connections that need verification._