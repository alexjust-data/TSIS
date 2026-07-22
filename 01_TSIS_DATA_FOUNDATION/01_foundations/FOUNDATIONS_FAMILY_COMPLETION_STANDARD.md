# Foundations Family Completion Standard

## 1. Role

This document defines what it means for a data family to be **finished inside `01_foundations`**.

Finished here does **not** mean:

- clean data;
- production-ready data;
- authorized for `backtest_core`;
- authorized for ML, RL, live trading or execution simulation.

Finished here means:

```text
a human inspector can open 01_foundations, follow the family across every required foundation folder, understand the data structure, inspect evidence, understand the verdict, and reproduce or review the reasoning without hidden context.
```

This is the completion standard for family-level governance work.

## 2. Two Status Axes

Every family must be evaluated on two separate axes.

### Axis A: Data Quality Verdict

This axis answers:

```text
What did the audit conclude about the data?
```

Examples:

- `usable_for_declared_scope`
- `complete_scoped`
- `blocked_by_data_defect`
- `provisional`
- `not_assessed`

This axis can be negative. A blocked family can still have an excellent audit.

### Axis B: Foundations Completion Status

This axis answers:

```text
Is the family package inside 01_foundations complete enough for a human inspector?
```

Examples:

- `human_inspector_ready`
- `human_inspector_ready_scoped`
- `visual_casepack_required`
- `dossier_partial`
- `governance_pack_created_dossier_missing`
- `summary_report_created`
- `schema_only`
- `not_started`

This axis is independent from data quality.

Critical rule:

```text
A family can be blocked as data and still be human_inspector_ready.
A family can have a data_quality_report and still not be human_inspector_ready.
```

Additional rule:

```text
A family cannot be human_inspector_ready at the trades/quotes/daily/1m
standard if it lacks a visual inspector pack or an explicit documented visual
waiver.
```

## 3. Non-Negotiable Interpretation

The following are not equivalent:

| Artifact exists | Does it mean the family is finished? |
| --- | --- |
| schema exists | no |
| contract exists | no |
| registry exists | no |
| policy exists | no |
| validator notes exist | no |
| one readout exists | no |
| one quality report exists | no |
| data is blocked | no, this is a verdict, not a completion state |
| data is clean | no, evidence still must be inspectable |

The minimum finished state is a coherent family package across the foundation folders.

## 4. Required Foundation Surfaces

A family is not `human_inspector_ready` unless all applicable surfaces are present or explicitly waived with a reason.

Required surfaces:

1. `canonical_schemas/<family>/`
2. `contract_registry/dataset_contracts/`
3. `data_consumption_policies/`
4. `dataset_registry/<family>/`
5. `validators/<family>/`
6. `inspection_dossiers/<family>/`
7. `data_quality_report/families/`
8. `module_contracts/`, when transversal semantics are required
9. `README` / index updates
10. `CHANGELOG.md`
11. `visual_inspector_pack/` or an explicit family-level visual waiver

If any surface is missing, the family cannot be called complete. It can only be called partial, scoped, provisional or blocked.

## 5. Minimum Content By Surface

### `canonical_schemas/<family>/`

Must explain:

- logical unit;
- grain;
- keys;
- required fields;
- optional fields;
- accepted aliases;
- semantic types;
- sentinel or empty-file forms, if any;
- what cannot be inferred from schema alone.

### `contract_registry/dataset_contracts/`

Must explain:

- dataset identity;
- scope;
- what the dataset is not;
- source lineage;
- quality vocabulary;
- allowed and prohibited consumers;
- known limitations;
- versioning triggers.

If taxonomy or cut policy exists, it must be explicit and versioned.

### `data_consumption_policies/`

Must explain:

- which consumers are allowed;
- which consumers are restricted;
- which states require flags;
- which states are `research_only` or `forensic_only`;
- which price view or semantic view is required;
- which downstream uses remain prohibited.

### `dataset_registry/<family>/`

Must explain:

- physical roots;
- layout;
- version or logical identity;
- linked schema;
- linked contract;
- linked policy;
- linked validators;
- linked dossier;
- materialization or promotion state.

### `validators/<family>/`

Must explain:

- checks required;
- hard failures;
- warning/review flags;
- expected outputs;
- evidence left by the checks;
- limitations of the validators.

Validators cannot silently emit final business meaning that they do not prove.

### `inspection_dossiers/<family>/`

Must be the human inspection layer.

Minimum expected structure:

```text
inspection_dossiers/<family>/
  README.md
  build_<family>_inspection_pack.md or generation/provenance note
  <family>_inspection_readout_vX_Y.md
  evidence_assets/
    README.md or manifest
    population summaries
    schema observed vs expected evidence
    quality tables
    sample manifests
    case assets or equivalent technical evidence
  good_justification/ or equivalent positive-evidence section
  flagged_case_evidence_packs/ or equivalent review-evidence section
  bad_case_evidence_packs/ or equivalent defect-evidence section
  coverage_case_evidence_packs/ when coverage is material
  visual_inspector_pack/ or documented visual waiver
```

The folder names can differ when the family is not naturally `good/review/bad`, but the evidence roles cannot disappear.

Visual evidence is the default requirement, not an optional extra. The
benchmark families (`quotes`, `trades`, `daily`, `minute` and
`ohlcv_1m_split_normalized`) define the minimum level:

- population-level visuals before individual cases;
- stratified case visuals for good/review/bad or equivalent states;
- written interpretation for every visual or visual family;
- a manifest linking images to cases, metrics, status and consequence;
- an asset audit proving every referenced image exists.

If a family truly cannot produce meaningful image-based casepacks, it must
record an explicit waiver in:

```text
inspection_dossiers/<family>/visual_inspector_pack/visual_waiver_v0_1.md
```

That waiver must explain:

- why visual inspection would not add evidence beyond the tabular assets;
- which tabular assets replace each expected visual role;
- which auditor questions remain answerable without images;
- what future condition would revoke the waiver.

Without that waiver, equivalent tabular evidence is not enough to claim
`human_inspector_ready`.

Equivalent evidence can support a waiver, but it does not silently replace
images:

- tabular casepacks;
- file manifests;
- schema-drift tables;
- missingness tables;
- null/sentinel reports;
- outlier reports;
- coverage reports;
- example payload extracts;
- data-dictionary deltas;
- error manifests;
- or source reconciliation tables.

### `visual_inspector_pack/`

When not waived, every family must expose a visual inspection entry point:

```text
inspection_dossiers/<family>/visual_inspector_pack/
  README.md
  <family>_visual_inspector_pack_v0_1.md
  <family>_visual_case_manifest_v0_1.csv
  <family>_visual_asset_audit_v0_1.csv
  images/
    *.png
```

Minimum visual roles:

1. population map;
2. coverage map;
3. quality-state distribution;
4. good/pass examples;
5. flagged/review examples;
6. bad/blocking examples;
7. boundary or scope-limitation examples, when applicable.

Each visual or visual family must state:

- what it shows;
- what question it answers;
- what it does not answer;
- what downstream consequence follows.

### `data_quality_report/families/`

Must summarize:

- scope and role;
- physical roots;
- artifact map;
- file structure and technical profile;
- expected vs observed schema;
- population and coverage;
- cleanliness and interpretability;
- semantic quality;
- case evidence;
- consumer matrix;
- verdict;
- open debt.

The quality report is an entry point. It does not replace the dossier.

## 6. Human Inspector Ready Gate

To mark a family as `human_inspector_ready`, a reviewer must be able to answer:

- What files exist?
- What does each file contain?
- What schema was expected?
- What schema was observed?
- What nulls, empty files, sentinels or malformed values exist?
- What duplicates or non-unique keys exist?
- What outliers or impossible values exist?
- What coverage exists and what coverage is missing?
- What cases are good, flagged, bad or blocked?
- What evidence supports each case type?
- What can be consumed and what cannot?
- Which scripts, notebooks, manifests or summaries produced the evidence?
- What changed in the changelog?

If any answer requires hidden conversation context, the family is not complete.

## 7. Status Classes

Use these classes for `foundations_completion_status`.

| Status | Meaning |
| --- | --- |
| `human_inspector_ready` | Full foundation package exists, including visual inspector pack or explicit visual waiver, and the human inspector can review the family without hidden context. |
| `human_inspector_ready_scoped` | Complete for a declared limited scope, including visual inspector pack or explicit visual waiver for that scope. The limitation is explicit and evidence-backed. |
| `visual_casepack_required` | Governance, readout and tabular evidence may exist, but the family still lacks the required visual inspector pack or waiver. It cannot be called complete. |
| `dossier_partial` | Some dossier/readout/evidence exists, but one or more human-inspection gates are missing. |
| `governance_pack_created_dossier_missing` | Schema/contract/policy/registry/validators/report exist, but the dossier is not at the required evidence level. |
| `summary_report_created` | A report or readout exists, but the foundation package is not complete. |
| `schema_only` | Schema-level definition exists without full governance or inspection evidence. |
| `not_started` | No usable foundation package exists. |

## 8. Quality Verdict Classes

Use these classes for `data_quality_verdict`.

| Verdict | Meaning |
| --- | --- |
| `usable_for_declared_scope` | The data is acceptable for the consumers and scope declared by its policy. |
| `complete_scoped` | The data is acceptable only for a narrower declared scope. |
| `blocked_by_data_defect` | The audit found defects that block institutional consumption for the intended role. |
| `provisional` | Evidence exists, but the verdict is not final. |
| `not_assessed` | No sufficient data-quality verdict exists. |

## 9. Required Matrix Columns

Any family-level matrix must separate at least:

```text
family
physical_root
role
data_quality_verdict
foundations_completion_status
visual_inspection_status
main_reading
missing_completion_gates_or_next_action
```

Do not use a single status column for both quality and completion.

## 10. Example Of A Non-Complete Family

A family folder like:

```text
inspection_dossiers/<family>/
  README.md
  <family>_inspection_readout_v0_1.md
```

is not `human_inspector_ready` by itself.

Even if the readout says the data is blocked, clean, scoped or usable, the family still lacks the inspection package expected by this standard unless it also contains or links equivalent evidence assets, manifests, case examples and technical profiles.

A family folder with strong CSV/JSON assets but no visual inspector pack and no
visual waiver is also not `human_inspector_ready`. Its correct status is:

```text
visual_casepack_required
```

## 11. Relationship To Existing Standards

This document complements:

- `DATA_AUDIT_QUALITY_STANDARD.md`
- `DATA_AUDIT_TOPIC_NAVIGATION.md`
- `module_contracts/inspection_dossier_model.md`
- `module_contracts/bad_evidence_and_rehabilitation.md`
- `data_quality_report/README.md`

`DATA_AUDIT_QUALITY_STANDARD.md` defines how deep the audit must be.

This document defines when the whole family package across `01_foundations` can be called finished for human inspection.

## 12. Final Rule

Do not call a family finished because the conclusion is known.

Call it finished only when the conclusion, evidence, structure, limitations,
visual or waived inspection layer and downstream consequences are all
inspectable from `01_foundations` without hidden state.
