# SEC PIT Massive structured evidence consumption policy v0.1

Status: **BLOCKED_UNTIL_CERTIFIED**

## Allowed before promotion

- integrity and schema inspection;
- vendor/source comparison;
- coverage and missingness measurement;
- reconciliation research inside a versioned experiment;
- storage and operational benchmarking.

## Prohibited before promotion

- use as canonical float, shares outstanding or market-state truth;
- silent replacement of SEC source-of-truth artifacts;
- direct training/backtest/live consumption;
- inference that retrieval time equals filing availability time;
- forward-filled values without explicit availability/staleness semantics;
- use of 8-K text or 13F under the direct-lane authorization;
- redistribution or retention beyond confirmed license rights.

## Temporal rule

Filing date, report period, transaction date and retrieval time are distinct.
Consumers must select a contractually valid availability timestamp and prove
PIT causality. No future outcome may enter feature/state materializations.

## Endpoint beta rule

Massive SEC endpoints are treated as early-access/beta. Unknown fields may be
preserved in raw evidence, but schema changes cannot be promoted silently.
Required identity-field loss is a hard failure.

## Admission

Consumption remains BLOCKED until the dataset registry points to a complete
run, final integrity audit, versioned schema readout, license evidence and
explicit promotion decision.
