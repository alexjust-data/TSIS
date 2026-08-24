# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 5 files · ~7,897 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 45 nodes · 65 edges · 7 communities
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 13 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Layered Market Activation
- Eligible Universe Construction
- Screener Authority Boundaries
- Governed Screener Execution
- Evidence and Backtest Gates
- Downstream Consumer Contracts
- Sealed Validation Artifacts

## God Nodes (most connected - your core abstractions)
1. `Layered Screener System Design` - 7 edges
2. `Market Activation / Wake-Up` - 6 edges
3. `Evidence Bundle` - 6 edges
4. `DailyEligibleUniverseResolver` - 6 edges
5. `Screener Engine Authority and Consumer Boundary` - 5 edges
6. `Daily Eligible Universe Selector` - 5 edges
7. `daily_eligible_universe_proxy_v0_1` - 5 edges
8. `Daily Eligible Universe` - 4 edges
9. `Strategy-Specific In-Play Scanners` - 4 edges
10. `Trading Activity and Wake-Up Consumption` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Daily Eligible Universe` --semantically_similar_to--> `Daily Eligible Universe Selector`  [INFERRED] [semantically similar]
  00_CTO/15_SCREENER_ENGINE/00_STRUCTURE_SYSTEM.md → 00_CTO/15_SCREENER_ENGINE/README.md
- `Daily Eligible Universe Selector` --semantically_similar_to--> `DailyEligibleUniverseResolver`  [INFERRED] [semantically similar]
  00_CTO/15_SCREENER_ENGINE/README.md → 00_CTO/15_SCREENER_ENGINE/SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1.md
- `DailyEligibleUniverseResolver` --semantically_similar_to--> `daily_eligible_universe_proxy_v0_1`  [INFERRED] [semantically similar]
  00_CTO/15_SCREENER_ENGINE/SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1.md → 00_CTO/15_SCREENER_ENGINE/01_LAYER_1/initial_idea.MD
- `Market Activation / Wake-Up` --conceptually_related_to--> `Trading Activity and Wake-Up Consumption`  [INFERRED]
  00_CTO/15_SCREENER_ENGINE/00_STRUCTURE_SYSTEM.md → 00_CTO/15_SCREENER_ENGINE/README.md
- `Strategy-Specific In-Play Scanners` --conceptually_related_to--> `ScannerDefinitionRegistry`  [INFERRED]
  00_CTO/15_SCREENER_ENGINE/00_STRUCTURE_SYSTEM.md → 00_CTO/15_SCREENER_ENGINE/SCREENER_ENGINE_ARCHITECTURE_PROPOSAL_v0_1.md

## Hyperedges (group relationships)
- **Daily PIT Universe Consistency** — 00_cto_15_screener_engine_00_structure_system_daily_eligible_universe, 00_cto_15_screener_engine_readme_daily_eligible_universe_selector, 00_cto_15_screener_engine_screener_engine_architecture_proposal_v0_1_daily_eligible_universe_resolver, 00_cto_15_screener_engine_01_layer_1_initial_idea_daily_eligible_universe_proxy_v0_1 [INFERRED 0.95]
- **Sealed Artifact Consumer Boundary** — 00_cto_15_screener_engine_00_structure_system_sealed_screener_artifact, 00_cto_15_screener_engine_readme_backtest_artifact_consumption, 00_cto_15_screener_engine_screener_engine_architecture_proposal_v0_1_sealed_run_contract, 00_cto_15_screener_engine_screener_engine_architecture_proposal_v0_1_consumer_adapters [INFERRED 0.85]
- **Presession Proxy Scope Preservation** — 00_cto_15_screener_engine_00_structure_system_daily_eligible_universe, 00_cto_15_screener_engine_screener_engine_architecture_proposal_v0_1_presession_4824_candidate, 00_cto_15_screener_engine_01_layer_1_initial_idea_market_cap_proxy_layer, 00_cto_15_screener_engine_01_layer_1_initial_idea_sec_os_pit_successor [INFERRED 0.85]

## Communities (7 total, 0 thin omitted)

### Community 0 - "Layered Market Activation"
Cohesion: 0.46
Nodes (8): Daily Eligible Universe, Layered Screener System Design, Heavy Observation, Light Observation State, Market Activation / Wake-Up, Reason-Preserving Activation, Strategy-Specific In-Play Scanners, Two-Clock Screener

### Community 1 - "Eligible Universe Construction"
Cohesion: 0.25
Nodes (8): daily_eligible_universe_proxy_v0_1, Layer 1 Initial Idea, Market-Cap Proxy Layer, Proxy Membership States, SEC O/S PIT Successor Universe, Session Freeze Manifest, Presession Selector Evidence, Presession 4,824 Candidate

### Community 2 - "Screener Authority Boundaries"
Cohesion: 0.38
Nodes (7): Screener Engine Evidence Index, Screener Engine Conceptual Authority, Screener Engine Authority and Consumer Boundary, Independent Screener Runtime, Consumer Adapters, Screener Engine Architecture Proposal v0.1, Screener Layer Separation

### Community 3 - "Governed Screener Execution"
Cohesion: 0.33
Nodes (7): ArtifactWriter, DailyEligibleUniverseResolver, Fail-Closed Execution, InputManifestResolver, ScannerDefinitionRegistry, ScannerExecutor, ScreenerRunValidator

### Community 4 - "Evidence and Backtest Gates"
Cohesion: 0.33
Nodes (6): Backtest Engine Authority Evidence, Evidence Bundle, Processed Bibliography and Source Maps, Repository Originals as Authority, Scanner Conceptual Precedents, BT-GATE-016

### Community 5 - "Downstream Consumer Contracts"
Cohesion: 0.40
Nodes (6): Backtest Artifact Consumption, Consumer-Specific Adoption Gates, Daily Eligible Universe Selector, Restricted A/B Consumption Bridge, Single Membership Authority, Trading Activity and Wake-Up Consumption

### Community 6 - "Sealed Validation Artifacts"
Cohesion: 0.67
Nodes (3): Sealed Screener Artifact, Scientific Validation Process, Sealed Screener Run Contract

## Knowledge Gaps
- **6 isolated node(s):** `Scanner Conceptual Precedents`, `Processed Bibliography and Source Maps`, `Restricted A/B Consumption Bridge`, `Proxy Membership States`, `Session Freeze Manifest` (+1 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DailyEligibleUniverseResolver` connect `Governed Screener Execution` to `Eligible Universe Construction`, `Screener Authority Boundaries`, `Downstream Consumer Contracts`?**
  _High betweenness centrality (0.346) - this node is a cross-community bridge._
- **Why does `Daily Eligible Universe Selector` connect `Downstream Consumer Contracts` to `Layered Market Activation`, `Governed Screener Execution`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `Layered Screener System Design` connect `Layered Market Activation` to `Screener Authority Boundaries`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `DailyEligibleUniverseResolver` (e.g. with `Daily Eligible Universe Selector` and `daily_eligible_universe_proxy_v0_1`) actually correct?**
  _`DailyEligibleUniverseResolver` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Scanner Conceptual Precedents`, `Processed Bibliography and Source Maps`, `Restricted A/B Consumption Bridge` to the rest of the system?**
  _6 weakly-connected nodes found - possible documentation gaps or missing edges._