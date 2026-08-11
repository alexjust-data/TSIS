# SEC PIT seven-ticker owner-exclusion stratified probe readout v0_1

Date: `2026-08-11`

Status: `PARTIAL_PASS_SCALE_BLOCKED_ADAPTIVE_BASELINE_BACKFILL_REQUIRED`

## Decision

The bounded production-equivalent implementation generalized without
ticker-specific parser, accession, holder or arithmetic exceptions to three
eligible common-equity cases: `ALUR`, `BNAI` and `PGAC`. `BBBY`, `BGM` and
`DOMH` failed closed with causal NULLs. `CNOBP` halted before acquisition as
the preferred/depositary negative control.

This is a successful stratified discovery probe, but it does not authorize a
4,824-instrument materialization. The next implementation gate is adaptive
ownership-baseline backfill for partial amendments and special-meeting proxies,
followed by a repeat of all frozen cases and one production-equivalent probe
per planned execution shard.

```text
selection/acquisition architecture       PASS
content-addressed recovery               PASS
O/S PIT                                  5 PASS, 1 explicit NULL, 1 class HALT
owner-exclusion float                    3 PASS, 3 explicit NULL, 1 class HALT
schema/grain/hash/PIT audit              PASS across 6 executed owner runs
economic result human confirmation       PENDING
scale to 4,824                           NOT AUTHORIZED
```

## Frozen scope and acquisition

```text
selected primary documents               343
verified reusable documents                96
authorized missing documents              247
acquired                                  247/247
failed                                          0
retries                                         0
HTTP 429                                        0
actual response bytes                   29,122,331
elapsed acquisition time                ~182 seconds
network concurrency                              1
SEC request rate                           5.0 rps
```

The acquisition was hash-bound, sequential and content-addressed. It produced
pre-manifest, PID manifest, heartbeat history, live log, document performance,
performance summary and final manifest. Resume skips URLs already recorded as
`FETCHED` with verified SHA-256; a power loss therefore loses at most the
active request, not completed objects.

Telemetry identified `SEC_RATE_LIMIT_OR_NETWORK` as the provisional
bottleneck. Peak process-tree RSS was approximately `0.113 GiB`; peak private
memory was `0.592 GiB`. CPU and memory were not limiting resources, so C++ or
GPU acceleration is not indicated for acquisition.

The immutable acquisition manifest lists `PGAC` under
`security_class_halts`. That label is a manifest-semantic defect: PGAC was
already locally complete, not halted. The source classifier and regression
test now distinguish `HALT_SECURITY_CLASS` from `LOCAL_EVIDENCE_COMPLETE`.
The historical manifest is preserved rather than silently rewritten.

## O/S PIT results

All executed cases used the same O/S implementation and five canonical
sessions. The authoritative O/S iteration is `os_stratified_v0_5`.

| Ticker | O/S gate | Admitted anchors | Daily non-NULL | O/S as known | Decision |
|---|---|---:|---:|---:|---|
| `ALUR` | `PASS_WITH_RESTRICTIONS` | 2 | 5/5 | 9,262,586 | admitted |
| `BBBY` | `BLOCKED_WITH_EXPLICIT_NULLS` | 0 | 0/5 | NULL | ticker-reuse interval conflict |
| `BGM` | `PASS_WITH_RESTRICTIONS` | 2 | 5/5 | 6,006,480 | admitted Class A |
| `BNAI` | `PASS_WITH_RESTRICTIONS` | 2 | 5/5 | 44,880,795 | admitted |
| `DOMH` | `PASS_WITH_RESTRICTIONS` | 1 | 5/5 | 16,012,435 | admitted |
| `PGAC` | `PASS_WITH_RESTRICTIONS` | 2 | 5/5 | 8,869,250 | admitted Class A |
| `CNOBP` | `HALT_SECURITY_CLASS` | 0 | not executed | NULL | preferred/depositary control |

For `BBBY`, the explicit blockers are
`UNRESOLVED_INSTRUMENT_INTERVAL_STATE` and
`NO_CAUSAL_ADMITTED_OS_ANCHOR`. No observed row used a future anchor.

## Owner-exclusion PIT results

The authoritative owner iteration is `owner_stratified_v0_5`. The output is
`FLOAT_OWNER_EXCLUSION_ESTIMATE_AS_KNOWN`, not freely tradable float and not
13F institutional ownership.

| Ticker | O/S | Unique supported excluded | Float estimate | Float percent | Result |
|---|---:|---:|---:|---:|---|
| `ALUR` | 9,262,586 | 655,338 | 8,607,248 | 92.9249% | 5/5 calculated |
| `BNAI` | 44,880,795 | 11,578,292 | 33,302,503 | 74.2021% | 5/5 calculated |
| `PGAC` | 8,869,250 | 244,250 | 8,625,000 | 97.2461% | 5/5 calculated |
| `BBBY` | NULL | NULL | NULL | NULL | blocked |
| `BGM` | 6,006,480 | NULL | NULL | NULL | blocked |
| `DOMH` | 16,012,435 | NULL | NULL | NULL | blocked |
| `CNOBP` | NULL | NULL | NULL | NULL | class halt |

### ALUR

The proxy reports `655,338` shares for all current directors and executive
officers as a group. That exact aggregate supersedes nine additive management
components. `Leavitt Equity Partners III`, `Armistice Capital` and `RTW` are
correctly classified as five-percent holders and are not subtracted by
`officer_director_explicit_affiliate_v0_1`.

An earlier diagnostic iteration incorrectly treated those funds as management
because the parser recognized `5% Holders` but not `Five Percent Holders`.
That result is invalidated and retained only as diagnostic evidence.

### BNAI

The proxy management aggregate is `11,562,565`. A later Form 4 position for a
new officer contributes a causal `15,727`-share temporal update, giving
`11,578,292` supported excluded shares. Nine individual proxy management rows
are suppressed by the exact aggregate, preventing double counting.

### PGAC

Exact multi-class reconciliation establishes zero Class A shares in the
management aggregate and `244,250` Class A shares for the explicit sponsor
affiliate. Class B founder shares are not subtracted from Class A O/S.

## Correct blocked outcomes

### BBBY

`BBBY` remains blocked by `TICKER_REUSE_CONFLICT`. The same ticker string does
not establish continuity across the historic issuers and instruments in the
selected corpus. O/S is NULL, so owner-exclusion float is necessarily NULL.

### BGM

The selected `20-F/A` is Amendment No. 3. Its explanatory note says it only
restates specified Item 4 and Item 5 sections and must be read with the
original filing and earlier amendments. It contains no Item 6/major-holder
table. The current newest-baseline rule therefore selected a valid filing but
not a self-contained ownership baseline.

Required generic fix: traverse the amendment family and earlier causal annual
filings until a parseable ownership baseline is found, while retaining the
newest amendment as provenance and applying its explicitly restated sections.

### DOMH

The selected `DEF 14A` is for a special meeting and contains voting/outstanding
share information but no security-ownership table. It is not an ownership
baseline. Existing extracted historical positions also contain unresolved
economic overlaps.

Required generic fix: classify proxy purpose/content and backfill to the
latest causal annual proxy with a complete ownership table. If no complete
baseline exists, preserve NULL. Overlaps must still be resolved separately;
baseline backfill alone cannot force a result.

## Generic corrections proven by the probe

The implementation now:

1. recognizes issuer-name evidence by normalized token presence rather than an
   invalid substring over alphabetically sorted document tokens;
2. applies identity continuity to evidence that actually enters the PIT state,
   not every prehistory candidate;
3. recognizes `Directors and Named Executive Officers`, `All current
   directors...as a group`, `5%`, and `Five Percent Holders/Shareholders`;
4. preserves a single-class management aggregate;
5. admits a multi-class management aggregate only when its atomic rows
   reproduce the reported total exactly;
6. suppresses individual management components when an exact group aggregate
   is available;
7. blocks a positive aggregate plus positive explicit affiliate when their
   economic overlap cannot be disproved;
8. preserves lifecycle conflicts, unsupported class states and missing
   baselines as explicit NULLs.

No ticker-specific accession, holder, parser branch or numerical constant was
added.

## Automated certification

The versioned audit
`owner_exclusion_certification_audit_v0_1.json` reports `PASS` for all six
executed owner runs and verifies:

```text
same component hashes across cases          PASS
same ordered schema across cases            PASS
same schema version across cases            PASS
five rows per case                          PASS
unique instrument/session grain             PASS
ordered sessions                            PASS
baseline eligible no later than session     PASS
calculated arithmetic and 0-100 percent     PASS
blocked values NULL with blocker codes      PASS
all output hashes                           PASS
network requests                            0
```

This technical PASS means both calculated and fail-closed outputs obey their
contracts. It does not convert a blocked economic value into a PASS.

The complete `test_sec_pit_*.py` suite reports `142 PASS` after the final
changes.

## Scale gate and required next work

Do not launch the 4,824-instrument acquisition or materialization yet.

The next governed sequence is:

```text
implement adaptive baseline-family traversal
-> classify annual vs special proxy content
-> pair 20-F/A with the original and prior amendments
-> bounded acquisition only for newly selected baseline documents
-> repeat all seven frozen cases with one code/config version
-> variable-by-variable human audit
-> one production-equivalent probe per planned execution shard
-> versioned certification readout
-> human scale authorization
```

The three successful cases demonstrate that event extraction, exact class
allocation, management-aggregate precedence, temporal Form 4 updates and PIT
daily materialization can be automated. The blocked foreign/special-proxy
strata demonstrate that document selection is still the limiting semantic
layer.

## Evidence

```text
probe root
C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/probes/
  sec_pit_owner_exclusion_7t_stratified_v0_1_20260811T1600Z/

authoritative O/S runs
C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/runs/
  sec_pit_<ticker>_os_stratified_v0_5_20260811T1730Z/

authoritative owner runs
C:/TSIS_Data/runtime/sec_pit_stratified_owner_exclusion_v0_1/runs/
  sec_pit_<ticker>_owner_stratified_v0_5_20260811T2200Z/

acquisition run
D:/TSIS/fundamental_context/sec_pit_v0_1/runs/
  sec_pit_owner_exclusion_7t_missing_primary_v0_1_20260811T1600Z/
```

Earlier owner iterations `v0_1` through `v0_4` remain immutable diagnostic
runs. They are not authoritative and must not be combined with `v0_5`.
