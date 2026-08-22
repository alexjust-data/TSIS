# Trading Activity Binding B B-01 freeze and B-02 draft handoff v0.1

## Package identity

```text
package_id
= trading_activity_binding_b_b01_freeze_b02_draft_handoff_v0_1_20260815

package_status
= CURRENT_GOVERNANCE_HANDOFF_B01_FROZEN_B02_DRAFT_NOT_FROZEN

created_at
= 2026-08-15
```

This package supersedes the earlier preparation ZIP only as the current
handoff. It does not overwrite or invalidate that audited historical package:

```text
trading_activity_binding_b_preparation_handoff_v0_1_20260815.zip
SHA-256
= 6419be68576a579c4ce6ac3ec38dab58a83d01318d8c202f29da0f61fa14e6fd
```

## Exact current gate

```text
Binding B preparation external audit       = PASS
B-01 inheritance/delta                     = FROZEN_BY_HUMAN_AFTER_EXTERNAL_AUDIT
B-02 exact specification                   = DRAFT_PREPARED_NOT_FROZEN
B-02 blocking decisions                    = 12 OPEN
B-03 implementation                        = NOT_AUTHORIZED
all-variable/all-shard probes              = NOT_AUTHORIZED
long materialization                       = NOT_AUTHORIZED
A/B comparison                             = NOT_AUTHORIZED
temporal OOS                               = NOT_AUTHORIZED
canonical promotion                        = NOT_AUTHORIZED
```

## Reading order

1. `CURRENT_STATUS_AND_HANDOFF_v0_24.md`
2. `TRADING_ACTIVITY_BINDING_B_EXTERNAL_PREPARATION_AUDIT_AND_B01_FREEZE_READOUT_v0_1.md`
3. `TRADING_ACTIVITY_BINDING_B_INHERITANCE_AND_DELTA_CONTRACT_v0_1.md`
4. `TRADING_ACTIVITY_BINDING_B_PREREGISTRATION_v0_1.md`
5. `TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md`
6. `TRADING_ACTIVITY_BINDING_B_DEVELOPMENT_AND_CERTIFICATION_PLAN_v0_1.md`
7. `TRADING_ACTIVITY_TO_WAKE_UP_COMPLETION_ROADMAP_v0_13.md`
8. `SHA256SUMS.txt`

## What the reviewer must decide

The reviewer must audit the twelve decisions `B02-D01..B02-D12` in the exact
specification: operational-time thresholds, zero baseline, silence break,
kernel epsilon, economic-unit support, family topology, false-alarm budget,
detector capacity, p95 margin, paired uncertainty, compute budget and exact
final-lockbox identity.

This package does not authorize code. A separate explicit human gate is needed
to freeze B-02, and another later gate is needed before implementation or any
runtime execution.

## Integrity

`SHA256SUMS.txt` covers every non-manifest entry in this ZIP, including this
file. The ZIP also has an external `.zip.sha256` sidecar.
