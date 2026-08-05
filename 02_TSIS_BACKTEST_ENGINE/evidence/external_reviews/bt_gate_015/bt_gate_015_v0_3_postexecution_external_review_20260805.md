# BT-GATE-015 V0.3 Post-Execution External Review

## Artifact Under Review

```text
C:\TSIS_Data\02_TSIS_BACKTEST_ENGINE\deliverables\
bt_gate_015_v0_3_consumed_failure_postexecution_packet_r2_20260805T111834Z.zip

SHA-256 =
546f64cb20b81db368d894d0ebc0864fd9487fe21d49b627ad7071eeef0f79f6
```

## Verdict

```text
POSTEXECUTION_FAILURE_EVIDENCE = ACCEPTED

ROOT_CAUSE =
CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR

V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3 = PROHIBITED

BT-GATE-015 = OPEN_TARGETED_CORRECTION_REQUIRED
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
NEW_SINGLE_USE_AUTHORIZATION = NOT_AUTHORIZED
```

The failure was fail-closed. No Event State event, store insert or observation was
produced. The provider candidate and provider sidecar are not shown to be
defective by this audit.

## Reproduced Results

```text
ZIP entries = 581
manifest declared files = 580
missing / extras = 0 / 0
hash / size mismatches = 0 / 0
duplicates / unsafe paths / symlinks / encryption = 0 / 0 / 0 / 0
ZIP CRC = PASS
physical Event State files included = 0

Focused V0.3 = 21/21 PASS
Full repository suite = 256/256 PASS
Governance = PASS, 146/146 hashes

physical files opened = 1
physical records scanned = 8
physical rows selected = 1
Market State dependencies = 1
Event State events = 0
store inserts = 0
observations = 0
```

The included immutable pre-execution packet hashes to:

```text
52aab61b0f6343448d47ae988bc575df1ae86d485c4c4d3ab854bfdd554c47fe
```

The included provider handoffs hash to:

```text
contract handoff =
b7a4783d0ab64ffaf37fbfdf2ee76dffacbe9b14cf3f059891908c87116369b2

provider completion =
3a6bf3ca04c0428a1728e1719cd6aeaea6bfaef43e12fb83939dde3cb6cb85d9
```

## Finding 1 - Confirmed Root Cause

Severity: HIGH, execution-blocking consumer defect.

The provider defines two distinct Market State dataset fingerprints:

```text
market_state_dependency_dataset_fingerprint =
433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

market_state_availability_evidence_dataset_fingerprint =
516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
```

The Event State candidate was built from the first dataset. The provider
bounded-execution runner writes:

```python
"source_market_state_candidate_dataset_fingerprint":
    ms_final["candidate_dataset_fingerprint"]
```

The provider candidate output manifest and lineage both bind that value to
`433288...`. The replay sidecar separately preserves `433288...` as the
dependency dataset and `516a27...` as the availability-evidence dataset.

The backtester consumer instead compares the physical field to the second
dataset:

```python
"source_market_state_candidate_dataset_fingerprint": sidecar[
    "market_state_availability_evidence_dataset_fingerprint"
]
```

That comparison is false by design:

```text
physical source authority == dependency dataset = true
physical source authority == availability dataset = false
```

The correct binding is:

```text
physical row.source_market_state_candidate_dataset_fingerprint
<-> sidecar.market_state_dependency_dataset_fingerprint
```

The availability dataset must remain independently validated against the Market
State replay sidecar. Cross-dataset equivalence remains governed by exact row ID
and state fingerprint; it does not make the two dataset fingerprints identical.

## Finding 2 - Positive Fixture Erases the Domain Distinction

Severity: HIGH, test gap that allowed the execution defect.

The synthetic fixture overwrites the Market State sidecar dataset fingerprint
with the Event State availability-evidence fingerprint and then copies that value
into the physical Event State row. This makes the incorrect consumer comparison
pass while failing to represent the accepted provider handoff.

Required regression behavior:

```text
positive fixture:
  physical source dataset = 433288...
  dependency dataset = 433288...
  availability dataset = 516a27...
  result = PASS

negative fixture, domains swapped:
  result = FAIL_EVENT_STATE_IDENTITY_MISMATCH
```

## Finding 3 - Failure Evidence Is Not Field-Diagnostic

Severity: MEDIUM.

The consumer aggregates all physical-sidecar identity comparisons into one
`any(...)` and raises only:

```text
FAIL_EVENT_STATE_IDENTITY_MISMATCH: physical-sidecar identity
```

The failure manifest therefore cannot identify the field, expected value and
observed value. The next implementation must emit a bounded diagnostic such as:

```text
identity_mismatches = [
  {
    field,
    expected_sha256_or_value,
    observed_sha256_or_value,
    expected_authority
  }
]
```

No scientific payload values need to be exposed.

## Finding 4 - Authorization State Retains Pre-Execution Claims

Severity: MEDIUM, institutional-state inconsistency.

The canonical V0.3 state correctly records one consumption and the consumed run,
but still declares:

```text
event_state_physical_read = NOT_EXECUTED
physical_command_status = NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW
preexecution_review_status = NOT_EXECUTED
```

Those fields contradict the durable run evidence. The state must preserve
`CONSUMED_FAILED_FINAL` while recording that execution occurred once and failed
closed. This correction must not reset, recreate or reuse V0.3.

## Minimal Correction

1. Change only the physical-row dataset binding in the backtester consumer from
   `market_state_availability_evidence_dataset_fingerprint` to
   `market_state_dependency_dataset_fingerprint`.
2. Preserve the independent validation of the Market State replay sidecar against
   `market_state_availability_evidence_dataset_fingerprint`.
3. Rebuild the positive synthetic fixture with distinct `433288...` and
   `516a27...` domains.
4. Add positive and negative cross-domain regressions.
5. Emit field-level bounded mismatch diagnostics in failure evidence.
6. Synchronize the consumed V0.3 state fields without changing its single-use
   terminal status.
7. Run the complete non-physical suite and an exact vertical dry-run that stops
   before authorization consumption and candidate opening.
8. Only after a new external pre-execution PASS may a new authorization version be
   issued. V0.3 remains permanently consumed.

## Ownership

```text
primary correction owner = backtester / BT-GATE-015 consumer
provider modification required = no
provider candidate rebuild required = no
new provider evidence required = no
```

The accepted provider artifacts already preserve both fingerprint domains and the
cross-dataset row equivalence separately.
