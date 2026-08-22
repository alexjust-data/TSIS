# Trading Activity A/B denominator — Daily Eligible Universe reconciliation readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_ab_denominator_daily_eligible_universe_reconciliation` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_READ_ONLY_EXACT_RECONCILIATION` |
| `document_status` | `PASS_EXACT_WITH_EXPERIMENTAL_SELECTOR_RESTRICTIONS` |
| `executed_at` | `2026-08-15` |
| `network_access` | `NOT_USED` |
| `outputs_written` | `0` |
| `duckdb_version` | `1.4.4` |

## 1. Inputs

```text
selected TARGET contexts
= G:/TSIS/data/data_foundation_outputs/trading_activity_ta3_stratified_sample/
  trading_activity_ta3_stratified_sample_v0_1_20260807T175808Z/
  selected_target_contexts_v0_1.parquet
SHA-256
= 55890736132080098114ac356ab5bce66adf3c26a9a4b92915788594d06b2220

daily population candidate
= G:/TSIS/data/data_foundation_outputs/population_target_presession_4824_candidate/
  population_target_presession_4824_candidate_v0_1_experimental_20260807T170430Z/
  population_target_presession_4824_candidate_v0_1.parquet
SHA-256
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

population manifest SHA-256
= 26a131b7c01e8b598fe0bd2dbeac8b768ddcd4103fdb1d66746508f4aca398da
```

## 2. Method

A left join was executed on exact `population_context_id`. For every TARGET row
the audit compared:

```text
instrument_id
session_date
population_membership_state
presession_reference_price
presession_reference_market_cap_proxy
```

No date-range inference, ticker-only join or tolerance-based numeric comparison
was used.

## 3. Result

```text
selected TARGET rows             = 2,400
exact context matches            = 2,400
unmatched                        = 0
identity mismatches              = 0
membership-state mismatches      = 0
reference-price mismatches       = 0
market-cap-proxy mismatches      = 0
ELIGIBLE_UNDER_DECLARED_PROXY    = 2,400
duplicate population_context_id  = 0
duplicate instrument-session     = 0
```

Observed selected range:

```text
session dates                    = 2011-08-11 through 2022-12-29
unique instruments               = 194
minimum reference price          = 0.50 USD
maximum reference price          = 19.95 USD
maximum market-cap proxy         = 99,909,321.84 USD
```

## 4. Interpretation

```text
current A development denominator satisfies candidate daily eligibility
= PASS_EXACT

A rematerialization solely for eligibility repair
= NOT_REQUIRED

B may change the selector or denominator alone
= PROHIBITED

candidate becomes canonical operational screener
= false

full eligible-symbol-second operational denominator certified
= false
```

The 2,400 sessions are a frozen stratified development sample. They are not a
substitute for the complete daily membership and eligible-symbol-second
denominator needed to measure operational false-alert burden.
