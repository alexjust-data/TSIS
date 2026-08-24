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

## Minute-bar remediation dependency

The screener does not depend on repairing the existing `ohlcv_1m` RAW. The
governed sequence is frozen as:

```text
1. Complete full-field Massive Trades acquisition.
2. Complete and certify SEC PIT shares outstanding.
3. Build and run the daily 04:01 ET screener.
4. Persist the exact ticker-session dates selected by the screener.
5. Intersect only those selections with known 1m coverage incidents.
6. If an affected selection needs minute bars for backtesting, reconstruct a
   versioned derived candle view from complete Trades.
```

There will be no blanket 1m redownload or immediate repair based only on the
5,238 observed ticker-dates without RTH. The 14,302 rows in those cases are
present extended-session bars, not missing rows. A local cross-family forensic
pass isolated eight high-confidence candidates, but current Massive REST
parity was not certified and 2,117 cases lacked a legacy RTH Trades file.

Any future reconstruction must preserve `G:/TSIS/data/ohlcv_1m` as immutable
RAW and publish a separate derived dataset with source Trades lineage, rule
version, affected ticker-date inventory and validation evidence. The governing
readout is:

`C:/TSIS_Data/01_TSIS_DATA_FOUNDATION/01_foundations/inspection_dossiers/core_market_family_download_audit/OHLCV_1M_FULL_AUDIT_READOUT_v0_1.md`
