# SEC PIT Seven-Ticker Lifecycle Extraction and Market Reconciliation Readout v0_2

## Artifact control

~~~text
document_status             = EXECUTED
metadata_run                = sec_pit_7t_lifecycle_v0_2
acquisition_run             = sec_pit_7t_lifecycle_primary_v0_1
extraction_run              = sec_pit_7t_lifecycle_extract_v0_2
market_presence_run         = sec_pit_7t_lifecycle_market_presence_v0_2
overall_status              = PASS_WITH_RESTRICTIONS
legal_lifecycle_resolution  = NOT_COMPLETE
canonical_promotion         = NOT_AUTHORIZED
parent_universe_scale       = NOT_AUTHORIZED
~~~

## Corrections discovered by first-output audit

The first extraction output was not accepted.

~~~text
sec_pit_7t_lifecycle_v0_1
= SUPERSEDED_IDENTITY_INTERVAL_DEFECT

sec_pit_7t_lifecycle_extract_v0_1
= QUARANTINED_FALSE_POSITIVE_CLASSIFICATION_AND_IDENTITY_DEFECT

sec_pit_7t_lifecycle_market_presence_v0_1
= SUPERSEDED_INCOMPLETE_CROSS_SOURCE_QUALITY
~~~

Defects:

1. BBBY ticker reuse was initially aggregated across old and current identities.
2. The standard Item 3.01 heading caused false transfer/delisting/regained labels.
3. Daily/tape boundary differences were initially not exposed as a quality state.

Non-destructive supersession sidecars prohibit downstream use of those runs.

## Corrected identity gate

BBBY now resolves as:

~~~text
ticker-history first snapshot = 2016-10-25
current target identity first = 2025-09-01
current target identity last  = 2026-03-09
~~~

The 2023 Overstock transfer and Form 25 observations are therefore correctly
classified as PRE_OBSERVED_TARGET_INTERVAL for the current BBBY identity.

## Extraction v0_2

~~~text
source observations                       = 50
security/class/exchange mentions           = 44
registration observations                 = 12
Form 25 observations                      = 2
Item 3.01 observations                    = 36
Item 3.01 sections found                  = 36 / 36
pre-observed-target-interval filings       = 38
within/after observed target interval      = 12
target ticker explicitly mentioned         = 8
other/predecessor ticker mentioned         = 8
trading symbol not extracted               = 34
~~~

Hard-gate results:

~~~text
duplicate observations         = 0
missing source hashes          = 0
missing evidence snippets      = 0
CNOBP observations             = 0
event_effective_at populated   = 0
first_trade_at populated       = 0
last_trade_at populated        = 0
~~~

Representative corrected cases:

~~~text
BBBY 2023 Item 3.01
= LISTING_TRANSFER + VOLUNTARY_WITHDRAWAL
= OSTK predecessor evidence
= PRE_OBSERVED_TARGET_INTERVAL

BBBY 2023 Form 25
= OVERSTOCK.COM, INC.
= Common Stock
= PRE_OBSERVED_TARGET_INTERVAL

BNAI 2024 Form 25
= Brand Engagement Network Inc.
= Unit
= rule 12d2-2(a)(3)
= class reconciliation still required

DOMH 2020 Item 3.01
= CONTINUED_LISTING_NONCOMPLIANCE_NOTICE
= not a delisting event
= predecessor ticker evidence
~~~

## Market-presence reconciliation v0_2

All reads used canonical physical roots on G:.

~~~text
daily source:
G:/TSIS/data/ohlcv_daily

trade source:
G:/TSIS/data/trades_ticks_prod_2005_2026
~~~

Results:

| Ticker | Identity window | Daily bounds | Tape bounds | Quality |
|---|---|---|---|---|
| ALUR | 2023-08-02 to 2026-03-04 | 2023-08-02 to 2026-03-04 | unavailable | daily only |
| BBBY | 2025-09-01 to 2026-03-09 | 2025-09-02 to 2026-03-06 | 2025-09-02 to 2026-03-06 | daily/tape agree by date |
| BGM | 2024-08-12 to 2026-03-09 | 2024-08-12 to 2026-03-06 | 2024-08-12 to 2026-03-06 | daily/tape agree by date |
| BNAI | 2024-03-15 to 2026-03-09 | 2024-03-15 to 2026-03-06 | 2024-03-18 to 2026-03-06 | boundary difference |
| DOMH | 2022-12-22 to 2026-03-09 | 2022-12-22 to 2026-03-06 | unavailable | daily only |
| PGAC | 2025-08-11 to 2026-03-09 | 2025-08-15 to 2026-03-06 | 2025-08-11 to 2026-03-06 | boundary difference |

~~~text
daily bounds observed             = 6 / 6
tape bounds observed              = 4 / 6
tape unavailable                  = 2 / 6
daily/tape boundary differences   = 2
legal list dates populated        = 0
legal delist dates populated      = 0
~~~

Tape timestamps are retained as source-naive and require a separate timezone
contract review before any UTC field can be published.

## Output locations

~~~text
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_v0_2

D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_extract_v0_2

D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_market_presence_v0_2
~~~

Main tables:

~~~text
lifecycle_source_observations.parquet
lifecycle_security_mentions.parquet
lifecycle_market_presence_bounds.parquet
~~~

## Validation

~~~text
full explicit SEC PIT suite = 90 PASS
ruff = PASS
py_compile = PASS
git diff check = PASS
~~~

## Current scientific verdict

The regulatory evidence has been acquired, extracted and reconciled against
bounded market presence for the six passing cases. The result is suitable as
experimental lifecycle evidence.

It is not yet a canonical lifecycle table because:

~~~text
affected security class remains unresolved for many filings
34 filings have no extracted trading symbol
ALUR and DOMH tape is unavailable on G:
BNAI and PGAC have daily/tape boundary differences
source-naive tape timezone is not frozen
legal list/delist dates remain unproved
~~~

The next gate is targeted human/fixture review of the 12 filings within or after
the observed target interval, followed by an identity-interval candidate ledger.
No parent-universe replay is authorized yet.