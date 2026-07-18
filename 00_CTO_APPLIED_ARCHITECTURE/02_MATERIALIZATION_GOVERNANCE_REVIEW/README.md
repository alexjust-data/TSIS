# Representation Materialization Review - Revision Index

Status: `governance_phase_ready_index_v0_2`

Date: `2026-07-15`

This folder contains the working governance artifacts created during the
Representation Materialization Review.

The current operational conclusion is:

```text
Design Phase is closed enough.
Governance Phase is active.
Event State candidate build is authorized.
No official table, promotion, certification, full-universe claim, or downstream
consumption is authorized here.
```

------------------------------------------------------------------------

## Folder Structure

```text
00_REVISION/
  README.md

  00_governance_phase/
    00_GOVERNANCE_PHASE_START.md
    CRM_PATTERN_v0_2.md
    CRM_CANDIDATE_FREEZE_RECORD_v0_1.md
    CRM_APPLICABILITY_MATRIX_v0_1.md

  01_contracts_and_templates/
    representation_justification_contract_v0_8.md
    representation_justification_record_template_v0_2.md
    materialization_decision_contract_v0_3.md

  02_market_state_pilot/
    rjr_market_state_v0_4.md
    mdr_market_state_v0_4.md
    mdr_market_state_v1.md

  03_event_state_governance/
    rjr_event_state_v1_3.md
    mdr_event_state_v1.md
    canonical_to_physical_mapping_event_state_v1.md
    event_state_candidate_build_authorization_v1.md

  _00_CTO/
    01_questions.md

  99_superseded_or_historical/
    historical or superseded seed material
```

------------------------------------------------------------------------

## How To Read This Folder

### `00_governance_phase/`

Defines the governance mechanism and the phase transition.

Use it to understand:

```text
Contract -> Record -> Review -> Decision -> Authorization
```

It also defines which TSIS objects require full CRM governance and which ones
should stay under ordinary Table Creation Process.

### `01_contracts_and_templates/`

Contains reusable governance contracts and templates.

These are not case-specific outputs. They govern how future Representation
Justification Records and Materialization Decision Records should be produced.

### `02_market_state_pilot/`

Contains the Market State pilot lineage.

Market State was used to prove the governance pattern and derive the first
materialization decision contract.

Interpretation:

```text
mdr_market_state_v0_4 = prototype lineage
mdr_market_state_v1   = first contract-compliant Market State MDR lineage
```

### `03_event_state_governance/`

Contains the active Event State governance chain.

Current chain:

```text
rjr_event_state_v1_3
  -> mdr_event_state_v1
  -> canonical_to_physical_mapping_event_state_v1
  -> event_state_candidate_build_authorization_v1
```

Current outcome:

```text
candidate_build_allowed_now = true
official_table_authorized = false
promotion_authorized = false
```

This means TSIS may build or rebuild the controlled candidate:

```text
event_state_table_v0_1_candidate_intraday_1m_quote_guarded_controlled
```

It does not mean the official `event_state_table` is promoted or ready for
production consumption.

------------------------------------------------------------------------

## Current Good Artifacts

| Artifact | Location | Interpretation |
| --- | --- | --- |
| `00_GOVERNANCE_PHASE_START.md` | `00_governance_phase/` | Marks the phase transition from design to governance. |
| `CRM_PATTERN_v0_2.md` | `00_governance_phase/` | Reusable governance pattern. |
| `CRM_CANDIDATE_FREEZE_RECORD_v0_1.md` | `00_governance_phase/` | Freeze record for the first stable governance baseline. |
| `CRM_APPLICABILITY_MATRIX_v0_1.md` | `00_governance_phase/` | Scope matrix for applying CRM governance. |
| `representation_justification_contract_v0_8.md` | `01_contracts_and_templates/` | Candidate contract for RJR governance. |
| `representation_justification_record_template_v0_2.md` | `01_contracts_and_templates/` | Template for future RJR records. |
| `materialization_decision_contract_v0_3.md` | `01_contracts_and_templates/` | Candidate contract for MDR governance. |
| `rjr_market_state_v0_4.md` | `02_market_state_pilot/` | Accepted Market State RJR pilot. |
| `mdr_market_state_v0_4.md` | `02_market_state_pilot/` | Prototype MDR used to derive the MDR contract. |
| `mdr_market_state_v1.md` | `02_market_state_pilot/` | Contract-compliant Market State MDR lineage. |
| `rjr_event_state_v1_3.md` | `03_event_state_governance/` | Accepted Event State RJR. |
| `mdr_event_state_v1.md` | `03_event_state_governance/` | Accepted Event State MDR for planning authorization. |
| `canonical_to_physical_mapping_event_state_v1.md` | `03_event_state_governance/` | Accepted Event State canonical-to-physical mapping. |
| `event_state_candidate_build_authorization_v1.md` | `03_event_state_governance/` | Accepted controlled candidate build authorization. |

------------------------------------------------------------------------

## Operational Rule

Do not create more governance documents here unless implementation work hits a
real blocker.

The next work should be engineering work:

```text
builder -> validator -> candidate table -> manifest -> status matrix update
```
