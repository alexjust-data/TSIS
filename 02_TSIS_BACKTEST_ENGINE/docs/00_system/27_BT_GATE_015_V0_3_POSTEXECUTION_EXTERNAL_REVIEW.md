# BT-GATE-015 V0.3 Postexecution External Review

Status: `PASS_FAILURE_EVIDENCE_ACCEPTED_CONSUMER_CORRECTION_REQUIRED`

```text
POSTEXECUTION_FAILURE_EVIDENCE = ACCEPTED
ROOT_CAUSE = CONFIRMED_CONSUMER_DATASET_FINGERPRINT_DOMAIN_BINDING_ERROR
V0.3 = CONSUMED_FAILED_FINAL
SECOND_EXECUTION_V0.3 = PROHIBITED
BT-GATE-015_CLOSED_PASS = NOT_AUTHORIZED
```

External report SHA-256:
`faf069958509ee07d87db02e3e6bf9cc594758524d9eac77465b62e86d50e590`.

## Confirmed Cause

The provider exposes two distinct dataset fingerprints:

```text
market_state_dependency_dataset_fingerprint =
433288b634924676a3c516fac600574ed36237c3c02ca640111f17609b6c235b

market_state_availability_evidence_dataset_fingerprint =
516a27d0f8f53762fbd8e7be151c84577544c056b093b859ab1fbce45dbac416
```

The V0.3 consumer incorrectly compared the physical Event State provenance
field `source_market_state_candidate_dataset_fingerprint` with the availability
evidence fingerprint. The correct binding is:

```text
physical.source_market_state_candidate_dataset_fingerprint
=
sidecar.market_state_dependency_dataset_fingerprint
```

The Market State replay sidecar must be validated independently against
`market_state_availability_evidence_dataset_fingerprint`.

## Evidence

```text
physical files opened = 1
records scanned = 8
rows selected = 1
Event State events emitted = 0
EventStateStore inserts = 0
bounded observations = 0
orders / fills / PnL = 0 / 0 / false
```

The single-use mechanism failed closed. Provider data and provider evidence
remain accepted and unchanged. No provider modification or replacement handoff
is required.

## Required Recovery

V0.4 must preserve the two domains as unequal, validate each against its own
authority, emit field-level identity diagnostics on failure and pass an
independent pre-execution review before any new physical read.
