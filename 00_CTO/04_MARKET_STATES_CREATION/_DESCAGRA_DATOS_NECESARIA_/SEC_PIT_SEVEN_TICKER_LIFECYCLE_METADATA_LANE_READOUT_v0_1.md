# SEC PIT Seven-Ticker Lifecycle Metadata Lane Readout v0_1

## Artifact control

~~~text
document_status              = EXECUTED
run_id                       = sec_pit_7t_lifecycle_v0_1
run_status                   = COMPLETE
lifecycle_metadata_lane_gate = PASS_WITH_RESTRICTIONS
primary_document_acquisition = NOT_EXECUTED
first_last_trade_resolution  = NOT_EXECUTED
promotion_status             = NOT_AUTHORIZED
~~~

## Executed inputs

~~~text
SEC filing metadata:
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
sec_pit_7t_metadata_v0_2__<ticker>/filing_inventory.parquet

governed ticker snapshots:
G:/TSIS/data/reference/all_tickers/*.parquet

frozen cases:
BNAI, DOMH, BBBY, BGM, CNOBP, ALUR, PGAC
~~~

No primary filing, complete submission or exhibit was downloaded by this run.

## Results

~~~text
candidate rows                 = 52
registration candidates        = 14
Form 25 / 25-NSE candidates    = 2
8-K Item 3.01 candidates       = 36
security-class PASS            = 6
security-class FAIL            = 1
negative-control behavior      = PASS
duplicate ticker/accession     = 0
resolved lifecycle events      = 0
~~~

| Ticker | Registration | Form 25 | Item 3.01 | Total | Security class | Next state |
|---|---:|---:|---:|---:|---|---|
| ALUR | 1 | 0 | 4 | 5 | PASS | eligible for lifecycle-only document selection |
| BBBY | 3 | 1 | 4 | 8 | PASS | identity restrictions remain |
| BGM | 1 | 0 | 0 | 1 | PASS | eligible for lifecycle-only document selection |
| BNAI | 1 | 1 | 7 | 9 | PASS | eligible for lifecycle-only document selection |
| CNOBP | 2 | 0 | 0 | 2 | FAIL | halt before deep acquisition |
| DOMH | 5 | 0 | 21 | 26 | PASS | eligible for lifecycle-only document selection |
| PGAC | 1 | 0 | 0 | 1 | PASS | eligible for lifecycle-only document selection |

CNOBP fails because the reference common-stock flag conflicts with a security
name describing depositary shares representing preferred stock. One CNOBP
8-A12G candidate from 1996 lacks a primary-document URL; this does not weaken
the halt because CNOBP is prohibited from deep acquisition under the current
class gate.

## Interpretation

Every ledger row intentionally remains:

~~~text
event_resolution_state = REQUIRES_PRIMARY_DOCUMENT_EXTRACTION
event_effective_at      = NULL
event_type              = NULL
~~~

The run proves metadata observability and candidate selection only. It does not
prove the affected class, listing venue, effective event, first trade or last
trade.

## Validation

~~~text
ruff focused checks          = PASS
python compilation           = PASS
focused lifecycle tests      = 7 PASS
explicit SEC PIT suite        = 78 PASS
ledger duplicate check       = PASS
negative control             = PASS
full tests directory attempt = BLOCKED_BY_UNRELATED_IMPORT_COLLECTION
~~~

The broad tests-directory command was blocked during collection by the existing
test_ohlcv_1m_quote_guarded.py import environment (src not on module path).
The SEC PIT suite was therefore rerun from an explicit file list and all 78 tests passed. The unrelated full-directory import environment remains a separate test-harness gap.

## Next authorized action

~~~text
1. Build lifecycle-only primary-document acquisition plan for six PASS cases.
2. Produce exact candidate count and byte forecast.
3. Audit identity/class/date extraction fixtures.
4. Request explicit authorization before network acquisition.
5. Reconcile extracted regulatory events with governed market presence.
~~~

The previous broad physical seven-ticker replay remains unauthorized.

## Lifecycle-only acquisition forecast

A deterministic post-run filter retained only candidates whose ticker passed the
security-class gate and whose primary-document URL is present.

~~~text
planned primary documents       = 50
known filing-size values        = 50
SEC filing-size upper ceiling   = 5,774,253 bytes
SEC filing-size upper ceiling   = 5.507 MiB

ALUR = 5 documents
BBBY = 8 documents
BGM  = 1 document
BNAI = 9 documents
DOMH = 26 documents
PGAC = 1 document
CNOBP = 0 documents (halted)
~~~

This is a metadata filing-size ceiling, not an observed download size. It is
small enough that disk capacity is not the blocker; source semantics and
identity extraction remain the controlling gates.

## Primary acquisition completed - 2026-08-10

The lifecycle-only physical acquisition has now completed under
sec_pit_7t_lifecycle_primary_v0_1.

~~~text
planned / fetched / failed = 50 / 50 / 0
actual response bytes      = 1,300,708
byte-level audit           = PASS
complete submissions       = 0
exhibits                   = 0
~~~

This supersedes the prior NOT_EXECUTED state for acquisition only. Primary
extraction, event resolution and first/last trade resolution remain NOT_EXECUTED.
See SEC_PIT_SEVEN_TICKER_LIFECYCLE_PRIMARY_ACQUISITION_READOUT_v0_1.md.