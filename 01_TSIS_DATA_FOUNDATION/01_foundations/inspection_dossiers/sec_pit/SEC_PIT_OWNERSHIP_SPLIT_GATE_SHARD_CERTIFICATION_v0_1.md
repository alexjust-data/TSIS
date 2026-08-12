# SEC PIT ownership split gate shard certification v0.1

Status: `PASS_BOUNDED_99_CASE_RERUN_AUTHORIZED`

Date: `2026-08-12`

Scope: fail-closed treatment of corporate-action scale changes between an
ownership baseline measurement and a target session. This gate authorizes only
a new versioned 99-case rerun and does not authorize 4,824 instruments.

## Discovery

The parser-improved v0.6 batch completed 99/99 cases, zero failures and zero
network requests. It raised full float coverage from 11 to 15 cases without
regressing any previously calculated case. New cases were ATYR, EJH, PLL and
SYTA. `AMENDMENT_FAMILY_UNRESOLVED` fell from 38 to 20 cases.

Readable-value review found that MULN's newly visible baseline produced
`EXCLUDED_SHARES_EXCEED_OS`. The governed corporate-actions dataset proves that
multiple reverse splits occurred between the ownership baseline and the target
sessions. Carrying the unadjusted baseline through those events is invalid.

The review also distinguished SYTA: its next recorded split is 2025-10-07,
after all five bounded sessions (2025-09-30 through 2025-10-06). It must not be
blocked merely because a later split exists. SYTA still uses a stale O/S anchor;
that quality dimension is separate and remains pending explicit policy.

## Implemented fail-closed rule

For each daily float row:

```text
ownership baseline measurement_at
-> any valid split execution_date <= target session?
-> yes: NULL + OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED
-> no: continue existing owner-exclusion resolver
```

The gate intentionally does not apply an automatic ratio yet. Fractional-share
treatment, cash-in-lieu, class applicability, multiple splits and effective
session semantics require their own certification.

The per-ticker split parquet is an explicit config input. Its physical path and
SHA-256 are persisted in every pre/final manifest. No ticker-specific rule was
introduced.

## Four-shard production-equivalent probe

Evidence root:
`C:/TSIS_Data/runtime/sec_pit_100_case_ownership_split_gate_shard_probe_v0_1`

| Shard | Ticker | Expected result | Observed |
|---:|---|---|---|
| 0 | ADMP | preserve prior content blocker | 0/5, `BASELINE_DOCUMENT_PARTIAL` |
| 1 | MULN | block intervening reverse splits | 0/5, `OWNERSHIP_SPLIT_ADJUSTMENT_UNRESOLVED` |
| 2 | CYTO | preserve identity/content blockers | 0/5, fail-closed unchanged |
| 3 | SYTA | later split must not contaminate window | 5/5 calculated |

All probes used `float_estimate.py` SHA-256
`d5cd4b410aad25956c8037013062100275ceec054861f1ac888234e95ebd234b`,
made zero network requests, preserved stable output schema and emitted the
split-source SHA-256 in each manifest.

## Gate decision

v0.6 remains a completed and auditable diagnostic batch, but is superseded for
scale-gate decisions because it predates the split gate. A fresh 99-case batch
must use a new root and run identity, rebuild both O/S and ownership with the
updated config, and must not resume or mix earlier outputs.

Scale to 4,824 remains `NOT_GRANTED`.
