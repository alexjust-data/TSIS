# Trading Activity Trade Eligibility Pilot Readout v0_1

## 1. Decision

```text
PILOT_EXECUTION
= PASS

OBSERVED_CONDITION_COVERAGE
= PASS_WITH_RESTRICTIONS

UNKNOWN_CONDITION_EXPOSURE
= ZERO_IN_THIS_PILOT

FULL_UNIVERSE_CLAIM
= FALSE

STRATIFIED_SAMPLE_CLAIM
= FALSE

BINDING_A_CANONICAL_PROMOTION
= NOT_AUTHORIZED
```

## 2. Inputs gobernados

Coverage sidecar:

```text
tests/test_runs/
trading_activity_rth_coverage_sidecar_pilot_20260806T215945Z/
trading_activity_rth_coverage_sidecar_candidate_v0_1.csv

SHA256
=
fe457c05f35526571959899dc2f245b92a2bc03b5c04126d00f98f3eb066ab93
```

Condition policy matrix:

```text
tests/third_party_evidence/massive/market_operations/
snapshot_20260806T220504Z/policy_matrix_candidate_v0_1/
trading_activity_trade_condition_policy_matrix_candidate_v0_1.csv

SHA256
=
b2f208496809cb970437d04024d93bfb98780b54b5d790091362aa145eb9635f
```

## 3. Ejecucion

```text
task_count               = 100
downloaded_ok            = 83
downloaded_empty         = 17
evaluated_trade_rows     = 23,855
activity_eligible        = 23,604
activity_ineligible      = 251
unknown_fail_closed      = 0
exact_duplicate_flags    = 98
price_forming_eligible   = 15,157
```

```text
activity_eligible_fraction
=
0.9894780968350451
```

La politica no elimina los 98 duplicados exactos detectados. Los conserva y
emite `EXACT_DUPLICATE_RESEARCH_FLAG` porque el schema legacy no contiene
identidad de mensaje o trade.

## 4. Condiciones observadas

El piloto contiene 14 condition IDs:

```text
2, 7, 9, 10, 12, 14, 16,
17, 31, 32, 37, 41, 52, 53
```

Todos poseen decision candidata explicita en la matriz. Esto explica:

```text
unknown_fail_closed = 0
```

No demuestra que los otros 41 codigos actuales de Massive esten resueltos. En
la matriz permanecen `KNOWN_BUT_UNREVIEWED_FAIL_CLOSED`.

## 5. Principales exclusiones

Entre los reason codes de exclusion o degradacion aparecen:

```text
OFFICIAL_MARKER_NOT_TRANSACTION_ACTIVITY       = 163
DERIVATIVELY_PRICED_FAIL_CLOSED                 = 52
OUTSIDE_OR_NONCONTEMPORANEOUS_RTH_ACTIVITY      = 11
LEGACY_TIMING_AMBIGUOUS_FAIL_CLOSED              = 8
OUT_OF_SEQUENCE_NOT_CAUSAL_ACTIVITY              = 7
CONTINGENT_TRANSACTION_FAIL_CLOSED               = 5
QUALIFIED_CONTINGENT_TRANSACTION_FAIL_CLOSED     = 5
NONPOSITIVE_OR_INVALID_PRICE                     = 5
NON_CAUSAL_AVERAGE_PRICE_REPORT                  = 2
SPECIAL_SETTLEMENT_FAIL_CLOSED                   = 2
```

Los reason codes pueden coexistir en una misma fila y no deben sumarse como
filas mutuamente exclusivas.

## 6. Outputs

```text
tests/test_runs/
trading_activity_trade_eligibility_pilot_20260806T222300Z/
```

Per-file output:

```text
trading_activity_trade_eligibility_pilot_per_file_v0_1.csv
SHA256
=
bb8ccc20580974470fc3b005642f67542a54b7154eb0dd21b58112f7b7b6b096
```

Condition-count output:

```text
trading_activity_trade_eligibility_pilot_conditions_v0_1.csv
SHA256
=
c2dd75f82621ac2e4d2c136749f6ab79f8ed51baff22097d1a9a307c1e3fbd16
```

## 7. Tests

```text
coverage sidecar tests              = 4 passed
Massive snapshot tests              = 2 passed
trade eligibility tests             = 17 passed
pilot audit regression tests        = 2 passed
total                                = 25 passed
```

La regresion cubre lectura directa de un Parquet situado bajo carpetas Hive y
evita fusionar accidentalmente sus columnas internas con las particiones de la
ruta.

## 8. Limites

```text
sample selection
= deterministic first 100 tasks

tickers
= AACT and AAGR

historical condition validity
= current snapshot without effective intervals

legacy timing
= reconciled event-time research-only

provider revisions
= not observable
```

Por tanto, el resultado autoriza la implementacion piloto de Binding A sobre
este scope. No autoriza una comparacion estratificada, OOS ni promocion
canonica.
