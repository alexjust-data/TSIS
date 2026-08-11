# SEC PIT PGAC no-network O/S probe readout v0_1

Status: `EVIDENCE_READY_HUMAN_CONFIRMATION_PENDING`

Date: `2026-08-11`

Run ID: `sec_pit_pgac_no_network_os_v0_2_20260811T1145Z`

## Decision

The bounded PGAC probe passed automated stages S0 through S4. It reconstructed
a causal daily Class A shares-outstanding state from already acquired SEC
primary documents. No network request was authorized or made. This is not an
authorization to scale to another ticker, and it does not resolve owner
exclusions, tradability or institutional ownership.

```text
S0 schema and units                     PASS
S1 accession-to-instrument admission    PASS_WITH_RESTRICTIONS
S2 class-specific O/S extraction        PASS_DUAL_EXTRACTION
S3 O/S anchor reconciliation            PASS_WITH_RESTRICTIONS
S4 daily O/S PIT state                   PASS
S5 manual change audit                   HUMAN_CONFIRMATION_PENDING
S6-S9 ownership and float                NOT_EXECUTED
```

## Frozen scope

```text
ticker                                  PGAC
instrument_id                           cik_ticker:0002030829:PGAC
registrant                              Pantages Capital Acquisition Corporation
target class                            Class A ordinary shares
selection-plan SHA-256                  ddce5a64826268ceb4f36d34476eba03d879c9a47c6a94d634a7af74823bb998
selected O/S candidate documents        14
target-interval documents               3
prehistoric candidates rejected         9
post-interval candidates rejected       2
network requests                        0
```

The target filings were admitted only when the filing itself identified both
the registrant and the Nasdaq trading table for ticker `PGAC`, Class A ordinary
shares. The nine prehistory records were not assigned to PGAC because they can
represent AIFE or multiple instruments. The two post-interval records were not
used to alter the target interval.

## Source observations and admitted anchors

Each admitted value was extracted twice from the same immutable primary
document: once from class-specific cover text and once from inline XBRL with
class context. Exact agreement was required.

| Accession | Form | Measurement date | SEC accepted at | Eligible session | Class A O/S |
|---|---:|---:|---:|---:|---:|
| `0001213900-25-075873` | 10-Q | 2025-08-13 | 2025-08-13 22:20:04Z | 2025-08-14 | 8,869,250 |
| `0001213900-25-108205` | 10-Q | 2025-11-10 | 2025-11-10 21:06:18Z | 2025-11-11 | 8,869,250 |
| `0001213900-26-024889` | 10-K | 2026-03-02 | 2026-03-07 02:31:23Z | 2026-03-09 | 8,869,250 |

Result:

```text
raw observations                        6
candidate reconciliation groups         3
admitted O/S anchors                    3
unadmitted reconciliation groups        0
distinct admitted O/S values            1
```

The two extraction paths reduce parser risk but are not independent economic
sources. For that reason S3 remains `PASS_WITH_RESTRICTIONS`.

## Daily PIT result

The series uses the canonical market calendar and the observed PGAC market
presence interval `2025-08-15` through `2026-03-06`.

```text
daily rows                               140
unique sessions                          140
non-NULL O/S rows                        140
distinct daily O/S values                1
daily Class A O/S                        8,869,250
rows using future anchors                0
causality state                          PIT_VALID
```

There are two anchor-vintage explanations within the observed window:

1. `2025-08-15`: initial admitted anchor from accession
   `0001213900-25-075873`, eligible from `2025-08-14`.
2. `2025-11-11`: admitted anchor changes to accession
   `0001213900-25-108205`; the value remains `8,869,250`.

The third anchor is valid and admitted but becomes eligible on `2026-03-09`,
after the final observed market-presence session `2026-03-06`; it therefore
does not enter this daily series.

## S0 unit correction

The resolved-daily-state schema is now `sec_pit_resolved_daily_states_v0_2`:

```text
float_fraction_estimate_as_known         0.0 to 1.0
float_percent_estimate_as_known          0.0 to 100.0
```

Non-positive shares outstanding block float calculation. Historical v0_1
outputs are not rewritten silently.

## Verification

```text
focused automated tests                  24 PASS
full test_sec_pit_*.py suite             120 PASS
compile checks                           PASS
selection hash gate                      PASS
source byte/hash verification            PASS for 3/3 target objects
acceptance timestamps resolved locally   6/6 observations
daily uniqueness                         PASS
future-anchor leakage                    0 rows
```

## Restrictions and next gate

- `security_class_id` remains physically NULL; the governed identity gate and
  filing-level registrant/ticker/class evidence identify the target class, but
  a canonical class ID has not yet been materialized.
- A human must confirm the three accession admissions and the two in-window
  anchor-vintage explanations before S5 can be marked PASS.
- This probe resolves only Class A shares outstanding. It does not calculate
  owner-exclusion float, tradable float or 13F institutional ownership.
- The next technical stage after S5 is the PGAC holder event ledger and
  ownership deduplication, still using the 68 local documents and no new
  acquisition.

## Evidence paths

```text
C:/TSIS_Data/runtime/sec_pit_pgac_no_network_v0_1/runs/sec_pit_pgac_no_network_os_v0_2_20260811T1145Z/
  pre_manifest.json
  accession_instrument_admission.parquet
  os_source_observations.parquet
  admitted_os_anchors.parquet
  daily_os_state.parquet
  os_change_explanation.parquet
  os_anchor_reconciliation.json
  variable_audit.json
  final_manifest.json
```

The earlier `sec_pit_pgac_no_network_os_v0_1_20260811T1115Z` run remains
preserved as the first blocked probe. The intermediate
`sec_pit_pgac_no_network_os_v0_2_20260811T1130Z` attempt remains preserved as a
failed implementation run caused by a readout-key mismatch; it is not an
authoritative result.

