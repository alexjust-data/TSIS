# Massive + SEC screener data decision `v0_1`

Status: `DECISION_FROZEN_PENDING_DATA_ACQUISITION`

## Decision

TSIS will complete the required Massive and SEC data acquisition before
building or promoting the definitive screener.

The future screener contract is:

```text
decision_timestamp = 04:01:00 America/New_York

0.50 <= price_0401 <= 20.00

market_cap_0401 =
    price_0401 * SEC_PIT_shares_outstanding_as_known

market_cap_0401 < 100,000,000 USD
```

## Price authority

```text
1. Last eligible trade known by 04:01 ET.
2. Fallback: last valid NBBO known by 04:01 ET.
3. If neither exists: UNKNOWN_PRICE.
```

Trade causality must use `sip_timestamp <= decision_timestamp`, while also
preserving `participant_timestamp` and every other Massive trade field.

Massive extended Trades will be acquired for the complete `04:00-20:00 ET`
session. Quotes will remain the NBBO fallback and reconciliation source.

## Shares authority

The canonical denominator will come from SEC PIT reconstruction and preserve:

```text
measurement_at
available_at
eligible_from_session
share_class
shares_outstanding
accession
source
quality_state
```

Massive Ticker Overview may be retained as a current vendor snapshot for
reconciliation and anomaly detection, but it must not fill historical PIT
shares.

The proxy TTL of 180 days does not automatically apply to SEC PIT shares.
Exact O/S states advance through causally known filings and corporate events;
uncertain states remain NULL or flagged.

## Separation of outputs

Until SEC PIT is complete, the two meanings must remain separate:

```text
market_cap_proxy_0401 =
    price_0401 * weighted_average_shares_proxy

market_cap_0401 =
    price_0401 * SEC_PIT_shares_outstanding_as_known
```

The first is an explicitly labelled research proxy. Only the second may become
the canonical screener variable after full acquisition and certification.

No new screener output will be promoted as canonical until both Massive and
SEC acquisitions, temporal coverage, identity reconciliation and validation
gates are complete.
