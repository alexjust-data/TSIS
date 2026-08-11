# SEC PIT PGAC ownership class-reconciliation probe plan v0_1

Date: `2026-08-11`

Status: `AUTHORIZED_BOUNDED_EXECUTION`

Human gate: `S5_CONFIRMED_2026-08-11`

## Purpose

Continue the no-network PGAC pilot from the confirmed daily Class A O/S state
through ownership extraction, holder identity, economic-position deduplication
and a candidate owner-exclusion float. No other ticker or network acquisition
is authorized.

## Critical class rule

The July 15, 2025 proxy table reports ownership against combined Class A and
Class B ordinary shares. Its rows must not be subtracted directly from Class A
O/S.

The local primary evidence supports this reconciliation:

```text
proxy insider/affiliate total             2,400,500
Class B ordinary shares                   2,156,250
Class A private-placement sponsor shares    244,250
                                         ---------
reconciled total                          2,400,500
```

The sponsor Schedule 13D explicitly decomposes its 2,180,500 total into
244,250 Class A and 1,936,250 Class B shares. The individual director/officer
proxy rows total 220,000 and are matched to Class B Forms 3. The Class B
components therefore reconcile exactly:

```text
sponsor Class B                           1,936,250
individual officer/director Class B         220,000
                                         ---------
total Class B                             2,156,250
```

Only the supported 244,250 Class A sponsor position is a candidate exclusion
under `officer_director_explicit_affiliate_v0_1`. Generic Schedule 13G
institutional positions are preserved in the neutral ledger but are not
automatically excluded.

## Identity continuity gate

Opening-state evidence may cross the Shepherd Ave -> Aifeex Nexus -> Pantages
name sequence only because the locally acquired August 12, 2025 Form 8-K
explicitly proves:

- the same issuer CIK `0002030829`;
- a name change, not a new issuer;
- the ticker transition `AIFE -> PGAC` commencing August 8, 2025;
- continued Class A ordinary-share registration.

CIK equality alone remains insufficient.

## Mandatory sequence

```text
S5 persist human O/S confirmation
-> S6 extract all neutral ownership rows and document dispositions
-> S6A normalize dates, issuer name, CUSIP and actual security-class title
-> S6B extract explicit Class A/Class B holder components
-> S7 canonicalize holders and resolve joint/aggregate/direct-indirect overlaps
-> S7A reconcile proxy totals to class-specific components exactly
-> S8 calculate candidate daily owner-exclusion float
-> S9 emit every float transition for human review
```

Any unresolved class allocation, role, overlap, date or later relevant event
must produce NULL float rather than a guessed value.

## Expected bounded outputs

```text
ownership_document_disposition.parquet
ownership_source_observations.parquet
holder_position_ledger_broad.parquet
holder_position_ledger_class_a.parquet
ownership_class_reconciliation.json
holder_deduplication.json
ownership_source_coverage.json
daily_float_state.parquet
float_change_explanation.parquet
variable_audit.json
final_manifest.json
```

## Path migration note

New active work resolves heavy Data Foundation data through `G:/TSIS/data`.
Historical manifests that record `E:/TSIS/data` remain immutable provenance;
they are not evidence that a second physical dataset is required.

## Non-goals

- freely tradable float;
- 13F institutional ownership;
- canonical promotion;
- another ticker;
- network access;
- rewriting historical runs or their `E:` provenance.
## Parent-universe automation requirement

PGAC is evidence for a production-equivalent probe, not a permitted code
special case. The implementation must be parameterized for the 4,824-instrument
parent universe.

The following are prohibited in production logic:

- ticker-specific numeric constants;
- accession-specific arithmetic;
- holder-name exceptions that alter economic meaning;
- manually supplied float values;
- treating an unresolved class allocation as zero;
- maintaining one parser or resolver per ticker.

The same code, schemas, event types and policies must process every instrument.
Ticker-specific facts may enter only as extracted, hashed source observations
or governed configuration/identity inputs. PGAC values such as 244,250 must be
derived from its documents and exact reconciliation, never embedded in code.

The scale sequence is:

1. production-equivalent PGAC probe;
2. stratified difficult multi-ticker probes using the same implementation;
3. one bounded probe per planned execution shard;
4. variable-by-variable certification;
5. governed authorization for the 4,824-instrument materialization.

Automation includes explicit unresolved outcomes. A generic resolver that emits
a reproducible NULL plus blocker is valid; a ticker-specific guessed value is
not.
## Bounded execution outcome

Status: S6_S8_COMPLETE_S9_HUMAN_CONFIRMATION_PENDING

The preserved first run
sec_pit_pgac_owner_exclusion_v0_1_20260811T1500Z failed closed on issuer-name
continuity. A generic linguistic parser correction was tested without PGAC
constants. The successful immutable rerun
sec_pit_pgac_owner_exclusion_v0_2_20260811T1530Z then produced:

    ownership documents processed            47/47
    daily PIT rows                           140/140
    future-baseline rows                       0
    supported Class A exclusions         244,250
    owner-exclusion float               8,625,000
    float percent                       97.24610311

The evidence readout is
01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/sec_pit/SEC_PIT_PGAC_OWNERSHIP_AND_OWNER_EXCLUSION_PROBE_READOUT_v0_1.md.

This completes only the PGAC production-equivalent probe. S9 human
confirmation, stratified difficult-ticker replay, one probe per execution shard
and variable certification remain mandatory before the 4,824-instrument
materialization can be authorized.
