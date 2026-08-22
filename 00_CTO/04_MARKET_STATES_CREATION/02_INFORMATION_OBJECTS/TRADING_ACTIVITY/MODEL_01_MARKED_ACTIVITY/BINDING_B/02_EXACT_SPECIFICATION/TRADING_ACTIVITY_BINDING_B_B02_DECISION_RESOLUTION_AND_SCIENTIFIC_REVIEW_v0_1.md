# Trading Activity Binding B B-02 decision resolution and scientific review v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_binding_b_b02_decision_resolution_and_scientific_review` |
| `document_version` | `v0_1` |
| `document_role` | `EXTERNAL_REVIEW_ADJUDICATION_AND_B02_AMENDMENT_READOUT` |
| `document_status` | `EXECUTED_10_OF_12_RESOLVED_B02_NOT_READY_FOR_FREEZE` |
| `audited_package_sha256` | `366b46d57d16179e658bd0fc99fca2b727a1fb9252a478b0514e982f0354cfad` |
| `amended_exact_spec_sha256` | `5f1ff8678bdbc2a8e1829ce002ccc2daeb111d68b7f578a0a1f2df451b8fa8fc` |
| `post_review_update` | `D07_D12_UPSTREAM_DRAFT_REFERENCES_ADDED_NO_FREEZE` |
| `human_instruction` | `NO_ABRIR_B03_NO_GENERAR_CODIGO_CREAR_PRIMERO_AUTORIDADES_D07_D12_2026-08-15` |
| `implementation_authorized_by_gate` | `false` |
| `created_at` | `2026-08-15` |

## 1. External verdict accepted

```text
B-01                              = PASS_FROZEN
B-02 scientific core             = PASS_WITH_REQUIRED_AMENDMENTS
B-02 exact specification         = NOT_READY_FOR_FREEZE
B-03                              = NOT_AUTHORIZED
```

The eight immediately closable decisions were incorporated. Read-only physical
evidence also closes the factual/capacity portion of D08, and the human's
instruction accepts the proposed static D11 host budget for the draft. D07 and
D12 remain genuinely blocked.

## 2. Resolution matrix

| Decision | Resolution | Final state |
|---|---|---|
| `D01` | `theta_fast=0.10`; `0.05/0.20` diagnostic-only | `RESOLVED` |
| `D02` | `2 * zero_session_count >= B` | `RESOLVED` |
| `D03` | Laplace formula plus insufficient-history and observed-zero branches | `RESOLVED` |
| `D04` | scientific epsilon removed; log-domain kernel ratio | `RESOLVED` |
| `D05` | conditional-positive U_B60; support `20/60`; two support companions | `RESOLVED` |
| `D06` | three families, `5*D_s` rows, 7,200 partitions, one cardinality authority | `RESOLVED` |
| `D07` | episode skeleton drafted; close/rearm and Wake-up negative-label authority absent | `OPEN` |
| `D08` | A=97 inputs verified; common heads/grid; exact effective df cap=12 | `RESOLVED` |
| `D09` | median improvement and p95 margin use `max` rules | `RESOLVED` |
| `D10` | paired five-session moving-block bootstrap, 5,000 replicates, seed fixed | `RESOLVED` |
| `D11` | machine-bound static budget annex accepted; later measurement mandatory | `RESOLVED_FOR_B02` |
| `D12` | no real final-lockbox or Wake-up label manifest exists | `OPEN` |

```text
resolved = 10 / 12
open     = 2 / 12
```

## 3. D04 implementation clarification

The scientific ratio is never repaired with `epsilon`:

```text
no event history in both kernels
-> ratio = 0
-> observation_state = OBSERVED_ZERO

positive event history
-> log_ratio = log_kernel_short - log_kernel_long

impossible/inconsistent state
-> terminal failure
```

Kernel mass must be maintained in a stable scaled or log representation.
Implementation equivalence tolerance is separate metadata and cannot change a
scientific value.

## 4. D08 physical capacity evidence

The certified A schemas were read directly with `ParquetFile`, yielding:

```text
A primary predictor inputs = 97
B full                     = 22
B renewal-only             = 10
B kernel-only              = 8
```

The common L2 logistic/hazard head caps effective degrees of freedom at 12,
excluding the intercept. This allows unequal raw dimensions without giving one
binding more effective statistical capacity.

## 5. Why code remains blocked despite the human request

The human explicitly requested continuation and code. That authorizes the
agent to pursue the next gates; it does not manufacture missing label or
lockbox authorities and does not silently override the frozen sequence:

```text
B-02 exact specification freeze
-> B-03 implementation
```

Creating B-03 now would produce code against an unfrozen comparison denominator
and undefined false-activation truth. It would violate the exact contract the
external audit passed.

## 6. B-00 disposition

When B-02 eventually freezes, it will explicitly supersede the B-00
preregistration as implementation authority while preserving B-00 as scientific
provenance. B-00 is not silently promoted from draft.

## 7. Required next external authorities

### D07

Approve exact `quiet_close_seconds`, `rearm_seconds`, assessment horizon and a
versioned Wake-up negative-label manifest.

### D12

Create and seal the exact final-lockbox manifest with a separately governed
population/selection authority and an exact Wake-up label/outcome manifest.

## 8. Current gate

```text
B-01 frozen                         = PASS
B-02 amended draft                  = 10_OF_12_RESOLVED
B-02 freeze                         = NOT_READY
B-03 code                           = NOT_AUTHORIZED
new package containing B-03 code    = BLOCKED
```
