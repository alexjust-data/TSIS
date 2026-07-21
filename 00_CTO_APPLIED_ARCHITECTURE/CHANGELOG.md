# 00_CTO_APPLIED_ARCHITECTURE Changelog

This changelog records semantic, structural and governance-relevant changes in:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
```

It does not replace:

```text
C:\TSIS_Data\CHANGELOG.md
C:\TSIS_Data\00_CTO\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\CHANGELOG.md
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\01_foundations\CHANGELOG.md
```

Use this changelog for changes to the applied architecture map, local rules,
Graphify map, table reading surface and continuation guides.

Do not use it for ordinary Git noise or minor typos.

---

## 2026-07-21 | 03_TABLES_feature_engineering | TSIS Market Ontology v1 review added

- Added `03_INFORMATION_OBJECTS/TSIS_MARKET_ONTOLOGY_V1_REVIEW.md` as the Cross-Object Ontology Review for the 12 formally admitted Information Objects.
- Decision: cross-object review `passes_with_restrictions`; recommendation is to proceed to a separate `TSIS Market Ontology v1` freeze artifact.
- Updated `03_TABLES_feature_engineering/AGENT.md` so the next handoff step is ontology freeze, not another cross-object review.
- Boundary unchanged: no README, methodology, Operational Mapping, builder, schema, State consumption, physical variable or materialization was authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | remaining formal admissions completed

- Added Formal Admissions for the remaining TSIS Market Ontology Phase Information Objects: `Volatility / Range State`, `Liquidity`, `Market Microstructure State`, `Order Flow Pressure`, `News / Catalyst Context`, `Fundamental Context`, `Short-Side Context`, `Broad Market Context` and `Halt Context`.
- Result: all 12 main Information Objects with Object Admission Reviews now have Formal Admission artifacts.
- Updated `03_TABLES_feature_engineering/AGENT.md` so the handoff points to Cross-Object Ontology Review after completing all 12 Formal Admissions.
- Boundary unchanged: no README, methodology, Operational Mapping, builder, schema, State consumption, physical variable or materialization was authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Price Location formal admission added

- Added `Price Location / Structure` Formal Admission under `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/`.
- Decision: scientific identity accepted; operational readiness accepted with restrictions.
- Boundary unchanged: no Operational Mapping expansion, builder change, schema change, State consumption, physical variable or materialization was authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | local agent handoff prompt added

- Added `03_TABLES_feature_engineering/AGENT.md` as a local continuation prompt for the TSIS Market Ontology Phase.
- Documented required reading order, current Formal Admission status, remaining admission queue, cross-object review path and Phase B deferral.
- Boundary unchanged: no methodology layer, README, Operational Mapping, builder, schema, State consumption or physical materialization was changed.

## 2026-07-21 | 03_TABLES_feature_engineering | Price Movement formal admission added

- Added `Price Movement` Formal Admission under `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/`.
- Decision: scientific identity accepted; operational readiness accepted with restrictions.
- Boundary unchanged: no Operational Mapping expansion, builder change, schema change, State consumption, physical variable or materialization was authorized.

## 2026-07-21 | 03_TABLES_feature_engineering | Phase A/B README boundary corrected

- Corrected `03_INFORMATION_OBJECTS/README.md` so the active work is Formal Admission, Cross-Object Ontology Review and `TSIS Market Ontology v1` freeze, not vertical validation.
- Added the active Phase A / deferred Phase B boundary to the feature-engineering README before the lifecycle steps.
- Boundary unchanged: no schema, builder, dataset, State variable or physical materialization was authorized.

## 2026-07-20 | 03_TABLES_feature_engineering | Ontology Phase gate activated

- Activated `TSIS Market Ontology Phase` as the current scientific governance phase.
- Classified the `Trading Activity` vertical as a pilot/proof-of-process, not Phase B operational authority.
- Deferred new Operational Mapping, Builder Validation, Market State Integration and production builder development until all main Information Objects pass Formal Admission and cross-object ontology review.
- Boundary unchanged: no schema, builder, dataset, State variable or physical materialization was authorized.

## 2026-07-20 | 03_TABLES_feature_engineering | Trading Activity formal admission vertical added

- Added the first vertical post-review flow for `Trading Activity`:
  - formal admission under `03_INFORMATION_OBJECTS/ACCEPTED_WITH_RESTRICTIONS/`;
  - operational mapping under `04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/`;
  - builder validation design under `05_STATE_BUILDER_VALIDATION/`;
  - Market State integration design under `06_MARKET_STATE_INTEGRATION/`.
- Decision: `Trading Activity` is accepted with restrictions as an Information Object; State consumption, schema changes, builder changes and physical materialization remain unauthorized.
- Updated local README/index surfaces to point to the new vertical flow.
- Boundary unchanged: applied architecture only; operational authority remains in `01_foundations` contracts, schemas, validators, manifests and status matrices.


## 2026-07-20 | event_state | consumption legality boundary added

- Clarified that Event State needs independent `state_role` and `consumption_legality` classifications.
- `post_event`/`post_event_review` may be valid for research but not legal predictive X for an event-time decision.
- Boundary unchanged: no dataset promotion or State consumption authorization changed.


## 2026-07-20 | 03_TABLES_feature_engineering | Market State profile boundary added

- Clarified the anti mega-table rule for canonical Market State.
- Market State canonicality is now documented as shared semantics and identity with compatible physical profiles, not a universal all-column table.
- Boundary unchanged: no operational schema, builder, dataset or promotion status changed.


## 2026-07-20 | 03_TABLES_feature_engineering | taxonomy axes separated

- Clarified that Information Object families are semantic only.
- Added the four-axis taxonomy rule: `information_object_family`, `source_domain`, `temporal_resolution`, and `institutional_role`.
- Boundary unchanged: no Information Object admission, table promotion or State consumption authorization changed.

## 2026-07-20 | 03_TABLES_feature_engineering | Information Object definition clarified

- Clarified that an Information Object is not itself a Representation Model or physical representation.
- Defined Information Object as the semantic unit TSIS decides to preserve about observable phenomena, independent of model and implementation.
- Boundary unchanged: no Information Object admission, table promotion or State consumption authorization changed.

## 2026-07-20 | 03_TABLES_feature_engineering | Object Discovery vs Admission boundary formalized

- Updated the feature-engineering/table-review process to distinguish bottom-up `Object Discovery Process` from top-down `Object Admission Process`.
- Clarified that tables and variables can reveal candidate Information Objects, but admission defines scientific meaning and State eligibility.
- Boundary unchanged: no table, dataset or Information Object was promoted.

## 2026-07-20 | 03_TABLES_feature_engineering | canonical 013-018 DAG fixed

- Updated `03_TABLES_feature_engineering/02_TABLE_REPRESENTATION_REVIEW/LOCAL_RULES.md` to remove the obsolete linear 013-018 dependency chain.
- Aligned local table-review rules with the README architecture: `014` and `015` are sibling representation surfaces, `018` is optional scanner/candidate context, and `016` consumes governed context/observables under contract.
- Added dependency-class language to distinguish semantic, physical source, eligibility and materialization-selection dependencies.

## 2026-07-20 | applied architecture | global representation tree added to README

- Added `Arquitectura Global De Representacion` to `README.md`.
- The new section maps the chain from `Mercado` to `Market State / Event State` and adds one guiding question per layer.
- Clarified that derivable capability, variable existence and table materialization do not by themselves authorize inclusion in State.
## 2026-07-20 | applied architecture | root README refreshed for current layer map

- Updated `README.md` to reflect the current top-level folder structure:
  - `03_TABLES_feature_engineering`
  - `04_DATA_Raw_audit`
  - `05_DATA_derivable`
  - `06_DATA_Live_Source`
  - `07_NEW_STRATEGIES_by_Experiments`
  - `08_EXPERIMENTS`
  - `09_STRATEGIES_know`
- Clarified the chain from epistemology to governance, RAW audit, derivable capabilities, table feature engineering, Market State/Event State, experiments and strategy knowledge.
- Added explicit boundaries for `05_DATA_derivable`: calculation capability only; no semantic admission or Market State authorization.
- Reaffirmed that applied architecture is a secondary map and does not override contracts, schemas, registries, validators, manifests or status matrices.

## 2026-07-20 | 05_DATA_derivable | reading-order filename prefixes

- Renamed active derivable-layer documents to make reading order explicit:
  - `00_DATA_DERIVABLE_CATALOG_BY_RAW_SOURCE_v0_1.md`
  - `01_DERIVABLE_CAPABILITY_REGISTER_v0_1.md`
  - `02_DERIVABLE_CAPABILITY_STATUS_MATRIX_v0_1.md`
- Updated local references in `05_DATA_derivable/README.md` and the capability status matrix.
- Boundary unchanged: this is a naming/readability change only; no derivable capability status or operational authority changed.

## 2026-07-20 | 05_DATA_derivable | atomic derivable capability register

- Refactored `DERIVABLE_CAPABILITY_REGISTER_v0_1.md` so each row represents one canonical derivable capability.
- Split grouped rows such as `daily__return_range_metrics`, `daily__adjustable_Nd_families`, `intraday__shape_pace_W`, trade size distributions, trade quality ratios and quote spread groups into atomic capability rows.
- Added explicit `variant_required` and `required_variant_fields` columns so parameterized capabilities can stay compact without mixing different capabilities.
- Updated `DERIVABLE_CAPABILITY_STATUS_MATRIX_v0_1.md` to summarize the atomic register and its status counts.
- Updated `05_DATA_derivable/README.md` with the atomic register rule.
- Boundary unchanged: this layer records legal/reproducible calculation capacity only; semantic family assignment and Information Object admission remain downstream.
## 2026-07-20 | 05_DATA_derivable | compact derivable layer bootstrap

- Added `05_DATA_derivable/README.md` to define the derivable layer as technical calculation capacity, not semantic admission.
- Added `05_DATA_derivable/DERIVABLE_CAPABILITY_REGISTER_v0_1.md` as a compact register of derivation capabilities by source.
- Added `05_DATA_derivable/DERIVABLE_CAPABILITY_STATUS_MATRIX_v0_1.md` as a compact state matrix for existing, formula-defined, variant-required, candidate, blocked and prohibited derivation capabilities.
- Added `05_DATA_derivable/99_archive/` for future superseded derivable-layer documents.
- Boundary: this layer answers what can be calculated legally from RAW/governed sources; semantic family assignment and Information Object admission remain in `03_TABLES_feature_engineering`.

## 2026-07-20 | 03_TABLES_feature_engineering | table representation review handoff package 000-018

- Added structured external-agent handoff package for `02_TABLE_REPRESENTATION_REVIEW`:

```text
03_TABLES_feature_engineering/02_TABLE_REPRESENTATION_REVIEW/TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720/
03_TABLES_feature_engineering/02_TABLE_REPRESENTATION_REVIEW/TABLE_REPRESENTATION_REVIEW_HANDOFF_000_018_v0_1_20260720.zip
```

- Purpose: package table-level variable/component documentation and Spanish representation audits for tables `000-018`.
- Boundary: secondary applied-architecture handoff only; operational authority remains in contracts, schemas, registries, validators, manifests and status matrices.

## 2026-07-20 | 04_DATA_Raw_audit | observable RAW parquet content handoff package

- Renamed RAW audit parquet content sample documents from `PARQUET_CONTENT_SAMPLE.md` to source-specific names, for example `PARQUET_CONTENT_TRADES.md` and `PARQUET_CONTENT_QUOTES.md`.
- Added flat external-agent handoff folder:

```text
04_DATA_Raw_audit/OBSERVABLE_RAW_PARQUET_CONTENT_INVENTORY_v0_1_20260720/
```

- Added compressed package:

```text
04_DATA_Raw_audit/OBSERVABLE_RAW_PARQUET_CONTENT_INVENTORY_v0_1_20260720.zip
```

- Purpose: provide a clean inventory of observable RAW parquet columns by documented source/family.
- Boundary: sample-content inventory only; no dataset certification, schema promotion, consumption authorization or physical data claim changed.

## 2026-07-20 | 05_DATA_derivable | raw-source derivable information catalog

- Added `05_DATA_derivable/DATA_DERIVABLE_CATALOG_BY_RAW_SOURCE_v0_1.md`.
- Purpose: consolidate, by RAW/governed source, the observable measures TSIS can derive before Information Object admission.
- Sources summarized: `raw_data_authority_and_derivation_map.md`, `family_status_matrix_v0_1.md`, `state_observable_eligibility_contract_v0_1.md`, `state_derived_observables_formula_contract_v0_1.md`, schemas, policies, lineage contracts and RAW audit folders.
- Boundary: secondary applied-architecture summary only; operational authority remains in `01_foundations` contracts, schemas, registries, validators, manifests and status matrices.

## 2026-07-17 | 03_TABLES_feature_engineering | information object model alignment

- Refactored the market representation family catalog so it aligns with `00_FEATURE_ADMISION_PROCESS.md`.
- The catalog now maps families to Information Objects, variables, physical tables, consumers and coverage status.


## 2026-07-17 | applied architecture | folder numbering normalized

- Reordered top-level applied architecture folders so `03_TABLES_feature_engineering` sits immediately after `02_MATERIALIZATION_GOVERNANCE_REVIEW`.
- Renamed:

```text
03_DATA_Raw_audit    -> 04_DATA_Raw_audit
04_DATA_Live_Source  -> 05_DATA_Live_Source
05_STRATEGIES_know   -> 06_STRATEGIES_know
```

- Updated internal references from old `06_TABLES` / `06_TABLES_feature_engineering` paths to `03_TABLES_feature_engineering`.
- Preserved the distinct duplicate file found under the transient `06_TABLES_feature_engineering` folder as:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\00_FEATURE_ADMISION_PROCESS_duplicate_preserved_20260717.md.md
```

- Removed the now-empty duplicate `06_TABLES_feature_engineering` folder.


## 2026-07-16 | 03_TABLES_feature_engineering | consolidated family attribute index

- Added `03_TABLES_feature_engineering/MARKET_REPRESENTATION_ATTRIBUTES_BY_FAMILY_ES.md`.
- It maps market representation families to known attributes from `000-012` and pending responsibilities for `013-018`.


## 2026-07-16 | 03_TABLES_feature_engineering | ES block format for table readings

- Reformatted Spanish table representation readings `000` through `012` into block-based answers with explicit line breaks.
- Purpose: make family, hypothesis, variables and consumers readable at a glance.


## 2026-07-16 | 03_TABLES_feature_engineering | concise spanish representation readings

- Rewrote Spanish per-table audits `000` through `012` into short family-based representation readings.
- Purpose: reduce documentation noise and focus variable admission on phenomenon, hypothesis, minimum variables and consumers.


## 2026-07-16 | 03_TABLES_feature_engineering | spanish audit copies

- Added Spanish copies of the feature-engineering guardrail, audit template and per-table audits `000` through `012`.
- Boundary: originals were preserved; no dataset status or promotion changed.


## 2026-07-16 | 03_TABLES_feature_engineering | 000-012 representation audits

- Generated per-table representation audits for `000` through `012` under `03_TABLES_feature_engineering`.
- Purpose: document what each table represents, which variable families it owns, why those variables deserve to exist, and how they contribute to Market State / Event State / downstream research.
- Boundary: these are applied architecture audits, not dataset promotions.


## 2026-07-16 | 03_TABLES_feature_engineering | market representation guardrails

- Added `03_TABLES_feature_engineering/TABLES_REPRESENTATION_OF_MARKET.md`.
- Added `03_TABLES_feature_engineering/TABLE_REPRESENTATION_AUDIT_TEMPLATE.md`.
- Updated local README and LOCAL_RULES to make variable selection depend on market representation family, scientific hypothesis, downstream consumer and evidence.
- Boundary: this is an applied architecture audit surface, not an operational source of truth.

## 2026-07-16 | 013 | quote-guarded v0_2 controlled consumption recorded

- Updated `03_TABLES_feature_engineering/013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md` to `operational_reading_v0_9`.
- Recorded that `ohlcv_1m_quote_guarded_full_universe_v0_2_candidate` passed validation and supersedes the v0.1 failed physical tree for controlled downstream work.
- Linked the new foundations contract, policy and registry entry.
- Boundary preserved: controlled downstream input only; not unrestricted institutional promotion and not raw mutation.

## 2026-07-16 | local governance | local agent/rules/changelog scaffold

- Added local `AGENTS.md` to define the entry point for agents working in
  `00_CTO_APPLIED_ARCHITECTURE`.
- Added local `LOCAL_RULES.md` to clarify that this folder is applied
  architecture and not operational source of truth.
- Added this `CHANGELOG.md`.
- Added `03_TABLES_feature_engineering/LOCAL_RULES.md` and `03_TABLES_feature_engineering/CHANGELOG.md` for table work
  governance.
- Established the mandatory six-question gate for future table work.

## 2026-07-16 | 013 | quote-guarded operational reading verified

- Created/updated `03_TABLES_feature_engineering/013_ohlcv_1m_quote_guarded/013_ohlcv_1m_quote_guarded_operational_reading.md`.
- Correct reading fixed:

```text
013 = raw ohlcv_1m + repair_manifest_lt1b_v0_1.parquet overlay
```

- Verified promoted/PASS manifest locally under:

```text
G:\TSIS\data\data_foundation_outputs\ohlcv_1m_quote_guarded\repair_manifest_lt1b_v0_1.parquet
```

- Focused quote-guarded tests executed:

```text
7 passed in 2.81s
```

- Important limitation preserved: `013` is not an official full-universe
  physical replacement tree.

## 2026-07-16 | 013 | physical full-universe failure correction

- Corrected the operational reading of `013_ohlcv_1m_quote_guarded` to separate
  the promoted/PASS LT1B repair overlay from the physical full-universe
  candidate tree.
- Confirmed that `ohlcv_1m_quote_guarded_full_universe_v0_1` remains
  `candidate_not_official` with `full_universe_claim=false`.
- Recorded unresolved `complete_with_failures` summaries for 2015..2020:

```text
2015 failed_tickers = 548
2016 failed_tickers = 571
2017 failed_tickers = 596
2018 failed_tickers = 758
2019 failed_tickers = 744
2020 failed_tickers = 701
```

- Current next action: controlled rematerialization/reconciliation of failed
  2015..2020 ticker-year cases before any clean full-universe claim.


- Generated operational failure manifest: `013_ohlcv_1m_quote_guarded/013_failed_tickers_2015_2020_v0_1.csv` with 3,918 failed ticker-year rows for controlled rematerialization.

## 2026-07-16 | 013 | failed-rerun launcher prepared and smoke passed

- Prepared non-destructive delta rerun root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate
```

- Generated year task plans for 3,918 failed ticker-year cases across 2015..2020.
- Rewrote task-plan raw input paths from `E:\TSIS\data\ohlcv_1m` to `G:\TSIS\data\ohlcv_1m` for this machine.
- Created governed launcher and monitor:

```text
run_full_rerun_2015_2020.ps1
monitor_full_rerun_2015_2020.ps1
```

- Executed short smoke test on separate smoke root:

```text
completed_tickers = 3
failed_tickers = 0
rows_written = 102,678
repairs_applied = 6
```

- Full rerun not launched by agent because `LONG_RUNNING_OPERATIONS_CONTRACT.md` requires human-visible launch command and monitor before long materialization runs.

## 2026-07-16 | 013 | failed 2015-2020 delta rerun completed

- Completed the controlled delta rerun for previously failed 2015..2020 physical candidate cases.
- Launcher final status:

```text
final_status = complete
exit_code = 0
completed_years = 6/6
```

- Year summaries verified:

```text
2015 complete failed_tickers=0 rows=21,995,617 repairs=627,338
2016 complete failed_tickers=0 rows=20,924,494 repairs=535,880
2017 complete failed_tickers=0 rows=22,619,373 repairs=711,769
2018 complete failed_tickers=0 rows=28,141,678 repairs=1,378,332
2019 complete failed_tickers=0 rows=27,102,457 repairs=1,021,067
2020 complete failed_tickers=0 rows=29,686,897 repairs=1,412,098
```

- Aggregate delta output:

```text
rows_written = 150,470,516
repairs_applied = 5,686,484
failed_tickers = 0
```

- Boundary preserved: this creates a parallel candidate delta root and does not by itself promote `013` or mutate the original `v0_1` tree.
- Next gate: reconcile original `v0_1` plus delta candidate, validate partitions/rows/schema/repair counts, then decide merge/promote path.

## 2026-07-16 | 013 | reconciliation PASS before technical merge

- Added reusable reconciliation script:

```text
C:\TSIS_Data\01_TSIS_backtest_SmallCaps\scripts\data_foundation\ohlcv_1m_quote_guarded_full_universe\reconcile_ohlcv_1m_qg_failed_delta_v0_1.py
```

- Accepted reconciliation run:

```text
run_id = qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
status = PASS
errors = 0
warnings = 0
expected_unique_pairs = 3,918
committed_pairs = 3,918
output_file_missing = 0
schema_checked_files = 600
schema_mismatches = 0
```

- Evidence root:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_failed_2015_2020_rerun_v0_1_candidate\_reconciliation_runs\qg_1m_failed_2015_2020_reconciliation_v0_1_20260716T094317Z
```

- Decision boundary: reconciliation PASS authorizes preparing a technical `v0_2_candidate` merge; it does not authorize institutional promotion.

## 2026-07-16 | 013 | technical merge candidate v0_2 completed

- Created physical technical merge candidate:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Merge run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z
status = complete
mode = hardlink
errors = 0
original_files_seen = 1,272,004
original_files_linked = 1,228,331
original_files_skipped_expected_delta_pair = 43,673
delta_files_seen = 43,673
delta_files_linked = 43,673
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_build_runs\qg_1m_full_universe_v0_2_candidate_merge_20260716T100000Z\final_manifest_merge.json
```

- Boundary: this completes a technical candidate merge only. It does not promote the dataset. Next gate is validation of `v0_2_candidate`.

## 2026-07-16 | 013 | v0_2 candidate validation PASS

- Validated merged candidate tree:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate
```

- Validation run:

```text
run_id = qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z
status = PASS
errors = 0
warnings = 0
candidate_files_seen = 1,272,004
candidate_files_from_original = 1,228,331
candidate_files_from_delta = 43,673
candidate_files_bad_source = 0
source_missing = 0
expected_delta_pairs_observed = 3,918
schema_checked = 600
schema_mismatches = 0
```

- Evidence:

```text
C:\TSIS_Data\data\data_foundation_outputs\ohlcv_1m_quote_guarded_full_universe_v0_2_candidate\_validation_runs\qg_1m_full_universe_v0_2_candidate_validation_20260716T102500Z\final_manifest_validation.json
```

- Boundary: `v0_2_candidate` is now a validated technical candidate tree and is eligible for promotion review. It is not yet promoted.
