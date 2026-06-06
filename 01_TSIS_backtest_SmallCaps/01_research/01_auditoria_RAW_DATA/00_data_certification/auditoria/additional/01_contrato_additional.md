# Contrato Additional

## Rol del bloque

`additional` no es un dataset único. Es un bloque compuesto de datos auxiliares de Polygon con semánticas distintas y, por tanto, con reglas de auditoría distintas.

El bloque se audita dentro del universo operativo ya fijado en la auditoría general:

- `<1B>`

Pero no todas sus capas tienen grano `ticker-day`. Algunas son:

- `ticker-event`
- `ticker-filing`
- `macro-date`

La regla central es:

- no mezclar bajo una sola política datasets que cumplen funciones analíticas distintas

## Subbloques reales

### 1. `financials_core`

Incluye:

- `income_statements`
- `balance_sheets`
- `cash_flow_statements`

Unidad analítica:

- `financial_snapshot = ticker + period_end + filing_date + timeframe`

Qué responde:

- qué información contable/fundamental útil existe por ticker
- si la serie es lo bastante completa para research/factors/contexto estructural

Qué esperamos:

- cobertura alta
- filas no vacías reales
- consistencia temporal razonable
- coexistencia de `quarterly` y `trailing_twelve_months` cuando aplique

### 2. `financials_ratios`

Incluye:

- `ratios`

Unidad analítica:

- `ratio_snapshot = ticker + period_end + filing_date + timeframe`

Qué responde:

- si el endpoint de ratios aporta información usable para el universo `<1B>`

Qué esperamos:

- cobertura menor que `financials_core`
- posible escasez estructural
- necesidad de validar si la baja cobertura es natural del endpoint o un problema funcional

### 3. `news`

Incluye:

- `news`

Unidad analítica:

- `news_event = ticker + published_utc + id`

Qué responde:

- si existe contexto informativo real cerca de episodios de mercado
- si los bursts de noticias ayudan a explicar:
  - `halts`
  - anomalías en `quotes`
  - anomalías en `trades`
  - episodios de `short`

Campos importantes observados:

- `published_utc`
- `title`
- `description`
- `tickers`
- `keywords`
- `insights`
- `publisher.*`
- `article_url`

Qué esperamos:

- cobertura material pero no universal
- mezcla de artículos mono-ticker y multi-ticker
- ruido de press release / syndication
- valor real como capa causal contextual

### 4. `ipos`

Incluye:

- `ipos`

Unidad analítica:

- `ipo_event = ticker + event_date`

Qué responde:

- si la condición de ticker recién listado explica comportamientos anómalos en fases tempranas

Qué esperamos:

- alta escasez estructural
- muchos placeholders vacíos
- utilidad principalmente en `early-life cases`

### 5. `corporate_actions_additional`

Incluye:

- `splits`
- `dividends`
- `ticker_events`

Unidad analítica:

- `corp_action_event = ticker + event_date + event_type`

Qué responde:

- si `additional` aporta valor incremental frente a `reference`

Qué esperamos:

- cobertura naturalmente escasa en muchos tickers
- mucha fila placeholder vacía
- posible redundancia parcial con `reference`, que ya es la capa principal para:
  - `splits`
  - `dividends`
  - `ticker events`

### 6. `economic`

Incluye:

- `inflation`
- `inflation_expectations`
- `treasury_yields`

Unidad analítica:

- `macro_snapshot = dataset + date`

Qué responde:

- si el bloque macro está completo y utilizable como contexto de régimen

Qué esperamos:

- series temporales largas y limpias
- no ticker-based
- utilidad contextual, no causalidad microestructural directa por ticker

## Hallazgos estructurales ya conocidos

### A. Placeholders vacíos son parte del diseño

Varios subdatasets ticker-based usan parquets con esta forma:

- `ticker`
- `_empty`
- `_dataset`
- `_ingested_utc`

Eso no implica fallo por sí mismo.

Puede significar:

- dataset naturalmente no aplicable al ticker
- endpoint sin resultado útil para ese ticker

Por eso la métrica válida no es:

- `files_present`

Sino:

- `files_non_empty`
- `rows_non_empty`
- `coverage_effective`

### B. Riesgo de lectura por schema merge

En varios roots apareció conflicto de lectura estilo:

- `Field ticker has incompatible types: string vs dictionary...`

Implicación:

- el builder de auditoría debe leer archivo físico puro
- no debe depender de lectura dataset-merge automática a nivel directorio

## Cruces causales obligatorios

### `news`

Cruzar con:

- `halts`
- `quotes`
- `trades`
- `short`

Preguntas:

- ¿hay bursts de noticias cerca de halts?
- ¿las anomalías de mercado tienen contexto informativo?
- ¿las noticias son mono-ticker o multi-ticker ambiguas?

### `ipos`

Cruzar con:

- `daily`
- `quotes`
- `trades`
- `reference`

Preguntas:

- ¿la condición de IPO / listing reciente explica early-life fragilidad?

### `corporate_actions_additional`

Cruzar con:

- `reference`
- y solo secundariamente con mercado

Preguntas:

- ¿aporta algo que `reference` no tenga ya mejor resuelto?

### `financials_core` y `financials_ratios`

Cruce causal ligero, no intradía fuerte.

Cruzar con:

- `daily`
- ventanas amplias
- opcionalmente `short`

Preguntas:

- ¿la data es suficientemente poblada para research y factores?
- ¿hay lag o sparsity que limite su uso?

### `economic`

Cruzar con:

- calendario global
- regímenes del mercado, no ticker-event intradía

## Política esperada por subbloque

### Probable `good`

- `financials_core`
- `economic`
- parte de `news`

### Probable `review`

- `financials_ratios`
- `ipos`
- `corporate_actions_additional`
- parte de `news`

### `bad`

- no se presupone un bucket `bad`
- solo emergerá si aparece:
  - data artificialmente vacía donde no debería
  - incoherencia estructural
  - contradicción fuerte con capas principales

## Criterio de cierre

`additional` solo se considera auditado si al final tiene:

- builder offline reproducible
- artefactos por subbloque
- notebook metodológico único, pero claramente seccionado
- closeout estructural
- closeout causal
- y cierre ejecutivo final

La evaluación final no será una sola etiqueta para todo el bloque.

Debe quedar:

- política por subbloque
- y una decisión ejecutiva agregada para `additional`
