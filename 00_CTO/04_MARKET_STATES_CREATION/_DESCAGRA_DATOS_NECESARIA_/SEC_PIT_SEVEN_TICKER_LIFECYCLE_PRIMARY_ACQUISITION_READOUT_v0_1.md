# SEC PIT Seven-Ticker Lifecycle Primary Acquisition Readout v0_1

## Artifact control

~~~text
document_status              = EXECUTED
run_id                       = sec_pit_7t_lifecycle_primary_v0_1
run_status                   = COMPLETE
acquisition_audit            = PASS
source_selection_gate        = PASS_WITH_RESTRICTIONS
primary_document_extraction  = NOT_EXECUTED
lifecycle_event_resolution   = NOT_EXECUTED
first_last_trade_resolution  = NOT_EXECUTED
canonical_promotion          = NOT_AUTHORIZED
parent_universe_scale        = NOT_AUTHORIZED
~~~

## Executed scope

The acquisition consumed only the lifecycle metadata ledger admitted by
sec_pit_7t_lifecycle_v0_1.

~~~text
planned documents                    = 50
fetched documents                    = 50
failed documents                     = 0
SEC filing-size planning ceiling     = 5,774,253 bytes
actual uncompressed response bytes   = 1,300,708
free space at launch                 = 901.513 GiB
complete submissions                 = 0
exhibits                             = 0
CNOBP documents                      = 0
~~~

No O/S, ownership, restriction or institutional document was selected merely
because it belonged to those other lanes.

## Acquired distribution

| Ticker | Documents |
|---|---:|
| ALUR | 5 |
| BBBY | 8 |
| BGM | 1 |
| BNAI | 9 |
| DOMH | 26 |
| PGAC | 1 |
| CNOBP | 0 |

~~~text
registration primary documents = 12
Form 25 primary documents       = 2
Item 3.01 primary documents     = 36
~~~

The metadata ledger contained 14 registration candidates. Two belonged to
CNOBP and were deliberately excluded by HALT_SECURITY_CLASS.

## Byte-level audit

~~~text
plan/result parity                 = PASS
missing result rows                = 0
duplicate ticker/accession rows    = 0
missing object files               = 0
unreadable compressed objects      = 0
SHA-256 mismatches                 = 0
byte-count mismatches              = 0
SEC error-page signatures          = 0
null object paths                  = 0
null hashes                        = 0
complete-submission paths          = 0
exhibit paths                      = 0
~~~

Audit artifact:

~~~text
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_primary_v0_1/
lifecycle_primary_acquisition_audit.json
~~~

## Physical implementation

~~~text
runner:
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/
run_lifecycle_primary_acquisition.py

auditor:
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/
audit_lifecycle_primary_acquisition.py

run root:
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_primary_v0_1

content-addressed objects:
D:/TSIS/fundamental_context/sec_pit_v0_1/objects
~~~

The run supports resume from acquisition.jsonl, refuses silent overwrite and
stores source-ledger and source-gate hashes in its pre-manifest.

## Validation

~~~text
focused runner tests = 2 PASS
focused lifecycle tests = 9 PASS
full explicit SEC PIT suite = 80 PASS
ruff = PASS
py_compile = PASS
git diff check = PASS
~~~

## Scientific interpretation

This run establishes that the required primary evidence was acquired intact. It
does not establish any lifecycle event.

Every candidate still requires extraction and reconciliation of:

~~~text
affected issuer and security class
ticker and exchange
event semantics
filing acceptance and eligible session
stated effective date
conditions and amendments
predecessor/successor identity
market-presence confirmation
~~~

The following inferences remain prohibited:

~~~text
8-A date = first trade date
Form 25 date = last trade date
Item 3.01 date = delisting date
CIK history = continuous security history
~~~

## Next action

Build and test the primary-document lifecycle extractor, beginning with fixtures
for BBBY ticker reuse, BNAI Form 25/predecessor context, DOMH Item 3.01 history
and the foreign/SPAC controls. Then reconcile extracted regulatory events with
G:/TSIS/data market-presence evidence before admitting identity intervals.

## Extraction and market reconciliation completed

The acquired documents were reused without another download.

~~~text
authoritative extraction = sec_pit_7t_lifecycle_extract_v0_2
market reconciliation    = sec_pit_7t_lifecycle_market_presence_v0_2
status                   = PASS_WITH_RESTRICTIONS
~~~

See SEC_PIT_SEVEN_TICKER_LIFECYCLE_EXTRACTION_AND_MARKET_RECONCILIATION_READOUT_v0_2.md.