# Daily Row Availability Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `metadata_only_column_binding_gate`

This policy resolves the `004_master_daily_table.as_of_utc` binding only as a
conservative legal availability rule. It does not claim observed source
availability, source ingestion time, vendor publication time or row-level value
legality.

## Decision

`session_date` is not an availability timestamp.

The physical schema currently does not expose a row-level `as_of_utc` field or a
manifest-level observed availability timestamp for the inspected daily surface.
Therefore `004_master_daily_table.as_of_utc` may be represented only as:

```text
observed_source_availability = unavailable
conservative_legal_availability = governed_by_policy
```

## Conservative Rule

```text
current-session final daily fields
    available only after official session close plus declared safety delay

prior-session daily fields
    available from the next valid session start
    if the daily row exists and applicable quality gates pass
```

The future builder must compute any usable `component_as_of_utc` from governed
calendar/session metadata and the source `session_date`; it must not equate the
source event date with source availability.

## Current Gate Authority

This policy authorizes only metadata-level binding resolution:

```text
physical_resolution_type = derived_from_existing_column
derivation_rule = daily_row_availability_policy_v0_1
bounded_sample_data_read_allowed = false
temporal_value_validation = not_executed
state_materialization_allowed = false
```

A later temporal-value gate must validate the actual cutoff behavior before this
source can support row-level State construction.
