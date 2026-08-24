# Massive SEC acquisition execution and recovery plan v0.1

Status: **PREPARED_NOT_AUTHORIZED**

Date: 2026-08-22  
Owner: TSIS Data Foundation  
Heavy output root: D:/sec_float_pit_MASSIVE

## 1. Authority and purpose

The only download-scope authority is:

C:/TSIS_Data/00_CTO/04_MARKET_STATES_CREATION/07_SEC_UPSTREAM_DATA/01_MASSIVE_SEC_OBJETIVO_01.md

00_MASSIVE_SEC.md is supporting analysis, not download authority. The v0.1
handoff package is implementation guidance, not permission to expand scope.

This plan prepares a resumable Massive REST acquisition. It does not authorize
an API request. Written confirmation of subscription, retention and intended
research-use rights is a hard precondition.

## 2. Frozen scope

Direct lane:

1. EDGAR index;
2. Form 3 and 3/A;
3. Form 4 and 4/A;
4. 8-K structured disclosures;
5. disclosure taxonomy.

Conditional and currently excluded:

- 8-K text, until the bounded 250-case coverage/size gate passes and a human or
  governed authorization is persisted;
- 13F, until a multi-quarter CUSIP/filter design passes and is separately
  authorized.

Massive float, all-tickers, ticker overview/events, splits, balance sheets,
risk factors, news and market-data endpoints are prohibited in this run.

The frozen target is 4,824 ordered ticker cases represented by 4,288 unique
normalized issuer CIKs. Vendor calls may deduplicate by CIK, but the full target
membership and order remain hash-bound.

## 3. Throughput decision

Initial production-equivalent probe:

- 4 concurrent HTTP workers;
- one process-wide adaptive ceiling of 2 requests/second;
- exponential retry with jitter for 429 and transient 5xx failures;
- automatic rate reduction after 429;
- no GPU;
- 200 GiB minimum free-space reserve.

The 2 requests/second value is an engineering safety ceiling, not a claimed
Massive subscription limit. The public documentation does not establish one
universal REST rate. Eight workers is only a future maximum and requires a new
hash-bound config after a clean probe with no 429 pressure, stable latency and
I/O headroom. v0.1 always executes with 4 workers.

## 4. Transactional page commit

~~~text
HTTPS response
-> immutable gzip raw object in SHA-256 CAS
-> deterministic normalized JSONL gzip page shard
-> atomic COMMITTED receipt
-> fsync append to request ledger
~~~

The receipt is the commit authority. A page without a valid receipt is not
complete. Existing paths may only be reused when decompressed content hashes
match exactly.

## 5. Power-loss recovery

Resume granularity is one response page; HTTP byte-range resume is not claimed.

- Power loss before receipt: the page is requested again. Existing identical
  CAS/shard bytes are reused; changed content at the same work identity fails
  closed.
- Power loss after receipt but before ledger append: the request ledger is
  deterministically rebuilt from receipts.
- Power loss after receipt and ledger: resume validates hashes and skips the
  committed page.
- Duplicate live process: the output-root lock blocks the second writer.
- Dead same-host process: only --resume may archive the stale lock and take
  ownership.
- Foreign-host or unverifiable lock: no automatic takeover.

The actual run state lives under D:/sec_float_pit_MASSIVE/runs/<run_id>.
The pointer under C:/TSIS_Data/runtime/massive_sec_acquisition_v0_1 is
convenience metadata and is not recovery authority.

This design protects interrupted writes; it cannot recover a physically failed
single disk. A UPS and a separately governed copy to another NTFS volume remain
recommended before treating the acquisition as durable evidence.

## 6. Mandatory gates

~~~text
code + mocked tests PASS
-> plan-only manifest PASS
-> written license/retention confirmation
-> human PROBE_ONLY authorization
-> exact 250-case production runner
-> endpoint/schema/value audit + storage projection
-> governed probe PASS
-> separate FULL_AFTER_PROBE_PASS authorization
-> full run
-> no-network integrity audit
-> final certification
~~~

8-K text and 13F remain outside this sequence unless their independent gates
are completed.

## 7. Current evidence

- local Massive-specific tests: 20 passed;
- Ruff: PASS;
- exact plan-only run: massive_sec_probe_plan_20260822_v0_1;
- planned probe: 250 cases, 249 unique CIKs, 997 endpoint/CIK chains;
- observed D free space: 870.98 GiB;
- network requests made by this preparation: zero;
- data written to D by this preparation: zero.

Official endpoint references were checked against the
[Massive Stocks REST overview](https://massive.com/docs/rest/stocks/overview)
and the endpoint pages linked from it. These SEC surfaces are documented as
early-access/beta; live schemas remain provisional until the bounded probe.

## 8. Stop conditions

Stop without promotion on any scope/hash drift, credential leakage, 401/403,
schema identity failure, pagination host/path drift, repeated 429 pressure,
free space below 200 GiB, artifact hash mismatch, second writer, or unexplained
coverage loss.

The full-universe command is intentionally not authorized or launched by this
preparation.
