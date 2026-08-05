# Ranking descendente de robustez metodológica — SCC Issues 1–15

## Qué significa este orden

Este ranking **no afirma que ninguna estrategia tenga edge validado ni que sea apta para operar en real**. Ordena los archivos como candidatos de investigación y réplica, usando exclusivamente las auditorías contenidas en el ZIP.

No se ha ordenado por net profit, win rate o Profit Factor bruto. Esas métricas quedan penalizadas cuando proceden de una muestra pequeña, una búsqueda masiva, un margen por trade insuficiente, una ejecución no causal o una fórmula difícil de reproducir.

## Fórmula de puntuación

Cada estrategia recibe seis notas de 0 a 10:

1. plausibilidad del mecanismo; 2. legalidad temporal y determinismo; 3. soporte estadístico efectivo; 4. resistencia a selección/overfitting; 5. robustez frente a costes y ejecución; 6. reproducibilidad y generalización.

`score_estrategia = 100 × suma(componentes) / 60`

Como cada archivo contiene una revista completa y no una sola estrategia:

`score_issue = 70% × mejor estrategia + 30% × media de las restantes`

Esta ponderación coloca primero los números que contienen el candidato más útil, pero evita que una segunda estrategia metodológicamente débil quede ignorada. Los decimales son una herramienta de priorización, no una estimación de probabilidad de beneficio.

## Ranking final

| Puesto | Issue original | Score /100 | Estrategia más fuerte | Diagnóstico crítico |
|---:|---|---:|---|---|
| 001 | Issue 9 — septiembre de 2015 | 72.8 | 017 2+1 Moving Average (73.3) | El conjunto más equilibrado: dos reglas diarias, causales, de baja rotación y con hipótesis estructurales fáciles de falsificar. |
| 002 | Issue 8 — agosto de 2015 | 71.8 | 015 Normalized VIX (78.3) | Contiene la estrategia individual mejor puntuada; Net Tick Fade arrastra el conjunto porque su edge desaparece con ~1 tick de slippage. |
| 003 | Issue 14 — febrero de 2016 | 68.2 | 029 Trend Capture (71.7) | Trend Capture es el candidato multi-activo más serio, aunque el genetic search, el drawdown y la falsa noción de “1% risk” reducen la confianza. |
| 004 | Issue 7 — julio de 2015 | 63.5 | 014 Parabolic Plus (65.0) | Parabolic Plus aporta la muestra más amplia del issue; aún exige costes, contratos físicos y simulación intrabar. |
| 005 | Issue 6 — junio de 2015 | 62.5 | 011 Asymmetric Channel Breakout (65.0) | Buen valor estructural y muestras decentes; Final Thirty queda muy penalizada por 29.952 candidatos. |
| 006 | Issue 5 — mayo de 2015 | 62.2 | 009 MACD Difference Turn (66.7) | MACD Turn es una réplica limpia y razonable; DMI queda muy penalizada por ser el máximo de un grid 31x31. |
| 007 | Issue 12 — diciembre de 2015 | 61.3 | 024 Market Breadth Gauge (63.3) | Breadth es conceptualmente fuerte y de baja rotación, pero depende de una serie propietaria; Pivot tiene margen económico débil. |
| 008 | Issue 10 — octubre de 2015 | 60.6 | 019 Pinpoint Pullback (63.3) | Tres hipótesis útiles; Pinpoint y Williams sostienen el issue, aunque persisten ambigüedades de ejecución y selección. |
| 009 | Issue 13 — enero de 2016 | 59.0 | 026 VWAP Bands (60.0) | Muestras amplias, pero el VWAP tiene margen minúsculo y Regression Angles no es invariante a escala ni dispone de stop. |
| 010 | Issue 15 — marzo de 2016 | 59.0 | 030 Overnight-Futures-Range Breakout (60.0) | Arquitecturas útiles y muestras grandes en VWAP, pero márgenes por trade muy estrechos; la rama short del overnight no aporta evidencia. |
| 011 | Issue 1 — enero de 2015 | 56.2 | 002 Moving Average Channel (56.7) | Dos candidatos implementables, pero uno usa una formulación inestable y el otro deja aproximadamente un tick por trade. |
| 012 | Issue 3 — marzo de 2015 | 55.8 | 006 Bar Range Expansion (58.3) | BRE es investigable, pero exige replay intrabar; la otra pieza es una búsqueda masiva, no una estrategia validada. |
| 013 | Issue 11 — noviembre de 2015 | 53.3 | 022 Measured Moves (53.3) | Una estrategia es inviable con costes razonables y la otra depende de 31 trades y un outlier dominante. |
| 014 | Issue 4 — abril de 2015 | 47.5 | 007 CCI Bollinger Bands Combo (50.0) | Sobreoptimización extrema: 8.000 y 18.628 configuraciones, además de confusión entre alpha y aumento de exposición. |
| 015 | Issue 2 — febrero de 2015 | 44.5 | 004 VIX Pivot (45.0) | El peor conjunto: riesgo de repainting/look-ahead y una segunda estrategia con sólo 12 trades y sin stop. |

## Lectura profesional del podio

### 1. Issue 9

Es el conjunto más equilibrado. `2+1 Moving Average` tiene una muestra pequeña, pero su regla es extremadamente simple, causal, barata de ejecutar y fácil de falsificar. `Adaptive VIX Bands` añade una hipótesis de volatilidad relativa con baja rotación y diez años de evidencia publicada. Ninguna está validada, pero ambas sobreviven mejor que el resto al filtro de costes, complejidad y causalidad.

### 2. Issue 8

`Normalized VIX` es la estrategia individual mejor puntuada: señal diaria, normalización por régimen, poca exposición y menor dependencia del microcoste. El issue no queda primero porque `Net Tick Fade`, pese a sus 1.722 trades, tiene una esperanza tan estrecha que aproximadamente un tick de slippage round trip destruiría el beneficio medio.

### 3. Issue 14

`Trend Capture` es el candidato multi-activo más serio: lógica de tendencia conocida, sizing ATR y 18 instrumentos. No sube más porque el universo y los parámetros fueron seleccionados con búsqueda genética, el drawdown ronda el 41%, no existe el supuesto stop de 2 ATR y el resultado incluye open P/L.

## Exclusión de duplicado

El ZIP original contenía dos copias de `015_SCC_Issue_15_Mar_2016_Auditoria_Completa.md`. Sus SHA-256 eran idénticos (`dac880c8b26b76d5...`), por lo que el paquete ordenado conserva una sola copia.

## Advertencia operativa

Todas las revistas siguen en estado `EDGE_UNPROVEN / NOT_LIVE_ELIGIBLE`. El ranking sólo determina **qué replicar y falsificar primero**. Antes de aceptar cualquier edge deben ejecutarse, como mínimo, OOS postpublicación, contratos físicos cuando proceda, costes completos, pruebas de estabilidad de parámetros, atribución long/short, sensibilidad a outliers y validación temporal purgada.

## Correspondencia de nombres

| Nuevo prefijo | Archivo original | Archivo renombrado |
|---:|---|---|
| 001 | `001_SCC_Issue_1_Jan_2015_Auditoria_Completa.md` | `001_SCC_Issue_1_Jan_2015_Auditoria_Completa.md` |
| 002 | `002_SCC_Issue_2_Feb_2015_Auditoria_Completa.md` | `002_SCC_Issue_2_Feb_2015_Auditoria_Completa.md` |
| 003 | `003_SCC_Issue_3_Mar_2015_Auditoria_Completa.md` | `003_SCC_Issue_3_Mar_2015_Auditoria_Completa.md` |
| 004 | `004_SCC_Issue_4_Apr_2015_Auditoria_Completa.md` | `004_SCC_Issue_4_Apr_2015_Auditoria_Completa.md` |
| 005 | `005_SCC_Issue_5_May_2015_Auditoria_Completa.md` | `005_SCC_Issue_5_May_2015_Auditoria_Completa.md` |
| 006 | `006_SCC_Issue_6_Jun_2015_Auditoria_Completa.md` | `006_SCC_Issue_6_Jun_2015_Auditoria_Completa.md` |
| 007 | `007_SCC_Issue_7_Jul_2015_Auditoria_Completa.md` | `007_SCC_Issue_7_Jul_2015_Auditoria_Completa.md` |
| 008 | `008_SCC_Issue_8_Aug_2015_Auditoria_Completa.md` | `008_SCC_Issue_8_Aug_2015_Auditoria_Completa.md` |
| 009 | `009_SCC_Issue_9_Sep_2015_Auditoria_Completa.md` | `009_SCC_Issue_9_Sep_2015_Auditoria_Completa.md` |
| 010 | `010_SCC_Issue_10_Oct_2015_Auditoria_Completa.md` | `010_SCC_Issue_10_Oct_2015_Auditoria_Completa.md` |
| 011 | `011_SCC_Issue_11_Nov_2015_Auditoria_Completa.md` | `011_SCC_Issue_11_Nov_2015_Auditoria_Completa.md` |
| 012 | `012_SCC_Issue_12_Dec_2015_Auditoria_Completa.md` | `012_SCC_Issue_12_Dec_2015_Auditoria_Completa.md` |
| 013 | `013_SCC_Issue_13_Jan_2016_Auditoria_Completa.md` | `013_SCC_Issue_13_Jan_2016_Auditoria_Completa.md` |
| 014 | `014_SCC_Issue_14_Feb_2016_Auditoria_Completa.md` | `014_SCC_Issue_14_Feb_2016_Auditoria_Completa.md` |
| 015 | `015_SCC_Issue_15_Mar_2016_Auditoria_Completa.md` | `015_SCC_Issue_15_Mar_2016_Auditoria_Completa.md` |

