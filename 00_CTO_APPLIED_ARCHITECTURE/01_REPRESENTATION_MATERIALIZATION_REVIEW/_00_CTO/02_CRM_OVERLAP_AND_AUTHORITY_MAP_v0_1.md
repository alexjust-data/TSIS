# CRM Overlap And Authority Map v0.1

Status: `architectural_review_v0_1`

Reviewed object: `C:\TSIS_Data\00_CTO_1\01_CANONICAL_REPRESENTATION_MATERIALIZATION`

Reviewed as: `candidate_architecture`

Review date: `2026-07-14`

## Overlap Classes

- `none`: no material overlap found.
- `complementary`: adds a useful bridge or operational view without replacing prior authority.
- `partial_duplicate`: repeats part of an existing authority and must be reduced or cited.
- `strong_duplicate`: restates an existing authority so heavily that it risks becoming a parallel source of truth.
- `authority_conflict`: would contradict or supersede an existing authority if adopted as written.

## Authority Rule

The candidate CRM book may only become authoritative for the review workflow that connects semantic representation to physical realization. It must not become the primary authority for market ontology, materialization modes, schema contracts, dataset contracts, validators, builders, manifests, status matrices or promotion rules.

## Chapter Authority Map

### Chapter 1 - Purpose

Overlap classification: `complementary`

Authority documented before this book:

- `C:\TSIS_Data\AGENTS.md`, sections `No Hidden State Assumption`, `Reglas operativas no negociables`, `Regla final`.
- `C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md`, root operating model.
- `C:\TSIS_Data\00_CTO_1\05_TABLES\README.md`, section `Lectura obligatoria`.
- `C:\TSIS_Data\00_CTO_1\05_TABLES\paths.md`, section `Source of truth`.

Content that already exists:

- TSIS requires structural knowledge to live in repo artifacts.
- `05_TABLES` is an inspection/index surface, not source of truth.
- Source of truth for table creation is `01_foundations`, scripts, tests and manifests.

Content really new:

- A named bridge between epistemological representation theory and physical materialization.

Risk of second source of truth:

- Low if the chapter states candidate status and explicitly defers to existing authorities.

Correct location:

- Keep in CRM book as an authority-boundary introduction.

### Chapter 2 - Canonical Market Representations

Overlap classification: `partial_duplicate`; possible `authority_conflict` if left as ontology.

Authority documented before this book:

- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`, sections `16.2 Semantic Existence vs Physical Materialization`, `16.3 Materialization Modes`.
- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\19_Chapter_18_Representation_Governance_TSIS.md`, sections `Governance Hierarchy`, `Change Classes`, `Promotion Path`.
- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\22_Chapter_21_Constitutional_Principles_TSIS.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_canonical_vs_representation_layer_contract_v0_1.md`.

Content that already exists:

- The representation layer is distinct from implementation.
- Semantic authority precedes physical materialization.
- State is not signal, strategy, outcome, reward or execution fill.

Content really new:

- The book attempts to name the handoff from canonical representation to physical representation.

Risk of second source of truth:

- High if "Canonical Market Representation" is defined independently of Market Representation Part I.

Correct location:

- Semantic definition stays in `00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY`.
- CRM should keep only a reference/interface chapter and a required `canonical_representation_ref`.

### Chapter 3 - Representation Justification

Overlap classification: `complementary`

Authority documented before this book:

- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, sections `Institutional maturity status model`, `Promotion barrier`, `Required Versioning Practices`.
- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\19_Chapter_18_Representation_Governance_TSIS.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`, section `target_contract = que debe existir y por que`.

Content that already exists:

- Promotion requires owner, semantics, reproducibility, compatibility and validation.
- Target contracts define why outputs should exist.

Content really new:

- A pre-materialization justification record with separate justification types.
- Explicit category `Enabling Institutional Artifact`, useful for `instrument_master`, `expected_data_calendar` and `dataset_certification_matrix`.

Risk of second source of truth:

- Medium if the record duplicates target contracts instead of extending them.

Correct location:

- Keep the theory in CRM.
- Store the operational fields in dataset contracts, registry entries or a controlled proposal template.

### Chapter 4 - Materialization Decision

Overlap classification: `partial_duplicate`

Authority documented before this book:

- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\17_Chapter_16_Materialization_Policy_TSIS.md`, sections `16.2`, `16.3`, `16.12`, `16.13`.
- `C:\TSIS_Data\00_CTO_1\05_TABLES\_00_CTO\politica_cobertura_full_history_tsis.md`, sections on full-history meanings and microstructure selectivity.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\market_state_coverage_and_lookback_policy_v0_1.md`, sections `Coberturas Permitidas`, `Campos Obligatorios En Futuros Manifests`, `Promotion Gate`.

Content that already exists:

- Semantic existence does not force physical materialization.
- Materialization modes already include full source history, full context history, full research population, selective event windows, on-demand replay, cache-only and experimental.
- State tables must declare coverage and lookback policy before promotion.

Content really new:

- A candidate `materialization_decision_record` that could operationalize this rule before builders start.

Risk of second source of truth:

- Medium if it invents modes not aligned with Market Representation Chapter 16.

Correct location:

- Keep the decision record in CRM or proposal template.
- Keep allowed modes in Market Representation Chapter 16.
- Persist final decision in dataset contract, manifest and status matrix.

### Chapter 5 - Physical Representations

Overlap classification: `complementary`

Authority documented before this book:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\README.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_target_contract_v0_1.md`.
- `C:\TSIS_Data\00_CTO_1\05_TABLES\README.md`.

Content that already exists:

- Dataset registry, contracts, manifests and policies govern physical outputs.
- Some important physical artifacts are manifests or overlays, not ordinary promoted tables, e.g. quote-guarded 1m repair manifest.

Content really new:

- A general physical-representation vocabulary that can cover tables, views, overlays, candidate datasets and manifest-backed representations.

Risk of second source of truth:

- Low if fields are added to registries/manifests instead of creating a new registry.

Correct location:

- Keep concept in CRM.
- Store actual physical identity in `dataset_registry`, `dataset_contracts`, manifests and status matrix.

### Chapter 6 - Materialization Strategies

Overlap classification: `partial_duplicate`

Authority documented before this book:

- Market Representation Chapter 16 materialization modes.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\master_intraday_bar_table_wider_scope_materialization_plan_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\microstructure_features_table_multi_window_materialization_plan_v0_1.md`.

Content that already exists:

- `master_intraday_bar_table` must not claim full universe without denominator manifest and validation.
- `microstructure_features_table` should expand through candidate windows, not blind full-universe microstructure.
- Candidate outputs must remain candidate until tests/evidence pass.

Content really new:

- A higher-level strategy selection checklist.

Risk of second source of truth:

- Medium if it duplicates table-specific plans.

Correct location:

- Merge into Chapter 4 as `Materialization Decision`.
- Table-specific execution stays in materialization plans and table creation process.

### Chapter 7 - Institutional Contracts

Overlap classification: `strong_duplicate` unless reduced to a crosswalk.

Authority documented before this book:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\canonical_schemas\outputs\*.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\contract_registry\dataset_contracts\*.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\dataset_registry\outputs\*.yaml`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\data_consumption_policies\*.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\validators\outputs\*.md`.

Content that already exists:

- Schema contracts, dataset contracts, consumption policies, registry entries and validators exist for the reviewed tables, including `instrument_master`, `expected_data_calendar`, `dataset_certification_matrix`, `event_windows_table`, `outcomes_table`, `master_intraday_bar_table`, `microstructure_features_table`, `market_state_table` and `event_state_table`.

Content really new:

- A contract-set crosswalk attached to representation review.

Risk of second source of truth:

- High if CRM defines contract requirements instead of referencing the contract stack.

Correct location:

- CRM can define a required crosswalk.
- Authority stays in `01_foundations`.

### Chapter 8 - Physical Realization

Overlap classification: `strong_duplicate`

Authority documented before this book:

- `C:\TSIS_Data\00_CTO_1\05_TABLES\TABLES_CREATION_process_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_builder_contract_v0_1.md`.
- Builders under `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts`.
- Tests under `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\tests\data_foundation_outputs`.

Content that already exists:

- Table creation, materialization, validation, manifests and builder responsibilities are already governed outside CRM.
- State builder contract has config requirements, source component registry, raw-to-consumption gate, manifest obligations, validators and acceptance criteria.

Content really new:

- A governance-to-engineering handoff concept.

Risk of second source of truth:

- High if implementation process is restated in CRM.

Correct location:

- Move detailed process to `TABLES_CREATION_process_v0_1` or table-specific contracts.
- CRM keeps only the handoff rule.

### Chapter 9 - Institutional Certification

Overlap classification: `partial_duplicate`

Authority documented before this book:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\data_foundation_outputs_status_matrix_v0_1.md`.
- `C:\TSIS_Data\VERSIONING_STANDARDS.md`.
- Validators and test-run evidence under `C:\TSIS_Data\tests\test_runs`.

Content that already exists:

- Status matrix distinguishes `validated_for_declared_scope`, `scoped_pilot`, `seed_state_sample`, `controlled_candidate_not_promoted`, `not_materialized`.
- Specific candidate evidence exists for microstructure, market_state, event_state, event_windows and outcomes.

Content really new:

- A compact certification record spanning architecture and engineering.

Risk of second source of truth:

- Medium if certification status lives both in CRM and status matrix.

Correct location:

- Certification status stays in status matrix and registries.
- CRM may provide checklist/template for missing evidence.

### Chapter 10 - Institutional Promotion

Overlap classification: `partial_duplicate`

Authority documented before this book:

- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, sections `Institutional Promotion Review`, `Promotion barrier`.
- Market Representation Chapter 18, sections `Promotion Path`, `Governance Review`.
- Table-specific promotion gates in materialization plans and state policies.

Content that already exists:

- Promotion requires reproducibility, naming, manifests, downstream compatibility, epistemological coherence and contracts.
- Candidate materialization is not promotion.

Content really new:

- A representation-scoped promotion record tying semantic authority to physical evidence.

Risk of second source of truth:

- Medium if CRM owns promotion status.

Correct location:

- Promotion rules remain in `VERSIONING_STANDARDS.md`, governance docs and table-specific contracts.
- CRM can create a promotion-record template.

### Chapter 11 - Representation Lifecycle

Overlap classification: `complementary`

Authority documented before this book:

- `C:\TSIS_Data\VERSIONING_STANDARDS.md`, sections `Semantic Versioning`, `Dataset and Output Versioning`, `Deprecation / Archive`.
- Market Representation Chapter 18 governance lifecycle.
- Dataset registry entries and manifests.

Content that already exists:

- Datasets and institutional artifacts have statuses, versioning and deprecation rules.

Content really new:

- A clear separation between canonical lifecycle and physical lifecycle.

Risk of second source of truth:

- Low if lifecycle fields are stored in registries/status matrices.

Correct location:

- Keep concept in CRM.
- Persist lifecycle in registry/status fields.

### Chapter 12 - Architectural Traceability

Overlap classification: `complementary`

Authority documented before this book:

- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_contract_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_daily_event_windows_controlled_v0_1.md`.
- `C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\module_contracts\outputs\state_raw_to_consumption_lineage_intraday_1m_quote_guarded_v0_1.md`.
- Dataset registry README authority-chain concepts.

Content that already exists:

- State components must show RAW -> consumption lineage, manifests, transforms, cutoff, quality gates and consumption permissions.

Content really new:

- A broader architecture-to-physical traceability record from epistemological chapter to physical manifest.

Risk of second source of truth:

- Low if it references existing lineage contracts and manifests.

Correct location:

- Keep in CRM as traceability requirement.
- Store operational traceability in registry/status/manifests and lineage contracts.

### Chapter 13 - Constitutional Principles

Overlap classification: `strong_duplicate`; possible `authority_conflict`.

Authority documented before this book:

- `C:\TSIS_Data\AGENTS.md`.
- `C:\TSIS_Data\PROJECT_RULES.md`.
- `C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md`.
- `C:\TSIS_Data\00_CTO_1\00_EPISTEMOLOGICAL_architecture\01_TSIS_REPRESENTATION_THEORY\22_Chapter_21_Constitutional_Principles_TSIS.md`.

Content that already exists:

- Representation before intelligence, temporal integrity, reproducibility, semantic stability, layer separation, governance, scientific neutrality and extension-over-replacement are already constitutional principles.

Content really new:

- CRM-specific summary of compatibility.

Risk of second source of truth:

- High if the chapter calls itself constitutional authority.

Correct location:

- Reduce to appendix or compatibility checklist.
- Root and epistemological constitutional documents remain authoritative.

## High-Risk Authority Boundaries

1. `Market Representation - Chapter 16 Materialization Policy` must remain the authority for materialization modes. CRM can record decisions, not redefine modes.
2. `Market Representation - Chapter 18 Representation Governance` must remain the authority for governance hierarchy, change classes and promotion path. CRM can require crosswalk evidence.
3. `Market Representation - Chapter 21 Constitutional Principles` must remain constitutional authority. CRM Chapter 13 can only be compatibility summary.
4. `TABLES_CREATION_process_v0_1` and table-specific module contracts must remain authority for physical execution.
5. `data_foundation_outputs_status_matrix_v0_1.md` must remain authority for current status and promotion/candidate distinctions.
6. Dataset contracts, schemas, registries, policies and validators in `01_foundations` must remain operational source of truth.

## Map Conclusion

The CRM book is useful if it becomes a missing governance bridge. It is unsafe if it becomes a second version of the epistemology book, the table creation process, the status matrix or the promotion standard.

