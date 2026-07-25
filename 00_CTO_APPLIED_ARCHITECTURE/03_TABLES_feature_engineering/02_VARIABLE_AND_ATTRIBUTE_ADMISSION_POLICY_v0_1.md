# Variable And Attribute Admission Policy v0.1

Status: `recorded_policy_v0_1_no_execution`
Date: `2026-07-24`
Scope: `applied_architecture_variable_attribute_admission_policy_bridge`

## Purpose

This document consolidates an existing TSIS policy that was previously
distributed across:

```text
00_TABLES_MARKET_STATE_EVENT_STATE.md
01_INFORMATION_OBJECT_ADMISSION_PROCESS.md
04_INFORMATION_OBJECT_OPERATIONAL_MAPPING/
05_STATE_BUILDER_VALIDATION/
06_MARKET_STATE_INTEGRATION/
```

It answers one institutional question:

```text
Why does one variable, attribute or feature enter a TSIS representation while
another does not?
```

This document does not create a new architecture. It records the bridge between
Data Foundation attributes, Information Objects, operational mappings, State
profiles and future research variables.

## Boundary

This policy does not:

```text
admit a new Information Object
admit a new variable into Market State
admit a new variable into Event State
change any physical schema
promote any dataset
authorize any builder
authorize any materialization
authorize any downstream consumption
populate the Event Type Registry
create outcomes or labels
```

Current status:

```text
variable_and_attribute_admission_policy = RECORDED_NO_EXECUTION
physical_schema_changes_authorized = false
state_variable_admission_authorized = false
event_variable_admission_authorized = false
outcome_label_admission_authorized = false
builder_execution_authorized = false
dataset_promotion_authorized = false
downstream_consumption_authorized = false
```

## Authority Split

No single layer decides everything.

| Authority | Decides | Does Not Decide |
| --- | --- | --- |
| `Data Foundation` | Physical source attributes, dataset contracts, schemas, validators, registry state, quality evidence, physical location and consumption policies. | Scientific meaning of State variables or trading use. |
| `Applied Architecture` | Information Objects, representation models, operational mapping, State profile semantics and whether a variable can represent admitted information. | Physical dataset promotion, production use or schema truth by itself. |
| `Execution Authority` | Whether a specific run may read, build, materialize, promote or consume an artifact under an approved scope. | Scientific meaning or source truth. |
| `Research Governance` | Research questions, evidence generation, hypothesis tests and proposed variables. | Final institutional admission by itself. |
| `ML / AlphaEvolve / Optimizers` | Candidate evidence about redundancy, instability, utility or transformations. | Direct admission, promotion or source-of-truth changes. |

Rule:

```text
Research may propose.
Applied Architecture may admit semantic representation.
Data Foundation governs physical data authority.
Execution gates authorize use.
Builders execute; builders do not choose.
```

## Artifact Classes

TSIS must not use one word, `variable`, for every column-like object.

| Class | Meaning | Authority |
| --- | --- | --- |
| `raw_source_attribute` | Field preserved from a source payload or raw/staged source table. | Data Foundation. |
| `derived_feature` | Feature calculated from governed source attributes under an explicit formula and temporal policy. | Data Foundation for physical derivation; Applied Architecture for representational meaning. |
| `state_variable` | Variable that implements a Representation Model for an admitted Information Object inside a Market State or Event State profile. | Applied Architecture plus builder validation. |
| `event_variable` | Variable that describes an Event Type, Event Instance, Event Window, temporal role or event-conditioned state. | Event State governance plus Applied Architecture. |
| `outcome_label` | Forward-looking or post-decision result variable. | Research / Outcome governance; never an input State variable unless explicitly allowed as research-only context. |
| `quality_lineage_governance_attribute` | Quality flag, lineage pointer, fingerprint, source id, run id, policy field or restriction marker. | Governing layer that owns the artifact. It may accompany a State record but is not market information by default. |

## Admission Direction

Variables must not enter from intuition or convenience.

Forbidden pattern:

```text
I need ATR, so add ATR.
I need VWAP, so add VWAP.
This paper mentions Gap%, so add Gap%.
```

Required scientific direction:

```text
observable phenomenon or scientific need
    -> Information Object
        -> Representation Model
            -> candidate capability
                -> candidate variable / attribute
                    -> governed source or derivation
                        -> temporal legality
                            -> validation evidence
                                -> admission decision
```

Physical tables can discover candidates:

```text
existing tables
    -> real variables
        -> derivable capabilities
            -> possible meanings
                -> candidate Information Objects
```

But discovery does not admit.

```text
Tables can discover candidates.
Admission defines meaning.
Operational mapping authorizes the bridge.
Execution gates authorize use.
```

## Required Admission Questions

Before a variable, attribute or feature can be treated as admitted for a TSIS
representation, the responsible gate must answer:

```text
1. What Information Object, Event construct or Outcome construct does it serve?
2. What Representation Model does it implement?
3. What distinct information does it add that is not already represented?
4. What governed source attributes or derivation formula produce it?
5. What is the grain, key and temporal/as-of rule?
6. Is it legally observable at the decision timestamp or event role where it is used?
7. What lineage, contract, schema, validator and evidence support it?
8. What profile, dataset, builder or experiment is allowed to consume it?
9. What restrictions, blockers or research-only limits remain live?
10. What would make the variable rejected, quarantined or superseded?
```

If these questions cannot be answered, the variable remains a candidate, not an
admitted variable.

## Admission Criteria

A variable can be admitted only when all required evidence exists for its
declared class and scope.

Minimum criteria:

```text
represents_admitted_information_object_or_governed_construct = true
implements_approved_representation_model = true
governed_source_or_formula_exists = true
temporal_as_of_policy_exists = true
leakage_gate_passed = true
lineage_available = true
contract_or_schema_reference_available = true
quality_or_validator_evidence_available = true
scope_and_profile_declared = true
builder_or_materialization_gate_if_needed = authorized_separately
```

Admission can be restricted:

```text
accepted_with_restrictions
```

is valid when the variable has clear meaning and legal use under a bounded
scope, but still carries limitations such as incomplete history, candidate
physical status, source-specific quality limits or non-production usage.

## Rejection And Blocking Criteria

A variable must be blocked, rejected or kept investigational when:

```text
it has no admitted Information Object or governed construct
it is a redundant proxy without demonstrated additional information
it belongs to another Information Object
it is an outcome or future-dependent field presented as an input
it lacks a governed source
it lacks a derivation formula
it lacks temporal/as-of legality
it lacks schema, contract, lineage or validator evidence
it depends on arbitrary parameters with no declared rationale
it changes scientific meaning through a variant name
it creates leakage, ambiguous grain or unstable identity
it cannot be reproduced under a versioned run/config
```

Example:

```text
ATR may represent Volatility / Range State if admitted under a defined model.
ATR(17) is not automatically admitted because ATR exists.
The parameter 17 needs a representation rationale, empirical evidence, or a
restricted research status.
```

## Status Model

Recommended statuses for variable-level records:

```text
discovered_source_attribute
candidate_derived_feature
candidate_state_variable
candidate_event_variable
candidate_outcome_label
mapped_with_restrictions
accepted_with_restrictions
accepted
blocked_pending_source_authority
blocked_pending_temporal_policy
blocked_pending_validator_evidence
rejected_redundant
rejected_leakage
rejected_wrong_object
quarantined
superseded
```

These statuses do not replace Data Foundation dataset status, Information
Object admission status or Event Type Registry status. They are a bridge for
attribute-level reasoning.

## How This Applies To 000-012

The `000-012` representation tables were reconciled against Data Foundation
evidence as restricted datasets for their declared scopes.

That means:

```text
their physical attributes have Data Foundation evidence
their use remains bounded by contracts and consumption policies
their columns are not automatically State variables
their presence does not imply official unrestricted dataset status
```

Applied Architecture can use those fields only when an admitted Information
Object, mapping and execution gate allow it.

## How This Applies To 013-018

The `013-018` area requires extra care because physical artifacts, scoped
candidates, semantic profiles and future Event State design can be confused.

Rules:

```text
013/014 source or surface attributes do not become builder inputs unless an
explicit gate authorizes the surface and mapping.

016 legacy physical candidates do not instantiate the promoted
market_state_core_four_intraday_profile_v0_1 official semantic profile as an
official dataset.

017 Event State variables cannot be admitted until Event Type, Event Instance,
Event Window and compatibility gates allow the relevant construct.

018 scanner candidates are attention/candidate surfaces, not accepted Event
Types and not Event State authority.
```

## Role Of Research, ML And AlphaEvolve

Research, ML and AlphaEvolve can produce evidence such as:

```text
variable redundancy
instability across regimes
improved representation quality
candidate transformations
candidate thresholds
candidate event definitions
```

They cannot directly admit variables.

Their output must be routed through:

```text
research_experiment
    -> evidence
        -> admission review
            -> mapping or rejection decision
```

## Minimal Future Admission Record

When TSIS later admits or rejects a specific variable, the record should include:

```text
variable_id
artifact_class
information_object_id_or_governed_construct
representation_model_id
source_dataset_id
source_attribute_ids
derivation_formula_id
temporal_policy_id
grain
keys
as_of_rule
lineage_requirements
quality_requirements
validator_evidence
admission_status
restrictions
allowed_profiles
allowed_consumers
promotion_status
supersession_policy
```

The standing record template now lives in:

```text
03_VARIABLE_ATTRIBUTE_ADMISSION_RECORD_TEMPLATE_v0_1.md
```

This can become a separate executable admission gate later. This document only
records the policy.

## Current Institutional Conclusion

```text
variable_and_attribute_admission_policy = RECORDED_NO_EXECUTION
variable_attribute_admission_record_template = RECORDED_TEMPLATE_NO_EXECUTION
policy_function = consolidate_existing_distributed_policy
new_variables_admitted = 0
schema_changes_authorized = 0
builder_runs_authorized = 0
materializations_authorized = 0
dataset_promotions_authorized = 0
downstream_consumption_authorized = 0
```

The practical answer to "who chooses variables?" is:

```text
Data Foundation governs what physically exists.
Applied Architecture governs what a variable means.
Operational mapping proves how it represents an admitted object.
Execution gates decide whether it can be used in a run.
Research and ML may provide evidence, but not final authority.
```
