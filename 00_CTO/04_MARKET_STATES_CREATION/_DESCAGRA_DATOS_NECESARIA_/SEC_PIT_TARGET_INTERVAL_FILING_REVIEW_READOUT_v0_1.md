# SEC PIT Target-Interval Filing Review Readout v0_1

## Veredicto

```text
RUN = sec_pit_7t_target_interval_filing_review_v0_1
STATUS = PASS_WITH_RESTRICTIONS
REVIEWED FILINGS = 12 / 12
LEGAL LIST DATES ADMITTED = 0
LEGAL DELIST DATES ADMITTED = 0
PARENT-UNIVERSE SCALE = NOT_AUTHORIZED
```

## Resultado

| Resultado de frontera | Filings |
|---|---:|
| Sin autoridad de frontera | 10 |
| Fin de trading en exchange observado, candidato | 1 |
| Fin de trading en exchange programado, candidato | 1 |

| Scope de clase | Filings |
|---|---:|
| Common stock objetivo | 8 |
| Common stock y warrant objetivo | 1 |
| Warrant no objetivo | 1 |
| Unit no objetivo | 1 |
| Preferred right no objetivo | 1 |

## Hallazgos

### ALUR

Los filings de agosto de 2024 son avisos de incumplimiento sin delisting inmediato. El filing de 2 de marzo de 2026 inicia procedimientos, pero declara que el trading continua durante la apelacion. El filing de 12 de marzo informa que NYSE suspendio el trading despues del cierre del 6 de marzo de 2026 y que la accion paso a OTC; el Form 25 seguia siendo futuro y condicional.

```text
2026-03-06
= OBSERVED_EXCHANGE_TRADING_END_CANDIDATE
!= legal_delist_date
```

### BBBY

El 8-A de octubre de 2025 registra warrants, no common stock. El 8-K de agosto de 2026 anuncia una transferencia NYSE -> Nasdaq con fin esperado en NYSE el 14 de agosto y comienzo esperado en Nasdaq el 17 de agosto. Como eran fechas futuras al filing, requieren confirmacion posterior.

### BNAI

El Form 25 de marzo de 2024 afecta a `Unit`, no al common stock BNAI. Los restantes filings son avisos o extensiones de cumplimiento. La revision corrige el filing de julio de 2025: es una extension, no `compliance regained`.

### DOMH

El 8-A registra `Series Q Preferred Purchase Rights`, no DOMH common stock.

## Outputs

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/sec_pit_7t_target_interval_filing_review_v0_1/
target_interval_filing_review_ledger.parquet
target_interval_filing_review_ledger.csv
final_manifest.json
```

## Restricciones

Este readout no resuelve todavia fechas legales completas. Impide que clases no objetivo, avisos, fechas programadas o suspensiones se conviertan automaticamente en listing/delisting.

Siguiente trabajo: materializar la primera comparacion de las seis identidades piloto entre ventanas Massive/Polygon, evidencia SEC revisada y bounds observados en G:, bajo `MASSIVE_SEC_LIFECYCLE_WINDOW_RECONCILIATION_CONTRACT_v0_1`.