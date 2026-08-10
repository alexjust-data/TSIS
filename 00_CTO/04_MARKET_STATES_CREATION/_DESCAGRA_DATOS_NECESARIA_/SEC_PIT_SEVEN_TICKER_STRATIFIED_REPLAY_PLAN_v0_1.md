# SEC PIT Seven-Ticker Stratified Replay Plan v0_1

## Artifact control

```text
document_status       = METADATA_PREFLIGHT_EXECUTED
execution_status      = BLOCKED_BY_DOCUMENT_SELECTION_GATE
canonical_promotion   = NOT_AUTHORIZED
parent_universe_scale = NOT_AUTHORIZED
```

## Purpose

Validate the SEC PIT acquisition and resolution pipeline on seven deliberately
heterogeneous cases before any scale-out toward the 4,821-instrument parent
universe. This supersedes the proposed 50-ticker replay size; it does not erase
the earlier 50-ticker raw-download evidence.

## Frozen cases

| Ticker | CIK | Stratum |
|---|---:|---|
| `BNAI` | `0001838163` | modern XBRL benchmark |
| `DOMH` | `0000012239` | pre-XBRL and identity stress |
| `BBBY` | `0001130713` | lifecycle and ticker-change stress |
| `BGM` | `0001779578` | foreign issuer |
| `CNOBP` | `0000712771` | non-common equity negative control |
| `ALUR` | `0001964979` | OTC and security-type review |
| `PGAC` | `0002030829` | SPAC and foreign-identity stress |

Together these cases cover every major selection tag present in the previous
pilot: modern benchmark, pre-XBRL, multi-row CIK, duplicate identity, ticker
changes, foreign/ordinary shares, missing class FIGI, missing overview O/S,
SPAC/acquisition, OTC and non-common negative control.

## Acquisition policy

```text
metadata                = acquire and retain
companyfacts            = acquire and retain
selected primary docs   = acquire, maximum 300 per case
complete submissions    = prohibited by default
exhibits                 = prohibited by default
content store           = shared and SHA-256 deduplicated
concurrency              = one ticker at a time
output                   = D:/TSIS/fundamental_context/sec_pit_v0_1
```

The previous raw holdings for these cases occupy approximately `3.53 GiB`, but
they were produced by a broad `primary + complete` policy. They are forensic
evidence, not the storage forecast for this replay.

## Safety and recovery

- Preflight refuses execution below `100 GiB` free on the output volume.
- Free space is checked again before every ticker.
- A low-space event pauses before the next ticker with `PAUSED_LOW_DISK`.
- Each ticker is an isolated child run with immutable content-addressed objects.
- Resume skips child runs whose final manifest is `COMPLETE`.
- A power loss can lose only the active HTTP/object operation; completed child
  runs and content objects remain reusable.
- Moving to another disk requires a stopped run, verified object copy and a new
  versioned output-root binding. The root must never change silently mid-run.

## Execution sequence

```text
P0 plan-only replay
P1 inspect acquisition plans and identity resolution
P2 estimate selected-document count and bytes
P3 human-authorized physical replay
P4 audit G0-G16 per ticker and across strata
P5 storage/runtime readout
P6 decide whether another pilot is required
P7 only then consider parent-universe scale-out
```

## Commands

Plan-only preflight:

```powershell
python C:\TSIS_Data\01_TSIS_DATA_FOUNDATION\scripts\sec_pit\run_seven_ticker_replay.py --run-id sec_pit_7t_plan_v0_1
```

Physical execution is intentionally not authorized by this document alone.
Before launch, the human must receive an updated byte/time estimate, exact
command, monitor command and stop/resume instructions.

## Executed metadata preflight

Authoritative run:

```text
run_id                       = sec_pit_7t_metadata_v0_2
status                       = COMPLETE
cases                        = 7 / 7
filings inventoried          = 6,371
primary documents selected   = 1,595
filing-size upper bound      = 3.012 GiB
primary documents acquired   = 0
complete submissions         = 0
exhibits                     = 0
content store physical size  = 10.54 MiB
```

The `3.012 GiB` figure is deliberately conservative: it sums SEC filing-size
metadata for selected accessions, not the smaller primary-document response
size. It is a capacity ceiling for the next decision, not a promised download
size.

The earlier `sec_pit_7t_metadata_v0_1` completed identity and selection but
bound the forecast to a non-existent `size` field and therefore emitted zero
bytes. It is retained as non-authoritative diagnostic evidence. `v0_2` binds
the physical schema field `filing_size_bytes` and is the current forecast.

## Document-selection audit

The physical replay remains unauthorized. The fixed cap covers the observed current-ticker intervals in this sample, but the broad selection still fails policy, class and issuer-prehistory sufficiency gates. The dedicated lifecycle metadata lane now passes with restrictions; primary lifecycle extraction and the broader replay remain unexecuted.


## Lifecycle metadata prerequisite executed

~~~text
run_id                       = sec_pit_7t_lifecycle_v0_1
metadata lifecycle gate      = PASS_WITH_RESTRICTIONS
deep-acquisition candidates  = 6 cases
security-class halt          = CNOBP
primary documents acquired   = 0
~~~

The next replay step is not the former 1,595-document download. It is a
lifecycle-only acquisition plan and byte forecast, followed by explicit human
authorization.

## Lifecycle-only primary acquisition executed

~~~text
run_id                 = sec_pit_7t_lifecycle_primary_v0_1
documents              = 50 / 50
audit                  = PASS
actual response bytes  = 1,300,708
~~~

The lifecycle primary source prerequisite is now physically complete. This does
not authorize the former broad replay. The next gate is primary-document
lifecycle extraction followed by market-presence reconciliation.