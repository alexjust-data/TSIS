# 00_CTO_APPLIED_ARCHITECTURE Local Rules

Status: `local_rules_v0_1`
Date: `2026-07-16`

These rules govern work inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
```

They refine root TSIS rules. They do not replace them.

---

## 1. Role

This folder is the applied architecture layer for TSIS.

It explains how high-level epistemology connects to physical table work, data
audits, experiments and strategy research.

It is a working map and architectural bridge.

It is not:

```text
the data root
the builder root
the validator root
the official dataset registry
the final source of truth for promoted tables
```

---

## 2. Authority

The authority hierarchy is:

```text
1. Root TSIS governance
2. Operational module governance
3. 01_foundations contracts, schemas, registries, policies and validators
4. manifests, status matrices and test evidence
5. this applied architecture folder
```

If this folder says a table is ready but the status matrix, validator, manifest
or dataset contract says otherwise, the operational evidence wins.

---

## 3. Knowledge State

Every artifact in this folder must be read as one of:

```text
working_map
architectural_reading
candidate_governance
operational_guide
historical_record
secondary_summary
```

Only artifacts explicitly promoted through operational contracts or status
matrices can govern production work.

---

## 4. No Second Source Of Truth

This folder must not duplicate official operational authority.

It may summarize or explain schemas, contracts, registries, validators, builders,
manifests and status matrices.

The active source of truth remains in the operational module, especially:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
```

---

## 5. Graphify Rule

Graphify is semantic navigation only.

It can answer:

```text
what is related to what?
where is this concept documented?
which folders are connected?
```

It cannot prove:

```text
dataset promotion
validator success
physical materialization
full-universe completeness
```

Those claims require manifests, validators, status matrices or physical
inspection.

---

## 6. Table Work Rule

All table work in `03_TABLES_feature_engineering` must obey:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\LOCAL_RULES.md
```

The six-question gate is mandatory before defining or changing attributes.

---

## 7. Changelog Rule

Update:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\CHANGELOG.md
```

when there is a semantic, structural or governance-relevant change in this
folder.

Examples:

```text
folder rename
new local governance
Graphify build/update
change in 013-018 continuation process
new table operational reading
change in source-of-truth interpretation
```

Do not log trivial typo fixes.

---

## 8. Final Rule

This folder exists to help future humans and agents understand TSIS faster
without inventing hidden assumptions.

If a statement cannot be traced to a document, contract, manifest, validator,
test or physical artifact, it must be marked as interpretation, not fact.

