# Graph Report - C:\TSIS_Data  (2026-08-22)

## Corpus Check
- 22 files · ~60,234 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 273 nodes · 684 edges · 9 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 7 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e71c6ce5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Corpus Distillation Pipeline
- P15 Pilot Generation
- P09 Pilot Generation
- Cognitive Audit Architecture
- P02 Pilot Generation
- Distillation Validation Toolchain
- Lesson Pack Traceability
- Agentic Harness Architecture
- Data Audit Operations

## God Nodes (most connected - your core abstractions)
1. `process_lesson()` - 26 edges
2. `TSIS Cognitive Architecture` - 17 edges
3. `main()` - 16 edges
4. `Agentic Harness Architecture Reference for TSIS` - 16 edges
5. `main()` - 15 edges
6. `main()` - 14 edges
7. `rel_project()` - 14 edges
8. `Section` - 12 edges
9. `write_text()` - 11 edges
10. `write_text()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Minimum Dataset Audit Package` --semantically_similar_to--> `Lesson Pack Artifact Contract`  [INFERRED] [semantically similar]
  00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/10_DATA_QUALITY_HARNESS/data_audit_completion_artifact_contract.md → 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md
- `Layered Validation` --semantically_similar_to--> `Lesson Quality Report`  [INFERRED] [semantically similar]
  00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/shared_validation_principles.md → 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/20_SERSAN_DISTILLATION_HARNESS/sersan_lesson_pack_contract.md
- `TSIS Cognitive Architecture` --references--> `Agentic Harness Architecture Reference for TSIS`  [EXTRACTED]
  00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/README.md → 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/agentic_harness_architecture_reference.md
- `TSIS Cognitive Architecture` --references--> `Harness Toolchain Traceability Contract`  [EXTRACTED]
  00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/README.md → 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/harness_toolchain_traceability_contract.md
- `TSIS Cognitive Architecture` --references--> `Shared Run Manifest Contract`  [EXTRACTED]
  00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/README.md → 00_CTO/12_TSIS_COGNITIVE_ARCHITECTURE/00_SHARED_HARNESS_KERNEL/shared_run_manifest_contract.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Shared Harness Kernel** — 00_cto_12_tsis_cognitive_architecture_00_shared_harness_kernel_agentic_harness_architecture_reference_agentic_harness, 00_cto_12_tsis_cognitive_architecture_00_shared_harness_kernel_harness_toolchain_traceability_contract_toolchain_traceability, 00_cto_12_tsis_cognitive_architecture_00_shared_harness_kernel_shared_run_manifest_contract_shared_run_manifest, 00_cto_12_tsis_cognitive_architecture_00_shared_harness_kernel_shared_validation_principles_layered_validation, 00_cto_12_tsis_cognitive_architecture_00_shared_harness_kernel_agentic_harness_architecture_reference_governance_gate [INFERRED 0.95]
- **Data Quality Evidence Promotion Flow** — 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_data_audit_completion_artifact_contract_historical_preflight, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_data_audit_harness_agentic_operating_map_recurrent_data_audit_operating_system, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_data_audit_completion_artifact_contract_evidence_assets, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_historical_audit_preservation_and_promotion_contract_historical_audit_preservation, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_historical_audit_preservation_and_promotion_contract_evidence_promotion, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_data_audit_completion_artifact_contract_consumption_decision, 00_cto_12_tsis_cognitive_architecture_10_data_quality_harness_future_live_data_quality_contract_live_data_quality_harness [INFERRED 0.95]
- **Sersan Lesson Distillation Flow** — 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_distillation_protocol_lesson_pack, 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_distillation_protocol_mechanical_rule_extraction, 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_distillation_protocol_tsis_translation, 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_distillation_protocol_doctrine_review, 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_lesson_pack_contract_lesson_pack_artifact_contract, 00_cto_12_tsis_cognitive_architecture_20_sersan_distillation_harness_sersan_pilot_harness_runbook_three_lesson_pilot [INFERRED 0.95]

## Communities (9 total, 0 thin omitted)

### Community 0 - "Corpus Distillation Pipeline"
Cohesion: 0.11
Nodes (60): bool_str(), build_images(), build_sections(), build_toolchain_artifacts(), build_translations(), classify_section(), classify_visual(), clean_heading() (+52 more)

### Community 1 - "P15 Pilot Generation"
Cohesion: 0.15
Nodes (35): build_image_records(), build_sections(), directory_hash(), extract_image_refs(), image_id(), image_md_path(), image_md_path_from_record(), main() (+27 more)

### Community 2 - "P09 Pilot Generation"
Cohesion: 0.15
Nodes (33): build_image_records(), build_sections(), directory_hash(), find_section_for_line(), image_id(), image_md_path(), main(), normalize_ref() (+25 more)

### Community 3 - "Cognitive Audit Architecture"
Cohesion: 0.10
Nodes (33): Consumption Decision, Data Audit Completion Artifact Contract, Evidence Assets, Historical Preflight, Minimum Dataset Audit Package, Protected Data Roots, TSIS Data Audit Harness Agentic Operating Map, Historical-to-Live Audit Bridge (+25 more)

### Community 4 - "P02 Pilot Generation"
Cohesion: 0.16
Nodes (30): build_images(), build_rules(), build_sections(), default_image_class(), find_section_for_line(), image_id(), main(), Path (+22 more)

### Community 5 - "Distillation Validation Toolchain"
Cohesion: 0.25
Nodes (24): find_project_root(), harness_paths(), load_inventory(), main(), prohibited_path(), project_path(), project_root(), Any (+16 more)

### Community 6 - "Lesson Pack Traceability"
Cohesion: 0.14
Nodes (24): Harness Toolchain Traceability Contract, Hash-Bound Execution, Project-Local Toolchain, Harness Toolchain Traceability, Traceable Re-Execution, Shared Run Manifest Contract, Extension Without Relaxation, Shared Run Manifest (+16 more)

### Community 7 - "Agentic Harness Architecture"
Cohesion: 0.19
Nodes (16): Agentic Harness, Anthropic Agentic Guidance, Context Builder, Google DeepMind AlphaEvolve, Agentic Harness Architecture Reference for TSIS, Evaluator Layer, Governance Gate, Context + Tools + Memory + Contracts + Evaluators + Traces + Guardrails + Orchestration (+8 more)

### Community 8 - "Data Audit Operations"
Cohesion: 0.26
Nodes (12): Data Audit Agent Prompt Pack - 2026-06-12, One Dataset per Run, Prompt-Protected Paths, Single-Agent Data Audit Completion, Overnight Data Audit Completion Harness Runbook, Human Review Between Datasets, Mature-Block Benchmark, Overnight Completion Workflow (+4 more)

## Knowledge Gaps
- **4 isolated node(s):** `Memory Manager`, `OpenAI Agentic Guidance`, `Anthropic Agentic Guidance`, `Google DeepMind AlphaEvolve`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TSIS Cognitive Architecture` connect `Cognitive Audit Architecture` to `Lesson Pack Traceability`, `Agentic Harness Architecture`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `Agentic Harness Architecture Reference for TSIS` connect `Agentic Harness Architecture` to `Cognitive Audit Architecture`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `Minimum Dataset Audit Package` connect `Cognitive Audit Architecture` to `Data Audit Operations`, `Lesson Pack Traceability`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **What connects `Memory Manager`, `OpenAI Agentic Guidance`, `Anthropic Agentic Guidance` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Corpus Distillation Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.11422527763088314 - nodes in this community are weakly interconnected._
- **Should `P09 Pilot Generation` be split into smaller, more focused modules?**
  _Cohesion score 0.1497326203208556 - nodes in this community are weakly interconnected._
- **Should `Cognitive Audit Architecture` be split into smaller, more focused modules?**
  _Cohesion score 0.10227272727272728 - nodes in this community are weakly interconnected._