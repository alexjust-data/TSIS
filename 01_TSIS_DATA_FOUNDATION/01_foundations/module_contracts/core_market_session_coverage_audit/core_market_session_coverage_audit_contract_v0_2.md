# Core Market Session Coverage Audit Contract v0.2

## Objetivo

Comparar para los 4.824 tickers gobernados y 2005-01-01 a 2026-08-20 las fechas de sesión ET presentes en ohlcv_daily, ohlcv_1m y quotes_, mientras Trades continúa su auditoría física independiente.

## Contrato del run autorizado

- comparison_families: ohlcv_daily, ohlcv_1m, quotes_.
- deferred_families: trades_ticks_prod_2005_2026.

Una familia diferida no se consulta, no entra en el conjunto unión, no genera huecos y queda registrada como DEFERRED_BY_RUN_CONTRACT. No equivale a SOURCE_PENDING, ausencia de datos ni fallo.

## Autoridades temporales

- Daily usa date.
- Quotes usa su partición year/month/day ya inventariada.
- 1m deriva session_date_et desde ts_utc con America/New_York.
- La columna date UTC de 1m no se compara directamente con Daily o Quotes.

## Seguridad y cierre

- Todos los RAW permanecen read-only.
- Cada ticker se compromete atómicamente con hashes y checkpoint SQLite.
- El full exige 4.824 de 4.824 tareas committed, cero fallos y manifest final.
- El resultado describe presencia, ventanas y ausencias observadas; no promociona por sí solo una certificación material del proveedor.
