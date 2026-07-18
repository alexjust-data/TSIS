# Additional Closeout

## Alcance

El bloque `additional` no se comporta como un dataset homogéneo. La auditoría se cerró separando explícitamente seis subcapas:

- `financials_core`
- `financials_ratios`
- `news`
- `ipos`
- `corporate_actions_additional`
- `economic`

La lectura se hizo sobre el universo operativo `<1B>` ya fijado por la auditoría general y usando builder offline con lectura de archivo físico puro, porque el merge automático por dataset falla en varios roots por conflicto de schema (`ticker` string vs `ticker` dict/nested).

## Resultado por subbloque

### `financials_core`

Queda aceptado como `good`.

- `income_statements`: `99.772%`
- `balance_sheets`: `99.772%`
- `cash_flow_statements`: `99.710%`

Los tres subdatasets están ampliamente poblados, con grano temporal útil (`period_end`, `filing_date`, `fiscal_quarter`, `fiscal_year`, `timeframe`) y sin señal estructural de corrupción generalizada.

### `financials_ratios`

Queda en `review`.

- cobertura efectiva: `46.269%`

No parece un bug puntual de lectura. La evidencia actual es más compatible con endpoint naturalmente escaso o con estrategia de materialización incompleta. No se rechaza, pero tampoco se eleva a capa primaria del bloque.

### `news`

Queda como subbloque causal más fuerte de `additional`, con cierre provisional `good/review` mixto.

- `287,138` eventos normalizados
- `3,869` tickers con noticias no vacías
- solo `36.38%` mono-ticker

Buckets actuales:

- `news_near_halt_market_event = 1,268`
- `news_near_market_anomaly = 98,400`
- `news_context_only = 18,296`
- `review_multi_ticker_ambiguous_news = 169,154`
- `news_near_short_flow_only = 20`

Lectura:

- `news_near_halt_market_event` es el subconjunto con más valor `good`
- `news_near_market_anomaly` tiene valor real, pero requiere revisión visual selectiva antes de promoverlo en masa
- `review_multi_ticker_ambiguous_news` se queda en `review` por ambigüedad estructural

### `ipos`

Queda `good/review` mixto, por utilidad real pero localizada.

- cobertura efectiva: `26.016%`
- `ipo_near_halt_market_event = 156`
- `ipo_near_market_anomaly = 676`
- `ipo_market_clean = 449`

Lectura:

- `ipo_near_halt_market_event` es un subconjunto claramente útil
- `ipo_near_market_anomaly` aporta contexto de early-life behavior, pero requiere calibración visual caso a caso
- `ipo_market_clean` se queda en `review` por utilidad contextual sin anomalía evidente

### `corporate_actions_additional`

Queda en `review` y como capa secundaria frente a `reference`.

Cobertura efectiva:

- `ticker_events = 56.032%`
- `splits = 38.889%`
- `dividends = 26.078%`

Solape con `reference`:

- `splits`: overlap fuerte (`reference_exact_overlap = 1858`)
- `dividends`: overlap fuerte (`reference_exact_overlap = 1253`)
- `ticker_events`: presencia, pero sin overlap exacto útil (`reference_present_no_exact_overlap = 2703`)

Lectura:

- `splits` y `dividends` aquí son básicamente confirmación secundaria o redundancia
- `ticker_events` mantiene valor potencial, pero no con semántica suficientemente estable como para desplazar a `reference`

### `economic`

Queda `good` como dataset y `review` como capa causal ticker-level.

Series auditadas:

- `inflation`
- `inflation_expectations`
- `treasury_yields`

Son limpias, largas y temporalmente coherentes, pero su papel es de overlay macro, no de causalidad directa por ticker.

## Política final

### `good`

- `financials_core`
- `economic` como dataset macro
- `news_near_halt_market_event`
- subconjunto de `ipo_near_halt_market_event`

### `review`

- `financials_ratios`
- `news_near_market_anomaly`
- `review_multi_ticker_ambiguous_news`
- `news_context_only`
- `ipo_near_market_anomaly`
- `ipo_market_clean`
- `corporate_actions_additional`
- `economic` como causalidad de mercado por ticker

### `bad`

No emerge todavía una familia agregada `bad`.

Los límites observados son principalmente:

- sparsity natural
- ambigüedad multi-ticker
- redundancia frente a `reference`

No aparecen, por ahora, señales de corrupción masiva del bloque.

## Decisión operativa

`additional` queda aceptado, pero no como una capa única de igual peso interno.

Jerarquía final del bloque:

1. `financials_core`: fuerte y utilizable
2. `news`: subbloque causal más valioso
3. `ipos`: contextual útil, sobre todo en early-life y halts cercanos
4. `economic`: overlay macro útil
5. `corporate_actions_additional`: secundario frente a `reference`
6. `financials_ratios`: mantener en `review`

## Pendiente útil

La única pieza que todavía merece muestreo visual adicional antes de considerar el bloque completamente rematado es:

- calibración manual de casos representativos de `news_near_market_anomaly`
- calibración manual de casos representativos de `ipo_near_halt_market_event` e `ipo_near_market_anomaly`

Para eso ya queda integrado el viewer causal al final de:

- `03_additional_root_cause_audit_notebook.ipynb`
