# Trading Activity D07/D12 upstream authority workstream readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_id` | `trading_activity_d07_d12_upstream_authority_workstream_readout` |
| `document_version` | `v0_1` |
| `document_role` | `EXECUTED_AUTHORITY_PREPARATION_READOUT` |
| `document_status` | `PASS_PREPARATION_HUMAN_DECISIONS_AND_CUSTODIAN_EXECUTION_PENDING` |
| `b03_authorized` | `false` |
| `created_at` | `2026-08-15` |

## 1. Human authorization interpreted

The human authorized opening two upstream workstreams while explicitly keeping
B-03 and code closed:

```text
A) Wake-up labels/negatives + denominator + false-activation counting
B) temporal-validation/final-OOS selection + exact identities + sealed manifests
```

No A/B values, detector scores, labels, outcomes, charts or PnL were inspected
for membership selection.

## 2. Authorities audited

Graphify identified the relevant institutional layers: outcomes separated from
state, event-candidate anchors, observable eligibility, calendar consumption and
the scientific validation pipeline. The physical audit then bound the current
files and exposed that the graph predates current Binding B work.

Principal evidence:

```text
Wake-up semantic definition SHA
= 1ff56c25744d069cbdac997af628c174a61215209dbd82ac8c7275bc67a9aa46

representation lifecycle SHA
= 585e64e9fecc2669077f936899aa319b272293ab397207a829bae18fc660a0a1

development sample plan SHA
= 61aa1ef8a17f9bffc4c7c8dd6f9ca4146d65a35cdebf50e2a6b5a9043bee86ec

population candidate SHA
= a777b3338d1ff2f2304e768113a5a14728d16372553081b144c943a93fa0702c

population manifest SHA
= 26a131b7c01e8b598fe0bd2dbeac8b768ddcd4103fdb1d66746508f4aca398da

market calendar SHA
= cbf1879261866d980c5a8542fadf683dbc91f96b80b7865055417a16d1e6e87c
```

## 3. Important semantic correction

The authoritative Wake-up definition states that a later failure does not
invalidate a valid Wake-up. Therefore the illustrative class
`NEGATIVE_TRANSIENT_BURST` was not adopted as a generic negative:

```text
minimally corroborated Wake-up that later fails
= POSITIVE_WAKE_UP + FAILED_ACTIVATION outcome

candidate that never meets minimum corroboration
= NEGATIVE_INSUFFICIENT_CORROBORATION
```

This preserves the separation Wake-up/In-Play/persistence.

## 4. Physical population preflight

The experimental population proxy spans 2005-01-03 through 2026-03-09 and
contains:

```text
temporal validation
= 1,425,981 candidate rows
= 367,644 ELIGIBLE_UNDER_DECLARED_PROXY rows
= 1,691 eligible instruments

final OOS
= 632,769 candidate rows
= 213,965 ELIGIBLE_UNDER_DECLARED_PROXY rows
= 1,494 eligible instruments
```

This is adequate identity supply for a restricted experiment, but the source
manifest explicitly disclaims exact point shares and a complete historical
`<$100M` population. That restriction is carried, not hidden.

## 5. Artifacts prepared

```text
WAKE_UP_LABEL_AND_NEGATIVE_DEFINITION_CONTRACT_v0_1.md
WAKE_UP_LABEL_AND_DENOMINATOR_MATERIALIZATION_CONTRACT_v0_1.md
TRADING_ACTIVITY_FALSE_ACTIVATION_COUNTING_CONTRACT_v0_1.md
TRADING_ACTIVITY_VALIDATION_AND_FINAL_OOS_SELECTION_AND_SEAL_CONTRACT_v0_1.md
TRADING_ACTIVITY_LOCKBOX_MANIFEST_SCHEMA_v0_1.json
```

They define semantic classes, abstention, outcome-only timestamps, grains,
required fields, episode matching, permitted selection inputs, prohibited
leakage, custody, access accounting and JSON validation. They are deliberately
non-executable.

## 6. Human scientific decisions still required

### D07

```text
confirmation horizon
PIT dormant-regime estimator/lookback
relative-anomaly rule
de-minimis floor
minimum distinct-cluster/source quorum
minimum coverage/timestamp resolution
episode closure and rearm
oracle/adjudication policy
early-lead and late-delay matching windows
maximum tolerable false episodes per day
```

### D12

```text
accept/reject experimental population-proxy scope
validation target size
final-OOS target size
selection salts
custodian identity
```

The current selection proposal is 60 blocks x 10 sessions in each lockbox. It
is not frozen.

## 7. Current verdict

```text
D07 semantic architecture       = PREPARED
D07 numeric authority           = OPEN_HUMAN_DECISIONS
D07 label artifacts             = NOT_CREATED
D12 selection architecture      = PREPARED
D12 source coverage             = PASS_WITH_PROXY_RESTRICTION
D12 membership decisions        = OPEN_HUMAN_DECISIONS
D12 custodian artifacts         = NOT_CREATED
B-02                             = 10/12 RESOLVED, NOT_FROZEN
B-03                             = NOT_AUTHORIZED
```

