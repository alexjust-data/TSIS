# Daily Eligible Universe restricted consumption gate readout v0.1

## 0. Artifact control

| Field | Value |
|---|---|
| `document_role` | `EXECUTED_CONSUMPTION_AND_DENOMINATOR_GATE_READOUT` |
| `document_status` | `PASS_RESTRICTED_EXPERIMENTAL_NOT_CANONICAL` |
| `run_id` | `daily_eligible_universe_restricted_consumption_gate_v0_1_20260815` |
| `executed_at` | `2026-08-15` |
| `network_access` | `NOT_USED` |

## 1. Decision

The existing presession population candidate is admitted as the hash-bound
membership authority for the restricted Trading Activity A/B experiment.

```text
Daily Eligible Universe Selector owns membership       PASS
Bindings recalculate price/cap thresholds              false
canonical screener promotion                           false
validation/final-OOS target generation                 not authorized
Wake-up label materialization                          not authorized
Binding B implementation                               not authorized
```

## 2. Executed evidence

```text
candidate rows                            7,369,699
eligible rows                             1,417,316
candidate/member identities unique        PASS
eligible selector semantics exact         PASS
development targets                       2,400 / 2,400
development targets eligible              2,400 / 2,400
calendar/grid mismatches                   0
early-close targets                        27
logical development symbol-seconds         55,866,000
physical interval rows                     2,400
builder hard checks                        23 / 23 PASS
independent validator checks               25 / 25 PASS
```

Split candidate-pool evidence remains explicit:

| Split | Eligible instrument-session rows | Eligible instruments |
|---|---:|---:|
| Development | 798,761 | 1,841 |
| Temporal validation | 367,644 | 1,691 |
| Engineering-exposed embargo | 36,946 | 930 |
| Final temporal OOS | 213,965 | 1,494 |

These are candidate-pool memberships, not selected lockbox targets and not
flat symbol-second materializations.

## 3. Hashes

```text
config
669b3e7b170fa978f526d7f3872019b52dcb9b670e2c24be822e1d076a2390fb

builder
d3de5694a199977cba7e553fd7dc317e39f8b5e3e623e159e39ccaecbce7cde0

independent validator
1e54ba4c613d47a0dbd0d4f1d121c3ab552304a62c92c662dc88546cc58a44c2

final manifest
6dc68a5ece74c364177296adade5e81902addbb7d1333eac1fa2b76eeeedf47e

consumption manifest
c1ed29f2764e98bef0f4b4c90144cfce4c56db7d3d7d84b33255b50418b355d7

independent validation
d0c2f001d749f20c472faa8171e399aa1621b313ca39468a296ee93e97bcdb0e

development denominator intervals
11ea435f69aa43e239b5b926a4788970686dfd7f24fb3a0533de7322e62615d4
```

## 4. Why interval encoding is exact

Binding A's frozen decision grid is:

```text
session_open_utc < decision_timestamp < session_close_utc
```

at integer UTC seconds. Each interval row stores open, close, first decision,
last decision and exact decision-point count. Expansion is deterministic and
produces the same 55,866,000 logical identities without storing a redundant
55.9-million-row identity table.

## 5. Tests

```text
python -m pytest
  tests/test_daily_eligible_universe_consumption_gate.py
  tests/test_validate_daily_eligible_universe_consumption_gate.py

result = 5 passed
```

## 6. Restrictions

The source remains a fixed-parent-universe, prior-close and weighted-average
shares proxy. It is not exact historical market cap, historical float, a full
US `<$100M` census or a live canonical screener.

No validation or final-OOS target identities, labels, detector metrics or
outcomes were created or inspected.

## 7. Next gate

The development selector/denominator blocker is closed. The next unresolved
authority is human-scientific:

```text
D07
= exact Wake-up label/counting numbers and false-episode tolerance

D12
= validation/final-OOS target counts, salts and independent custodian
```

B-03 remains closed until D07/D12 are resolved, independently audited and
B-02 receives an explicit human freeze.
