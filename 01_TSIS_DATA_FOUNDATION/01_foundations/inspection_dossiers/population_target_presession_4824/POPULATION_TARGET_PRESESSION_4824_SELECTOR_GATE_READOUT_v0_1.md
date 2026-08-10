# POPULATION_TARGET_PRESESSION_4824_SELECTOR_GATE_READOUT_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_presession_4824_selector_gate_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_SELECTOR_GATE_READOUT` |
| `document_status` | `EXECUTED` |
| `g0_contract_gate` | `PASS` |
| `g1_daily_spine_gate` | `PASS_WITH_RESTRICTIONS` |
| `g2_shares_source_temporal_gate` | `PASS_WITH_RESTRICTIONS` |
| `g3_measure_ttl_reconciliation_gate` | `PASS_WITH_RESTRICTIONS` |
| `controlled_fixture_gate` | `PASS` |
| `controlled_probe_validation_gate` | `PASS` |
| `selector_gate` | `PASS_WITH_RESTRICTIONS` |
| `broad_experimental_materialization` | `AUTHORIZED` |
| `ta3_sample_freeze` | `PENDING_FULL_MATERIALIZATION_VALIDATION` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

## 1. Verdict

```text
POPULATION TARGET PRESESSION 4824 SELECTOR GATE
= PASS_WITH_RESTRICTIONS
```

The available physical sources are sufficient to materialize an experimental,
causal and denominator-preserving proxy selector inside the fixed 4,824-ticker
parent frame.

They are not sufficient to claim exact historical legal market cap, historical
float or complete historical US `<$100M` population coverage.

## 2. Authorized construct

```text
PRESSESSION_REFERENCE_PRICE
= prior eligible RTH close

SHARES_PROXY
= diluted weighted-average shares when available
  else basic weighted-average shares

AVAILABILITY
= source_as_of_date < session_date
  under DATE_ONLY_CONSERVATIVE_AVAILABILITY

TTL
= 180 calendar days

PRESSESSION_REFERENCE_MARKET_CAP_PROXY
= PRESSESSION_REFERENCE_PRICE x SHARES_PROXY
```

Membership is:

```text
0.50 <= PRESSESSION_REFERENCE_PRICE <= 20.00
AND
PRESSESSION_REFERENCE_MARKET_CAP_PROXY < 100,000,000
```

The numeric-pass state is named:

```text
ELIGIBLE_UNDER_DECLARED_PROXY
```

## 3. G0 contract result

G0 passed executable checks for:

```text
fixed parent universe = lt1b_universe_v0_1
parent ticker count = 4,824
cutoff = 04:00 America/New_York
strict availability operator
prior eligible RTH close semantics
inclusive price boundaries
strict market-cap threshold
S1/S2 measure candidates
TTL 90/180/365 sensitivity candidates
float as nonblocking context
non-claims and possible verdicts
```

## 4. G1 daily spine result

Full-history metrics:

```text
requested daily_raw rows        = 7,369,699
ticker count                    = 4,824
session range                   = 2005-01-03 through 2026-03-09
master_daily_id unique rows     = 7,369,699
ticker-session unique rows      = 7,369,699
exact parent identity joins     = 7,369,699
hard-invalid selected prices    = 0
```

Restriction discovered:

```text
instrument_id-session duplicate groups = 28,876
```

The current identity master can assign one `instrument_id` to multiple
contemporaneous tickers. Therefore:

```text
PROHIBITED GRAIN
= instrument_id x session_date

AUTHORIZED GRAIN
= instrument_id x ticker_as_of_session x session_date
```

Fundamental joins must require both `instrument_id` and ticker. This prevents
cross-ticker shares contamination in cases such as `HSON/STRR`.

## 5. G2 source and temporal result

```text
income statement rows                  = 242,886
positive basic rows                    = 242,857
positive diluted rows                  = 242,857
temporal identity match rows           = 195,996
admissible deduplicated observations   = 75,353
admissible instrument count            = 4,580
availability range                     = 2010-06-09 through 2026-03-09
same-date selected rows                = 0
```

The source provides filing-date availability at date resolution. It does not
provide exact historical intraday `available_at`. Same-date observations are
therefore excluded conservatively.

Historical sessions before source coverage remain in the denominator as
unavailable. They are not backfilled with current or retrospective values.

The recovered legacy panel remains reconciliation evidence only. For parent
tickers it contains 9,989,254 rows and uses diluted shares on all selected-share
rows; it is not the primary presession selector source.

## 6. G3 measure and TTL result

| TTL | Classifiable rows | Eligible S1 | Eligible S2 | Disagreements |
|---:|---:|---:|---:|---:|
| 90 | 2,644,045 | 1,189,774 | 1,199,483 | 9,915 |
| 180 | 3,106,545 | 1,417,316 | 1,428,915 | 11,871 |
| 365 | 3,261,280 | 1,494,582 | 1,506,489 | 12,179 |

The primary experimental proxy binding is preregistered as:

```text
S1_DILUTED_FIRST x SHARES_TTL_180D
```

S1 is conservative at the `<$100M` threshold when diluted exceeds basic. TTL
180 is the declared coverage/staleness compromise. Every other S1/S2 x TTL
combination remains sensitivity evidence.

## 7. Fixture gate

```text
pytest result = 5 passed
```

Covered behavior includes:

```text
strict same-date exclusion
latest prior-date selection
inclusive $0.50 and $20 boundaries
basic/diluted threshold disagreement
TTL staleness
missing shares
missing reference price
split review
shared instrument_id without cross-ticker contamination
denominator preservation
composite grain enforcement
```

## 8. Controlled probe

Probe sessions:

```text
2012-06-15
2016-06-15
2020-06-15
2024-06-14
2025-03-14
```

Probe accounting:

```text
requested rows                       = 8,911
output rows                          = 8,911
eligible under declared proxy        = 2,342
ineligible market-cap proxy          = 2,490
ineligible price                     = 2,185
stale shares proxy                   = 293
unavailable reference price          = 681
unavailable shares proxy             = 914
corporate-action review              = 6
```

Independent validation:

```text
21/21 checks PASS
five price bands present
four eligible market-cap bands present
cutoff 04:00 ET exact
strict shares cutoff exact
market-cap formula exact
shares source identity exact
hash and row accounting exact
```

## 9. Restrictions carried forward

Every output and downstream TA-3 sample must preserve:

```text
fixed_4824_parent_frame
prior_RTH_close_reference_price
weighted_average_shares_proxy
date_only_conservative_availability
S1_diluted_first_primary
TTL_180D_primary
explicit_unavailable_and_stale_states
composite_instrument_ticker_session_grain
no_historical_float_claim
no_exact_point_shares_claim
no_full_historical_US_lt100m_population_claim
```

Float remains supporting context and does not block TA-3.

## 10. Authorization

The following is now authorized:

```text
full experimental materialization
of population_target_presession_4824_candidate_v0_1
under S1_DILUTED_FIRST x SHARES_TTL_180D
```

The full run must comply with `LONG_RUNNING_OPERATIONS_CONTRACT.md`, write to a
new output root, preserve all requested rows, and pass the independent
validator before TA-3 sample freeze.

The following remains unauthorized:

```text
canonical dataset promotion
exact market-cap claims
historical float claims
silent replacement of existing scanner market-cap fields
TA-3 OOS opening
Trading Activity model admission
```

## 11. Evidence anchors

```text
full audit run
= population_target_presession_4824_full_audit_20260807T164922Z

full audit sha256
= e9e19296c81caf28466198f91cacade14aabb4b092dea017828959064fccd2c9

probe parquet sha256
= c75653f539c5d102111a99476fd671da1969b8b92487ec59129bbbc646818c46
```

The earlier runtime
`population_target_presession_4824_full_audit_20260807T164721Z` produced a valid
audit payload but a false `FAILED` wrapper state because PowerShell read a null
child exit code. It is retained as a telemetry incident and is superseded by
the complete run above.
