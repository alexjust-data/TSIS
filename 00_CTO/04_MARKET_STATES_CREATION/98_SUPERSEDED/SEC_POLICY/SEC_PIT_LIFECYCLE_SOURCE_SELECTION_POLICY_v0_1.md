# SEC PIT Lifecycle Source Selection Policy v0_1

## Artifact control

~~~text
document_status              = EXECUTED_AS_EXPERIMENTAL_POLICY
policy_id                    = sec_pit_lifecycle_source_selection_policy_v0_1
implementation_status        = TESTED
metadata_lane_gate           = PASS_WITH_RESTRICTIONS
primary_document_gate        = NOT_EXECUTED
first_last_trade_gate        = NOT_EXECUTED
canonical_promotion          = NOT_AUTHORIZED
parent_universe_scale        = NOT_AUTHORIZED
~~~

## Purpose

Add a dedicated regulatory lifecycle evidence lane before the seven-ticker
physical replay. This lane prevents SEC issuer history from being treated as one
continuous listed security and prevents a filing date from being promoted
directly to a market-trading boundary.

## Candidate sources

~~~text
8-A, 8-A/A, 8-A12B, 8-A12B/A, 8-A12G, 8-A12G/A
-> REGISTRATION_FILING_CANDIDATE

25, 25-NSE
-> FORM_25_FILING_CANDIDATE

8-K or 8-K/A containing Item 3.01
-> ITEM_3_01_DISCLOSURE_CANDIDATE
~~~

These are source candidates, not resolved lifecycle events.

## Prohibited inference

~~~text
8-A acceptance date
!= first trade date

Form 25 filing/effective date
!= last trade date

8-K Item 3.01
!= automatic delisting date

issuer CIK history
!= one continuous ticker/share-class history
~~~

Primary-document extraction must identify the security class, exchange,
effective date, conditions, predecessor/successor context and affected ticker.
Actual first/last trading boundaries require governed market-presence evidence.

## Hard gates

~~~text
G-L0 METADATA OBSERVABILITY
candidate form/item is present in SEC submissions metadata

G-L1 SECURITY CLASS
candidate belongs to the intended common-stock share class

G-L2 IDENTITY
CIK, ticker interval and share-class identity are reconciled

G-L3 PRIMARY DOCUMENT
affected security, event semantics and effective date are extracted

G-L4 MARKET PRESENCE
first/last observed trade or governed market presence is reconciled

G-L5 PIT AVAILABILITY
the event may be consumed only from its governed eligible session

G-L6 PROMOTION
no lifecycle row becomes canonical before all required gates pass
~~~

## Physical bindings

~~~text
policy config:
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/configs/
sec_pit_lifecycle_source_selection_policy_v0_1.json

classification:
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/metadata.py

metadata auditor:
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/scripts/sec_pit/
audit_lifecycle_metadata_lane.py

executed evidence:
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_7t_lifecycle_v0_1
~~~

## Current decision

The metadata lane is admitted only as an experimental acquisition selector.
It authorizes preparation of a lifecycle-only primary-document forecast for the
six passing cases. It does not authorize the former broad 1,595-document replay,
parent-universe scale-out or lifecycle promotion.