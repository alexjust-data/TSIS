# Contrato de Auditoria Short

## Principio rector

La auditoria `short` no se basa en microestructura intradia como `quotes` o `trades`, pero debe alcanzar el mismo nivel de rigor.

El bloque `short` se audita sobre dos unidades distintas:

- `short_interest_snapshot`
  - clave: `ticker + settlement_date`
- `short_volume_snapshot`
  - clave: `ticker + date`

Y sobre una tercera unidad derivada:

- `short_market_link`
  - vinculo entre el snapshot `short` y lo observado en `daily`, `ohlcv_1m`, `quotes`, `trades`, `halts`

## Fuentes

### Baseline oficial

La fuente baseline de certificacion es `FINRA`, materializada en:

- `C:\TSIS_Data\data\short_review\finra_short`

Subcapas:

- `normalized\short_interest\TICKER.parquet`
- `normalized\short_volume\TICKER.parquet`
- `artifacts\short_interest_all_biweekly_finra.parquet`
- `artifacts\short_volume_all_daily_finra.parquet`

### Capa comparativa secundaria

La descarga actual de `Polygon` se mantiene como capa paralela:

- `C:\TSIS_Data\data\short\short_interest`
- `C:\TSIS_Data\data\short\short_volume`

No se toma como ground truth de cobertura historica.

## Universo

El universo operativo es el mismo ya establecido en la auditoria general `<1B>`.

## Preguntas que debe responder la auditoria

1. Si la data `short_interest` por ticker es internamente consistente.
2. Si la data `short_volume` por ticker es internamente consistente.
3. Si la cobertura temporal observada es razonable dentro de la ventana real del source.
4. Si existen mezclas de identidad o `ticker reuse`.
5. Si `Polygon` queda por debajo o contradice al baseline `FINRA`.
6. Si `short` explica o contextualiza anomalias reales de mercado.

## Unidades y chequeos obligatorios

### A. short_interest_snapshot

Campos minimos esperados:

- `settlement_date`
- `ticker`
- `short_interest`
- `avg_daily_volume`
- `days_to_cover`

Chequeos:

- no duplicados por `ticker + settlement_date`
- `short_interest >= 0`
- `avg_daily_volume >= 0`
- `days_to_cover >= 0`
- `days_to_cover ~= short_interest / avg_daily_volume`
- continuidad temporal razonable

### B. short_volume_snapshot

Campos minimos esperados:

- `ticker`
- `date`
- `total_volume`
- `short_volume`
- `exempt_volume`
- `non_exempt_volume`
- `short_volume_ratio`

Venue columns esperadas en baseline `FINRA`:

- `nyse_short_volume`
- `nyse_short_volume_exempt`
- `nasdaq_carteret_short_volume`
- `nasdaq_carteret_short_volume_exempt`
- `nasdaq_chicago_short_volume`
- `nasdaq_chicago_short_volume_exempt`
- `adf_short_volume`
- `adf_short_volume_exempt`
- `orf_short_volume`
- `orf_short_volume_exempt`

Chequeos:

- no duplicados por `ticker + date`
- `total_volume >= short_volume >= 0`
- `short_volume = exempt_volume + non_exempt_volume`
- `short_volume_ratio ~= 100 * short_volume / total_volume`
- continuidad temporal razonable

### C. short_identity_link

Cruces obligatorios con `reference`:

- `overview`
- `all_tickers`
- `events`
- `splits`

Objetivo:

- detectar `ticker reuse`
- detectar series fuera de la ventana de vida del ticker
- distinguir ausencia real de data de mezcla de identidad

### D. short_market_link

Cruces obligatorios:

- `short_volume` vs `daily`, `quotes`, `trades`, `halts`
- `short_interest` vs ventanas multi-dia y eventos relevantes

Objetivo:

- medir si `short` aporta contexto o explicacion a anomalias reales

## Politica de severidad esperada

### Estructural

- `good`
  - integridad aritmetica y temporal defendible
- `review`
  - coverage parcial, identidad dudosa, sparse series, discrepancias entre providers
- `bad`
  - inconsistencia interna fuerte o identidad no resoluble

### Causal

- `good`
  - `short` explica o contextualiza un patron de mercado de forma fuerte
- `review`
  - `short` ayuda, pero no cierra del todo la lectura causal
- `bad`
  - contradiccion fuerte o serie inutil para interpretacion

## Decisiones metodologicas fijadas

1. `FINRA` es baseline oficial para certificacion.
2. `Polygon` se conserva como capa paralela de comparacion.
3. La ausencia pre-2018 en `short_volume` official/free no se trata como fallo del builder sino como limite del source.
4. El hueco `2005-2018` de `short_volume` y el pre-history antiguo de `short_interest` quedan explicitamente fuera del alcance official/free completo.
