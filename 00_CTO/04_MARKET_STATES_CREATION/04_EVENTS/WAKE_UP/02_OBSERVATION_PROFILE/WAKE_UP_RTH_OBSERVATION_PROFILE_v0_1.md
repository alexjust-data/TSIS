# Wake-up RTH observation profile v0.1

Status: `DRAFT_FOR_EXPLICIT_HUMAN_FREEZE`

## Claim permitido

```text
first observable Trading Activity transition during governed RTH
after an observed within-scope dormant interval
```

## Scope

```text
calendar = governed XNYS calendar
open boundary = exclusive
close boundary = exclusive
decision grid = symbol-second
source = trades_ticks_prod_2005_2026_legacy_rth
simulated latency = 1000 ms
population = frozen TA-3 development targets
```

Este perfil se limita a casos cuya actividad dormida se observa después de la
apertura y cuya transición ocurre antes del cierre. No autoriza claims de
premarket, after-hours ni full-session.

## Estados

```text
RTH_ADJUDICABLE
= prior within-scope evidence is sufficient
   and candidate/negative assessment interval closes before session close

RTH_INSUFFICIENT_PRIOR_OBSERVATION
= the selected dormant lookback is not fully observable after the open

RTH_RIGHT_CENSORED_CONFIRMATION
= the confirmation horizon extends beyond session close

UNAVAILABLE_SOURCE_OR_QUALITY
= source/coverage/timestamp evidence cannot support adjudication

OUT_OF_SCOPE
= target is not a governed TA-3 development target or lies outside RTH
```

The present experiment intentionally excludes
`LEFT_CENSORED_ACTIVE_AT_SCOPE_START` from candidate calibration because the
human has chosen to study only instruments observed dormant after 09:30 and
waking within RTH. Such rows remain accounted outside the primary panel; they
are never rewritten as negatives.

## Metric inclusion

Only `RTH_ADJUDICABLE` cases may enter primary agreement, onset-delay and false-
activation calculations. Other states remain in accounting with their typed
reason.

## Freeze dependency

The profile becomes executable only together with the calibration protocol and
the frozen WUL decisions. This document does not select WUL-D01…D08.

