# Variable Attribute Admission Record Template v0.1

Status: `template_v0_1_no_execution`
Date: `2026-07-24`
Scope: `variable_attribute_admission_record_template`
Parent policy: `02_VARIABLE_AND_ATTRIBUTE_ADMISSION_POLICY_v0_1.md`

## Purpose

Use this template when a TSIS actor proposes that a raw source attribute,
derived feature, State variable, Event variable, outcome label or
quality/lineage/governance attribute should be admitted, restricted, blocked or
rejected.

This template answers:

```text
Who proposed this variable?
Why now?
What governed construct does it serve?
What evidence supports or blocks admission?
What authority is allowed to decide?
```

This template does not admit the variable by itself.

## Boundary

```text
record_template_status = RECORDED_TEMPLATE_NO_EXECUTION
new_variable_admitted = false
schema_change_authorized = false
builder_execution_authorized = false
materialization_authorized = false
dataset_promotion_authorized = false
downstream_consumption_authorized = false
```

## Who May Propose A Variable

A proposal may originate from several layers, but proposal is not admission.

| Proposer | May Propose When | Cannot Do |
| --- | --- | --- |
| `Data Foundation owner / validator` | A source exposes a new governed field, a schema/quality audit identifies a useful physical attribute, or a derived feature can be produced under a governed formula. | Cannot decide scientific State meaning alone. |
| `Applied Architecture owner / Information Object steward` | An admitted Information Object needs a Representation Model implementation or an operational mapping has a gap. | Cannot promote physical datasets or authorize production use. |
| `Research experiment owner` | A versioned research question needs a candidate measure, or evidence shows a representation is missing, unstable or redundant. | Cannot add the variable directly to canonical State. |
| `Event governance owner` | Event Type, Event Instance, Event Window or Event State design requires an event variable or temporal legality field. | Cannot populate accepted event instances without later gates. |
| `Builder / validator agent` | A validation run exposes a blocker, missing source binding, ambiguity, leakage risk or determinism issue. | Cannot solve the blocker by silently adding fields. |
| `ML / AlphaEvolve / optimizer` | It produces candidate evidence about redundancy, predictive utility, stability or transformations under a research experiment. | Cannot admit, promote or rewrite source truth. |
| `Human / CTO reviewer` | A conceptual gap, operational need or governance concern requires a formal admission review. | Cannot make the decision live only in conversation. |

## When A Proposal Is Legitimate

A proposal is legitimate only when it is attached to one of these triggers:

```text
new_information_object_admission
operational_mapping_gap
builder_validation_blocker
Data_Foundation_source_capability_change
research_experiment_evidence
redundancy_or_instability_evidence
Event_State_contract_requirement
outcome_contract_requirement
promotion_or_consumption_review_gap
```

A proposal is not legitimate when the reason is only:

```text
indicator_is_popular
paper_mentions_it_without_TSIS_mapping
backtest_result_improved_after_trying_it
it_is_easy_to_compute
it_exists_in_a_library
it_is_available_in_a_table
strategy_needs_it_without_object_admission
```

## Record Identity

```text
record_id:
record_version: v0_1
created_at_utc:
created_by:
proposer_role:
proposal_trigger:
proposal_status: draft
```

Allowed `proposal_status` values:

```text
draft
ready_for_review
accepted_with_restrictions
accepted
blocked
rejected
quarantined
superseded
```

## Candidate Attribute

```text
candidate_attribute_id:
candidate_attribute_name:
artifact_class:
```

Allowed `artifact_class` values:

```text
raw_source_attribute
derived_feature
state_variable
event_variable
outcome_label
quality_lineage_governance_attribute
```

## Scientific Or Institutional Construct

```text
information_object_id:
event_construct_id:
outcome_construct_id:
governance_construct_id:
representation_model_id:
state_profile_id:
event_state_profile_id:
research_experiment_id:
```

Rule:

```text
At least one governed construct must be named.
If none exists, the proposal cannot be admitted and must remain investigational.
```

## Source And Formula

```text
source_dataset_id:
source_dataset_version:
source_table_id:
source_attribute_ids:
source_registry_status:
source_consumption_policy:
derivation_formula_id:
derivation_formula_version:
derivation_inputs:
derivation_window:
parameter_values:
parameter_rationale:
```

Parameter rule:

```text
A parameterized feature is not admitted because the base feature is admitted.
ATR does not automatically admit ATR(17).
RVOL does not automatically admit every RVOL window.
Each parameter must have representation rationale or restricted research status.
```

## Temporal And Grain Policy

```text
grain:
primary_keys:
entity_keys:
decision_timestamp_field:
source_timestamp_field:
as_of_field:
valid_from_field:
valid_to_field:
calendar_authority:
cutoff_policy:
lookback_policy:
future_data_dependency_check:
```

Required statement:

```text
Is this attribute legally observable at the timestamp or state_role where it is
intended to be used?
```

Answer:

```text
legal_as_of_status:
legal_as_of_evidence:
leakage_risk:
```

## Information Gain And Redundancy

```text
information_added:
existing_variables_with_overlap:
redundancy_assessment:
why_existing_variables_are_insufficient:
stability_evidence:
regime_sensitivity_evidence:
research_evidence:
```

A variable should be blocked if it is only another encoding of information TSIS
already preserves and no clear reason exists for keeping it.

## Quality, Lineage And Validation

```text
schema_contract:
dataset_contract:
validator_evidence:
inspection_dossier:
lineage_requirements:
fingerprint_requirements:
null_policy:
duplicate_policy:
outlier_policy:
known_failure_modes:
```

## Consumption And Execution Boundary

```text
allowed_profiles:
allowed_experiments:
allowed_builders:
allowed_materializations:
allowed_consumers:
production_allowed: false
downstream_consumption_allowed: false
```

Any non-false production or downstream field requires a separate gate. This
record cannot authorize it by itself.

## Review Decision

```text
reviewer:
review_date:
decision:
decision_reason:
restrictions:
blockers:
required_followup_gate:
supersedes:
superseded_by:
```

Allowed `decision` values:

```text
ACCEPTED
ACCEPTED_WITH_RESTRICTIONS
BLOCKED_PENDING_SOURCE_AUTHORITY
BLOCKED_PENDING_TEMPORAL_POLICY
BLOCKED_PENDING_VALIDATOR_EVIDENCE
REJECTED_REDUNDANT
REJECTED_LEAKAGE
REJECTED_WRONG_OBJECT
QUARANTINED
SUPERSEDED
```

## Minimal Example: ATR Proposal

```text
candidate_attribute_name = ATR_14
artifact_class = derived_feature
information_object_id = volatility_range_state
representation_model_id = range_instability_model
source_dataset_id = governed OHLCV source
parameter_values = window=14
parameter_rationale = must be justified by representation policy or research evidence
legal_as_of_status = pending
proposal_status = draft
```

Conclusion:

```text
ATR_14 can be proposed.
ATR_14 is not admitted until source, formula, temporal legality, redundancy and
validation evidence are reviewed.
```

## Minimal Example: RVOL Proposal

```text
candidate_attribute_name = RVOL_20D
artifact_class = derived_feature or state_variable, depending on scope
information_object_id = trading_activity
representation_model_id = relative_participation_model
source_dataset_id = governed daily/intraday volume source
parameter_values = lookback_sessions=20
legal_as_of_status = pending prior-session cutoff evidence
proposal_status = draft
```

Conclusion:

```text
RVOL_20D can be proposed by an Information Object mapping owner, Research owner
or Data Foundation feature owner, but the admission decision belongs to the
relevant governed review.
```

## Final Boundary

```text
This template records how to ask for admission.
It does not answer the admission request.
```
