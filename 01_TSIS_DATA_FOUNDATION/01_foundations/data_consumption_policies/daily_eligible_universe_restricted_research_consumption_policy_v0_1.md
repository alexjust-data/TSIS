# Daily Eligible Universe restricted research consumption policy v0.1

## 0. Control

| Field | Value |
|---|---|
| `policy_id` | `daily_eligible_universe_restricted_research_consumption_policy_v0_1` |
| `status` | `ACTIVE_RESTRICTED_EXPERIMENTAL` |
| `canonical_screener` | `false` |
| `created_at` | `2026-08-15` |

## 1. Authority and scope

This policy admits the existing validated experimental population candidate as
the sole daily-membership authority for the restricted Trading Activity A/B
experiment. It does not promote a canonical live screener or exact historical
market-cap dataset.

This policy is a controlled bridge for the A/B experiment, not the general
Screener Engine. The project-wide conceptual authority lives in
`C:/TSIS_Data/00_CTO/15_SCREENER_ENGINE`; its future runtime and each consumer,
including Backtest, require separate governed gates.

```text
selector owns membership
-> A and B consume identities and hashes
-> A and B do not recalculate price or market-cap thresholds
```

The admitted restricted policy is:

```text
cutoff                         = 04:00 America/New_York
reference price                = prior eligible RTH close
price membership               = 0.50 <= price <= 20.00
shares binding                 = S1_DILUTED_FIRST weighted-average proxy
shares TTL                     = 180 calendar days
market-cap membership          = price * shares proxy < 100,000,000 USD
eligible state                 = ELIGIBLE_UNDER_DECLARED_PROXY
```

## 2. Hash-bound source

```text
candidate parquet SHA-256
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

candidate manifest SHA-256
= 26a131b7c01e8b598fe0bd2dbeac8b768ddcd4103fdb1d66746508f4aca398da

restricted consumption manifest SHA-256
= c1ed29f2764e98bef0f4b4c90144cfce4c56db7d3d7d84b33255b50418b355d7
```

## 3. Allowed consumers

- frozen Binding A development evidence;
- Binding B preparation after its independent B-02/B-03 gates;
- development Wake-up label design and denominator accounting;
- temporal-validation and final-OOS selection preparation before sealing;
- research audits that carry all proxy restrictions and exact hashes.

## 4. Restricted consumers

Temporal-validation and final-OOS target identity generation require their
separate human selection/custody gate. Wake-up labels require the D07 numeric
and adjudication authority. This policy alone opens neither gate.

## 5. Prohibited consumers and claims

- live or canonical scanner membership;
- Backtest, live or RL consumption without a dedicated adapter and gate;
- relabelling this restricted bridge as the general Screener Engine;
- exact legal point shares outstanding;
- exact historical market cap or historical float;
- complete historical US common-stock `<$100M` census;
- changing A/B population independently;
- deriving Wake-up, In-Play, alerts or entry decisions from eligibility alone;
- materializing validation/final-OOS labels or opening lockboxes.

## 6. Development denominator

The 2,400 development targets reconcile exactly to the source candidate. Their
symbol-second denominator is represented losslessly as 2,400 session intervals:

```text
logical identity
= instrument_id x session_date x decision_timestamp_utc

grid
= integer UTC seconds satisfying
  session_open_utc < decision_timestamp_utc < session_close_utc

logical symbol-seconds
= 55,866,000
```

The interval encoding must not be interpreted as a reduction or sample of the
logical denominator.

## 7. Invalidation

Any change to source Parquet, manifest, selector thresholds, shares binding,
TTL, calendar, target identities or decision-grid semantics invalidates this
policy binding and requires a new versioned gate. No consumer may silently
substitute a new daily universe.
