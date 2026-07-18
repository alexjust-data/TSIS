# Row-level Comparison Readiness - DAS CMDAPI 2026-07-08

Run: das_cmdapi_live_20260708T193719Z

Este informe comprueba si las familias historicas bajo E:\TSIS\data tienen fisicamente la misma fecha/simbolo que la captura DAS del 2026-07-08 para los 18 simbolos PASS unicos.

| familia_local | check | found | denominator | lectura |
| --- | --- | --- | --- | --- |
| 000_TRADES | exact 2026-07-08 market.parquet | 0 | 18 | No row-level intraday comparison yet; reconstructed DAS TMS table is ready. |
| 001_QUOTES | exact 2026-07-08 quotes.parquet | 0 | 18 | No row-level quote comparison yet; reconstructed DAS Lv1/Lv2 tables are ready. |
| 002_DAILY | year file exists / date row exists | 18/18 files, 0/18 date rows | 18 | Year files exist but stop at 2026-03-06 for checked symbols. |
| 003_DAILY_ADJUSTED | year file exists / date row exists | 18/18 files, 0/18 date rows | 18 | Adjusted year files exist but stop at 2026-03-06 for checked symbols. |
| 004_1_MINUTE | 2026-07 month file exists | 0 | 18 | No row-level 1m historical comparison for DAS date yet. |
| 005_1_MINUTE_SPLIT_NORMALIZED | 2026-07 month file exists | 0 | 18 | No split-normalized 1m historical comparison for DAS date yet. |
| 009_SHORT | symbol short file exists | 18 | 18 | Files exist, but settlement-date comparison is not same as intraday DAS SHORTINFO. |

## Conclusion

La reconstruccion DAS ya esta materializada y lista para comparacion. Pero, con las rutas comprobadas, las familias historicas no contienen datos intradia ni filas daily para 2026-07-08 en estos 18 simbolos. Por tanto ahora se puede hacer comparacion de schema/source parity y de logica de campos; la comparacion row-level de valores queda pendiente hasta que Data Foundation incluya esa fecha o se agregue una fuente historica equivalente.

## Detalle Por Simbolo

ROW_LEVEL_COMPARISON_READINESS_BY_SYMBOL.csv contiene el detalle por ticker.
