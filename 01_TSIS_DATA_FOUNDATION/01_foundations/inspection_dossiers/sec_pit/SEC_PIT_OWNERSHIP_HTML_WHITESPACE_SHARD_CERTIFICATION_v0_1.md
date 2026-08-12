# SEC PIT ownership HTML whitespace shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

## Finding

The v0.10 run calculated owner-exclusion float for 19/99 eligible cases, or
95/495 bounded sessions. Twenty cases remained under
`AMENDMENT_FAMILY_UNRESOLVED`.

Local, no-network inspection showed that this blocker was still overbroad.
Many family-head filings already contained complete ownership tables, but SEC
HTML inserted line breaks, non-breaking spaces or zero-width characters inside
otherwise ordinary headers. For example, AIEV exposed `Name and Address of
Beneficial Owner`, `Number of Shares`, `Percent` and a management aggregate of
114,200 shares, but the parser did not recognize the fragmented header.

The correction is generic. `ownership_v2.py` now normalizes visible whitespace
before classifying tables and recognizes a single-class aggregate table only
when it contains:

- a document-level ownership heading;
- a semantic management aggregate containing directors, officers and
  `as [a] group`;
- a shares/beneficial-ownership column family;
- a percentage column; and
- no simultaneous Class A and Class B headers.

Multiclass tables do not enter this generic path. No ticker, CIK, accession or
numeric result is hard-coded. Identity, causal date, split, class, holder
overlap, economic overlap and post-baseline gates remain downstream authority.

## Required four-shard production-equivalent probe

Evidence root:
`C:/TSIS_Data/runtime/sec_pit_100_case_html_whitespace_shard_probe_v0_1`

All four probes used parser SHA-256 prefix `251cb33f1e6f`, the same O/S v0.10
dependency, the immutable combined acquisition ledger and zero network
requests.

| Shard | Ticker | Structured result | Daily float | Final behavior |
|---:|---|---|---:|---|
| 0 | OMCC | 13 rows in a candidate document | 0/5 | fail-closed on partial baseline and holder/economic overlap |
| 1 | AIEV | baseline `0001213900-25-026239` | 5/5 | calculated |
| 2 | APDN | ownership baseline resolved | 0/5 | fail-closed on intervening split adjustment |
| 3 | TONX | baseline `0001493152-25-016864` | 0/5 | fail-closed on post-baseline event identity/date |

AIEV's readable values are:

- O/S as known: `70,724,664`;
- management aggregate: `114,200`;
- owner-exclusion float: `70,610,464`;
- float percent: `99.838529%`;
- measurement date: `2025-03-31`;
- eligible from session: `2025-04-01`;
- five bounded sessions: all `CALCULATED`.

The 17,900,564-share 5% holder shown in the same table is not subtracted by
`officer_director_explicit_affiliate_v0_1`, because the methodology does not
turn ownership percentage alone into an affiliate assertion.

## Tests and authorization

- focused parser/baseline/float suite: `41 passed`;
- complete SEC PIT suite: `213 passed`;
- network requests in all probes: `0`;
- previously fail-closed downstream gates remained fail-closed.

A fresh immutable v0.11 rerun of the 99 eligible cases is authorized. It must
use a new output root and run identity, must not resume or mix v0.10 outputs,
must use the same acquisition, selection, Company Facts and O/S dependencies,
and must publish coverage/blocker deltas before any further scale decision.

Scale to 4,824 instruments remains `NOT_GRANTED`.
