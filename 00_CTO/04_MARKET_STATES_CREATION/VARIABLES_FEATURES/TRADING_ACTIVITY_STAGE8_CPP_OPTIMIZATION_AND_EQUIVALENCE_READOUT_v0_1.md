# Trading Activity Stage 8 C++ optimization and equivalence readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `IMPLEMENTATION_INCIDENT_AND_EQUIVALENCE_READOUT` |
| `document_status` | `ACTIVE_BLOCKING_READOUT` |
| `snapshot_at` | `2026-08-11` |
| `scope` | `Trading Activity Binding A v0.2 / Stage 8 PIT baseline and surprise` |
| `python_role` | `FROZEN_SEMANTIC_ORACLE` |
| `cpp_role` | `CANDIDATE_EXECUTION_ENGINE_ONLY` |
| `promotion_status` | `NOT_AUTHORIZED` |
| `broad_materialization_authorized` | `false` |

## 1. Non-negotiable invariant

C++ is only an implementation optimization. It is not a new feature version,
formula, schema, missingness policy, PIT policy or lineage authority.

```text
Python reference semantics
= C++ semantics

for every row, variable, formula, column, column order, dtype, NULL mask,
calculation state, PIT reference field, identity field and lineage field.
```

Any difference is a complete equivalence failure. Attractive speed, low memory,
passing compilation or passing narrow unit tests cannot override this rule.

## 2. Runtime interruption

The TA-3 broad Binding A run was deliberately paused after Stage 8 was observed
as a single-core Python bottleneck. The pause manifests record:

```text
status = PAUSED_FOR_HARDWARE_OPTIMIZATION
reason = STAGE_8_SINGLE_CORE_PYTHON_BOTTLENECK
resume_without_revalidation = PROHIBITED
complete_partitions_preserved = true
```

Power was then lost. No Trading Activity worker survived the interruption.
Heartbeats that still report `RUNNING` are stale and do not override process
liveness, pause manifests or block final manifests.

Physical reconciliation on 2026-08-11 found 23 `COMPLETE` block final manifests:

```text
ba2r2_s0of4 = 8 complete
ba2r2_s1of4 = 15 complete
failed complete blocks = 0
```

The shard-0 pause manifest reports seven completed blocks, but eight physical
block final manifests predate the pause. Block final manifests and output hashes
are the granular authority. No output was deleted or rewritten.

## 3. Prototype result and discovered failure

Representative production session:

```text
ticker = ACU
session_date = 2012-04-18
current rows = 116,995
prior rows = 15,155,350
output rows = 350,985
baseline candidates = B20 / B60 / B120
```

The first C++ prototype reduced the kernel from 210.990 seconds to 29.139
seconds and peak RSS from 9.763 GB to approximately 3.742 GB. That result is
performance evidence only and is invalid as equivalence evidence.

Full-frame comparison found:

```text
reference_session_count mismatches = 54,000 rows
first_reference_date mismatches     = 1,074 rows
last_reference_date mismatches      = 1,074 rows
equivalence verdict                 = FAIL
```

The former wrapper selected one global list of available dates. The Python
reference selects dates separately for each `(clock_minute_et, window_seconds)`
group. Sparse histories therefore produced incorrect reference-session metadata
in C++ even when many downstream numeric values appeared equal.

## 4. Correction

The candidate C++ kernel now constructs causal historical date sets per
`(clock_minute_et, window_seconds)` group and applies each B20/B60/B120 lookback
inside that group. It emits group-specific:

- `reference_session_count`;
- `first_reference_date`;
- `last_reference_date`;
- selected observation count;
- maximum input availability;
- baseline calculation and duration states;
- all distributions, percentiles, ratios and duration compression fields.

The Python runner remains unchanged and still calls the Python reference. C++
has not been integrated into broad production execution.

## 5. Executed validation

### 5.1 Unit and adversarial tests

```text
pytest baseline/vectorized/native/C++/comparator suite = 8 PASS
```

The adversarial fixture covers group-specific sparse session histories,
B20/B60/B120, insufficient history, source missingness, non-calculated rows,
zero-dominated history, a current group with no prior history and fixed ET
minutes across DST.

### 5.2 Production-equivalent representative comparison

The corrected benchmark wrote a new artifact under:

```text
D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/
benchmarks/stage8_cpp_group_history_fix_v0_2
```

Result:

```text
reference Parquet SHA-256 = 6f2a4b8c4ecac1eebec2d22be640235a5876c628dd897e852ba583212b1900e1
corrected C++ SHA-256     = 6f2a4b8c4ecac1eebec2d22be640235a5876c628dd897e852ba583212b1900e1
kernel seconds           = 41.409
total seconds            = 46.698
peak RSS bytes           = 3,802,042,368
kernel speedup           = approximately 5.10x
total speedup            = approximately 4.67x
```

### 5.3 End-to-end equivalence-gate smoke

The governed comparator smoke is persisted under:

```text
D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/
benchmarks/ta8_eq_smoke_20260811_v4
```

```text
status                    = PASS
blocks                    = 1
sessions                  = 1
rows                      = 350,985
contract mismatches       = 0
exact value mismatches    = 0
dtype mismatches          = 0
NULL-mask mismatches      = 0
Parquet SHA-256 exact     = true
kernel seconds            = 43.105
require exact value match = true
native module SHA-256     = 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
```

The preceding smoke attempt with the longer runtime path failed before output
comparison due Windows `MAX_PATH`. Its failure manifest is preserved. The v4
runner uses compact benchmark-only paths while retaining complete IDs in the
manifests.

## 6. Limited stratified gate executed: PASS_EXACT

Executable gate:

```text
01_TSIS_DATA_FOUNDATION/scripts/
validate_trading_activity_baseline_cpp_block_equivalence.py
```

Governed plan:

```text
TRADING_ACTIVITY_STAGE8_CPP_BLOCK_EQUIVALENCE_PLAN_v0_1.json
```

The plan compares two complete Python blocks of ten sessions each, one from
shard 0 and one from shard 1, plus five adversarial sessions from four other
blocks. The 25 preserved Python partitions are the oracle; only C++ is
recalculated. Selection covers the original failure case, post-DST execution,
fall and spring DST boundaries, non-nominal reference-session histories,
insufficient history, zero-dominated states and extreme NULL patterns. It
requires:

```text
row count and row order exact
column names and order exact
dtypes exact
NULL masks exact
all values, including floating values, exact
rtol=1e-12 and atol=1e-12 diagnostics reported but never sufficient for PASS
exact-difference count = 0 required
serialized Parquet SHA-256 exact
```

The human-authorized run was executed under:

```text
D:/TSIS/IO/wake_up/trading_activity/pit_marked_activity/binding_a_v02/
benchmarks/ta8_eq_limited_v0_1_20260811T010000Z
```

Final manifest result:

```text
status                         = PASS
complete source blocks covered = 2
targeted source blocks covered = 4
sessions                       = 25/25
rows compared                  = 8,612,625
contract mismatches            = 0
exact value mismatches         = 0
all dtypes exact               = true
Parquet SHA-256 exact          = 25/25
kernel seconds total           = 813.294
kernel seconds mean            = 32.532
kernel seconds min/max         = 26.616 / 46.599
wall-clock elapsed seconds     = 927.500
native module SHA-256          = 5fe3682d593c2563e137cc1790759c6c2cd624bbdfff3a1d6b0970e06dbbb4c4
promotion status               = NOT_AUTHORIZED
broad materialization          = false
```

The preregistered plan remains byte-preserved rather than being rewritten with
post-run state. Its SHA-256 is
`2bd29bda872d69db4064ff648239ec06014583f4aede76b7fc91292ab97a102a`,
exactly the `plan_sha256` recorded by the final manifest. Execution status
lives in the immutable runtime manifest and this readout.

The non-standard DST session cardinalities are why the exact row total is not
`25 * 350,985`; cardinality matched the Python oracle session by session. The
run emitted the required pre-manifest, PID manifest, heartbeat, live log and
final manifest and was observed by a separate monitor.

This result closes the limited comparison gate only. One mismatch would have
produced `FAIL`; none occurred. C++ integration, resume and broad
materialization remain prohibited until the gates in section 7 are completed.

## 7. Gates after limited stratified equivalence

Even a limited stratified equivalence `PASS` does not authorize immediate
continuation.
Changing the execution engine changes the code fingerprint. The required
sequence is:

```text
2 complete blocks + 5 adversarial sessions Python/C++ equivalence PASS
-> integrate C++ behind an explicit engine/version fingerprint
-> rerun one bounded production-equivalent probe on each of 4 shards
-> variable-by-variable and cross-shard certification PASS
-> human governed gate PASS
-> launch a new versioned broad run from zero
```

The 23 preserved Python blocks are oracle/evidence. They must not be mixed with
new C++ partitions under the old run IDs.

## 8. SEC PIT boundary

SEC PIT is a separate pending workstream governed under:

```text
00_CTO/04_MARKET_STATES_CREATION/_DESCAGRA_DATOS_NECESARIA_/
```

Its existing evidence is preserved, but it is not the active implementation
lane for this recovery. Continue SEC PIT only after the Trading Activity Stage-8
equivalence, four-shard revalidation and governed materialization decision are
closed.
