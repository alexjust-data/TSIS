# POPULATION_TARGET_PRESESSION_4824_PROXY_BINDING_DECISION_v0_1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `population_target_presession_4824_proxy_binding_decision` |
| `document_version` | `v0_1` |
| `document_role` | `EXPERIMENTAL_PROXY_BINDING_DECISION` |
| `document_status` | `PREREGISTERED_FOR_CONTROLLED_PROBE` |
| `selector_gate` | `NOT_YET_EVALUATED` |
| `broad_materialization` | `NOT_YET_AUTHORIZED` |
| `canonical_promotion` | `NOT_AUTHORIZED` |
| `created_at` | `2026-08-07` |

## 1. Governed decision

The primary experimental proxy binding for the controlled probe is:

```text
share_selection_policy_id
= S1_DILUTED_FIRST

shares_ttl_policy_id
= SHARES_TTL_180D
```

This is a proxy-lane implementation decision. It is not a declaration that
diluted weighted-average shares equal legal point shares outstanding or that
180 days is a universal staleness truth.

## 2. Evidence used

The full-history read-only audit covered:

```text
7,369,699 requested ticker-session rows
2005-01-03 through 2026-03-09
4,824 parent-universe tickers
```

For sessions inside the price profile, classifiable rows were:

| TTL | Classifiable rows | Eligible S1 | Eligible S2 | S1/S2 disagreements |
|---:|---:|---:|---:|---:|
| 90 | 2,644,045 | 1,189,774 | 1,199,483 | 9,915 |
| 180 | 3,106,545 | 1,417,316 | 1,428,915 | 11,871 |
| 365 | 3,261,280 | 1,494,582 | 1,506,489 | 12,179 |

The admissible source observations also showed:

```text
basic/diluted ratio p50 = 1.0000
basic/diluted ratio p99 = 1.3275
basic/diluted ratio max = 37.5644
```

## 3. Selection rationale

### S1 diluted-first

When diluted exceeds basic, S1 produces the larger market-cap proxy and is
therefore conservative for a strict `< $100M` membership rule. It also matches
the measure selected throughout the recovered legacy panel, which supports
reconciliation without granting that panel primary authority.

S2 remains mandatory sensitivity evidence because 11,871 TTL-180 decisions
change at the threshold.

### TTL 180 days

Relative to TTL 90, TTL 180 adds 462,500 classifiable rows. Extending from 180
to 365 adds 154,735 more rows but admits substantially older accounting
proxies. TTL 180 is therefore preregistered as the primary compromise between
coverage and staleness for the proxy lane.

TTL 90 and TTL 365 remain mandatory sensitivity policies.

## 4. Required sensitivity set

The following alternatives remain governed and may not be deleted from the
evidence package:

```text
S1_DILUTED_FIRST x TTL_90D
S1_DILUTED_FIRST x TTL_365D
S2_BASIC_FIRST x TTL_90D
S2_BASIC_FIRST x TTL_180D
S2_BASIC_FIRST x TTL_365D
```

## 5. Restrictions

The selected primary binding must retain these labels and non-claims:

```text
weighted-average shares proxy
date-only conservative availability
presession reference market-cap proxy
fixed 4,824-ticker parent frame
no complete historical US <$100M population claim
no exact point-shares claim
no historical float claim
```

Sessions before source coverage, with stale shares, unresolved price, or a
split/ticker-change review state remain in the denominator with explicit
states. They may not be silently excluded.

## 6. Authorization boundary

```text
primary proxy binding preregistered
-> controlled physical probe
-> independent probe validation
-> selector gate readout
-> broad materialization only if authorized
```

This decision alone does not authorize broad materialization or TA-3 sample
freeze.

## 7. Evidence anchors

```text
run_id
= population_target_presession_4824_full_audit_20260807T164922Z

audit_output_sha256
= e9e19296c81caf28466198f91cacade14aabb4b092dea017828959064fccd2c9
```
