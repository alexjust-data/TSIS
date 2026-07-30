# BT-GATE-014 - Single-Use Physical Consumer Authorization V0.5

authorization_id: BT-GATE-014-SINGLE-USE-PHYSICAL-AUTHORIZATION-V0-5
status: AUTHORIZED_NOT_CONSUMED
physical_command_execution: NOT_APPROVED_PENDING_EXTERNAL_PREEXECUTION_REVIEW

V0.3 and V0.4 are `CONSUMED_FAILED_FINAL` and cannot be reused. V0.5 is a
new single-use authorization for the same two ACIU rows and no wider scope.

## Restriction-domain authority

```text
binding_id =
market_state_restriction_domain_binding_clarification_v0_1

binding_sha256 =
b3ebace6fab7cb0a690be165f0a1706a5906dc7a729488fa1139af00c02e53a9

physical_provenance_restriction_codes =
audit lineage and physical fingerprint only

replay_consumption_restriction_codes =
bounded delivery policy

component_replay_restriction_codes =
component-labelled subsets of replay consumption policy
```

No equality or unlabeled union is permitted between physical provenance and
replay-consumption restrictions.

## Frozen scope

```text
instrument = ACIU
session = 2021-03-15
rows = 2 exact governed identities
strategy = NONE
orders = 0
fills = 0
PnL = false
provider modification = false
```

## Execution rule

This document does not approve execution by itself. The exact V0.5
pre-execution packet must pass independent external review before the command
may be run once. Any consumed success or failure permanently exhausts V0.5.

`BT-GATE-014_CLOSED_PASS = NOT_AUTHORIZED`.
