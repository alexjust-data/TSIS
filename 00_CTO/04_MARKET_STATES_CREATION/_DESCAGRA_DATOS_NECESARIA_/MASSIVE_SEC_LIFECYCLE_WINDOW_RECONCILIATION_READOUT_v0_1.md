# Massive / SEC Lifecycle Window Reconciliation Readout v0_1

## Veredicto

```text
RUN = sec_pit_6i_lifecycle_window_reconciliation_v0_1
ROWS = 6
STATUS = PASS_WITH_RESTRICTIONS
LEGAL LIST DATES ADMITTED = 0
LEGAL DELIST DATES ADMITTED = 0
PARENT-UNIVERSE SCALE = NOT_AUTHORIZED
```

## Comparacion piloto

| Ticker | Vendor first | Target identity start | First daily | SEC boundary | Resultado |
|---|---|---|---|---|---|
| ALUR | 2023-08-02 | 2023-08-02 | 2023-08-02 | NYSE suspension candidate 2026-03-06 | SEC exchange end candidate, not legal delist |
| BBBY | 2016-10-25 | 2025-09-01 | 2025-09-02 | scheduled transfer 2026-08-14 | ticker reuse conflict |
| BGM | 2024-08-12 | 2024-08-12 | 2024-08-12 | none | vendor start matches daily |
| BNAI | 2024-03-15 | 2024-03-15 | 2024-03-15 | none for target class | vendor start matches daily |
| DOMH | 2022-12-23 | 2022-12-22 | 2022-12-22 | none for target class | one-day source difference |
| PGAC | 2025-08-08 | 2025-08-11 | 2025-08-15 | none | source dates not directly comparable |

## Hallazgos

1. `first_seen_date` y `last_observed_date` conservan procedencia Massive/Polygon.
2. La ventana vendor no se ha sobrescrito con SEC ni con market presence.
3. BBBY demuestra que ticker string no basta para resolver identidad historica.
4. BNAI Form 25 y DOMH/BBBY 8-A afectan clases no objetivo y no alteran la ventana common-stock.
5. ALUR 2026-03-06 es un fin de trading NYSE candidato, no un delisting legal admitido.
6. El final vendor `2026-03-09` excede en tres dias el ultimo daily disponible para cinco tickers y en cinco dias para ALUR; refleja diferencias de corte/cobertura que requieren politica, no correccion silenciosa.

## Output

```text
D:/TSIS/fundamental_context/sec_pit_v0_1/replays/
sec_pit_6i_lifecycle_window_reconciliation_v0_1/

lifecycle_window_reconciliation.parquet
lifecycle_window_reconciliation.csv
final_manifest.json
```

## Estado siguiente

La comparacion piloto esta ejecutada, pero el gate de autoridad lifecycle final permanece abierto. Antes de escalar deben resolverse como minimo:

```text
BBBY ticker reuse / identity intervals
confirmation of BBBY scheduled transfer
ALUR Form 25 or appeal outcome
PGAC snapshot/tape/daily start semantics
DOMH one-day start difference
vendor delisted_utc source lane, absent from instrument_master_v0_1
```
