# Event Type Registry Seed Design v0.1

Status: `closed_design_ready_with_restrictions_no_population_v0_1`
Date: `2026-07-24`
Scope: `empty_event_type_registry_schema_status_model_and_admission_workflow`

This document closes the seed design for an empty TSIS Event Type Registry.

It does not populate the registry.
It does not accept any Event Type.
It does not detect events.
It does not create event instances.
It does not authorize Event State builders, integration, materialization,
parquet, production or downstream consumption.

## 1. Design Decision

```text
event_type_registry_seed_design = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_schema = CLOSED_DESIGN_READY_WITH_RESTRICTIONS
event_type_registry_population = NOT_AUTHORIZED
accepted_event_families = 0
accepted_event_types = 0
event_detection_execution = NOT_AUTHORIZED
event_instance_binding_execution = NOT_AUTHORIZED
event_state_builder_execution = NOT_AUTHORIZED
```

The registry grammar is now designed. The event dictionary remains empty.

## 2. Governing Inputs

This seed design depends on:

```text
event_state_event_policy_v0_1.md
event_type_or_event_family_contract_design_v0_1.md
event_type_or_event_family_contract_design_contract_v0_1.json
../06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_v0_1.md
../06_MARKET_STATE_INTEGRATION/event_state_profile_contract_design_contract_v0_1.json
```

The parent Market State profile remains:

```text
market_state_core_four_intraday_profile_v0_1
```

This is a semantic parent profile. This seed design does not authorize physical
Market State dataset consumption.

## 3. Registry Identity

The seed registry identity is:

```text
event_type_registry_id = tsis_event_type_registry
event_type_registry_version = v0_1
registry_population_state = empty
registry_population_authorized = false
accepted_event_type_count = 0
```

Future population gates must create a new governed registry snapshot or append
under an explicitly authorized registry update policy. No entry may appear in
the registry without a review record.

Current-state clarification after the initial candidate population: entries with
`status = investigational_candidate` may carry
`admission_review_record_id = pending_admission_review_not_authorized`. That
marker is not an admission review and must block Event Instance binding until a
separate admission review creates a real review record and changes status.

## 4. Registry Sections

The registry schema has these top-level sections:

```text
registry_metadata
family_entries
type_entries
variant_entries
composition_entries
admission_review_records
supersession_records
closed_boundary_attestation
```

For this seed design, all entry arrays are empty by design.

## 5. Status Model

Every future family, type, variant or composition entry must carry one explicit
status:

```text
investigational_candidate
contract_draft
accepted_with_restrictions
accepted
rejected
quarantined
superseded
```

Only the following statuses may support concrete Event Instance binding:

```text
accepted_with_restrictions
accepted
```

All other statuses are non-binding for Event State.

## 6. Namespace Rules

Allowed candidate family namespaces:

```text
market_data
regulatory
market_structure
information
scanner
geometry
microstructure
research
```

Allowed event domains:

```text
market
information
microstructure
regulatory
system
research
scanner
```

Allowed epistemic roles:

```text
observed_phenomenon
system_generated_candidate
research_annotation
governance_state_change
```

These namespaces are allowed candidate namespaces, not accepted registry
families. A scanner or research event must not be represented as a market
phenomenon unless its `event_domain` and `event_epistemic_role` explicitly
justify that classification.

## 7. Family Entry Schema

Every future family entry must include:

```text
event_family_id
event_family_version
event_family_namespace
canonical_name
semantic_definition
observable_origin
anchor_definition_policy
eligible_event_domain_values
eligible_event_epistemic_role_values
allowed_event_type_namespace
forbidden_strategy_labels
status
definition_hash
admission_review_record_id
created_at_utc
supersedes_family_id
superseded_by_family_id
```

Validation requirements:

```text
event_family_id is unique within registry version
status is one of the allowed status values
definition_hash is present for non-draft entries
accepted family entries require admission_review_record_id
strategy, outcome and profitability labels are forbidden in identity
```

## 8. Type Entry Schema

Every future Event Type entry must include:

```text
event_type_id
event_type_version
event_family_id
event_domain
event_epistemic_role
canonical_name
semantic_definition
observable_origin
source_dataset_authority
source_quality_requirements
event_anchor_timestamp_policy
first_observable_timestamp_policy
detection_timestamp_policy
confirmation_timestamp_policy
invalidation_timestamp_policy
end_timestamp_policy
eligibility_policy_id
population_policy_id
window_policy_id
allowed_state_roles
allowed_consumption_legality
detector_contract_id
detector_version
detector_required
event_variant_policy
composition_allowed
status
definition_hash
admission_review_record_id
created_at_utc
supersedes_event_type_id
superseded_by_event_type_id
```

Validation requirements:

```text
event_type_id is unique within registry version
event_family_id resolves to exactly one family entry
event_domain is explicit
event_epistemic_role is explicit
timestamp policies are explicit
source_dataset_authority is explicit
accepted entries require definition_hash
accepted entries require admission_review_record_id
accepted entries require detector_contract_id unless detector_required = false
strategy, trade action, outcome, profitability and reward labels are forbidden
```

## 9. Variant Entry Schema

Variants may specialize implementation without changing scientific meaning.

Every future variant entry must include:

```text
event_variant_id
event_variant_version
parent_event_type_id
implementation_parameters
threshold_policy
detector_variant_version
status
variant_hash
admission_review_record_id
```

Variants must not become hidden strategy rules or hidden outcome filters.

## 10. Composition Entry Schema

Compositions combine accepted Event Types into a higher-order construct.

Every future composition entry must include:

```text
event_composition_id
event_composition_version
component_event_type_ids
composition_semantics
temporal_order_policy
overlap_policy
status
definition_hash
admission_review_record_id
```

Compositions do not replace elemental Event Type definitions.

## 11. Admission Review Record Schema

Every future admission review record must include:

```text
admission_review_record_id
reviewed_entry_id
reviewed_entry_kind
reviewed_entry_version
review_decision
reviewed_at_utc
reviewer_authority
evidence_bundle_id
source_authority_check
temporal_legality_check
leakage_check
strategy_outcome_boundary_check
detector_contract_check
market_state_compatibility_check
known_restrictions
blocking_findings
```

Allowed review decisions:

```text
approve_with_restrictions
approve
reject
quarantine
request_revision
```

An accepted Event Type requires a review decision of either:

```text
approve_with_restrictions
approve
```

## 12. Identity Rules

Future identifiers must be stable, deterministic and not implementation-only.

Recommended identity shape:

```text
event_family_id = event_family:<namespace>:<slug>
event_type_id = event_type:<namespace>:<slug>
event_variant_id = event_variant:<event_type_slug>:<variant_slug>
event_composition_id = event_composition:<slug>
```

Identifiers must not include:

```text
long
short
buy
sell
profit
winner
edge
alpha
reward
best
high_probability
```

## 13. Binding Rules For Future Instance Gates

Concrete Event Instance binding may proceed only if:

```text
event_type_id resolves to exactly one registry entry
entry status is accepted_with_restrictions or accepted
event_family_id resolves to exactly one registry entry
definition_hash matches the registry entry
source_dataset_authority is satisfied
timestamp policies are satisfied
detector authority is satisfied when detector_required = true
```

If any requirement is missing, the instance gate must block before creating
instances.

## Future Event Identity Stability Field

Date: `2026-07-24`

Before the registry grows materially, a future registry schema revision should
consider adding:

```text
event_identity_stability
    = immutable
    | conditionally_stable
    | source_dependent
    | experimental
```

This field is not required by the v0.1 seed schema and does not change the
current candidate population. Its purpose would be to separate administrative
status from epistemic stability. For example, `halt_resumed` may eventually be
classified as `immutable` if source authority and timestamp semantics pass
admission review, while more interpretive phenomena may remain `experimental`.

## 14. Closed Boundaries

Still closed:

```text
event_type_registry_population
event_type_admission_execution_without_separate_authorization
event_detection_execution
event_instance_binding_execution
event_window_binding_execution
market_state_physical_consumption
event_state_builder_execution
event_state_integration_execution
event_state_materialization
event_state_physical_validation
official_event_state_profile_promotion
official_event_state_dataset_promotion
production
downstream_consumption
```

## 15. Next Gate

Next gate, only if explicitly authorized:

```text
market_state_profile_compatibility_design_authorization_v0_1
```

The initial population, initial admission review, Event Instance Binding Design and Event Window Binding Design are now recorded separately. The next gate may authorize Market State Profile Compatibility Design only; it does not create instances, bind windows, authorize detectors, builders, materialization, production or downstream consumption.

