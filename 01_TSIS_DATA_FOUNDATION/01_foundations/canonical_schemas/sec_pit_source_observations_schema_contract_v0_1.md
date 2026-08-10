# SEC PIT Source Observations Schema Contract v0_1

## Role

`sec_pit_source_observations_v0_1` stores immutable, source-oriented evidence
extracted from SEC filings. It is not a daily state table and does not assert
exact historical float.

## Grain

```text
one extracted observation or event
from one accession/source object
under one extraction method
```

Logical key: `observation_id`.

## Required columns

```text
observation_id
observation_type
cik
accession_number
form
instrument_id
security_class_id
value
unit
measurement_at
effective_at
filing_accepted_at
eligible_from_session
availability_policy_id
source_url
source_sha256
source_excerpt
extraction_method
quality_state
causality_state
attributes
```

`value = NULL` is permitted for event evidence. Missing values must never be
coerced to zero.

## Separation

This dataset may contain O/S anchors, capital-event candidates, holder
positions, holder status and restriction evidence. Methodology-dependent float
belongs downstream in a resolved state dataset.

## Causality

Only observations with a resolved `eligible_from_session` may enter a PIT
resolver. `filing_date`, `report_date` and accounting `period_end` are not
availability timestamps.

