# Additional Root Cause Audit Phase 1 Closeout

## Estado

La fase 1 estructural de `additional` ya quedó materializada en:

- `cache_v2`
- con separación real por subbloque

Artefactos principales:

- `additional_effective_coverage_summary.parquet`
- `additional_family_summary.parquet`
- `additional_schema_samples.parquet`
- `additional_financials_summary.parquet`
- `additional_news_summary.parquet`
- `additional_news_ticker_density.parquet`
- `additional_news_multi_ticker_summary.parquet`
- `additional_corporate_actions_summary.parquet`
- `additional_ipos_summary.parquet`
- `additional_macro_calendar_summary.parquet`

## Lectura estructural

### 1. `financials_core`

Cobertura efectiva:

- `income_statements = 99.772%`
- `balance_sheets = 99.772%`
- `cash_flow_statements = 99.710%`

Lectura:

- queda como la parte más fuerte de `additional`
- la cobertura no vacía es casi total en el universo `<1B>`
- los samples muestran:
  - `period_end`
  - `filing_date`
  - `timeframe`
  - arrays `tickers`
- eso significa que la capa es rica y analíticamente defendible

### 2. `financials_ratios`

Cobertura efectiva:

- `ratios = 46.269%`

Hallazgo importante:

- el sample no vacío sí trae columnas útiles
- pero la cobertura es mucho más baja que `financials_core`

Lectura:

- no parece un fallo de descarga
- sí parece un endpoint escaso/incompleto para este universo
- queda en `review`

### 3. `news`

Cobertura efectiva:

- `news = 80.203%`

Y además:

- `288,093` filas totales
- sample rico con:
  - `published_utc`
  - `title`
  - `description`
  - `tickers`
  - `keywords`
  - `insights`
  - publisher fields

Hallazgo fuerte:

- `news` es masivo, pero muchos artículos son multi-ticker
- en la muestra de 50 files:
  - hay tickers con media de `tickers por noticia` muy alta
  - por tanto el matching causal ticker-event deberá vigilar ambigüedad multi-ticker

Lectura:

- `news` es un subbloque fuerte
- no basta con contar noticias; hay que separar mono-ticker vs multi-ticker

### 4. `corporate_actions_additional`

Cobertura efectiva:

- `ticker_events = 56.032%`
- `splits = 38.889%`
- `dividends = 26.078%`

Hallazgos:

- `splits` no vacíos sí existen y traen estructura buena
- `dividends` no vacíos también traen estructura real
- `ticker_events` trae campos como:
  - `type`
  - `date`
  - `ticker_change.ticker`

Lectura:

- este bloque no está roto
- pero sigue siendo más débil y más escaso que la capa equivalente en `reference`
- por tanto, la pregunta clave ya no es “existe data”
- sino “aporta valor incremental frente a `reference`”

### 5. `ipos`

Cobertura efectiva:

- `ipos = 26.016%`

Sample no vacío:

- sí trae campos reales de IPO:
  - `announced_date`
  - `listing_date`
  - `issuer_name`
  - `final_issue_price`
  - `primary_exchange`
  - `ipo_status`

Lectura:

- no es un dataset roto
- es estructuralmente escaso
- potencialmente útil para early-life behavior

### 6. `economic`

Cobertura:

- `inflation`: `950` filas, `1947-01-01 -> 2026-02-01`
- `inflation_expectations`: `531` filas, `1982-01-01 -> 2026-03-01`
- `treasury_yields`: `16047` filas, `1962-01-02 -> 2026-04-02`

Lectura:

- capa macro larga y limpia
- no ticker-based
- buena candidata a `good` como dataset

## Hallazgo técnico transversal

Sigue presente el problema de lectura mergeada:

- `Field ticker has incompatible types: string vs dictionary...`

Conclusión operativa:

- el builder debe seguir leyendo archivo físico puro
- este hallazgo es parte del contrato técnico del bloque

## Decisión provisional de fase 1

### good

- `financials_core`
- `economic`
- `news` como dataset estructural

### review

- `financials_ratios`
- `ipos`
- `corporate_actions_additional`

### bad

- no emerge un subbloque estructuralmente `bad`

## Qué falta

1. notebook metodológico
2. cruces causales:
   - `news -> halts/quotes/trades/short`
   - `ipos -> early anomalies`
   - `corporate_actions_additional -> reference overlap`
   - `macro -> market regime context`
3. política final `good / review / bad`
