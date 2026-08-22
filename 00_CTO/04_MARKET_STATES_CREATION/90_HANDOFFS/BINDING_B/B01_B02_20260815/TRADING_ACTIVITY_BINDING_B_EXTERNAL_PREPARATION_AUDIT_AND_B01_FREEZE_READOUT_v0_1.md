# Trading Activity Binding B external preparation audit and B-01 freeze readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_external_preparation_audit_and_b01_freeze_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXTERNAL_AUDIT_DECISION_AND_HUMAN_FREEZE_EVIDENCE` |
| `document_status` | `EXECUTED_PASS_B01_FROZEN_B02_DRAFTING_AUTHORIZED` |
| `information_object_id` | `trading_activity` |
| `binding_id` | `trading_activity_binding_b_event_time_renewal_burst_v0_1` |
| `decision_date` | `2026-08-15` |
| `implementation_authorized` | `false` |
| `probe_execution_authorized` | `false` |
| `long_materialization_authorized` | `false` |
| `a_b_comparison_authorized` | `false` |
| `temporal_oos_authorized` | `false` |

## 1. Audited package identity

The external auditor reviewed the immutable preparation handoff:

```text
trading_activity_binding_b_preparation_handoff_v0_1_20260815.zip

SHA-256
= 6419be68576a579c4ce6ac3ec38dab58a83d01318d8c202f29da0f61fa14e6fd
```

The hash was reproduced again immediately before this readout. The ZIP and its
sidecar were not regenerated or overwritten during B-01 freeze. They remain
the pre-freeze provenance reviewed by the external auditor.

## 2. Reproduced package-integrity result

The auditor reported:

```text
ZIP entries                         = 7
principal governed documents       = 5
SHA256SUMS coverage                 = 5/5 PASS
UTF-8 BOM                           = 0
CRLF                                = 0
bare CR                             = 0
null bytes                          = 0
missing final newline               = 0
code                                = 0
data                                = 0
material outputs                    = 0
```

Institutional verdict:

```text
PACKAGE_INTEGRITY                   = PASS
BINDING_B_PREPARATION_HANDOFF       = PASS
BINDING_B_SCIENTIFIC_DIRECTION      = PASS_FOR_EXACT_SPECIFICATION_DRAFTING
BINDING_B_PREREGISTRATION           = DRAFT_NOT_FROZEN
BINDING_B_INHERITANCE_DELTA         = READY_FOR_HUMAN_REVIEW_AND_FREEZE
BINDING_B_EXACT_SPECIFICATION       = PENDING_AT_AUDIT_TIME
IMPLEMENTATION                      = NOT_AUTHORIZED
A/B_COMPARISON                      = NOT_AUTHORIZED
TEMPORAL_OOS                        = NOT_AUTHORIZED
```

## 3. Mandatory findings imported from the audit

The audit identified five matters that the exact specification must close
before implementation can be considered.

### 3.1 Timestamp resolution and event ordering

The exact specification must freeze the authoritative timestamp field,
physical resolution, normalization, timestamp-cluster key, source/schema
behavior and insufficient-resolution states. It must prohibit artificial
jitter, timestamp interpolation and causal use of `physical_row_ordinal`.

Required typed reasons and companions include:

```text
TIMESTAMP_RESOLUTION_INSUFFICIENT
INSUFFICIENT_DISTINCT_CLUSTERS
EVENT_ORDER_UNRESOLVED

same_timestamp_cluster_trade_count
timestamp_resolution_us
distinct_cluster_count_available
```

### 3.2 Zero baselines and censoring

The exact specification must close `lambda0`, zero-dominated baseline,
silence-break, fast-duration, robust-surprise, epsilon, `U_B60`, session-start,
fewer-than-K and non-attainment semantics. These conditions may not become
zero silently.

Required typed reasons include:

```text
INSUFFICIENT_CLUSTER_HISTORY
ZERO_DOMINATED
BASELINE_INSUFFICIENT_HISTORY
RIGHT_CENSORED_ECONOMIC_CLOCK
```

### 3.3 Effective independence from Binding A

The A/B protocol must preregister all three B ablations before results exist:

```text
B-renewal-only
B-kernel-only
B-full
```

The primary comparison remains `Binding A` versus `B-full`. Ablations explain
which B mechanism contributes value; they cannot be selected post hoc.

### 3.4 Comparable statistical capacity

The same model family alone is insufficient. The exact comparison protocol
must freeze development-only preprocessing, missingness treatment,
regularization, search budget, effective-capacity limits and paired inference.
Uncertainty must be clustered by a governed unit such as ticker-session or
session/episode block rather than treating symbol-seconds as independent.

### 3.5 Calibration and selection

The false-activation threshold must be calibrated only on development and then
frozen for temporal validation. The primary estimand, hard non-inferiority
constraints, uncertainty method and selection margins must be explicit before
candidate comparison.

## 4. Human authorization and exact scope

After receiving the audit, the human was presented with this explicit gate:

```text
AUTORIZO EL FREEZE DE B-01 Y LA REDACCIÓN DE LA EXACT SPECIFICATION B-02
```

The human replied on `2026-08-15`:

```text
sigue
```

Within the immediately preceding explicit gate, this response authorizes:

```text
B-01 inheritance/delta freeze       = AUTHORIZED
B-02 exact-specification drafting   = AUTHORIZED
```

It does not authorize:

```text
B-02 exact-specification freeze     = NOT_AUTHORIZED
implementation                     = NOT_AUTHORIZED
unit/probe execution                = NOT_AUTHORIZED
long materialization                = NOT_AUTHORIZED
A/B comparison                      = NOT_AUTHORIZED
temporal validation or final OOS    = NOT_AUTHORIZED
canonical promotion                 = NOT_AUTHORIZED
```

## 5. Gate result

```text
B-01_EXTERNAL_REVIEW
= PASS

B-01_HUMAN_FREEZE
= PASS_AUTHORIZED_2026-08-15

frozen B-01 contract SHA-256
= 50dbfa50730ed0832711d626864a719a285195e582e6157650faca7d4a20ffd9

B-02_DRAFTING
= AUTHORIZED

B-02_FREEZE
= PENDING_SEPARATE_HUMAN_REVIEW
```

The frozen B-01 contract must cite this readout and import all five audit
findings. B-02 must distinguish frozen inherited rules from proposed numerical
choices and unresolved blocking decisions. No code may treat a proposed B-02
value as authority.

## 6. Next governed gate

```text
review TRADING_ACTIVITY_BINDING_B_EXACT_SPECIFICATION_v0_1.md
-> close every BLOCKING_B02_FREEZE decision
-> independent scientific review
-> explicit human B-02 freeze decision
```

Only a later explicit authorization may open B-03 implementation.
