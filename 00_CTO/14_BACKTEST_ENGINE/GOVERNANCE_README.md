# Governance and inspection protocol

## Purpose

This baseline converts distributed backtester documentation into an inspectable authority layer. It was derived from the 92-entry `02_TSIS_BACKTEST_ENGINE` snapshot reviewed on 2026-07-29. It does not claim coverage outside that snapshot or outside the backtester domain.

## Evidence classifications

| Classification | Meaning |
|---|---|
| `EXPLICITLY_DOCUMENTED` | Source states the decision or status directly. |
| `VERIFIED_IN_IMPLEMENTATION` | Code and bound tests demonstrate the behavior. |
| `VERIFIED_BY_RUN` | A preserved run demonstrates the bounded physical result. |
| `INFERRED_FROM_IMPLEMENTATION` | Behavior is visible but no explicit decision record exists. |
| `CONTRADICTORY` | Current sources contain incompatible live statements. |
| `MISSING_EVIDENCE` | A claim lacks the proof needed to close it. |
| `UNRESOLVED` | A choice remains open. |

## Inspector path

For any policy:

```text
POLICY_REGISTER
  -> governing DECISION_LEDGER entry
  -> contract artifact
  -> implementation bindings
  -> acceptance-test bindings
  -> evidence run
  -> exceptions/limitations
  -> authorizing or closing gate
```

Absence from any column is meaningful and must appear as `[]`, `null`, `NOT_IMPLEMENTED`, `NOT_EVALUATED` or an exception; it must not be guessed.

## Change protocol

1. Open a gate with a bounded scope and non-goals.
2. Add or amend decisions and policies.
3. Authorize implementation separately from contract definition.
4. Implement only the authorized subset.
5. Bind tests to each policy.
6. Generate immutable evidence when physical behavior is claimed.
7. Reconcile every live status.
8. Close the gate and update the registers atomically.

## Baseline limitations

- The authority is reconstructed from the current backtester evidence, not from a pre-existing CTO record.
- Original human approver identities are not present; `TSIS_OWNER` is used as the accountable role, not as a claim about a named person.
- Historical rationales are recorded only where source evidence supports them.
- The State Provider, Event Library, Outcome Engine, ML/RL, portfolio/risk and live systems are outside scope.

