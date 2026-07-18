# CRM_APPLICABILITY_MATRIX_v0_1

Status: `candidate_applicability_matrix_v0_1`

Date: `2026-07-15`

Scope: `01_REPRESENTATION_MATERIALIZATION_REVIEW / candidate_governance`

This document defines where the Canonical Representation Materialization
(CRM) governance mechanism applies, and with which intensity.

It is not an institutional promotion record.
It does not authorize physical realization, certification, promotion or
downstream consumption.

------------------------------------------------------------------------

## Purpose

The purpose of this matrix is to prevent CRM governance from being applied
too broadly.

The CRM framework should not force every table, builder, manifest, cache or
intermediate dataset through the full governance sequence.

The central question is:

```text
What kind of object is being governed?
```

The governance intensity depends on the answer.

------------------------------------------------------------------------

## Governing Principle

The CRM framework does not govern physical files by default.

It governs proposed institutional representations and governed artifacts.

```text
object class
    ↓
required governance intensity
    ↓
authorized next artifact
```

The full CRM path is reserved for Canonical Core Representations.

------------------------------------------------------------------------

## Applicability Levels

| Level | Object class | Examples | Governance intensity |
| --- | --- | --- | --- |
| A | Canonical Core Representations | `Market State`, `Event State`, `Outcome`, `Decision` if it exists | Full CRM governance |
| B | Canonical Supporting Representations | `Feature`, `Market Primitive`, `Microstructure Primitive` | Partial CRM governance |
| C | Enabling Institutional Artifacts | `instrument_master`, `expected_data_calendar`, `dataset_certification_matrix` | Institutional artifact governance |
| D | Engineering Artifacts | builders, validators, manifests, temporary outputs, caches, intermediate tables | Table Creation Process / engineering governance |

------------------------------------------------------------------------

## Level A - Canonical Core Representations

Level A objects are the nuclear representations of TSIS.

They define reusable, canonical market knowledge that may feed research,
backtests, ML, RL, execution analysis, audits or downstream decision systems.

Required governance:

```text
Representation Justification Record
    ↓
Formal Review
    ↓
Materialization Decision Record
    ↓
Canonical-to-Physical Mapping
    ↓
Architectural Traceability
```

Current Level A candidates:

| Object | Current interpretation | Current status |
| --- | --- | --- |
| `Market State` | Canonical Core Representation | RJR exists; MDR v1 exists as draft/not_reviewed |
| `Event State` | Canonical Core Representation | conceptual justification ready; RJR should be created next |
| `Outcome` | Canonical Core Representation | not yet reviewed under CRM |
| `Decision` | Conditional Canonical Core Representation | only if TSIS formally defines it as a governed representation |

------------------------------------------------------------------------

## Level B - Canonical Supporting Representations

Level B objects are canonical, but usually support a higher-level
representation rather than standing alone as the main institutional state.

Examples:

```text
Feature
Market Primitive
Microstructure Primitive
Feature Family
```

Default governance:

```text
scope definition
    ↓
eligibility / observability rules
    ↓
registry or contract entry
    ↓
mapping only when independently materialized
```

A full MDR is not required by default.

A full MDR may become required if the supporting representation becomes an
independent institutional physical representation with broad downstream use.

------------------------------------------------------------------------

## Level C - Enabling Institutional Artifacts

Level C objects are not Canonical Market Representations.

They are institutional infrastructure required for identity, calendar,
certification, governance or reproducibility.

Examples:

```text
instrument_master
expected_data_calendar
dataset_certification_matrix
```

Default governance:

```text
Institutional Artifact Justification
    ↓
Simplified Materialization Decision
    ↓
Mapping or registry entry when applicable
    ↓
Traceability / status evidence
```

They should not use the classic Representation Justification Record unless
they truly represent market state, event state, outcome or decision semantics.

------------------------------------------------------------------------

## Level D - Engineering Artifacts

Level D objects are implementation artifacts.

Examples:

```text
builders
validators
manifests
temporary datasets
intermediate tables
overlays
caches
runtime outputs
```

Default governance:

```text
Table Creation Process
code review
schema or manifest contract when applicable
validator evidence when applicable
```

They do not pass through RJR or MDR by default.

------------------------------------------------------------------------

## Applicability Matrix

| Artifact or class | Level | RJR | MDR | Mapping | Traceability | Default route |
| --- | --- | --- | --- | --- | --- | --- |
| `Market State` | A | required | required | required | required | Full CRM |
| `Event State` | A | required | required | required | required | Full CRM |
| `Outcome` | A | required | required | required | required | Full CRM |
| `Decision` | A, conditional | required if adopted | required if adopted | required if adopted | required if adopted | Full CRM if formally defined |
| `Feature` | B | simplified or registry-backed | not default | when independently materialized | required if reused downstream | Partial CRM |
| `Market Primitive` | B | simplified or registry-backed | not default | when independently materialized | required if reused downstream | Partial CRM |
| `Microstructure Primitive` | B | simplified or registry-backed | not default | when independently materialized | required if reused downstream | Partial CRM |
| `instrument_master` | C | not classic RJR | simplified | required if physical contract exists | required | Institutional Artifact Governance |
| `expected_data_calendar` | C | not classic RJR | simplified | required if physical contract exists | required | Institutional Artifact Governance |
| `dataset_certification_matrix` | C | not classic RJR | simplified | required if physical contract exists | required | Institutional Artifact Governance |
| `master_intraday_bar_table` | D or B-derived physical table | not default | not default | engineering/materialization plan | required by table process | Table Creation Process |
| `microstructure_features_table` | B-derived physical table | not default full RJR | not default full MDR | required as feature materialization | required | Partial CRM + Table Creation Process |
| intermediate builder outputs | D | no | no | no | run/manifest traceability only | Engineering governance |
| caches / overlays / temporary outputs | D | no | no | no | runtime or manifest traceability only | Engineering governance |

------------------------------------------------------------------------

## Decision Rule

Use this rule before creating a new governance artifact:

```text
If the object defines a nuclear market representation:
    Level A → Full CRM

If the object defines canonical inputs or primitives supporting core states:
    Level B → Partial CRM

If the object enables institutional identity, calendar, certification or governance:
    Level C → Institutional Artifact Governance

If the object is implementation, runtime, intermediate or cache infrastructure:
    Level D → Table Creation Process / engineering governance
```

------------------------------------------------------------------------

## Governance Validation Roadmap

Current recommended order:

```text
Market State
    ↓
Event State
    ↓
Outcome
    ↓
Decision, only if formally adopted
    ↓
Framework review
    ↓
Pilot with Enabling Institutional Artifacts
    ↓
Candidate governance freeze / revision
```

Interpretation:

```text
Market State validates the snapshot/state side.
Event State validates the event-relative state side.
Outcome validates the separated future-result side.
Decision is conditional and should not be forced if TSIS does not define it
as an independent canonical representation.
```

------------------------------------------------------------------------

## Current Next Step

The next governance action should be:

```text
rjr_event_state_v1.md
```

It should be derived from:

```text
00_REVISION/_00_CTO/01_questions.md
```

and governed by:

```text
representation_justification_contract_v0_8.md
```

It should not authorize materialization.

Materialization planning can only be considered later through:

```text
mdr_event_state_v1.md
```

------------------------------------------------------------------------

## Non-Authorization Statement

This matrix does not:

- promote any representation to institutional status;
- approve any physical table;
- approve any schema;
- approve any builder;
- approve any validator;
- replace existing dataset contracts;
- replace the Table Creation Process;
- authorize downstream consumption.

It only defines which governance path should be used for each class of
object.