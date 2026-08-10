# SEC PIT Lifecycle Source Selection Policy v0_2

## Artifact control

~~~text
document_status              = EXECUTED
policy_id                    = sec_pit_lifecycle_source_selection_policy_v0_2
metadata_run                 = sec_pit_7t_lifecycle_v0_2
metadata_lane_gate           = PASS_WITH_RESTRICTIONS
primary_acquisition_run      = sec_pit_7t_lifecycle_primary_v0_1
primary_extraction_run       = sec_pit_7t_lifecycle_extract_v0_2
market_presence_run          = sec_pit_7t_lifecycle_market_presence_v0_2
canonical_promotion          = NOT_AUTHORIZED
parent_universe_scale        = NOT_AUTHORIZED
~~~

## v0_2 correction

v0_1 computed the first/last snapshot over every historical identity that reused
a ticker. This mixed old BBBY and current BBBY identities. v0_2 resolves the
target snapshot interval by:

~~~text
share_class_figi when available
else CIK
within the ticker snapshot history
~~~

It also requires Item 3.01 classification from the filing narrative rather than
from words present only in the standard heading.

## Candidate sources

~~~text
8-A family      -> registration source candidate
25 / 25-NSE     -> removal-notification source candidate
8-K Item 3.01   -> listing-compliance/transfer source candidate
~~~

Candidate is not resolved event.

## Mandatory boundaries

~~~text
SEC filing evidence
!= first or last trade

daily market observation
!= legal listing or delisting date

trade-tape observation
!= complete market lifecycle

ticker string
!= stable economic identity
~~~

The active outputs must preserve source availability, identity interval,
security-class mentions, market bounds, missing tape and cross-source
differences. Legal lifecycle dates remain NULL until separately demonstrated.