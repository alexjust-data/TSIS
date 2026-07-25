# 00_CTO_APPLIED_ARCHITECTURE Agents

Status: `local_agent_contract_v0_1`
Date: `2026-07-16`

This file is the local entry point for agents working inside:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE
```

It refines, but does not replace:

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
```

If this document conflicts with root governance, root governance wins.

---

## 1. Role Of This Folder

`00_CTO_APPLIED_ARCHITECTURE` is an applied architecture and working-map layer.

It connects:

```text
epistemology
representation materialization
materialization governance
raw data audit
table specifications
experiments
strategy knowledge
```

It is not the operational source of truth for datasets, schemas, builders,
validators or promoted outputs.

Operational authority lives primarily in:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests
G:\TSIS\data
```

---

## 2. Mandatory Local Reading Order

Before modifying this folder, read:

```text
C:\TSIS_Data\AGENTS.md
C:\TSIS_Data\PROJECT_OPERATING_SYSTEM.md
C:\TSIS_Data\PROJECT_RULES.md
C:\TSIS_Data\VERSIONING_STANDARDS.md
C:\TSIS_Data\RESEARCH_PHILOSOPHY.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\LOCAL_RULES.md
```

For table work, also read:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\LOCAL_RULES.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\README.md
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\AGENT_CONTINUATION_GUIDE_013_018_v0_1.md
```

Then verify operational authority in:

```text
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\module_contracts\outputs
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\canonical_schemas
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\contract_registry
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\dataset_registry
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\data_consumption_policies
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\01_foundations\validators
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts
C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\tests
```

---

## 3. Critical Rule

This folder can explain meaning, sequence and governance.

It cannot by itself prove:

```text
dataset promotion
full-universe coverage
validator success
builder correctness
downstream consumption permission
```

Those claims require evidence from contracts, manifests, validators, status
matrices, test runs or inspected physical artifacts.

---

## 4. Graphify

Graphify is a map, not source of truth.

Use:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\graphify-out
```

for semantic navigation only.

Do not manually edit:

```text
graphify-out\graph.json
graphify-out\GRAPH_REPORT.md
graphify-out\graph.html
```

---

## 5. Table Work

For `03_TABLES_feature_engineering`, agents must follow:

```text
C:\TSIS_Data\00_CTO_APPLIED_ARCHITECTURE\03_TABLES_feature_engineering\LOCAL_RULES.md
```

No table work should start by inventing columns.

Every table must first answer:

```text
What phenomenon or representation do I want to materialize?
Why does it deserve to exist as its own entity?
What scientific questions must it answer?
What other representations consume it?
What minimum information does it need to contain?
Now, and only now: what attributes must it have?
```

---

## 6. Final Rule

No important TSIS knowledge should remain only in conversations.

If a decision matters, it must become one of:

```text
documented rule
contract
policy
validator
manifest
status matrix
changelog entry
```

