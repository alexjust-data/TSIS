# SEC PIT 100-case stratified scale gate readout v0.1

Status: `SYSTEM_GATE_COMPLETE_SCALE_BLOCKED_OWNERSHIP_COVERAGE_LOOP_REQUIRED`

Date: 2026-08-12

Authority level: versioned Data Foundation evidence readout; no canonical float promotion.

## Objective

Measure how often the existing causal SEC pipeline can resolve shares outstanding,
ownership and `FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN` across a heterogeneous,
temporally representative sample before any 4,824-instrument expansion.

The gate preserves explicit `NULL` and security-class halts. Coverage is measured;
it is not manufactured.

## Parent universe and identity

- Parent universe: `lt1b_universe_v0_1`, exactly 4,824 unique tickers.
- Canonical universe source: `market_cap_cutoff_lt_1b_active_inactive.parquet`.
- `instrument_master_v0_1` is used only as the identity/security-class projection.
- All 4,824 universe rows matched a CIK-bearing instrument-master row.
- Vendor observation windows remain evidence candidates and are not silently
  promoted as legal SEC listing/delisting intervals.

## Deterministic temporal design

A 240-case candidate pool was frozen, followed by an exact 100-case MILP selection.
All 60 sample constraints passed.

Temporal cohorts in the final 100:

| Cohort | Cases |
|---|---:|
| 2005-2008 | 12 |
| 2009-2012 | 8 |
| 2013-2016 | 22 |
| 2017-2020 | 20 |
| 2021-2023 | 25 |
| 2024-2025 | 13 |

Every calendar year from 2005 through 2025 has at least 12 represented cases.
The four deterministic execution shards contain exactly 25 cases each.

Observed-history span buckets:

| Span | Cases |
|---|---:|
| >=15 years | 12 |
| 10-15 years | 6 |
| 5-10 years | 31 |
| 2-5 years | 30 |
| <2 years | 21 |

The sample also enforces lifecycle/document strata including domestic annual and
special proxies, foreign 20-F families and amendments, multiclass cases, ticker
reuse, SPAC/de-SPAC, bankruptcy, pre-XBRL history, sparse ownership history,
reverse splits and offering-heavy histories.

## Metadata-only profile

Run: `submissions_profile_v0_1_20260811T2255Z`

- 240/240 cases complete.
- 149,309 SEC filing metadata rows.
- Zero primary-document downloads.
- Zero Company Facts downloads.
- Peak RSS: 0.128 GiB.
- System CPU peak: 37.4%.

This profile supports selection and sizing only; filing metadata is not treated as
resolved O/S, ownership or float evidence.

## Predownload control

- Final sample: 100 cases.
- Common-equity eligible: 99.
- Intentional security-class halt: `CNOBP`.
- Indiscriminate plan rejected: 56,782 documents and a 53.5 GB filing-size ceiling.
- Selective owner/O/S/lifecycle plan: 6,245 selected rows.
- Initial missing set: 5,921 rows after prior evidence reuse.
- Median selected documents per case: 56.
- P95: 142.
- Maximum: 218.

## Mandatory four-shard production-equivalent gate

The anchor-delta probe downloaded ten previously missing documents, built a
322-document verified composite ledger, and reran the bounded O/S and ownership
probes. All four planned shards passed ordered schema, grain, PIT eligibility,
explicit blocker, lineage and readable-value checks with identical component
hashes. The ten added documents changed none of the six previously eligible
reference outcomes.

This certification authorized the selective 100-case acquisition; it did not
authorize the full 4,824-instrument materialization.

## Acquisition history and recovery

### v0.1 historical-primary failure

The first execution encountered a legacy SEC primary-document URL returning 404.
The same-CIK, same-accession complete submission remained available. A generic,
fail-closed fallback was implemented:

`SAME_CIK_SAME_ACCESSION_COMPLETE_SUBMISSION_ONLY_V0_1`

The fallback preserves the originally authorized URL, resolved URL, accession,
CIK and content scope, and marks complete submissions as requiring document-boundary
parsing. The changed runner was not resumed inside the old run.

### v0.3 telemetry failure

Run: `sec_pit_100_case_primary_v0_3_20260811T2355Z`

- 1,994 documents fetched.
- 319,610,144 response bytes.
- 0 HTTP 429.
- 8 recovered request retries.
- Failure was not a SEC/network/data failure.
- Exact failure: transient Windows `PermissionError` while atomically replacing
  `heartbeat_latest.json`, consistent with a reader holding the target file.

All acquired objects remained valid in content-addressed storage. The shared SEC
atomic writer now retries short-lived Windows `PermissionError` replacement locks.
A regression test reproduces two denied replacements followed by success. The
telemetry/scope/fallback test set passes 10/10.

### v0.4 recovery execution

Probe root: `bounded_probe_authorized_v0_4_20260812T0530Z`

Run: `sec_pit_100_case_primary_v0_4_20260812T0535Z`

- Prior objects are reread, decompressed and checked by bytes and SHA-256.
- Remaining authorized selection: 3,722 rows.
- Execution is monothread at five SEC requests per second maximum.
- Terminal status: `COMPLETE`.
- Fetched: 3,722/3,722.
- Response bytes: 593,813,717.
- Failed rows: 0.
- Retries: 0.
- HTTP 429: 0.
- Peak system CPU: 62.3%; peak process-tree RSS: 0.137 GiB.
- The verified composite ledger contains 6,051 unique selected URLs, zero
  missing URLs and `PASS_ALL_ROWS` object verification. The 6,245 selection
  rows include 194 repeated URL uses across case/document roles.
- No O/S, ownership or float result may be promoted until acquisition completes,
  the composite ledger has zero missing selected URLs, and local resolution/audit
  stages complete.

## Verified composite acquisition ledger

The completed acquisition histories were merged without copying payloads into a
verified composite ledger:

- 6,051 unique selected URLs;
- 6,245 selection rows, including 194 repeated role uses;
- zero missing objects;
- every object decompressed and verified by bytes plus SHA-256;
- composite ledger SHA-256:
  `f403107b6cdcda1e5f95a600df2d2e981ae64de2be0b8db04eb977f0c8fa321d`.

No additional primary-document network acquisition is required for this gate.

## Invalidated first local-resolution attempt

Batch `sec_pit_100_case_resolution_v0_1_20260812T0615Z` completed technically,
but its scientific results are invalidated. All 99 eligible cases returned NULL
O/S, including prior positive controls ALUR, BGM and DOMH.

Root cause: the 100-case loader placed the gate category
`COMMON_STOCK_CLASS_CANDIDATE` into `target_class_label`, whose contract requires
a filing-readable legal class label such as `Common Stock` or `Class A Ordinary
Shares`. Some instrument display names also appended that class to the registrant
name, making exact registrant matching fail.

The resolver now:

1. tests a governed common-equity class vocabulary against the SEC exchange table;
2. requires the class and exact ticker to co-occur;
3. prefers the most specific admitted class over a generic suffix;
4. separates a trailing class suffix from registrant identity;
5. persists the resolved class in the O/S manifest; and
6. binds the ownership config to that resolved class.

No ticker-specific exceptions were introduced.

After the semantic change, a new production-equivalent four-shard probe passed:

| Shard | Control | Result |
|---:|---|---|
| 0 | BBBY | explicit NULL retained |
| 1 | ALUR | 5/5 float rows |
| 2 | BGM | 5/5 float rows |
| 3 | DOMH | 5/5 float rows |

Schema, component-hash equivalence, grain, causal eligibility, formulas and
explicit NULL checks all passed. Corrected 99-case batch
`sec_pit_100_case_resolution_v0_2_20260812T0700Z` completed without new network
downloads, but was also invalidated after the PGAC positive control produced
5/5 O/S rows and 0/5 float rows. Ownership still received the instrument display
name instead of the resolved registrant name. Resolved registrant identity is now
persisted by O/S and propagated to ownership. A new four-shard identity/class
probe, including PGAC, passed before v0.3. Neither v0.1 nor v0.2 may be combined
with later results.

## Authoritative bounded local resolution v0.3

Batch: `sec_pit_100_case_resolution_v0_3_20260812T0750Z`

- O/S executions: 99/99.
- Ownership executions: 99/99.
- Failed executions: 0.
- Network requests: 0.
- Owner result/hash/schema audit: 99/99 PASS.
- Four-shard variable certification: PASS.
- O/S full coverage: 34/99 cases and 170/495 sessions.
- Owner-exclusion float full coverage: 9/99 cases and 45/495 sessions.
- Security-class halt: CNOBP, as designed.
- Calculated float cases: ALUR, BGM, BNAI, BNED, DOMH, IOBT, ONCO, PGAC and TAOX.

Positive controls ALUR, BGM, BNAI, DOMH and PGAC each retain 5/5 O/S and
5/5 float rows. BBBY remains explicit NULL with amendment-family and instrument-
interval blockers. No partial five-session cases were silently filled.

| Cohort | Float cases / eligible cases |
|---|---:|
| 2005-2008 | 0/12 |
| 2009-2012 | 0/8 |
| 2013-2016 | 1/22 |
| 2017-2020 | 0/20 |
| 2021-2023 | 4/24, plus one class halt |
| 2024-2026 | 4/13 |

## O/S loss decomposition and multi-evidence correction

The 65 v0.3 O/S NULL cases separate into 23 with no class-admitted periodic
document, 18 with admitted documents but no extracted observation and 24 with
observations but no admitted anchor.

The audit found four unhandled cover-page sentence families and one false-positive
`issuable under outstanding ...` context. The parser now supports the observed
families and rejects `issuable`/`reserved` contexts. It does not promote a single
regex result by itself.

Official SEC Company Facts supplies an independent O/S reconciliation lane. An
exact same-accession, same-measurement, same-value agreement can promote the
primary observation only for a passing single or unnumbered common class.
Multiclass scope and value conflicts stay fail-closed. Company Facts remains
neither a float source nor independent ownership/class identity authority.

The one-case-per-shard certification is persisted in
`SEC_PIT_100_CASE_OS_MULTI_EVIDENCE_SHARD_CERTIFICATION_v0_1.md`:

| Shard | Case | Result |
|---:|---|---|
| 0 | ADMP | 5/5 O/S, exact primary + Company Facts |
| 1 | ASNA | 5/5 O/S, exact primary + Company Facts |
| 2 | ANTH | 0/5, explicit Company Facts value conflict |
| 3 | ADTX | 5/5 O/S, text + inline XBRL; Company Facts agrees |

## Remaining governed stages

The official Company Facts acquisition and multi-evidence rerun are complete.
The eligible-case acquisition persisted 10,158 raw observations from 68 new
requests and 31 byte-and-SHA-verified reused responses. BPT was explicitly
classified `COMPANYFACTS_NOT_AVAILABLE` after the official endpoint returned
HTTP 404. Resolution recomputed reconciliation locally from the immutable raw
observation artifact; it did not consume a stale parser-specific reconciliation.

Batch v0.4 reproduced the expected O/S improvement but was stopped and marked
`SUPERSEDED_NOT_AUTHORITATIVE` after a post-O/S mechanical source edit caused
component-hash drift. No v0.4 output is promoted. Clean batch
`sec_pit_100_case_resolution_v0_5_20260812T1210Z` repeated all work from source
with frozen hashes and completed:

Authoritative source snapshot commit: `27607c8`. Per-component SHA-256 values
remain persisted in the batch and child manifests. Later lint-only source changes
must not be represented as the code that produced v0.5.

- 99/99 O/S and 99/99 ownership executions; zero failures and zero network requests;
- 99/99 owner result/hash/schema audits PASS;
- four-shard variable certification PASS, including the CNOBP fail-closed control;
- one component identity across all 99 O/S runs and zero current-source hash mismatches;
- O/S full coverage 56/99 cases and 280/495 sessions;
- owner-exclusion float full coverage 11/99 cases and 55/495 sessions;
- no cases lost relative to v0.3;
- new calculated float cases BIOC and WINT;
- calculated float cases ALUR, BGM, BIOC, BNAI, BNED, DOMH, IOBT, ONCO, PGAC,
  TAOX and WINT.

The O/S change is +22 complete cases and +110 non-NULL sessions versus v0.3.
Float improves by two complete cases and ten sessions. This proves Company Facts
is useful O/S corroboration, but also quantifies that ownership resolution is now
the dominant gate.

Remaining work:

1. Attack ownership blocker families generically, repeating all four shard probes
   after each semantic change.
2. Prioritize amendment-family resolution, instrument-interval conflicts and
   partial baseline documents before isolated parser cases.
3. Execute a historical transition audit where calculated series actually change;
   five-session tail probes contain no transitions and cannot satisfy it.
4. Keep the 4,824 scale gate closed until human/governed authorization.

## Current decision

`100_CASE_SYSTEM_GATE_COMPLETE`; `OS_MULTI_EVIDENCE_99_RERUN_PASS`;
`OWNERSHIP_COVERAGE_LOOP_REQUIRED`;
`4824_SCALE_BLOCKED`.

The bounded system gate is certified. No population-wide coverage claim or
4,824-instrument materialization is authorized until the ownership and historical
transition stages close.
