
Ticker-based completo

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\066_download_additional_ticker_data_lt1b_from_polygon.py --universe-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet --env-file C:\TSIS_Data\02_backtest_SmallCaps\.env --out-root C:\TSIS_Data\data\additional --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_downloads\20260405_full_refresh_ticker_based  --datasets splits,dividends,ticker_events,news,ipos,income_statements,balance_sheets,cash_flow_statements,ratios --workers 6 --resume
{
  "started_at_utc": "2026-04-05T18:21:08.595064+00:00",
  "finished_at_utc": "2026-04-05T18:39:07.507173+00:00",
  "universe_parquet": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\market_cap_last_observed_cutoff\\20260320_market_cap_last_observed_cutoff\\market_cap_cutoff_lt_1b_active_inactive.parquet",
  "universe_tickers": 4824,
  "datasets": [
    "splits",
    "dividends",
    "ticker_events",
    "news",
    "ipos",
    "income_statements",
    "balance_sheets",
    "cash_flow_statements",
    "ratios"
  ],
  "out_root": "C:\\TSIS_Data\\data\\additional",
  "run_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\additional_downloads\\20260405_full_refresh_ticker_based",
  "workers": 6,
  "resume": true,
  "pause_sec": 0.0,
  "submitted_tasks": 43416,
  "ok_tasks": 43416,
  "error_tasks": 0,
  "sources": {
    "splits": "https://polygon.io/docs/rest/stocks/corporate-actions/splits",
    "dividends": "https://polygon.io/docs/rest/stocks/corporate-actions/dividends",
    "ticker_events": "https://polygon.io/docs/rest/stocks/corporate-actions/ticker-events",
    "news": "https://polygon.io/docs/rest/stocks/news/",
    "ipos": "https://polygon.io/docs/rest/stocks/corporate-actions/ipos",
    "balance_sheets": "https://polygon.io/docs/rest/stocks/fundamentals/balance-sheets",
    "income_statements": "https://polygon.io/docs/rest/stocks/fundamentals/income-statements",
    "cash_flow_statements": "https://polygon.io/docs/rest/stocks/fundamentals/cash-flow-statements",
    "ratios": "https://polygon.io/docs/rest/stocks/fundamentals/ratios"
  }
}
```

  - 43416 / 43416 tareas ok
  - 0 errores
  - universo completo intentado: 4824 tickers x 9 datasets
  - root correcto: C:\TSIS_Data\data\additional

  Eso significa que la materialización está completa y reanudable.

  Lo que sí veo en los volúmenes:

  - news, financials y dividends tienen masa razonable
  - splits, ticker_events e ipos son naturalmente escasos
  - ratios con 2232 filas totales para 4824 tickers es demasiado bajo para asumir que está bien sin auditar; no lo doy por malo todavía, pero sí por
    pendiente de revisión

  Comando macro:
```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\067_download_additional_macro_from_polygon.py --env-file C:\TSIS_Data\02_backtest_SmallCaps\.env --out-root C:\TSIS_Data\data\additional --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_downloads\20260405_full_refresh_macro --datasets inflation,inflation_expectations,treasury_yields
{
  "started_at_utc": "2026-04-05T18:41:55.015359+00:00",
  "finished_at_utc": "2026-04-05T18:41:56.249422+00:00",
  "datasets": [
    "inflation",
    "inflation_expectations",
    "treasury_yields"
  ],
  "out_root": "C:\\TSIS_Data\\data\\additional",
  "run_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\additional_downloads\\20260405_full_refresh_macro",
  "submitted_tasks": 3,
  "ok_tasks": 3,
  "error_tasks": 0,
  "summary_by_dataset": [
    {
      "dataset": "inflation",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 950,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\inflation.parquet",
      "ts_utc": "2026-04-05T18:41:55.496009+00:00"
    },
    {
      "dataset": "inflation_expectations",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 531,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\inflation_expectations.parquet",
      "ts_utc": "2026-04-05T18:41:55.662237+00:00"
    },
    {
      "dataset": "treasury_yields",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 16047,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\treasury_yields.parquet",
      "ts_utc": "2026-04-05T18:41:56.241835+00:00"
    }
  ],
  "sources": {
    "inflation": "https://polygon.io/docs/rest/economy/inflation",
    "inflation_expectations": "https://polygon.io/docs/rest/economy/inflation-expectations",
    "treasury_yields": "https://polygon.io/docs/rest/economy/treasury-yields"
  }
}
```
La descarga macro también ha salido limpia:

  - 3 / 3 tareas ok
  - 0 errores
  - inflation: 950 filas
  - inflation_expectations: 531 filas
  - treasury_yields: 16047 filas

  Estado actual de C:\TSIS_Data\data\additional:

  - ticker-based: refrescado
  - macro: refrescado
  - sin errores operativos de descarga

  Los manifests fiables ahora son:

  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_downloads/20260405_full_refresh_ticker_based/download_manifest.parquet
  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_downloads/20260405_full_refresh_ticker_based/download_summary.json
  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_downloads/20260405_full_refresh_macro/download_manifest.parquet
  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_downloads/20260405_full_refresh_macro/download_summary.json

  El siguiente paso correcto ya no es descargar. Es auditar cobertura efectiva y vacíos por dataset, especialmente:

  - news
  - ipos
  - splits
  - ticker_events
  - ratios

  Porque ok en descarga sólo significa “endpoint respondido y parquet escrito”, no “dataset útil y no vacío para el ticker”.

**auditoría para comprobar cobertura y no-vacíos por ticker**

primero el ticker-based completo:

```sh
python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\066_download_additional_ticker_data_lt1b_from_polygon.py --universe-parquet C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\market_cap_last_observed_cutoff\20260320_market_cap_last_observed_cutoff\market_cap_cutoff_lt_1b_active_inactive.parquet --env-file C:\TSIS_Data\02_backtest_SmallCaps\.env --out-root C:\TSIS_Data\data\additional --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_downloads\20260405_full_refresh_ticker_based --datasets splits,dividends,ticker_events,news,ipos,income_statements,balance_sheets,cash_flow_statements,ratios --workers 6 --resume
```

Luego el macro:

```sh
PS C:\Users\AlexJ> python C:\TSIS_Data\02_backtest_SmallCaps\data_auditoria_polygon\cell_code\00_data_certification\067_download_additional_macro_from_polygon.py --env-file C:\TSIS_Data\02_backtest_SmallCaps\.env --out-root C:\TSIS_Data\data\additional --run-dir C:\TSIS_Data\02_backtest_SmallCaps\runs\backtest\additional_downloads\20260405_full_refresh_macro --datasets inflation,inflation_expectations,treasury_yields
{
  "started_at_utc": "2026-04-05T18:44:24.152663+00:00",
  "finished_at_utc": "2026-04-05T18:44:25.612099+00:00",
  "datasets": [
    "inflation",
    "inflation_expectations",
    "treasury_yields"
  ],
  "out_root": "C:\\TSIS_Data\\data\\additional",
  "run_dir": "C:\\TSIS_Data\\v1\\backtest_SmallCaps\\runs\\backtest\\additional_downloads\\20260405_full_refresh_macro",
  "submitted_tasks": 3,
  "ok_tasks": 3,
  "error_tasks": 0,
  "summary_by_dataset": [
    {
      "dataset": "inflation",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 950,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\inflation.parquet",
      "ts_utc": "2026-04-05T18:44:24.679850+00:00"
    },
    {
      "dataset": "inflation_expectations",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 531,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\inflation_expectations.parquet",
      "ts_utc": "2026-04-05T18:44:24.903422+00:00"
    },
    {
      "dataset": "treasury_yields",
      "status": "ok",
      "http_status": 200,
      "message": "ok",
      "rows_saved": 16047,
      "pages": 1,
      "out_file": "C:\\TSIS_Data\\data\\additional\\economic\\treasury_yields.parquet",
      "ts_utc": "2026-04-05T18:44:25.603794+00:00"
    }
  ],
  "sources": {
    "inflation": "https://polygon.io/docs/rest/economy/inflation",
    "inflation_expectations": "https://polygon.io/docs/rest/economy/inflation-expectations",
    "treasury_yields": "https://polygon.io/docs/rest/economy/treasury-yields"
  }
}
```

He creado y ejecutado C:/TSIS_Data/02_backtest_SmallCaps/data_auditoria_polygon/cell_code/00_data_certification/068_audit_additional_lt1b_coverage.py.

Salida maestra:

```
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_lt1b_coverage_audit_summary.json
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_ticker_datasets_summary.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_ticker_datasets_by_file.parquet
- C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_macro_datasets_summary.parquet
```

Lectura final sobre los 4824 tickers:

```
- income_statements: 4813 no vacíos, cobertura efectiva 99.772%
- balance_sheets: 4813 no vacíos, cobertura efectiva 99.772%
- cash_flow_statements: 4810 no vacíos, cobertura efectiva 99.710%
- news: 3869 no vacíos, cobertura efectiva 80.203%
- ticker_events: 2703 no vacíos, cobertura efectiva 56.032%
- ratios: 2232 no vacíos, cobertura efectiva 46.269%
- splits: 1876 no vacíos, cobertura efectiva 38.889%
- dividends: 1258 no vacíos, cobertura efectiva 26.078%
- ipos: 1255 no vacíos, cobertura efectiva 26.016%
```

Punto importante:

```
- todos los datasets ticker-based tienen files_present = 4824, porque el downloader escribió un parquet por ticker
- la métrica que importa es files_non_empty / target_hit_non_empty, no files_present
```

Macro:

```
- inflation: 950 filas, 1947-01-01 a 2026-02-01
- inflation_expectations: 531 filas, 1982-01-01 a 2026-03-01
- treasury_yields: 16047 filas, 1962-01-02 a 2026-04-02
```

Conclusión operativa:

```
- financials sí quedan casi completos y útiles
- news queda bastante usable
- splits, dividends, ipos, ticker_events son datasets naturalmente escasos; no es un fallo de descarga
- ratios es el único que merece revisión funcional adicional, porque su cobertura efectiva es baja para algo que podría esperarse más poblado
```

**Ratios**

Ya lo contrasté y la conclusión es clara: ratios no está mal descargado; el endpoint es escaso para este universo.

Comparativa real:

- nuevo C:\TSIS_Data\data\additional\financials\ratios
    - files_present: 4824
    - files_non_empty: 2232
    - target_hit_non_empty: 2232
    - coverage_non_empty_pct: 46.269%
- antiguo D:\financial\ratios
    - files_present: 12468
    - files_non_empty: 4309
    - sobre el universo <1B: target_hit_non_empty = 2237
    - coverage_non_empty_pct = 46.372%

La diferencia es mínima:

- antes: 2237
- ahora: 2232

Eso significa:

- no hemos perdido cobertura relevante en el refresh
- la baja cobertura de ratios ya existía
- el problema no es del script 066
- el endpoint de Polygon para ratios simplemente no devuelve dato útil para muchos tickers del universo

Además, el schema observado en los no vacíos es coherente:

- una fila snapshot por ticker
- columnas tipo date, price, market_cap, price_to_earnings, price_to_book, ev_to_sales, free_cash_flow, etc.

Y los vacíos están bien materializados:

- ticker
- _empty
- _dataset
- _ingested_utc

Conclusión operativa:

- ratios queda aceptado como dataset descargado correctamente
- pero no debe tratarse como cobertura casi completa
- su cobertura efectiva real para <1B es ~46.3%

Si quieres, el siguiente paso te saco una clasificación final de additional en:

- core usable
- auxiliary sparse but valid
- macro global
para dejar cerrada la política de uso.




Core Usable
  Datasets que sí puedes tratar como capa operativa principal dentro de additional:

  - income_statements
    Cobertura efectiva: 99.772%
  - balance_sheets
    Cobertura efectiva: 99.772%
  - cash_flow_statements
    Cobertura efectiva: 99.710%
  - news
    Cobertura efectiva: 80.203%

  Lectura:

  - los tres financials son prácticamente completos para el universo <1B
  - news no es completo, pero sí suficientemente poblado como para ser útil en modelos/event studies

  Auxiliary Sparse But Valid
  Datasets correctos, pero naturalmente escasos. No hay que interpretarlos como fallo de cobertura:

  - ticker_events
    Cobertura efectiva: 56.032%
  - ratios
    Cobertura efectiva: 46.269%
  - splits
    Cobertura efectiva: 38.889%
  - dividends
    Cobertura efectiva: 26.078%
  - ipos
    Cobertura efectiva: 26.016%

  Lectura:

  - ticker_events, splits, dividends, ipos son escasos por naturaleza del evento
  - ratios también queda en este bucket, pero con una nota: no es que el downloader falle, sino que Polygon no devuelve ratios para gran parte del
    universo

  Macro Global
  No se auditan por ticker. Se usan como series comunes para todo el backtest:

  - inflation
    950 filas, 1947-01-01 a 2026-02-01
  - inflation_expectations
    531 filas, 1982-01-01 a 2026-03-01
  - treasury_yields
    16047 filas, 1962-01-02 a 2026-04-02

  Política de uso
  Yo cerraría additional así:

  - usar como core:
      - income_statements
      - balance_sheets
      - cash_flow_statements
      - news
  - usar como auxiliary:
      - ticker_events
      - splits
      - dividends
      - ipos
      - ratios
  - usar como macro:
      - inflation
      - inflation_expectations
      - treasury_yields

  Artefacto de auditoría final:

  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_ticker_datasets_summary.parquet
  - C:/TSIS_Data/02_backtest_SmallCaps/runs/backtest/additional_audit/20260405_additional_lt1b_coverage/additional_macro_datasets_summary.parquet

  Si quieres, el siguiente paso te preparo un 069 que materialice un inventory canónico de additional con una columna usage_policy ya asignada por
  dataset.