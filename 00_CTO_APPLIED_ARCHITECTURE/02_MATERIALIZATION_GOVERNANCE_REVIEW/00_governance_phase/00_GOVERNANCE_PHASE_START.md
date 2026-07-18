# 00_GOVERNANCE_PHASE_START

Status: `phase_transition_marker_v0_1`

Date: `2026-07-15`

This document marks the transition from the Representation
Materialization Design Phase to the Governance Phase.

It is not a contract.

It is not an institutional promotion record.

It is a historical and operational marker.

------------------------------------------------------------------------

## Phase Transition

```text
Design Phase has concluded.

Governance Phase begins.
```

The purpose of the Design Phase was to discover, test and stabilize the
governance mechanism itself.

The purpose of the Governance Phase is to apply that mechanism to real
cases.

------------------------------------------------------------------------

## Design Phase Outputs

The Design Phase produced the following candidate governance artifacts:

| Artifact | Role |
| --- | --- |
| `CRM_PATTERN_v0_2.md` | Governance Pattern |
| `CRM_CANDIDATE_FREEZE_RECORD_v0_1.md` | Freeze Record |
| `representation_justification_contract_v0_8.md` | Candidate Contract |
| `representation_justification_record_template_v0_2.md` | Candidate Template |
| `rjr_market_state_v0_4.md` | Pilot Record |
| `mdr_market_state_v0_4.md` | Prototype Record |
| `materialization_decision_contract_v0_3.md` | Candidate Contract |

These artifacts are Design Phase outputs.

They are stable enough to support Governance Phase work, but they do not
constitute global TSIS institutional law.

------------------------------------------------------------------------

## Governance Phase Rule

From this point onward, TSIS should not keep designing the governance
mechanism unless a fundamental architectural issue is found.

The default operating mode becomes:

```text
Apply existing governance contracts to real cases.
```

The question changes from:

```text
How should the contract work?
```

to:

```text
What decision does the contract produce when applied to this case?
```

------------------------------------------------------------------------

## Lineage Boundary

The prototype MDR lineage is complete:

```text
mdr_market_state_v0_1
        |
        v
mdr_market_state_v0_2
        |
        v
mdr_market_state_v0_3
        |
        v
mdr_market_state_v0_4
        |
        v
materialization_decision_contract_v0_3
```

That lineage belongs to the Design Phase.

The first Governance Phase MDR should start a new lineage:

```text
materialization_decision_contract_v0_3
        |
        v
mdr_market_state_v1
```

Do not create:

```text
mdr_market_state_v0_5
```

because that would mix prototype lineage with contract-compliant
governance lineage.

Use:

```text
mdr_market_state_v1
```

with candidate status inside the record, for example:

```text
governance_scope = candidate_governance
mdr_status = draft
contract_version = materialization_decision_contract_v0_3
```

`candidate` is a status, not a stable artifact identity.

------------------------------------------------------------------------

## Operational Consequence

Before this transition, TSIS was primarily producing:

```text
documents
        |
        v
reviews
```

After this transition, TSIS should increasingly produce:

```text
real case
        |
        v
governance record
        |
        v
formal review
        |
        v
decision
        |
        v
scoped authorization
```

The system should grow through governed records, not through uncontrolled
documentation expansion.

------------------------------------------------------------------------

## Reopening Design Phase

The Design Phase may be reopened only if a serious architectural issue is
found, such as:

- a contradiction between candidate contracts;
- an authority conflict with higher-level TSIS documents;
- a missing governance gate that could permit physical realization,
  certification, promotion or downstream consumption without review;
- an inability to apply the contract to real cases.

Minor wording improvements are not sufficient reason to reopen the Design
Phase.

------------------------------------------------------------------------

## Fundamental Rule

```text
Design Phase produced the governance mechanism.

Governance Phase applies the governance mechanism.
```

From this point forward, every new representation materialization decision
should be expressed as a governed record under the appropriate candidate
contract, reviewed explicitly, and converted into a scoped decision.
