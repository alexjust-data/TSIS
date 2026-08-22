# Core Market Session Coverage Audit

Auditor corregido de presencia por `ticker × session_date_et` para:

- `ohlcv_daily`;
- `ohlcv_1m`;
- `quotes_`;
- `trades_ticks_prod_2005_2026`.

Reutiliza la auditoría física `20260821_core_market_raw_alignment_audit_v0_1`. Solo vuelve a leer `ohlcv_1m.ts_utc`, porque su columna `date` es UTC y no puede compararse directamente con la fecha de sesión ET de las otras familias.

No modifica RAW. Una tarea de Trades todavía no cerrada se registra como `SOURCE_PENDING`, no como data ausente. El ledger de huecos conserva por separado la ausencia observada y su diagnóstico.

El modo `Full` exige `-HumanAuthorizedFull`. Antes debe pasar el probe production-equivalent y debe entregarse al humano el comando, impacto, monitor, parada segura y artefactos esperados conforme a `LONG_RUNNING_OPERATIONS_CONTRACT.md`.
