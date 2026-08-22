# SEC PIT Seven-Ticker Lifecycle Coverage Readout v0_1

## Artifact control

```text
document_status                  = EXECUTED
physical_source                  = G:/TSIS/data/reference/all_tickers
snapshot_count                   = 3,109
snapshot_period                  = 2005-01-02 to 2026-03-09
exact_lifecycle_contract_found   = NO
current-ticker coverage result   = PASS_WITH_RESTRICTIONS
issuer-history coverage result   = NOT_DETERMINED
```

## Authority finding

No current C: contract defines exact per-ticker listing and delisting windows for
the 4,821-instrument parent universe.

The closest active contracts are:

```text
01_foundations/contract_registry/dataset_contracts/
  instrument_master_dataset_contract_v0_1.md

01_foundations/canonical_schemas/outputs/
  instrument_master_schema_contract.md
```

They explicitly define:

```text
valid_from = lt1b_first_seen_date
valid_to   = lt1b_last_observed_date
```

These fields delimit observed operational LT1B membership. They are not listing
or delisting dates, and instrument_master v0_1 explicitly states that it is not
a final lifecycle engine.

The reference audit contract identifies the appropriate raw authority:

```text
01_research/01_auditoria_RAW_DATA/00_data_certification/
  auditoria/reference/01_contrato_reference.md
```

Its `listing_snapshot` grain is `ticker + snapshot_date`, sourced from
`G:/TSIS/data/reference/all_tickers`. The physical source contains 3,109
snapshots from 2005-01-02 through 2026-03-09.

`overview.list_date` is useful context but cannot be treated as the exact start
of the current ticker identity. It can describe the issuer/security lineage and
can predate ticker reuse or ticker changes. Examples include DOMH=1973-01-02 and
the current BBBY CIK=0001130713 with overview list_date=2002-05-30.

## Current-ticker observed intervals and SEC selection

| Ticker | Current identity evidence | First observed ticker snapshot | Last observed snapshot | Active at last snapshot | Selected SEC date range | Covers observed ticker interval |
|---|---|---:|---:|---|---|---|
| BNAI | CIK 0001838163 / FIGI BBG00Z83ZBP7 | 2024-03-15 | 2026-03-09 | yes | 2021-02-09 to 2026-07-27 | yes |
| DOMH | CIK 0000012239 / FIGI BBG001S9BVW1 | 2022-12-22 | 2026-03-09 | yes | 2016-08-08 to 2026-07-28 | yes |
| BBBY | CIK 0001130713 / FIGI BBG001S64TS5 | 2025-09-01 | 2026-03-09 | yes | 2018-12-28 to 2026-08-07 | yes |
| BGM | CIK 0001779578 | 2024-08-12 | 2026-03-09 | yes | 2019-11-04 to 2026-07-30 | yes |
| CNOBP | CIK 0000712771, class conflict | 2023-05-07 | 2026-03-09 | yes | 2018-09-04 to 2026-08-04 | yes, but wrong-class gate unresolved |
| ALUR | FIGI BBG01HPVRLV5 | 2023-08-02 | 2026-03-04 | yes | 2023-07-07 to 2026-07-24 | yes |
| PGAC | CIK 0002030829 | 2025-08-11 | 2026-03-09 | yes | 2024-07-24 to 2026-08-06 | yes |

All seven selected SEC ranges cover the currently observed ticker interval. The
fixed 300-document cap therefore has not been shown to remove the current ticker
life in this sample.

## BBBY ticker reuse evidence

The same ticker is not one continuous economic identity:

```text
2016-10-25 to 2023-05-02
CIK 0000886158 / FIGI BBG001S720V4
Bed Bath & Beyond Inc

2025-09-01 to 2026-03-09
CIK 0001130713 / FIGI BBG001S64TS5
Bed Bath & Beyond, Inc.
```

Therefore a ticker-level first/last date cannot govern SEC acquisition by
itself. The lifecycle grain must be an identity interval, preferably
`instrument_id/share-class + ticker + CIK + effective interval`.

## Remaining restrictions

```text
CURRENT TICKER INTERVAL COVERAGE
= PASS_WITH_RESTRICTIONS

EXACT LISTING/DELISTING COVERAGE
= NOT PROVABLE FROM CURRENT CONTRACTS

ISSUER PREHISTORY REQUIRED FOR O/S/FLOAT
= NOT YET DEFINED

TICKER REUSE / IDENTITY CONTINUITY
= REQUIRES LIFECYCLE RESOLVER

CNOBP SECURITY CLASS
= BLOCKING SOURCE CONFLICT
```

The physical replay must not be rejected merely because the 300 cap omits old
CIK history. It must instead prove that omitted history is or is not required
for the opening O/S/ownership state at the first target cutoff.

## Required lifecycle output

TSIS still needs a governed table with grain:

```text
instrument_identity_interval
```

and fields at minimum:

```text
instrument_id
security_class_id
ticker
cik
share_class_figi
effective_from
effective_to
list_date
delist_date
first_observed_snapshot
last_observed_snapshot
active_state
predecessor_identity
successor_identity
source
quality_state
```

Until that table exists, `all_tickers` snapshots are the best observed-presence
evidence, while exact listing/delisting claims remain restricted.

## Lifecycle metadata lane execution - 2026-08-10

The dedicated metadata lane has now been executed under
sec_pit_lifecycle_source_selection_policy_v0_1.

~~~text
run_id                       = sec_pit_7t_lifecycle_v0_1
candidate rows               = 52
registration candidates      = 14
Form 25 candidates           = 2
Item 3.01 candidates         = 36
security-class PASS / FAIL   = 6 / 1
metadata lane                = PASS_WITH_RESTRICTIONS
primary extraction           = NOT_EXECUTED
first/last trade resolution  = NOT_EXECUTED
~~~

This supplements observed ticker intervals with regulatory source candidates;
it does not replace market-presence evidence. See
SEC_PIT_SEVEN_TICKER_LIFECYCLE_METADATA_LANE_READOUT_v0_1.md.