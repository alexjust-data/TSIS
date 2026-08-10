# Population Target PIT Recovery Inventory Readout `v0_1`

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_pti_recovery_inventory_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_RECOVERY_AND_SOURCE_FIT_READOUT` |
| `document_status` | `EXECUTED` |
| `recovery_integrity_gate` | `PASS_WITH_RESTRICTIONS` |
| `direct_session_start_selector_gate` | `FAIL` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

## 1. Question answered

This readout answers:

```text
Does the historical population_target_pti artifact still exist,
is its physical content consistent with its preserved summary,
and may it be consumed directly as the point-in-time selector
for a Wake-up research session before market open?
```

Answer:

```text
RECOVERY
= SUCCESSFUL

RECOVERY INTEGRITY
= PASS_WITH_RESTRICTIONS

DIRECT SESSION-START CONSUMPTION
= FAIL

AUTHORIZED ROLE
= historical evidence, reconciliation input and source evidence
  for a new session-start candidate
```

## 2. Executed evidence

Auditor:

```text
01_TSIS_DATA_FOUNDATION/scripts/
audit_population_target_pti_recovery.py
```

Unit tests:

```text
01_TSIS_DATA_FOUNDATION/tests/
test_population_target_pti_recovery_audit.py

3 passed
```

Machine-readable inventory:

```text
01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/
population_target_pit/
population_target_pti_recovery_inventory_v0_1.json
```

The auditor is read-only with respect to all historical sources and runtime
evidence.

## 3. Recovered artifact

Current physical location:

```text
C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/runs/backtest/
population_target_pti/population_target_pti_run_01/
population_target_pti.parquet
```

Companion evidence recovered in the same run:

```text
population_target_pti_summary.json
population_target_pti_artifacts.json
population_target_pti_year_summary.parquet
marketcap_audit/
```

Integrity anchor established after recovery:

```text
size_bytes = 498,132,535
sha256     = 0fccd316741a9460a223c9558f65f3f6917664feb565a737c5c84ee4784f573a
```

The preserved manifest did not contain an original full-file hash. The new
hash is therefore a post-recovery integrity anchor, not a comparison against
the creation-time hash.

## 4. Physical verification

| Metric | Result |
|---|---:|
| rows | 29,735,570 |
| tickers | 13,066 |
| date minimum | 2005-01-01 |
| date maximum | 2026-03-09 |
| rows with close | 19,702,631 |
| rows with accepted shares | 15,143,484 |
| classifiable market-cap rows | 10,278,625 |
| anti-lookahead violations under legacy date rule | 0 |
| TTL violations above 180 days | 0 |
| market-cap formula mismatches | 0 |
| legacy `<2B` flag mismatches | 0 |

The scan reproduces the declared row, ticker and classifiable-row counts.

## 5. Identity restriction

The legacy key `ticker + date` is not unique:

```text
rows_total                       = 29,735,570
unique ticker-date keys          = 29,735,523
ticker-date excess rows          = 47
unique entity_id-date keys       = 29,735,570
entity_id-date excess rows       = 0
null entity_id rows              = 0
```

The 47 collisions are ticker reuse or overlapping identity records affecting:

```text
HIW
HW
IPW
KW
```

Consequences:

```text
ticker + date
= prohibited as the governed primary key

resolved instrument identity + session_date
= required for the new panel

affected identity windows
= must receive an explicit local resolution or review state
```

This restriction changes the recovery verdict from `PASS` to
`PASS_WITH_RESTRICTIONS`; it does not invalidate unrelated rows.

## 6. Shares semantics

The recovered construction used:

```text
COALESCE(diluted_shares_outstanding, basic_shares_outstanding)
```

with priority given to diluted shares and a 180-day TTL. Physical results:

```text
rows carrying shares_source = diluted  15,945,525
rows with usable diluted shares          15,143,484
rows carrying shares_source = basic               0
same-date accepted share observations       161,130
```

These fields are statement-period average share measures used in EPS
calculation. They are not proven equivalent to legal common shares outstanding
at every session and they are not float.

The legacy availability rule was date-level:

```text
shares_observed_date <= date
```

That rule passes the historical anti-lookahead check but is not sufficient for
a pre-open selector because a filing dated on the target session may have been
published after the session opened.

Conservative session-start rule:

```text
shares_as_of_session
= latest accepted observation where as_of_date < session_date
  and age at session start <= 180 days
```

The strict `<` rule treats every same-date filing as unavailable at session
start until intraday publication timestamps exist.

## 7. Price and threshold restrictions

The historical panel calculates:

```text
market_cap_t = target_date_close_t * shares_outstanding_t
```

This is valid for an end-of-day historical context, but the target-session
close is future information before the session opens.

The legacy boolean `is_small_cap_t` means:

```text
market_cap_t < $2B
```

It does not mean `<$100M`. The physical market-cap value can support another
threshold, but the boolean may not be reused for TA-3.

Although 1,473,545 same-day rows fall numerically inside both `$0.50-$20` and
`<$100M`, that count is descriptive only and is not a causal TA-3 denominator.

## 8. Current governed sources

### Price and session spine

`master_daily_table_v0_1`, `price_view=daily_raw`:

```text
rows                                      = 7,369,699
tickers                                   = 4,824
rows with prior_close                     = 6,697,494
rows with prior_close in $0.50-$20        = 4,336,170
development rows 2011-2022                = 4,614,183
development price-band rows 2011-2022     = 2,505,639
```

This source provides the causal price candidate:

```text
prior_close
```

Corporate-action sessions still require the governed price bridge and local
audit defined by the recovery plan.

### Shares history

`fundamentals_asof_table_v0_1`, income statements:

```text
rows                                      = 242,886
tickers                                   = 4,813
as_of range                               = 2010-06-09..2026-04-03
rows with basic shares                    = 242,858
rows with diluted shares                  = 242,858
event-context candidate rows              = 195,995
event-context rows with share measures    = 195,973
```

This source has governed `filing_date/as_of_date` lineage and is the primary
candidate for a new operational-universe session-start panel. Its share
measure remains a proxy and must be named as such.

## 9. Gate decisions

```text
LEGACY_ARTIFACT_LOCATION
= RESOLVED

LEGACY_RECOVERY_INTEGRITY_GATE
= PASS_WITH_RESTRICTIONS

LEGACY_DIRECT_SESSION_START_SELECTOR_GATE
= FAIL

CURRENT_PRIOR_CLOSE_SOURCE_OBSERVABILITY
= PASS

CURRENT_SHARE_PROXY_SOURCE_OBSERVABILITY
= PASS_WITH_RESTRICTIONS

POPULATION_TARGET_PIT_SELECTOR_GATE
= PENDING

TA-3 BROAD EXECUTION
= BLOCKED UNTIL THE NEW SELECTOR AND SAMPLE MANIFEST EXIST
```

Foundation labels or historical review states do not automatically exclude a
target session. Variable-relevant local audit determines whether a context is
usable, degraded or unavailable. This rule does not permit future information
or unresolved identity ambiguity.

## 10. Required next package

The next executable package is:

```text
population_target_pti_session_start_candidate_v0_1
```

Its primary construction must use:

```text
master_daily_table_v0_1 daily_raw session spine
+ prior_close
+ fundamentals_asof_table_v0_1 share proxy with as_of_date < session_date
+ 180-day TTL
+ resolved instrument identity
+ corporate-action bridge/review state
```

The recovered panel is used for:

```text
historical equivalence fixtures
coverage reconciliation
source fallback research
identity-collision fixtures
```

It is not copied, renamed or promoted as the new session-start panel.

Before a full 7.37-million-row materialization, the builder must pass a
controlled fixture/probe covering:

```text
normal session
same-date filing
stale shares
missing shares
split-effective session
ticker reuse
missing prior close
<$100M boundary
$0.50 and $20 price boundaries
```
