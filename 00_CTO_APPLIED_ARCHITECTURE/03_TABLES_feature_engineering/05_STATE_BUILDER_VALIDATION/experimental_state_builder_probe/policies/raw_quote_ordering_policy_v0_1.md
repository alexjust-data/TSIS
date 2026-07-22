# Raw Quote Ordering Policy v0.1

Status: `experimental_non_production_policy`
Date: `2026-07-21`
Scope: `bounded_quality_and_lineage_validation`

This policy governs quote-level ordering evidence for `raw_quotes`.

It does not deduplicate quotes, choose a venue, repair quote rows, or authorize quote-dependent builders.

## Decision

`instrument_id + quote_timestamp` is not assumed to be a complete physical key. If bounded evidence finds more than one distinct quote state at the same instrument and timestamp, quote-level builder execution remains blocked until an additional governed ordering component exists.

Acceptable future ordering evidence may include:

```text
quote_sequence
source_row_number
ingestion_ordinal
venue + source precedence
manifested ordering contract
```

## Rule

```text
same timestamp + identical quote rows:
    deterministic duplicate collapse may be considered later
    promotion remains restricted until full-history validation

same timestamp + distinct quote states:
    no silent collapse
    quote-level builder execution blocked
    require additional ordering or precedence policy
```

This blocker is scoped to quote-dependent objects. It does not block the core-four experimental builder path when that path does not consume `raw_quotes`.

## Current Gate Authority

```text
bounded_sample_data_read_allowed = true_under_scope_only
feature_builder_execution_allowed = false
state_materialization_allowed = false
source_mutation_allowed = false
```
