# Core Market Family Download Audit

Tres runs independientes y read-only:

```text
ohlcv_daily -> presencia diaria; sin falsa clasificación intradía
ohlcv_1m    -> actividad exacta por ts_utc y sesión ET
quotes_     -> actividad exacta por timestamp ns y sesión ET
```

El auditor adopta la integridad física cerrada del run `20260821_core_market_raw_alignment_audit_v0_1` y verifica sus hashes. No repite los millones de footers. Solo 1m y Quotes vuelven a leer su columna temporal.


## Cierre Full 1m

El run `20260823_ohlcv_1m_download_audit_v0_1` terminó con 4.824/4.824
tickers committed y cero fallos. Su analizador reproducible es:

`analyze_ohlcv_1m_full_audit.py`

El readout institucional vive en
`01_foundations/inspection_dossiers/core_market_family_download_audit/OHLCV_1M_FULL_AUDIT_READOUT_v0_1.md`.
El estado global es present-data healthy pero temporalmente incompleto a 2026-08-20.
Orden autorizado: tests, probe Daily, probe 1m, revisión; después Full Daily/1m con autorización humana. Quotes queda preparada, pero no se lanza hasta la segunda fase.

Comandos y rutas vigentes están en `LAUNCH_DAILY_1M_QUOTES_v0_1.md`.

