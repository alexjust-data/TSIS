# SEC PIT ownership identity and Record Date shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

Scope: generic issuer-name identity reconciliation and causal ownership-table
date binding. This certification authorizes only a fresh 99-case local rerun.
It does not authorize the 4,824-instrument scale.

## Findings and generic changes

The governed instrument master can contain a security description rather than
only the SEC legal registrant name. For example, security and jurisdiction
suffixes such as `Common Shares 0.01 SF (Bermuda)` or `(NV)` do not appear in
the SEC registrant name. The prior matcher treated those suffixes as required
issuer tokens and emitted an identity conflict.

The corrected admission still requires the governed interval, CIK and either
class CUSIP, name-change continuity or issuer-name evidence. It never admits a
document by CIK alone. The new auditable basis
`ISSUER_CORE_NAME_TOKEN_EVIDENCE` removes only a closed vocabulary of vendor
security/jurisdiction labels. Simulation over every content-complete but
identity-rejected baseline in v0.7 admitted AEN and CYTO while preserving the
rejection of AGL, ALR, VELO and VIVE.

Ownership tables also commonly state `as of the Record Date` while defining
that date elsewhere in the proxy. The parser now accepts only:

1. an explicit date bound in a sentence to the ownership table; or
2. an ownership table explicitly referencing `Record Date` plus one unique
   document-level Record Date defined by contractual wording.

Conflicting Record Date definitions remain NULL. Compensation, awards and
unrelated outstanding-share dates remain rejected. The category state machine
also recognizes separate `Directors:`, `Other Named Officers:` and
`5% or greater stockholders` sections, plus aggregate management labels that
contain the issuer name.

No ticker, CIK or accession is hard-coded.

## Invalidated diagnostic run

`C:/TSIS_Data/runtime/sec_pit_100_case_resolution_v0_8` was stopped after
99/99 O/S and 18/99 owner cases when `ownership_v2.py` changed during the run.
All 18 completed owner cases still shared the old component hash and no network
request occurred, but the root is persisted as
`INVALIDATED_SUPERSEDED_COMPONENT_VERSION`; resume and promotion are forbidden.

## Final four-shard probe

Evidence root:
`C:/TSIS_Data/runtime/sec_pit_100_case_record_date_shard_probe_v0_2`

All four cases used ownership parser SHA-256
`96e3233ed66d725e43dfcb533807cbff1e16ce4e45a41b115b944d8d781db8be`,
the same runner hash, stable schema/order, five unique session rows and zero
network requests.

| Shard | Ticker | Result | Interpretation |
|---:|---|---|---|
| 0 | ADMP | baseline selected; 0/5 float | remains fail-closed on intervening split |
| 1 | ATYR | 5/5 calculated | values unchanged from prior certified control |
| 2 | CYTO | baseline selected; 0/5 float | remains fail-closed on unavailable O/S |
| 3 | ADTX | 0/5 float | identity and partial baseline blockers preserved |

ATYR remains O/S `97,986,634`, supported excluded shares `1,400,094`, float
`96,586,540` and float percent `98.57113777374984%`.

## Test gate

- focused parser/baseline/float suite: `37 passed`;
- complete SEC PIT suite: `209 passed`.

The repository-wide Data Foundation suite was also attempted. Its SEC PIT tests
are not the cause of failure; unrelated output-contract tests reference missing
legacy `E:/TSIS/...` artifacts. That environment failure is not counted as SEC
PIT evidence.

## Gate decision

A fresh immutable 99-case rerun is authorized. It must use a new root/run id,
make zero network requests, not resume v0.8, persist component hashes and retain
all O/S, identity, class, overlap and split failures as explicit NULL states.
