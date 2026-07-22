# `trades` Validators

## Purpose

This document defines the validator families that govern `trades` at institutional level.

The key principle is that validators must be layered. The historical audit showed that a single monolithic judgement would incorrectly mix:

- physical file validity
- reference disagreement
- microstructure effects
- and final acceptance policy

Therefore `trades` validators are organized into three layers:

1. integrity validators
2. comparability validators
3. acceptance-policy validators

## Layer 1: Integrity Validators

These validators answer:

- is the raw file structurally readable and physically coherent as a trade tape?

### V1. Timestamp Parseability

Checks:

- timestamps exist
- timestamps parse into a coherent intraday sequence
- session-day mapping is recoverable

Why:

A tape with unusable timestamps cannot support execution or microstructure analysis.

### V2. Non-negative Price

Checks:

- `price >= 0`

Why:

Negative executed price is physically invalid under the current scope.

### V3. Non-negative Size

Checks:

- `size >= 0`

Why:

Negative executed size is physically invalid.

### V4. Stable File Identity

Checks:

- one session date per file
- stable ticker identity inside file

Why:

Files that combine days or instruments break the file-level audit unit.

## Layer 2: Comparability Validators

These validators answer:

- how and where does the tape disagree with reference layers?
- is the disagreement plausibly explained by tape context, scale, or reference problems?

### V5. Outside `daily` Range

Checks:

- prints outside daily high/low envelope
- side decomposition: `below_only`, `above_only`, `both`
- magnitude in absolute and relative buckets

Why:

This is historically the dominant break signal, but it is not sufficient by itself to call the tape bad.

### V6. Outside `1m` Range

Checks:

- prints outside `1m` reference envelope
- confirmation of daily conflicts against a finer intraday reference

Why:

The historical notebooks show that `1m` confirmation is one of the strongest escalators of seriousness. But even here, confirmation may still reflect scale mismatch rather than intrinsic tape failure.

### V7. Duplicate Burden

Checks:

- exact duplicate rows present
- duplicate excess ratio and severity

Why:

Duplicates contaminate apparent activity and volume structure, and were a major component of the historical stress population.

### V8. Session Profile

Checks:

- regular-session share
- off-session activity
- mismatches between inherited session metrics and raw recompute

Why:

The `05` audit showed that inherited off-session diagnostics were partly unreliable, so validators must privilege raw recompute over legacy metrics.

### V9. Odd-Lot vs Round-Lot Core

Checks:

- odd-lot share
- round-lot share
- conflict inside conservative `regular + round_lot` core

Why:

This is one of the decisive findings of the historical methodology sample: much of the conflict concentrates outside the round-lot core. That changes interpretation from bad tape to microstructure comparability.

### V10. Condition-Code Structure

Checks:

- individual sale-condition frequencies
- condition combinations
- conflict concentration by code / combo

Why:

Not all sale conditions behave equally. Treating them as equivalent would destroy explanatory power.

### V11. Scale-Mismatch Detection

Checks:

- plausible multiplicative scale factors against references
- bucketization of factors (`~4x`, `~5x`, `~10x`, etc.)

Why:

This validator is crucial. The historical file-acceptance work showed that many apparently extreme cases are better explained as `reference_scale_mismatch` than as tape corruption.

## Layer 3: Acceptance-Policy Validators

These validators do not re-measure the file. They map lower-layer evidence into final labels.

### V12. Conservative Good Filter

Goal:

- identify the extremely narrow tail that remains acceptable as `good`

Historical implication:

- this bucket is tiny in full closeout (`106` files)
- it must stay conservative

### V13. Reference-Scale-Mismatch Filter

Goal:

- isolate files where disagreement is dominated by scaling inconsistency rather than tape failure

### V14. Microstructure Review Filter

Goal:

- isolate files where odd-lot structure, session context or sale-condition anatomy dominate interpretation

### V15. No-`1m`-Reference Review Filter

Goal:

- isolate files where daily disagreement exists but `1m` support is unavailable or insufficient

### V16. `1m`-Reference-Alignment Review Filter

Goal:

- isolate files where `daily` / `VWAP` style readings and `1m` core comparisons create a meaningful unresolved contradiction

### V17. Residual `bad_data` Filter

Goal:

- reserve a final hard-negative tail after scale, session, odd-lot and reference-coverage explanations are drained away

This filter is what protects the rest of the stack from over-optimistic reinterpretation.

## Validator Output Philosophy

A validator should never emit more meaning than it proves.

Examples:

- `outside_daily_range` proves disagreement against `daily`, not bad tape
- `outside_1m_range` proves disagreement against `1m`, not automatically bad tape
- high odd-lot conflict proves microstructure difficulty, not portfolio unusability
- detected scale factor proves comparability tension, not corruption

The final acceptance layer is responsible for combining these signals conservatively.

## Scientific / Institutional Rationale

These layered validators are consistent with:

- O'Hara and Hasbrouck: raw prints must be interpreted in market-state context
- Menkveld: small-size and non-core activity can structurally diverge from benchmark-like flow
- Lopez de Prado: labels must respect the data-generating process, not just validation artifacts

## Current Status

The historical `v2` chain already contains these ideas in operational form. This document formalizes them as the validator contract that `01_foundations` must preserve when `trades` is promoted further.
