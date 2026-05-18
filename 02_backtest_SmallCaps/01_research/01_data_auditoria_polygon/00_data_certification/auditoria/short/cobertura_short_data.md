

## cobertura short_data `C:\TSIS_Data\data\short_data`

Auditoría de cobertura short_data para el universo completo <1B, con control de riesgo por ticker reutilizado.


Script
```
C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/063_short_data_lt1b_ticker_coverage_audit.py.
```
Objetivo del script:

auditar, por cada ticker del universo <1B, qué cobertura real existe en C:\TSIS_Data\data\short_data, separando:

```
- presencia física de fichero
- cobertura temporal observada
- validez estructural del parquet
- consistencia ticker-filename
- riesgo de mezcla histórica por reutilización de símbolo
```

Qué hace:

```
- carga el universo <1B desde market_cap_cutoff_lt_1b_active_inactive.parquet
- cruza cada ticker con short_interest y short_volume
- inspecciona cada parquet ticker-based
- valida columnas requeridas
- calcula rows, date_min, date_max, nulos de fecha y duplicados por fecha
- verifica si la columna ticker del file coincide con el nombre del archivo
- cruza con tickers_panel_pti para medir entity_id_nunique
- clasifica el riesgo por ticker en:
    - ok_single_entity_in_window
    - multi_entity_in_window
    - outside_universe_window
    - high_risk_possible_reuse_mix
    - missing_file
```

Inputs por defecto:

```
- universo:   
C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet

- panel PTI: 
C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_panel_pti

- root short data: 
C:\TSIS_Data\data\short_data
```

Outputs del run ejecutado:

```
- carpeta: C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_data_audit\20260405_183332_short_data_lt1b_ticker_coverage_audit
- resumen: C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_audit/20260405_183332_short_data_lt1b_ticker_coverage_audit/
short_data_lt1b_ticker_coverage_audit_summary.json
- joined por ticker: C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_audit/20260405_183332_short_data_lt1b_ticker_coverage_audit/
short_data_lt1b_coverage_joined_by_ticker.parquet
- alto riesgo de reuse mix: C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/
short_data_audit/20260405_183332_short_data_lt1b_ticker_coverage_audit/short_data_lt1b_high_risk_possible_reuse_mix.parquet
- faltantes en algún dataset: C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/
short_data_audit/20260405_183332_short_data_lt1b_ticker_coverage_audit/short_data_lt1b_missing_any_dataset.parquet
```

Hallazgos

```
Sobre 4824 tickers del universo <1B:
- short_interest: 4205 files presentes, 619 faltantes, cobertura 87.168%
- short_volume: 2978 files presentes, 1846 faltantes, cobertura 61.733%
- tickers con cualquier short_data: 4205
- tickers con riesgo alto de mezcla por reuse en al menos un dataset: 163
```
Riesgo estructural real:

```
- 1499 tickers del universo <1B tienen más de un entity_id en tickers_panel_pti
- como short_interest y short_volume son ticker-based, eso introduce riesgo real de contaminar una serie con otra entidad histórica
- el script no asume que todo dato “fuera de ventana” sea malo, pero sí lo marca cuando coincide con reutilización de ticker
```
Lectura operativa:
```
- short_interest está razonablemente cubierto, pero ya tiene 162 tickers en high_risk_possible_reuse_mix
- short_volume está bastante menos cubierto y tiene 88 tickers en high_risk_possible_reuse_mix
- el problema principal no es sólo missing coverage; también hay mezcla histórica probable en símbolos reciclados
- ejemplos de alto riesgo visibles en la salida: ADXS, AGRX, ANTH, ATXI, BTCY, CDTI
```

**Contenido Esperado**

Para `C:\TSIS_Data\data\short_data\short_interest\TICKER.parquet`:
```
- un parquet por ticker
- una fila por settlement_date
- columnas obligatorias observadas:
    - settlement_date
    - ticker
    - short_interest
    - avg_daily_volume
    - days_to_cover
- el ticker interno debe coincidir con el filename
- no debería haber mezcla de varias entidades bajo el mismo símbolo si el ticker fue reutilizado
```

Para `C:\TSIS_Data\data\short_data\short_volume\TICKER.parquet`:

```
- un parquet por ticker
- una fila por date
- columnas obligatorias observadas:
    - ticker
    - date
    - total_volume
    - short_volume
    - exempt_volume
    - non_exempt_volume
    - short_volume_ratio
    - nyse_short_volume
    - nyse_short_volume_exempt
    - nasdaq_carteret_short_volume
    - nasdaq_carteret_short_volume_exempt
    - nasdaq_chicago_short_volume
    - nasdaq_chicago_short_volume_exempt
    - adf_short_volume
    - adf_short_volume_exempt
    - short_ratio
    - exempt_ratio
    - short_ratio_ma5
    - short_ratio_change
    - short_ratio_zscore
- el ticker interno debe coincidir con el filename
- igual que en short_interest, el gran riesgo es que el endpoint no distingue entity_id
```

Conclusión:

sí, hay que tratar short_data como dataset con riesgo explícito de ticker reuse contamination. Con la evidencia actual, no conviene certificarlo
sólo por presencia de fichero. Hay que certificarlo por ticker y además por compatibilidad temporal con la ventana PTI de la entidad vigente. Para short_data, volver a descargar sólo para el universo <1B es más limpio que intentar certificar a ciegas lo que ya hay.

La razón no es sólo cobertura:

- short_interest cubre 87.168%, pero short_volume sólo 61.733%
- hay 163 tickers con high_risk_possible_reuse_mix
- los endpoints son ticker-based, no entity_id-based, así que un parquet histórico por símbolo puede mezclar entidades distintas bajo el mismo
ticker reutilizado

Operativamente, yo haría esto:

1. construir la lista canónica de tickers <1B
2. redescargar short_interest y short_volume sólo para ese universo
3. persistir en un root nuevo, no encima de C:\TSIS_Data\data\short_data
4. materializar inventario por ticker con date_min/date_max/rows/schema
5. marcar desde el principio los tickers con entity_id_nunique > 1 como REVIEW_TICKER_REUSE
6. decidir después si se conservan completos, se recortan a la ventana válida PTI o se cuarentenan


## Redescarga en `C:\TSIS_Data\data\short`

Deep Research Polygon
Revisando la documentación oficial de Polygon, lo relevante para este caso es:


- Short Interest: endpoint REST dedicado por ticker. La documentación oficial lo expone como endpoint histórico de short interest por símbolo.
Fuente: https://polygon.io/docs/rest/stocks/fundamentals/short-interest
- Short Volume: endpoint REST dedicado por ticker. Igual, por símbolo, no por entidad.
Fuente: https://polygon.io/docs/rest/stocks/fundamentals/short-volume
- Ticker Overview / Ticker Details: necesario como metadata de apoyo para interpretar el símbolo “actual” y su estado a una fecha.
Fuente: https://polygon.io/docs/rest/stocks/tickers/ticker-overview/
- Ticker Events: relevante para lifecycle/cambios del ticker; útil para investigar reutilización o transiciones del símbolo.
Fuente: https://polygon.io/docs/stocks/get_vx_reference_tickers__ticker__events
- Splits: no es short data en sí, pero sí endpoint relacionado para interpretar cambios fuertes en series ligadas a shares/volumen.
Fuente: https://polygon.io/docs/stocks/get_v3_reference_splits
- All Tickers: útil sólo como referencia general; para esta descarga no lo necesitas porque ya tienes el universo canónico <1B.
Fuente: https://polygon.io/docs/rest/stocks/tickers/all-tickers


Mi lectura operativa de Polygon para este caso:

```
- los endpoints que sí debes descargar ahora son short_interest y short_volume
- los endpoints “relacionados” que sí tienen sentido como apoyo son ticker_overview/details, ticker_events y splits
- no encontré una vía oficial de flat files para short data comparable a trades/quotes/aggs; para short data, la ruta práctica sigue siendo REST
ticker a ticker
```

**Qué faltaba respecto a estos endpoints**

En local teníais muestra/inspección de schema y ahora auditoría de cobertura, pero no un downloader limpio y versionado para refrescar
short_interest + short_volume contra el universo <1B en un root nuevo.

Por eso añadí este script:

```
C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/064_download_short_data_lt1b_from_polygon.py
```

Objetivo del 

```
- descargar desde Polygon short_interest y short_volume para todos los tickers del parquet <1B
- leer POLYGON_API_KEY desde C:\TSIS_Data\02_backtest_SmallCaps\.env
- escribir un parquet por ticker en C:\TSIS_Data\data\short\short_interest y C:\TSIS_Data\data\short\short_volume
- materializar manifiesto de descarga y resumen de run
```

Inputs:

```
- --universe-parquet
- --env-file
- --out-root
- --run-dir
- --datasets
- --workers
- --pause-sec
- --resume
```

Outputs:

```
- C:\TSIS_Data\data\short\short_interest\TICKER.parquet
- C:\TSIS_Data\data\short\short_volume\TICKER.parquet
- manifest CSV/Parquet y summary JSON en el run-dir
```

No he lanzado la descarga real contra Polygon desde este entorno; dejé el downloader compilado y listo.

Comando de descarga `descargar fresh con 064`

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\064_download_short_data_lt1b_from_polygon.py --universe-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet --env-file C:\TSIS_Data\02_backtest_SmallCaps\.env --out-root C:\TSIS_Data\data\short --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_downloads\lt1b_short_refresh --datasets short_interest,short_volume --workers 6 --resume
[OK] short_interest AAN rows=163 date_min=2017-12-29 date_max=2024-09-30
...
[OK] short_volume ZYXI rows=473 date_min=2024-02-06 date_max=2025-12-23
{
  "started_at_utc": "2026-04-05T17:00:59.676584+00:00",
  "finished_at_utc": "2026-04-05T17:11:31.760975+00:00",
  "universe_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\market_cap_last_observed_cutoff\\20260320_market_cap_last_observed_cutoff\\market_cap_cutoff_lt_1b_active_inactive.parquet",
  "universe_tickers": 4824,
  "datasets": [
    "short_interest",
    "short_volume"
  ],
  "out_root": "C:\\TSIS_Data\\data\\short",
  "run_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_downloads\\lt1b_short_refresh",
  "workers": 6,
  "resume": true,
  "pause_sec": 0.0,
  "submitted_tasks": 9648,
  "ok_tasks": 9648,
  "error_tasks": 0,
  "summary_by_dataset": [
    {
      "dataset": "short_interest",
      "ok": 4824,
      "error": 0,
      "rows_total": 520048
    },
    {
      "dataset": "short_volume",
      "ok": 4824,
      "error": 0,
      "rows_total": 1430506
    }
  ]
}
```

**`063` para auditar coverage/risk de lo descargado**

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\063_short_data_lt1b_ticker_coverage_audit.py --universe-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet --panel-parquet C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_panel_pti --short-root C:\TSIS_Data\data\short --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_data_audit\lt1b_short_refresh_audit
{
    "audited_at_utc": "2026-04-05T17:21:59.521868+00:00",
    "inputs": {
      "universe_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\market_cap_last_observed_cutoff\
  \20260320_market_cap_last_observed_cutoff\\market_cap_cutoff_lt_1b_active_inactive.parquet",
      "panel_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\data\\reference\\universe_pti_rebuild_compare\\tickers_panel_pti",
      "short_root": "C:\\TSIS_Data\\data\\short"
    },
    "universe_tickers": 4824,
    "short_interest": {
      "files_present": 4824,
      "files_missing": 0,
      "coverage_pct": 100.0,
      "tickers_outside_window_any": 2938,
      "high_risk_possible_reuse_mix": 754,
      "extra_files_outside_universe": 0,
      "risk_bucket_counts": {
        "outside_universe_window": 2184,
        "ok_single_entity_in_window": 1141,
        "high_risk_possible_reuse_mix": 754,
        "multi_entity_in_window": 745
      }
    },
    "short_volume": {
      "files_present": 4824,
      "files_missing": 0,
      "coverage_pct": 100.0,
      "tickers_outside_window_any": 2807,
      "high_risk_possible_reuse_mix": 701,
      "extra_files_outside_universe": 0,
      "risk_bucket_counts": {
        "outside_universe_window": 2106,
        "ok_single_entity_in_window": 1219,
        "multi_entity_in_window": 798,
        "high_risk_possible_reuse_mix": 701
      }
    },
    "joined": {
      "tickers_with_any_short_data": 4824,
      "tickers_missing_any_dataset": 0,
      "tickers_high_risk_possible_reuse_mix_any": 761,
      "entity_reuse_counts": {
        "1": 3325,
        "2": 1190,
        "3": 243,
        "4": 62,
        "5": 2,
        "6": 2
      }
    },
    "expected_file_content": {
      "short_interest": {
        "unit": "one parquet per ticker",
        "required_columns": [
          "settlement_date",
          "ticker",
          "short_interest",
          "avg_daily_volume",
          "days_to_cover"
        ],
        "expected_rows_semantics": "one row per settlement_date for the ticker; ticker column should match the filename"
      },
      "short_volume": {
        "unit": "one parquet per ticker",
        "required_columns": [
          "ticker",
          "date",
          "total_volume",
          "short_volume",
          "exempt_volume",
          "non_exempt_volume",
          "nyse_short_volume_exempt",
          "nasdaq_carteret_short_volume",
          "nasdaq_carteret_short_volume_exempt",
          "nasdaq_chicago_short_volume",
          "nasdaq_chicago_short_volume_exempt",
          "adf_short_volume",
          "adf_short_volume_exempt",
          "short_ratio",
          "exempt_ratio",
          "short_ratio_ma5",
          "short_ratio_change",
          "short_ratio_zscore"
        ],
        "expected_rows_semantics": "one row per trading date for the ticker; ticker column should match the filename"
      }
    },
    "outputs": {
      "short_interest_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_interest_lt1b_coverage_by_ticker.parquet",
      "short_interest_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_interest_lt1b_coverage_by_ticker.csv",
      "short_volume_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_volume_lt1b_coverage_by_ticker.parquet",
      "short_volume_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_volume_lt1b_coverage_by_ticker.csv",
      "joined_by_ticker_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_coverage_joined_by_ticker.parquet",
      "joined_by_ticker_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_coverage_joined_by_ticker.csv",
      "high_risk_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_high_risk_possible_reuse_mix.parquet",
      "high_risk_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_high_risk_possible_reuse_mix.csv",
      "missing_any_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_missing_any_dataset.parquet",
      "missing_any_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_missing_any_dataset.csv",
      "short_interest_extra_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_interest_extra_files_outside_lt1b_universe.parquet",
      "short_interest_extra_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_interest_extra_files_outside_lt1b_universe.csv",
      "short_volume_extra_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_volume_extra_files_outside_lt1b_universe.parquet",
      "short_volume_extra_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_volume_extra_files_outside_lt1b_universe.csv",
      "summary_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_audit\\lt1b_short_refresh_audit\
  \short_data_lt1b_ticker_coverage_audit_summary.json"
    }
  }
```
**Lectura de `063`**

La descarga fresh ha cerrado completamente la cobertura física:

```
- short_interest: 4824/4824
- short_volume: 4824/4824
- 0 faltantes
- 0 extra fuera del universo <1B
```

Pero la parte importante es esta:

```
- short_interest tiene 2938 tickers con datos fuera de la ventana PTI esperada
- short_volume tiene 2807 tickers con datos fuera de la ventana PTI esperada
- 761 tickers quedan en high_risk_possible_reuse_mix en al menos uno de los dos datasets
```
Eso significa:

```
- la descarga fresh resolvió el problema de cobertura
- pero no resolvió el problema de certificación histórica
- de hecho, confirma que el problema fuerte no era missing data sino desalineación temporal y posible mezcla por ticker reutilizado
```


## Cobertura `D:\reference`

En D:\ ya tienes descargada la data relacionada relevante para interpretar short_data.

Lo que encontré en D:\reference:

```
- D:\reference\overview
- D:\reference\splits
- D:\reference\events
- D:\reference\dividends
- D:\reference\all_tickers
- D:\reference\exchanges
- D:\reference\ticker_types
```


Cobertura sobre el universo <1B (4824 tickers):


```
- overview: 4824/4824 (100%)
- splits: 4824/4824 (100%)
- events: 4824/4824 (100%)
- dividends: 4824/4824 (100%)
```


Detalles útiles:


```
- overview, splits, events, dividends están guardados por ticker bajo carpetas tipo ticker=XYZ
- all_tickers existe como snapshots por fecha en parquet
- exchanges y ticker_types existen como parquet únicos
- no vi un root de short_interest / short_volume en D:\; la short data actual está en C:\TSIS_Data\data\short_data
```


Conclusión operativa:

```
- no hace falta redescargar en D:\ la metadata relacionada básica para este trabajo; ya está
- lo que sí falta refrescar es la propia short_data
- para tratar ticker reuse, puedes apoyar la nueva descarga de short_interest / short_volume con:
    - D:\reference\events
    - D:\reference\overview
    - D:\reference\splits
    - y secundariamente D:\reference\dividends
```

## Auditoría posterior de cobertura/riesgo sobre lo descargado:

La certificación debe cruzar:

```
- C:\TSIS_Data\data\short\short_interest
- C:\TSIS_Data\data\short\short_volume
- D:\reference\events
- D:\reference\overview
- D:\reference\splits
- universo <1B de C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/market_cap_last_observed_cutoff/20260320_market_cap_last_observed_cutoff/
market_cap_cutoff_lt_1b_active_inactive.parquet
- tickers_panel_pti para entity_id_nunique
```

**Qué certificamos**

Por ticker, hay que responder seis preguntas:

```
1. ¿Existe el file?
2. ¿Tiene el schema correcto?
3. ¿La ventana temporal del file cae dentro de la vida PTI esperada?
4. ¿El ticker tiene reuse potencial (entity_id_nunique > 1)?
5. ¿events/overview/splits explican la discontinuidad o la vuelven sospechosa?
6. ¿El ticker queda apto, revisable o bloqueado para backtest?
```

**Clasificación seria**

Yo usaría estas salidas finales, no sólo PASS/REVIEW/QUARANTINE genéricas:

- CERTIFIED_OK : File presente, schema válido, ventana compatible, sin señal fuerte de mezcla.
- CERTIFIED_OK_WITH_LIMITED_WINDOW : El file existe pero sólo una subventana es defendible para uso.
- REVIEW_TICKER_REUSE : Hay reuse potencial y la evidencia no permite asegurar separación limpia por entidad.
- REVIEW_REFERENCE_CONFLICT : overview/events/splits no cuadran bien con la ventana observada.
- MISSING_DATA : Falta el file o falta una parte crítica.
- QUARANTINE_HIGH_RISK_MIX : Señal fuerte de mezcla histórica entre vidas distintas del ticker.

Objetivo:

certificar por ticker la usabilidad de short_interest y short_volume para el universo <1B, usando referencias de D:\reference y controlando
explícitamente ticker reuse.

```
C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\065_certify_short_data_lt1b_with_reference.py

Qué hace:

- lee el universo <1B
- lee tickers_panel_pti
- cruza short_interest y short_volume
- cruza D:\reference\overview, D:\reference\events, D:\reference\splits
- clasifica por ticker en:
    - CERTIFIED_OK
    - CERTIFIED_OK_WITH_LIMITED_WINDOW
    - REVIEW_TICKER_REUSE
    - REVIEW_REFERENCE_CONFLICT
    - MISSING_DATA
    - QUARANTINE_HIGH_RISK_MIX
```

Inputs

```
- universo <1B
- tickers_panel_pti
- C:\TSIS_Data\data\short
- D:\reference\overview
- D:\reference\events
- D:\reference\splits
```
Outputs
```
- short_data_certification_by_ticker.parquet
- short_data_certification_by_ticker.csv
- short_data_certified_ok.parquet
- short_data_review_ticker_reuse.parquet
- short_data_quarantine_high_risk_mix.parquet
- short_data_certification_summary.json
```
Qué haría
```
- leer short_interest y short_volume por ticker
- validar columnas esperadas y consistencia ticker-file
- medir date_min/date_max, duplicados y filas fuera de ventana PTI
- leer entity_id_nunique desde PTI
- cruzar overview/events/splits del ticker
- derivar un certification_status
- derivar, si aplica, una certified_date_start y certified_date_end
- dejar trazabilidad de por qué se certificó o bloqueó
```
Reglas mínimas
```
- Si falta ambos datasets: MISSING_DATA
- Si el schema falla: QUARANTINE_HIGH_RISK_MIX
- Si hay filas fuera de ventana y entity_id_nunique == 1: REVIEW_REFERENCE_CONFLICT
- Si hay filas fuera de ventana y entity_id_nunique > 1: REVIEW_TICKER_REUSE o QUARANTINE_HIGH_RISK_MIX
- Si hay reuse pero el file cae limpiamente dentro de la subventana defendible: CERTIFIED_OK_WITH_LIMITED_WINDOW
- Si todo cuadra: CERTIFIED_OK
```
**Contenido esperado de los files**

`short_interest/TICKER.parquet`

```
- una fila por settlement_date
- columnas mínimas:
    - settlement_date
    - ticker
    - short_interest
    - avg_daily_volume
    - days_to_cover
```

`short_volume/TICKER.parquet`

```
- una fila por date
- columnas mínimas:
    - ticker
    - date
    - total_volume
    - short_volume
    - exempt_volume
    - non_exempt_volume
    - short_volume_ratio
    - nyse_short_volume
    - nyse_short_volume_exempt
    - nasdaq_carteret_short_volume
    - nasdaq_carteret_short_volume_exempt
    - nasdaq_chicago_short_volume
    - nasdaq_chicago_short_volume_exempt
    - adf_short_volume
    - adf_short_volume_exempt
    - short_ratio
    - exempt_ratio
    - short_ratio_ma5
    - short_ratio_change
    - short_ratio_zscore
```

Lo correcto ahora

1. descargar fresh con 064
2. correr la auditoría 063
3. construir 065 para certificación seria con referencia

**`065`, o sea certificación sobre una short data que ya exista en C:\TSIS_Data\data\short**

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\065_certify_short_data_lt1b_with_reference.py --universe-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet --panel-parquet C:\TSIS_Data\02_backtest_SmallCaps\data\reference\universe_pti_rebuild_compare\tickers_panel_pti --short-root C:\TSIS_Data\data\short --reference-root D:\reference --outdir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\short_data_certification\lt1b_short_reference_certification_v2
{
  "certified_at_utc": "2026-04-05T17:35:53.056220+00:00",
  "inputs": {
    "universe_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\market_cap_last_observed_cutoff\\20260320_market_cap_last_observed_cutoff\\market_cap_cutoff_lt_1b_active_inactive.parquet",
    "panel_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\data\\reference\\universe_pti_rebuild_compare\\tickers_panel_pti",
    "short_root": "C:\\TSIS_Data\\data\\short",
    "reference_root": "D:\\reference"
  },
  "universe_tickers": 4824,
  "status_counts": {
    "REVIEW_REFERENCE_CONFLICT": 2195,
    "CERTIFIED_OK": 1130,
    "REVIEW_TICKER_REUSE": 761,
    "CERTIFIED_OK_WITH_LIMITED_WINDOW": 738
  },
  "entity_reuse_counts": {
    "1": 3325,
    "2": 1190,
    "3": 243,
    "4": 62,
    "5": 2,
    "6": 2
  },
  "outputs": {
    "certification_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_certification_by_ticker.parquet",
    "certification_csv": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_certification_by_ticker.csv",
    "certified_ok_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_certified_ok.parquet",
    "certified_ok_with_limited_window_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_certified_ok_with_limited_window.parquet",
    "review_ticker_reuse_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_review_ticker_reuse.parquet",
    "review_reference_conflict_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_review_reference_conflict.parquet",
    "missing_data_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_missing_data.parquet",
    "quarantine_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_quarantine_high_risk_mix.parquet",
    "summary_json": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\short_data_certification\\lt1b_short_reference_certification_v2\\short_data_certification_summary.json"
  }
}
```

**Resultado**

Sobre 4824 tickers:

```sh
- CERTIFIED_OK: 1130
- CERTIFIED_OK_WITH_LIMITED_WINDOW: 738
- REVIEW_TICKER_REUSE: 761
- REVIEW_REFERENCE_CONFLICT: 2195
```

No aparecen:

```sh
- MISSING_DATA
- QUARANTINE_HIGH_RISK_MIX
```

Eso encaja con lo que vimos en 064 y 063:

```
- la cobertura física quedó completa
- el problema real no era falta de descarga
- el problema real era compatibilidad temporal y ticker reuse
```

Lectura correcta

```sh
CERTIFIED_OK (1130)

- son los tickers más limpios
- short data dentro de ventana
- sin conflicto relevante de referencia
- estos son la parte más defendible para uso directo

CERTIFIED_OK_WITH_LIMITED_WINDOW (738)

- son utilizables, pero no de manera ciega sobre todo el historial del ticker
- hay que respetar la ventana certificada por ticker

REVIEW_TICKER_REUSE (761)

- son los casos donde el ticker probablemente ha tenido más de una vida económica
- aquí no conviene usar el file completo como si fuera una sola entidad

REVIEW_REFERENCE_CONFLICT (2195)

- es el bucket más grande
- aquí la data existe, pero no cae limpiamente dentro de la ventana PTI esperada
- no implica necesariamente corrupción; implica que para el backtest serio no deberías asumir que todo el historial del file es válido para la
entidad que estás certificando
```

**Conclusión operativa**

La short data fresh ya no está en fase de descarga. Ya está en fase de política de uso.

Si quieres ser serio de verdad para backtest:
```sh
- usa directamente CERTIFIED_OK
- usa CERTIFIED_OK_WITH_LIMITED_WINDOW sólo recortando por certified_date_start / certified_date_end
- no uses todavía REVIEW_TICKER_REUSE
- no uses todavía REVIEW_REFERENCE_CONFLICT sin una política adicional
```

**Qué file mirar ahora**

El file maestro de verdad para decidir uso es:
```sh
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certification_by_ticker.parquet
```

Y los subconjuntos listos:

```sh
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certified_ok.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_certified_ok_with_limited_window.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_review_ticker_reuse.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/short_data_certification/lt1b_short_reference_certification_v2/short_data_review_reference_conflict.parquet
```

**Mi recomendación**

Haz una primera versión operativa con:

```sh
- CERTIFIED_OK
- CERTIFIED_OK_WITH_LIMITED_WINDOW
```

Y deja fuera por ahora:

```sh
- REVIEW_TICKER_REUSE
- REVIEW_REFERENCE_CONFLICT
```

Si quieres, el siguiente paso te lo hago yo conceptualmente:

```sh
- definir la política exacta de construcción del dataset final de short data para backtest
- qué columnas conservar
- cómo aplicar el recorte de ventana por ticker
- y qué artefacto final materializar como fuente canónica.
```