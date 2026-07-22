# Corporate Actions Adjustment Methodology - Modulo 01

## 1. Rol del documento

Este documento fija la metodologia general con la que el modulo debe tratar corporate actions al construir vistas de precio comparables.

La libreria reusable ya existe en una primera version en:

- `src/data/price_views.py`

Este documento sigue teniendo rol normativo:

- define la secuencia obligatoria;
- delimita el alcance de la implementacion actual;
- y deja explicitamente fuera lo que aun no puede promocionarse a verdad institucional completa.

## 2. Eventos relevantes confirmados

Hoy estan confirmados al menos:

- dividends
- splits
- reverse splits
- ticker changes

Y deben considerarse, cuando el stack lo soporte:

- stock dividends
- spin-offs
- otros remaps corporativos compatibles con continuidad economica

## 3. Principio rector

No debe mezclarse:

- ajuste de escala por split;
- con ajuste economico por dividendos u otras distribuciones.

La secuencia metodologica correcta es:

1. identificar corporate actions relevantes
2. construir `split_normalized`
3. construir `adjusted`
4. usar `adjusted_proxy` solo como capa de contraste si la vista `adjusted` institucional aun no existe

## 4. Split normalization

### 4.1 Objetivo

Reexpresar observaciones de precio para que vivan en una base coherente de split a lo largo del tiempo.

### 4.2 Reglas

- forward y reverse splits deben entrar en una cadena multiplicativa de factores;
- la escala resultante debe ser comparable entre `quotes_raw`, `trades_raw` y `daily_raw` cuando la diferencia sea solo de split handling;
- la cadena debe ser fecha-sensible.

### 4.3 Hallazgo practico confirmado

Casos como `SGC` muestran que:

- `quotes raw` puede vivir en una escala;
- `daily raw` en otra;
- y ambas pueden reconciliarse correctamente con un factor de split.

## 5. Economic adjustment

### 5.1 Objetivo

Construir una vista comparable para retornos economicos y contraste con plataformas externas ajustadas.

### 5.2 Reglas

- los dividendos deben entrar con una metodologia explicita;
- el modulo no debe usar una resta ingenua como politica institucional final;
- la vista `adjusted` debe construirse con una cadena coherente de factores corporativos;
- esa cadena debe aplicarse sobre base ya `split_normalized`, no sobre una mezcla ambigua de escalas.

### 5.3 Estado actual

Hoy existen dos capas distintas:

- `adjusted_proxy`
- `adjusted`

#### `adjusted_proxy`

Existe hoy una `adjusted_proxy` de inspeccion.

Sirve para:

- explicar discrepancias con TradingView/Yahoo;
- y distinguir mismatch explicado por ajuste de mismatch abierto.

No debe promocionarse automaticamente a vista `adjusted` institucional final.

#### `adjusted`

Ya existe una primera implementacion reusable institucional de:

- `split_normalized`
- `adjusted`

en:

- `src/data/price_views.py`

La secuencia implementada hoy es:

1. construir `future_split_factor`
2. materializar `split_normalized`
3. calcular `future_dividend_factor` sobre esa base ya split-normalized
4. producir `adjusted`

Este alcance es suficiente para:

- `daily`
- reconciliacion con `quotes`
- labels/returns economicos iniciales
- backtest y ML en primera iteracion disciplinada

Pero aun no equivale a una cadena vendor-perfecta tipo CRSP completa si entran:

- stock dividends
- spin-offs
- otros eventos corporativos complejos

Audit especifico de la cola compleja realmente presente en fuentes:

- [daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md](../inspection_dossiers/daily/daily_adjusted_complex_corporate_actions_tail_audit_v0_1.md)

Ese audit deja una conclusion importante:

- en las fuentes estructuradas hoy auditadas no aparece una masa rica de `spin-offs` o `stock dividends` lista para consumo institucional;
- la deuda material visible hoy es, sobre todo, `ticker_change`;
- y la cola `dividend_type != CD` existe, pero es pequena y aparece solo como `SC`.

## 6. Ticker changes y continuidad

Los `ticker_change` no implican automaticamente continuidad economica completa.

La implementacion futura debe distinguir:

- remap nominal de simbolo;
- continuidad corporativa defendible;
- y casos donde el ticker visible coincide pero la serie economica no debe tratarse como unica.

El audit de cola compleja ya cuantifica esta deuda en el universo `daily`:

- `3037` filas `ticker_change` estructuradas
- `2142` dentro de ventana real de `daily`
- `2072` tickers con al menos un `ticker_change` dentro de cobertura

## 7. Implicaciones por consumidor

### Backtest

- signal y valuation:
  - `adjusted`
- execution:
  - `quotes_raw` / `trades_raw`
- reconciliacion:
  - `daily_raw` + `split_normalized`

### ML

- features microestructurales:
  - raw
- labels de retorno:
  - adjusted

### Dossiers

- pueden usar `adjusted_proxy`
- pero deben declararlo como tal

## 8. Relacion con plataformas externas

El modulo debe asumir que plataformas externas pueden estar mostrando:

- `raw`
- `split adjusted`
- `fully adjusted`
- o una cadena vendor-specific no totalmente identificada

Por tanto, la comparacion correcta exige declarar:

- la vista interna
- la vista externa inferida
- y la politica de corporate actions implicada

## 9. Estado pendiente

Queda ya iniciada y funcional la implementacion reusable de:

- `split_normalized_view`
- `adjusted_proxy_view`
- `adjusted_view`

en:

- `src/data/price_views.py`

Lo pendiente ya no es “existencia de adjusted”, sino:

- su promocion como vista institucional consumida por todos los pipelines relevantes;
- su extension futura a corporate actions mas complejas;
- y su aterrizaje explicito en:
  - `daily`
  - `quotes`
  - `trades`
  - `1m`
  - backtest
  - ML
