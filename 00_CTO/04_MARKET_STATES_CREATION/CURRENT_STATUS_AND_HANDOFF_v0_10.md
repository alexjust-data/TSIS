# CURRENT_STATUS_AND_HANDOFF_v0_10

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `WORKSTREAM_STATUS_AND_AGENT_HANDOFF` |
| `document_status` | `CURRENT_HANDOFF` |
| `snapshot_at` | `2026-08-10` |
| `active_workstream` | `wake_up_trading_activity_ta_3` |
| `scope_id` | `legacy_rth_reconciled_event_time_research_only` |
| `promotion_state` | `EXPERIMENTAL_NOT_CANONICAL` |
| `next_gate` | `COMPLETE_TA3_BINDING_A_AND_CONTINUE_SEC_G8` |
| `supersedes` | `CURRENT_STATUS_AND_HANDOFF_v0_9.md` |

## 1. Current position

```text
TA-1 deterministic pilot                 = PASS_WITH_RESTRICTIONS
TA-2 legacy source gate                  = PASS_WITH_RESTRICTIONS
TA-3 stratified sample                   = FROZEN_AND_VALIDATED
TA-3 G-only source gate                  = PASS_WITH_RESTRICTIONS
TA-3 Binding A orchestrator              = IMPLEMENTED_AND_RESUME_CORRECTED
TA-3 Binding A preflight                 = PASS
TA-3 Binding A bounded physical smoke    = PASS
TA-3 broad Binding A execution           = RUNNING_WITH_CONTROLLED_CONCURRENCY
```

The run remains experimental. It does not authorize model admission, canonical
features, OOS access or Wake-up detection.

## 2. Frozen execution scope

```text
sample manifest SHA-256
= 100f0ac0e1faaecd54eded1d99886daafbe9ecf374a247fa9835febc70b1addf

blocks                 = 240
targets                = 2,400
scope sessions         = 32,013
projected output rows  = 558,684,000
official trade root    = G:/TSIS/data/trades_ticks_prod_2005_2026
D fallback             = PROHIBITED
unavailable G sessions = 3,221 retained in denominator
```

## 3. Runtime incident and correction

Four deterministic shards were launched with 60 blocks each. During execution,
the parent orchestrators for shards 0, 2 and 3 terminated while block workers
had produced or were still producing governed outputs. Shard 1 remained alive.

The first recovery attempt exposed an orchestrator defect: global `--resume`
was forwarded to blocks that had never started. The single-block runner rejects
that state because no output run exists. Shard 2 therefore preserved its first
complete block and failed when the second, new block received `--resume`.

The orchestrator now resolves every block as:

```text
COMPLETE -> skip and register SKIPPED_COMPLETE
PARTIAL  -> invoke the subrunner with --resume
NEW      -> invoke the subrunner without --resume
```

Validation performed after the correction:

```text
Python compilation       = PASS
Ruff                     = PASS
orchestrator pytest      = PASS
PowerShell parser        = PASS
physical resume states   = COMPLETE / COMPLETE / NEW as expected
```

## 4. Concurrency decision

Workers reached approximately 6 GB during `STAGE_8` PIT baseline and surprise
materialization. The host exposes approximately 31.9 GB physical memory. Four
concurrent workers left an unsafe operating margin and may have contributed to
wrapper loss.

```text
MAX_CONCURRENT_TA3_WORKERS = 2
```

This is an operational safety decision, not a scientific change to Binding A
or the frozen sample.

## 5. Shard snapshot

Snapshot observed on 2026-08-08:

```text
SHARD 0 = RUNNING, 6/60 completed, 0 failed
SHARD 1 = RUNNING, 15/60 completed, 0 failed
SHARD 2 = QUEUED_FOR_CONTROLLED_RESUME, 1 complete block preserved
SHARD 3 = QUEUED_FOR_CONTROLLED_RESUME, 5 complete block outputs preserved
```

Shard counters are runtime snapshots and will advance. Governed block manifests
and output hashes, not this snapshot, determine final completion.

## 6. Monitor behavior

The monitor reads the active nested subrunner heartbeat and reports block
completion, internal stage, session, rows, partitions, elapsed time, CPU,
heartbeat age, internal message, and wrapper/worker liveness.

Block progress advances only after a complete block. Progress within a block is
demonstrated by stage, session, rows, partitions, elapsed time, CPU and fresh
heartbeats.

## 7. Immediate sequence

```text
1. Finish the currently active shards 0 and 1.
2. Resume shards 2 and 3 under the two-worker limit.
3. Reconcile all 240 block final manifests and output hashes.
4. Validate requested versus produced rows, coverage and missingness.
5. Emit the TA-3 stratified development source-gate readout.
6. Only after that gate, begin Binding B implementation.
```

Not authorized:

```text
Binding B execution
Binding C implementation without justification
OOS access
Representation Model admission
canonical feature promotion
Wake-up detector calibration
```

## 8. Parallel SEC/fundamental lane

The SEC lane is now an executed one-ticker BNAI pilot, not only a future
acquisition proposal. Its physical output authority is:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1
```

Current authoritative run:

```text
sec_pit_bnai_g8_os_reconciliation_v0_40_20260810
```

Audited milestones:

```text
G0 identity/security class              = PASS
G1 EDGAR metadata completeness          = PASS
G2 availability policy                  = PASS_WITH_RESTRICTIONS
G3 O/S anchor extraction                = PASS_WITH_RESTRICTIONS
G4 O/S event reconciliation             = PASS_WITH_RESTRICTIONS
G5 ownership source coverage            = PASS_WITH_RESTRICTIONS
G6 holder deduplication                  = PASS_WITH_RESTRICTIONS
G7 owner-exclusion methodology           = PASS_WITH_RESTRICTIONS
G8 restriction and tradability           = BLOCKED_BY_INPUT_GATES
```

G7 resolves 82 non-null daily owner-exclusion estimates. The other 414
sessions remain NULL because a complete causal ownership baseline is absent.
These rows are experimental PIT estimates, not observed historical float.

G8 preserves 28 registration-scope components under classifier v0.2. Twenty-four
applicable components link to EFFECT evidence: 18 remain
`ISSUANCE_OR_EXERCISE_UNCONFIRMED` and six are reported-current candidates.
All six are consistent with causal O/S capacity, but two rely on stale anchors.
Four rows are non-component aggregate/threshold evidence. O/S consistency does
not prove component inclusion or tradability. EFFECT never proves tradable supply.

```text
tradable-supply confirmations = 0
non-null daily tradability estimates = 0
canonical promotion = NOT_AUTHORIZED
50-ticker replay = NOT_AUTHORIZED
4,821-instrument scale-out = NOT_AUTHORIZED
```

Diagnostic run `v0_37` is non-authoritative because its default 100-document
cap omitted required EFFECT/424B3 evidence. The governed BNAI scope currently
requires `--max-primary-documents 300`. Empty component input now returns
`BLOCKED_BY_INPUT_GATES`, never a pass.

Next SEC work: reconcile reported issued/current components against admitted
O/S events; extract and resolve lockup, restrictive-legend and resale conditions;
retain tradability as NULL until a methodology and all input gates are admitted.

Authoritative readout:

```text
_DESCAGRA_DATOS_NECESARIA_/
SEC_PIT_IMPLEMENTATION_READOUT_v0_1.md
```

This lane remains independent from and does not block the active Trading
Activity Binding A execution.

## 9. Remaining Trading Activity sequence

```text
Binding B implementation
-> A/B comparison at fixed false-alarm budget
-> justified Binding C only if needed
-> temporal OOS validation
-> Representation Model admission or rejection
-> canonical physical binding decision
-> table and lineage mapping
-> full-scope materialization decision
```

Completing Trading Activity does not complete Wake-up. Market Microstructure
State, Price Movement, Liquidity, supporting/conditional context, integrated
representation, detector evaluation and Episode Instance remain downstream.

## 10. Experimental-to-canonical lifecycle clarification

The active TA-3 run is a restricted experimental development materialization.
It evaluates Binding A and its builder; it is not the final 2005-2026 canonical
Trading Activity history.

```text
Binding A / B / justified C
-> frozen development comparison
-> untouched temporal OOS
-> model and binding admission or rejection
-> canonical specification and builder
-> separate full-history production materialization
-> backtest consumption
```

Three time concepts must not be conflated:

```text
feature horizon W       = trailing event window at decision time t
PIT baseline lookback B = causal historical reference before t
coverage period         = calendar history physically materialized
```

Canonical promotion first governs selected dimensions, variables, formulas,
horizons, policies, schema, lineage and the validated builder. A separate run
must then materialize and validate the authorized parent universe and historical
coverage. Backtests normally read this versioned representation dataset; they do
not recompute every raw-event window on each request.

Full contract:

```text
EXPERIMENTAL_TO_CANONICAL_REPRESENTATION_LIFECYCLE_v0_1.md
```

## SEC PIT continuation update - v0_43 (2026-08-10)

The current authoritative BNAI run is:

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
sec_pit_bnai_g8_assignment_reconciled_v0_43_20260810
```

Status: `COMPLETE`; tests: `52/52 PASS`; lint: `PASS`.

G8 now reconciles 23 Assignment Agreement observations into five economic
events, preferring the origin 8-K. One SEC numeric conflict is preserved and no
tradable-supply confirmation is emitted. Daily tradability remains NULL for all
496 sessions. G8 remains `BLOCKED_BY_INPUT_GATES`.

Next work is governed event-to-share-lot linkage. Do not equate the 1,185,000
assigned Sponsor Securities with the separate 1,252,500 release commitment, and
do not infer release, issuance or tradability from an exact numeric match alone.
## SEC PIT continuation update - v0_45 (2026-08-10)

Runs v0_44/v0_45 acquired the two necessary exhibits under demand and linked all
seven Purchasers in the 1,185,000-share Assignment Agreement to exact
selling-holder lots in `333-282130`. The BEN 2,000,000/200,000 source conflict is
preserved explicitly. Linkage is `IDENTITY_AND_QUANTITY_LINKED`, not a
tradability confirmation. G8 remains `BLOCKED_BY_INPUT_GATES`.

Next: resolve actual Required Funding/escrow-release evidence by cutoff and the
separate 1,252,500-share lockup-release schedule. Do not propagate the full
1,185,000 into tradability from registration effectiveness or schedule linkage.
## 2026-08-10 - August funding evidence v0_49

The sentence-bounded extractor resolves the November 13, 2024 disclosure as:

```text
gross proceeds = 550,000 USD
combined shares reported = 220,000
contract rule = one SPA share + one Sponsor share per 5 USD
SPA shares supported = 110,000
Sponsor shares supported = 110,000
failed required funding = 1,250,000 USD
tradable-supply confirmations = 0
```

Authoritative run: `sec_pit_bnai_g8_august_funding_evidence_v0_49_20260810`.
Runs v0_46, v0_47 and v0_48 are preserved as `QUARANTINED` because audit found
cross-transaction/cross-sentence matches to the May SPA. They are prohibited as
downstream evidence. The 110,000 Sponsor shares are aggregate condition-supported
releases as of the disclosure, but purchaser allocation and cancellation amounts
remain unavailable. G8 remains `BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - August funding multivintage resolver v0_53

The governed multivintage builder scanned the acquired primary-document set and
reconciled 24 source observations into seven PIT vintages. Authoritative run:
`sec_pit_bnai_g8_august_multivintage_v0_53_20260810`.

```text
2024-09-13 / eligible 2024-09-16: 50,000 escrow shares, lot unattributed
2024-11-13 / eligible 2024-11-15: 220,000 combined shares / $550,000, equation consistent
2025-02-14 / eligible 2025-02-17: 110,000 / rendered $550, source numeric conflict
2025-03-27 / eligible 2025-04-01: 110,000 / rendered $550, source numeric conflict
2025-03-31 / eligible 2025-06-05: partial termination, purchasers unidentified
2025-06-30 / eligible 2025-10-13: partial termination reiterated
2025-09-30 / eligible 2025-11-26: partial termination reiterated
```

v0_51 is `FAILED` due an unsupported numeric token. v0_52 is
`SUPERSEDED_INCOMPLETE_QUALITY_CLASSIFICATION`. Neither is authorized downstream.
The 2025 `$550` renderings are not silently changed to `$550,000`; they remain
`SOURCE_NUMERIC_CONFLICT`. Cancellation quantities and purchaser allocation stay
NULL. Tradable-supply confirmations remain zero and G8 stays
`BLOCKED_BY_INPUT_GATES`.
## 2026-08-10 - Lockup lifecycle, corporate actions and presession market cap v0_54-v0_58

G8 lockup evidence now resolves the six ex10-2 schedule rows totaling 1,252,500
shares. The contract reports a release of the prior lockup, subject to side-letter
execution and initiation of transfer to escrow, plus a 25% ADV transfer limit.
The later 10-Q supports the 1,185,000-share Sponsor transfer only from its own
public availability date. Neither legend-removal instruction nor registration
proves completed tradability.

```text
v0_54 lockup lots = 6; reported total = 1,252,500
v0_55 daily lifecycle rows = 2,976 (496 sessions x 6 lots)
tradability confirmations = 0
G8 = BLOCKED_BY_INPUT_GATES
```

G9 consumed only the primary `reference` split row from the governed corporate
actions table. The duplicate `additional` row was retained as corroboration but
not applied twice. BNAI's 10-for-1 reverse split effective 2025-12-12 transforms
58 stale pre-split O/S rows from that session onward.

```text
v0_56 daily O/S rows = 496
primary splits applied = 1
secondary duplicates ignored = 1
G9 = PASS_WITH_RESTRICTIONS
```

G10 proved from BNAI's physical downloader checkpoint that the source under
`G:/TSIS/data/ohlcv_daily` was requested with `adjusted=true`. It therefore must
not be multiplied directly by historical-basis O/S. The builder recovers the
historical price basis with future split factors and then aligns prior eligible
RTH close to the target session basis before multiplication.

Run v0_57 was rejected during mandatory first-output audit because pandas `NaN`
O/S was treated as available. A regression test was added and v0_58 supersedes
it. v0_57 is `NOT_AUTHORIZED` downstream.

```text
v0_58 daily rows = 496
market cap estimated = 485
market cap unavailable due O/S = 10
market cap unavailable due price = 1
duplicates = 0
non-finite resolved prices = 0
non-positive market caps = 0
provisional price-and-cap eligible sessions = 212
SEC PIT tests = 67/67 PASS
ruff = PASS
G10 = PASS_WITH_RESTRICTIONS
```

Authoritative run:
`sec_pit_bnai_g10_presession_market_cap_v0_58_20260810`.

This is a one-instrument pipeline pilot, not authorization to scale blindly.
The next scale gate requires a stratified filing/issuer sample and an explicit
parent-universe manifest resolution (4824 vs later references to 4821).
## 2026-08-10 - Historical CUSIP, 13F source gate, core EV and change explanations v0_59-v0_62

G11 extracted CUSIP observations only from SEC objects already acquired. Checksum
validation rejects narrative false positives. The issuer-number gate excludes the
pre-combination SPAC CUSIP `G2758T109` from the BNAI share class.

```text
source observations = 16
admitted BNAI observations = 3
104932108 = 2024-07-29 through 2025-12-11
104932207 = 2025-12-12 through 2026-03-09
pre-first-supported interval = CUSIP_UNAVAILABLE
G11 = PASS_WITH_RESTRICTIONS
```

G12 audited the official local data roots and found no acquired global 13F
information-table source. Institutional ownership remains `UNAVAILABLE`, never
zero. Run `sec_pit_bnai_g12_13f_source_audit_v0_60_20260810` records:

```text
G12 = BLOCKED_BY_SOURCE_NOT_ACQUIRED
required source = GLOBAL_SEC_13F_INFORMATION_TABLE_ACQUISITION
```

G13 resolves only same-measurement-date, causally eligible Company Facts for
cash, ConvertibleNotesPayable and ShortTermBorrowings. Facts measured before the
BNAI instrument valid interval are excluded. The output is deliberately named
`CORE_EV_ESTIMATE`; it is not represented as complete enterprise value.

```text
daily rows = 496
core EV calculated = 391
incomplete/unavailable = 105
lookahead rows = 0
non-finite core EV rows = 0
G13 = PASS_WITH_RESTRICTIONS
```

G16 emits one explanation row per daily state. The split session 2025-12-12 is
explained by corporate-action basis change, prior-close update and CUSIP interval
change. Counts are:

```text
prior-close updates = 495
O/S anchor vintage changes = 2
balance-sheet vintage changes = 6
CUSIP interval changes = 2
corporate-action basis changes = 1
G16 = PASS_WITH_RESTRICTIONS
```

Authoritative runs are v0_59 through v0_62 under
`D:/TSIS/fundamental_context/sec_pit_v0_1/runs`. This closes the executable BNAI
pilot except G8 tradability and G12 institutional ownership. Scale-out is not
authorized until the optimized stratified replay and parent-universe identity
scope are frozen.

## SEC PIT lifecycle source lane - 2026-08-10

The lifecycle metadata prerequisite is complete:

~~~text
run = sec_pit_7t_lifecycle_v0_1
gate = PASS_WITH_RESTRICTIONS
52 regulatory candidates
6 security-class PASS
CNOBP = HALT_SECURITY_CLASS
primary lifecycle documents = NOT_ACQUIRED
resolved first/last trade = NOT_EXECUTED
~~~

Continue with a lifecycle-only primary-document acquisition plan and capacity
forecast. Do not launch the former broad seven-ticker replay or infer listing
boundaries directly from filing dates.

## SEC PIT lifecycle primary acquisition - 2026-08-10

~~~text
run = sec_pit_7t_lifecycle_primary_v0_1
50 / 50 fetched
0 failures
1,300,708 response bytes
byte-level audit = PASS
SEC PIT tests = 80 PASS
~~~

Next: implement the lifecycle primary-document extractor and reconcile the
regulatory candidates with security-class identity and market presence. Do not
launch the broad replay or promote filing dates as trading boundaries.

## SEC PIT lifecycle extraction and market reconciliation v0_2

~~~text
metadata = sec_pit_7t_lifecycle_v0_2
extraction = sec_pit_7t_lifecycle_extract_v0_2
market presence = sec_pit_7t_lifecycle_market_presence_v0_2
50 observations
44 security mentions
6 daily bounds
4 tape bounds
2 tape unavailable
2 cross-source boundary differences
legal lifecycle dates = 0
SEC PIT tests = 90 PASS
~~~

The next gate is targeted review of the 12 filings within/after each target
identity interval. Do not consume the superseded v0_1 runs or scale to the
parent universe.
## SEC PIT target-interval filing review v0_1

```text
run = sec_pit_7t_target_interval_filing_review_v0_1
reviewed = 12 / 12
no boundary authority = 10
observed exchange trading end candidate = 1
scheduled exchange trading end candidate = 1
legal list dates admitted = 0
legal delist dates admitted = 0
tests = 4 PASS
status = PASS_WITH_RESTRICTIONS
```

Existing ticker windows are sourced from Massive/Polygon historical reference observations. They must be preserved and compared, not silently replaced, by future SEC lifecycle evidence. Governing contract: `MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1.md`.

Next: materialize the six-identity Massive/SEC/market-bound comparison. Parent-universe scale remains unauthorized.
## Massive/SEC lifecycle window reconciliation v0_1

```text
run = sec_pit_6i_lifecycle_window_reconciliation_v0_1
rows = 6
vendor/daily start exact matches = 2
ticker reuse conflicts = 1
SEC exchange-end candidates = 1
not directly comparable = 2
legal list dates admitted = 0
legal delist dates admitted = 0
status = PASS_WITH_RESTRICTIONS
```

The pilot preserves Massive/Polygon windows, SEC evidence and market-presence bounds as separate authorities. BBBY is explicitly unresolved as ticker reuse. Parent-universe scale remains unauthorized.