# Tables 000-018 Evidence Reconciliation Authorization v0.1

Status: `AUTHORIZED_WITH_RESTRICTIONS_CONSUMED`
Date: `2026-07-24`
Gate: `tables_000_018_evidence_reconciliation_against_data_foundation_registry_v0_1`
Accepted run: `tables_000_018_evidence_reconciliation_v0_1_20260724T081044Z`
Reconciliation status: `CLOSED_WITH_FINDINGS_NO_PROMOTION`

## Purpose

This authorization opens a read-only reconciliation gate between:

```text
Applied Architecture table ids 000-018
```

and the Data Foundation evidence stack:

```text
schemas
dataset contracts
dataset registry entries
consumption policies
validators
status matrices
physical-output status evidence
```

The gate answers:

```text
What evidence exists?
What evidence is missing?
What evidence is ambiguous?
What institutional conclusion can be stated conservatively?
```

It does not design new tables, does not promote datasets and does not authorize
execution or downstream consumption.

## Authorized Inputs

```text
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/
  04_TSIS_TABLES_000_018_INSTITUTIONAL_STATUS_MATRIX_v0_1.md

01_TSIS_DATA_FOUNDATION/01_foundations/
  module_contracts/outputs/data_foundation_outputs_status_matrix_v0_1.md
  module_contracts/outputs/data_foundation_outputs_target_contract_v0_1.md
  canonical_schemas/
  contract_registry/dataset_contracts/
  dataset_registry/
  data_consumption_policies/
  validators/
```

Historical path references must be interpreted through:

```text
PATH_MIGRATION_2026_07_22.md
```

## Authorized Outputs

```text
00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/
  06_tables_000_018_evidence_reconciliation_readout_v0_1.md

00_CTO_APPLIED_ARCHITECTURE/03_TABLES_feature_engineering/runs/
  tables_000_018_evidence_reconciliation_v0_1_<timestamp>/
    pre_manifest.json
    heartbeat.json
    reconciliation_matrix.csv
    reconciliation_matrix.json
    final_manifest.json
    tables_000_018_evidence_reconciliation_readout.md
```

## Explicitly Not Authorized

```text
dataset promotion = false
official dataset registry write = false
official parquet write = false
candidate parquet copy = false
production builder execution = false
downstream consumption = false
Market State materialization = false
Event State materialization = false
event type registry population = false
event detection execution = false
physical source market-data reads = false
parquet reads = false
heavy recursive dossier scan = false
```

## Reconciliation Rule

The reconciler may record a stronger status only when concrete Data Foundation
evidence is found. It must not infer official status from:

```text
file existence alone
discovery-pass maturity
Graphify nodes
bounded experimental runs
candidate parquet evidence
semantic-profile promotion
```

When evidence is insufficient, the correct status is:

```text
UNRESOLVED
```

or a narrower partial state such as:

```text
PARTIALLY_RECONCILED
```

## Immediate Scope

The gate covers all table ids `000` through `018`, with emphasis on the
highest-risk semantic/physical split:

```text
013, 014, 016, 017, 018
001, 004
000-012 remainder
```

## Next Gate

At reconciliation close, the next allowed architectural gate was `event_type_registry_seed_design_v0_1`. That design-only gate has since closed. The current next possible Event State gate, only if explicitly authorized, is:

```text
event_type_registry_initial_population_authorization_v0_1
```

No Event State execution opens from this reconciliation.
